# Design: Web Source Capture

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-28 10:27 PDT
**Branch:** `webfetch-tools`
**Commit:** `af49028`

---

## Overview

Add URL-to-markdown extraction to `agentic-mbse extract` via a new web backend, HTML sanitization module, and shared HTTP utility. URLs are dispatched by content type: HTML goes through trafilatura extraction with a BeautifulSoup sanitization pre-pass; PDF URLs download and route through the existing pipeline. Dependencies are optional (`[web]` extra).

## Related Artifacts

- **Spec:** `.project/active/web-source-capture/spec.md`
- **Research:** `.project/research/20260328-web-source-capture-integration.md`
- **Upstream:** `fusion-tea/.project/research/20260328-source-capture-pipeline-feasibility.md`, `fusion-tea/.project/research/20260328-web-content-sanitization-for-llm-pipelines.md`

---

## Research Findings

### Existing Patterns to Follow

**CLI dispatch** (`cli/extract_cli.py`):
- `cmd_extract()` (:196) uses a `for doc in docs:` loop with per-extension branching: `.pdf` → `extract_pdf()`, `.docx` → `_run_extraction()` with backend selection
- URL dispatch should happen *before* the `discover_documents()` call, since URLs are not files on disk
- `MockArgs` pattern in `test_extract_cli.py` (:24-51) — test args class with defaults dict. New flags (`urls_from`, `no_sanitize`, `raw_html`) need entries here
- `register_extract_subcommand()` (:492-620) adds argparse flags. New flags slot in after the existing groups

**HTTP fetching** (`extraction/pandoc_convert.py`):
- User-Agent: `"agentic-mbse/0.1 (PDF extraction pipeline)"` — hardcoded in two places (:116, :159)
- HEAD check: `check_arxiv_html()` (:111-124) — `urllib.request.Request(url, method="HEAD")`, timeout=5
- Full download: `convert_arxiv_html()` (:132-206) — `urllib.request.Request(url)`, timeout=30, `.read().decode("utf-8")`
- Both use `urllib.request` (stdlib), no `requests` library

**Result types** (`extraction/base.py`):
- `ExtractionResult` (:18-28) — 7 fields: `success`, `output_dir`, `markdown_path`, `image_count`, `char_count`, `error`, `backend_used`
- `get_output_dir()` (:56-65) — takes `input_path: Path` + optional `output_base`. For URLs we need a different approach: derive dir name from sanitized URL/title
- `sanitize_filename()` (:44-53) — strips extension, replaces non-alnum with `_`, truncates to 100 chars. Reusable for URL-derived names
- `write_summary()` (:105-131) — writes `summary.json` with file hash. For web content, we don't have a source file to hash — use content hash instead

**Metrics** (`extraction/metrics.py`):
- `compute_metrics(markdown, elapsed)` (:41-108) → `ExtractionMetrics` — works on any markdown string, no PDF assumptions. Directly reusable for web extraction output

**Optional dependencies** (`pyproject.toml`):
- Existing pattern: `extract = ["pymupdf4llm>=0.0.17"]`, `extract-full = ["docling>=2.0", ...]` (:33-35)
- Lazy import pattern in `_is_available()` (:34-52) and `_run_extraction()` (:116-142) — `try: import X; except ImportError: return False`

**Test patterns** (`test_pandoc_convert.py`, `test_extract_cli.py`):
- Pure function tests (preprocessing, postprocessing) use direct assertions
- HTTP tests use `@patch("module.urllib.request.urlopen")` with mock response objects
- CLI tests use `MockArgs` + `@patch` on pipeline functions
- No live network calls in tests

### Integration Points

| Point | File:Line | How Web Capture Connects |
|-------|-----------|--------------------------|
| CLI entry | `extract_cli.py:196` | New URL branch before `discover_documents()` |
| Arg registration | `extract_cli.py:492` | Add `--urls-from`, `--no-sanitize`, `--raw-html` |
| Output dir | `base.py:56` | Use `sanitize_filename(title_or_domain)` for URL-derived dirs |
| Result type | `base.py:18` | Return `ExtractionResult` directly |
| Metrics | `metrics.py:41` | Call `compute_metrics(markdown)` on extracted content |
| User-Agent | `pandoc_convert.py:116,159` | Replace with import from `http.py` |
| Package exports | `__init__.py:3-22` | Add `extract_web_content` if we want a public API |

