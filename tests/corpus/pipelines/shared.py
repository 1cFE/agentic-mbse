"""Shared utilities for pipeline experiment scripts.

Provides per-page extraction, GMFT table handling, output saving,
and ground truth scoring used by all pipeline hypotheses.
"""

import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Ensure imports work when run from tests/corpus/pipelines/
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf4llm  # type: ignore[import-untyped]
from metrics import (
    ExtractionMetrics,
    AccuracyScore,
    compute_metrics,
    load_ground_truth,
    score_against_ground_truth,
)

CORPUS_DIR = Path(__file__).parent.parent
PAPERS_JSONL = CORPUS_DIR / "papers.jsonl"
PDFS_DIR = CORPUS_DIR / "pdfs"
RUNS_DIR = CORPUS_DIR / "runs"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class PageResult:
    """Per-page extraction result from pymupdf4llm."""

    page_num: int  # 0-indexed
    markdown: str


@dataclass
class GmftTable:
    """A single table detected by GMFT on a page."""

    markdown: str  # Pipe-table markdown
    confidence: float
    num_rows: int  # Data rows (excluding header/separator)
    num_cols: int
    avg_cell_length: float  # Average character length of non-empty cells


@dataclass
class PageDecision:
    """Decision log entry for one page."""

    page_num: int
    action: str  # "keep", "gmft_replace", "gmft_append", "claude_replace", etc.
    reasons: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Paper loading
# ---------------------------------------------------------------------------


def load_papers(slugs: list[str] | None = None) -> list[dict]:
    """Load paper registry, optionally filtering by slug."""
    papers = []
    with PAPERS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if line:
                paper = json.loads(line)
                if slugs is None or paper["slug"] in slugs:
                    papers.append(paper)
    return papers


def get_pdf_path(slug: str) -> Path | None:
    """Get absolute PDF path for a slug."""
    papers = load_papers([slug])
    if not papers:
        return None
    rel_path = papers[0]["pdf_path"]
    # papers.jsonl paths are relative to repo root
    repo_root = CORPUS_DIR.parent.parent
    pdf_path = repo_root / rel_path
    return pdf_path if pdf_path.exists() else None


# ---------------------------------------------------------------------------
# pymupdf4llm per-page extraction
# ---------------------------------------------------------------------------

# CompositeHeaderDetector from experiment.py — re-implemented here to avoid
# importing the full experiment module with its heavy dependencies.


def _bold_header_detector(span, page=None):
    """Bold-based header detector matching experiment.py's _bold_header_detector."""
    text = span["text"].strip()
    if not text:
        return ""
    is_bold = bool(span["flags"] & 16)
    if not is_bold:
        return ""

    # Arabic numbered sections
    m = re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Z]", text)
    if m:
        sec_num = text.split()[0].rstrip(".")
        depth = sec_num.count(".") + 1
        return "#" * min(depth + 1, 6) + " "

    # Roman numeral sections
    m = re.match(r"^(X{0,3})(IX|IV|V?I{0,3})\.?\s+[A-Z]", text)
    if m and (m.group(1) or m.group(2)):
        return "## "

    # All-caps short titles
    if text.isupper() and len(text) < 60 and len(text.split()) <= 6:
        return "## "

    return ""


class _CompositeHeaderDetector:
    """Combines font-size + bold pattern detection. Matches experiment.py."""

    def __init__(self):
        self._identify_headers = None
        self._current_doc_name = None

    def _ensure_initialized(self, page):
        if page is None:
            return
        doc = page.parent
        doc_name = doc.name if doc else None
        if doc_name != self._current_doc_name:
            self._current_doc_name = doc_name
            try:
                from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders
                self._identify_headers = IdentifyHeaders(doc)
            except Exception:
                self._identify_headers = None

    def get_header_id(self, span, page=None):
        self._ensure_initialized(page)
        bold_result = _bold_header_detector(span, page)
        font_result = ""
        if self._identify_headers is not None:
            try:
                font_result = self._identify_headers.get_header_id(span, page)
            except Exception:
                font_result = ""
        if bold_result and font_result:
            return bold_result if len(bold_result) > len(font_result) else font_result
        return bold_result or font_result

    def __call__(self, span, page=None):
        return self.get_header_id(span, page)


BEST_V1_PARAMS = {
    "write_images": False,
    "dpi": 150,
    "page_chunks": True,  # Per-page output
    "table_strategy": "lines",
    "force_text": True,
    "ignore_code": True,
    "hdr_info": _CompositeHeaderDetector(),
}


