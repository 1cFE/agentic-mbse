"""Tests for agentic_mbse.extraction.web_backend — web content extraction pipeline."""

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.http import FetchResult
from agentic_mbse.extraction.web_backend import (
    _build_frontmatter,
    _sanitize_yaml_value,
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
# _sanitize_yaml_value
# ---------------------------------------------------------------------------


def test_sanitize_yaml_value_strips_newlines():
    assert "\n" not in _sanitize_yaml_value("line1\nline2\rline3")


def test_sanitize_yaml_value_escapes_quotes():
    assert '"' not in _sanitize_yaml_value('He said "hello"')


def test_sanitize_yaml_value_collapses_whitespace():
    assert "  " not in _sanitize_yaml_value("too   many   spaces")


# ---------------------------------------------------------------------------
# _build_frontmatter
# ---------------------------------------------------------------------------


def test_build_frontmatter_has_required_fields():
    fm = _build_frontmatter(
        source_url="https://example.com",
        content_hash="abc123",
        title="Test Title",
        author="Author",
        tool_version="trafilatura 2.0",
    )
    assert "source_url:" in fm
    assert "access_date:" in fm
    assert "content_hash_sha256:" in fm
    assert "title:" in fm
    assert "author:" in fm
    assert "extraction_tool:" in fm
    assert fm.startswith("---")
    assert fm.endswith("---")


def test_build_frontmatter_omits_none_fields():
    fm = _build_frontmatter(
        source_url="https://example.com",
        content_hash="abc123",
        title=None,
        author=None,
        tool_version="trafilatura 2.0",
    )
    assert "title:" not in fm
    assert "author:" not in fm


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
    assert "source_url:" in content


def test_frontmatter_fields(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert result.success
    md_files = list(tmp_path.glob("*.md"))
    content = md_files[0].read_text()
    assert "source_url:" in content
    assert "access_date:" in content
    assert "content_hash_sha256:" in content
    # Title should be extracted by trafilatura from the fixture
    assert "title:" in content


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


def test_raw_html_saved(tmp_path):
    mock_fetch = _make_fetch_result()
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content(
            "https://example.com/article", output_dir=tmp_path, save_raw_html=True
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
