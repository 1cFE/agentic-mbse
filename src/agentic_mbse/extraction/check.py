"""Pipeline component verification (``--check`` support).

Probes every extraction pipeline component against a real PDF and reports
pass/fail with actionable detail.  Catches broken components (like the
JSONL parsing bug in invoke_claude) before wasting time on full extraction
batches.

Cross-module imports: Several private functions are imported from sibling
modules (_detect_gmft, _detect_img2table, _pandoc_available,
_assess_math_garbling).  These are stable internal functions within the
extraction package — the coupling risk is low and check.py tests catch
signature changes immediately.
"""

from __future__ import annotations

import contextlib
import io
import json as _json
import os
import shutil
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from agentic_mbse.extraction.claude_enhance import invoke_claude, render_page_image
from agentic_mbse.extraction.pandoc_convert import (
    _pandoc_available,
    check_arxiv_html,
    convert_arxiv_html,
    detect_arxiv_id,
)
from agentic_mbse.extraction.pymupdf_backend import extract_pages
from agentic_mbse.extraction.quality_gate import _assess_math_garbling
from agentic_mbse.extraction.tables import (
    _detect_gmft,
    _detect_img2table,
    count_pipe_rows,
)
from agentic_mbse.extraction.types import PageResult

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class ProbeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_INSTALLED = "not_installed"
    SKIPPED = "skipped"
    UNTESTED = "untested"


class OverallStatus(str, Enum):
    PASS = "pass"
    DEGRADED = "degraded"
    FAIL = "fail"


@dataclass
class ProbeResult:
    component: str
    status: ProbeStatus
    detail: str | None = None
    error: str | None = None
    cost_usd: float | None = None
    model: str | None = None


@dataclass
class SelectedPages:
    headings: int | None = None
    math: int | None = None
    tables: int | None = None
    total_pages: int = 0


@dataclass
class CheckResult:
    pdf_name: str
    total_pages: int
    selected_pages: SelectedPages
    probes: list[ProbeResult]
    capabilities: dict[str, bool] = field(default_factory=dict)
    overall: OverallStatus = OverallStatus.PASS


# ---------------------------------------------------------------------------
# Import guard helpers (thin wrappers for testability)
# ---------------------------------------------------------------------------


def _try_import_gmft():
    """Raise ImportError if GMFT is not installed."""
    from gmft.auto import AutoTableDetector  # noqa: F401


def _try_import_img2table():
    """Raise ImportError if Img2Table deps are not installed."""
    from gmft.detectors.img2table import Img2TableDetector  # noqa: F401


def _try_import_docling():
    """Raise ImportError if Docling is not installed."""
    import docling  # noqa: F401


# ---------------------------------------------------------------------------
# Corpus discovery
# ---------------------------------------------------------------------------


def get_check_corpus() -> list[Path]:
    """Return paths to built-in test PDFs for --check."""
    corpus_dir = Path(__file__).parent / "check_corpus"
    if not corpus_dir.exists():
        return []
    return sorted(p for p in corpus_dir.iterdir() if p.suffix == ".pdf")


# ---------------------------------------------------------------------------
# Result aggregation
# ---------------------------------------------------------------------------

# Status priority for aggregation: higher = better
_STATUS_PRIORITY = {
    ProbeStatus.PASS: 5,
    ProbeStatus.UNTESTED: 4,
    ProbeStatus.SKIPPED: 3,
    ProbeStatus.NOT_INSTALLED: 2,
    ProbeStatus.FAIL: 1,
}


