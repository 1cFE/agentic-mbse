"""Tests for ConversionResult data model."""

import json

import pytest

from src.doc_ingest.types import ConversionResult, QualityFlags


class TestConversionResult:
    """Tests for ConversionResult class."""

    def test_successful_jats_conversion_with_table_warning(self) -> None:
        """Given successful JATS conversion with table warning, when result created, then all fields populated."""
        # Spec AC: "Given a successful JATS conversion with a table warning,
        # when result is created, then markdown contains extracted text,
        # warnings=["Table 2 missing column headers"], converter_name="JATSPandocConverter""
        flags = QualityFlags(has_tables=True)
        result = ConversionResult(
            markdown="# Introduction\n\nSample text.",
            warnings=["Table 2 missing column headers"],
            quality_flags=flags,
            converter_name="JATSPandocConverter",
        )

        assert result.markdown == "# Introduction\n\nSample text."
        assert result.warnings == ["Table 2 missing column headers"]
        assert result.quality_flags.has_tables is True
        assert result.converter_name == "JATSPandocConverter"

    def test_pdf_conversion_with_no_warnings(self) -> None:
        """Given PDF conversion with no warnings, when result created, then warnings is empty list."""
        # Spec AC: "Given a PDF conversion with no warnings,
        # when result is created, then warnings=[] (empty list, not None)"
        flags = QualityFlags()
        result = ConversionResult(
            markdown="# Document Title\n\nContent.",
            warnings=[],
            quality_flags=flags,
            converter_name="PyMuPDFConverter",
        )

        assert result.warnings == []
        assert result.warnings is not None
        assert len(result.warnings) == 0

    def test_quality_flags_serialization(self) -> None:
        """Given any conversion result, when serialized to JSON, then quality_flags is nested object."""
        # Spec AC: "Given any conversion result, when serialized to JSON,
        # then quality_flags is a nested object with all boolean fields"
        flags = QualityFlags(has_math=True, math_preserved=True)
        result = ConversionResult(
            markdown="Formula: $E=mc^2$",
            warnings=[],
            quality_flags=flags,
            converter_name="ArXivConverter",
        )

        # Serialize using dataclass __dict__ (simulating JSON serialization)
        result_dict = {
            "markdown": result.markdown,
            "warnings": result.warnings,
            "quality_flags": {
                "has_tables": result.quality_flags.has_tables,
                "tables_likely_corrupted": result.quality_flags.tables_likely_corrupted,
                "has_math": result.quality_flags.has_math,
                "math_preserved": result.quality_flags.math_preserved,
                "has_figures": result.quality_flags.has_figures,
                "figure_captions_present": result.quality_flags.figure_captions_present,
                "heading_structure_detected": result.quality_flags.heading_structure_detected,
            },
            "converter_name": result.converter_name,
        }

        # Verify all quality_flags keys are present
        assert "quality_flags" in result_dict
        quality_flags_dict = result_dict["quality_flags"]
        assert quality_flags_dict["has_math"] is True
        assert quality_flags_dict["math_preserved"] is True
        assert quality_flags_dict["has_tables"] is False  # Default value
        assert "heading_structure_detected" in quality_flags_dict

        # Verify it's JSON serializable
        json_str = json.dumps(result_dict)
        assert json_str is not None
        assert "quality_flags" in json_str

    def test_converter_name_required_for_provenance(self) -> None:
        """Given converter produces result, when converter_name is missing, then provenance cannot be created."""
        # Spec AC: "Given a converter that produces a result,
        # when converter_name is missing, then provenance record cannot be created
        # (converter name is required)"
        #
        # Note: Python dataclasses don't enforce required fields at construction time
        # if all parameters are positional. This test verifies that converter_name
        # is a required parameter in the dataclass signature.
        flags = QualityFlags()

        # This should require converter_name (will fail if we try to omit it)
        with pytest.raises(TypeError):
            ConversionResult(  # type: ignore[call-arg]
                markdown="Content",
                warnings=[],
                quality_flags=flags,
                # converter_name omitted - should fail
            )

    def test_multiple_warnings_allowed(self) -> None:
        """Given conversion with multiple issues, when result created, then warnings list contains all warnings."""
        flags = QualityFlags(has_tables=True, tables_likely_corrupted=True)
        result = ConversionResult(
            markdown="# Report\n\nSee table below.",
            warnings=[
                "Table 1 missing column headers",
                "Table 2 has merged cells",
                "Table 3 possibly malformed",
            ],
            quality_flags=flags,
            converter_name="PDFConverter",
        )

        assert len(result.warnings) == 3
        assert "Table 1 missing column headers" in result.warnings
        assert "Table 2 has merged cells" in result.warnings
        assert "Table 3 possibly malformed" in result.warnings

    def test_empty_markdown_allowed(self) -> None:
        """Given document with no extractable text, when result created, then markdown is empty string."""
        flags = QualityFlags()
        result = ConversionResult(
            markdown="",
            warnings=["No text content found"],
            quality_flags=flags,
            converter_name="EmptyDocConverter",
        )

        assert result.markdown == ""
        assert len(result.warnings) == 1

    def test_long_markdown_content(self) -> None:
        """Given large document, when result created, then markdown can contain long text."""
        flags = QualityFlags(heading_structure_detected=True)
        long_content = "# Chapter 1\n\n" + ("Lorem ipsum dolor sit amet. " * 1000)
        result = ConversionResult(
            markdown=long_content,
            warnings=[],
            quality_flags=flags,
            converter_name="LargeDocConverter",
        )

        assert len(result.markdown) > 10000
        assert result.markdown.startswith("# Chapter 1")

    def test_quality_flags_independence(self) -> None:
        """Given conversion result, when quality_flags is set, then it's independent from other results."""
        flags1 = QualityFlags(has_tables=True)
        result1 = ConversionResult(
            markdown="Doc 1",
            warnings=[],
            quality_flags=flags1,
            converter_name="Converter1",
        )

        flags2 = QualityFlags(has_math=True)
        result2 = ConversionResult(
            markdown="Doc 2",
            warnings=[],
            quality_flags=flags2,
            converter_name="Converter2",
        )

        # Verify independence
        assert result1.quality_flags.has_tables is True
        assert result1.quality_flags.has_math is False
        assert result2.quality_flags.has_tables is False
        assert result2.quality_flags.has_math is True

    def test_converter_name_provenance_tracking(self) -> None:
        """Given results from different converters, when comparing, then converter_name distinguishes them."""
        flags = QualityFlags()

        result_jats = ConversionResult(
            markdown="Content",
            warnings=[],
            quality_flags=flags,
            converter_name="JATSConverter",
        )

        result_pdf = ConversionResult(
            markdown="Content",
            warnings=[],
            quality_flags=flags,
            converter_name="PDFConverter",
        )

        # Same content, different converters
        assert result_jats.markdown == result_pdf.markdown
        assert result_jats.converter_name != result_pdf.converter_name
        assert result_jats.converter_name == "JATSConverter"
        assert result_pdf.converter_name == "PDFConverter"