---

## Proposed Design

### Component Overview

```
                        cmd_extract(args)
                              │
                    ┌─────────┼──────────┐
                    │         │          │
               URL input   .pdf file  .docx file
                    │         │          │
              ┌─────┴─────┐   │          │
              │ HEAD req  │   │          │
              │ for type  │   │          │
              └─────┬─────┘   │          │
               ┌────┴────┐    │          │
             HTML      PDF    │          │
               │      (download          │
               │       to tmp)│          │
               │         │    │          │
          web_backend   extract_pdf  _run_extraction
               │              │          │
        ┌──────┴──────┐       │          │
    html_sanitize  trafilatura│          │
        │              │      │          │
        └──────┬───────┘      │          │
               │              │          │
          ExtractionResult    │          │
           + metrics.json     │          │
                              │          │
        ───── shared http.py (fetch_url, head_content_type) ─────
```

### 1. `extraction/http.py` — Shared HTTP Utility

**Purpose:** Consolidate URL fetching logic used by both `pandoc_convert.py` and `web_backend.py`.

**Location:** `src/agentic_mbse/extraction/http.py`

**Dependencies:** stdlib only (`urllib.request`, `urllib.error`)

```python
"""Shared HTTP utilities for extraction backends."""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "agentic-mbse/0.1 (document extraction pipeline)"

DEFAULT_TIMEOUT = 30  # seconds
HEAD_TIMEOUT = 5      # seconds


@dataclass
class FetchResult:
    """Result of an HTTP fetch."""

    content: bytes
    final_url: str
    content_type: str
    encoding: str | None = None

    def text(self) -> str:
        """Decode content to string."""
        enc = self.encoding or "utf-8"
        return self.content.decode(enc)


def fetch_url(url: str, *, timeout: int = DEFAULT_TIMEOUT) -> FetchResult:
    """Fetch URL content with standard headers.

    Returns FetchResult with content bytes, final URL (after redirects),
    content type, and detected encoding.

    Raises:
        urllib.error.URLError: On network errors.
        urllib.error.HTTPError: On HTTP error status codes.
        TimeoutError: When request exceeds timeout.
    """
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content = resp.read()
        final_url = resp.url  # after redirects
        content_type = resp.headers.get_content_type() or ""
        encoding = resp.headers.get_content_charset()
        return FetchResult(
            content=content,
            final_url=final_url,
            content_type=content_type,
            encoding=encoding,
        )


def head_content_type(url: str, *, timeout: int = HEAD_TIMEOUT) -> str | None:
    """Send HEAD request and return Content-Type, or None on failure."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.headers.get_content_type()
    except Exception:
        return None
```

**Refactoring `pandoc_convert.py`:** Replace inline urllib usage with imports from `http.py`:
- `check_arxiv_html()` (:111-124) → use `head_content_type()` or keep as-is (it checks status code, not content type). Minimal change: import `USER_AGENT` constant and `HEAD_TIMEOUT`.
- `convert_arxiv_html()` (:156-163) → use `fetch_url()` for the URL branch. The local file branch stays unchanged.

The refactoring of `pandoc_convert.py` is conservative — we replace the duplicated User-Agent string and urllib boilerplate while keeping the same external behavior. The arXiv-specific pre/post-processing stays in `pandoc_convert.py`.

### 2. `extraction/html_sanitize.py` — HTML Sanitization

**Purpose:** Strip CSS-hidden elements, scripts, and zero-width characters from HTML before content extraction. Addresses the gap no standard Python library fills (FR-6).

**Location:** `src/agentic_mbse/extraction/html_sanitize.py`

**Dependencies:** `beautifulsoup4` (optional — guarded import), `lxml` (preferred parser, falls back to `html.parser`), `re` (stdlib)

```python
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

# Off-screen positioning pattern (must be combined with position:absolute)
_OFFSCREEN = re.compile(r"(?:left|top)\s*:\s*-\d{4,}", re.IGNORECASE)
_POSITION_ABS = re.compile(r"position\s*:\s*(?:absolute|fixed)", re.IGNORECASE)


def strip_hidden_content(html: str) -> str:
    """Remove elements hidden from human viewers but visible to text extractors.

    Three-layer stripping:
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
```