def extract_pymupdf_pages(pdf_path: Path, params: dict | None = None) -> list[PageResult]:
    """Extract per-page markdown with pymupdf4llm.

    Uses page_chunks=True to get per-page results with full-document header
    calibration (IdentifyHeaders scans all pages for font statistics).

    Args:
        pdf_path: Path to PDF file.
        params: pymupdf4llm params. Defaults to BEST_V1_PARAMS.

    Returns:
        List of PageResult, one per page (0-indexed).
    """
    if params is None:
        params = dict(BEST_V1_PARAMS)
    else:
        params = dict(params)

    # Force page_chunks=True for per-page output
    params["page_chunks"] = True

    chunks = pymupdf4llm.to_markdown(str(pdf_path), **params)

    results = []
    for chunk in chunks:
        page_num = chunk["metadata"]["page"] - 1  # Convert 1-indexed to 0-indexed
        results.append(PageResult(page_num=page_num, markdown=chunk["text"]))

    return results


# ---------------------------------------------------------------------------
# GMFT per-page table extraction
# ---------------------------------------------------------------------------


def extract_gmft_pages(pdf_path: Path) -> dict[int, list[GmftTable]]:
    """Extract tables per page using GMFT.

    Returns:
        Dict mapping 0-indexed page number to list of GmftTable objects.
    """
    from gmft.auto import AutoTableDetector, AutoTableFormatter
    from gmft.pdf_bindings.pdfium import PyPDFium2Document

    detector = AutoTableDetector()
    formatter = AutoTableFormatter()

    doc = PyPDFium2Document(str(pdf_path))
    pages_tables: dict[int, list[GmftTable]] = {}

    try:
        for page_idx in range(len(doc)):
            page = doc.get_page(page_idx)
            tables = detector.extract(page)
            if not tables:
                continue

            page_tables = []
            for table in tables:
                try:
                    ft = formatter.extract(table)
                    df = ft.df()
                    if df is None or df.empty:
                        continue

                    table_md = df.to_markdown(index=False)
                    num_rows = len(df)
                    num_cols = len(df.columns)

                    # Compute average cell text length (non-empty cells)
                    cell_lengths = []
                    for col in df.columns:
                        for val in df[col]:
                            s = str(val).strip()
                            if s and s != "nan":
                                cell_lengths.append(len(s))
                    avg_cell = sum(cell_lengths) / len(cell_lengths) if cell_lengths else 0

                    page_tables.append(GmftTable(
                        markdown=table_md,
                        confidence=table.confidence_score,
                        num_rows=num_rows,
                        num_cols=num_cols,
                        avg_cell_length=avg_cell,
                    ))
                except Exception:
                    continue

            if page_tables:
                pages_tables[page_idx] = page_tables
    finally:
        doc.close()

    return pages_tables


# ---------------------------------------------------------------------------
# GMFT false-positive filter
# ---------------------------------------------------------------------------


def filter_gmft_tables(
    tables: list[GmftTable],
    page_num: int,
) -> tuple[list[GmftTable], list[str]]:
    """Filter out likely false-positive GMFT tables.

    Returns:
        (kept_tables, rejection_reasons) — rejected tables get a reason logged.

    Heuristics based on Stage 1-2 analysis:
    - Confidence < 0.98: title blocks, abstracts, metadata (hansen p1, hsu p1)
    - Average cell length > 80 chars: description lists, prose blocks (hsu p6-7)
    - Single data row with many columns: layout artifacts (hsu CAS descriptions)
    """
    kept = []
    reasons = []

    for i, table in enumerate(tables):
        tag = f"table {i + 1} (conf={table.confidence:.2f}, {table.num_rows}r×{table.num_cols}c)"

        # Low confidence → likely false positive
        if table.confidence < 0.98:
            reasons.append(f"REJECT {tag}: confidence < 0.98")
            continue

        # Long prose cells → likely description block, not data table
        if table.avg_cell_length > 80:
            reasons.append(f"REJECT {tag}: avg cell length {table.avg_cell_length:.0f} > 80 (prose)")
            continue

        # Single-row table with many columns → layout artifact
        if table.num_rows == 1 and table.num_cols > 4:
            reasons.append(f"REJECT {tag}: single row with {table.num_cols} columns (layout artifact)")
            continue

        kept.append(table)
        reasons.append(f"KEEP {tag}")

    return kept, reasons


# ---------------------------------------------------------------------------
# Markdown table detection helpers
# ---------------------------------------------------------------------------

# A "table block" in markdown is a contiguous group of lines where each line
# has at least 2 pipe characters.  We also include blank lines adjacent to
# the block and any preceding bold label like "**Table N**".

_PIPE_LINE_RE = re.compile(r"^.*\|.*\|.*$")
_COL_HEADER_RE = re.compile(r"\bCol\d+\b")


def _is_table_row(line: str) -> bool:
    """Check if a line is a real pipe-table row (starts with |, has >= 2 pipes).

    Lines with pipes embedded in running text (equation bars like v|| or |ϕ|²)
    are NOT table rows — they don't start with |.
    """
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def count_pipe_rows(markdown: str) -> int:
    """Count lines with >= 2 pipe characters (matches metrics.py definition)."""
    count = 0
    for line in markdown.split("\n"):
        if line.count("|") >= 2:
            count += 1
    return count