def merge_check_results(results: list[CheckResult]) -> CheckResult:
    """Aggregate probe results across multiple PDFs.

    For each probe component, keeps the best status (PASS > UNTESTED > ... > FAIL).
    Uses the ProbeResult from whichever PDF produced the best status.
    """
    # Group probes by component, pick best
    best_probes: dict[str, ProbeResult] = {}
    for result in results:
        for probe in result.probes:
            existing = best_probes.get(probe.component)
            if existing is None:
                best_probes[probe.component] = probe
                continue
            new_pri = _STATUS_PRIORITY.get(probe.status, 0)
            old_pri = _STATUS_PRIORITY.get(existing.status, 0)
            if new_pri > old_pri:
                best_probes[probe.component] = probe
            elif new_pri == old_pri:
                # Equal status: prefer the probe with more detail
                new_len = len(probe.detail or "")
                old_len = len(existing.detail or "")
                if new_len > old_len:
                    best_probes[probe.component] = probe

    # Preserve probe ordering from first result
    component_order = []
    seen = set()
    for result in results:
        for probe in result.probes:
            if probe.component not in seen:
                component_order.append(probe.component)
                seen.add(probe.component)

    merged_probes = [best_probes[c] for c in component_order if c in best_probes]

    # Merge SelectedPages: first non-None wins for each field
    headings = None
    math = None
    tables = None
    for result in results:
        sp = result.selected_pages
        if headings is None and sp.headings is not None:
            headings = sp.headings
        if math is None and sp.math is not None:
            math = sp.math
        if tables is None and sp.tables is not None:
            tables = sp.tables

    total_pages = sum(r.total_pages for r in results)
    merged_selected = SelectedPages(
        headings=headings, math=math, tables=tables, total_pages=total_pages
    )

    # Recompute capabilities and overall from merged probes
    capabilities = compute_capabilities(merged_probes, merged_selected)
    overall = compute_overall(merged_probes)

    return CheckResult(
        pdf_name=f"built-in corpus ({len(results)} PDFs)",
        total_pages=total_pages,
        selected_pages=merged_selected,
        probes=merged_probes,
        capabilities=capabilities,
        overall=overall,
    )


# ---------------------------------------------------------------------------
# Page selection
# ---------------------------------------------------------------------------


def select_pages(pages: list[PageResult]) -> SelectedPages:
    """Select 1-3 pages that exercise key pipeline capabilities.

    Uses only fast heuristics (no external tools):
    - Page 0: always selected for headings
    - Highest math garble score >= 1.0 -> math page
    - Highest pipe row count > 0 -> tables page
    """
    selected = SelectedPages(headings=0, total_pages=len(pages))

    best_math_score = 0.0
    best_math_page = None
    best_table_count = 0
    best_table_page = None

    for page in pages:
        score, _ = _assess_math_garbling(page.markdown)
        if score >= 1.0 and score > best_math_score:
            best_math_score = score
            best_math_page = page.page_num

        pipe_rows = count_pipe_rows(page.markdown)
        if pipe_rows > 0 and pipe_rows > best_table_count:
            best_table_count = pipe_rows
            best_table_page = page.page_num

    selected.math = best_math_page
    selected.tables = best_table_page
    return selected


# ---------------------------------------------------------------------------
# Component probes
# ---------------------------------------------------------------------------


def probe_pymupdf(pages: list[PageResult]) -> ProbeResult:
    """Validate pymupdf4llm extraction results (already extracted pages)."""
    char_counts = [len(p.markdown) for p in pages if p.markdown.strip()]
    if not char_counts:
        return ProbeResult("pymupdf4llm", ProbeStatus.FAIL, error="all pages empty")
    avg = sum(char_counts) // len(char_counts)
    return ProbeResult(
        "pymupdf4llm",
        ProbeStatus.PASS,
        detail=f"{len(pages)} pages extracted ({avg} chars avg)",
    )


def probe_gmft(pdf_path: Path, table_page: int | None) -> ProbeResult:
    """Probe GMFT table detector."""
    try:
        _try_import_gmft()
    except ImportError:
        return ProbeResult("gmft", ProbeStatus.NOT_INSTALLED)

    try:
        result = _detect_gmft(pdf_path, save_images=False)
        total = sum(len(v) for v in result.values())

        if table_page is None:
            return ProbeResult(
                "gmft",
                ProbeStatus.UNTESTED,
                detail=f"no table pages found in PDF — ran on all pages, {total} tables detected",
            )

        tables_on_page = result.get(table_page, [])
        return ProbeResult(
            "gmft",
            ProbeStatus.PASS,
            detail=f"{len(tables_on_page)} tables on page {table_page + 1}, {total} total",
        )
    except Exception as exc:
        return ProbeResult("gmft", ProbeStatus.FAIL, error=str(exc)[:200])