**Design decisions:**
- Parser selection is runtime: try `lxml` first (5-10x faster), fall back to `html.parser` (stdlib). Both are valid BeautifulSoup parsers.
- The `opacity:0` regex uses `0(?:[;\s"]|$)` to avoid matching `opacity: 0.5` — a common legitimate CSS value.
- `font-size:0` similarly anchors to avoid matching `font-size: 0.8em`.
- Zero-width stripping uses a character-level filter on the final string rather than per-text-node traversal. Simpler and handles characters that span tag boundaries.
- The function raises `ImportError` naturally (via `from bs4 import BeautifulSoup`) — no wrapper needed. The CLI catches this at dispatch time.

### 3. `extraction/web_backend.py` — Web Extraction

**Purpose:** Fetch URL, sanitize HTML, extract article content via trafilatura, produce markdown with YAML frontmatter and metrics.

**Location:** `src/agentic_mbse/extraction/web_backend.py`

**Dependencies:** `trafilatura` (optional — lazy import), `html_sanitize` (internal), `http` (internal), stdlib (`hashlib`, `datetime`, `json`, `shutil`, `tempfile`)

```python
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
_HTML_CONTENT_TYPES = frozenset({
    "text/html",
    "application/xhtml+xml",
})

_PDF_CONTENT_TYPES = frozenset({
    "application/pdf",
})


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

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html)
        tmp = Path(f.name)

    try:
        # NOTE: Pandoc flags must stay in sync with convert_arxiv_html()
        # in pandoc_convert.py (:178-186).
        result = subprocess.run(
            [
                "pandoc", str(tmp),
                "-f", "html-native_divs-native_spans",
                "-t", "markdown-header_attributes",
                "--wrap=none",
                "--markdown-headings=atx",
            ],
            capture_output=True, text=True, timeout=60,
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
        save_raw_html: If True, save raw HTML alongside markdown.
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
        log.info("trafilatura returned %d chars, trying pandoc fallback",
                 len(markdown or ""))
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

    # Determine trafilatura version for frontmatter (module already
    # imported by _extract_with_trafilatura above)
    import trafilatura as _traf  # cached — no re-import cost
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

    if output_dir is None:
        output_dir = Path.cwd() / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write markdown
    md_filename = f"{dir_name}.md"
    md_path = output_dir / md_filename
    md_path.write_text(full_markdown, encoding="utf-8")

    # Write metrics
    elapsed = time.monotonic() - t0
    metrics: ExtractionMetrics = compute_metrics(markdown, elapsed)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics.to_dict(), indent=2)
    )

    # Optionally save raw HTML
    if save_raw_html:
        (output_dir / "raw.html").write_text(
            fetched.text(), encoding="utf-8"
        )

    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        image_count=0,
        char_count=metrics.char_count,
        backend_used=backend,
    )
```

**Key design decisions:**

- **`classify_url()`** is separate from `extract_web_content()` so the CLI can dispatch PDF URLs to the PDF pipeline before ever importing trafilatura.
- **`_fallback_pandoc()`** reuses the same Pandoc flags as `pandoc_convert.py` (:178-186) for consistency. A sync comment marks the duplication so future changes update both sites.
- **`_build_frontmatter()`** uses manual string building rather than `yaml.dump()` to avoid a dependency on PyYAML formatting details (quote style, key order). Values are sanitized via `_sanitize_yaml_value()` which strips newlines, collapses whitespace, and escapes double quotes.
- **`check_web_deps()`** is a separate function the CLI calls early, before any extraction logic. This gives a clean error message rather than a raw `ImportError` traceback.
- The function does **not** call `write_summary()` from `base.py` because that function expects a source file for hashing (`_compute_file_hash`). Web content has no source file — the content hash in the YAML frontmatter serves the same purpose. Instead, metrics.json is written directly.
- **Output directory naming**: Prefers page title (via `sanitize_filename`), falls back to domain+path. This produces readable directory names like `Fusion_energy` instead of `https___en_wikipedia_org_wiki_Fusion_energy`.
- **Timing**: `time.monotonic()` brackets the fetch+extract pipeline so `ExtractionMetrics.extraction_time_seconds` is populated, not left at 0.0.
- **`trafilatura` API (2.0+)**: `bare_extraction()` returns a `Document` object (not a dict as in 1.x). We use `extract()` for formatted markdown text and `bare_extraction()` with `getattr()` for metadata only. Two calls are needed because `extract()` returns the formatted string but no metadata, while `bare_extraction()` has metadata but not formatted output.

