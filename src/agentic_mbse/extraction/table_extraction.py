"""Layer 2: GMFT-based table extraction.

Uses Microsoft's Table Transformer (via the ``gmft`` library) to detect
and extract tables from PDF page images.  Produces Pandas DataFrames
which are then rendered as markdown pipe tables and spliced into the
document.

GMFT is an **optional** dependency.  When not installed the functions
raise ``ImportError`` which the caller catches to skip Layer 2.
"""

from __future__ import annotations

from pathlib import Path

from agentic_mbse.extraction.base import RepairRequest


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
    rows = []
    for _, row in df.iterrows():
        cells = "| " + " | ".join(str(v) if pd.notna(v) else "" for v in row) + " |"
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
    from gmft import AutoTableDetector, AutoTableFormatter  # type: ignore[import-untyped]
    from gmft.pdf_bindings import PyPDFium2Document  # type: ignore[import-untyped]

    detector = AutoTableDetector()
    formatter = AutoTableFormatter()

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


def enhance_tables(
    md: str,
    pdf_path: Path,
    repair_requests: list[RepairRequest],
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

    # Process in reverse order so line indices stay valid
    for req in sorted(repair_requests, key=lambda r: r.markdown_lines[0], reverse=True):
        if req.region_type != "table":
            remaining.append(req)
            continue

        page = req.page_num
        if page < 0:
            # Try to estimate page from position in document
            # Rough heuristic: 60 lines per page
            page = req.markdown_lines[0] // 60

        try:
            dfs = extract_tables_from_page(pdf_path, page)
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
