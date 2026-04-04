"""Web content extraction backend — URL to structured markdown.

Fetches HTML pages, strips hidden content, extracts article text
via trafilatura, and writes markdown with YAML frontmatter metadata.

arXiv HTML URLs are detected and routed through the Pandoc-based arXiv
pipeline (pandoc_convert.py) which produces far better output for
scientific content (tables with subscripts/superscripts, MathML equations,
proper structure).

Requires trafilatura and beautifulsoup4. Install via:
    pip install agentic-mbse[web]
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

from agentic_mbse.extraction.base import ExtractionResult, sanitize_filename
from agentic_mbse.extraction.frontmatter import build_frontmatter, compute_source_hash
from agentic_mbse.extraction.http import FetchResult, fetch_url, head_content_type
from agentic_mbse.extraction.metrics import ExtractionMetrics, compute_metrics

# Minimum extracted content length before trying fallback
_MIN_CONTENT_LENGTH = 100

# Content types routed to the web backend
_HTML_CONTENT_TYPES = frozenset(
    {
        "text/html",
        "application/xhtml+xml",
    }
)

_PDF_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
    }
)


_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?")

log = logging.getLogger(__name__)


def _download_arxiv_images(
    markdown: str,
    page_url: str,
    output_dir: Path,
    *,
    max_image_bytes: int = 10 * 1024 * 1024,
    timeout: int = 15,
) -> tuple[str, int, list[str]]:
    """Download images from arXiv markdown and rewrite refs to local paths.

    Returns (rewritten_markdown, download_count, warnings).
    """
    from agentic_mbse.extraction.http import USER_AGENT

    matches = list(_MD_IMAGE_RE.finditer(markdown))
    if not matches:
        return markdown, 0, []

    images_dir = output_dir / "images"
    download_count = 0
    warnings: list[str] = []
    used_filenames: dict[str, int] = {}  # basename -> times seen

    # Process replacements in reverse order to preserve string positions
    replacements: list[tuple[int, int, str]] = []

    for m in matches:
        alt, img_url, attr_block = m.group(1), m.group(2), m.group(3) or ""
        attr_str = attr_block

        # Skip data: URIs
        if img_url.startswith("data:"):
            continue

        # Resolve URL (normalize repeated slashes from LaTeXML paths)
        if img_url.startswith("/"):
            # Root-relative: resolve against arxiv.org
            normalized = re.sub(r"/+", "/", img_url)
            abs_url = f"https://arxiv.org{normalized}"
        elif img_url.startswith(("http://", "https://")):
            abs_url = img_url
        else:
            # Relative to page URL
            abs_url = urljoin(page_url, img_url)

        # Extract filename
        parsed_path = urlparse(abs_url).path
        basename = Path(parsed_path).name
        if not basename:
            continue

        # Handle duplicate filenames
        if basename in used_filenames:
            used_filenames[basename] += 1
            stem = Path(basename).stem
            suffix = Path(basename).suffix
            local_name = f"{stem}_{used_filenames[basename]}{suffix}"
        else:
            used_filenames[basename] = 1
            local_name = basename

        # Download
        try:
            req = urllib.request.Request(abs_url)
            req.add_header("User-Agent", USER_AGENT)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read(max_image_bytes + 1)
                if len(data) > max_image_bytes:
                    msg = f"Image too large ({len(data)} bytes), skipping: {abs_url}"
                    log.warning(msg)
                    warnings.append(msg)
                    continue
        except Exception as exc:
            msg = f"Failed to download image: {abs_url} ({exc})"
            log.warning(msg)
            warnings.append(msg)
            continue

        # Save
        images_dir.mkdir(parents=True, exist_ok=True)
        (images_dir / local_name).write_bytes(data)
        download_count += 1

        # Record replacement
        new_ref = f"![{alt}](images/{local_name}){attr_str}"
        replacements.append((m.start(), m.end(), new_ref))

    # Apply replacements in reverse order
    result = markdown
    for start, end, new_text in reversed(replacements):
        result = result[:start] + new_text + result[end:]

    return result, download_count, warnings


def check_web_deps() -> None:
    """Check that web extraction dependencies are installed.

    Raises ImportError with an actionable message if missing.
    """
    try:
        import trafilatura  # noqa: F401
    except ImportError:
        raise ImportError(
            "Web extraction requires additional dependencies.\n"
            "Install with: pip install agentic-mbse[web]\n"
            "         or: uv add agentic-mbse --extra web"
        ) from None

    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        raise ImportError(
            "Web extraction requires beautifulsoup4.\n"
            "Install with: pip install agentic-mbse[web]\n"
            "         or: uv add agentic-mbse --extra web"
        ) from None


def classify_url(url: str) -> str:
    """Classify URL by content type via HEAD request.

    Returns:
        "html", "pdf", or the raw content-type string for unknown types.
    """
    ct = head_content_type(url)
    if ct is None:
        # HEAD failed — assume HTML (most common, and trafilatura
        # handles non-HTML gracefully)
        return "html"
    if ct in _HTML_CONTENT_TYPES:
        return "html"
    if ct in _PDF_CONTENT_TYPES:
        return "pdf"
    return ct


def _extract_with_trafilatura(
    html: str,
    url: str,
) -> tuple[str | None, dict]:
    """Run trafilatura extraction, return (markdown, metadata_dict).

    Uses extract() for markdown text and bare_extraction() for metadata.
    trafilatura 2.0 returns a Document object from bare_extraction
    (not a dict), so we access attributes directly.
    """
    import trafilatura

    # Get markdown text
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        include_links=True,
        output_format="markdown",
    )

    # Get metadata via bare_extraction (returns Document object in 2.0+)
    doc = trafilatura.bare_extraction(
        html,
        url=url,
        include_comments=False,
        with_metadata=True,
    )

    metadata: dict = {}
    if doc is not None:
        metadata = {
            "title": getattr(doc, "title", None),
            "author": getattr(doc, "author", None),
            "date": getattr(doc, "date", None),
        }

    return text, metadata


_ARXIV_HTML_RE = re.compile(r"https?://arxiv\.org/html/\d{4}\.\d{4,5}")


def _is_arxiv_html_url(url: str) -> bool:
    """Check if URL is an arXiv HTML page."""
    return bool(_ARXIV_HTML_RE.match(url))


def _extract_with_arxiv_pandoc(html: str) -> str | None:
    """Convert arXiv/LaTeXML HTML to markdown via Pandoc with arXiv-specific
    pre/post-processing.

    Reuses the proven pipeline from pandoc_convert.py that the PDF
    extraction arXiv shortcut uses. Returns None on failure.
    """
    from agentic_mbse.extraction.pandoc_convert import (
        _pandoc_available,
        _postprocess_markdown,
        _preprocess_html,
    )

    if not _pandoc_available():
        return None

    import subprocess

    processed = _preprocess_html(html)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(processed)
        tmp = Path(f.name)

    try:
        # Pandoc flags match convert_arxiv_html() in pandoc_convert.py (:180-188).
        result = subprocess.run(
            [
                "pandoc",
                str(tmp),
                "-f",
                "html-native_divs-native_spans",
                "-t",
                "markdown-header_attributes",
                "--wrap=none",
                "--markdown-headings=atx",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            return _postprocess_markdown(result.stdout)
        return None
    except Exception:
        return None
    finally:
        tmp.unlink(missing_ok=True)


def _fallback_pandoc(html: str) -> str | None:
    """Fallback: convert HTML to markdown via Pandoc if available."""
    if not shutil.which("pandoc"):
        return None

    import subprocess

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = Path(f.name)

    try:
        # NOTE: Pandoc flags must stay in sync with convert_arxiv_html()
        # in pandoc_convert.py (:178-186).
        result = subprocess.run(
            [
                "pandoc",
                str(tmp),
                "-f",
                "html-native_divs-native_spans",
                "-t",
                "markdown-header_attributes",
                "--wrap=none",
                "--markdown-headings=atx",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        return None
    except Exception:
        return None
    finally:
        tmp.unlink(missing_ok=True)


def extract_web_content(
    url: str,
    *,
    output_dir: Path | None = None,
    sanitize: bool = True,
    save_source: bool = False,
    no_frontmatter: bool = False,
    timeout: int = 30,
) -> ExtractionResult:
    """Extract web page content to structured markdown.

    Pipeline: fetch → sanitize → extract → write output.

    Args:
        url: The URL to fetch and extract.
        output_dir: Where to write output files. If None, creates a
            directory alongside CWD based on the page title/domain.
        sanitize: If True, run HTML sanitization pre-pass (default True).
        save_source: If True, save the original (pre-sanitization) HTML
            alongside the extracted markdown as ``raw.html``.
        no_frontmatter: If True, suppress YAML frontmatter in output.
        timeout: HTTP request timeout in seconds.

    Returns:
        ExtractionResult with success status, output paths, and metrics.
    """
    import time

    t0 = time.monotonic()

    # Step 1: Fetch
    try:
        fetched: FetchResult = fetch_url(url, timeout=timeout)
    except Exception as exc:
        out = output_dir or Path(".")
        return ExtractionResult(
            success=False,
            output_dir=out,
            error=f"Failed to fetch {url}: {exc}",
        )

    html = fetched.text()
    final_url = fetched.final_url

    # Step 2: Sanitize
    if sanitize:
        from agentic_mbse.extraction.html_sanitize import strip_hidden_content

        html = strip_hidden_content(html)

    # Step 3: Extract — route arXiv HTML through Pandoc (proven pipeline),
    # everything else through trafilatura with Pandoc fallback.
    markdown: str | None = None
    metadata: dict = {}
    backend = "trafilatura"

    if _is_arxiv_html_url(final_url):
        log.info("arXiv HTML detected, using Pandoc extraction pipeline")
        markdown = _extract_with_arxiv_pandoc(html)
        if markdown and len(markdown) >= _MIN_CONTENT_LENGTH:
            backend = "pandoc-arxiv"
            # Still grab metadata from trafilatura (title, author, date)
            _, metadata = _extract_with_trafilatura(html, final_url)
        else:
            log.warning("Pandoc arXiv extraction failed/short, falling back to trafilatura")
            markdown = None  # fall through to trafilatura below

    if markdown is None:
        markdown, metadata = _extract_with_trafilatura(html, final_url)
        backend = "trafilatura"

    # Step 3b: Fallback to pandoc if trafilatura returned too little
    if not markdown or len(markdown) < _MIN_CONTENT_LENGTH:
        log.info(
            "trafilatura returned %d chars, trying pandoc fallback",
            len(markdown or ""),
        )
        pandoc_md = _fallback_pandoc(html)
        if pandoc_md and len(pandoc_md) >= _MIN_CONTENT_LENGTH:
            markdown = pandoc_md
            backend = "pandoc-fallback"

    if not markdown:
        out = output_dir or Path(".")
        return ExtractionResult(
            success=False,
            output_dir=out,
            error=f"No content extracted from {url}",
        )

    # Step 4: Build output
    title = metadata.get("title") or ""
    content_hash = compute_source_hash(fetched.content)  # hash raw HTML bytes

    if no_frontmatter:
        full_markdown = markdown
    else:
        backend_str = backend  # "trafilatura", "pandoc-arxiv", or "pandoc-fallback"
        frontmatter = build_frontmatter(
            source=final_url,
            source_type="url",
            backend=backend_str,
            content_hash=content_hash,
            title=title or None,
            author=metadata.get("author"),
        )
        full_markdown = f"{frontmatter}\n\n{markdown}"

    # Determine output directory name from title or URL
    dir_name = sanitize_filename(title) if title else sanitize_filename(final_url)
    if not dir_name or dir_name.startswith("https___") or dir_name.startswith("http___"):
        # Fallback: use domain + path fragment
        parsed = urlparse(final_url)
        dir_name = sanitize_filename(f"{parsed.netloc}{parsed.path}")

    caller_provided_dir = output_dir is not None
    if output_dir is None:
        output_dir = Path.cwd() / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 4a: Download images (pandoc-arxiv only)
    image_count = 0
    extraction_warnings: list[str] = []
    if backend == "pandoc-arxiv":
        full_markdown, image_count, extraction_warnings = _download_arxiv_images(
            full_markdown, final_url, output_dir
        )

    # Write markdown — when the caller provides output_dir (e.g., batch mode
    # with --output), use "output.md" to avoid filename collisions between
    # URLs that share the same title.  When auto-creating the dir, use a
    # title-derived name for readability.
    md_filename = "output.md" if caller_provided_dir else f"{dir_name}.md"
    md_path = output_dir / md_filename
    md_path.write_text(full_markdown, encoding="utf-8")

    # Write metrics
    elapsed = time.monotonic() - t0
    metrics: ExtractionMetrics = compute_metrics(markdown, elapsed)
    metrics_dict = metrics.to_dict()
    if extraction_warnings:
        metrics_dict["warnings"] = extraction_warnings
    (output_dir / "metrics.json").write_text(json.dumps(metrics_dict, indent=2))

    # Optionally save raw source HTML
    if save_source:
        (output_dir / "raw.html").write_text(fetched.text(), encoding="utf-8")

    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        image_count=image_count,
        char_count=metrics.char_count,
        backend_used=backend,
        warnings=extraction_warnings,
    )
