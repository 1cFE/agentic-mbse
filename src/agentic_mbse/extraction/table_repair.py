"""Two-pass table repair using Claude headless mode.

Pass 1: Identify broken markdown tables (inconsistent column counts,
        missing separator rows).
Pass 2: Send each broken table to ``claude -p`` for repair and replace
        the original in the markdown file.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# A line that looks like a table row: starts with optional whitespace then |
_TABLE_ROW_RE = re.compile(r"^\s*\|")
# Separator row: | followed by dashes/colons separated by pipes
_SEPARATOR_RE = re.compile(r"^\s*\|[\s:]*-+[\s:]*(\|[\s:]*-+[\s:]*)*\|\s*$")


def _count_columns(row: str) -> int:
    """Count the number of columns in a pipe-delimited table row."""
    stripped = row.strip()
    # Remove leading/trailing pipes, split by pipe
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return len(stripped.split("|"))


def _extract_table_blocks(markdown: str) -> list[tuple[str, int, int]]:
    """Extract contiguous table blocks from *markdown*.

    Returns a list of ``(table_text, start_line, end_line)`` tuples where
    line numbers are 0-indexed into the split lines.
    """
    lines = markdown.split("\n")
    blocks: list[tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        if _TABLE_ROW_RE.match(lines[i]):
            start = i
            while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                i += 1
            end = i  # exclusive
            block_text = "\n".join(lines[start:end])
            blocks.append((block_text, start, end))
        else:
            i += 1
    return blocks


def _is_table_valid(block: str) -> bool:
    """Check whether a table block has consistent columns and a separator row."""
    rows = block.strip().split("\n")
    if len(rows) < 2:
        return False

    # Must have a separator row (typically the second row)
    has_separator = any(_SEPARATOR_RE.match(row) for row in rows)
    if not has_separator:
        return False

    # All rows must have the same column count
    counts = [_count_columns(row) for row in rows]
    return len(set(counts)) == 1


def find_broken_tables(markdown: str) -> list[str]:
    """Find broken markdown tables in *markdown*.

    Returns a list of table block strings that fail validation
    (inconsistent column counts or missing separator row).
    """
    blocks = _extract_table_blocks(markdown)
    return [text for text, _start, _end in blocks if not _is_table_valid(text)]


def _call_claude(table_text: str) -> str | None:
    """Call ``claude -p`` to repair a broken table.

    Returns the repaired table text, or ``None`` on failure.
    """
    prompt = (
        "Fix this broken markdown table. Return ONLY the corrected table, "
        "no explanation, no code fences, no extra text:\n\n" + table_text
    )
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def repair_tables(markdown_path: Path) -> bool:
    """Fix broken markdown tables in *markdown_path* using Claude.

    Reads the file, identifies broken tables, sends each to ``claude -p``
    for repair, and replaces them in-place.

    Returns ``True`` if any tables were repaired, ``False`` on no repairs
    or on I/O errors.
    """
    try:
        content = markdown_path.read_text()
    except (OSError, UnicodeDecodeError):
        return False

    blocks = _extract_table_blocks(content)

    broken = [(text, start, end) for text, start, end in blocks if not _is_table_valid(text)]
    if not broken:
        return False

    lines = content.split("\n")
    any_repaired = False

    # Process in reverse order so line indices remain valid after replacement
    for table_text, start, end in reversed(broken):
        fixed = _call_claude(table_text)
        if fixed is not None:
            fixed_lines = fixed.split("\n")
            lines[start:end] = fixed_lines
            any_repaired = True

    if any_repaired:
        try:
            markdown_path.write_text("\n".join(lines))
        except OSError:
            return False

    return any_repaired
