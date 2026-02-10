"""Tests for SourceCandidate data model."""

import pytest

from src.doc_ingest.types import QUALITY_TIERS, SourceCandidate


class TestSourceCandidate:
    """Tests for SourceCandidate class."""

    def test_jats_xml_from_openalex(self) -> None:
        """Given JATS XML from OpenAlex, when created, then correct format and tier."""
        source = SourceCandidate(
            quality_tier=QUALITY_TIERS["jats_xml"],
            format="jats_xml",
            url="https://example.com/article.xml",
            discovered_via="openalex_api",
        )
        assert source.format == "jats_xml"
        assert source.quality_tier == 1
        assert source.discovered_via == "openalex_api"
        assert source.url == "https://example.com/article.xml"
        assert source.local_path is None

    def test_pdf_from_arxiv(self) -> None:
        """Given PDF from arXiv, when created, then quality_tier=4."""
        source = SourceCandidate(
            quality_tier=QUALITY_TIERS["pdf"],
            format="pdf",
            url="https://arxiv.org/pdf/1602.03837.pdf",
            discovered_via="arxiv_api",
        )
        assert source.format == "pdf"
        assert source.quality_tier == 4
        assert source.discovered_via == "arxiv_api"

    def test_local_pdf_file(self) -> None:
        """Given local PDF file, when created, then local_path set and url is None."""
        source = SourceCandidate(
            quality_tier=QUALITY_TIERS["pdf"],
            format="pdf",
            local_path="/path/to/paper.pdf",
            discovered_via="local_file",
        )
        assert source.local_path == "/path/to/paper.pdf"
        assert source.url is None
        assert source.discovered_via == "local_file"

    def test_requires_either_url_or_local_path(self) -> None:
        """Given neither url nor local_path, when created, then raises ValueError."""
        with pytest.raises(ValueError, match="Either url or local_path must be provided"):
            SourceCandidate(
                quality_tier=4,
                format="pdf",
                discovered_via="unknown",
            )

    def test_url_and_local_path_are_mutually_exclusive(self) -> None:
        """Given both url and local_path, when created, then raises ValueError."""
        with pytest.raises(ValueError, match="url and local_path are mutually exclusive"):
            SourceCandidate(
                quality_tier=4,
                format="pdf",
                url="https://example.com/paper.pdf",
                local_path="/path/to/paper.pdf",
                discovered_via="unknown",
            )

    def test_sorting_by_quality_tier(self) -> None:
        """Given sources with different quality tiers, when sorted, then lower tier first."""
        jats = SourceCandidate(
            quality_tier=1, format="jats_xml", url="https://example.com/a.xml", discovered_via="api"
        )
        arxiv_html = SourceCandidate(
            quality_tier=2,
            format="arxiv_html",
            url="https://arxiv.org/html/1234",
            discovered_via="api",
        )
        pdf = SourceCandidate(
            quality_tier=4, format="pdf", url="https://example.com/paper.pdf", discovered_via="api"
        )

        sources = [pdf, arxiv_html, jats]
        sorted_sources = sorted(sources)

        assert sorted_sources[0].format == "jats_xml"
        assert sorted_sources[1].format == "arxiv_html"
        assert sorted_sources[2].format == "pdf"

    def test_secondary_sort_by_url(self) -> None:
        """Given sources with same quality tier, when sorted, then lexicographic by URL."""
        source_a = SourceCandidate(
            quality_tier=4, format="pdf", url="https://a.com/paper.pdf", discovered_via="api"
        )
        source_b = SourceCandidate(
            quality_tier=4, format="pdf", url="https://b.com/paper.pdf", discovered_via="api"
        )
        source_z = SourceCandidate(
            quality_tier=4, format="pdf", url="https://z.com/paper.pdf", discovered_via="api"
        )

        sources = [source_z, source_a, source_b]
        sorted_sources = sorted(sources)

        assert sorted_sources[0].url == "https://a.com/paper.pdf"
        assert sorted_sources[1].url == "https://b.com/paper.pdf"
        assert sorted_sources[2].url == "https://z.com/paper.pdf"

    def test_secondary_sort_by_local_path(self) -> None:
        """Given local sources with same tier, when sorted, then lexicographic by path."""
        source_a = SourceCandidate(
            quality_tier=4, format="pdf", local_path="/a/paper.pdf", discovered_via="local"
        )
        source_b = SourceCandidate(
            quality_tier=4, format="pdf", local_path="/b/paper.pdf", discovered_via="local"
        )

        sources = [source_b, source_a]
        sorted_sources = sorted(sources)

        assert sorted_sources[0].local_path == "/a/paper.pdf"
        assert sorted_sources[1].local_path == "/b/paper.pdf"

    def test_http_content_type_preserved(self) -> None:
        """Given source with HTTP content type, when serialized, then field preserved."""
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/paper.pdf",
            discovered_via="api",
            http_content_type="application/pdf",
        )
        assert source.http_content_type == "application/pdf"

    def test_optional_metadata_fields(self) -> None:
        """Given source with publisher and license, when created, then metadata preserved."""
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/article.xml",
            discovered_via="openalex_api",
            http_content_type="application/xml",
            publisher="Nature Publishing Group",
            license="CC-BY-4.0",
        )
        assert source.publisher == "Nature Publishing Group"
        assert source.license == "CC-BY-4.0"
        assert source.http_content_type == "application/xml"

    def test_quality_tier_constants(self) -> None:
        """Given QUALITY_TIERS mapping, when accessed, then correct values."""
        assert QUALITY_TIERS["jats_xml"] == 1
        assert QUALITY_TIERS["arxiv_html"] == 2
        assert QUALITY_TIERS["publisher_html"] == 3
        assert QUALITY_TIERS["pdf"] == 4
        assert QUALITY_TIERS["docx"] == 5

    def test_all_source_formats_have_quality_tiers(self) -> None:
        """Given all SourceFormat literals, when checked, then all in QUALITY_TIERS."""
        # This ensures QUALITY_TIERS is complete
        formats = ["jats_xml", "arxiv_html", "publisher_html", "pdf", "docx"]
        for fmt in formats:
            assert fmt in QUALITY_TIERS

    def test_arxiv_html_higher_quality_than_publisher_html(self) -> None:
        """Given arXiv HTML and publisher HTML, when compared, then arXiv is better."""
        assert QUALITY_TIERS["arxiv_html"] < QUALITY_TIERS["publisher_html"]

    def test_any_structured_format_better_than_pdf(self) -> None:
        """Given any structured format, when compared to PDF, then structured is better."""
        assert QUALITY_TIERS["jats_xml"] < QUALITY_TIERS["pdf"]
        assert QUALITY_TIERS["arxiv_html"] < QUALITY_TIERS["pdf"]
        assert QUALITY_TIERS["publisher_html"] < QUALITY_TIERS["pdf"]
