"""Quality gate: per-page extraction quality assessment.

Detects extraction problems that warrant enhancement (GMFT table replacement
or Claude vision re-extraction). Used by H3, H5, and other pipeline scripts
to decide which pages need improvement.

Detection dimensions:
- Math garbling: ~~ strikethrough wrapping, Unicode replacement chars, garbled fractions
- Table anomaly: <br> in pipe tables, ColN auto-headers (false tables from diagrams)
- Heading anomaly: Document-level heading count vs expectations
- Text density: Very low char count suggesting OCR failure or blank page
"""

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class PageAssessment:
    """Quality assessment for a single page."""

    page_num: int
    needs_claude: bool = False  # Needs Claude vision re-extraction
    needs_gmft: bool = False  # Needs GMFT table replacement
    reasons: list[str] = field(default_factory=list)
    severity: float = 0.0  # Higher = more urgent for Claude budget allocation

    # Raw signal values (for debugging / threshold tuning)
    math_garble_score: float = 0.0
    table_anomaly: bool = False
    heading_anomaly: bool = False
    low_text_density: bool = False


# ---------------------------------------------------------------------------
# Math garbling detection
# ---------------------------------------------------------------------------

# Strikethrough-wrapped content: ~~text~~ where text is short (equation fragments)
_STRIKETHROUGH_RE = re.compile(r"~~[^~]{1,40}~~")

# Unicode replacement character
_REPLACEMENT_CHAR = "\ufffd"

# Garbled equation patterns from pymupdf4llm:
# - ~~\ufffd~~ (replacement char in strikethrough)
# - ~~\ufffd\ufffd~~ (multiple replacement chars)
# - Bracket-encoded fractions: [/], [+], [-] in running text (not in tables)
_GARBLED_FRACTION_RE = re.compile(r"\[([/+\-])\]")

# Isolated Unicode math symbols without LaTeX context
# (pymupdf4llm produces these; Claude would produce $\sum$, $\int$, etc.)
_UNICODE_MATH_RANGES = [
    (0x2200, 0x22FF),  # Mathematical Operators
    (0x2100, 0x214F),  # Letterlike Symbols
    (0x27C0, 0x27EF),  # Miscellaneous Mathematical Symbols-A
]


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
    """Count isolated Unicode math symbols (Greek, operators, etc.).

    High counts of these WITHOUT LaTeX ($...$) context suggest garbled
    math encoding from pymupdf4llm rather than clean output.
    """
    count = 0
    for char in text:
        code = ord(char)
        for lo, hi in _UNICODE_MATH_RANGES:
            if lo <= code <= hi:
                count += 1
                break
    return count


def assess_math_garbling(page_markdown: str) -> tuple[float, list[str]]:
    """Assess math garbling severity on a page.

    Returns:
        (severity_score, reasons) — score >= 1.0 means page should be flagged.
    """
    reasons = []
    score = 0.0

    # Signal 1: Strikethrough sequences (strongest signal)
    st_count = _count_strikethroughs(page_markdown)
    if st_count >= 3:
        score += 2.0
        reasons.append(f"strikethrough sequences: {st_count} (garbled content)")
    elif st_count >= 1:
        score += 0.5
        reasons.append(f"strikethrough sequences: {st_count}")

    # Signal 2: Replacement characters (very strong signal)
    repl_count = _count_replacement_chars(page_markdown)
    if repl_count >= 2:
        score += 2.0
        reasons.append(f"replacement chars (\ufffd): {repl_count}")
    elif repl_count >= 1:
        score += 1.0
        reasons.append(f"replacement char (\ufffd): {repl_count}")

    # Signal 3: Bracket-encoded operators outside tables
    frac_count = _count_garbled_fractions(page_markdown)
    if frac_count >= 3:
        score += 1.0
        reasons.append(f"bracket-encoded operators: {frac_count}")
    elif frac_count >= 1:
        score += 0.3
        reasons.append(f"bracket-encoded operators: {frac_count}")

    # Signal 4: High Unicode math symbol density (weaker signal)
    # Only matters if combined with other signals — Unicode Greek in running
    # text (hansen_2025 style) is normal and shouldn't trigger alone.
    math_sym_count = _count_unicode_math_symbols(page_markdown)
    char_count = len(page_markdown)
    if char_count > 0:
        math_density = math_sym_count / char_count
        if math_density > 0.02 and score > 0:
            # Only boost if already suspicious from other signals
            score += 0.5
            reasons.append(
                f"Unicode math symbol density: {math_density:.3f} "
                f"({math_sym_count} symbols in {char_count} chars)"
            )

    return score, reasons


