"""arXiv detection and Pandoc conversion for PDF extraction pipeline.

Identifies a PDF's own arXiv paper from trusted evidence, checks HTML
availability, and converts arXiv HTML to markdown via Pandoc with
pre/post-processing.
"""

from __future__ import annotations

import re
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from agentic_mbse.extraction.arxiv_html import convert_article, load_arxiv_html
from agentic_mbse.extraction.http import USER_AGENT

# Whether the PDF pipeline substitutes a PDF's identified arXiv paper with its
# HTML version when the caller doesn't say. The only place this default is set.
ARXIV_SHORTCUT_DEFAULT = True


def resolve_arxiv_shortcut(explicit: bool | None) -> bool:
    """Return *explicit* when the caller set it, otherwise ``ARXIV_SHORTCUT_DEFAULT``."""
    return ARXIV_SHORTCUT_DEFAULT if explicit is None else explicit


# ---------------------------------------------------------------------------
# Pandoc availability
# ---------------------------------------------------------------------------


def _pandoc_available(pandoc_path: str = "pandoc") -> bool:
    """Check if Pandoc is available on the system PATH."""
    return shutil.which(pandoc_path) is not None


# ---------------------------------------------------------------------------
# arXiv detection
# ---------------------------------------------------------------------------


# arXiv stamps every PDF it serves with one line in the left margin of page 1,
# rotated 90°: ``arXiv:<id>v<N>  [<category>]  <date>``. Prose citations are
# horizontal body text, so only a vertical left-margin line in the full stamp
# shape counts as the paper's own ID.
_STAMP_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5}v\d+)\s+\[[^\]]+\]\s+\d{1,2}\s+\w{3}\s+\d{4}")
_STAMP_MAX_DIR_X = 0.05  # |dir.x| below this means the line runs vertically
_STAMP_MARGIN_FRACTION = 0.15  # the line must end within this share of page width

# A PDF fetched from arxiv.org/abs/<id> or arxiv.org/pdf/<id>[.pdf] is that paper.
_SOURCE_URL_PATH_RE = re.compile(r"/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)(?:\.pdf)?/?")


@dataclass(frozen=True)
class ArxivIdentity:
    """Which arXiv paper a PDF is, by trusted evidence only."""

    arxiv_id: str | None  # e.g. "2610.14224v1"; None = don't substitute
    evidence: tuple[str, ...]  # sources found: ("stamp",), ("url",), ("stamp", "url")
    conflict: str | None = None  # reason when sources disagree; if set, arxiv_id is None


def _margin_stamp_ids(pdf_path: Path) -> list[str]:
    """Return the arXiv IDs of page-1 lines shaped like arXiv's margin stamp."""
    import pymupdf  # type: ignore[import-untyped]

    doc = pymupdf.open(str(pdf_path))
    try:
        if len(doc) == 0:
            return []
        page = doc[0]
        margin = page.rect.width * _STAMP_MARGIN_FRACTION
        ids: list[str] = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                if abs(line["dir"][0]) >= _STAMP_MAX_DIR_X or line["bbox"][2] > margin:
                    continue
                text = "".join(span["text"] for span in line["spans"]).strip()
                m = _STAMP_RE.fullmatch(text)
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))
        return ids
    finally:
        doc.close()