### 4. CLI Integration — `extract_cli.py` Changes

**URL dispatch** goes at the top of `cmd_extract()`, before the `discover_documents()` path. This keeps URL handling cleanly separated from file handling:

```python
def cmd_extract(args: argparse.Namespace) -> int:
    # ... deprecation warnings unchanged ...

    # --check handling unchanged ...

    # ---- NEW: URL and batch-URL dispatch ----

    # Batch URL mode
    if getattr(args, "urls_from", None):
        return _extract_urls_from_file(args)

    # Single URL mode
    if args.path and args.path.startswith(("http://", "https://")):
        return _extract_url(args.path, args)

    # ---- Existing file-based path (unchanged) ----

    if args.path is None:
        print("Error: path is required (unless using --check)")
        return EXIT_FAILURE

    path = Path(args.path)
    # ... rest of existing logic ...
```

**New dispatch functions:**

```python
def _extract_url(url: str, args: argparse.Namespace) -> int:
    """Handle a single URL extraction."""
    from agentic_mbse.extraction.web_backend import (
        check_web_deps,
        classify_url,
        extract_web_content,
    )

    # Check dependencies early
    try:
        check_web_deps()
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    # Classify URL content type
    url_type = classify_url(url)

    if url_type == "pdf":
        # Download PDF to temp file, run through PDF pipeline
        return _extract_pdf_url(url, args)

    if url_type not in ("html",):
        print(f"Error: unsupported content type '{url_type}' for {url}")
        return EXIT_FAILURE

    output_base = Path(args.output) if args.output else None
    result = extract_web_content(
        url,
        output_dir=output_base,
        sanitize=not getattr(args, "no_sanitize", False),
        save_raw_html=getattr(args, "raw_html", False),
        timeout=args.timeout,
    )

    if result.success:
        stats = []
        if result.char_count:
            stats.append(f"{result.char_count:,} chars")
        stats.append(f"backend: {result.backend_used}")
        print(f"   ok   {url} ({', '.join(stats)})")
        if result.markdown_path:
            print(f"        → {result.markdown_path}")
        return EXIT_SUCCESS
    else:
        print(f"  FAIL  {url}: {result.error}")
        return EXIT_FAILURE


def _extract_pdf_url(url: str, args: argparse.Namespace) -> int:
    """Download a PDF from URL and extract via the PDF pipeline."""
    import copy
    import tempfile

    from agentic_mbse.extraction.http import fetch_url

    print(f"  fetch {url} (PDF detected)")
    try:
        fetched = fetch_url(url, timeout=args.timeout)
    except Exception as exc:
        print(f"  FAIL  Download failed: {exc}")
        return EXIT_FAILURE

    # Write to temp file, then extract as normal PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(fetched.content)
        tmp_pdf = Path(f.name)

    try:
        # Shallow-copy args to avoid corrupting shared state in batch mode
        pdf_args = copy.copy(args)
        pdf_args.path = str(tmp_pdf)
        return cmd_extract(pdf_args)
    finally:
        tmp_pdf.unlink(missing_ok=True)


def _extract_urls_from_file(args: argparse.Namespace) -> int:
    """Process URLs from a text file (one per line)."""
    urls_file = Path(args.urls_from)
    if not urls_file.exists():
        print(f"Error: URLs file not found: {urls_file}")
        return EXIT_FAILURE

    urls = [
        line.strip()
        for line in urls_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print(f"Error: no URLs found in {urls_file}")
        return EXIT_FAILURE

    print(f"Processing {len(urls)} URLs from {urls_file}")
    ok = 0
    fail = 0
    for url in urls:
        rc = _extract_url(url, args)
        if rc == EXIT_SUCCESS:
            ok += 1
        else:
            fail += 1

    print(f"\nProcessed: {ok}, Failed: {fail}")
    return EXIT_FAILURE if fail > 0 else EXIT_SUCCESS
```

**New argparse flags** (added in `register_extract_subcommand()`):

