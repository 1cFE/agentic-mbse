"""Tests for agentic_mbse.extraction.web_backend — web content extraction pipeline."""

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.http import FetchResult
from agentic_mbse.extraction.web_backend import (
    check_web_deps,
    classify_url,
    extract_web_content,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_fetch_result(
    html_path: Path | None = None, html: str | None = None, url: str = "https://example.com/article"
) -> FetchResult:
    """Build a FetchResult from a fixture file or raw HTML."""
    if html is None:
        html = (html_path or FIXTURES / "sample_article.html").read_text()
    return FetchResult(
        content=html.encode("utf-8"),
        final_url=url,
        content_type="text/html",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# classify_url
# ---------------------------------------------------------------------------


def test_classify_url_html():
    with patch("agentic_mbse.extraction.web_backend.head_content_type", return_value="text/html"):
        assert classify_url("https://example.com") == "html"


def test_classify_url_xhtml():
    with patch(
        "agentic_mbse.extraction.web_backend.head_content_type",
        return_value="application/xhtml+xml",
    ):
        assert classify_url("https://example.com") == "html"


def test_classify_url_pdf():
    with patch(
        "agentic_mbse.extraction.web_backend.head_content_type", return_value="application/pdf"
    ):
        assert classify_url("https://example.com/file.pdf") == "pdf"


def test_classify_url_head_fails():
    with patch("agentic_mbse.extraction.web_backend.head_content_type", return_value=None):
        assert classify_url("https://example.com") == "html"


def test_classify_url_unknown_type():
    with patch("agentic_mbse.extraction.web_backend.head_content_type", return_value="image/png"):
        assert classify_url("https://example.com/img.png") == "image/png"


# ---------------------------------------------------------------------------
# Frontmatter (via shared module — unit tests in test_frontmatter.py)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# extract_web_content
# ---------------------------------------------------------------------------


def test_extract_produces_markdown_with_frontmatter(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    assert isinstance(result, ExtractionResult)
    # Find the markdown file
    md_files = list(tmp_path.glob("*.md"))
    assert len(md_files) == 1
    content = md_files[0].read_text()
    assert content.startswith("---")
    assert "source:" in content


def test_frontmatter_uses_new_field_names(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    md_files = list(tmp_path.glob("*.md"))
    content = md_files[0].read_text()
    # New field names
    assert "source:" in content
    assert "extracted_at:" in content
    assert "content_hash_sha256:" in content
    assert "backend:" in content
    # Title should be extracted by trafilatura from the fixture
    assert "title:" in content
    # Old field names must NOT appear
    assert "source_url:" not in content
    assert "access_date:" not in content
    assert "extraction_tool:" not in content


def test_extraction_result_type(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert isinstance(result, ExtractionResult)


def test_backend_used_field(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    assert result.backend_used in ("trafilatura", "pandoc-fallback")


def test_metrics_json_written(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    assert (tmp_path / "metrics.json").exists()


def test_sanitization_applied(tmp_path):
    """Hidden content is stripped when sanitize=True (default)."""
    mock_fetch = _make_fetch_result(html_path=FIXTURES / "hidden_injection.html")
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content(
            "https://example.com/article", output_dir=tmp_path, sanitize=True
        )
    assert result.success
    md_files = list(tmp_path.glob("*.md"))
    content = md_files[0].read_text()
    assert "INJECTION_DISPLAY_NONE" not in content
    assert "INJECTION_SCRIPT" not in content
    assert "Legitimate Article Title" in content or "real article content" in content


def test_no_sanitize_flag(tmp_path):
    """strip_hidden_content is NOT called when sanitize=False.

    We verify by confirming the sanitization module is never imported
    during the call (the import is inside the `if sanitize:` block).
    """
    import agentic_mbse.extraction.html_sanitize as san_mod

    original_fn = san_mod.strip_hidden_content
    call_count = 0

    def tracking_wrapper(html):
        nonlocal call_count
        call_count += 1
        return original_fn(html)

    san_mod.strip_hidden_content = tracking_wrapper
    try:
        html = "<html><body><p>Visible</p><span style='display:none'>HIDDEN</span></body></html>"
        mock_fetch = _make_fetch_result(html=html)
        with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
            extract_web_content(
                "https://example.com/article", output_dir=tmp_path, sanitize=False
            )
        assert call_count == 0, "strip_hidden_content should not be called when sanitize=False"
    finally:
        san_mod.strip_hidden_content = original_fn


def test_save_source_saves_raw_html(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content(
            "https://example.com/article", output_dir=tmp_path, save_source=True
        )
    assert result.success
    assert (tmp_path / "raw.html").exists()


def test_raw_html_not_saved_by_default(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    assert not (tmp_path / "raw.html").exists()


def test_fetch_failure_returns_error(tmp_path):
    with patch(
        "agentic_mbse.extraction.web_backend.fetch_url", side_effect=Exception("connection refused")
    ):
        result = extract_web_content("https://example.com/down", output_dir=tmp_path)
    assert not result.success
    assert result.error is not None
    assert "connection refused" in result.error


def test_char_count_populated(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    assert result.char_count > 0


def test_no_frontmatter_flag(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content(
            "https://example.com/article", output_dir=tmp_path, no_frontmatter=True
        )
    assert result.success
    md_files = list(tmp_path.glob("*.md"))
    content = md_files[0].read_text()
    assert not content.startswith("---")


def test_content_hash_uses_raw_bytes(tmp_path):
    """content_hash_sha256 should hash the raw fetched HTML bytes, not extracted markdown."""
    raw_html = "<html><body><p>Test content for hashing verification.</p></body></html>"
    expected_hash = hashlib.sha256(raw_html.encode("utf-8")).hexdigest()
    mock_fetch = _make_fetch_result(html=raw_html)
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    md_files = list(tmp_path.glob("*.md"))
    content = md_files[0].read_text()
    assert expected_hash in content


# ---------------------------------------------------------------------------
# check_web_deps
# ---------------------------------------------------------------------------


def test_check_web_deps_passes():
    """Should not raise when deps are installed (they are in dev env)."""
    check_web_deps()


def test_check_web_deps_missing_trafilatura():
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "trafilatura":
            raise ImportError("no trafilatura")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ImportError, match="pip install agentic-mbse"):
            check_web_deps()


def test_check_web_deps_missing_bs4():
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "bs4":
            raise ImportError("no bs4")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ImportError, match="pip install agentic-mbse"):
            check_web_deps()


# ---------------------------------------------------------------------------
# arXiv latest-version resolution
# ---------------------------------------------------------------------------


def test_versioned_arxiv_url_normalized_before_fetch(tmp_path):
    """A version-pinned arXiv URL is fetched at its bare (latest) URL."""
    seen = []

    def fake_fetch(u, **kwargs):
        seen.append(u)
        return _make_fetch_result(html="<p>irrelevant</p>", url=u)

    with patch("agentic_mbse.extraction.web_backend.fetch_url", side_effect=fake_fetch):
        extract_web_content("https://arxiv.org/html/2401.00001v1", output_dir=tmp_path)

    assert seen == ["https://arxiv.org/html/2401.00001"]  # stripped, single fetch


def test_non_arxiv_url_untouched(tmp_path):
    """A non-arXiv URL is fetched verbatim — no version stripping."""
    seen = []

    def fake_fetch(u, **kwargs):
        seen.append(u)
        return _make_fetch_result(url=u)

    with patch("agentic_mbse.extraction.web_backend.fetch_url", side_effect=fake_fetch):
        extract_web_content("https://example.com/article/1234.56789v2", output_dir=tmp_path)

    assert seen == ["https://example.com/article/1234.56789v2"]


def test_bare_fetch_failure_falls_back_to_requested(tmp_path):
    """If the bare (latest) fetch fails, retry the exact requested URL (D5)."""
    seen = []

    def fake_fetch(u, **kwargs):
        seen.append(u)
        if u == "https://arxiv.org/html/2401.00001":
            raise OSError("bare unavailable")
        return _make_fetch_result(html="<p>irrelevant</p>", url=u)

    with patch("agentic_mbse.extraction.web_backend.fetch_url", side_effect=fake_fetch):
        result = extract_web_content("https://arxiv.org/html/2401.00001v1", output_dir=tmp_path)

    assert result.success
    assert seen == [
        "https://arxiv.org/html/2401.00001",       # bare first (fails)
        "https://arxiv.org/html/2401.00001v1",     # requested fallback
    ]


def test_arxiv_source_records_fetched_version(tmp_path):
    """Frontmatter source names the version arXiv actually served, not the pinned one."""
    html = (FIXTURES / "arxiv_1706.03762_latest.html").read_text()

    def fake_fetch(u, **kwargs):
        # Bare URL serves latest; final_url comes back bare (arXiv, no redirect).
        return _make_fetch_result(html=html, url=u)

    with (
        patch("agentic_mbse.extraction.web_backend.fetch_url", side_effect=fake_fetch),
        patch(
            "agentic_mbse.extraction.web_backend._extract_with_arxiv_pandoc",
            return_value="A" * 200,  # non-empty, no image refs (skips downloads)
        ),
    ):
        result = extract_web_content(
            "https://arxiv.org/html/1706.03762v1", output_dir=tmp_path
        )

    assert result.success
    assert result.backend_used == "pandoc-arxiv"
    md_text = (tmp_path / "output.md").read_text()
    assert 'source: "https://arxiv.org/html/1706.03762v7"' in md_text
