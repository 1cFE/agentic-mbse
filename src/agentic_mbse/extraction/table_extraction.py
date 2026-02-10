"""Layer 2: GMFT-based table extraction.

Uses Microsoft's Table Transformer (via the ``gmft`` library) to detect
and extract tables from PDF page images.  Produces Pandas DataFrames
which are then rendered as markdown pipe tables and spliced into the
document.

GMFT is an **optional** dependency.  When not installed the functions
raise ``ImportError`` which the caller catches to skip Layer 2.
"""

from __future__ import annotations

import time
from pathlib import Path

from agentic_mbse.extraction.base import RepairRequest

# ---------------------------------------------------------------------------
# Singleton model cache — load once, reuse across calls
# ---------------------------------------------------------------------------

_detector = None
_formatter = None


def _get_detector():
    """Return the cached ``AutoTableDetector``, creating it on first use."""
    global _detector
    if _detector is None:
        from gmft import AutoTableDetector  # type: ignore[import-untyped]

        _detector = AutoTableDetector()
    return _detector


def _get_formatter():
    """Return the cached ``AutoTableFormatter``, creating it on first use."""
    global _formatter
    if _formatter is None:
        from gmft import AutoTableFormatter  # type: ignore[import-untyped]

        _formatter = AutoTableFormatter()
    return _formatter


def is_gmft_available() -> bool:
    """Check if the ``gmft`` package is importable."""
    try:
        import gmft  # type: ignore[import-untyped]  # noqa: F401

        return True
    except ImportError:
        return False


def dataframe_to_pipe_table(df) -> str:  # pd.DataFrame
    """Convert a Pandas DataFrame to a markdown pipe table string."""
    import pandas as pd  # noqa: F811

    if df.empty:
        return ""

    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    separator = "| " + " | ".join("---" for _ in cols) + " |"

    def _fmt(v):
        if pd.isna(v):
            return ""
        if isinstance(v, float) and v == int(v):
            return str(int(v))
        return str(v)

    rows = []
    for _, row in df.iterrows():
        cells = "| " + " | ".join(_fmt(v) for v in row) + " |"
        rows.append(cells)

    return "\n".join([header, separator, *rows])


def extract_tables_from_page(
    pdf_path: Path,
    page_num: int,
) -> list:  # list[pd.DataFrame]
    """Extract tables from a single PDF page using GMFT.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    page_num:
        0-indexed page number.

    Returns
    -------
    list[pd.DataFrame]
        One DataFrame per detected table.  Empty list if no tables found.
    """
    from gmft.pdf_bindings import PyPDFium2Document  # type: ignore[import-untyped]

    detector = _get_detector()
    formatter = _get_formatter()

    doc = PyPDFium2Document(str(pdf_path))
    try:
        if page_num >= len(doc):
            return []
        page = doc[page_num]
        tables = detector.detect(page)
        results = []
        for table in tables:
            try:
                ft = formatter.extract(table)
                df = ft.df()
                if df is not None and not df.empty:
                    results.append(df)
            except Exception:
                continue
        return results
    finally:
        doc.close()


# Default timeouts (seconds)
PER_PAGE_TIMEOUT = 30
TOTAL_TIMEOUT = 120


def enhance_tables(
    md: str,
    pdf_path: Path,
    repair_requests: list[RepairRequest],
    *,
    per_page_timeout: int = PER_PAGE_TIMEOUT,
    total_timeout: int = TOTAL_TIMEOUT,
) -> tuple[str, list[RepairRequest]]:
    """Attempt to fix broken tables using GMFT.

    For each table ``RepairRequest``, runs GMFT on the corresponding PDF
    page.  If GMFT produces a valid DataFrame, replaces the broken table
    region in the markdown.

    Parameters
    ----------
    md:
        Full document markdown text.
    pdf_path:
        Path to the source PDF.
    repair_requests:
        Table repair requests from quality detection.
    per_page_timeout:
        Maximum seconds for a single page extraction. If the first page
        exceeds this, all remaining requests are skipped.
    total_timeout:
        Maximum total seconds for all table enhancements combined.

    Returns
    -------
    tuple[str, list[RepairRequest]]
        Updated markdown and list of requests that GMFT couldn't fix
        (for Layer 3 escalation).
    """
    if not repair_requests:
        return md, []

    lines = md.split("\n")
    remaining: list[RepairRequest] = []
    t_start = time.monotonic()

    # Process in reverse order so line indices stay valid
    for req in sorted(repair_requests, key=lambda r: r.markdown_lines[0], reverse=True):
        if req.region_type != "table":
            remaining.append(req)
            continue

        # Check total time budget
        elapsed = time.monotonic() - t_start
        if elapsed > total_timeout:
            remaining.append(req)
            continue

        page = req.page_num
        if page < 0:
            remaining.append(req)
            continue

        try:
            t_page_start = time.monotonic()
            dfs = extract_tables_from_page(pdf_path, page)
            t_page_elapsed = time.monotonic() - t_page_start

            # If first GMFT call took too long, bail on remaining
            if t_page_elapsed > per_page_timeout:
                remaining.append(req)
                # Skip all remaining table requests
                remaining.extend(
                    r
                    for r in sorted(
                        repair_requests, key=lambda r: r.markdown_lines[0], reverse=True
                    )
                    if r.region_type == "table"
                    and r.markdown_lines[0] < req.markdown_lines[0]
                    and r not in remaining
                )
                break
        except Exception:
            remaining.append(req)
            continue

        if not dfs:
            remaining.append(req)
            continue

        # Use the first (largest) table from the page
        best_df = max(dfs, key=lambda df: df.size)
        pipe_table = dataframe_to_pipe_table(best_df)

        if not pipe_table:
            remaining.append(req)
            continue

        start, end = req.markdown_lines
        start = max(0, start)
        end = min(len(lines), end)
        lines[start:end] = pipe_table.split("\n")

    return "\n".join(lines), remaining