```python
# Web extraction flags
p.add_argument(
    "--urls-from",
    default=None,
    metavar="FILE",
    help="Read URLs from FILE (one per line) for batch extraction",
)
p.add_argument(
    "--no-sanitize",
    action="store_true",
    help="Skip HTML sanitization pre-pass (web extraction only)",
)
p.add_argument(
    "--raw-html",
    action="store_true",
    help="Save raw HTML alongside extracted markdown (web extraction only)",
)
```

**`MockArgs` update** in `test_extract_cli.py` — add defaults:
```python
urls_from=None,
no_sanitize=False,
raw_html=False,
```

### 5. `pyproject.toml` Changes

```toml
[project.optional-dependencies]
extract = ["pymupdf4llm>=0.0.17"]
extract-tables = ["gmft>=0.3"]
extract-full = ["docling>=2.0", "pymupdf4llm>=0.0.17", "gmft>=0.3"]
web = ["trafilatura>=2.0", "beautifulsoup4>=4.12", "lxml>=5.0"]
dev = [
    "mypy>=1.0",
    "ruff>=0.1",
]
```

The `[web]` extra is independent of `[extract]`/`[extract-full]`. Users install what they need:
- `pip install agentic-mbse` — base (validation, SysML, PDF via pymupdf4llm)
- `pip install agentic-mbse[web]` — adds URL extraction
- `pip install agentic-mbse[extract-full,web]` — everything

### 6. Testing Strategy

**`tests/test_html_sanitize.py`** — Unit tests for `strip_hidden_content()`:

| Test | What it covers | FR |
|------|---------------|-----|
| `test_strip_script_tags` | `<script>` removal | FR-6.1 |
| `test_strip_style_tags` | `<style>` removal | FR-6.1 |
| `test_strip_noscript_iframe_embed_object` | Remaining dangerous tags | FR-6.1 |
| `test_strip_display_none` | `display:none` CSS hiding | FR-6.2 |
| `test_strip_visibility_hidden` | `visibility:hidden` CSS hiding | FR-6.2 |
| `test_strip_opacity_zero` | `opacity:0` (not `0.5`) | FR-6.2 |
| `test_strip_font_size_zero` | `font-size:0px` and variants | FR-6.2 |
| `test_strip_offscreen_positioned` | `position:absolute; left:-9999px` | FR-6.3 |
| `test_preserve_normal_absolute` | `position:absolute` without offscreen (no false positive) | FR-6.3 |
| `test_strip_hidden_attribute` | `<div hidden>` | FR-6.4 |
| `test_strip_aria_hidden` | `aria-hidden="true"` | FR-6.4 |
| `test_strip_zero_width_chars` | All 7 zero-width Unicode chars | FR-6.5 |
| `test_preserve_visible_content` | Normal HTML passes through unchanged | — |
| `test_combined_injection_scenario` | Realistic hidden prompt injection | — |

No network access, no external dependencies beyond bs4. Follows the pattern in `test_pandoc_convert.py` — pure function tests with inline HTML strings.

**`tests/test_web_backend.py`** — Integration tests with mocked HTTP:

| Test | What it covers | FR |
|------|---------------|-----|
| `test_classify_url_html` | HEAD returns text/html → "html" | FR-2 |
| `test_classify_url_pdf` | HEAD returns application/pdf → "pdf" | FR-2 |
| `test_classify_url_head_fails` | HEAD failure → defaults to "html" | FR-2 |
| `test_extract_produces_markdown_with_frontmatter` | Full pipeline: mock fetch → sanitize → extract → verify .md + metrics.json | FR-8, FR-9 |
| `test_frontmatter_fields` | YAML frontmatter has all required fields | FR-9 |
| `test_extraction_result_type` | Returns ExtractionResult, not custom type | FR-14 |
| `test_backend_used_field` | `backend_used` is "trafilatura" | FR-14 |
| `test_pandoc_fallback_on_empty` | Short trafilatura output triggers pandoc | FR-11 |
| `test_sanitization_applied` | Hidden content stripped when sanitize=True | FR-4 |
| `test_no_sanitize_flag` | Hidden content preserved when sanitize=False | FR-4 |
| `test_fetch_failure_returns_error` | Network error → ExtractionResult with error | — |
| `test_check_web_deps_missing` | ImportError with actionable message | FR-15 |

Tests use `@patch` on `agentic_mbse.extraction.http.fetch_url` to return canned HTML. Trafilatura is called on the canned HTML (not mocked) to verify end-to-end extraction.