def count_real_table_rows(markdown: str) -> int:
    """Count real table rows (lines starting with | that have >= 2 pipes).

    Excludes equation bars (v||, |ϕ|²) embedded in running text.
    """
    return sum(1 for line in markdown.split("\n") if _is_table_row(line))


def has_br_in_tables(markdown: str) -> bool:
    """Check if any real table rows contain <br> artifacts."""
    for line in markdown.split("\n"):
        if _is_table_row(line) and "<br>" in line.lower():
            return True
    return False


def has_col_headers(markdown: str) -> bool:
    """Check if table rows have auto-generated ColN headers (Col1, Col2, etc.).

    pymupdf4llm generates ColN headers when it can't determine real column
    names — a strong signal that the "table" is actually a diagram or figure.
    """
    for line in markdown.split("\n"):
        if _is_table_row(line) and _COL_HEADER_RE.search(line):
            return True
    return False


def strip_pipe_tables(markdown: str) -> str:
    """Remove all pipe-table blocks from markdown.

    Only strips blocks of real table rows (starting with |). Preserves
    equation bars and other lines with incidental pipe characters.
    """
    lines = markdown.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a table block (real table rows)
        if _is_table_row(line):
            # Skip the entire table block
            while i < len(lines) and _is_table_row(lines[i]):
                i += 1
            # Also skip trailing blank lines after table
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue

        result.append(line)
        i += 1

    return "\n".join(result)


def insert_tables_at_end(page_markdown: str, gmft_tables: list[GmftTable]) -> str:
    """Append GMFT tables at the end of a page's markdown."""
    parts = [page_markdown.rstrip()]

    for i, table in enumerate(gmft_tables):
        parts.append("")
        parts.append(table.markdown)
        parts.append("")

    return "\n".join(parts)


def replace_tables(page_markdown: str, gmft_tables: list[GmftTable]) -> str:
    """Replace all pipe tables in page markdown with GMFT tables."""
    # Strip existing tables
    stripped = strip_pipe_tables(page_markdown)

    # Append GMFT tables
    return insert_tables_at_end(stripped, gmft_tables)


# ---------------------------------------------------------------------------
# Output saving
# ---------------------------------------------------------------------------


def save_pipeline_result(
    run_name: str,
    slug: str,
    markdown: str,
    elapsed: float,
    decisions: list[PageDecision],
    extra_data: dict | None = None,
) -> Path:
    """Save pipeline results in standard experiment format.

    Creates:
        runs/pipeline_{run_name}/{slug}/output.md
        runs/pipeline_{run_name}/{slug}/metrics.json
        runs/pipeline_{run_name}/{slug}/decisions.json

    Returns:
        Path to the slug output directory.
    """
    run_dir = RUNS_DIR / f"pipeline_{run_name}" / slug
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save output markdown
    (run_dir / "output.md").write_text(markdown)

    # Compute and save metrics
    metrics = compute_metrics(markdown, elapsed)
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics.to_dict(), indent=2) + "\n"
    )

    # Save decisions
    decisions_data = [asdict(d) for d in decisions]
    (run_dir / "decisions.json").write_text(
        json.dumps(decisions_data, indent=2) + "\n"
    )

    # Save any extra data (e.g., cost tracking)
    if extra_data:
        (run_dir / "extra.json").write_text(
            json.dumps(extra_data, indent=2) + "\n"
        )

    return run_dir


# ---------------------------------------------------------------------------
# Ground truth scoring
# ---------------------------------------------------------------------------


def score_and_print(slug: str, metrics: ExtractionMetrics) -> dict[str, AccuracyScore | None]:
    """Score metrics against ground truth and print results.

    Returns:
        Accuracy scores dict (same as score_against_ground_truth).
    """
    gt_map = load_ground_truth()
    gt = gt_map.get(slug)

    if gt is None:
        print(f"  {slug}: no ground truth available")
        return {"headings": None, "table_rows": None}

    scores = score_against_ground_truth(metrics, gt)

    parts = [f"  {slug}:"]
    for dim, score in scores.items():
        if score is not None:
            sign = "+" if score.delta > 0 else ""
            parts.append(
                f"    {dim}: {score.detected} vs GT {score.ground_truth} "
                f"({sign}{score.delta}, {score.error_pct:.0f}% error, {score.category})"
            )
    print("\n".join(parts))

    return scores


def save_config(run_name: str, config: dict) -> None:
    """Save pipeline config for reproducibility."""
    run_dir = RUNS_DIR / f"pipeline_{run_name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(
        json.dumps(config, indent=2) + "\n"
    )
