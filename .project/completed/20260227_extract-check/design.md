# Design: `agentic-mbse extract --check` — Pipeline Component Verification

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-27 11:00
**Branch:** doc-ingest-clean
**Commit:** f4446b2
**Parent:** EPIC-PDFV4-001

---

## Overview

Add a `--check` flag to `agentic-mbse extract` that probes every pipeline component against a real PDF and reports pass/fail with actionable detail — catching broken components (like the JSONL parsing bug) before wasting time on full extraction batches.

## Related Artifacts

- **Spec:** `.project/active/extract-check/spec.md`
- **Triggering bug fix:** `.project/active/v4-claude-invocation-and-logging/design.md`
- **Pipeline architecture:** `.project/concepts/doc-extraction/design.md`
- **Pipeline code:** `src/agentic_mbse/extraction/pipeline.py`
- **CLI code:** `src/agentic_mbse/cli/extract_cli.py`

---

## Research Findings

### Existing Component Structure

The pipeline has 6 optional components, each with distinct dependency and invocation patterns:

| # | Component | Module | Import Guard | Current Check |
|---|-----------|--------|-------------|--------------|
| 1 | pymupdf4llm | `pymupdf_backend.py:20-24` | Lazy `import pymupdf4llm` | `_is_available("pymupdf")` in `extract_cli.py:31-36` — import only |
| 2 | GMFT | `tables.py:360-364` | `from gmft.auto import AutoTableDetector...` | `try/except ImportError` → returns `{}` |
| 3 | Img2Table | `tables.py:431-438` | `from gmft.detectors.img2table import...` | `try/except ImportError` → returns `{}` |
| 4 | Docling | `tables.py:499-507` | Stub — always returns `{}` | None (stub) |
| 5 | Pandoc | `pandoc_convert.py:21-22` | `shutil.which("pandoc")` | `_is_available("pandoc")` in `extract_cli.py:45-46` |
| 6 | Claude | `claude_enhance.py:78-125` | `shutil.which("claude")` in `pipeline.py:228-238` | Pre-flight binary check only (from v4 fix) |

### Reusable Functions for Probes

Each probe can reuse existing pipeline functions with minimal wrapping:

- **pymupdf4llm:** `extract_pages(pdf_path)` in `pymupdf_backend.py:124` — public, returns `list[PageResult]`
- **GMFT:** `_detect_gmft(pdf_path)` in `tables.py:352` — private, returns `dict[int, list[DetectedTable]]`
- **Img2Table:** `_detect_img2table(pdf_path, gmft_pages)` in `tables.py:421` — private, same pattern
- **Docling:** `_detect_docling(pdf_path, covered_pages)` in `tables.py:499` — private, stub
- **Pandoc:** `_pandoc_available()` in `pandoc_convert.py:21` — private; `detect_arxiv_id()` and `check_arxiv_html()` are public
- **Claude:** `invoke_claude(prompt, model)` in `claude_enhance.py:78` — public; `render_page_image()` at `claude_enhance.py:133` — public
- **Quality gate:** `_assess_math_garbling(md)` in `quality_gate.py:98` — private