**`tests/fixtures/`** — HTML fixtures:
- `sample_article.html` — minimal article HTML (title, heading, paragraph, table) for extraction tests
- `hidden_injection.html` — article HTML with hidden content in all 6 categories (script, CSS-hidden, aria-hidden, zero-width chars)

**Existing tests** — no changes needed. `test_pandoc_convert.py` continues to pass since `pandoc_convert.py` behavior doesn't change. New `MockArgs` defaults are additive and backward-compatible.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| trafilatura extraction quality on non-article pages (homepages, wikis) | Low-quality or empty markdown output | Pandoc fallback (FR-11); users can use `--no-sanitize` for debugging |
| BeautifulSoup `opacity:0` regex matches legitimate CSS (e.g., animation start states) | Strips visible content | Regex is anchored (`0(?:[;\s"]|$)`) to avoid `0.5`, `0.8`. Risk is minimal for article extraction |
| `head_content_type()` returns wrong type or `None` for servers that don't support HEAD | Wrong dispatch (PDF treated as HTML or vice versa) | Default to "html" on HEAD failure — trafilatura handles non-HTML gracefully, and the user sees an "empty content" error rather than a crash |
| Dependency weight of trafilatura (~15 transitive deps) | Slower install, potential conflicts | Optional `[web]` extra — users who don't need it don't pay the cost |
| pandoc_convert.py refactoring breaks arXiv shortcut | Regression in existing PDF extraction | Conservative refactoring: only replace User-Agent constant and urllib boilerplate. Run existing `test_pandoc_convert.py` suite. External behavior unchanged (NFR-2) |

---

## Integration Strategy

This feature adds a new extraction path alongside existing PDF and DOCX paths. It does not modify any existing extraction backend or pipeline logic.

**How it fits into workflows:**
- Research agents (`/research` command) can call `uv run agentic-mbse extract <url>` via Bash tool to capture full source content, replacing lossy WebFetch for substantive sources
- `/manage-sources` can call `extract <url>` to populate `knowledge/sources/` with rich markdown (future enhancement, not in this scope)
- Batch processing via `--urls-from` enables automated source enrichment scripts

**What it complements:**
- PDF extraction pipeline (handles document content)
- arXiv shortcut (handles academic papers with LaTeXML HTML)
- WebFetch (still useful for quick checks before committing to full extraction)

---

## Validation Approach

### Automated Testing

1. `uv run pytest tests/test_html_sanitize.py` — sanitization unit tests (no network)
2. `uv run pytest tests/test_web_backend.py` — web backend tests with mocked HTTP (no network)
3. `uv run pytest tests/test_pandoc_convert.py` — existing tests still pass after http.py refactoring
4. `uv run pytest tests/` — full suite, verify no regressions

### Manual Verification

1. `uv run agentic-mbse extract https://en.wikipedia.org/wiki/Fusion_energy` — produces readable markdown with frontmatter
2. `uv run agentic-mbse extract https://arxiv.org/pdf/2411.06644` — downloads PDF and extracts via pipeline
3. Create `test_urls.txt` with 3 URLs, run `uv run agentic-mbse extract --urls-from test_urls.txt`
4. Uninstall trafilatura, verify `extract <url>` gives clear dependency error

### Acceptance Criteria Traceability

All 14 acceptance criteria from the spec are covered by either automated tests or manual verification steps above. Key mapping:

| Acceptance Criterion | Covered By |
|---------------------|------------|
| Wikipedia produces markdown with frontmatter | Manual #1 |
| PDF URL routes to PDF pipeline | `test_classify_url_pdf` + Manual #2 |
| `--urls-from` batch mode | `_extract_urls_from_file` tests + Manual #3 |
| Hidden span stripped | `test_combined_injection_scenario` |
| Output has markdown + metrics.json | `test_extract_produces_markdown_with_frontmatter` |
| Missing deps → clear error | `test_check_web_deps_missing` + Manual #4 |
| No new result types | `test_extraction_result_type` |
| Shared HTTP constants | Code review (http.py imported by both modules) |
| html_sanitize importable without trafilatura | `test_html_sanitize.py` has no trafilatura import |
| Optional dependency | pyproject.toml `[web]` extra |

---

**Next Step:** After approval → `/_my_plan` (MEDIUM complexity, 3 new files + 2 modifications = benefits from phased implementation)
