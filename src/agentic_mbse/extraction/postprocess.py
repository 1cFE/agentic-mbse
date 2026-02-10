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

# Unnumbered standalone bold lines that look like section headings.
# Matches: **Site Improvements and Facilities, Account 21.01**
# Also matches bold with trailing text: **Title Here** - Description text
# Does NOT match: **Table 5...**, **Figure 1...**, short labels, split bold
_UNNUMBERED_BOLD_HEADER_RE = re.compile(
    r"^\*\*([A-Z][^*]{14,})\*\*\s*$",
    re.MULTILINE,
)

# Same pattern but with trailing text after the bold:
# **First Wall and Blanket, Account 22.01.01** - This subsystem is the primary
_UNNUMBERED_BOLD_HEADER_WITH_BODY_RE = re.compile(
    r"^\*\*([A-Z][^*]{14,})\*\*\s*[-–—]\s*(.+)$",
    re.MULTILINE,
)

# All-caps standalone lines between blank lines that look like section headings.
# Matches: ABSTRACT, REFERENCES, CONTENTS, INTRODUCTION, etc.
# Must be 4-60 chars, all uppercase letters/spaces/punctuation, between blank lines.
_ALLCAPS_HEADER_RE = re.compile(
    r"(?<=\n\n)([A-Z][A-Z &/,]{3,59})(?=\n\n)",
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
    hashes = "#" * _header_depth(section_num)
    return f"{hashes} {section_num} {title}"


def _is_bold_heading_candidate(text: str) -> bool:
    """Return True if bold text looks like a section heading, not a data label.

    Rejects:
    - Table/figure captions (``Table 5...``, ``Figure 1...``)
    - Definitions with equals signs (``LSA = 4``)
    - Pure punctuation/symbols (``++++++++``)
    - Split bold patterns that were already handled (contains ``** **``)
    """
    t = text.strip()
    # Table/figure captions
    if re.match(r"^(Table|Figure|Fig\.?|Note)\s", t, re.IGNORECASE):
        return False
    # Contains equals sign (definition, not heading)
    if "=" in t:
        return False
    # Contains internal bold split markers
    if "** **" in t or "****" in t:
        return False
    # Mostly non-alphanumeric (separators like ++++++)
    alnum = sum(1 for c in t if c.isalnum())
    if alnum < len(t) * 0.5:
        return False
    return True


def _replace_unnumbered_bold_header(match: re.Match) -> str:
    title = match.group(1).strip()
    if not _is_bold_heading_candidate(title):
        return match.group(0)
    return f"### {title}"


def _replace_unnumbered_bold_header_with_body(match: re.Match) -> str:
    title = match.group(1).strip()
    body = match.group(2).strip()
    if not _is_bold_heading_candidate(title):
        return match.group(0)
    return f"### {title}\n\n{body}"


def _is_allcaps_heading_candidate(text: str) -> bool:
    """Return True if all-caps text looks like a section heading.

    Rejects:
    - TOC entries (dot leaders, trailing page numbers)
    - Pure abbreviations (all consonants, <5 chars)
    - Common non-heading all-caps patterns
    """
    t = text.strip()
    if _is_toc_line(t):
        return False
    # Must contain at least one space or be a known single-word heading
    known_single_word = {"ABSTRACT", "CONTENTS", "REFERENCES", "ACKNOWLEDGMENTS",
                         "ACKNOWLEDGEMENTS", "INTRODUCTION", "CONCLUSION", "CONCLUSIONS",
                         "APPENDIX", "BIBLIOGRAPHY", "GLOSSARY", "ACRONYMS", "SUMMARY"}
    if " " not in t and t not in known_single_word:
        return False
    return True


def _replace_allcaps_header(match: re.Match) -> str:
    title = match.group(1).strip()
    if not _is_allcaps_heading_candidate(title):
        return match.group(0)
    # Title-case the heading for readability
    return f"## {title.title()}"


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


def promote_unnumbered_bold_headers(md: str) -> str:
    """Promote standalone bold lines without section numbers to ``###`` headers.

    Handles:
    - ``**Site Improvements and Facilities, Account 21.01**`` → ``### Site Improvements...``
    - ``**Plasma Confinement, Account 22.02** - Description`` → ``### Plasma Confinement...``

    Does NOT match:
    - ``**Table 5. Comparison...**`` — table captions
    - ``**LSA = 4** Denotes...`` — definitions
    - Short bold labels (``**MW**``, ``**Source**``)
    """
    # Handle bold-with-body first (more specific pattern)
    md = _UNNUMBERED_BOLD_HEADER_WITH_BODY_RE.sub(
        _replace_unnumbered_bold_header_with_body, md
    )
    # Then standalone bold lines
    md = _UNNUMBERED_BOLD_HEADER_RE.sub(_replace_unnumbered_bold_header, md)
    return md


def promote_allcaps_headers(md: str) -> str:
    """Promote standalone all-caps lines to ``##`` headers.

    Handles: ``ABSTRACT``, ``REFERENCES``, ``LIST OF FIGURES``, etc.
    Must be between blank lines and not look like TOC entries.
    """
    return _ALLCAPS_HEADER_RE.sub(_replace_allcaps_header, md)


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
    r"^(#{2,6})\s+(.+)$",
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
    md = promote_unnumbered_bold_headers(md)
    md = promote_allcaps_headers(md)
    md = clean_header_artifacts(md)
    md = reject_noise_headers(md)
    if images_dir is not None:
        md = normalize_image_paths(md, images_dir)
    md = repair_ligatures(md)
    md = promote_figure_captions(md)
    return md