def probe_img2table(pdf_path: Path, table_page: int | None) -> ProbeResult:
    """Probe Img2Table table detector."""
    try:
        _try_import_img2table()
    except ImportError:
        return ProbeResult("img2table", ProbeStatus.NOT_INSTALLED)

    try:
        result = _detect_img2table(pdf_path, gmft_pages=set(), save_images=False)
        total = sum(len(v) for v in result.values())

        if table_page is None:
            return ProbeResult(
                "img2table",
                ProbeStatus.UNTESTED,
                detail=f"no table pages found in PDF — ran on all pages, {total} tables detected",
            )

        tables_on_page = result.get(table_page, [])
        return ProbeResult(
            "img2table",
            ProbeStatus.PASS,
            detail=f"{len(tables_on_page)} tables on page {table_page + 1}, {total} total",
        )
    except Exception as exc:
        return ProbeResult("img2table", ProbeStatus.FAIL, error=str(exc)[:200])


def probe_docling(pdf_path: Path) -> ProbeResult:
    """Probe Docling table detection."""
    try:
        _try_import_docling()
    except ImportError:
        return ProbeResult("docling", ProbeStatus.NOT_INSTALLED)

    return ProbeResult(
        "docling", ProbeStatus.UNTESTED,
        detail="importable but detection is not yet implemented (stub)",
    )


def probe_pandoc(pdf_path: Path) -> ProbeResult:
    """Probe Pandoc availability and arXiv HTML conversion."""
    if not _pandoc_available():
        return ProbeResult("pandoc", ProbeStatus.NOT_INSTALLED)

    detail_parts = ["binary found"]
    try:
        arxiv_id = detect_arxiv_id(pdf_path)
        if arxiv_id:
            detail_parts.append(f"arXiv ID detected ({arxiv_id})")
            html_url = check_arxiv_html(arxiv_id)
            if html_url:
                md = convert_arxiv_html(html_url)
                detail_parts.append(f"HTML converted ({len(md)} chars)")
            else:
                detail_parts.append("no HTML available")
        return ProbeResult("pandoc", ProbeStatus.PASS, detail=", ".join(detail_parts))
    except Exception as exc:
        return ProbeResult("pandoc", ProbeStatus.FAIL, error=str(exc)[:200])


def probe_claude(
    pdf_path: Path,
    page_num: int,
    model: str = "haiku",
    budget: float = 2.0,
) -> ProbeResult:
    """Probe Claude CLI invocation with a real page extraction."""
    if budget <= 0:
        return ProbeResult(
            "claude",
            ProbeStatus.SKIPPED,
            detail="--budget 0: Claude probe skipped (costs ~$0.001-$0.01)",
        )

    if not shutil.which("claude"):
        return ProbeResult("claude", ProbeStatus.NOT_INSTALLED)

    try:
        image_path = render_page_image(pdf_path, page_num)
        try:
            prompt = (
                f"Read the image file at {image_path.resolve()} "
                f"and extract its content.\n\n"
                f"Extract the text content of this document page as markdown."
            )
            response = invoke_claude(prompt, model=model, timeout=60)

            result_text = response.get("result", "")
            cost = response.get("total_cost_usd", 0)
            tokens = response.get("usage", {})
            out_tokens = tokens.get("output_tokens", 0)

            if not result_text.strip():
                return ProbeResult(
                    "claude",
                    ProbeStatus.FAIL,
                    error="Claude returned empty result",
                )

            return ProbeResult(
                "claude",
                ProbeStatus.PASS,
                detail=f"{model} responded, {out_tokens} tokens, ${cost:.3f}",
                cost_usd=cost,
                model=response.get("model", model),
            )
        finally:
            image_path.unlink(missing_ok=True)
    except Exception as exc:
        return ProbeResult("claude", ProbeStatus.FAIL, error=str(exc)[:300])


# ---------------------------------------------------------------------------
# Capability mapping
# ---------------------------------------------------------------------------


