"""Tests for arxiv_html: paper selection and the shared Pandoc runner."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import re
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.arxiv_html import (
    _MD_IMAGE_RE,
    MIN_CONTENT_CHARS,
    ArxivConversionError,
    ArxivSource,
    ImageFetchError,
    ImagePersistResult,
    _postprocess_markdown,
    _preprocess_html,
    _run_pandoc,
    convert_article,
    extract_article,
    fetch_image,
    load_arxiv_html,
    persist_images,
    select_article,
)
from agentic_mbse.extraction.http import USER_AGENT, FetchResult
from tests.helpers.arxiv_page import FIGURES, assert_all_images_saved, serve_figure

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


class TestExtractArticle:
    def test_returns_the_article_with_svg_figures_as_images(self):
        page = FIXTURE.read_text(encoding="utf-8")
        assert page.count('<object type="image/svg+xml"') == 4

        article = extract_article(page)

        assert article.startswith("<article") and article.endswith("</article>")
        assert "<object" not in article
        assert (
            '<img src="2610.14224v1/scaling_curves.svg" alt="Refer to caption" id="S4.F5.g1" '
            'class="ltx_graphics ltx_centering ltx_img_landscape" width="310" height="119">'
        ) in article
        for figure in FIGURES:
            assert f'src="{figure}"' in article, f"figure {figure} missing"

    def test_no_article_raises(self):
        with pytest.raises(ArxivConversionError, match="no recognized arXiv article container"):
            extract_article("<html><body><p>plain page</p></body></html>")

    def test_object_fallback_text_becomes_alt(self):
        page = (
            '<article class="ltx_document"><object type="image/svg+xml" data="f.svg" '
            'class="ltx_graphics">A <b>plot</b> &amp; axes</object></article>'
        )
        assert extract_article(page) == (
            '<article class="ltx_document"><img src="f.svg" alt="A plot &amp; axes" '
            'class="ltx_graphics"></article>'
        )

    @pytest.mark.parametrize(
        "obj",
        [
            pytest.param('<object type="image/svg+xml" data="f.svg"></object>', id="no-ltx-class"),
            pytest.param(
                '<object type="application/pdf" data="f.pdf" class="ltx_graphics"></object>',
                id="not-svg",
            ),
        ],
    )
    def test_other_objects_untouched(self, obj):
        page = f'<article class="ltx_document">{obj}</article>'
        assert extract_article(page) == page


class TestConvertArticle:
    @patch("subprocess.run")
    def test_wraps_and_preprocesses_the_fragment(self, mock_run):
        seen: list[str] = []

        def fake_run(cmd, **kwargs):
            seen.append(Path(cmd[1]).read_text(encoding="utf-8"))
            return _completed("Text\\hspace{0pt}" + "y" * MIN_CONTENT_CHARS)

        mock_run.side_effect = fake_run
        article = (
            '<article class="ltx_document"><figure class="ltx_figure"><p>paper</p></figure>'
            "</article>"
        )

        markdown = convert_article(article)

        assert markdown == "Text" + "y" * MIN_CONTENT_CHARS
        assert seen == [
            '<html><body><article class="ltx_document"><p>paper</p></article></body></html>'
        ]

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
        markdown = convert_article(extract_article(FIXTURE.read_text(encoding="utf-8")))

        refs = [m.group(2) for m in _MD_IMAGE_RE.finditer(markdown)]
        assert [r for r in refs if not r.startswith("data:")] == FIGURES  # all nine, in order
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


def _fetched(content: bytes, final_url: str, encoding: str | None = "utf-8") -> FetchResult:
    return FetchResult(
        content=content, final_url=final_url, content_type="text/html", encoding=encoding
    )


class TestArxivSource:
    def test_from_fetch_keeps_raw_bytes_and_serving_url(self):
        raw = FIXTURE.read_bytes()
        source = ArxivSource.from_fetch(_fetched(raw, "https://arxiv.org/html/2610.14224v1"))

        assert source.raw_bytes == raw
        assert source.html == raw.decode("utf-8")
        assert source.serving_url == "https://arxiv.org/html/2610.14224v1"

    @pytest.mark.parametrize(
        ("final_url", "serving_url"),
        [
            ("https://arxiv.org/html/2610.14224v1/", "https://arxiv.org/html/2610.14224v1"),
            ("https://arxiv.org/html/2610.14224/", "https://arxiv.org/html/2610.14224"),
            ("https://example.com/paper/", "https://example.com/paper/"),
        ],
    )
    def test_from_fetch_strips_trailing_slash_on_arxiv_html_only(self, final_url, serving_url):
        source = ArxivSource.from_fetch(_fetched(b"<p>x</p>", final_url))
        assert source.serving_url == serving_url

    def test_image_base_without_base_href_is_serving_url(self):
        source = ArxivSource.from_fetch(
            _fetched(b"<p>x</p>", "https://arxiv.org/html/2610.14224v1")
        )
        assert source.image_base == "https://arxiv.org/html/2610.14224v1"

    @pytest.mark.parametrize(
        ("href", "base"),
        [
            ("https://cdn.example.org/assets/", "https://cdn.example.org/assets/"),
            ("figs/", "https://arxiv.org/html/figs/"),
        ],
    )
    def test_image_base_applies_base_href(self, href, base):
        html = f'<html><head><base href="{href}"></head><body></body></html>'.encode()
        source = ArxivSource.from_fetch(_fetched(html, "https://arxiv.org/html/2610.14224v1"))
        assert source.image_base == base


class TestLoadArxivHtml:
    def test_url_goes_through_fetch_url(self):
        raw = FIXTURE.read_bytes()
        with patch(
            "agentic_mbse.extraction.arxiv_html.fetch_url",
            return_value=_fetched(raw, "https://arxiv.org/html/2610.14224v1/"),
        ) as fetch:
            source = load_arxiv_html("https://arxiv.org/html/2610.14224", timeout=7)

        fetch.assert_called_once_with("https://arxiv.org/html/2610.14224", timeout=7)
        assert source.raw_bytes == raw
        assert source.serving_url == "https://arxiv.org/html/2610.14224v1"

    def test_local_file_serving_url_is_file_uri(self, tmp_path):
        page = tmp_path / "paper.html"
        page.write_bytes(FIXTURE.read_bytes())

        source = load_arxiv_html(page)

        assert source.raw_bytes == FIXTURE.read_bytes()
        assert source.serving_url == page.resolve().as_uri()
        assert source.image_base == page.resolve().as_uri()

    def test_local_file_path_as_string(self, tmp_path):
        page = tmp_path / "paper.html"
        page.write_text("<p>x</p>", encoding="utf-8")
        assert load_arxiv_html(str(page)).serving_url == page.resolve().as_uri()

    def test_missing_local_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_arxiv_html(tmp_path / "missing.html")


@pytest.mark.skipif(importlib.util.find_spec("bs4") is None, reason="needs [web] extra")
def test_selection_survives_web_sanitizer():
    from agentic_mbse.extraction.html_sanitize import strip_hidden_content

    article = select_article(strip_hidden_content(FIXTURE.read_text(encoding="utf-8")))
    assert article is not None
    for s in ["Recursive Agent Harnessing", "</span>Benchmarks</h2>", "ltx_tabular"]:
        assert s in article


# ---------------------------------------------------------------------------
# Image persistence (design D7, D8, D9; invariants 2, 3, 6)
# ---------------------------------------------------------------------------

_BASE = "https://arxiv.org/html/2610.14224v1"


def fake_fetch(table: dict[str, bytes | Exception]):
    """An image fetcher serving *table*; unknown URLs fail like a 404."""
    calls: list[str] = []

    def fetch(url: str) -> bytes:
        calls.append(url)
        value = table.get(url, OSError(f"HTTP Error 404: {url}"))
        if isinstance(value, Exception):
            raise value
        return value

    fetch.calls = calls  # type: ignore[attr-defined]
    return fetch


class TestPersistImages:
    def test_saves_and_rewrites_keeping_attributes(self, tmp_path):
        md = "![a](2610.14224v1/x1.png){#S1.F1.g1 .ltx_graphics} ![b](2610.14224v1/x2.png)"
        fetch = fake_fetch(
            {
                "https://arxiv.org/html/2610.14224v1/x1.png": b"P1",
                "https://arxiv.org/html/2610.14224v1/x2.png": b"P2",
            }
        )
        result = persist_images(md, _BASE, tmp_path / "images", fetch)

        assert result.saved_count == 2
        assert result.warnings == []
        assert result.markdown == (
            "![a](images/x1.png){#S1.F1.g1 .ltx_graphics} ![b](images/x2.png)"
        )
        assert (tmp_path / "images" / "x1.png").read_bytes() == b"P1"
        assert (tmp_path / "images" / "x2.png").read_bytes() == b"P2"

    def test_root_relative_and_absolute_refs(self, tmp_path):
        md = "![a](/html/2411.06644v1/figures/a.png) ![b](https://cdn.example.org/b.png)"
        fetch = fake_fetch(
            {
                "https://arxiv.org/html/2411.06644v1/figures/a.png": b"A",
                "https://cdn.example.org/b.png": b"B",
            }
        )
        result = persist_images(md, "https://arxiv.org/html/2411.06644v1", tmp_path, fetch)
        assert result.markdown == "![a](images/a.png) ![b](images/b.png)"
        assert result.saved_count == 2

    def test_same_url_twice_one_fetch_one_file(self, tmp_path):
        md = "![a](2610.14224v1/x1.png) and again ![a2](2610.14224v1/x1.png){width=50%}"
        fetch = fake_fetch({"https://arxiv.org/html/2610.14224v1/x1.png": b"P1"})

        result = persist_images(md, _BASE, tmp_path, fetch)

        assert fetch.calls == ["https://arxiv.org/html/2610.14224v1/x1.png"]
        assert result.saved_count == 1
        assert result.markdown == "![a](images/x1.png) and again ![a2](images/x1.png){width=50%}"
        assert sorted(p.name for p in tmp_path.iterdir()) == ["x1.png"]

    def test_same_url_twice_failure_one_warning_both_refs_kept(self, tmp_path):
        md = "![a](2610.14224v1/x1.png) ![a2](2610.14224v1/x1.png)"
        fetch = fake_fetch({})

        result = persist_images(md, _BASE, tmp_path / "images", fetch)

        assert result.markdown == md  # invariant 2: unsaved refs byte-identical
        assert result.saved_count == 0
        [warning] = result.warnings
        assert "https://arxiv.org/html/2610.14224v1/x1.png" in warning and "404" in warning
        assert not (tmp_path / "images").exists()

    def test_failure_leaves_ref_and_others_still_save(self, tmp_path):
        md = "![Good](figures/good.png) ![Bad](figures/bad.png)"
        fetch = fake_fetch({"https://arxiv.org/html/figures/good.png": b"G"})

        result = persist_images(md, _BASE, tmp_path, fetch)

        assert result.markdown == "![Good](images/good.png) ![Bad](figures/bad.png)"
        assert result.saved_count == 1
        assert len(result.warnings) == 1 and "bad.png" in result.warnings[0]

    def test_basename_collision_gets_suffix(self, tmp_path):
        md = "![A](figures/fig.png) ![B](extracted/fig.png) ![C](more/fig.png)"
        fetch = fake_fetch(
            {
                "https://arxiv.org/html/figures/fig.png": b"A",
                "https://arxiv.org/html/extracted/fig.png": b"B",
                "https://arxiv.org/html/more/fig.png": b"C",
            }
        )
        result = persist_images(md, _BASE, tmp_path, fetch)

        assert (
            result.markdown == "![A](images/fig.png) ![B](images/fig_2.png) ![C](images/fig_3.png)"
        )
        assert [(tmp_path / n).read_bytes() for n in ("fig.png", "fig_2.png", "fig_3.png")] == [
            b"A",
            b"B",
            b"C",
        ]

    def test_repeated_slashes_in_path_collapse(self, tmp_path):
        fetch = fake_fetch({"https://arxiv.org/html/2503.18960v1/fig_canis.png": b"F"})
        result = persist_images(
            "![Fig](/html/2503.18960v1//fig_canis.png)",
            "https://arxiv.org/html/2503.18960v1",
            tmp_path,
            fetch,
        )
        assert fetch.calls == ["https://arxiv.org/html/2503.18960v1/fig_canis.png"]
        assert result.markdown == "![Fig](images/fig_canis.png)"

    def test_data_uri_saved_by_content_hash_and_not_fetched(self, tmp_path):
        """D18: an inline data: image becomes a file, written once however often it appears."""
        png = b"\x89PNG fake"
        uri = "data:image/png;base64," + base64.b64encode(png).decode()
        md = f"![a]({uri}){{.ltx_picture}} ![Real](x/real.png) ![b]({uri})"
        fetch = fake_fetch({"https://arxiv.org/html/x/real.png": b"R"})

        result = persist_images(md, _BASE, tmp_path / "images", fetch)

        name = f"{hashlib.sha256(png).hexdigest()[:16]}.png"
        assert result.markdown == (
            f"![a](images/{name}){{.ltx_picture}} ![Real](images/real.png) ![b](images/{name})"
        )
        assert (tmp_path / "images" / name).read_bytes() == png
        assert result.saved_count == 2
        assert result.warnings == []
        assert fetch.calls == ["https://arxiv.org/html/x/real.png"]  # data: is never fetched

    def test_svg_data_uri_base64_and_percent_encoded(self, tmp_path):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>'
        b64 = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
        pct = "data:image/svg+xml," + urllib.parse.quote(svg.decode() + " ")

        result = persist_images(f"![a]({b64}) ![b]({pct})", _BASE, tmp_path, fake_fetch({}))

        refs = re.findall(r"\]\((images/[^)]+)\)", result.markdown)
        assert [Path(r).suffix for r in refs] == [".svg", ".svg"]
        assert (tmp_path / Path(refs[0]).name).read_bytes() == svg
        assert (tmp_path / Path(refs[1]).name).read_bytes() == svg + b" "
        assert result.saved_count == 2

    @pytest.mark.parametrize(
        ("uri", "reason"),
        [
            pytest.param("data:image/png;base64,@@not-base64@@", "base64", id="bad-base64"),
            pytest.param("data:application/x-unknown;base64,AAAA", "media type", id="unknown-type"),
            pytest.param("data:image/png;base64", "malformed", id="no-comma"),
        ],
    )
    def test_undecodable_data_uri_stays_inline_with_one_warning(self, tmp_path, uri, reason):
        md = f"![x]({uri}) ![y]({uri})"
        result = persist_images(md, _BASE, tmp_path / "images", fake_fetch({}))

        assert result.markdown == md
        assert result.saved_count == 0
        [warning] = result.warnings
        assert reason in warning
        assert len(warning) < 200  # names the image without dumping the payload

    def test_no_images_is_noop(self, tmp_path):
        result = persist_images("# Title\n\nText.", _BASE, tmp_path / "images", fake_fetch({}))
        assert result == ImagePersistResult("# Title\n\nText.", 0, [])
        assert not (tmp_path / "images").exists()

    def test_local_html_refs(self, tmp_path):
        """R1 local cases: absolute http fetched; <base href>-relative and file-relative copied;
        unresolvable left as written with a warning. No arXiv base is guessed."""
        page_dir = tmp_path / "page"
        (page_dir / "2610.14224v1").mkdir(parents=True)
        (page_dir / "2610.14224v1" / "local.png").write_bytes(b"L")
        (page_dir / "assets").mkdir()
        (page_dir / "assets" / "based.png").write_bytes(b"B")
        page = page_dir / "paper.html"
        page.write_text('<html><head><base href="assets/"></head><body></body></html>')
        source = load_arxiv_html(page)
        file_base = page.resolve().as_uri()
        md = (
            "![abs](https://cdn.example.org/abs.png) "
            "![rel](../2610.14224v1/local.png) "
            "![based](based.png) "
            "![root](/html/2610.14224v1/root.png) "
            "![missing](missing.png)"
        )
        fetch = fake_fetch({"https://cdn.example.org/abs.png": b"H"})

        result = persist_images(md, source.image_base, tmp_path / "images", fetch)

        assert source.image_base == file_base.rsplit("/", 1)[0] + "/assets/"
        assert result.markdown == (
            "![abs](images/abs.png) ![rel](images/local.png) ![based](images/based.png) "
            "![root](/html/2610.14224v1/root.png) ![missing](missing.png)"
        )
        assert result.saved_count == 3
        assert (tmp_path / "images" / "local.png").read_bytes() == b"L"
        assert len(result.warnings) == 2
        assert fetch.calls == ["https://cdn.example.org/abs.png"]

    def test_local_html_without_base_resolves_against_its_directory(self, tmp_path):
        (tmp_path / "2610.14224v1").mkdir()
        (tmp_path / "2610.14224v1" / "fig.png").write_bytes(b"F")
        page = tmp_path / "paper.html"
        page.write_text("<html><body></body></html>")

        source = load_arxiv_html(page)
        result = persist_images(
            "![f](2610.14224v1/fig.png)", source.image_base, tmp_path / "images", fake_fetch({})
        )

        assert result.markdown == "![f](images/fig.png)"
        assert (tmp_path / "images" / "fig.png").read_bytes() == b"F"

    def test_unsupported_scheme_warns(self, tmp_path):
        result = persist_images("![x](ftp://host/x.png)", _BASE, tmp_path, fake_fetch({}))
        assert result.markdown == "![x](ftp://host/x.png)"
        [warning] = result.warnings
        assert "ftp" in warning


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs Pandoc")
def test_all_fixture_images_persist(tmp_path):
    """Phase 6 and D18 acceptance at module level: every figure and inline image is a file."""
    markdown = convert_article(extract_article(FIXTURE.read_text(encoding="utf-8")))

    result = persist_images(markdown, _BASE, tmp_path / "images", serve_figure)

    assert result.warnings == []
    assert_all_images_saved(result.markdown, tmp_path / "images", result.saved_count)


class TestFetchImage:
    def _response(self, data: bytes) -> MagicMock:
        resp = MagicMock()
        resp.read = lambda n=-1: data if n == -1 else data[:n]
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_returns_bytes_with_user_agent(self):
        with patch("urllib.request.urlopen", return_value=self._response(b"PNG")) as urlopen:
            assert fetch_image("https://arxiv.org/html/x.png", max_bytes=10) == b"PNG"
        request = urlopen.call_args.args[0]
        assert request.get_header("User-agent") == USER_AGENT

    def test_oversize_raises(self):
        with patch("urllib.request.urlopen", return_value=self._response(b"X" * 11)):
            with pytest.raises(ImageFetchError, match="larger than 10 bytes"):
                fetch_image("https://arxiv.org/html/big.png", max_bytes=10)

    def test_oversize_through_persist_leaves_ref_and_warns(self, tmp_path):
        def too_big(url: str) -> bytes:
            raise ImageFetchError("larger than 10 bytes")

        result = persist_images("![Big](x/big.png)", _BASE, tmp_path / "images", too_big)
        assert result.markdown == "![Big](x/big.png)"
        assert result.saved_count == 0
        [warning] = result.warnings
        assert "larger than 10 bytes" in warning
        assert not (tmp_path / "images").exists()
