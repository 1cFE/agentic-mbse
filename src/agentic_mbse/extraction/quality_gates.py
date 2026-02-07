"""Quality detection between extraction layers.

Examines post-processed markdown and identifies regions that need
escalation to Layer 2 (GMFT) or Layer 3 (AI repair).  Returns a list
of :class:`RepairRequest` objects sorted by confidence.
"""

from __future__ import annotations

import re

from agentic_mbse.extraction.base import RepairRequest

# ---------------------------------------------------------------------------
# Page marker resolution
# ---------------------------------------------------------------------------

# Matches <!-- PAGE:N --> markers inserted by pymupdf_backend
_PAGE_MARKER_RE = re.compile(r"^<!--\s*PAGE:(\d+)\s*-->$")


def _build_page_map(lines: list[str]) -> list[int]:
    """Build a mapping from line index to 0-indexed PDF page number.

    Scans for ``<!-- PAGE:N -->`` markers and assigns each line the
    page number of the most recent marker above it.  Lines before the
    first marker get page -1 (unknown).

    pymupdf4llm emits 1-indexed page numbers in its metadata, so
    this function subtracts 1 to produce 0-indexed values that match
    GMFT's ``PyPDFium2Document`` indexing.
    """
    page_map = []
    current_page = -1
    for line in lines:
        m = _PAGE_MARKER_RE.match(line.strip())
        if m:
            current_page = int(m.group(1)) - 1  # convert 1-indexed → 0-indexed
        page_map.append(current_page)
    return page_map


# ---------------------------------------------------------------------------
# Table detection
# ---------------------------------------------------------------------------

# A pipe-delimited table row
_TABLE_ROW_RE = re.compile(r"^\s*\|")
# Separator row: | --- | --- |
_SEPARATOR_RE = re.compile(r"^\s*\|[\s:]*-+[\s:]*(\|[\s:]*-+[\s:]*)*\|\s*$")
# "Table N:" or "Table N." caption pattern
_TABLE_CAPTION_RE = re.compile(r"^(?:Table|TABLE)\s+\d+[.:]", re.MULTILINE)
# Lines with whitespace-aligned columns (≥3 chunks separated by 2+ spaces)
_ALIGNED_COLUMNS_RE = re.compile(r"^\S.*?\s{2,}\S.*?\s{2,}\S", re.MULTILINE)


def _count_columns(row: str) -> int:
    """Count pipe-delimited columns in a table row."""
    stripped = row.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return len(stripped.split("|"))


def _extract_table_blocks(lines: list[str]) -> list[tuple[int, int, str]]:
    """Find contiguous pipe-table blocks.

    Returns list of ``(start_line, end_line, block_text)`` with
    0-indexed line numbers.
    """
    blocks: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        if _TABLE_ROW_RE.match(lines[i]):
            start = i
            while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                i += 1
            block_text = "\n".join(lines[start:i])
            blocks.append((start, i, block_text))
        else:
            i += 1
    return blocks


def _is_table_valid(block: str) -> bool:
    """Check whether a pipe table has consistent columns and a separator."""
    rows = block.strip().split("\n")
    if len(rows) < 2:
        return False
    has_separator = any(_SEPARATOR_RE.match(row) for row in rows)
    if not has_separator:
        return False
    counts = [_count_columns(row) for row in rows]
    return len(set(counts)) == 1


def detect_broken_tables(
    md: str,
    page_map: list[int] | None = None,
) -> list[RepairRequest]:
    """Detect pipe tables with broken structure.

    Also detects non-pipe table indicators: whitespace-aligned columns
    near "Table N:" captions.

    Parameters
    ----------
    md:
        Full document markdown text.
    page_map:
        Optional per-line page mapping from :func:`_build_page_map`.
        When provided, ``RepairRequest.page_num`` is set accurately.
    """
    lines = md.split("\n")
    requests: list[RepairRequest] = []

    # Check pipe tables for validity
    for start, end, block_text in _extract_table_blocks(lines):
        if not _is_table_valid(block_text):
            page = page_map[start] if page_map and start < len(page_map) else -1
            requests.append(
                RepairRequest(
                    page_num=page,
                    region_type="table",
                    markdown_lines=(start, end),
                    original_text=block_text,
                    confidence=0.9,
                )
            )

    # Detect non-pipe tables: "Table N:" caption followed by aligned columns
    for m in _TABLE_CAPTION_RE.finditer(md):
        caption_offset = m.start()
        caption_line = md[:caption_offset].count("\n")
        # Look ahead up to 30 lines for aligned whitespace columns
        search_start = caption_line
        search_end = min(caption_line + 30, len(lines))
        region = "\n".join(lines[search_start:search_end])
        aligned_matches = _ALIGNED_COLUMNS_RE.findall(region)
        if len(aligned_matches) >= 2:
            # Check this region isn't already a pipe table
            has_pipe = any(_TABLE_ROW_RE.match(lines[j]) for j in range(search_start, search_end))
            if not has_pipe:
                page = page_map[search_start] if page_map and search_start < len(page_map) else -1
                requests.append(
                    RepairRequest(
                        page_num=page,
                        region_type="table",
                        markdown_lines=(search_start, search_end),
                        original_text=region,
                        confidence=0.8,
                    )
                )

    return requests


# ---------------------------------------------------------------------------
# Equation detection
# ---------------------------------------------------------------------------

# Clusters of U+FFFD replacement characters
_REPLACEMENT_CLUSTER_RE = re.compile(r"(?:\ufffd\s*){3,}")
# Bracket-soup patterns like _[C][AC]_
_BRACKET_SOUP_RE = re.compile(r"(?:[\[_]\w{1,3}[\]_]){2,}")


def detect_garbled_equations(
    md: str,
    page_map: list[int] | None = None,
) -> list[RepairRequest]:
    """Detect regions with garbled equations.

    Looks for clusters of U+FFFD replacement characters or
    bracket-soup patterns typical of math font extraction failures.

    Parameters
    ----------
    md:
        Full document markdown text.
    page_map:
        Optional per-line page mapping from :func:`_build_page_map`.
    """
    lines = md.split("\n")
    requests: list[RepairRequest] = []

    for i, line in enumerate(lines):
        is_garbled = False
        confidence = 0.0

        if _REPLACEMENT_CLUSTER_RE.search(line):
            is_garbled = True
            confidence = 0.9
        elif _BRACKET_SOUP_RE.search(line):
            is_garbled = True
            confidence = 0.7

        if is_garbled:
            # Expand to capture surrounding context (2 lines each side)
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            page = page_map[i] if page_map and i < len(page_map) else -1
            requests.append(
                RepairRequest(
                    page_num=page,
                    region_type="equation",
                    markdown_lines=(start, end),
                    original_text="\n".join(lines[start:end]),
                    confidence=confidence,
                )
            )

    return requests


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def detect_problems(md: str) -> list[RepairRequest]:
    """Run all quality detectors and return combined results sorted by confidence.

    Automatically builds a page map from ``<!-- PAGE:N -->`` markers if
    present, so that ``RepairRequest.page_num`` values are accurate.
    """
    lines = md.split("\n")
    page_map = _build_page_map(lines)

    problems: list[RepairRequest] = []
    problems.extend(detect_broken_tables(md, page_map=page_map))
    problems.extend(detect_garbled_equations(md, page_map=page_map))
    problems.sort(key=lambda r: r.confidence, reverse=True)
    return problems
