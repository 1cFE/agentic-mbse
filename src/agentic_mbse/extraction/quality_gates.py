"""Quality detection between extraction layers.

Examines post-processed markdown and identifies regions that need
escalation to Layer 2 (GMFT) or Layer 3 (AI repair).  Returns a list
of :class:`RepairRequest` objects sorted by confidence.
"""

from __future__ import annotations

import re

from agentic_mbse.extraction.base import RepairRequest

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


def detect_broken_tables(md: str) -> list[RepairRequest]:
    """Detect pipe tables with broken structure.

    Also detects non-pipe table indicators: whitespace-aligned columns
    near "Table N:" captions.
    """
    lines = md.split("\n")
    requests: list[RepairRequest] = []

    # Check pipe tables for validity
    for start, end, block_text in _extract_table_blocks(lines):
        if not _is_table_valid(block_text):
            requests.append(
                RepairRequest(
                    page_num=-1,  # unknown at this point
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
                requests.append(
                    RepairRequest(
                        page_num=-1,
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


def detect_garbled_equations(md: str) -> list[RepairRequest]:
    """Detect regions with garbled equations.

    Looks for clusters of U+FFFD replacement characters or
    bracket-soup patterns typical of math font extraction failures.
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
            requests.append(
                RepairRequest(
                    page_num=-1,
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
    """Run all quality detectors and return combined results sorted by confidence."""
    problems: list[RepairRequest] = []
    problems.extend(detect_broken_tables(md))
    problems.extend(detect_garbled_equations(md))
    problems.sort(key=lambda r: r.confidence, reverse=True)
    return problems
