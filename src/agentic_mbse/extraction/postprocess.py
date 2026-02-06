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
    r"^\*\*([A-Z](?:\.\d+)*)\s+(.+?)\*\*\s*$",
    re.MULTILINE,
)

# Plain-text standalone section headers (no bold, no ##).
# Matches lines like "1 Executive Summary" that are surrounded by blank lines
# and do NOT look like TOC entries (no trailing page number, no dot leaders).
_PLAIN_HEADER_RE = re.compile(
    r"(?<=\n\n)(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z].{2,80})(?=\n\n)",
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
    return False


def _replace_plain_header(match: re.Match) -> str:
    section_num = match.group(1)
    title = match.group(2).strip()
    if _is_toc_line(title):
        return match.group(0)
    hashes = "#" * _header_depth(section_num)
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
    md = promote_bold_headers(md)
    md = promote_plain_headers(md)
    md = clean_header_artifacts(md)
    md = strip_page_numbers(md)
    md = strip_running_headers(md)
    if images_dir is not None:
        md = normalize_image_paths(md, images_dir)
    md = repair_ligatures(md)
    md = promote_figure_captions(md)
    return md
