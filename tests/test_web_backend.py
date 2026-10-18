"""Tests for agentic_mbse.extraction.web_backend — web content extraction pipeline."""

import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.http import FetchResult
from agentic_mbse.extraction.web_backend import (
    check_web_deps,
    classify_url,
    extract_web_content,
)
from tests.helpers.arxiv_page import assert_all_images_saved, serve_figure

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


def test_metrics_json_records_zero_images_for_non_arxiv_pages(tmp_path):
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=_make_fetch_result()):
        extract_web_content("https://example.com/article", output_dir=tmp_path)
    assert json.loads((tmp_path / "metrics.json").read_text())["image_count"] == 0


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
        # The 1 KB version fixture has no article element; conversion is not the subject.
        patch("agentic_mbse.extraction.web_backend.extract_article", side_effect=lambda h: h),
        patch(
            "agentic_mbse.extraction.web_backend.convert_article",
            return_value="A" * 200,  # non-empty, no image refs (skips downloads)
        ),
    ):
        result = extract_web_content("https://arxiv.org/html/1706.03762v1", output_dir=tmp_path)

    assert result.success
    assert result.backend_used == "pandoc-arxiv"
    md_text = (tmp_path / "output.md").read_text()
    assert 'source: "https://arxiv.org/html/1706.03762v7"' in md_text


# ---------------------------------------------------------------------------
# arXiv Pandoc fallback warnings
# ---------------------------------------------------------------------------

_ARXIV_PAGE = FIXTURES / "arxiv_2610.14224v1_page.html"
_ARXIV_URL = "https://arxiv.org/html/2610.14224v1"


@pytest.mark.parametrize(
    ("pandoc", "reason"),
    [
        pytest.param(
            {"side_effect": FileNotFoundError("pandoc")}, "Pandoc not found", id="missing"
        ),
        pytest.param(
            {"return_value": MagicMock(returncode=0, stdout="tiny\n", stderr="")},
            "too short",
            id="short-output",
        ),
        pytest.param(
            {"return_value": MagicMock(returncode=1, stdout="", stderr="parse error")},
            "parse error",
            id="pandoc-error",
        ),
    ],
)
def test_arxiv_pandoc_failure_warns_and_keeps_trafilatura_backend(tmp_path, pandoc, reason):
    """Failed arXiv conversion → trafilatura output, honest backend, warning in result and metrics."""
    fetched = _make_fetch_result(html_path=_ARXIV_PAGE, url=_ARXIV_URL)

    with (
        patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=fetched),
        patch("subprocess.run", **pandoc),
    ):
        result = extract_web_content(_ARXIV_URL, output_dir=tmp_path)

    assert result.success
    assert result.backend_used == "trafilatura"
    assert len(result.warnings) == 1
    assert reason in result.warnings[0]
    assert "used trafilatura instead" in result.warnings[0]
    metrics = json.loads((tmp_path / "metrics.json").read_text())
    assert metrics["warnings"] == result.warnings


def test_non_arxiv_url_has_no_arxiv_warning(tmp_path):
    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=_make_fetch_result()):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)

    assert result.success
    assert result.warnings == []
    assert "warnings" not in json.loads((tmp_path / "metrics.json").read_text())


# ---------------------------------------------------------------------------
# arXiv paper-only conversion (design D4, D16; invariants 1 and 11)
# ---------------------------------------------------------------------------

# Chrome on the real page that must not reach the output, and paper parts that must.
_CHROME_TEXT = ["Report Issue", "Instructions for reporting errors", "major funders", "09 Oct 2026"]
_FOOTER_LOGO = "iVBORw0KGgoAAAANSUhEUgAAAAsAAAAO"
_PAPER_TEXT = [
    "## 1 Introduction",
    "## References",
    "## Appendix B Benchmarks",
    "Figure 1:",  # caption
    "w/o library",  # Table 3
    "$k = 5$",  # math
]