def _probe_ok(probes: list[ProbeResult], component: str) -> bool:
    """True if the component is installed and functional (PASS or UNTESTED)."""
    p = next((p for p in probes if p.component == component), None)
    return p is not None and p.status in (ProbeStatus.PASS, ProbeStatus.UNTESTED)


def compute_capabilities(
    probes: list[ProbeResult], selected: SelectedPages
) -> dict[str, bool]:
    """Map component statuses to user-visible capabilities."""
    pandoc_probe = next((p for p in probes if p.component == "pandoc"), None)
    pandoc_has_arxiv = (
        pandoc_probe is not None
        and pandoc_probe.detail is not None
        and "arXiv" in pandoc_probe.detail
    )

    return {
        "base_extraction": _probe_ok(probes, "pymupdf4llm"),
        "table_detection": _probe_ok(probes, "gmft") or _probe_ok(probes, "img2table"),
        "table_enhancement": (
            _probe_ok(probes, "claude")
            and (_probe_ok(probes, "gmft") or _probe_ok(probes, "img2table"))
        ),
        "math_reextraction": _probe_ok(probes, "claude"),
        "arxiv_shortcut": _probe_ok(probes, "pandoc") and pandoc_has_arxiv,
        "docling_tables": _probe_ok(probes, "docling"),
    }


# ---------------------------------------------------------------------------
# Overall status
# ---------------------------------------------------------------------------


def compute_overall(probes: list[ProbeResult]) -> OverallStatus:
    """Compute overall check status from individual probe results."""
    pymupdf = next((p for p in probes if p.component == "pymupdf4llm"), None)
    if pymupdf is None:
        return OverallStatus.FAIL
    if pymupdf.status == ProbeStatus.FAIL:
        return OverallStatus.FAIL

    has_failure = any(
        p.status == ProbeStatus.FAIL
        for p in probes
        if p.component != "pymupdf4llm"
    )
    if has_failure:
        return OverallStatus.DEGRADED

    return OverallStatus.PASS


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

# Capability display names for the human-readable table
_CAPABILITY_LABELS: dict[str, str] = {
    "base_extraction": "Base text extraction",
    "table_detection": "Table detection and enhancement (GMFT + Img2Table)",
    "table_enhancement": "Table enhancement via Claude",
    "math_reextraction": "Math/equation re-extraction (Claude)",
    "arxiv_shortcut": "arXiv HTML shortcut (Pandoc + arXiv ID found)",
    "docling_tables": "Third-pass table detection (Docling)",
}


def _page_1indexed(page: int | None) -> int | None:
    """Convert 0-indexed page to 1-indexed, preserving None."""
    return page + 1 if page is not None else None


def format_check_json(result: CheckResult) -> str:
    """Format check result as JSON string with 1-indexed pages."""
    sp = result.selected_pages
    components: dict[str, dict] = {}
    for p in result.probes:
        entry: dict = {"status": p.status.value, "detail": p.detail}
        if p.cost_usd is not None:
            entry["cost_usd"] = p.cost_usd
        if p.model is not None:
            entry["model"] = p.model
        components[p.component] = entry

    obj = {
        "pdf": result.pdf_name,
        "pages": result.total_pages,
        "selected_pages": {
            "headings": _page_1indexed(sp.headings),
            "math": _page_1indexed(sp.math),
            "tables": _page_1indexed(sp.tables),
        },
        "components": components,
        "capabilities": result.capabilities,
        "overall": result.overall.value,
    }
    return _json.dumps(obj, indent=2)