def _source_url_id(url: str) -> str | None:
    """Return the arXiv ID named by an arxiv.org abs/pdf URL, or None."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host != "arxiv.org" and not host.endswith(".arxiv.org"):
        return None
    m = _SOURCE_URL_PATH_RE.fullmatch(parsed.path)
    return m.group(1) if m else None


def identify_arxiv_paper(pdf_path: Path, pdf_source_url: str | None = None) -> ArxivIdentity:
    """Decide which arXiv paper *pdf_path* is, from trusted evidence only.

    Evidence is the margin stamp on page 1 and the arxiv.org URL the PDF was
    fetched from. IDs in body text never count. More than one stamp, or a
    stamp and URL naming different papers (ignoring version), is a conflict.
    """
    stamp_ids = _margin_stamp_ids(pdf_path)
    url_id = _source_url_id(pdf_source_url) if pdf_source_url else None
    evidence = tuple(name for name, found in (("stamp", stamp_ids), ("url", url_id)) if found)

    if len(stamp_ids) > 1:
        return ArxivIdentity(
            None, evidence, f"page 1 carries more than one arXiv stamp: {', '.join(stamp_ids)}"
        )
    stamp_id = stamp_ids[0] if stamp_ids else None
    if stamp_id and url_id and strip_arxiv_version(stamp_id)[0] != strip_arxiv_version(url_id)[0]:
        return ArxivIdentity(
            None, evidence, f"margin stamp names {stamp_id} but the PDF came from {pdf_source_url}"
        )
    return ArxivIdentity(stamp_id or url_id, evidence)


def detect_arxiv_id(pdf_path: Path) -> str | None:
    """Return the PDF's own arXiv ID from its margin stamp, or None.

    Kept for callers of the old API; see ``identify_arxiv_paper``.
    """
    return identify_arxiv_paper(pdf_path).arxiv_id


# ---------------------------------------------------------------------------
# arXiv version normalization
# ---------------------------------------------------------------------------

# Matches an arXiv id (NNNN.NNNNN) followed by a version suffix (vN), wherever
# it appears in a bare id or an HTML URL. The id and version are captured so we
# can strip the suffix and report the requested version.
_ARXIV_VERSION_RE = re.compile(r"(\d{4}\.\d{4,5})v(\d+)")


def strip_arxiv_version(id_or_url: str) -> tuple[str, int | None]:
    """Strip an arXiv version suffix from an id or HTML URL.

    Handles both forms uniformly, since ``NNNN.NNNNNvN`` appears verbatim in
    each: ``2401.12345v3`` -> ``("2401.12345", 3)`` and
    ``https://arxiv.org/html/2401.12345v3`` ->
    ``("https://arxiv.org/html/2401.12345", 3)``. A bare id/URL with no version
    is returned unchanged with ``None``.
    """
    m = _ARXIV_VERSION_RE.search(id_or_url)
    if m is None:
        return id_or_url, None
    stripped = id_or_url[: m.start()] + m.group(1) + id_or_url[m.end() :]
    return stripped, int(m.group(2))


def resolve_fetched_version(html: str, bare_id: str) -> int | None:
    """Recover the version arXiv actually served from the HTML's asset paths.

    LaTeXML asset references are prefixed ``{id}vN/`` (e.g.
    ``1706.03762v7/x1.png``), so the served version is readable from the markup.
    Returns the version number, or ``None`` when no such path is present (e.g. a
    figure-less paper).
    """
    m = re.search(re.escape(bare_id) + r"v(\d+)/", html)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# arXiv HTML check
# ---------------------------------------------------------------------------


def _arxiv_html_head_ok(url: str) -> bool:
    """Return True if a HEAD request to ``url`` returns 200.

    Any failure (404, timeout, network error) counts as "not available" — this
    is a reachability probe, not an invariant check.
    """
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return bool(resp.status == 200)
    except Exception:
        return False


def check_arxiv_html(arxiv_id: str) -> str | None:
    """Return the URL of the latest available arXiv HTML, or None.

    Prefers the bare (latest) URL so a version-pinned id upgrades to the newest
    version arXiv serves. If the bare URL is unavailable, falls back to the exact
    requested version so a pinned id still resolves.
    """
    bare_id, _ = strip_arxiv_version(arxiv_id)
    bare_url = f"https://arxiv.org/html/{bare_id}"
    if _arxiv_html_head_ok(bare_url):
        return bare_url
    if bare_id != arxiv_id and _arxiv_html_head_ok(f"https://arxiv.org/html/{arxiv_id}"):
        return f"https://arxiv.org/html/{arxiv_id}"
    return None


# ---------------------------------------------------------------------------
# Pandoc conversion
# ---------------------------------------------------------------------------


def convert_arxiv_html(
    html_source: str | Path,
    pandoc_path: str = "pandoc",
) -> tuple[str, bytes]:
    """Convert the paper in an arXiv HTML page to markdown via Pandoc.

    Only the page's ``<article class="ltx_document">`` is converted; the arXiv
    chrome around it is dropped.

    Args:
        html_source: URL (``https://...``) or local file path.
        pandoc_path: Path to pandoc binary.

    Returns:
        ``(markdown, raw_html_bytes)`` — raw bytes exactly as fetched or read.

    Raises:
        ``FileNotFoundError`` if Pandoc is not installed.
        ``ArxivConversionError`` if the page has no recognized article, Pandoc
        fails or times out, or its output is shorter than
        ``arxiv_html.MIN_CONTENT_CHARS``.
        ``OSError`` / ``UnicodeDecodeError`` if the page cannot be loaded.
    """
    if not _pandoc_available(pandoc_path):
        raise FileNotFoundError(
            f"Pandoc not found at '{pandoc_path}'. Install with: "
            "apt install pandoc (or brew install pandoc)"
        )
    source = load_arxiv_html(html_source)
    return convert_article(source.html, pandoc_path), source.raw_bytes