# ---------------------------------------------------------------------------
# Table anomaly detection
# ---------------------------------------------------------------------------

# Reuse patterns from shared.py
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|")
_COL_HEADER_RE = re.compile(r"\bCol\d+\b")


def assess_table_anomaly(page_markdown: str) -> tuple[bool, list[str]]:
    """Detect table anomalies on a page.

    Returns:
        (has_anomaly, reasons)
    """
    reasons = []
    has_anomaly = False

    table_lines = []
    for line in page_markdown.split("\n"):
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


# ---------------------------------------------------------------------------
# Heading anomaly detection (document-level, not per-page)
# ---------------------------------------------------------------------------


def assess_heading_anomaly(
    total_headings: int,
    total_pages: int,
) -> tuple[bool, list[str]]:
    """Assess heading anomaly at document level.

    Args:
        total_headings: Total headings detected across all pages.
        total_pages: Total pages in the document.

    Returns:
        (has_anomaly, reasons)
    """
    reasons = []

    # Zero headings on a multi-page document
    if total_headings == 0 and total_pages > 2:
        reasons.append(
            f"0 headings in {total_pages}-page document (expected at least a few)"
        )
        return True, reasons

    # Suspiciously high heading density (>3 headings per page on average)
    if total_pages > 0:
        density = total_headings / total_pages
        if density > 3.0:
            reasons.append(
                f"heading density {density:.1f}/page "
                f"({total_headings} headings in {total_pages} pages) — "
                f"possible over-detection"
            )
            return True, reasons

    return False, reasons


# ---------------------------------------------------------------------------
# Text density check
# ---------------------------------------------------------------------------

# Minimum expected chars for a non-blank page (references, TOC pages can be sparse)
_MIN_CHARS_PER_PAGE = 200


def assess_text_density(page_markdown: str, page_num: int) -> tuple[bool, list[str]]:
    """Check if a page has suspiciously low text content.

    Returns:
        (is_low, reasons)
    """
    char_count = len(page_markdown.strip())

    if char_count < _MIN_CHARS_PER_PAGE:
        return True, [
            f"very low text density: {char_count} chars "
            f"(threshold: {_MIN_CHARS_PER_PAGE})"
        ]

    return False, []


# ---------------------------------------------------------------------------
# Main assessment function
# ---------------------------------------------------------------------------


def assess_page_quality(
    page_markdown: str,
    page_num: int,
) -> PageAssessment:
    """Assess extraction quality for a single page.

    Checks multiple quality dimensions and determines what enhancement
    is needed (if any).

    Args:
        page_markdown: The pymupdf4llm markdown for this page.
        page_num: 0-indexed page number.

    Returns:
        PageAssessment with flags for needed enhancements.
    """
    assessment = PageAssessment(page_num=page_num)

    # --- Math garbling ---
    math_score, math_reasons = assess_math_garbling(page_markdown)
    assessment.math_garble_score = math_score
    if math_score >= 1.0:
        assessment.needs_claude = True
        assessment.severity += math_score
        assessment.reasons.extend([f"MATH: {r}" for r in math_reasons])

    # --- Table anomaly ---
    table_anomaly, table_reasons = assess_table_anomaly(page_markdown)
    assessment.table_anomaly = table_anomaly
    if table_anomaly:
        assessment.needs_gmft = True
        assessment.severity += 1.0
        assessment.reasons.extend([f"TABLE: {r}" for r in table_reasons])

    # --- Text density ---
    low_density, density_reasons = assess_text_density(page_markdown, page_num)
    assessment.low_text_density = low_density
    if low_density:
        assessment.needs_claude = True
        assessment.severity += 0.5
        assessment.reasons.extend([f"DENSITY: {r}" for r in density_reasons])

    return assessment


# ---------------------------------------------------------------------------
# Budget-aware page prioritization
# ---------------------------------------------------------------------------


def prioritize_pages(
    assessments: list[PageAssessment],
    budget_pages: int,
) -> list[int]:
    """Select the highest-priority pages for Claude re-extraction within budget.

    Args:
        assessments: All page assessments from the document.
        budget_pages: Maximum number of pages to send to Claude.

    Returns:
        List of 0-indexed page numbers to re-extract, sorted by page order.
    """
    # Filter to pages that need Claude
    claude_pages = [a for a in assessments if a.needs_claude]

    # Sort by severity (highest first) for budget prioritization
    claude_pages.sort(key=lambda a: a.severity, reverse=True)

    # Take top N within budget
    selected = claude_pages[:budget_pages]

    # Return in page order (not severity order) for coherent document assembly
    return sorted(a.page_num for a in selected)
