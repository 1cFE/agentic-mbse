"""arXiv detection and Pandoc conversion for PDF extraction pipeline.

Detects arXiv papers from PDF metadata, checks HTML availability, and
converts arXiv HTML to markdown via Pandoc with pre/post-processing.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from agentic_mbse.extraction.http import USER_AGENT

# ---------------------------------------------------------------------------
# Pandoc availability
# ---------------------------------------------------------------------------


def _pandoc_available(pandoc_path: str = "pandoc") -> bool:
    """Check if Pandoc is available on the system PATH."""
    return shutil.which(pandoc_path) is not None


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
# arXiv detection
# ---------------------------------------------------------------------------


def detect_arxiv_id(pdf_path: Path) -> str | None:
    """Extract arXiv ID from PDF page 1 text.

    Sequence:
    1. pymupdf page 1 text extraction
    2. Regex: ``arXiv:\\d{4}\\.\\d{4,5}(v\\d+)?``
    3. Fallback: check PDF Creator metadata for 'arXiv'
    """
    import pymupdf  # type: ignore[import-untyped]

    doc = pymupdf.open(str(pdf_path))
    try:
        if len(doc) == 0:
            return None

        page_text = doc[0].get_text()

        # Primary: regex on page 1 text
        m = re.search(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", page_text)
        if m:
            return m.group(1)

        # Fallback: PDF Creator metadata
        metadata = doc.metadata or {}
        creator = metadata.get("creator", "")
        if "arxiv" in creator.lower():
            for i in range(min(2, len(doc))):
                text = doc[i].get_text()
                m = re.search(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", text)
                if m:
                    return m.group(1)

        return None
    finally:
        doc.close()


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
    """Convert arXiv HTML to markdown via Pandoc.

    Args:
        html_source: URL (``https://...``) or local file path.
        pandoc_path: Path to pandoc binary.

    Returns:
        ``(markdown, raw_html_bytes)`` — raw bytes before preprocessing.

    Raises:
        ``subprocess.CalledProcessError`` on Pandoc failure.
        ``FileNotFoundError`` if Pandoc is not installed.
    """
    if not _pandoc_available(pandoc_path):
        raise FileNotFoundError(
            f"Pandoc not found at '{pandoc_path}'. Install with: "
            "apt install pandoc (or brew install pandoc)"
        )

    html_source_str = str(html_source)

    # Download URL to temp file if needed
    if html_source_str.startswith(("http://", "https://")):
        req = urllib.request.Request(html_source_str)
        req.add_header("User-Agent", USER_AGENT)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_bytes = resp.read()
            raw_html = raw_bytes.decode("utf-8")
    else:
        p = Path(html_source_str)
        raw_bytes = p.read_bytes()
        raw_html = raw_bytes.decode("utf-8")

    # Pre-process
    processed_html = _preprocess_html(raw_html)

    # Write to temp file for Pandoc
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(processed_html)
        tmp_path = Path(f.name)

    try:
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

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

        markdown = result.stdout
    finally:
        tmp_path.unlink(missing_ok=True)

    # Post-process
    return _postprocess_markdown(markdown), raw_bytes
