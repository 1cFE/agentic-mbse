"""HTML sanitization for safe LLM consumption.

Strips visually hidden content that standard extraction tools miss,
addressing CSS-based prompt injection concealment vectors.

Requires beautifulsoup4. Install via: pip install agentic-mbse[web]
"""

from __future__ import annotations

import re

# Zero-width characters to strip from text
_ZERO_WIDTH = frozenset("\u200b\u200c\u200d\u2060\ufeff\u200e\u200f")

# Tags to remove entirely (content and children)
_STRIP_TAGS = ["script", "style", "noscript", "iframe", "embed", "object"]

# CSS patterns that indicate hidden content
_HIDDEN_CSS = [
    re.compile(r"display\s*:\s*none", re.IGNORECASE),
    re.compile(r"visibility\s*:\s*hidden", re.IGNORECASE),
    re.compile(r"opacity\s*:\s*0(?:[;\s\"]|$)", re.IGNORECASE),
    re.compile(r"font-size\s*:\s*0(?:px|em|rem|%)?(?:[;\s\"]|$)", re.IGNORECASE),
]

# Off-screen positioning pattern (must be combined with position:absolute/fixed)
_OFFSCREEN = re.compile(r"(?:left|top)\s*:\s*-\d{4,}", re.IGNORECASE)
_POSITION_ABS = re.compile(r"position\s*:\s*(?:absolute|fixed)", re.IGNORECASE)


def strip_hidden_content(html: str) -> str:
    """Remove elements hidden from human viewers but visible to text extractors.

    Four-layer stripping:
    1. Dangerous tags: script, style, noscript, iframe, embed, object
    2. CSS-hidden elements: display:none, visibility:hidden, opacity:0,
       font-size:0, off-screen positioning
    3. Attribute-hidden: hidden attr, aria-hidden="true"
    4. Zero-width Unicode characters

    Args:
        html: Raw HTML string.

    Returns:
        Cleaned HTML string with hidden content removed.

    Raises:
        ImportError: If beautifulsoup4 is not installed.
    """
    from bs4 import BeautifulSoup

    # Prefer lxml for speed, fall back to html.parser
    try:
        import lxml  # noqa: F401

        parser = "lxml"
    except ImportError:
        parser = "html.parser"

    soup = BeautifulSoup(html, parser)

    # Layer 1: Remove dangerous tags
    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    # Layer 2: Remove CSS-hidden elements
    for tag in soup.find_all(style=True):
        style = tag.get("style", "")

        # Check simple hiding patterns
        if any(pat.search(style) for pat in _HIDDEN_CSS):
            tag.decompose()
            continue

        # Check off-screen positioning
        if _POSITION_ABS.search(style) and _OFFSCREEN.search(style):
            tag.decompose()
            continue

    # Layer 3: Attribute-hidden elements
    for tag in soup.find_all(attrs={"hidden": True}):
        tag.decompose()
    for tag in soup.find_all(attrs={"aria-hidden": "true"}):
        tag.decompose()

    # Layer 4: Strip zero-width characters from text nodes
    result = str(soup)
    result = "".join(c for c in result if c not in _ZERO_WIDTH)

    return result
