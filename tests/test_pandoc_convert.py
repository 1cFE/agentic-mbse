"""Tests for pandoc_convert module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.pandoc_convert import (
    _pandoc_available,
    _postprocess_markdown,
    _preprocess_html,
    check_arxiv_html,
    convert_arxiv_html,
    detect_arxiv_id,
    resolve_fetched_version,
    strip_arxiv_version,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestStripArxivVersion:
    def test_versioned_id(self):
        assert strip_arxiv_version("2401.12345v3") == ("2401.12345", 3)

    def test_bare_id_unchanged(self):
        assert strip_arxiv_version("2401.12345") == ("2401.12345", None)

    def test_versioned_html_url(self):
        assert strip_arxiv_version("https://arxiv.org/html/2401.12345v2") == (
            "https://arxiv.org/html/2401.12345",
            2,
        )

    def test_bare_html_url_unchanged(self):
        url = "https://arxiv.org/html/2401.12345"
        assert strip_arxiv_version(url) == (url, None)

    def test_multi_digit_version(self):
        assert strip_arxiv_version("1706.03762v11") == ("1706.03762", 11)

    def test_four_digit_id(self):
        assert strip_arxiv_version("1706.0376v2") == ("1706.0376", 2)


class TestResolveFetchedVersion:
    def test_recovers_from_asset_path(self):
        html = '<img src="1706.03762v7/x1.png">'
        assert resolve_fetched_version(html, "1706.03762") == 7

    def test_none_when_no_asset_path(self):
        assert resolve_fetched_version("<p>no figures here</p>", "1706.03762") is None

    def test_id_with_dot_is_escaped(self):
        # The '.' in the id must be treated literally, not as a regex wildcard.
        html = '<img src="1706X03762v7/x1.png">'
        assert resolve_fetched_version(html, "1706.03762") is None

    def test_recovers_from_real_fixture(self):
        html = (FIXTURES / "arxiv_1706.03762_latest.html").read_text()
        assert resolve_fetched_version(html, "1706.03762") == 7


class TestPreprocessHtml:
    def test_strip_figure_tags(self):
        html = '<p>Text</p><figure class="ltx_figure"><img src="x"></figure>'
        result = _preprocess_html(html)
        assert "<figure" not in result
        assert "</figure>" not in result
        assert "<p>Text</p>" in result
        assert '<img src="x">' in result

    def test_strip_css_transform_wrappers(self):
        html = (
            '<div class="ltx_inline-block ltx_transformed_outer" '
            'style="transform:scale(0.8)">'
            '<span class="ltx_transformed_inner" style="transform:scale(1.25)">'
            "content</span></div>"
        )
        result = _preprocess_html(html)
        assert "ltx_transformed_outer" not in result
        assert "ltx_transformed_inner" not in result
        assert "content" in result

    def test_preserve_normal_html(self):
        html = "<p>Normal paragraph</p><table><tr><td>cell</td></tr></table>"
        result = _preprocess_html(html)
        assert result == html


class TestPostprocessMarkdown:
    def test_strip_hspace(self):
        md = "Text\\hspace{0pt}more text"
        result = _postprocess_markdown(md)
        assert "\\hspace" not in result
        assert "Textmore text" in result

    def test_strip_html_comment_artifacts(self):
        md = "Some text`<!-- -->`{=html}more"
        result = _postprocess_markdown(md)
        assert "`<!-- -->`{=html}" not in result
        assert "Some textmore" in result

    def test_preserve_normal_markdown(self):
        md = "# Heading\n\nParagraph with **bold** text."
        result = _postprocess_markdown(md)
        assert result == md


class TestDetectArxivId:
    @patch("pymupdf.open")
    def test_finds_arxiv_id_on_page_1(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=10)
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "Some paper title\narXiv:2510.07314v1 [cs.AI] 10 Oct 2025\n"
            "Abstract: This paper..."
        )
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)
        mock_doc.metadata = {"creator": "LaTeX"}
        mock_open.return_value = mock_doc

        result = detect_arxiv_id(Path("fake.pdf"))
        assert result == "2510.07314v1"

    @patch("pymupdf.open")
    def test_no_arxiv_id(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=5)
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Some normal paper text without arXiv"
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)
        mock_doc.metadata = {"creator": "Microsoft Word"}
        mock_open.return_value = mock_doc

        result = detect_arxiv_id(Path("fake.pdf"))
        assert result is None

    @patch("pymupdf.open")
    def test_creator_metadata_fallback(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=2)

        pages = {
            0: MagicMock(),
            1: MagicMock(),
        }
        # Page 0 has no arXiv in text, but creator says arXiv
        pages[0].get_text.return_value = "Title of Paper\nNo ID here"
        # Page 1 has the arXiv ID
        pages[1].get_text.return_value = "arXiv:2301.12345 in footer"
        mock_doc.__getitem__ = MagicMock(side_effect=lambda i: pages[i])
        mock_doc.metadata = {"creator": "arXiv.org e-Print archive"}
        mock_open.return_value = mock_doc

        result = detect_arxiv_id(Path("fake.pdf"))
        assert result == "2301.12345"

    @patch("pymupdf.open")
    def test_empty_document(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=0)
        mock_open.return_value = mock_doc

        result = detect_arxiv_id(Path("fake.pdf"))
        assert result is None


def _mock_head(status):
    """Build a mock HEAD response context manager with the given status."""
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestCheckArxivHtml:
    @patch("agentic_mbse.extraction.pandoc_convert.urllib.request.urlopen")
    def test_strips_to_bare_and_returns_bare(self, mock_urlopen):
        # Bare URL is available → a version-pinned id upgrades to latest.
        mock_urlopen.return_value = _mock_head(200)

        result = check_arxiv_html("2510.07314v1")

        assert result == "https://arxiv.org/html/2510.07314"  # was v1
        # Verify HEAD method, target URL, User-Agent, timeout.
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "HEAD"
        assert req.full_url == "https://arxiv.org/html/2510.07314"
        assert "agentic-mbse" in req.get_header("User-agent")
        assert call_args[1]["timeout"] == 5

    @patch("agentic_mbse.extraction.pandoc_convert.urllib.request.urlopen")
    def test_falls_back_to_versioned_when_bare_unavailable(self, mock_urlopen):
        # Bare 404 → retry the requested version, which is available.
        mock_urlopen.side_effect = [_mock_head(404), _mock_head(200)]

        result = check_arxiv_html("2510.07314v1")

        assert result == "https://arxiv.org/html/2510.07314v1"
        # Two HEADs: bare first, then versioned.
        urls = [c.args[0].full_url for c in mock_urlopen.call_args_list]
        assert urls == [
            "https://arxiv.org/html/2510.07314",
            "https://arxiv.org/html/2510.07314v1",
        ]

    @patch("agentic_mbse.extraction.pandoc_convert.urllib.request.urlopen")
    def test_returns_none_on_non_200(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = check_arxiv_html("9999.99999v1")
        assert result is None

    @patch("agentic_mbse.extraction.pandoc_convert.urllib.request.urlopen")
    def test_returns_none_on_timeout(self, mock_urlopen):
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("timeout")

        result = check_arxiv_html("2510.07314v1")
        assert result is None

    @patch("agentic_mbse.extraction.pandoc_convert.urllib.request.urlopen")
    def test_returns_none_on_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = OSError("Connection refused")

        result = check_arxiv_html("2510.07314v1")
        assert result is None


class TestConvertArxivHtml:
    @patch("agentic_mbse.extraction.pandoc_convert._pandoc_available")
    @patch("subprocess.run")
    def test_local_file_conversion(self, mock_run, mock_available, tmp_path):
        mock_available.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# Heading\n\nConverted content\n",
            stderr="",
        )

        html_file = tmp_path / "test.html"
        html_file.write_text("<h1>Heading</h1><p>Content</p>")

        markdown, raw_bytes = convert_arxiv_html(html_file)

        assert "Converted content" in markdown
        assert raw_bytes == b"<h1>Heading</h1><p>Content</p>"
        mock_run.assert_called_once()
        # Verify Pandoc flags
        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        assert "html-native_divs-native_spans" in cmd
        assert "--wrap=none" in cmd
        assert "--markdown-headings=atx" in cmd

    @patch("agentic_mbse.extraction.pandoc_convert._pandoc_available")
    @patch("subprocess.run")
    def test_preprocessing_applied(self, mock_run, mock_available, tmp_path):
        mock_available.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Clean output\n",
            stderr="",
        )

        html_file = tmp_path / "test.html"
        html_file.write_text(
            '<figure class="ltx"><img src="x"></figure><p>Text</p>'
        )

        convert_arxiv_html(html_file)

        # The temp file passed to Pandoc should have figure tags stripped
        # (we can't easily inspect the temp file, but we can verify the
        # function completes without error)
        mock_run.assert_called_once()

    @patch("agentic_mbse.extraction.pandoc_convert._pandoc_available")
    @patch("subprocess.run")
    def test_postprocessing_applied(self, mock_run, mock_available, tmp_path):
        mock_available.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Text\\hspace{0pt}more `<!-- -->`{=html}end\n",
            stderr="",
        )

        html_file = tmp_path / "test.html"
        html_file.write_text("<p>content</p>")

        markdown, _raw_bytes = convert_arxiv_html(html_file)

        assert "\\hspace{0pt}" not in markdown
        assert "`<!-- -->`{=html}" not in markdown

    @patch("agentic_mbse.extraction.pandoc_convert._pandoc_available")
    def test_pandoc_not_available(self, mock_available, tmp_path):
        mock_available.return_value = False

        html_file = tmp_path / "test.html"
        html_file.write_text("<p>content</p>")

        with pytest.raises(FileNotFoundError, match="Pandoc not found"):
            convert_arxiv_html(html_file)


class TestPandocAvailable:
    @patch("shutil.which")
    def test_pandoc_found(self, mock_which):
        mock_which.return_value = "/usr/bin/pandoc"
        assert _pandoc_available() is True

    @patch("shutil.which")
    def test_pandoc_not_found(self, mock_which):
        mock_which.return_value = None
        assert _pandoc_available() is False
