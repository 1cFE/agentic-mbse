"""Ensemble table detection, filtering, quality assessment, and enhancement.

Provides three table detectors (GMFT, Img2Table, Docling stub), secondary
filters (prose cell length, layout artifacts), quality assessment for Claude
enhancement routing, and markdown table utilities.

All external dependencies (GMFT, Img2Table) are guarded by lazy import
with ``try/except ImportError`` for graceful degradation.
"""

from __future__ import annotations

import logging
import re
import tempfile
import time
from pathlib import Path

from agentic_mbse.extraction.types import CostRecord, DetectedTable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt constant — embedded from tests/corpus/prompts/extract_table_cropped.txt
# ---------------------------------------------------------------------------

_TABLE_EXTRACTION_PROMPT = """\
Extract this table as a markdown pipe table.
Rules:
- Use | column headers | separated | by pipes |
- Include separator row (|---|---|---|)
- Preserve ALL numerical values exactly as printed
- Preserve merged/spanning cells by repeating values
- Output ONLY the markdown table, no commentary"""

# ---------------------------------------------------------------------------
# Module-level singleton caches for GMFT detectors
# ---------------------------------------------------------------------------

_gmft_detector = None
_gmft_formatter = None


# ---------------------------------------------------------------------------
# Markdown table detection helpers
# ---------------------------------------------------------------------------

_COL_HEADER_RE = re.compile(r"\bCol\d+\b")
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")


def _is_separator_row(line: str) -> bool:
    """Check if a line is a markdown table separator (e.g. ``|---|---|``)."""
    return bool(_SEPARATOR_RE.match(line.strip()))


def _count_data_rows(markdown: str) -> int:
    """Count data rows in a markdown pipe table (excludes header and separator)."""
    table_lines = [
        line for line in markdown.split("\n") if _is_table_row(line)
    ]
    if not table_lines:
        return 0
    separators = sum(1 for line in table_lines if _is_separator_row(line))
    # header rows = number of separator rows (one header per separator)
    return max(0, len(table_lines) - separators * 2)


def _is_table_row(line: str) -> bool:
    """Check if a line is a real pipe-table row (starts with |, has >= 2 pipes).

    Lines with pipes embedded in running text (equation bars like v|| or |phi|^2)
    are NOT table rows — they don't start with |.
    """
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def count_pipe_rows(markdown: str) -> int:
    """Count lines with >= 2 pipe characters."""
    count = 0
    for line in markdown.split("\n"):
        if line.count("|") >= 2:
            count += 1
    return count


def has_br_in_tables(markdown: str) -> bool:
    """Check if any real table rows contain <br> artifacts."""
    for line in markdown.split("\n"):
        if _is_table_row(line) and "<br>" in line.lower():
            return True
    return False


def has_col_headers(markdown: str) -> bool:
    """Check if table rows have auto-generated ColN headers (Col1, Col2, etc.)."""
    for line in markdown.split("\n"):
        if _is_table_row(line) and _COL_HEADER_RE.search(line):
            return True
    return False


def strip_pipe_tables(markdown: str) -> str:
    """Remove all pipe-table blocks from markdown.

    Only strips blocks of real table rows (starting with |).  Preserves
    equation bars and other lines with incidental pipe characters.
    """
    lines = markdown.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

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


def insert_tables_at_end(
    page_markdown: str, tables: list[DetectedTable]
) -> str:
    """Append tables at the end of a page's markdown."""
    parts = [page_markdown.rstrip()]

    for table in tables:
        parts.append("")
        parts.append(table.markdown)
        parts.append("")

    return "\n".join(parts)


def replace_tables(
    page_markdown: str, tables: list[DetectedTable]
) -> str:
    """Replace all pipe tables in page markdown with provided tables."""
    stripped = strip_pipe_tables(page_markdown)
    return insert_tables_at_end(stripped, tables)