**Private function imports (Minor #1):** Three modules expose functions we need as private (`_detect_gmft`, `_detect_img2table`, `_pandoc_available`, `_assess_math_garbling`). Rather than making them public (which changes the module's API contract for all consumers), `check.py` imports them with a `# noqa: F811` comment documenting the cross-module coupling. These are stable internal functions used only within the extraction package — the coupling risk is low. If any of them change signature, the check module's tests will catch it immediately.

### Page Selection Heuristics

The quality gate already has the math/table detection logic we need:

- **Math detection:** `_assess_math_garbling(md)` in `quality_gate.py:98` — returns `(severity, reasons)`. Score >= 1.0 means garbled math.
- **Table detection:** `_assess_table_anomaly(md)` in `quality_gate.py:150` — detects `<br>` artifacts, `ColN` auto-headers. Also, `count_pipe_rows(md)` in `tables.py:79` for basic presence.
- **Heading detection:** `count_headings(md)` in `quality_gate.py:235`.
- **Page extraction for scanning:** `extract_pages(pdf_path)` in `pymupdf_backend.py:124` — extracts all pages with pymupdf4llm.

### CLI Pattern

The extract subcommand uses `register_extract_subcommand()` in `extract_cli.py:371` with `argparse`. The `--check` flag should be added here and handled in `cmd_extract()`. The existing exit code convention uses `EXIT_SUCCESS = 0` and `EXIT_FAILURE = 1` from `agentic_mbse.validation`.

### Testing Pattern

Tests in `test_pipeline.py` and `test_claude_enhance.py` use:
- `unittest.mock.patch` for all external dependencies
- Helper functions like `_page()`, `_table()`, `_cost()` for synthetic test data
- Module-level patch targets: `_P = "agentic_mbse.extraction.pipeline"`
- Real quality gate/routing implementations with mocked extraction functions

---

## Design Decisions

### DD-1: UNTESTED status for content-dependent probes (Major #1)

The spec requires reporting when the PDF lacks content types needed to exercise specific components (e.g., no math pages → Claude equation enhancement untested). The `UNTESTED` status is not just about the component being broken — it's about the **test being inconclusive** because the document didn't have the right content.

**Where UNTESTED applies:**
- GMFT/Img2Table: PDF has no table-like pages → detector ran on page 0 but result is meaningless
- Claude math re-extraction: PDF has no math-garbled pages → Claude's equation capability is untested

**Where UNTESTED does NOT apply:**
- pymupdf4llm: always testable (every PDF has pages)
- Pandoc: binary check + arXiv ID detection work on any PDF
- Claude invocation itself: the smoke test runs regardless of content type

**Implementation:** Probes that depend on content selection receive a `page_has_content: bool` flag. When the selected page lacks the expected content, the probe still runs (to verify the component works) but returns UNTESTED with an explanatory detail string. The capability mapping treats UNTESTED as "component works, but couldn't verify this specific capability."

### DD-2: 1-indexed page numbers in all user-facing output (Major #2)

Internally, pages are 0-indexed (matching pymupdf4llm). All user-facing output (table display, JSON, detail strings) converts to 1-indexed. The `SelectedPages` dataclass stores 0-indexed values; conversion happens at the display/serialization boundary only.

### DD-3: Overall status as enum (Minor #3, #6)

`CheckResult.overall` uses `OverallStatus` enum (`PASS`, `DEGRADED`, `FAIL`) instead of a bare string. The enum's `.value` provides the JSON-serializable string. Exit code mapping uses the enum directly — no string comparison.

---

## Proposed Design

### Architecture Overview

The `--check` feature is implemented as a single new module `src/agentic_mbse/extraction/check.py` that contains all probe logic, page selection, and output formatting. The CLI wires it up via a new code path in `cmd_extract()`.

```
cmd_extract(args)
  └─ if args.check:
       ├─ validate: single PDF, not used with --json alone
       └─ run_check(pdf_path, config) → CheckResult
            ├─ select_pages(pdf_path) → SelectedPages
            │    └─ extract_pages() → scan for math/tables/headings
            ├─ probe_pymupdf(pages)
            ├─ probe_gmft(pdf_path, table_page, has_table_content)
            ├─ probe_img2table(pdf_path, table_page, has_table_content)
            ├─ probe_docling(pdf_path)
            ├─ probe_pandoc(pdf_path)
            └─ probe_claude(pdf_path, page, model, budget)
```

### 1. Data Types

**File:** `src/agentic_mbse/extraction/check.py` (new)

```python
from enum import Enum
from dataclasses import dataclass, field

class ProbeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_INSTALLED = "not_installed"
    SKIPPED = "skipped"      # e.g., Claude skipped due to --budget 0
    UNTESTED = "untested"    # component ran OK, but PDF lacked content to exercise it

class OverallStatus(str, Enum):
    PASS = "pass"
    DEGRADED = "degraded"
    FAIL = "fail"

@dataclass
class ProbeResult:
    component: str           # "pymupdf4llm", "gmft", etc.
    status: ProbeStatus
    detail: str | None = None
    error: str | None = None  # truncated error message on FAIL
    cost_usd: float | None = None  # only for Claude
    model: str | None = None       # only for Claude

@dataclass
class SelectedPages:
    headings: int | None = None    # page number (0-indexed internally)
    math: int | None = None        # page with highest math garble score, or None
    tables: int | None = None      # page with most table-like content, or None
    total_pages: int = 0

@dataclass
class CheckResult:
    pdf_name: str
    total_pages: int
    selected_pages: SelectedPages
    probes: list[ProbeResult]
    capabilities: dict[str, bool]
    overall: OverallStatus
```

### 2. Page Selection

**Function:** `select_pages(pages: list[PageResult]) -> SelectedPages`

Takes already-extracted pages (from the pymupdf4llm probe step) and scans with heuristics:

1. Page 0 is always selected for headings.
2. Scan each page's markdown:
   - `_assess_math_garbling(md)` — highest severity score ≥ 1.0 → `math` page. If no page has score ≥ 1.0, `math` is **None** (not a fallback to page 0).
   - `count_pipe_rows(md)` — highest pipe row count > 0 → `tables` page. If no page has pipe rows, `tables` is **None**.
3. Return `SelectedPages` with 1–3 pages. `None` values for `math`/`tables` signal "PDF lacks this content type" — downstream probes use this to return UNTESTED.

### 3. Component Probes

Each probe is an independent function with the signature `probe_X(...) -> ProbeResult`. Each catches its own exceptions and returns `ProbeResult` with the appropriate status.

#### 3.1 `probe_pymupdf(pdf_path, selected_pages) -> ProbeResult`

```python
def probe_pymupdf(pdf_path: Path, pages: list[PageResult]) -> ProbeResult:
    # pages already extracted during select_pages — reuse them
    # Verify: non-empty markdown for selected pages
    char_counts = [len(p.markdown) for p in pages if p.markdown.strip()]
    if not char_counts:
        return ProbeResult("pymupdf4llm", ProbeStatus.FAIL, error="all pages empty")
    avg = sum(char_counts) // len(char_counts)
    return ProbeResult(
        "pymupdf4llm", ProbeStatus.PASS,
        detail=f"{len(pages)} pages extracted ({avg} chars avg)"
    )
```

Note: This doesn't re-extract — it validates the pages already obtained during `select_pages()`. This avoids double extraction.

#### 3.2 `probe_gmft(pdf_path, table_page) -> ProbeResult`

```python
def probe_gmft(pdf_path: Path, table_page: int | None) -> ProbeResult:
    try:
        from gmft.auto import AutoTableDetector  # noqa: F401
    except ImportError:
        return ProbeResult("gmft", ProbeStatus.NOT_INSTALLED)

    try:
        result = _detect_gmft(pdf_path, save_images=False)
        total = sum(len(v) for v in result.values())

        if table_page is None:
            # No table content in PDF — GMFT ran but result is inconclusive
            return ProbeResult(
                "gmft", ProbeStatus.UNTESTED,
                detail=f"no table pages found in PDF — ran on all pages, {total} tables detected"
            )

        tables_on_page = result.get(table_page, [])
        # Display page as 1-indexed
        return ProbeResult(
            "gmft", ProbeStatus.PASS,
            detail=f"{len(tables_on_page)} tables on page {table_page + 1}, {total} total"
        )
    except Exception as exc:
        return ProbeResult("gmft", ProbeStatus.FAIL, error=str(exc)[:200])
```

Import check first (distinguishes "not installed" from "installed but broken"), then real invocation. When `table_page` is None (PDF has no table content), the probe returns UNTESTED — the component ran without error but the result doesn't prove table detection works.

#### 3.3 `probe_img2table(pdf_path, table_page) -> ProbeResult`

Same pattern as GMFT: import check, run `_detect_img2table()`, return UNTESTED when `table_page is None`.

Note: Img2Table requires GMFT's `PyPDFium2Document`, so if GMFT is not installed, Img2Table is also not_installed (same import block in `tables.py:431-438`).

#### 3.4 `probe_docling(pdf_path) -> ProbeResult`

Import check for `docling`. Since `_detect_docling()` is a stub returning `{}`, the probe just checks the import:

```python
def probe_docling(pdf_path: Path) -> ProbeResult:
    try:
        import docling  # noqa: F401
    except ImportError:
        return ProbeResult("docling", ProbeStatus.NOT_INSTALLED)
    # Docling detection is a stub — report as pass if importable
    return ProbeResult("docling", ProbeStatus.PASS, detail="importable (detection is stub)")
```

#### 3.5 `probe_pandoc(pdf_path) -> ProbeResult`

```python
def probe_pandoc(pdf_path: Path) -> ProbeResult:
    if not _pandoc_available():
        return ProbeResult("pandoc", ProbeStatus.NOT_INSTALLED)

    detail_parts = ["binary found"]
    try:
        arxiv_id = detect_arxiv_id(pdf_path)  # reuse existing function
        if arxiv_id:
            detail_parts.append(f"arXiv ID detected ({arxiv_id})")
            html_url = check_arxiv_html(arxiv_id)
            if html_url:
                # Full end-to-end conversion — exercises download, preprocess,
                # Pandoc subprocess, postprocess (same path as _try_arxiv_shortcut)
                md = convert_arxiv_html(html_url)
                detail_parts.append(f"HTML converted ({len(md)} chars)")
            else:
                detail_parts.append("no HTML available")
        return ProbeResult("pandoc", ProbeStatus.PASS, detail=", ".join(detail_parts))
    except Exception as exc:
        return ProbeResult("pandoc", ProbeStatus.FAIL, error=str(exc)[:200])
```

The probe runs the full `convert_arxiv_html()` path rather than just a HEAD check. This exercises the same download → preprocess → Pandoc subprocess → postprocess pipeline that `_try_arxiv_shortcut()` uses in production. A shallow HEAD check would miss failures like wrong Pandoc version, HTML format changes, or conversion timeouts — the same class of silent failure that motivated the `--check` feature. Adds ~5-15s for arXiv PDFs; non-arXiv PDFs are unaffected.

#### 3.6 `probe_claude(pdf_path, page_num, model, budget) -> ProbeResult`

The critical probe. Must actually invoke Claude.

```python
def probe_claude(
    pdf_path: Path,
    page_num: int,
    model: str = "haiku",
    budget: float = 2.0,
) -> ProbeResult:
    if budget <= 0:
        return ProbeResult(
            "claude", ProbeStatus.SKIPPED,
            detail="--budget 0: Claude probe skipped (costs ~$0.001-$0.01)"
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
                    "claude", ProbeStatus.FAIL,
                    error="Claude returned empty result"
                )

            return ProbeResult(
                "claude", ProbeStatus.PASS,
                detail=f"{model} responded, {out_tokens} tokens, ${cost:.3f}",
                cost_usd=cost,
                model=response.get("model", model),
            )
        finally:
            image_path.unlink(missing_ok=True)
    except Exception as exc:
        return ProbeResult("claude", ProbeStatus.FAIL, error=str(exc)[:300])
```

Key design choices:
- Uses `model="haiku"` by default for cheapest probe (~$0.001)
- Renders a page image and passes it to `invoke_claude()` — exercises the full JSON parsing path (catches the JSONL bug)
- Cleans up temp image in `finally` block
- Short prompt — minimal token cost while still exercising the full path
- Reports actual cost

### 4. Capability Mapping

**Function:** `compute_capabilities(probes: list[ProbeResult], selected: SelectedPages) -> dict[str, bool]`

Maps component statuses to user-visible capabilities. PASS and UNTESTED both count as "component works" — UNTESTED means "ran without error but the PDF didn't have the right content to prove this specific capability." NOT_INSTALLED, FAIL, and SKIPPED count as unavailable.

```python
def _probe_ok(probes: list[ProbeResult], component: str) -> bool:
    """True if the component is installed and functional (PASS or UNTESTED)."""
    p = next((p for p in probes if p.component == component), None)
    return p is not None and p.status in (ProbeStatus.PASS, ProbeStatus.UNTESTED)
```

| Capability | Requires | Logic |
|------------|----------|-------|
| `base_extraction` | pymupdf4llm OK | `_probe_ok("pymupdf4llm")` |
| `table_detection` | GMFT OK or Img2Table OK | Either OK |
| `table_enhancement` | Claude OK + table_detection | Both OK |
| `math_reextraction` | Claude OK | Claude OK |
| `arxiv_shortcut` | Pandoc OK + arXiv ID in detail | Pandoc OK and "arXiv" in detail |
| `docling_tables` | Docling OK | Docling OK |

### 5. Overall Status

```python
def compute_overall(probes: list[ProbeResult]) -> OverallStatus:
    pymupdf = next(p for p in probes if p.component == "pymupdf4llm")
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
```

UNTESTED does NOT trigger degraded — the component ran without error. NOT_INSTALLED also does not trigger degraded (per FR-7: "not_installed components do NOT cause a non-zero exit code").

### 6. Output Formatting

#### 6.1 Human-Readable (default)

**Function:** `print_check_table(result: CheckResult) -> None`

Prints to stdout following the spec's format. **All page numbers are 1-indexed** (converted from internal 0-indexed at the display boundary).

```
Pipeline component check for: paper.pdf (14 pages)
Selected pages: 1 (headings), 5 (math+equations), 8 (tables)

  Component     Status          Detail
  ─────────     ──────          ──────
  pymupdf4llm   pass            14 pages extracted (1847 chars avg)
  GMFT          pass            2 tables on page 8, 5 total
  Img2Table     pass            0 additional tables (page 8)
  Docling       not installed
  Pandoc        pass            binary found, arXiv ID detected (2401.12345)
  Claude        pass            haiku responded, 43 tokens, $0.002

Expected quality with current setup:
  + Base text extraction
  + Table detection and enhancement (GMFT + Img2Table)
  + Math/equation re-extraction (Claude)
  + arXiv HTML shortcut (Pandoc + arXiv ID found)
  - Third-pass table detection (Docling not installed)
```

When a content type is missing:
```
Selected pages: 1 (headings)
  (no math-garbled pages found — Claude equation enhancement untested)
  (no table-like pages found — table detection untested)
```

Uses `+`/`-` instead of Unicode checkmarks for terminal compatibility.

#### 6.2 Machine-Readable JSON (`--check-json`)

**Function:** `format_check_json(result: CheckResult) -> str`

Produces the JSON structure from FR-5 in the spec. Output goes to stdout; all other output (cost warning, etc.) goes to stderr. **Page numbers in JSON are 1-indexed** (matching user expectation and spec examples).

```json
{
  "pdf": "paper.pdf",
  "pages": 14,
  "selected_pages": {"headings": 1, "math": 5, "tables": 8},
  "components": {
    "pymupdf4llm": {"status": "pass", "detail": "14 pages extracted (1847 chars avg)"},
    "gmft": {"status": "pass", "detail": "2 tables on page 8, 5 total"},
    "img2table": {"status": "untested", "detail": "no table pages found in PDF"},
    "docling": {"status": "not_installed", "detail": null},
    "pandoc": {"status": "pass", "detail": "binary found, arXiv ID: 2401.12345"},
    "claude": {"status": "pass", "detail": "haiku responded, 43 tokens, $0.002", "cost_usd": 0.002, "model": "haiku"}
  },
  "capabilities": {
    "base_extraction": true,
    "table_detection": true,
    "table_enhancement": true,
    "math_reextraction": true,
    "arxiv_shortcut": true,
    "docling_tables": false
  },
  "overall": "pass"
}
```

When `selected_pages.math` or `selected_pages.tables` is None (PDF lacks that content), the JSON field is `null`.

### 7. CLI Integration

**File:** `src/agentic_mbse/cli/extract_cli.py`

#### 7.1 Argument Registration

Add to `register_extract_subcommand()`:

```python
p.add_argument(
    "--check",
    action="store_true",
    help="Probe pipeline components against the PDF without extracting",
)
p.add_argument(
    "--check-json",
    action="store_true",
    dest="check_json",
    help="Output machine-readable JSON (implies --check)",
)
```

**Design choice (Minor #2, #4):** Using `--check-json` with `dest="check_json"` instead of bare `--json`:
- Avoids shadowing Python's `json` keyword (no `getattr` needed)
- `--check-json` implies `--check` — no ambiguous `--json` without `--check` state
- Access as `args.check_json` directly

#### 7.2 Command Handler

Add early return in `cmd_extract()` after path validation but before the extraction loop:

```python
# Handle --check-json implying --check
if args.check_json:
    args.check = True

if args.check:
    from agentic_mbse.extraction.check import (
        OverallStatus, run_check, print_check_table, format_check_json,
    )

    if not docs:
        print("Error: no PDF or DOCX files found at path")
        return EXIT_FAILURE

    if len(docs) > 1:
        print(f"Error: --check operates on a single PDF, got {len(docs)} files")
        print("       Provide a single PDF file path, not a directory")
        return EXIT_FAILURE

    pdf = docs[0]
    if pdf.suffix.lower() != ".pdf":
        print("Error: --check only works with PDF files")
        return EXIT_FAILURE

    check_result = run_check(
        pdf,
        claude_model=args.model,
        claude_budget=args.budget,
    )

    if args.check_json:
        print(format_check_json(check_result))
    else:
        print_check_table(check_result)

    # Exit codes per FR-7
    if check_result.overall == OverallStatus.FAIL:
        return 2
    elif check_result.overall == OverallStatus.DEGRADED:
        return EXIT_FAILURE
    return EXIT_SUCCESS
```

**Fixes addressed:**
- **Major #3:** `docs` is validated non-empty before indexing (the existing `discover_documents()` + empty check runs before `--check`, so this is a belt-and-suspenders guard)
- **Minor #4:** `--check-json` implies `--check` — no silent no-op
- **Minor #5:** Multiple files explicitly rejected with actionable error message

#### 7.3 Exit Codes

Per FR-7:

| Exit Code | Meaning | Constant |
|-----------|---------|----------|
| 0 | All installed components pass | `EXIT_SUCCESS` |
| 1 | One or more installed components broken | `EXIT_FAILURE` |
| 2 | pymupdf4llm broken (pipeline cannot run) | `2` (new, `EXIT_CRITICAL`) |

Note: `NOT_INSTALLED`, `SKIPPED`, and `UNTESTED` do NOT trigger non-zero exit. Only `FAIL` does.

### 8. Orchestrator

**Function:** `run_check(pdf_path, claude_model, claude_budget) -> CheckResult`

```python
def run_check(
    pdf_path: Path,
    claude_model: str = "haiku",
    claude_budget: float = 2.0,
) -> CheckResult:
    all_false_caps = {
        "base_extraction": False, "table_detection": False,
        "table_enhancement": False, "math_reextraction": False,
        "arxiv_shortcut": False, "docling_tables": False,
    }

    # 1. Base extraction (also validates pymupdf4llm)
    try:
        pages = extract_pages(pdf_path)
    except Exception as exc:
        # pymupdf4llm is broken — return fail result immediately
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

    # 2. Table probes (selected.tables may be None → UNTESTED)
    gmft_result = probe_gmft(pdf_path, selected.tables)
    img2table_result = probe_img2table(pdf_path, selected.tables)
    docling_result = probe_docling(pdf_path)

    # 3. Pandoc probe
    pandoc_result = probe_pandoc(pdf_path)

    # 4. Claude probe — always uses page 0 (guaranteed to exist)
    #    The math page selection affects the UNTESTED reporting in capabilities,
    #    not the Claude smoke test itself.
    claude_result = probe_claude(pdf_path, page_num=0, model=claude_model, budget=claude_budget)

    probes = [pymupdf_result, gmft_result, img2table_result,
              docling_result, pandoc_result, claude_result]
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
```

**Note on Claude page selection:** The Claude probe always uses page 0 (guaranteed to exist). The `selected.math` field is used for capability mapping (`math_reextraction` reports whether the PDF has math content that would benefit from Claude), not for choosing which page Claude extracts in the smoke test. The smoke test's purpose is to verify `invoke_claude()` + JSON parsing work at all — the page content doesn't matter for that.

### 9. Cost Warning

Before running the Claude probe, the orchestrator (or CLI) prints to stderr:

```
Note: Claude probe will invoke Claude haiku (~$0.001-$0.01). Use --budget 0 to skip.
```

This is printed to stderr so it doesn't pollute `--json` stdout output.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GMFT/Img2Table probe scans all pages (slow for large PDFs) | Medium | Medium | `_detect_gmft` scans all pages. For `--check`, we could limit to selected pages only. But this adds complexity. For V1, accept the cost — it's still <30s for typical PDFs. Add page-limited probing later if needed. |
| Claude probe cost surprises users | Low | Medium | Explicit stderr warning + `--budget 0` skip. Cost is tiny (~$0.001 for haiku). |
| Network-dependent probes (Claude, arXiv) fail due to network | Medium | Low | Report as FAIL with error message. The user can distinguish "auth error" from "component broken". Future: add "network_error" status. |
| Pandoc probe adds latency for arXiv PDFs (~5-15s for download + conversion) | Medium | Low | Only triggers when arXiv ID is detected. Non-arXiv PDFs skip conversion entirely. Comparable to Claude probe latency and acceptable for a diagnostic command. |
| `render_page_image` temp file leak on crash | Low | Low | `finally` block ensures cleanup. If process is killed, OS cleans up /tmp. |
| GMFT detection returns 0 tables on a page that has tables | Medium | Low | 0 tables is reported as "pass (0 tables on page N)" — GMFT working correctly but not detecting tables is not a GMFT bug. The spec explicitly says: "Returns without error (0 tables is OK)". |

---

## Integration Strategy

- `--check` is an early-return code path in `cmd_extract()` — it does NOT interfere with the existing extraction flow
- The new `check.py` module imports from existing pipeline modules but doesn't modify them
- Probe functions call the same underlying functions as the pipeline (e.g., `_detect_gmft`, `invoke_claude`) — if the probe passes, the pipeline will too
- `--check-json` is a dedicated flag (not `--json`) to avoid ambiguity if JSON output is later added for extraction results

---

## Validation Approach

### Unit Tests (in new `tests/test_check.py`)

**Page Selection:**

| Test | What it verifies |
|------|-----------------|
| `test_select_pages_finds_math` | Math page selection picks highest severity ≥ 1.0 |
| `test_select_pages_finds_tables` | Table page selection picks highest pipe row count > 0 |
| `test_select_pages_always_includes_page_0` | Page 0 always selected for headings |
| `test_select_pages_no_math` | No pages with severity ≥ 1.0 → `math` is None |
| `test_select_pages_no_tables` | No pages with pipe rows → `tables` is None |

**Probes:**

| Test | What it verifies |
|------|-----------------|
| `test_probe_pymupdf_pass` | Non-empty pages → pass |
| `test_probe_pymupdf_fail` | All empty pages → fail |
| `test_probe_gmft_not_installed` | ImportError → not_installed |
| `test_probe_gmft_pass_with_tables` | Table page found, returns without error → pass |
| `test_probe_gmft_untested_no_table_page` | `table_page=None` → untested |
| `test_probe_gmft_runtime_error` | Exception → fail with error |
| `test_probe_img2table_not_installed` | ImportError → not_installed |
| `test_probe_img2table_untested_no_table_page` | `table_page=None` → untested |
| `test_probe_docling_not_installed` | ImportError → not_installed |
| `test_probe_pandoc_not_installed` | `shutil.which → None` → not_installed |
| `test_probe_pandoc_no_arxiv` | No arXiv ID → pass with "binary found" only |
| `test_probe_pandoc_arxiv_no_html` | arXiv ID found but no HTML available → pass with "no HTML available" |
| `test_probe_pandoc_arxiv_converted` | Full conversion path → pass with char count in detail |
| `test_probe_pandoc_conversion_error` | `convert_arxiv_html` raises → fail with error |
| `test_probe_claude_budget_zero_skipped` | budget=0 → skipped |
| `test_probe_claude_not_installed` | `shutil.which → None` → not_installed |
| `test_probe_claude_pass` | Full invocation → pass with cost/tokens |
| `test_probe_claude_fail_parse_error` | invoke_claude raises → fail with error |

**Capability & Overall:**

| Test | What it verifies |
|------|-----------------|
| `test_compute_capabilities_all_pass` | All probes pass → all capabilities true |
| `test_compute_capabilities_untested_counts_as_ok` | UNTESTED probe still enables capability |
| `test_compute_capabilities_not_installed` | NOT_INSTALLED → capability false |
| `test_compute_overall_pass` | All installed pass → OverallStatus.PASS |
| `test_compute_overall_degraded` | One installed fails → OverallStatus.DEGRADED |
| `test_compute_overall_fail` | pymupdf fails → OverallStatus.FAIL |
| `test_compute_overall_untested_not_degraded` | UNTESTED does not trigger degraded |

**Output & CLI:**

| Test | What it verifies |
|------|-----------------|
| `test_format_json_valid` | JSON output is valid and has all fields |
| `test_format_json_pages_1_indexed` | Page numbers in JSON are 1-indexed |
| `test_format_json_null_for_missing_content` | `math: null` when no math pages |
| `test_print_table_pages_1_indexed` | Display page numbers are 1-indexed |
| `test_print_table_missing_content_message` | "no math-garbled pages found" shown |
| `test_exit_code_pass` | Overall pass → exit 0 |
| `test_exit_code_degraded` | Overall degraded → exit 1 |
| `test_exit_code_fail` | Overall fail → exit 2 |
| `test_check_multiple_files_errors` | `--check` with directory of files → error |
| `test_check_json_implies_check` | `--check-json` sets `args.check = True` |

### Integration Test (manual)

Run `agentic-mbse extract --check` on a real PDF with all components installed. Verify:
- All 6 probes complete
- Claude probe shows cost
- Table output is readable with 1-indexed page numbers
- `--check-json` produces valid JSON with 1-indexed pages
- Exit code is 0

---

## Files Changed

| File | Change | New/Modified |
|------|--------|-------------|
| `src/agentic_mbse/extraction/check.py` | New module: probes, page selection, formatting, orchestrator | **New** |
| `src/agentic_mbse/cli/extract_cli.py` | Add `--check` and `--check-json` flags, early return in `cmd_extract()` | Modified |
| `tests/test_check.py` | Unit tests for all probes, page selection, output, exit codes | **New** |

Modules NOT modified: `pipeline.py`, `tables.py`, `claude_enhance.py`, `pandoc_convert.py`, `pymupdf_backend.py`, `quality_gate.py`, `types.py` — all probe logic calls existing functions without changes.

**Cross-module imports from `check.py`** (Minor #1 — documented coupling):
- `tables._detect_gmft`, `tables._detect_img2table` — stable internal functions, same-package
- `pandoc_convert._pandoc_available` — trivial `shutil.which` wrapper
- `quality_gate._assess_math_garbling` — pure function, stable signature
- All public: `pymupdf_backend.extract_pages`, `claude_enhance.invoke_claude`, `claude_enhance.render_page_image`, `pandoc_convert.detect_arxiv_id`, `pandoc_convert.check_arxiv_html`, `pandoc_convert.convert_arxiv_html`, `tables.count_pipe_rows`

---

Next Step: After approval → `/_my_plan` or `/_my_implement`
