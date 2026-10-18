"""arXiv HTML to markdown: loading, paper selection, Pandoc and image saving.

arXiv serves each paper as one LaTeXML ``<article class="ltx_document">``
wrapped in site chrome (header, navigation, issue dialog, footers). Selecting
that element is the chrome removal; nothing inside it is filtered.

Stdlib only: the PDF pipeline's arXiv shortcut runs on a core install. This
module is imported by the PDF-side arXiv helpers and never imports them back.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import http.client
import re
import subprocess
import tempfile
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, unquote_to_bytes, urljoin, urlparse
from urllib.request import url2pathname

from agentic_mbse.extraction.http import DEFAULT_TIMEOUT, USER_AGENT, FetchResult, fetch_url

# Converted markdown shorter than this is treated as a failed conversion.
MIN_CONTENT_CHARS = 100

# arXiv's relative figure refs (``<id>vN/<file>``) resolve against the page URL
# without a trailing slash, so a slash after ``/html/<id>[vN]`` is dropped.
_ARXIV_HTML_SLASH_RE = re.compile(
    r"^(https?://(?:www\.)?arxiv\.org/html/\d{4}\.\d{4,5}(?:v\d+)?)/$", re.IGNORECASE
)
_BASE_HREF_RE = re.compile(r"""<base\b[^>]*?\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

_PANDOC_TIMEOUT_SECONDS = 60

_ARTICLE_OPEN_RE = re.compile(r"<article(?=[\s>])[^>]*>", re.IGNORECASE)
_ARTICLE_CLOSE_RE = re.compile(r"</article\s*>", re.IGNORECASE)
_CLASS_ATTR_RE = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
_OBJECT_RE = re.compile(r"<object\b([^>]*)>(.*?)</object\s*>", re.IGNORECASE | re.DOTALL)
_ATTR_RE = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')


class PandocError(Exception):
    """Pandoc is missing, failed or timed out; ``str(exc)`` is the reason."""


class ArxivConversionError(Exception):
    """arXiv HTML could not be converted; ``str(exc)`` is the reason."""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArxivSource:
    """An arXiv HTML page as loaded, before any cleanup."""

    raw_bytes: bytes  # exactly as fetched or read; what provenance hashes and saves
    html: str  # decoded raw_bytes
    serving_url: str  # post-redirect http(s) URL (arXiv trailing slash dropped), or file:// URI

    @classmethod
    def from_fetch(cls, fetched: FetchResult) -> ArxivSource:
        """Build a source from a fetch, normalizing the arXiv serving URL."""
        serving_url = _ARXIV_HTML_SLASH_RE.sub(r"\1", fetched.final_url)
        return cls(raw_bytes=fetched.content, html=fetched.text(), serving_url=serving_url)

    @property
    def image_base(self) -> str:
        """The URL image refs resolve against: the serving URL with any ``<base href>``."""
        m = _BASE_HREF_RE.search(self.html)
        if m is None:
            return self.serving_url
        href: str = m.group(1) or m.group(2)
        return urljoin(self.serving_url, href)


def load_arxiv_html(source: str | Path, *, timeout: int = DEFAULT_TIMEOUT) -> ArxivSource:
    """Load arXiv HTML from an http(s) URL (via ``fetch_url``) or a local file.

    Network and file errors propagate (``OSError`` subclasses; undecodable
    bytes raise ``UnicodeDecodeError``).
    """
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        return ArxivSource.from_fetch(fetch_url(source, timeout=timeout))
    path = Path(source).resolve()
    raw_bytes = path.read_bytes()
    return ArxivSource(
        raw_bytes=raw_bytes, html=raw_bytes.decode("utf-8"), serving_url=path.as_uri()
    )


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


def _svg_object_as_img(m: re.Match[str]) -> str:
    """Rewrite one LaTeXML SVG figure ``<object>`` as an ``<img>``; leave other objects alone."""
    attrs = dict(_ATTR_RE.findall(m.group(1)))
    is_svg_figure = (
        attrs.get("type") == "image/svg+xml"
        and "ltx_graphics" in attrs.get("class", "").split()
        and "data" in attrs
    )
    if not is_svg_figure:
        return m.group(0)
    fallback = " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())
    alt = (fallback or "Refer to caption").replace('"', "&quot;")
    kept = "".join(f' {k}="{attrs[k]}"' for k in ("id", "class", "width", "height") if k in attrs)
    return f'<img src="{attrs["data"]}" alt="{alt}"{kept}>'


