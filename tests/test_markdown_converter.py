"""Tests for JATS and DOCX Pandoc converters.

Tests JATS XML and DOCX validation, conversion via Pandoc, quality flag reporting,
and error handling according to spec 016.
"""

import subprocess
import zipfile
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from doc_ingest.converters.markdown_converter import DOCXPandocConverter, JATSPandocConverter
from doc_ingest.types import ConversionError


class TestJATSPandocConverter:
    """Test suite for JATSPandocConverter."""

    @pytest.fixture
    def converter(self):
        """Create JATS converter instance."""
        return JATSPandocConverter()

    @pytest.fixture
    def valid_jats_xml(self):
        """Create valid JATS XML with article and body tags."""
        return b"""<?xml version="1.0"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.2 20190208//EN" "JATS-archivearticle1.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML">
  <front>
    <article-meta>
      <title-group>
        <article-title>Test Article</article-title>
      </title-group>
    </article-meta>
  </front>
  <body>
    <sec>
      <title>Introduction</title>
      <p>This is a test article with some content.</p>
      <table-wrap>
        <table>
          <thead>
            <tr><th>Column 1</th><th>Column 2</th></tr>
          </thead>
          <tbody>
            <tr><td>Value 1</td><td>Value 2</td></tr>
          </tbody>
        </table>
      </table-wrap>
    </sec>
    <sec>
      <title>Methods</title>
      <p>Some equations: <inline-formula><mml:math><mml:mi>E</mml:mi><mml:mo>=</mml:mo><mml:mi>mc</mml:mi><mml:msup><mml:mi>c</mml:mi><mml:mn>2</mml:mn></mml:msup></mml:math></inline-formula></p>
      <fig>
        <caption><p>Figure 1: Test figure</p></caption>
      </fig>
    </sec>
  </body>
</article>"""

    @pytest.fixture
    def jats_missing_body(self):
        """Create JATS XML missing body tag."""
        return b"""<?xml version="1.0"?>
<article>
  <front>
    <article-meta>
      <title-group>
        <article-title>Test Article</article-title>
      </title-group>
    </article-meta>
  </front>
</article>"""

    @pytest.fixture
    def jats_no_article_tag(self):
        """Create XML without article tag."""
        return b"""<?xml version="1.0"?>
<document>
  <title>Not JATS</title>
</document>"""

    def test_converter_name(self, converter):
        """Test converter name property."""
        assert converter.name == "JATSPandocConverter"

    def test_can_convert_jats(self, converter):
        """Test converter accepts jats_xml format."""
        assert converter.can_convert("jats_xml") is True

    def test_can_convert_rejects_other_formats(self, converter):
        """Test converter rejects non-JATS formats."""
        assert converter.can_convert("pdf") is False
        assert converter.can_convert("docx") is False
        assert converter.can_convert("arxiv_html") is False

    def test_validate_valid_jats(self, converter, valid_jats_xml):
        """Test validation succeeds for valid JATS XML."""
        result = converter.validate_source(valid_jats_xml)

        assert result.is_valid is True
        assert result.has_body_content is True
        assert result.content_length == len(valid_jats_xml)
        assert result.detected_content_type == "application/xml"

    def test_validate_jats_missing_body(self, converter, jats_missing_body):
        """Test validation fails for JATS missing body tag."""
        result = converter.validate_source(jats_missing_body)

        assert result.is_valid is False
        assert result.has_body_content is False
        assert result.content_length == len(jats_missing_body)

    def test_validate_no_article_tag(self, converter, jats_no_article_tag):
        """Test validation fails for non-JATS XML."""
        result = converter.validate_source(jats_no_article_tag)

        assert result.is_valid is False
        assert result.has_body_content is False

    def test_validate_invalid_bytes(self, converter):
        """Test validation handles invalid content gracefully."""
        invalid_content = b"\x00\x01\x02\xff"
        result = converter.validate_source(invalid_content)

        assert result.is_valid is False
        assert result.has_body_content is False
        # Note: decode with errors="ignore" succeeds, so content_type is still "application/xml"
        # even though the content isn't valid JATS (no article/body tags)

    @patch("subprocess.run")
    def test_convert_success(self, mock_run, converter, valid_jats_xml):
        """Test successful JATS conversion via Pandoc."""
        # Mock Pandoc output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# Test Article\n\n## Introduction\n\nThis is a test.\n\n| Column 1 | Column 2 |\n|---|---|\n| Value 1 | Value 2 |",
            stderr="",
        )

        result = converter.convert(valid_jats_xml)

        # Verify Pandoc was called correctly
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "pandoc"
        assert "-f" in call_args
        assert "jats" in call_args
        assert "-t" in call_args
        assert "markdown" in call_args

        # Verify result
        assert result.converter_name == "JATSPandocConverter"
        assert "# Test Article" in result.markdown
        assert result.quality_flags.heading_structure_detected is True
        assert result.quality_flags.has_tables is True
        assert len(result.warnings) == 0

    @patch("subprocess.run")
    def test_convert_with_math(self, mock_run, converter, valid_jats_xml):
        """Test JATS conversion preserves math."""
        # Mock Pandoc output with LaTeX math
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# Test\n\nEquation: $E = mc^2$\n\nDisplay: \\[F = ma\\]",
            stderr="",
        )

        result = converter.convert(valid_jats_xml)

        assert result.quality_flags.has_math is True
        assert result.quality_flags.math_preserved is True

    @patch("subprocess.run")
    def test_convert_with_figures(self, mock_run, converter, valid_jats_xml):
        """Test JATS conversion detects figure captions."""
        # Mock Pandoc output with figure references
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# Test\n\nFigure 1: Test figure\n\n![Alt text](image.png)",
            stderr="",
        )

        result = converter.convert(valid_jats_xml)

        assert result.quality_flags.has_figures is True
        assert result.quality_flags.figure_captions_present is True

    @patch("subprocess.run")
    def test_convert_pandoc_failure(self, mock_run, converter, valid_jats_xml):
        """Test conversion raises ConversionError on Pandoc failure."""
        # Mock Pandoc failure
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error: Invalid JATS XML")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_jats_xml)

        assert exc_info.value.category == "unsupported_format"
        assert "Pandoc conversion failed" in str(exc_info.value)
        assert exc_info.value.details["exit_code"] == 1

    @patch("subprocess.run")
    def test_convert_pandoc_warnings(self, mock_run, converter, valid_jats_xml):
        """Test conversion includes Pandoc stderr as warnings."""
        # Mock Pandoc success with warnings
        mock_run.return_value = MagicMock(
            returncode=0, stdout="# Test", stderr="Warning: Unknown element ignored"
        )

        result = converter.convert(valid_jats_xml)

        assert len(result.warnings) == 1
        assert "Pandoc warnings" in result.warnings[0]
        assert "Unknown element ignored" in result.warnings[0]

    @patch("subprocess.run")
    def test_convert_timeout(self, mock_run, converter, valid_jats_xml):
        """Test conversion raises ConversionError on timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pandoc", timeout=60)

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_jats_xml)

        assert exc_info.value.category == "conversion_timeout"
        assert "timed out" in str(exc_info.value)

    @patch("subprocess.run")
    def test_convert_pandoc_not_found(self, mock_run, converter, valid_jats_xml):
        """Test conversion raises ConversionError when Pandoc not installed."""
        # Mock Pandoc not found
        mock_run.side_effect = FileNotFoundError("pandoc not found")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_jats_xml)

        assert exc_info.value.category == "unsupported_format"
        assert "Pandoc binary not found" in str(exc_info.value)
        assert exc_info.value.details["missing_dependency"] == "pandoc"

    @patch("subprocess.run")
    def test_convert_unexpected_error(self, mock_run, converter, valid_jats_xml):
        """Test conversion wraps unexpected errors."""
        # Mock unexpected error
        mock_run.side_effect = RuntimeError("Unexpected failure")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_jats_xml)

        assert exc_info.value.category == "unknown"
        assert "Unexpected conversion error" in str(exc_info.value)


class TestDOCXPandocConverter:
    """Test suite for DOCXPandocConverter."""

    @pytest.fixture
    def converter(self):
        """Create DOCX converter instance."""
        return DOCXPandocConverter()

    @pytest.fixture
    def valid_docx_bytes(self):
        """Create a minimal valid DOCX file (ZIP with required structure)."""
        # Create a minimal DOCX structure in memory
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # DOCX requires at least [Content_Types].xml
            zf.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
            )
            # Minimal word/document.xml
            zf.writestr(
                "word/document.xml",
                '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test content</w:t></w:r></w:p></w:body></w:document>',
            )
        return buffer.getvalue()

    @pytest.fixture
    def invalid_docx_bytes(self):
        """Create invalid DOCX bytes (not a ZIP file)."""
        return b"This is not a DOCX file"

    def test_converter_name(self, converter):
        """Test converter name property."""
        assert converter.name == "DOCXPandocConverter"

    def test_can_convert_docx(self, converter):
        """Test converter accepts docx format."""
        assert converter.can_convert("docx") is True

    def test_can_convert_rejects_other_formats(self, converter):
        """Test converter rejects non-DOCX formats."""
        assert converter.can_convert("pdf") is False
        assert converter.can_convert("jats_xml") is False
        assert converter.can_convert("arxiv_html") is False

    def test_validate_valid_docx(self, converter, valid_docx_bytes):
        """Test validation succeeds for valid DOCX (ZIP format)."""
        result = converter.validate_source(valid_docx_bytes)

        assert result.is_valid is True
        assert result.has_body_content is True
        assert result.content_length == len(valid_docx_bytes)
        assert "wordprocessingml" in result.detected_content_type

    def test_validate_invalid_docx(self, converter, invalid_docx_bytes):
        """Test validation fails for non-ZIP content."""
        result = converter.validate_source(invalid_docx_bytes)

        assert result.is_valid is False
        assert result.has_body_content is False
        assert result.detected_content_type == "unknown"

    def test_validate_empty_file(self, converter):
        """Test validation fails for empty file."""
        result = converter.validate_source(b"")

        assert result.is_valid is False

    @patch("subprocess.run")
    def test_convert_success(self, mock_run, converter, valid_docx_bytes):
        """Test successful DOCX conversion via Pandoc."""
        # Mock Pandoc output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# Document Title\n\n## Section 1\n\nParagraph text.\n\n| A | B |\n|---|---|\n| 1 | 2 |",
            stderr="",
        )

        result = converter.convert(valid_docx_bytes)

        # Verify Pandoc was called correctly
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "pandoc"
        assert "-f" in call_args
        assert "docx" in call_args
        assert "-t" in call_args
        assert "markdown" in call_args

        # Verify result
        assert result.converter_name == "DOCXPandocConverter"
        assert "# Document Title" in result.markdown
        assert result.quality_flags.heading_structure_detected is True
        assert result.quality_flags.has_tables is True
        assert len(result.warnings) == 0

    @patch("subprocess.run")
    def test_convert_with_math(self, mock_run, converter, valid_docx_bytes):
        """Test DOCX conversion detects math."""
        # Mock Pandoc output with LaTeX math
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Equation: $x^2 + y^2 = z^2$", stderr=""
        )

        result = converter.convert(valid_docx_bytes)

        assert result.quality_flags.has_math is True
        assert result.quality_flags.math_preserved is True

    @patch("subprocess.run")
    def test_convert_with_figures(self, mock_run, converter, valid_docx_bytes):
        """Test DOCX conversion detects figures."""
        # Mock Pandoc output with image
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="![Figure caption](media/image1.png)\n\nFigure 2: Another caption",
            stderr="",
        )

        result = converter.convert(valid_docx_bytes)

        assert result.quality_flags.has_figures is True
        assert result.quality_flags.figure_captions_present is True

    @patch("subprocess.run")
    def test_convert_pandoc_failure(self, mock_run, converter, valid_docx_bytes):
        """Test conversion raises ConversionError on Pandoc failure."""
        # Mock Pandoc failure
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error: Corrupted DOCX")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_docx_bytes)

        assert exc_info.value.category == "unsupported_format"
        assert "Pandoc conversion failed" in str(exc_info.value)
        assert exc_info.value.details["exit_code"] == 1

    @patch("subprocess.run")
    def test_convert_pandoc_warnings(self, mock_run, converter, valid_docx_bytes):
        """Test conversion includes Pandoc stderr as warnings."""
        # Mock Pandoc success with warnings
        mock_run.return_value = MagicMock(
            returncode=0, stdout="# Test", stderr="Warning: Style not found"
        )

        result = converter.convert(valid_docx_bytes)

        assert len(result.warnings) == 1
        assert "Pandoc warnings" in result.warnings[0]
        assert "Style not found" in result.warnings[0]

    @patch("subprocess.run")
    def test_convert_timeout(self, mock_run, converter, valid_docx_bytes):
        """Test conversion raises ConversionError on timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pandoc", timeout=60)

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_docx_bytes)

        assert exc_info.value.category == "conversion_timeout"
        assert "timed out" in str(exc_info.value)

    @patch("subprocess.run")
    def test_convert_pandoc_not_found(self, mock_run, converter, valid_docx_bytes):
        """Test conversion raises ConversionError when Pandoc not installed."""
        # Mock Pandoc not found
        mock_run.side_effect = FileNotFoundError("pandoc not found")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_docx_bytes)

        assert exc_info.value.category == "unsupported_format"
        assert "Pandoc binary not found" in str(exc_info.value)
        assert exc_info.value.details["missing_dependency"] == "pandoc"

    @patch("subprocess.run")
    def test_convert_unexpected_error(self, mock_run, converter, valid_docx_bytes):
        """Test conversion wraps unexpected errors."""
        # Mock unexpected error
        mock_run.side_effect = RuntimeError("Unexpected failure")

        with pytest.raises(ConversionError) as exc_info:
            converter.convert(valid_docx_bytes)

        assert exc_info.value.category == "unknown"
        assert "Unexpected conversion error" in str(exc_info.value)
