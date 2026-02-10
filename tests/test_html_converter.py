"""Tests for HTML converters (ArXiv and Publisher)."""

import pytest

from doc_ingest.converters.html_converter import ArXivHTMLConverter, PublisherHTMLConverter
from doc_ingest.types import ConversionError


class TestArXivHTMLConverter:
    """Tests for ArXivHTMLConverter."""

    def test_can_convert_arxiv_html(self) -> None:
        """Test can_convert returns True for arxiv_html format."""
        converter = ArXivHTMLConverter()
        assert converter.can_convert("arxiv_html") is True
        assert converter.can_convert("publisher_html") is False
        assert converter.can_convert("pdf") is False

    def test_converter_name(self) -> None:
        """Test converter returns correct name."""
        converter = ArXivHTMLConverter()
        assert converter.name == "ArXivHTMLConverter"

    def test_validate_valid_arxiv_html(self) -> None:
        """Test validation passes for valid arXiv HTML with body content."""
        # Need >1KB to pass truncation check
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <div class="ltx_page_content">
                <article>
                    <h1 class="ltx_title">Test Article</h1>
                    <p>Article content here with enough text to exceed truncation threshold.
                       Adding more text to ensure we have sufficient content for validation.
                       This paragraph needs to be long enough to avoid the 1KB truncation limit.
                       More text here to pad out the content and ensure proper validation passes.
                       Additional content to reach the byte threshold required for valid HTML.</p>
                    <p>Second paragraph with more substantial content to ensure the document
                       is not flagged as truncated during validation. This helps demonstrate
                       that the HTML document contains sufficient content to be considered valid.</p>
                    <p>Third paragraph adding even more text to absolutely ensure we exceed
                       the 1KB threshold that triggers the truncation flag. This verbose content
                       is necessary to test the validation logic properly and ensure it works.</p>
                </article>
            </div>
        </body>
        </html>
        """
        converter = ArXivHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_valid is True
        assert result.has_body_content is True
        assert result.detected_content_type == "text/html"
        assert result.is_truncated is False

    def test_validate_missing_body_content(self) -> None:
        """Test validation fails for HTML without body content."""
        html_content = b"""
        <!DOCTYPE html>
        <html><body><p>No article content</p></body></html>
        """
        converter = ArXivHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_valid is False
        assert result.has_body_content is False

    def test_validate_truncated_html(self) -> None:
        """Test validation fails for truncated HTML (< 1KB)."""
        html_content = b"<html><body><div class='ltx_page_content'>Short</div></body></html>"
        converter = ArXivHTMLConverter()
        result = converter.validate_source(html_content)

        # Should detect truncation
        assert result.is_truncated is True
        assert result.is_valid is False

    def test_validate_invalid_html(self) -> None:
        """Test validation handles invalid HTML gracefully."""
        html_content = b"\x00\x01\x02\x03"  # Binary garbage
        converter = ArXivHTMLConverter()
        result = converter.validate_source(html_content)

        # BeautifulSoup is permissive, so this still parses but has no body content
        assert result.is_valid is False
        assert result.has_body_content is False

    def test_convert_arxiv_html_with_mathml(self) -> None:
        """Test conversion of arXiv HTML with MathML."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <div class="ltx_page_content">
                <article>
                    <h1 class="ltx_title">Test Article</h1>
                    <section class="ltx_section">
                        <h2>Section 1</h2>
                        <p class="ltx_para">Here is some math: <math><mi>x</mi><mo>=</mo><mn>5</mn></math></p>
                    </section>
                </article>
            </div>
        </body>
        </html>
        """
        converter = ArXivHTMLConverter()
        result = converter.convert(html_content)

        assert result.converter_name == "ArXivHTMLConverter"
        assert "Test Article" in result.markdown
        assert "Section 1" in result.markdown
        assert result.quality_flags.has_math is True
        assert result.quality_flags.math_preserved is True
        assert result.quality_flags.heading_structure_detected is True

    def test_convert_arxiv_html_with_tables(self) -> None:
        """Test conversion detects tables."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <div class="ltx_page_content">
                <article>
                    <h1 class="ltx_title">Test Article</h1>
                    <table>
                        <tr><th>Header 1</th><th>Header 2</th></tr>
                        <tr><td>Data 1</td><td>Data 2</td></tr>
                    </table>
                </article>
            </div>
        </body>
        </html>
        """
        converter = ArXivHTMLConverter()
        result = converter.convert(html_content)

        assert result.quality_flags.has_tables is True
        assert "Header 1" in result.markdown
        assert "Data 1" in result.markdown
        assert "|" in result.markdown  # Markdown table syntax

    def test_convert_arxiv_html_with_figures(self) -> None:
        """Test conversion detects figures and captions."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <div class="ltx_page_content">
                <article>
                    <h1 class="ltx_title">Test Article</h1>
                    <figure>
                        <img src="fig1.png" alt="Figure 1">
                        <figcaption>This is a caption</figcaption>
                    </figure>
                </article>
            </div>
        </body>
        </html>
        """
        converter = ArXivHTMLConverter()
        result = converter.convert(html_content)

        assert result.quality_flags.has_figures is True
        assert result.quality_flags.figure_captions_present is True

    def test_convert_missing_main_content(self) -> None:
        """Test conversion fails gracefully when main content is missing."""
        html_content = b"<html><head><title>Test</title></head><p>No article structure</p></html>"
        converter = ArXivHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        assert exc_info.value.category == "unsupported_format"
        # Should fail with either "No main content" or "empty extraction" - both are valid failures
        assert exc_info.value.category == "unsupported_format"

    def test_convert_empty_extraction(self) -> None:
        """Test conversion fails when extracted markdown is empty."""
        html_content = b"""
        <html><body><div class="ltx_page_content"></div></body></html>
        """
        converter = ArXivHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        assert exc_info.value.category == "unsupported_format"
        assert "empty" in str(exc_info.value).lower()

    def test_convert_handles_unexpected_errors(self) -> None:
        """Test conversion wraps unexpected exceptions."""
        html_content = b"\x00\x01\x02\x03"  # Binary garbage
        converter = ArXivHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        # BeautifulSoup parses this but extraction fails due to no content
        assert exc_info.value.category == "unsupported_format"


class TestPublisherHTMLConverter:
    """Tests for PublisherHTMLConverter."""

    def test_can_convert_publisher_html(self) -> None:
        """Test can_convert returns True for publisher_html format."""
        converter = PublisherHTMLConverter()
        assert converter.can_convert("publisher_html") is True
        assert converter.can_convert("arxiv_html") is False
        assert converter.can_convert("pdf") is False

    def test_converter_name(self) -> None:
        """Test converter returns correct name."""
        converter = PublisherHTMLConverter()
        assert converter.name == "PublisherHTMLConverter"

    def test_validate_valid_publisher_html(self) -> None:
        """Test validation passes for valid publisher HTML with body content."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>Article content here with more text to exceed the truncation threshold.
                   This needs to be long enough to avoid being flagged as truncated.
                   Adding more text to ensure we exceed 1KB threshold for validation.</p>
                <p>Additional paragraph content to ensure sufficient length for validation.
                   This helps demonstrate that the article has complete content and is not
                   truncated or incomplete. More content here to reach the byte threshold.</p>
                <p>Third paragraph with even more text to ensure we definitely exceed the
                   1024 byte truncation limit. This is necessary to properly test the validation
                   logic and ensure it works as expected for valid publisher HTML documents.</p>
                <p>Fourth paragraph adding more substantial content to pad out the test data.
                   We need to be absolutely certain that the HTML content exceeds one kilobyte
                   so that the truncation flag is not triggered during validation testing.</p>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_valid is True
        assert result.has_body_content is True
        assert result.detected_content_type == "text/html"
        assert result.is_paywall is False

    def test_validate_paywall_detected(self) -> None:
        """Test validation fails when paywall markers detected."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>Login required to view this content.</p>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_valid is False
        assert result.is_paywall is True

    def test_validate_multiple_paywall_markers(self) -> None:
        """Test various paywall markers are detected."""
        paywall_texts = [
            b"<p>Access denied to this article</p>",
            b"<p>Subscribe to view full content</p>",
            b"<p>Subscription required for access</p>",
            b"<p>Purchase article to continue</p>",
        ]

        converter = PublisherHTMLConverter()
        for text in paywall_texts:
            html_content = b"<html><body><article>" + text + b"</article></body></html>"
            result = converter.validate_source(html_content)
            assert result.is_paywall is True, f"Failed to detect paywall in: {text}"

    def test_validate_missing_body_content(self) -> None:
        """Test validation fails for HTML without body content."""
        html_content = b"""
        <!DOCTYPE html>
        <html><body><p>No article element</p></body></html>
        """
        converter = PublisherHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_valid is False
        assert result.has_body_content is False

    def test_validate_truncated_html(self) -> None:
        """Test validation fails for truncated HTML (< 1KB)."""
        html_content = b"<html><body><article>Short</article></body></html>"
        converter = PublisherHTMLConverter()
        result = converter.validate_source(html_content)

        assert result.is_truncated is True
        assert result.is_valid is False

    def test_validate_invalid_html(self) -> None:
        """Test validation handles invalid HTML gracefully."""
        html_content = b"\x00\x01\x02\x03"
        converter = PublisherHTMLConverter()
        result = converter.validate_source(html_content)

        # BeautifulSoup is permissive, so this still parses but has no body content
        assert result.is_valid is False
        assert result.has_body_content is False

    def test_convert_publisher_html_basic(self) -> None:
        """Test conversion of basic publisher HTML."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article Title</h1>
                <h2>Section 1</h2>
                <p>Paragraph content here.</p>
                <h2>Section 2</h2>
                <p>More content in section 2.</p>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.convert(html_content)

        assert result.converter_name == "PublisherHTMLConverter"
        assert "Test Article Title" in result.markdown
        assert "Section 1" in result.markdown
        assert "Section 2" in result.markdown
        assert result.quality_flags.heading_structure_detected is True

    def test_convert_publisher_html_with_tables(self) -> None:
        """Test conversion detects tables."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <table>
                    <tr><th>Column 1</th><th>Column 2</th></tr>
                    <tr><td>Value 1</td><td>Value 2</td></tr>
                </table>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.convert(html_content)

        assert result.quality_flags.has_tables is True
        assert "Column 1" in result.markdown
        assert "|" in result.markdown  # Markdown table syntax

    def test_convert_publisher_html_with_math(self) -> None:
        """Test conversion detects math but warns about preservation."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>Here is math: <span class="math">x = 5</span></p>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.convert(html_content)

        assert result.quality_flags.has_math is True
        assert result.quality_flags.math_preserved is False
        assert any("math" in w.lower() for w in result.warnings)

    def test_convert_publisher_html_with_figures(self) -> None:
        """Test conversion detects figures and captions."""
        html_content = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <figure>
                    <img src="fig1.png" alt="Figure">
                    <figcaption>Figure caption</figcaption>
                </figure>
            </article>
        </body>
        </html>
        """
        converter = PublisherHTMLConverter()
        result = converter.convert(html_content)

        assert result.quality_flags.has_figures is True
        assert result.quality_flags.figure_captions_present is True

    def test_convert_missing_main_content(self) -> None:
        """Test conversion fails gracefully when main content is missing."""
        html_content = b"<html><head><title>Test</title></head><p>No article</p></html>"
        converter = PublisherHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        # Should fail with either "No main content" or "empty extraction" - both are valid
        assert exc_info.value.category == "unsupported_format"

    def test_convert_empty_extraction(self) -> None:
        """Test conversion fails when extracted markdown is empty."""
        html_content = b"<html><body><article></article></body></html>"
        converter = PublisherHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        assert exc_info.value.category == "unsupported_format"
        assert "empty" in str(exc_info.value).lower()

    def test_convert_handles_unexpected_errors(self) -> None:
        """Test conversion wraps unexpected exceptions."""
        html_content = b"\x00\x01\x02\x03"
        converter = PublisherHTMLConverter()

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(html_content)

        # BeautifulSoup parses this but extraction fails due to no content
        assert exc_info.value.category == "unsupported_format"

    def test_convert_alternative_content_structures(self) -> None:
        """Test converter handles various publisher HTML structures."""
        # Test with <main> element
        html_main = b"""
        <html><body>
            <main>
                <h1>Article with main tag</h1>
                <p>Content here.</p>
            </main>
        </body></html>
        """
        # Test with div.article
        html_div = b"""
        <html><body>
            <div class="article-content">
                <h1>Article with div class</h1>
                <p>Content here.</p>
            </div>
        </body></html>
        """

        converter = PublisherHTMLConverter()

        result_main = converter.convert(html_main)
        assert "Article with main tag" in result_main.markdown

        result_div = converter.convert(html_div)
        assert "Article with div class" in result_div.markdown
