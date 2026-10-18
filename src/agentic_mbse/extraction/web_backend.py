"""Web content extraction backend — URL to structured markdown.

Fetches HTML pages, strips hidden content, extracts article text
via trafilatura, and writes markdown with YAML frontmatter metadata.

arXiv HTML URLs are detected and routed through the Pandoc-based arXiv
pipeline (arxiv_html.py) which produces far better output for
scientific content (tables with subscripts/superscripts, MathML equations,
proper structure).

Requires trafilatura and beautifulsoup4. Install via:
    pip install agentic-mbse[web]
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

from agentic_mbse.extraction.arxiv_html import (
    MIN_CONTENT_CHARS,
    ArxivConversionError,
    ArxivSource,
    PandocError,
    convert_article,
    extract_article,
    fetch_image,
    persist_images,
    run_pandoc,
)
from agentic_mbse.extraction.base import ExtractionResult, sanitize_filename
from agentic_mbse.extraction.frontmatter import build_frontmatter, compute_source_hash
from agentic_mbse.extraction.http import FetchResult, fetch_url, head_content_type
from agentic_mbse.extraction.metrics import ExtractionMetrics, compute_metrics
from agentic_mbse.extraction.pandoc_convert import (
    resolve_fetched_version,
    strip_arxiv_version,
)

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


log = logging.getLogger(__name__)


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
# Captures the bare arXiv id (without version) from an arXiv HTML URL.
_ARXIV_ID_IN_URL_RE = re.compile(r"/html/(\d{4}\.\d{4,5})")


def _is_arxiv_html_url(url: str) -> bool:
    """Check if URL is an arXiv HTML page."""
    return bool(_ARXIV_HTML_RE.match(url))


def _fallback_pandoc(html: str) -> str | None:
    """Fallback: convert HTML to markdown via Pandoc if available."""
    try:
        markdown = run_pandoc(html)
    except PandocError:
        return None
    return markdown if markdown.strip() else None


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

    # Step 1: Fetch. A version-pinned arXiv HTML URL is fetched at its bare
    # (unversioned) URL so arXiv serves the latest version; if that fetch fails,
    # fall back to the exact requested URL (design.md D5).
    requested_version: int | None = None
    fetch_target = url
    if _is_arxiv_html_url(url):
        fetch_target, requested_version = strip_arxiv_version(url)

    candidates = [fetch_target] if fetch_target == url else [fetch_target, url]
    fetched: FetchResult | None = None
    last_exc: Exception | None = None
    for candidate in candidates:
        try:
            fetched = fetch_url(candidate, timeout=timeout)
            break
        except Exception as exc:
            last_exc = exc
            if candidate != url:
                log.warning("Latest-version fetch failed (%s); retrying %s", exc, url)
    if fetched is None:
        out = output_dir or Path(".")
        return ExtractionResult(
            success=False,
            output_dir=out,
            error=f"Failed to fetch {url}: {last_exc}",
        )

    html = fetched.text()
    final_url = fetched.final_url

    # Step 2: Sanitize
    if sanitize:
        from agentic_mbse.extraction.html_sanitize import strip_hidden_content

        html = strip_hidden_content(html)

    # Step 3: Extract — arXiv HTML converts only the paper's article element
    # through Pandoc; everything else goes through trafilatura with a
    # whole-page Pandoc fallback. The article is taken from the raw page and
    # sanitized on its own, because the sanitizer deletes the SVG figure
    # objects that extract_article turns into images (design D17a).
    markdown: str | None = None
    metadata: dict = {}
    backend = "trafilatura"
    extraction_warnings: list[str] = []
    image_base: str | None = None  # set when the arXiv paper converts; its figures are saved
    is_arxiv = _is_arxiv_html_url(final_url)

    if is_arxiv:
        log.info("arXiv HTML detected, converting the paper with Pandoc")
        # One source for the article and its image base, as on the PDF route.
        source = ArxivSource.from_fetch(fetched)
        try:
            article = extract_article(source.html)
            if sanitize:
                from agentic_mbse.extraction.html_sanitize import strip_hidden_content

                article = strip_hidden_content(article)
            markdown = convert_article(article)
            backend = "pandoc-arxiv"
            image_base = source.image_base
            # Still grab metadata from trafilatura (title, author, date)
            _, metadata = _extract_with_trafilatura(html, final_url)
        except ArxivConversionError as exc:
            log.warning("arXiv paper conversion failed (%s), falling back to trafilatura", exc)
            extraction_warnings.append(
                f"arXiv paper conversion failed ({exc}); used trafilatura instead"
            )
            markdown = None  # fall through to trafilatura below

    if markdown is None:
        markdown, metadata = _extract_with_trafilatura(html, final_url)
        backend = "trafilatura"

    # Step 3b: Fallback to whole-page Pandoc if trafilatura returned too little.
    # Never for arXiv: the whole page is exactly the chrome the article
    # selection exists to drop, so a short trafilatura result stands.
    if not is_arxiv and (not markdown or len(markdown) < MIN_CONTENT_CHARS):
        log.info(
            "trafilatura returned %d chars, trying pandoc fallback",
            len(markdown or ""),
        )
        pandoc_md = _fallback_pandoc(html)
        if pandoc_md and len(pandoc_md) >= MIN_CONTENT_CHARS:
            markdown = pandoc_md
            backend = "pandoc-fallback"

    if not markdown:
        out = output_dir or Path(".")
        return ExtractionResult(
            success=False,
            output_dir=out,
            error=f"No content extracted from {url}",
            warnings=extraction_warnings,  # why the arXiv conversion fell back, if it did
        )

    # Step 4: Build output
    title = metadata.get("title") or ""
    content_hash = compute_source_hash(fetched.content)  # hash raw HTML bytes

    # For arXiv, record the version arXiv actually served (bare URL = latest) in
    # the source, so provenance names the fetched version, not the pinned one.
    source_url = final_url
    if backend == "pandoc-arxiv":
        m = _ARXIV_ID_IN_URL_RE.search(final_url)
        if m:
            bare_id = m.group(1)
            version = resolve_fetched_version(html, bare_id)
            if version is not None:
                source_url = f"https://arxiv.org/html/{bare_id}v{version}"
                if requested_version is not None and requested_version != version:
                    log.info(
                        "arXiv version upgrade: requested v%d → fetched v%d",
                        requested_version,
                        version,
                    )

    if no_frontmatter:
        full_markdown = markdown
    else:
        backend_str = backend  # "trafilatura", "pandoc-arxiv", or "pandoc-fallback"
        frontmatter = build_frontmatter(
            source=source_url,
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

    # Step 4a: Save the paper's figures (pandoc-arxiv only)
    image_count = 0
    if image_base is not None:
        images = persist_images(full_markdown, image_base, output_dir / "images", fetch_image)
        full_markdown, image_count = images.markdown, images.saved_count
        extraction_warnings.extend(images.warnings)

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
    metrics_dict["image_count"] = image_count
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