def extract_article(html: str) -> str:
    """Return the paper's article element, with SVG figure objects rewritten as images.

    Pandoc drops ``<object>`` elements, so LaTeXML figures embedded as
    ``<object type="image/svg+xml" class="ltx_graphics">`` become ``<img>``
    here (design D17). Both routes call this on the raw page, before the web
    route sanitizes, because the sanitizer deletes every ``<object>`` (D17a).
    Raises ``ArxivConversionError`` when the page has no recognized article.
    """
    article = select_article(html)
    if article is None:
        raise ArxivConversionError("no recognized arXiv article container")
    return _OBJECT_RE.sub(_svg_object_as_img, article)


# ---------------------------------------------------------------------------
# Pandoc
# ---------------------------------------------------------------------------


def run_pandoc(html: str, pandoc_path: str = "pandoc") -> str:
    """Convert an HTML document to markdown with Pandoc; return stdout.

    The one place the Pandoc command and its flags live (design D6). It is
    route-neutral: arXiv conversion and the web route's plain-HTML fallback
    both call it. Raises ``PandocError`` when Pandoc is missing, fails or
    times out.
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
        raise PandocError(
            f"Pandoc not found at '{pandoc_path}'. Install with: "
            "apt install pandoc (or brew install pandoc)"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise PandocError(f"Pandoc timed out after {_PANDOC_TIMEOUT_SECONDS}s") from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise PandocError(f"Pandoc exited with status {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def convert_article(article: str, pandoc_path: str = "pandoc") -> str:
    """Convert an extracted article fragment to cleaned markdown.

    Wraps the fragment as a bare document, applies the LaTeXML pre-processing,
    runs Pandoc and post-processes the output. Raises ``ArxivConversionError``
    when Pandoc fails or the output is shorter than ``MIN_CONTENT_CHARS``.
    """
    document = f"<html><body>{article}</body></html>"
    try:
        output = run_pandoc(_preprocess_html(document), pandoc_path)
    except PandocError as exc:
        raise ArxivConversionError(str(exc)) from exc
    markdown = _postprocess_markdown(output)
    if len(markdown) < MIN_CONTENT_CHARS:
        raise ArxivConversionError(
            f"Pandoc output too short ({len(markdown)} chars, minimum {MIN_CONTENT_CHARS})"
        )
    return markdown


# ---------------------------------------------------------------------------
# Image persistence
# ---------------------------------------------------------------------------

# A Pandoc markdown image ref: ![alt](src){attrs}
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?")

MAX_IMAGE_BYTES = 10 * 1024 * 1024
_IMAGE_TIMEOUT_SECONDS = 15

ImageFetcher = Callable[[str], bytes]


class ImageFetchError(Exception):
    """An image could not be obtained for a reason other than an I/O error."""


def fetch_image(
    url: str, *, max_bytes: int = MAX_IMAGE_BYTES, timeout: int = _IMAGE_TIMEOUT_SECONDS
) -> bytes:
    """Download one image over http(s).

    Raises ``OSError`` (``urllib.error.URLError``, timeouts) on network and
    HTTP errors and ``ImageFetchError`` when the body exceeds *max_bytes*.
    """
    request = urllib.request.Request(url)
    request.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data: bytes = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ImageFetchError(f"larger than {max_bytes} bytes")
    return data


@dataclass(frozen=True)
class ImagePersistResult:
    markdown: str  # refs rewritten for saved images only
    saved_count: int  # files written
    warnings: list[str]  # one per image source not saved


# Media types LaTeXML and arXiv put in data: images; others fall back to mimetypes.
_DATA_URI_EXTENSIONS = {
    "image/svg+xml": ".svg",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def _decode_data_uri(uri: str) -> tuple[bytes, str]:
    """Return the bytes and file extension of a ``data:`` image URI.

    Raises ``ImageFetchError`` when the URI is malformed, its media type has
    no known image extension, or its base64 payload does not decode.
    """
    header, comma, payload = uri.removeprefix("data:").partition(",")
    if not comma:
        raise ImageFetchError("malformed data: URI (no comma)")
    media_type, *params = header.split(";")
    media_type = media_type.strip().lower()
    extension = _DATA_URI_EXTENSIONS.get(media_type)
    if extension is None:
        raise ImageFetchError(f"unsupported data: media type {media_type!r}")
    if "base64" not in params:
        return unquote_to_bytes(payload), extension
    try:
        return base64.b64decode(payload, validate=True), extension
    except binascii.Error as exc:
        raise ImageFetchError(f"invalid base64 payload ({exc})") from exc


def _image_source(base: str, ref: str) -> str:
    """What to read for *ref*: the ``data:`` URI itself, or *ref* resolved against *base*."""
    return ref if ref.startswith("data:") else _resolve_image_url(base, ref)


def _describe_source(source: str) -> str:
    """*source* for a warning, with a ``data:`` payload cut short."""
    return f"{source[:40]}…" if source.startswith("data:") else source


def _resolve_image_url(base: str, ref: str) -> str:
    """Join *ref* onto *base*, collapsing repeated slashes in the path (LaTeXML emits ``//``)."""
    parsed = urlparse(urljoin(base, ref))
    return parsed._replace(path=re.sub(r"/{2,}", "/", parsed.path)).geturl()


def _read_image(url: str, fetch: ImageFetcher) -> bytes:
    """Return the bytes behind *url*: fetched for http(s), read from disk for file."""
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        return fetch(url)
    if parsed.scheme == "file":
        return Path(url2pathname(parsed.path)).read_bytes()
    raise ImageFetchError(f"unsupported URL scheme {parsed.scheme!r}")


def _unique_name(url: str, taken: set[str]) -> str:
    """The URL's file name, suffixed ``_2``, ``_3``… if another URL already took it."""
    name = Path(unquote(urlparse(url).path)).name or "image"
    stem, suffix = Path(name).stem, Path(name).suffix
    n = 1
    while name in taken:
        n += 1
        name = f"{stem}_{n}{suffix}"
    return name


# Every way reading one image fails in practice: network, HTTP and file errors
# (OSError), an unparseable URL (ValueError), a broken HTTP response
# (http.client.HTTPException, e.g. IncompleteRead), oversize or undecodable data.
_IMAGE_FAILURES = (OSError, ValueError, http.client.HTTPException, ImageFetchError)


def _load_image(source: str, fetch: ImageFetcher, taken: set[str]) -> tuple[bytes, str]:
    """Return an image source's bytes and the file name to save them under.

    A ``data:`` image is decoded and named by its content hash (design D18);
    anything else is read through ``_read_image`` and keeps its URL's file name,
    suffixed if *taken*.
    """
    if source.startswith("data:"):
        data, extension = _decode_data_uri(source)
        return data, f"{hashlib.sha256(data).hexdigest()[:16]}{extension}"
    return _read_image(source, fetch), _unique_name(source, taken)


def persist_images(
    markdown: str, base: str, images_dir: Path, fetch: ImageFetcher
) -> ImagePersistResult:
    """Save every image *markdown* references into *images_dir* and point the refs at it.

    Each ref resolves against *base* (``ArxivSource.image_base``). Each distinct
    source is read once: http(s) through *fetch*, ``file:`` from disk, and an
    inline ``data:`` image decoded and named by its content hash (design D18).
    Saved refs become ``images/<name>`` with their attributes kept. A source
    that can't be resolved, read or written leaves every one of its refs
    exactly as written and adds one warning.
    """
    saved: dict[str, str | None] = {}  # image source -> file name, or None if it failed
    names: dict[str, str] = {}  # ref as written -> file name under images_dir
    warnings: list[str] = []
    for ref in dict.fromkeys(m.group(2) for m in _MD_IMAGE_RE.finditer(markdown)):
        source = ref
        try:
            source = _image_source(base, ref)
            if source not in saved:
                saved[source] = None
                data, name = _load_image(source, fetch, {n for n in saved.values() if n})
                images_dir.mkdir(parents=True, exist_ok=True)
                (images_dir / name).write_bytes(data)
                saved[source] = name
        except _IMAGE_FAILURES as exc:
            warnings.append(
                f"Image not saved; kept its original reference: {_describe_source(source)} ({exc})"
            )
            continue
        if (saved_name := saved[source]) is not None:
            names[ref] = saved_name

    def rewrite(m: re.Match[str]) -> str:
        alt, ref, attrs = m.group(1), m.group(2), m.group(3) or ""
        name = names.get(ref)
        return m.group(0) if name is None else f"![{alt}](images/{name}){attrs}"

    file_count = len({n for n in saved.values() if n})
    return ImagePersistResult(_MD_IMAGE_RE.sub(rewrite, markdown), file_count, warnings)
