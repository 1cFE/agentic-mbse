"""Per-page extraction quality assessment, routing, and heading anomaly check.

Detects extraction problems that warrant enhancement (GMFT table replacement
or Claude vision re-extraction) and routes pages to the appropriate action.

Promoted from tests/corpus/pipelines/quality_gate.py (Stage 3 experiment code)
with addition of route_page() from design §4.5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from agentic_mbse.extraction.types import (
    DetectedTable,
    PageAction,
    PageAssessment,
    PageDecision,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class QualityGateConfig:
    """Thresholds for quality gate assessment. Defaults match Stage 3 values."""

    math_severity_threshold: float = 1.0
    text_density_min_chars: int = 200
    heading_density_max: float = 3.0
    heading_anomaly_boost: float = 0.5
    # Consumed by _cross_reference_gmft() in pipeline.py, not by quality_gate.py
    # itself. Lives here because it's a quality-assessment threshold alongside
    # the other gate thresholds.
    gmft_xref_severity_boost: float = 1.5


# ---------------------------------------------------------------------------
# Internal detection helpers (from experiment quality_gate.py)
# ---------------------------------------------------------------------------

# Strikethrough-wrapped content: ~~text~~ where text is short (equation fragments)
_STRIKETHROUGH_RE = re.compile(r"~~[^~]{1,40}~~")

# Unicode replacement character
_REPLACEMENT_CHAR = "\ufffd"

# Bracket-encoded fractions: [/], [+], [-] in running text (not in tables)
_GARBLED_FRACTION_RE = re.compile(r"\[([/+\-])\]")

# Isolated Unicode math symbols without LaTeX context
_UNICODE_MATH_RANGES = [
    (0x2200, 0x22FF),  # Mathematical Operators
    (0x2100, 0x214F),  # Letterlike Symbols
    (0x27C0, 0x27EF),  # Miscellaneous Mathematical Symbols-A
]

# Table detection patterns
_COL_HEADER_RE = re.compile(r"\bCol\d+\b")


def _count_strikethroughs(text: str) -> int:
    """Count ~~...~~ sequences (pymupdf4llm uses these around garbled math)."""
    return len(_STRIKETHROUGH_RE.findall(text))


def _count_replacement_chars(text: str) -> int:
    """Count Unicode replacement characters (U+FFFD)."""
    return text.count(_REPLACEMENT_CHAR)


def _count_garbled_fractions(text: str) -> int:
    """Count bracket-encoded operators [/], [+], [-] outside of tables.

    These appear when pymupdf4llm can't properly encode equation operators.
    Only count on lines that are NOT table rows (no leading |).
    """
    count = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|"):
            continue  # Skip table rows
        count += len(_GARBLED_FRACTION_RE.findall(line))
    return count


def _count_unicode_math_symbols(text: str) -> int:
    """Count isolated Unicode math symbols (operators, letterlike)."""
    count = 0
    for char in text:
        code = ord(char)
        for lo, hi in _UNICODE_MATH_RANGES:
            if lo <= code <= hi:
                count += 1
                break
    return count


def _assess_math_garbling(md: str) -> tuple[float, list[str]]:
    """Assess math garbling severity on a page.

    Returns:
        (severity_score, reasons) — score >= 1.0 means page should be flagged.
    """
    reasons = []
    score = 0.0

    # Signal 1: Strikethrough sequences (strongest signal)
    st_count = _count_strikethroughs(md)
    if st_count >= 3:
        score += 2.0
        reasons.append(f"strikethrough sequences: {st_count} (garbled content)")
    elif st_count >= 1:
        score += 0.5
        reasons.append(f"strikethrough sequences: {st_count}")

    # Signal 2: Replacement characters (very strong signal)
    repl_count = _count_replacement_chars(md)
    if repl_count >= 2:
        score += 2.0
        reasons.append(f"replacement chars (\ufffd): {repl_count}")
    elif repl_count >= 1:
        score += 1.0
        reasons.append(f"replacement char (\ufffd): {repl_count}")

    # Signal 3: Bracket-encoded operators outside tables
    frac_count = _count_garbled_fractions(md)
    if frac_count >= 3:
        score += 1.0
        reasons.append(f"bracket-encoded operators: {frac_count}")
    elif frac_count >= 1:
        score += 0.3
        reasons.append(f"bracket-encoded operators: {frac_count}")

    # Signal 4: High Unicode math symbol density (weaker signal)
    # Only matters if combined with other signals
    math_sym_count = _count_unicode_math_symbols(md)
    char_count = len(md)
    if char_count > 0:
        math_density = math_sym_count / char_count
        if math_density > 0.02 and score > 0:
            score += 0.5
            reasons.append(
                f"Unicode math symbol density: {math_density:.3f} "
                f"({math_sym_count} symbols in {char_count} chars)"
            )

    return score, reasons


# Equation-fragment detection patterns
# Standalone equation number on its own line, e.g. "(2.2)" or "(3.1.4)"
_EQUATION_NUMBER_RE = re.compile(r"^\s*\((\d+(?:\.\d+)?)\)\s*$")

# Short italic fragment lines: contains _..._ markers
_ITALIC_MARKER_RE = re.compile(r"_[^_]+_")


def _assess_equation_fragments(md: str) -> tuple[float, list[str]]:
    """Detect equation-fragment rendering failures.

    Looks for isolated equation numbers (e.g., "(2.2)") preceded by
    short lines with heavy italic content — a pattern pymupdf4llm
    produces when it fails to render equations as LaTeX.

    Returns (severity_score, reasons).
    """
    lines = md.split("\n")
    score = 0.0
    reasons: list[str] = []

    for i, line in enumerate(lines):
        if not _EQUATION_NUMBER_RE.match(line.strip()):
            continue

        # Look at preceding non-blank lines (up to 5)
        italic_short_count = 0
        checked = 0
        for j in range(i - 1, -1, -1):
            prev = lines[j].strip()
            if not prev:
                continue
            checked += 1
            if checked > 5:
                break
            if len(prev) < 60 and _ITALIC_MARKER_RE.search(prev):
                italic_short_count += 1

        if italic_short_count >= 2:
            eq_num = line.strip()
            score += 1.0
            reasons.append(
                f"equation fragment: {italic_short_count} short italic lines "
                f"before {eq_num}"
            )

    return score, reasons


def _assess_table_anomaly(md: str) -> tuple[bool, list[str]]:
    """Detect table anomalies on a page.

    Returns:
        (has_anomaly, reasons)
    """
    reasons = []
    has_anomaly = False

    table_lines = []
    for line in md.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            table_lines.append(stripped)

    if not table_lines:
        return False, []

    # Check for <br> artifacts
    br_count = sum(1 for line in table_lines if "<br>" in line.lower())
    if br_count > 0:
        has_anomaly = True
        reasons.append(f"<br> artifacts in {br_count}/{len(table_lines)} table rows")

    # Check for ColN auto-headers (false tables from diagrams)
    col_header_lines = sum(1 for line in table_lines if _COL_HEADER_RE.search(line))
    if col_header_lines > 0:
        has_anomaly = True
        reasons.append(
            f"ColN auto-headers in {col_header_lines}/{len(table_lines)} rows "
            f"(likely diagram/figure falsely detected as table)"
        )

    return has_anomaly, reasons


def _assess_text_density(md: str, min_chars: int) -> tuple[bool, list[str]]:
    """Check if a page has suspiciously low text content.

    Returns:
        (is_low, reasons)
    """
    char_count = len(md.strip())

    if char_count < min_chars:
        return True, [f"very low text density: {char_count} chars (threshold: {min_chars})"]

    return False, []


# ---------------------------------------------------------------------------
# Private helpers for routing (from shared.py — temporary until tables.py)
# ---------------------------------------------------------------------------


def _has_col_headers(md: str) -> bool:
    """Check if table rows have auto-generated ColN headers."""
    for line in md.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            if _COL_HEADER_RE.search(stripped):
                return True
    return False


def _has_br_in_tables(md: str) -> bool:
    """Check if any real table rows contain <br> artifacts."""
    for line in md.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            if "<br>" in stripped.lower():
                return True
    return False


def has_pipe_tables(md: str) -> bool:
    """Check if the markdown contains any pipe table rows.

    Public API — consumed by quality_gate.py routing rules and by
    _cross_reference_gmft() in pipeline.py.
    """
    return any(line.strip().startswith("|") and line.count("|") >= 2 for line in md.split("\n"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def count_headings(markdown: str) -> int:
    """Count ATX headings (lines starting with # followed by space).

    Naive line-by-line check — does NOT track fenced code blocks.
    This matches the experiment code behavior and the metrics.py heading
    counter. Code blocks with # comments are rare in extraction output
    (pymupdf4llm doesn't produce fenced code blocks for PDF content).
    """
    count = 0
    for line in markdown.split("\n"):
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if level > 0 and (level >= len(line) or line[level] in (" ", "\t")):
                count += 1
    return count


def assess_page(
    page_markdown: str,
    page_num: int,
    config: QualityGateConfig | None = None,
) -> PageAssessment:
    """Assess extraction quality for a single page.

    Checks multiple quality dimensions and determines what enhancement
    is needed (if any).

    Args:
        page_markdown: The pymupdf4llm markdown for this page.
        page_num: 0-indexed page number.
        config: Quality gate thresholds. Uses defaults if None.

    Returns:
        PageAssessment with flags for needed enhancements.
    """
    if config is None:
        config = QualityGateConfig()

    assessment = PageAssessment(page_num=page_num)

    # --- Math garbling ---
    math_score, math_reasons = _assess_math_garbling(page_markdown)
    assessment.math_garble_score = math_score
    if math_score >= config.math_severity_threshold:
        assessment.needs_claude = True
        assessment.severity += math_score
        assessment.reasons.extend([f"MATH: {r}" for r in math_reasons])

    # --- Table anomaly ---
    table_anomaly, table_reasons = _assess_table_anomaly(page_markdown)
    assessment.table_anomaly = table_anomaly
    if table_anomaly:
        assessment.needs_gmft = True
        assessment.severity += 1.0
        assessment.reasons.extend([f"TABLE: {r}" for r in table_reasons])

    # --- Equation fragments ---
    eq_score, eq_reasons = _assess_equation_fragments(page_markdown)
    if eq_score > 0:
        assessment.needs_claude = True
        assessment.severity += eq_score
        assessment.reasons.extend([f"EQ_FRAG: {r}" for r in eq_reasons])

    # --- Text density ---
    low_density, density_reasons = _assess_text_density(
        page_markdown, config.text_density_min_chars
    )
    assessment.low_text_density = low_density
    if low_density:
        assessment.needs_claude = True
        assessment.severity += 0.5
        assessment.reasons.extend([f"DENSITY: {r}" for r in density_reasons])

    return assessment


def assess_heading_anomaly(
    total_headings: int,
    total_pages: int,
    config: QualityGateConfig | None = None,
) -> tuple[bool, list[str]]:
    """Assess heading anomaly at document level.

    Args:
        total_headings: Total headings detected across all pages.
        total_pages: Total pages in the document.
        config: Quality gate thresholds. Uses defaults if None.

    Returns:
        (has_anomaly, reasons)
    """
    if config is None:
        config = QualityGateConfig()

    reasons = []

    # Zero headings on a multi-page document
    if total_headings == 0 and total_pages > 2:
        reasons.append(f"0 headings in {total_pages}-page document (expected at least a few)")
        return True, reasons

    # Suspiciously high heading density
    if total_pages > 0:
        density = total_headings / total_pages
        if density > config.heading_density_max:
            reasons.append(
                f"heading density {density:.1f}/page "
                f"({total_headings} headings in {total_pages} pages) — "
                f"possible over-detection"
            )
            return True, reasons

    return False, reasons


def route_page(
    assessment: PageAssessment,
    gmft_tables: list[DetectedTable] | None,
    page_markdown: str,
    within_claude_budget: bool,
) -> PageDecision:
    """Route a page to the appropriate enhancement action.

    Decision table (evaluated in priority order):
    1. needs_claude + within_budget → CLAUDE_REPLACE
    2. needs_claude + over_budget + needs_gmft + tables → GMFT_REPLACE
    3. needs_gmft + tables → GMFT_REPLACE or GMFT_APPEND
    4. needs_gmft + no tables → STRIP_FALSE or STRIP_BROKEN or KEEP
    5. tables available + no issues → GMFT_APPEND (pymupdf missed tables)
    6. Default → KEEP

    Args:
        assessment: Quality assessment for the page.
        gmft_tables: GMFT-detected tables for the page, or None.
        page_markdown: The original page markdown (for table inspection).
        within_claude_budget: Whether this page is within the Claude budget.

    Returns:
        PageDecision with the chosen action and reasons.
    """
    reasons = list(assessment.reasons)  # Copy
    has_tables = gmft_tables is not None and len(gmft_tables) > 0

    # 1. Claude if needed and affordable
    if assessment.needs_claude and within_claude_budget:
        return PageDecision(assessment.page_num, PageAction.CLAUDE_REPLACE, reasons)

    # 2. Claude over budget — fall back to GMFT if table issues
    if (
        assessment.needs_claude
        and not within_claude_budget
        and assessment.needs_gmft
        and has_tables
    ):
        reasons.append("Claude over budget — GMFT fallback for table issues")
        return PageDecision(assessment.page_num, PageAction.GMFT_REPLACE, reasons)

    # 3. Table issues with GMFT available
    if assessment.needs_gmft and has_tables:
        has_existing_tables = has_pipe_tables(page_markdown)
        if has_existing_tables:
            return PageDecision(assessment.page_num, PageAction.GMFT_REPLACE, reasons)
        else:
            return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, reasons)

    # 4. Table issues but no GMFT — strip problematic tables or keep
    if assessment.needs_gmft and not has_tables:
        if _has_col_headers(page_markdown):
            reasons.append("ColN auto-headers detected, no GMFT — stripping false tables")
            return PageDecision(assessment.page_num, PageAction.STRIP_FALSE, reasons)
        if _has_br_in_tables(page_markdown):
            reasons.append("<br> artifacts in tables, no GMFT — stripping broken tables")
            return PageDecision(assessment.page_num, PageAction.STRIP_BROKEN, reasons)
        # Table anomaly flagged but neither ColN nor <br> matched — keep as-is
        reasons.append("Table anomaly detected but no specific strip action applicable — keeping")
        return PageDecision(assessment.page_num, PageAction.KEEP, reasons)

    # 5. GMFT tables available but no issues flagged — pymupdf missed tables
    # NOTE: This rule requires `not needs_claude`, so pages that need Claude
    # but are over budget won't get GMFT tables appended. The H5 spike ran
    # H1 table logic as a passthrough on all pages regardless of flags. If
    # budget-constrained operation becomes important, consider dropping the
    # `not needs_claude` guard to allow partial table recovery on those pages.
    if has_tables and not assessment.needs_gmft and not assessment.needs_claude:
        has_existing_tables = has_pipe_tables(page_markdown)
        if not has_existing_tables:
            reasons.append("GMFT found tables not in pymupdf4llm output")
            return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, reasons)

    # 6. Default: keep
    return PageDecision(assessment.page_num, PageAction.KEEP, reasons)


def prioritize_pages(
    assessments: list[PageAssessment],
    budget_pages: int,
) -> list[int]:
    """Select highest-severity pages for Claude re-extraction within a page budget.

    For dollar-based selection, see allocate_budget() in pipeline.py.

    Args:
        assessments: All page assessments from the document.
        budget_pages: Maximum number of pages to send to Claude.

    Returns:
        List of 0-indexed page numbers to re-extract, sorted by page order.
    """
    claude_pages = [a for a in assessments if a.needs_claude]
    claude_pages.sort(key=lambda a: a.severity, reverse=True)
    selected = claude_pages[:budget_pages]
    return sorted(a.page_num for a in selected)