# ---------------------------------------------------------------------------
# DataFrame to pipe table conversion (copied from table_extraction.py:57-79)
# ---------------------------------------------------------------------------


def _dataframe_to_pipe_table(df) -> str:
    """Convert a Pandas DataFrame to a markdown pipe table string."""
    import pandas as pd

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


# ---------------------------------------------------------------------------
# Table filtering
# ---------------------------------------------------------------------------


def filter_tables(
    tables: list[DetectedTable],
) -> tuple[list[DetectedTable], list[str]]:
    """Filter out likely false-positive detected tables.

    No confidence filter — only prose cell length and layout artifact
    filters.  Tables with ``extraction_failed=True`` pass through
    without filtering (Claude handles them).

    Returns ``(kept_tables, filter_reasons)``.
    """
    kept: list[DetectedTable] = []
    reasons: list[str] = []

    for i, table in enumerate(tables):
        tag = (
            f"table {i + 1} "
            f"({table.num_rows}r\u00d7{table.num_cols}c, "
            f"detector={table.detector})"
        )

        if table.extraction_failed:
            kept.append(table)
            reasons.append(f"PASS {tag}: extraction_failed (needs Claude)")
            continue

        if table.avg_cell_length > 80:
            reasons.append(
                f"REJECT {tag}: avg cell {table.avg_cell_length:.0f} > 80 (prose)"
            )
            continue

        if table.num_rows == 1 and table.num_cols > 4:
            reasons.append(
                f"REJECT {tag}: single row, {table.num_cols} cols (layout artifact)"
            )
            continue

        kept.append(table)
        reasons.append(f"KEEP {tag}")

    return kept, reasons


# ---------------------------------------------------------------------------
# Table quality assessment
# ---------------------------------------------------------------------------


def assess_table_quality(table: DetectedTable) -> tuple[bool, list[str]]:
    """Assess whether a detected table needs Claude enhancement.

    Primary trigger: ``extraction_failed=True``
    Secondary trigger: suspect quality (very few rows with many columns)

    Returns ``(needs_enhancement, reasons)``.
    """
    reasons: list[str] = []

    if table.extraction_failed:
        reasons.append(
            "Extraction failed: detector found table but DataFrame was null/empty"
        )
        return True, reasons

    if table.image_path is None:
        return False, []

    # Suspect: very few data rows for a table that was detected
    if table.num_rows <= 1 and table.num_cols >= 3:
        reasons.append(
            f"Suspect: only {table.num_rows} row(s) with {table.num_cols} columns"
        )
        return True, reasons

    return False, []


# ---------------------------------------------------------------------------
# Shared detection helpers
# ---------------------------------------------------------------------------


def _save_table_image(
    table,
    image_dir: Path | None,
    page_idx: int,
    table_idx: int,
    detector_name: str,
) -> Path | None:
    """Save a cropped table image to *image_dir*.  Returns the path or None."""
    if image_dir is None:
        return None
    try:
        img = table.image(dpi=200)
        img_file = image_dir / f"page_{page_idx:03d}_table_{table_idx}.png"
        img.save(str(img_file))
        return img_file
    except Exception as exc:
        logger.warning(
            f"Failed to save {detector_name} table image "
            f"p{page_idx} t{table_idx}: {exc}"
        )
        return None


def _dataframe_to_detected_table(
    df,
    confidence: float,
    image_path: Path | None,
    detector: str,
) -> DetectedTable:
    """Convert a DataFrame extraction result to a DetectedTable.

    If *df* is ``None`` or empty, returns a table with
    ``extraction_failed=True``.
    """
    if df is None or df.empty:
        return DetectedTable(
            markdown="",
            confidence=confidence,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            image_path=image_path,
            extraction_failed=True,
            detector=detector,
            source=detector,
        )

    table_md = _dataframe_to_pipe_table(df)
    num_rows = len(df)
    num_cols = len(df.columns)

    cell_lengths = []
    for col in df.columns:
        for val in df[col]:
            s = str(val).strip()
            if s and s != "nan":
                cell_lengths.append(len(s))
    avg_cell = (
        sum(cell_lengths) / len(cell_lengths) if cell_lengths else 0.0
    )

    return DetectedTable(
        markdown=table_md,
        confidence=confidence,
        num_rows=num_rows,
        num_cols=num_cols,
        avg_cell_length=avg_cell,
        image_path=image_path,
        extraction_failed=False,
        detector=detector,
        source=detector,
    )


