"""arXiv HTML to markdown: paper selection and the shared Pandoc runner.

arXiv serves each paper as one LaTeXML ``<article class="ltx_document">``
wrapped in site chrome (header, navigation, issue dialog, footers). Selecting
that element is the chrome removal; nothing inside it is filtered.

Stdlib only: the PDF pipeline's arXiv shortcut runs on a core install. This
module is imported by the PDF-side arXiv helpers and never imports them back.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

# Converted markdown shorter than this is treated as a failed conversion.
MIN_CONTENT_CHARS = 100

_PANDOC_TIMEOUT_SECONDS = 60

_ARTICLE_OPEN_RE = re.compile(r"<article(?=[\s>])[^>]*>", re.IGNORECASE)
_ARTICLE_CLOSE_RE = re.compile(r"</article\s*>", re.IGNORECASE)
_CLASS_ATTR_RE = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)


class ArxivConversionError(Exception):
    """arXiv HTML could not be converted; ``str(exc)`` is the reason."""


# ---------------------------------------------------------------------------
# HTML pre/post-processing (from h6_pandoc_shortcut.py)
# ---------------------------------------------------------------------------


def _preprocess_html(html: str) -> str:
    """Pre-process arXiv HTML before Pandoc conversion.

    Strips ``<figure>`` tags (so tables inside convert properly) and CSS
    transform wrappers (LaTeXML scaling artifacts).
    """
    # Strip <figure> tags but keep inner content
    html = re.sub(r"<figure[^>]*>", "", html)
    html = html.replace("</figure>", "")

    # Strip CSS transform wrappers (LaTeXML artifacts)
    html = re.sub(
        r'<div class="ltx_inline-block[^"]*ltx_transformed_outer[^>]*>',
        "",
        html,
    )
    html = re.sub(r'<span class="ltx_transformed_inner[^>]*>', "", html)

    return html


def _postprocess_markdown(md: str) -> str:
    r"""Post-process Pandoc markdown output.

    Cleans up LaTeXML artifacts that Pandoc doesn't handle:
    - ``\hspace{0pt}`` noise
    - HTML comment artifacts (``<!-- -->`{=html}``)
    """
    md = md.replace("\\hspace{0pt}", "")
    md = re.sub(r"`<!-- -->`\{=html\}", "", md)
    return md


# ---------------------------------------------------------------------------
# Paper selection
# ---------------------------------------------------------------------------


def select_article(html: str) -> str | None:
    """Return the page's one LaTeXML ``<article>`` element, or None.

    The page must hold exactly one ``<article`` opening tag and exactly one
    ``</article>``, and the opening tag's class must include ``ltx_document``.
    Any other shape returns None: an unrecognized page is never treated as
    paper-only.
    """
    openings = list(_ARTICLE_OPEN_RE.finditer(html))
    closings = list(_ARTICLE_CLOSE_RE.finditer(html))
    if len(openings) != 1 or len(closings) != 1:
        return None
    opening, closing = openings[0], closings[0]
    if closing.start() < opening.end():
        return None
    class_match = _CLASS_ATTR_RE.search(opening.group(0))
    if class_match is None:
        return None
    classes = (class_match.group(1) or class_match.group(2)).split()
    if "ltx_document" not in classes:
        return None
    return html[opening.start() : closing.end()]


# ---------------------------------------------------------------------------
# Pandoc
# ---------------------------------------------------------------------------


def _run_pandoc(html: str, pandoc_path: str = "pandoc") -> str:
    """Convert an HTML document to markdown with Pandoc; return stdout.

    Raises ``ArxivConversionError`` when Pandoc is missing, fails or times out.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp_path = Path(f.name)

    cmd = [
        pandoc_path,
        str(tmp_path),
        "-f",
        "html-native_divs-native_spans",
        "-t",
        "markdown-header_attributes",
        "--wrap=none",
        "--markdown-headings=atx",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_PANDOC_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise ArxivConversionError(
            f"Pandoc not found at '{pandoc_path}'. Install with: "
            "apt install pandoc (or brew install pandoc)"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ArxivConversionError(f"Pandoc timed out after {_PANDOC_TIMEOUT_SECONDS}s") from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise ArxivConversionError(
            f"Pandoc exited with status {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def _convert_document(document: str, pandoc_path: str = "pandoc") -> str:
    """Convert an arXiv HTML document to cleaned markdown.

    Applies the LaTeXML pre-processing, runs Pandoc and post-processes the
    output. Raises ``ArxivConversionError`` when Pandoc fails or the output is
    shorter than ``MIN_CONTENT_CHARS``.
    """
    markdown = _postprocess_markdown(_run_pandoc(_preprocess_html(document), pandoc_path))
    if len(markdown) < MIN_CONTENT_CHARS:
        raise ArxivConversionError(
            f"Pandoc output too short ({len(markdown)} chars, minimum {MIN_CONTENT_CHARS})"
        )
    return markdown


def convert_article(html: str, pandoc_path: str = "pandoc") -> str:
    """Convert the paper in an arXiv HTML page to markdown.

    Selects the article element, wraps it as a bare document, and converts it
    with Pandoc. Raises ``ArxivConversionError`` when the page has no
    recognized article, when Pandoc fails, or when the output is shorter than
    ``MIN_CONTENT_CHARS``.
    """
    article = select_article(html)
    if article is None:
        raise ArxivConversionError("no recognized arXiv article container")
    return _convert_document(f"<html><body>{article}</body></html>", pandoc_path)
