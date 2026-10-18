"""Tests for pandoc_convert module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.arxiv_html import MIN_CONTENT_CHARS, ArxivConversionError
from agentic_mbse.extraction.http import FetchResult
from agentic_mbse.extraction.pandoc_convert import (
    _pandoc_available,
    check_arxiv_html,
    convert_arxiv_html,
    resolve_fetched_version,
    strip_arxiv_version,
)

FIXTURES = Path(__file__).parent / "fixtures"

# Pandoc output shorter than MIN_CONTENT_CHARS counts as a failed conversion.
_PADDING = "x" * MIN_CONTENT_CHARS


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


def _article_page(body: str) -> str:
    """An arXiv-shaped page: chrome around one LaTeXML article."""
    return (
        "<html><body><nav>Site navigation</nav>"
        f'<article class="ltx_document">{body}</article>'
        "<footer>Site footer</footer></body></html>"
    )


def _pandoc_seeing(stdout: str, seen: list[str]):
    """A subprocess.run stand-in that records the HTML handed to Pandoc."""

    def run(cmd, **kwargs):
        seen.append(Path(cmd[1]).read_text(encoding="utf-8"))
        return MagicMock(returncode=0, stdout=stdout, stderr="")

    return run


@patch("agentic_mbse.extraction.pandoc_convert._pandoc_available", return_value=True)
class TestConvertArxivHtml:
    def test_local_file_converts_only_the_article(self, _available, tmp_path):
        page = _article_page("<h1>Heading</h1><p>Content</p>")
        html_file = tmp_path / "test.html"
        html_file.write_text(page, encoding="utf-8")
        seen: list[str] = []

        with patch(
            "subprocess.run",
            side_effect=_pandoc_seeing("# Heading\n\nConverted\n" + _PADDING, seen),
        ):
            markdown, raw_bytes = convert_arxiv_html(html_file)

        assert markdown.startswith("# Heading\n\nConverted")
        assert raw_bytes == page.encode("utf-8")  # raw bytes, chrome included
        [sent] = seen
        assert "<h1>Heading</h1>" in sent
        assert "Site navigation" not in sent and "Site footer" not in sent

    def test_url_is_fetched_through_fetch_url(self, _available):
        page = _article_page("<p>Content</p>").encode("utf-8")
        fetched = FetchResult(
            content=page, final_url="https://arxiv.org/html/2610.14224v1", content_type="text/html"
        )
        with (
            patch("agentic_mbse.extraction.arxiv_html.fetch_url", return_value=fetched) as fetch,
            patch(
                "subprocess.run", return_value=MagicMock(returncode=0, stdout=_PADDING, stderr="")
            ),
        ):
            markdown, raw_bytes = convert_arxiv_html("https://arxiv.org/html/2610.14224")

        fetch.assert_called_once()
        assert fetch.call_args.args == ("https://arxiv.org/html/2610.14224",)
        assert markdown == _PADDING
        assert raw_bytes == page

    def test_preprocessing_applied(self, _available, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text(_article_page('<figure class="ltx"><img src="x"></figure><p>Text</p>'))
        seen: list[str] = []

        with patch("subprocess.run", side_effect=_pandoc_seeing("Clean output\n" + _PADDING, seen)):
            convert_arxiv_html(html_file)

        assert "<figure" not in seen[0] and '<img src="x">' in seen[0]

    def test_postprocessing_applied(self, _available, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text(_article_page("<p>content</p>"))
        stdout = "Text\\hspace{0pt}more `<!-- -->`{=html}end\n" + _PADDING

        with patch(
            "subprocess.run", return_value=MagicMock(returncode=0, stdout=stdout, stderr="")
        ):
            markdown, _raw_bytes = convert_arxiv_html(html_file)

        assert "\\hspace{0pt}" not in markdown
        assert "`<!-- -->`{=html}" not in markdown

    def test_short_output_raises(self, _available, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text(_article_page("<p>content</p>"))

        with (
            patch(
                "subprocess.run", return_value=MagicMock(returncode=0, stdout="Tiny\n", stderr="")
            ),
            pytest.raises(ArxivConversionError, match="too short"),
        ):
            convert_arxiv_html(html_file)

    def test_page_without_article_raises_before_pandoc(self, _available, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body><p>whole page, no article</p></body></html>")

        with (
            patch("subprocess.run") as run,
            pytest.raises(ArxivConversionError, match="no recognized arXiv article"),
        ):
            convert_arxiv_html(html_file)
        run.assert_not_called()

    def test_pandoc_not_available(self, mock_available, tmp_path):
        mock_available.return_value = False

        html_file = tmp_path / "test.html"
        html_file.write_text(_article_page("<p>content</p>"))

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