# ---------------------------------------------------------------------------
# Ensemble table detection
# ---------------------------------------------------------------------------


def _detect_gmft(
    pdf_path: Path, save_images: bool = True
) -> dict[int, list[DetectedTable]]:
    """Detect tables using GMFT's AutoTableDetector.

    Returns dict mapping 0-indexed page number to list of DetectedTable.
    Returns empty dict if GMFT is not installed.
    """
    try:
        from gmft.auto import AutoTableDetector, AutoTableFormatter
        from gmft.pdf_bindings.pdfium import PyPDFium2Document
    except ImportError:
        return {}

    global _gmft_detector, _gmft_formatter
    if _gmft_detector is None:
        _gmft_detector = AutoTableDetector()
        _gmft_formatter = AutoTableFormatter()

    image_dir = Path(tempfile.mkdtemp(prefix="gmft_")) if save_images else None

    doc = PyPDFium2Document(str(pdf_path))
    result: dict[int, list[DetectedTable]] = {}

    try:
        for page_idx in range(len(doc)):
            try:
                page = doc.get_page(page_idx)
                tables = _gmft_detector.extract(page)
                if not tables:
                    continue

                page_tables: list[DetectedTable] = []
                for table_idx, table in enumerate(tables):
                    try:
                        image_path = _save_table_image(
                            table, image_dir, page_idx, table_idx, "GMFT"
                        )

                        ft = _gmft_formatter.extract(table)
                        df = ft.df()

                        page_tables.append(
                            _dataframe_to_detected_table(
                                df,
                                confidence=table.confidence_score,
                                image_path=image_path,
                                detector="gmft",
                            )
                        )
                    except Exception as exc:
                        logger.warning(
                            f"GMFT extraction failed for table on page {page_idx}: "
                            f"{exc}"
                        )
                        continue

                if page_tables:
                    result[page_idx] = page_tables

            except Exception as exc:
                logger.warning(f"GMFT failed on page {page_idx}: {exc}")
                continue
    finally:
        doc.close()

    return result


def _detect_img2table(
    pdf_path: Path,
    gmft_pages: set[int],
    save_images: bool = True,
) -> dict[int, list[DetectedTable]]:
    """Detect tables using Img2Table on pages where GMFT found nothing.

    Returns empty dict if Img2Table is not installed.
    """
    try:
        from gmft.auto import AutoTableFormatter
        from gmft.detectors.img2table import (
            Img2TableDetector,
            Img2TableDetectorConfig,
        )
        from gmft.pdf_bindings.pdfium import PyPDFium2Document
    except ImportError:
        return {}

    config = Img2TableDetectorConfig(borderless_tables=True)
    detector = Img2TableDetector(config)
    formatter = AutoTableFormatter()

    image_dir = (
        Path(tempfile.mkdtemp(prefix="img2table_")) if save_images else None
    )

    doc = PyPDFium2Document(str(pdf_path))
    result: dict[int, list[DetectedTable]] = {}

    try:
        for page_idx in range(len(doc)):
            if page_idx in gmft_pages:
                continue

            try:
                page = doc.get_page(page_idx)
                tables = detector.detect(page)
                if not tables:
                    continue

                page_tables: list[DetectedTable] = []
                for table_idx, table in enumerate(tables):
                    try:
                        image_path = _save_table_image(
                            table, image_dir, page_idx, table_idx, "Img2Table"
                        )

                        ft = formatter.extract(table)
                        df = ft.df()

                        page_tables.append(
                            _dataframe_to_detected_table(
                                df,
                                confidence=1.0,
                                image_path=image_path,
                                detector="img2table",
                            )
                        )
                    except Exception as exc:
                        logger.warning(
                            "Img2Table extraction failed for table on "
                            f"page {page_idx}: {exc}"
                        )
                        continue

                if page_tables:
                    result[page_idx] = page_tables

            except Exception as exc:
                logger.warning(f"Img2Table failed on page {page_idx}: {exc}")
                continue
    finally:
        doc.close()

    return result