def _serve(html: str | None = None, url: str = _ARXIV_URL):
    fetched = (
        _make_fetch_result(html_path=_ARXIV_PAGE, url=url)
        if html is None
        else _make_fetch_result(html=html, url=url)
    )
    return patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=fetched)


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs Pandoc")
def test_arxiv_web_route_outputs_paper_only_with_all_figures_saved(tmp_path):
    """Real page, real sanitizer, real Pandoc: paper only, and all nine figures on disk."""
    with (
        _serve(),
        patch("agentic_mbse.extraction.web_backend.fetch_image", side_effect=serve_figure),
    ):
        result = extract_web_content(_ARXIV_URL, output_dir=tmp_path)

    assert result.success
    assert result.backend_used == "pandoc-arxiv"
    assert result.warnings == []
    output = (tmp_path / "output.md").read_text()
    for s in _CHROME_TEXT + [_FOOTER_LOGO]:
        assert s not in output, f"chrome {s!r} in output"
    for s in _PAPER_TEXT:
        assert s in output, f"paper part {s!r} missing"
    assert_all_images_saved(output, tmp_path / "images", result.image_count)
    assert json.loads((tmp_path / "metrics.json").read_text())["image_count"] == result.image_count


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs Pandoc")
def test_arxiv_web_route_failed_figure_warns_and_keeps_ref(tmp_path):
    def all_but_one(url: str) -> bytes:
        if url.endswith("total_cost.svg"):
            raise OSError("HTTP Error 503")
        return serve_figure(url)

    with (
        _serve(),
        patch("agentic_mbse.extraction.web_backend.fetch_image", side_effect=all_but_one),
    ):
        result = extract_web_content(_ARXIV_URL, output_dir=tmp_path)

    output = (tmp_path / "output.md").read_text()
    files = {p.name for p in (tmp_path / "images").iterdir()}
    assert result.image_count == len(files)
    assert "total_cost.svg" not in files and len(files) == 8 + 3  # 8 figures, 3 inline images
    assert "](2610.14224v1/total_cost.svg)" in output
    [warning] = result.warnings
    assert "total_cost.svg" in warning and "503" in warning
    assert json.loads((tmp_path / "metrics.json").read_text())["warnings"] == [warning]


def test_unrecognized_container_falls_back_to_trafilatura_with_warning(tmp_path):
    page = _ARXIV_PAGE.read_text().replace("<article ", "<div ").replace("</article>", "</div>")

    with _serve(page), patch("subprocess.run") as pandoc:
        result = extract_web_content(_ARXIV_URL, output_dir=tmp_path)

    pandoc.assert_not_called()
    assert result.success
    assert result.backend_used == "trafilatura"
    [warning] = result.warnings
    assert "no recognized arXiv article container" in warning
    assert json.loads((tmp_path / "metrics.json").read_text())["warnings"] == [warning]


def test_arxiv_url_short_trafilatura_never_calls_whole_page_pandoc(tmp_path):
    """D16: after a failed article conversion the whole arXiv page never goes to Pandoc."""
    page = "<html><body><p>Too short.</p></body></html>"

    with (
        _serve(page),
        patch("agentic_mbse.extraction.web_backend._fallback_pandoc") as whole_page,
    ):
        result = extract_web_content(_ARXIV_URL, output_dir=tmp_path)

    whole_page.assert_not_called()
    assert result.backend_used == "trafilatura"
    assert any("no recognized arXiv article container" in w for w in result.warnings)


def test_non_arxiv_short_trafilatura_still_uses_whole_page_pandoc(tmp_path):
    page = "<html><body><p>Too short.</p></body></html>"

    with (
        _serve(page, url="https://example.com/article"),
        patch(
            "agentic_mbse.extraction.web_backend._fallback_pandoc", return_value="P" * 200
        ) as whole_page,
    ):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)

    whole_page.assert_called_once()
    assert result.backend_used == "pandoc-fallback"


def test_arxiv_raw_bytes_and_hash_are_the_fetched_page(tmp_path):
    """Invariant 1: provenance hashes and saves the fetched bytes, not the article slice."""
    raw = _ARXIV_PAGE.read_bytes()
    with (
        _serve(),
        patch(
            "agentic_mbse.extraction.web_backend.convert_article",
            return_value="# Paper\n\n" + "text " * 40,
        ),
    ):
        extract_web_content(_ARXIV_URL, output_dir=tmp_path, save_source=True)

    assert (tmp_path / "raw.html").read_bytes() == raw
    assert hashlib.sha256(raw).hexdigest() in (tmp_path / "output.md").read_text()


def test_arxiv_images_resolve_against_normalized_serving_url(tmp_path):
    """B5: a trailing-slash serving URL is normalized before figure refs resolve."""
    with (
        _serve(url="https://arxiv.org/html/2610.14224v1/"),
        patch(
            "agentic_mbse.extraction.web_backend.convert_article",
            return_value="# Paper\n\n![f](2610.14224v1/components.png)\n\n" + "text " * 40,
        ),
        patch(
            "agentic_mbse.extraction.web_backend.fetch_image", side_effect=serve_figure
        ) as fetch,
    ):
        result = extract_web_content("https://arxiv.org/html/2610.14224v1", output_dir=tmp_path)

    fetch.assert_called_once_with("https://arxiv.org/html/2610.14224v1/components.png")
    assert result.image_count == 1
    assert "![f](images/components.png)" in (tmp_path / "output.md").read_text()
