"""Tests for arxiv_html: paper selection and the shared Pandoc runner."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.arxiv_html import (
    MIN_CONTENT_CHARS,
    ArxivConversionError,
    _postprocess_markdown,
    _preprocess_html,
    _run_pandoc,
    convert_article,
    select_article,
)
from agentic_mbse.extraction.web_backend import _MD_IMAGE_RE

FIXTURE = Path(__file__).parent / "fixtures" / "arxiv_2610.14224v1_page.html"

# Chrome outside the article on the real page: issue dialog, header navigation,
# the page watermark, both footers, a funder logo and the footer's data-URI logo.
CHROME = [
    '<dialog id="modal-form"',
    '<nav class="html-header-nav">',
    '<nav class="ltx_TOC">',
    '<div id="watermark-tr">',
    '<footer class="arxiv-html-footer">',
    '<footer class="ds-site-footer">',
    'alt="Simons Foundation"',
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAO",
]
# Paper parts inside the article.
PAPER = [
    "Recursive Agent Harnessing",
    "ltx_abstract",
    "</span>Introduction</h2>",
    "</span>Analysis</h2>",
    "</span>Benchmarks</h2>",
    "L. A. Agrawal, S. Tan",
    "ltx_Math",
    "ltx_tabular",
    "2610.14224v1/intro_teaser.png",
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB",
]
# Chrome text that must not survive conversion.
CHROME_TEXT = [
    "Report Issue",
    "Simons Foundation",
    "major funders",
    "Instructions for reporting errors",
    "09 Oct 2026",
    "iVBORw0KGgoAAAANSUhEUgAAAAsAAAAO",
]

_SHORT_ARTICLE = '<article class="ltx_document"><p>paper</p></article>'


def _completed(stdout: str = "x" * MIN_CONTENT_CHARS, returncode: int = 0) -> MagicMock:
    return MagicMock(returncode=returncode, stdout=stdout, stderr="boom")


class TestSelectArticle:
    def test_keeps_paper_drops_chrome(self):
        page = FIXTURE.read_text(encoding="utf-8")
        article = select_article(page)

        assert article is not None
        assert article.startswith("<article")
        assert article.endswith("</article>")
        for s in CHROME:
            assert s in page, f"fixture lost chrome marker {s!r}"
            assert s not in article, f"chrome {s!r} inside the article"
        for s in PAPER:
            assert s in article, f"paper part {s!r} missing from the article"

    @pytest.mark.parametrize(
        "html",
        [
            pytest.param("<html><body><p>no article</p></body></html>", id="no-article"),
            pytest.param(_SHORT_ARTICLE + _SHORT_ARTICLE, id="two-articles"),
            pytest.param('<article class="post"><p>x</p></article>', id="no-ltx-class"),
            pytest.param('<article class="ltx_documents"><p>x</p></article>', id="class-prefix"),
            pytest.param("<articles>x</articles>", id="articles-tag"),
            pytest.param('<article class="ltx_document"><p>unclosed</p>', id="unclosed"),
            pytest.param('</article><article class="ltx_document">', id="reversed"),
        ],
    )
    def test_fails_closed(self, html):
        assert select_article(html) is None

    def test_case_insensitive_and_single_quoted_class(self):
        html = "<ARTICLE class='ltx_document x'>p</ARTICLE >"
        assert select_article(html) == html


class TestRunPandoc:
    @patch("subprocess.run")
    def test_command_carries_conversion_flags(self, mock_run):
        mock_run.return_value = _completed("# out\n")

        assert _run_pandoc("<p>x</p>") == "# out\n"

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "pandoc"
        assert cmd[2:] == [
            "-f",
            "html-native_divs-native_spans",
            "-t",
            "markdown-header_attributes",
            "--wrap=none",
            "--markdown-headings=atx",
        ]
        assert not Path(cmd[1]).exists(), "temp input file not cleaned up"

    @patch("subprocess.run", side_effect=FileNotFoundError("pandoc"))
    def test_missing_pandoc(self, _run):
        with pytest.raises(ArxivConversionError, match="Pandoc not found"):
            _run_pandoc("<p>x</p>")

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pandoc", 60))
    def test_timeout(self, _run):
        with pytest.raises(ArxivConversionError, match="timed out"):
            _run_pandoc("<p>x</p>")

    @patch("subprocess.run")
    def test_nonzero_exit(self, mock_run):
        mock_run.return_value = _completed("", returncode=2)
        with pytest.raises(ArxivConversionError, match="status 2: boom"):
            _run_pandoc("<p>x</p>")


class TestConvertArticle:
    @patch("subprocess.run")
    def test_converts_only_the_article(self, mock_run):
        seen: list[str] = []

        def fake_run(cmd, **kwargs):
            seen.append(Path(cmd[1]).read_text(encoding="utf-8"))
            return _completed("Text\\hspace{0pt}" + "y" * MIN_CONTENT_CHARS)

        mock_run.side_effect = fake_run
        page = (
            "<html><head><title>Page title</title></head><body><nav>chrome</nav>"
            '<article class="ltx_document"><figure class="ltx_figure"><p>paper</p></figure>'
            "</article><footer>footer</footer></body></html>"
        )

        markdown = convert_article(page)

        assert markdown == "Text" + "y" * MIN_CONTENT_CHARS
        assert seen == [
            '<html><body><article class="ltx_document"><p>paper</p></article></body></html>'
        ]

    def test_no_article_raises_without_running_pandoc(self):
        with patch("subprocess.run") as mock_run:
            with pytest.raises(ArxivConversionError, match="no recognized arXiv article"):
                convert_article("<html><body><p>plain page</p></body></html>")
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_short_output_raises(self, mock_run):
        mock_run.return_value = _completed("x" * (MIN_CONTENT_CHARS - 1))
        with pytest.raises(ArxivConversionError, match="too short"):
            convert_article(_SHORT_ARTICLE)

    @patch("subprocess.run", side_effect=FileNotFoundError("pandoc"))
    def test_missing_pandoc_raises(self, _run):
        with pytest.raises(ArxivConversionError, match="Pandoc not found"):
            convert_article(_SHORT_ARTICLE)

    @pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs Pandoc")
    def test_real_pandoc_on_fixture(self):
        markdown = convert_article(FIXTURE.read_text(encoding="utf-8"))

        refs = [m.group(2) for m in _MD_IMAGE_RE.finditer(markdown)]
        assert "2610.14224v1/intro_teaser.png" in refs
        assert "2610.14224v1/components.png" in refs
        assert any(
            r.startswith("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB") for r in refs
        )
        for s in ["# ", "## 1 Introduction", "## References", "## Appendix B Benchmarks"]:
            assert s in markdown
        assert "Agrawal et al. (2026)" in markdown
        assert "Figure 1:" in markdown
        assert "w/o library" in markdown  # Table 3
        assert "$k = 5$" in markdown  # math
        for s in CHROME_TEXT:
            assert s not in markdown, f"chrome {s!r} in converted output"


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
