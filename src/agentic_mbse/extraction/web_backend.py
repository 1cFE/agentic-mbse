"""Web content extraction backend — URL to structured markdown.

Fetches HTML pages, strips hidden content, extracts article text
via trafilatura, and writes markdown with YAML frontmatter metadata.

Requires trafilatura and beautifulsoup4. Install via:
    pip install agentic-mbse[web]
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult, sanitize_filename
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


def _sanitize_yaml_value(value: str) -> str:
    """Escape a string for use as a double-quoted YAML value."""
    # Strip newlines/carriage returns, collapse whitespace, escape quotes
    value = value.replace("\r", "").replace("\n", " ")
    value = " ".join(value.split())  # collapse runs of whitespace
    value = value.replace('"', "'")
    return value


def _build_frontmatter(
    *,
    source_url: str,
    content_hash: str,
    title: str | None,
    author: str | None,
    tool_version: str,
) -> str:
    """Build YAML frontmatter string."""
    lines = ["---"]
    lines.append(f'source_url: "{_sanitize_yaml_value(source_url)}"')
    lines.append(f'access_date: "{datetime.now(timezone.utc).isoformat()}"')
    lines.append(f'content_hash_sha256: "{content_hash}"')
    if title:
        lines.append(f'title: "{_sanitize_yaml_value(title)}"')
    if author:
        lines.append(f'author: "{_sanitize_yaml_value(author)}"')
    lines.append(f'extraction_tool: "{tool_version}"')
    lines.append("---")
    return "\n".join(lines)


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
    save_raw_html: bool = False,
    timeout: int = 30,
) -> ExtractionResult:
    """Extract web page content to structured markdown.

    Pipeline: fetch → sanitize → extract → write output.

    Args:
        url: The URL to fetch and extract.
        output_dir: Where to write output files. If None, creates a
            directory alongside CWD based on the page title/domain.
        sanitize: If True, run HTML sanitization pre-pass (default True).
        save_raw_html: If True, save the original (pre-sanitization) HTML
            alongside the extracted markdown as ``raw.html``.
        timeout: HTTP request timeout in seconds.

    Returns:
        ExtractionResult with success status, output paths, and metrics.
    """
    import logging
    import time

    log = logging.getLogger(__name__)
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

    # Step 3: Extract with trafilatura
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
    content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()

    # Determine trafilatura version for frontmatter
    import trafilatura as _traf

    traf_version = getattr(_traf, "__version__", "unknown")
    tool_str = f"trafilatura {traf_version}" if backend == "trafilatura" else "pandoc (fallback)"

    frontmatter = _build_frontmatter(
        source_url=final_url,
        content_hash=content_hash,
        title=title or None,
        author=metadata.get("author"),
        tool_version=tool_str,
    )

    full_markdown = f"{frontmatter}\n\n{markdown}"

    # Determine output directory name from title or URL
    dir_name = sanitize_filename(title) if title else sanitize_filename(final_url)
    if not dir_name or dir_name.startswith("https___") or dir_name.startswith("http___"):
        # Fallback: use domain + path fragment
        from urllib.parse import urlparse

        parsed = urlparse(final_url)
        dir_name = sanitize_filename(f"{parsed.netloc}{parsed.path}")

    caller_provided_dir = output_dir is not None
    if output_dir is None:
        output_dir = Path.cwd() / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

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
    (output_dir / "metrics.json").write_text(json.dumps(metrics.to_dict(), indent=2))

    # Optionally save raw HTML
    if save_raw_html:
        (output_dir / "raw.html").write_text(fetched.text(), encoding="utf-8")

    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        image_count=0,
        char_count=metrics.char_count,
        backend_used=backend,
    )
