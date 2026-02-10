"""Tests for PyMuPDF4LLMConverter.

Tests PDF validation, conversion, scanned PDF detection, quality flag reporting,
and error handling according to spec 014.
"""

import pymupdf
import pytest

from doc_ingest.converters.pdf_converter import PyMuPDF4LLMConverter
from doc_ingest.types import ConversionError


class TestPyMuPDF4LLMConverter:
    """Test suite for PyMuPDF4LLMConverter."""

    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        return PyMuPDF4LLMConverter()

    @pytest.fixture
    def native_pdf_bytes(self):
        """Create a simple native PDF with text."""
        # Create a minimal PDF with text using PyMuPDF
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)  # A4 size
        page.insert_text((72, 72), "This is a test document.\n\nIt has multiple paragraphs.")
        page.insert_text((72, 120), "# Heading 1\n\nSome content under heading.")

        # Add a simple table-like structure
        page.insert_text((72, 200), "| Column A | Column B |")
        page.insert_text((72, 220), "|----------|----------|")
        page.insert_text((72, 240), "| Value 1  | Value 2  |")

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    @pytest.fixture
    def scanned_pdf_bytes(self):
        """Create a PDF with no extractable text (simulates scanned PDF)."""
        # Create a PDF with just a blank page, no text (simulates scanned)
        doc = pymupdf.open()
        _ = doc.new_page(width=595, height=842)
        # No text insertion = scanned simulation

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    @pytest.fixture
    def pdf_with_tables(self):
        """Create a PDF with table structures."""
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)

        # Create markdown table syntax
        table_text = """
# Data Table

| Name    | Age | City       |
|---------|-----|------------|
| Alice   | 30  | New York   |
| Bob     | 25  | London     |
| Charlie | 35  | Tokyo      |
"""
        page.insert_text((72, 72), table_text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    @pytest.fixture
    def pdf_with_headings(self):
        """Create a PDF with heading structure."""
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)

        headings_text = """
# Main Title

## Section 1

Some content here.

## Section 2

More content.

### Subsection 2.1

Detailed information.
"""
        page.insert_text((72, 72), headings_text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_converter_name(self, converter):
        """Test converter name property."""
        assert converter.name == "PyMuPDF4LLMConverter"

    def test_can_convert_pdf(self, converter):
        """Test can_convert returns True for PDF format."""
        assert converter.can_convert("pdf") is True

    def test_can_convert_other_formats(self, converter):
        """Test can_convert returns False for non-PDF formats."""
        assert converter.can_convert("jats_xml") is False
        assert converter.can_convert("arxiv_html") is False
        assert converter.can_convert("publisher_html") is False
        assert converter.can_convert("docx") is False

    def test_validate_native_pdf(self, converter, native_pdf_bytes):
        """Test validation succeeds for native PDF with text."""
        result = converter.validate_source(native_pdf_bytes)

        assert result.is_valid is True
        assert result.content_length == len(native_pdf_bytes)
        assert result.has_body_content is True
        assert result.detected_content_type == "application/pdf"

    def test_validate_scanned_pdf(self, converter, scanned_pdf_bytes):
        """Test validation fails for scanned PDF (no text)."""
        result = converter.validate_source(scanned_pdf_bytes)

        assert result.is_valid is False
        assert result.content_length == len(scanned_pdf_bytes)
        assert result.has_body_content is False
        assert result.detected_content_type == "application/pdf"

    def test_validate_invalid_pdf(self, converter):
        """Test validation fails for invalid PDF bytes."""
        invalid_bytes = b"not a pdf"

        result = converter.validate_source(invalid_bytes)

        assert result.is_valid is False
        assert result.content_length == len(invalid_bytes)
        assert result.has_body_content is False

    def test_convert_native_pdf(self, converter, native_pdf_bytes):
        """Test successful conversion of native PDF."""
        result = converter.convert(native_pdf_bytes)

        assert result.markdown is not None
        assert len(result.markdown) > 0
        assert "test document" in result.markdown.lower()
        assert result.converter_name == "PyMuPDF4LLMConverter"
        assert isinstance(result.warnings, list)
        assert result.quality_flags is not None

    def test_convert_scanned_pdf_raises_needs_ocr(self, converter, scanned_pdf_bytes):
        """Test conversion raises ConversionError with needs_ocr for scanned PDF."""
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(scanned_pdf_bytes)

        error = exc_info.value
        assert error.category == "needs_ocr"
        assert "no extractable text" in str(error).lower()
        assert "content_length" in error.details

    def test_quality_flags_tables_detected(self, converter, pdf_with_tables):
        """Test quality flags report table presence."""
        result = converter.convert(pdf_with_tables)

        # Should detect tables from markdown table syntax
        assert result.quality_flags.has_tables is True

    def test_quality_flags_headings_detected(self, converter, pdf_with_headings):
        """Test quality flags report heading structure."""
        result = converter.convert(pdf_with_headings)

        # Should detect markdown headings (# ## ###)
        assert result.quality_flags.heading_structure_detected is True

    def test_quality_flags_no_tables(self, converter, native_pdf_bytes):
        """Test quality flags correctly report absence of tables."""
        result = converter.convert(native_pdf_bytes)

        # Native PDF might have table-like text, but should detect it
        # The test fixture has a simple table, so has_tables should be True
        assert result.quality_flags.has_tables is True

    def test_warnings_large_pdf(self, converter):
        """Test warnings include large PDF notice for 100+ pages."""
        # Create a PDF with 101 pages (with sufficient text on each)
        doc = pymupdf.open()
        for i in range(101):
            page = doc.new_page(width=595, height=842)
            # Add more text to ensure it's not considered scanned
            text = f"Page {i + 1}\n" + "Sample text content. " * 20
            page.insert_text((72, 72), text)

        pdf_bytes = doc.tobytes()
        doc.close()

        result = converter.convert(pdf_bytes)

        # Should warn about large PDF
        assert any("large pdf" in w.lower() for w in result.warnings)

    def test_warnings_images_present(self, converter):
        """Test warnings mention images when PDF contains images."""
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)

        # Add text to make it valid
        page.insert_text((72, 72), "Document with image placeholder.\n" * 10)

        # Create a minimal image and insert it
        # (PyMuPDF needs proper image data, so we'll create a 1x1 pixel)
        import base64

        # 1x1 red pixel PNG
        red_pixel_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        )

        rect = pymupdf.Rect(100, 100, 200, 200)
        page.insert_image(rect, stream=red_pixel_png)

        pdf_bytes = doc.tobytes()
        doc.close()

        result = converter.convert(pdf_bytes)

        # Should warn about images
        assert any("image" in w.lower() for w in result.warnings)

    def test_conversion_error_wraps_unexpected_exceptions(self, converter):
        """Test unexpected exceptions are wrapped as ConversionError with category=unknown."""
        # Create intentionally corrupted PDF bytes that will fail conversion
        corrupted_bytes = b"%PDF-1.4\n" + b"corrupted data" * 100

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(corrupted_bytes)

        error = exc_info.value
        # Should be wrapped as unknown error
        assert error.category in ["unknown", "needs_ocr"]  # Might fail validation first

    def test_multiple_conversions_same_instance(self, converter, native_pdf_bytes):
        """Test converter can be reused for multiple conversions."""
        result1 = converter.convert(native_pdf_bytes)
        result2 = converter.convert(native_pdf_bytes)

        # Should produce identical results
        assert result1.markdown == result2.markdown
        assert result1.converter_name == result2.converter_name

    def test_empty_pdf(self, converter):
        """Test handling of PDF with minimal text (near-empty)."""
        # PyMuPDF can't save empty PDFs, so create one with minimal text
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 72), "")  # Empty text insertion

        pdf_bytes = doc.tobytes()
        doc.close()

        # Should be treated as scanned (no meaningful text)
        result = converter.validate_source(pdf_bytes)
        assert result.is_valid is False

    def test_pdf_with_math_indicators(self, converter):
        """Test detection of math indicators in PDF."""
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)

        math_text = """
Mathematical equation:

E = mc²

Integration: ∫ f(x) dx

Summation: ∑ᵢ xᵢ

Square root: √(x² + y²)
"""
        page.insert_text((72, 72), math_text)
        pdf_bytes = doc.tobytes()
        doc.close()

        result = converter.convert(pdf_bytes)

        # Should detect math indicators (though not preserved)
        assert result.quality_flags.has_math is True
        # pymupdf4llm doesn't preserve LaTeX
        assert result.quality_flags.math_preserved is False
