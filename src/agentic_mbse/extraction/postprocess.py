"""Backend-agnostic post-processing for extracted markdown.

Pure functions: ``str → str``. No ML, no network, no external tools.
Applied after any extraction backend to clean up common artifacts.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Ligature replacement map (Unicode FB00–FB04)
# ---------------------------------------------------------------------------

_LIGATURE_MAP: dict[str, str] = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
}

_LIGATURE_RE = re.compile("|".join(re.escape(k) for k in _LIGATURE_MAP))


# ---------------------------------------------------------------------------
# 1. Header promotion
# ---------------------------------------------------------------------------

# Primary: **1 Introduction**, **2.1 Background**, **1. Introduction**
_BOLD_HEADER_RE = re.compile(
    r"^\*\*(\d+(?:\.\d+)*)\.?\s+(.+?)\*\*\s*$",
    re.MULTILINE,
)

# Split bold: **1.** **Introduction** (seen in 2238)
_SPLIT_BOLD_HEADER_RE = re.compile(
    r"^\*\*(\d+(?:\.\d+)*)\.?\*\*\s*\*\*(.+?)\*\*\s*$",
    re.MULTILINE,
)

# Appendix letter headers: **A Introduction**, **A.1 Background**
_APPENDIX_HEADER_RE = re.compile(
    r"^\*\*([A-Z](?:\.\d+)*)\s+([A-Z][a-z].+?)\*\*\s*$",
    re.MULTILINE,
)

# Plain-text standalone section headers (no bold, no ##).
# Matches lines like "1 Executive Summary" or "1. Introduction" that are surrounded by blank lines
# and do NOT look like TOC entries (no trailing page number, no dot leaders).
# The \.? allows optional trailing period (e.g., "1." or "1.2.")
_PLAIN_HEADER_RE = re.compile(
    r"(?<=\n\n)(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z].{2,80})(?=\n\n)",
)

# Headers with redundant bold: ## **1 Introduction** → ## 1 Introduction
_HEADER_BOLD_CLEANUP_RE = re.compile(
    r"^(#{2,6})\s+\*\*(.+?)\*\*\s*$",
    re.MULTILINE,
)

# TOC page number artifact left on headers: ## 1 Title** **5 → ## 1 Title
_TOC_PAGE_NUMBER_RE = re.compile(
    r"^(#{2,6}\s+.+?)\*\*\s+\*\*\d+\s*$",
    re.MULTILINE,
)


def _header_depth(section_num: str) -> int:
    """Count depth from a section number string.

    ``"1"`` → 0 dots → ``##``, ``"2.1"`` → 1 dot → ``###``, etc.
    """
    dots = section_num.count(".")
    level = dots + 2  # ## for top-level
    return min(level, 6)


def _replace_header(match: re.Match) -> str:
    section_num = match.group(1)
    title = match.group(2).strip()
    hashes = "#" * _header_depth(section_num)
    return f"{hashes} {section_num} {title}"


def _is_toc_line(text: str) -> bool:
    """Check if a line looks like a table-of-contents entry."""
    # Dot leaders: ". . . . ." or "......"
    if ". . ." in text or "......" in text:
        return True
    # Trailing bare page number (e.g., "Executive Summary 4")
    if re.search(r"\s+\d{1,4}\s*$", text):
        return True
    # Publication date patterns: "4/1995", "2/2024" (volume/year in journal refs)
    if re.search(r"\b\d{1,2}/\d{4}\b", text):
        return True
    return False


def _replace_plain_header(match: re.Match) -> str:
    section_num = match.group(1)
    title = match.group(2).strip()
    if _is_toc_line(title):
        return match.group(0)

    # Cap section numbers: reject top-level sections > 99 (year numbers, addresses)
    depth = _header_depth(section_num)
    if depth == 2:  # depth==2 means top-level (##)
        # Extract the leading integer from section_num
        leading_num = section_num.split(".")[0]
        if int(leading_num) > 99:
            return match.group(0)  # Don't promote

    # Reject figure/table/equation references
    if re.match(r"^(?:Figure|Fig\.|Table|Equation)\s", title):
        return match.group(0)  # Don't promote

    hashes = "#" * depth
    return f"{hashes} {section_num} {title}"


def promote_bold_headers(md: str) -> str:
    """Convert standalone bold lines matching numbered section patterns to markdown headers.

    Handles:
    - ``**1 Introduction**`` → ``## 1 Introduction``
    - ``**2.1 Background**`` → ``### 2.1 Background``
    - ``**1.** **Introduction**`` → ``## 1 Introduction`` (split bold)
    - ``**A Introduction**`` → ``## A Introduction`` (appendix letters)
    - ``**A.1 Background**`` → ``### A.1 Background``

    Does NOT match:
    - ``**2**, 473 (2012)`` — bibliography (bold wraps only the number)
    - Bold text mid-paragraph (not a standalone line)
    """
    md = _BOLD_HEADER_RE.sub(_replace_header, md)
    md = _SPLIT_BOLD_HEADER_RE.sub(_replace_header, md)
    md = _APPENDIX_HEADER_RE.sub(_replace_header, md)
    return md


def promote_plain_headers(md: str) -> str:
    """Promote plain-text numbered section headers to markdown headers.

    Matches standalone lines like ``1 Executive Summary`` that are
    between blank lines and do NOT look like TOC entries (no trailing
    page number, no dot leaders).
    """
    return _PLAIN_HEADER_RE.sub(_replace_plain_header, md)


def clean_header_artifacts(md: str) -> str:
    """Clean up artifacts in markdown headers.

    1. Remove redundant bold markers: ``## **1 Title**`` → ``## 1 Title``
    2. Remove TOC page number artifacts: ``## 1 Title** **5`` → ``## 1 Title``
    """
    md = _TOC_PAGE_NUMBER_RE.sub(r"\1", md)
    md = _HEADER_BOLD_CLEANUP_RE.sub(r"\1 \2", md)
    return md


# ---------------------------------------------------------------------------
# 2. Page number stripping
# ---------------------------------------------------------------------------

# Bare page numbers between blank lines
_PAGE_NUMBER_RE = re.compile(r"\n\n\s*\d{1,4}\s*\n\n")

# Bold page numbers between blank lines: **40**
_BOLD_PAGE_NUMBER_RE = re.compile(r"\n\n\s*\*\*\d{1,4}\*\*\s*\n\n")


def strip_page_numbers(md: str) -> str:
    """Remove bare page numbers on standalone lines between blank lines.

    Handles both plain (``42``) and bold (``**42**``) page numbers.
    """
    md = _BOLD_PAGE_NUMBER_RE.sub("\n\n", md)
    md = _PAGE_NUMBER_RE.sub("\n\n", md)
    return md


# ---------------------------------------------------------------------------
# 3. Running header/footer removal
# ---------------------------------------------------------------------------


def _normalize_running_header(text: str) -> str:
    """Normalize a line for running header detection.

    Strips leading/trailing digits, whitespace, and markdown formatting
    (italic underscores, bold markers) to find the stable "base" text.
    Also collapses internal whitespace runs to a single space.
    """
    base = text.strip()
    # Strip italic markers: _text_ → text
    base = re.sub(r"^_+|_+$", "", base)
    # Strip bold markers: **text** → text
    base = re.sub(r"^\*\*|\*\*$", "", base)
    base = base.strip()
    # Collapse internal whitespace runs
    base = re.sub(r"\s+", " ", base)
    # Strip leading/trailing digits
    base = re.sub(r"^\d+\s*", "", base)
    base = re.sub(r"\s*\d+$", "", base)
    return base.strip()


def strip_running_headers(md: str, threshold: int = 3) -> str:
    """Remove repeated short lines that appear across multiple pages.

    Algorithm:
    1. Find all short standalone paragraphs (< 120 chars, in their own block).
    2. Normalize each by stripping leading/trailing digits, whitespace,
       and markdown formatting (italic/bold markers).
    3. If a normalized form appears more than *threshold* times, remove all
       matching paragraphs.
    """
    # Isolate PAGE markers into their own blocks so adjacent running
    # headers don't merge into multi-line blocks and escape detection.
    md = re.sub(r"(<!-- PAGE:\d+ -->)", r"\n\n\1\n\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)

    # Split into paragraph blocks (separated by blank lines)
    blocks = re.split(r"\n{2,}", md)

    # Count frequency of short, normalized blocks.
    # Check length *after* normalization (which collapses whitespace),
    # not before, because journal running headers may be padded with spaces.
    freq: dict[str, int] = {}
    for block in blocks:
        stripped = block.strip()
        if not stripped or "\n" in stripped:
            continue
        base = _normalize_running_header(stripped)
        if not base or len(base) > 120:
            continue
        freq[base] = freq.get(base, 0) + 1

    # Identify bases to remove
    remove_bases = {base for base, count in freq.items() if count >= threshold}

    if not remove_bases:
        return md

    # Filter out matching blocks
    result_blocks: list[str] = []
    for block in blocks:
        stripped = block.strip()
        if stripped and "\n" not in stripped:
            base = _normalize_running_header(stripped)
            if base in remove_bases:
                continue
        result_blocks.append(block)

    return "\n\n".join(result_blocks)


# ---------------------------------------------------------------------------
# 4. Image path normalization
# ---------------------------------------------------------------------------


def normalize_image_paths(md: str, images_dir: Path) -> str:
    """Replace absolute image paths with relative ``images/`` paths."""
    abs_pattern = re.escape(str(images_dir))
    return re.sub(abs_pattern, "images", md)


# ---------------------------------------------------------------------------
# 5. Ligature repair
# ---------------------------------------------------------------------------


def repair_ligatures(md: str) -> str:
    """Replace Unicode ligature codepoints (U+FB00–FB04) with ASCII equivalents.

    U+FFFD replacement characters are left as-is (context reconstruction
    is too error-prone without a dictionary).
    """
    return _LIGATURE_RE.sub(lambda m: _LIGATURE_MAP[m.group()], md)


# ---------------------------------------------------------------------------
# 6. Figure caption promotion
# ---------------------------------------------------------------------------

_FIGURE_CAPTION_RE = re.compile(
    r"(!\[\]\(images/[^)]+\))\s*\n+\s*((?:Figure|Fig\.?)\s*\d+[.:]\s*.+)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# 6a. Header noise rejection
# ---------------------------------------------------------------------------

# Headers that are too short, contain math operators, look like table rows,
# or are just a number + tiny word (page artifacts from OCR)
_NOISE_HEADER_RE = re.compile(
    r"^(#{1,6})\s+(.+)$",
    re.MULTILINE,
)


def _is_noise_header(header_text: str) -> bool:
    """Return True if *header_text* (after the ``## `` prefix) looks like noise.

    Noise indicators:
    - Contains math/science operators: ASCII ``=+[]{}`` or Unicode ``≥≤≈∇∆∑∏µ±×÷→←∞•>~``
    - Contains embedded bold markers (``** **`` or ``****``)
    - Looks like a table row (contains ``|`` or tab characters)
    - Is just a number + short word under 4 chars (page-number artifact)
    - Very short (< 4 chars after stripping the section number prefix)
    - Report/figure labels (e.g., "ORNL 99-1407 EFG", "DOE/ER-1234")
    - Numbered sentences that reference figures/tables (e.g., "12. Figure 11 excludes...")
    - Bibliographic entries (numbered or numberless): requires ≥2 signals from journal
      abbreviations, volume/issue patterns, page ranges, author initials, or year patterns
    """
    text = header_text.strip()
    if re.search(r"[=+\[\]{}>~≥≤≈∇∆∑∏µ±×÷→←∞•]", text):
        return True
    # Embedded bold markers from garbled slide transitions
    if "** **" in text or "****" in text:
        return True
    if "|" in text or "\t" in text:
        return True
    # Number + single short word: "3 of", "42 Fig", etc.
    if re.match(r"^\d+(?:\.\d+)*\s+\S{1,3}$", text):
        return True
    # Very short: strip any leading section number to check title length
    title_only = re.sub(r"^\d+(?:\.\d+)*\s*", "", text).strip()
    if title_only and len(title_only) < 4:
        return True

    # Report/figure labels: "ORNL 99-1407 EFG", "DOE/ER-1234", "ANL-2020-42"
    # Pattern 1: 2-5 uppercase letters, space/slash/hyphen, then digits with hyphens/slashes
    if re.match(r"^[A-Z]{2,5}[\s/-]+\d{2,}[-/]\d+", text):
        return True
    # Pattern 2: "DOE/ER-1234" where there's a second acronym after slash
    if re.match(r"^[A-Z]{2,5}/[A-Z]{2,5}-\d+", text):
        return True

    # Numbered sentences referencing figures/tables: "12. Figure 11 excludes..."
    # These start with a number, then mention Figure/Fig./Table/Equation
    if re.match(r"^\d+\.\s+(Figure|Fig\.|Table|Equation)\s+\d", text, re.IGNORECASE):
        return True

    # Reference entries: numbered items with bibliographic indicators
    # Pattern: "N. Title..." where N is 1-3 digits
    if re.match(r"^\d{1,3}\.\s+", text):
        # Check for bibliographic indicators
        # - Journal abbreviations: "Nucl. Fusion", "Phys. Rev.", "J. Appl. Phys."
        if re.search(r"\b[A-Z][a-z]*\.\s+[A-Z]", text):
            return True
        # - Author initials: "J. Smith", "R. W. Moir"
        if re.search(r"\b[A-Z]\.\s+[A-Z]", text):
            return True
        # - Publisher names: "U.S. Department", "Oak Ridge"
        if re.search(r"\bU\.S\.\s+(Department|Energy)", text):
            return True
        # - Conference/institution indicators
        if re.search(r"\b(presented at|University of|National Laboratory)", text, re.IGNORECASE):
            return True
        # - Year in parentheses: "(1998)", "(2020)"
        if re.search(r"\(\d{4}\)", text):
            return True

    # Numberless bibliographic entries: detect journal citations without leading numbers
    # Require at least 2 independent bibliographic signals to avoid false positives
    # This catches references where the detector stripped the leading number
    bib_signal_count = 0

    # Signal 1: Journal abbreviation pattern (e.g., "Control. Fusion", "Nucl. Fusion")
    # Match pattern: abbreviated word (capital + lowercase + period) followed by space and capital
    journal_abbrev_matches = re.findall(r"\b[A-Z][a-z]+\.\s+[A-Z]", text)
    has_journal_abbrev = len(journal_abbrev_matches) >= 1
    if len(journal_abbrev_matches) >= 2:
        bib_signal_count += 1

    # Signal 2: Volume/issue pattern (e.g., "51 (12)", "45(3)")
    has_volume_issue = re.search(r"\d+\s*\(\d+\)", text) is not None
    if has_volume_issue:
        bib_signal_count += 1

    # Signal 3: Page range pattern (e.g., "124-130", "S404-S413")
    has_page_range = re.search(r"\b\d+[–-]\d+\b", text) is not None
    if has_page_range:
        bib_signal_count += 1

    # Signal 4: Multiple author initials (e.g., "J. W.", "R. W.")
    # Count sequences of capital letter + period + space/capital
    author_initial_matches = re.findall(r"\b[A-Z]\.\s*(?:[A-Z]\.?)", text)
    if len(author_initial_matches) >= 2:
        bib_signal_count += 1

    # Signal 5: Year in parentheses
    has_year_parens = re.search(r"\(\d{4}\)", text) is not None
    if has_year_parens:
        bib_signal_count += 1

    # Reject if we have at least 2 bibliographic signals
    # OR if we have 1 strong signal (journal abbrev) + 1 supporting signal (volume/issue, page range, or year)
    if bib_signal_count >= 2:
        return True
    if has_journal_abbrev and (has_volume_issue or has_page_range or has_year_parens):
        return True

    # Address line rejection (spec-02 requirement #3)
    # Reject headings that look like postal addresses or building locations
    # Common patterns:
    # - ZIP codes: 5-digit sequences (e.g., "5285 Port Royal Road")
    # - Street addresses: number + street keywords (Road, Avenue, Street, etc.)
    # - State abbreviations: 2-letter uppercase after comma (e.g., ", VA")

    # Street keywords that commonly appear in addresses
    street_keywords = (
        r"Road|Avenue|Ave\.?|Street|St\.?|Boulevard|Blvd\.?|Drive|Dr\.?|"
        r"Highway|Hwy\.?|Suite|Parkway|Pkwy\.?|Lane|Ln\.?|Circle|"
        r"SW|NW|SE|NE"
    )

    # Pattern 1: Contains 5-digit ZIP code (not at start, to avoid false positive with section numbers)
    # Combined with street keyword for precision
    has_zip = re.search(r"\b\d{5}\b", text) is not None
    has_street_keyword = re.search(street_keywords, text, re.IGNORECASE) is not None

    # Pattern 2: Number followed by street keyword (e.g., "5285 Port Royal Road")
    # Requires multi-digit number to avoid false positives with "3 Main Ideas"
    # Allow one or more words between the number and street keyword (e.g., "Port Royal" Road)
    has_numbered_street = (
        re.search(r"\b\d{2,}\s+(?:\w+\s+)*(" + street_keywords + r")", text, re.IGNORECASE)
        is not None
    )

    # Pattern 3: State abbreviation pattern (2 uppercase letters after comma)
    has_state_abbrev = re.search(r",\s+[A-Z]{2}\b", text) is not None

    # Reject if we have strong address indicators
    if has_zip and has_street_keyword:
        return True
    if has_numbered_street:
        return True
    if has_state_abbrev and (has_street_keyword or has_zip):
        return True

    return False


def reject_noise_headers(md: str) -> str:
    """Demote ``## ``-style headers back to plain text when they look like noise.

    Targets OCR artifacts: equation fragments, table rows, and
    page-number+word combos that were incorrectly promoted to headers.
    """

    def _maybe_demote(match: re.Match) -> str:
        header_text = match.group(2)
        if _is_noise_header(header_text):
            return header_text
        return match.group(0)

    return _NOISE_HEADER_RE.sub(_maybe_demote, md)


# ---------------------------------------------------------------------------
# 7. Figure caption promotion
# ---------------------------------------------------------------------------


def promote_figure_captions(md: str) -> str:
    """Move adjacent figure captions into image alt-text.

    Pattern: ``![](images/figure_NNN.png)`` followed within 1–2 lines
    by ``Figure N:`` text.

    Promotes to: ``![Figure N: caption text](images/figure_NNN.png)``
    """

    def _replacer(match: re.Match) -> str:
        img_tag = match.group(1)
        caption = match.group(2).strip()
        # Extract the URL from the image tag
        url_match = re.search(r"\(([^)]+)\)", img_tag)
        if url_match:
            url = url_match.group(1)
            return f"![{caption}]({url})"
        return match.group(0)

    return _FIGURE_CAPTION_RE.sub(_replacer, md)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def postprocess(md: str, images_dir: Path | None = None) -> str:
    """Apply all post-processing steps in order. Returns cleaned markdown."""
    md = strip_page_numbers(md)
    md = strip_running_headers(md)
    md = promote_bold_headers(md)
    md = promote_plain_headers(md)
    md = clean_header_artifacts(md)
    md = reject_noise_headers(md)
    if images_dir is not None:
        md = normalize_image_paths(md, images_dir)
    md = repair_ligatures(md)
    md = promote_figure_captions(md)
    return md