def print_check_table(result: CheckResult) -> None:
    """Print human-readable check results to stdout."""
    sp = result.selected_pages

    # Header
    print(f"Pipeline component check for: {result.pdf_name} ({result.total_pages} pages)")

    # Selected pages line
    page_parts: list[str] = []
    if sp.headings is not None:
        page_parts.append(f"{sp.headings + 1} (headings)")
    if sp.math is not None:
        page_parts.append(f"{sp.math + 1} (math+equations)")
    if sp.tables is not None:
        page_parts.append(f"{sp.tables + 1} (tables)")
    print(f"Selected pages: {', '.join(page_parts)}")

    # Missing content messages
    if sp.math is None:
        print("  (no math-garbled pages found — Claude equation enhancement untested)")
    if sp.tables is None:
        print("  (no table-like pages found — table detection untested)")
    print()

    # Component table
    print(f"  {'Component':<14}{'Status':<16}Detail")
    print(f"  {'─' * 13:<14}{'─' * 15:<16}{'─' * 6}")
    for p in result.probes:
        status_str = p.status.value.replace("_", " ")
        if p.status == ProbeStatus.FAIL:
            status_str = status_str.upper()
        detail_str = p.error if p.status == ProbeStatus.FAIL and p.error else (p.detail or "")
        print(f"  {p.component:<14}{status_str:<16}{detail_str}")
    print()

    # Capabilities
    print("Expected quality with current setup:")
    for key, label in _CAPABILITY_LABELS.items():
        enabled = result.capabilities.get(key, False)
        marker = "+" if enabled else "-"
        print(f"  {marker} {label}")


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_check(
    pdf_path: Path,
    claude_model: str = "haiku",
    claude_budget: float = 2.0,
) -> CheckResult:
    """Run all component probes against a PDF and return aggregated results."""
    all_false_caps = {
        "base_extraction": False,
        "table_detection": False,
        "table_enhancement": False,
        "math_reextraction": False,
        "arxiv_shortcut": False,
        "docling_tables": False,
    }

    # Suppress third-party stdout noise (pymupdf warnings, gmft debug prints)
    # so that --check-json output is clean for machine consumption.
    # Belt-and-suspenders: env var suppresses pymupdf's layout recommendation
    # even if redirect_stdout misses it (e.g. first-run model loading race).
    _prev_suggest = os.environ.get("PYMUPDF_SUGGEST_LAYOUT_ANALYZER")
    os.environ["PYMUPDF_SUGGEST_LAYOUT_ANALYZER"] = "0"
    _devnull = io.StringIO()

    def _restore_env() -> None:
        if _prev_suggest is None:
            os.environ.pop("PYMUPDF_SUGGEST_LAYOUT_ANALYZER", None)
        else:
            os.environ["PYMUPDF_SUGGEST_LAYOUT_ANALYZER"] = _prev_suggest

    # 1. Base extraction (also validates pymupdf4llm)
    try:
        with contextlib.redirect_stdout(_devnull):
            pages = extract_pages(pdf_path)
    except Exception as exc:
        _restore_env()
        return CheckResult(
            pdf_name=pdf_path.name,
            total_pages=0,
            selected_pages=SelectedPages(),
            probes=[ProbeResult("pymupdf4llm", ProbeStatus.FAIL, error=str(exc)[:300])],
            capabilities=all_false_caps,
            overall=OverallStatus.FAIL,
        )

    selected = select_pages(pages)
    pymupdf_result = probe_pymupdf(pages)

    # 2. Table probes (selected.tables may be None -> UNTESTED)
    with contextlib.redirect_stdout(_devnull):
        gmft_result = probe_gmft(pdf_path, selected.tables)
        img2table_result = probe_img2table(pdf_path, selected.tables)
    docling_result = probe_docling(pdf_path)

    _restore_env()

    # 3. Pandoc probe
    pandoc_result = probe_pandoc(pdf_path)

    # 4. Claude probe — cost warning to stderr (only if budget > 0 AND installed)
    if claude_budget > 0 and shutil.which("claude"):
        print(
            f"Note: Claude probe will invoke Claude {claude_model} "
            f"(~$0.001-$0.01). Use --budget 0 to skip.",
            file=sys.stderr,
        )
    claude_result = probe_claude(
        pdf_path, page_num=0, model=claude_model, budget=claude_budget
    )

    probes = [
        pymupdf_result,
        gmft_result,
        img2table_result,
        docling_result,
        pandoc_result,
        claude_result,
    ]
    capabilities = compute_capabilities(probes, selected)
    overall = compute_overall(probes)

    return CheckResult(
        pdf_name=pdf_path.name,
        total_pages=len(pages),
        selected_pages=selected,
        probes=probes,
        capabilities=capabilities,
        overall=overall,
    )