def _detect_docling(
    pdf_path: Path, covered_pages: set[int]
) -> dict[int, list[DetectedTable]]:
    """Detect tables using Docling MCP integration.

    Stub — returns empty dict.  Full implementation requires MCP server
    integration (out of scope for Item 2).
    """
    return {}


def detect_tables_ensemble(
    pdf_path: Path,
    save_images: bool = True,
    enable_img2table: bool = True,
    enable_docling: bool = False,
) -> dict[int, list[DetectedTable]]:
    """Run ensemble table detection: GMFT -> Img2Table -> Docling.

    GMFT runs on all pages.  Img2Table runs only on pages where GMFT
    found nothing.  Docling (when enabled) runs on remaining uncovered
    pages.

    Returns dict mapping 0-indexed page number to list of DetectedTable.
    """
    result = _detect_gmft(pdf_path, save_images=save_images)
    gmft_pages = set(result.keys())

    if enable_img2table:
        img2table_result = _detect_img2table(
            pdf_path, gmft_pages, save_images=save_images
        )
        for page_idx, tables in img2table_result.items():
            result[page_idx] = tables

    if enable_docling:
        covered = set(result.keys())
        docling_result = _detect_docling(pdf_path, covered)
        for page_idx, tables in docling_result.items():
            result[page_idx] = tables

    return result


# ---------------------------------------------------------------------------
# Claude table enhancement
# ---------------------------------------------------------------------------


def enhance_table_with_claude(
    table: DetectedTable,
    model: str = "sonnet",
    timeout: int = 120,
) -> tuple[DetectedTable, CostRecord]:
    """Enhance a single table using Claude vision on its cropped image.

    Requires ``table.image_path`` to be set.  When Claude returns empty
    or 0-row output, the returned table has ``markdown=""`` — the caller
    treats this as a confirmed false positive.

    Returns ``(enhanced_table, cost_record)``.
    """
    from agentic_mbse.extraction.claude_enhance import invoke_claude

    if table.image_path is None:
        raise ValueError("Cannot enhance table without image_path")

    prompt = (
        f"Read the image file at {table.image_path.resolve()} "
        f"and extract its content.\n\n{_TABLE_EXTRACTION_PROMPT}"
    )

    start = time.time()
    response = invoke_claude(prompt, model=model, timeout=timeout)
    elapsed = time.time() - start

    markdown = response.get("result", "").strip()

    cost = CostRecord(
        page_num=0,
        cost_usd=response.get("total_cost_usd", 0),
        input_tokens=response.get("usage", {}).get("input_tokens", 0),
        output_tokens=response.get("usage", {}).get("output_tokens", 0),
        model=response.get("model", model),
        elapsed_seconds=elapsed,
        table_index=0,
    )

    # FP filter: empty or no pipe table rows → markdown=""
    pipe_rows = count_pipe_rows(markdown)
    if not markdown or pipe_rows == 0:
        markdown = ""

    enhanced = DetectedTable(
        markdown=markdown,
        confidence=table.confidence,
        num_rows=_count_data_rows(markdown),
        num_cols=table.num_cols,
        avg_cell_length=table.avg_cell_length,
        image_path=table.image_path,
        extraction_failed=False,
        detector=table.detector,
        source="claude_cropped",
    )

    return enhanced, cost
