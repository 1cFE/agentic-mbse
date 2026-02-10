"""Tests for QualityFlags data model."""

import json

from src.doc_ingest.types import QualityFlags


class TestQualityFlags:
    """Tests for QualityFlags class."""

    def test_default_values_all_false(self) -> None:
        """Given no arguments, when QualityFlags created, then all fields default to False."""
        flags = QualityFlags()
        assert flags.has_tables is False
        assert flags.tables_likely_corrupted is False
        assert flags.has_math is False
        assert flags.math_preserved is False
        assert flags.has_figures is False
        assert flags.figure_captions_present is False
        assert flags.heading_structure_detected is False

    def test_jats_with_clean_tables(self) -> None:
        """Given JATS converter with tables, when flags set, then has_tables=True and not corrupted."""
        flags = QualityFlags(has_tables=True, tables_likely_corrupted=False)
        assert flags.has_tables is True
        assert flags.tables_likely_corrupted is False

    def test_pdf_with_corrupted_tables(self) -> None:
        """Given PDF converter with garbled tables, when flags set, then both table flags=True."""
        flags = QualityFlags(has_tables=True, tables_likely_corrupted=True)
        assert flags.has_tables is True
        assert flags.tables_likely_corrupted is True

    def test_arxiv_html_with_preserved_math(self) -> None:
        """Given arXiv HTML with MathML, when flags set, then math flags=True."""
        flags = QualityFlags(has_math=True, math_preserved=True)
        assert flags.has_math is True
        assert flags.math_preserved is True

    def test_converter_without_figure_detection(self) -> None:
        """Given converter without figure detection, when flags set, then figure flags=False."""
        flags = QualityFlags()
        assert flags.has_figures is False
        assert flags.figure_captions_present is False

    def test_json_serialization_includes_all_fields(self) -> None:
        """Given QualityFlags, when serialized to JSON, then all 7 fields present."""
        flags = QualityFlags(has_tables=True, math_preserved=True)
        # Dataclass asdict or manual dict conversion
        flags_dict = {
            "has_tables": flags.has_tables,
            "tables_likely_corrupted": flags.tables_likely_corrupted,
            "has_math": flags.has_math,
            "math_preserved": flags.math_preserved,
            "has_figures": flags.has_figures,
            "figure_captions_present": flags.figure_captions_present,
            "heading_structure_detected": flags.heading_structure_detected,
        }
        json_str = json.dumps(flags_dict)
        parsed = json.loads(json_str)

        # Verify all 7 keys present
        assert len(parsed) == 7
        assert "has_tables" in parsed
        assert "tables_likely_corrupted" in parsed
        assert "has_math" in parsed
        assert "math_preserved" in parsed
        assert "has_figures" in parsed
        assert "figure_captions_present" in parsed
        assert "heading_structure_detected" in parsed

    def test_partial_flags_leave_others_at_defaults(self) -> None:
        """Given only some flags set, when created, then unset flags remain False."""
        flags = QualityFlags(has_tables=True, heading_structure_detected=True)
        assert flags.has_tables is True
        assert flags.heading_structure_detected is True
        # Others remain False
        assert flags.tables_likely_corrupted is False
        assert flags.has_math is False
        assert flags.math_preserved is False
        assert flags.has_figures is False
        assert flags.figure_captions_present is False

    def test_all_flags_can_be_set_to_true(self) -> None:
        """Given all flags set to True, when created, then all are True."""
        flags = QualityFlags(
            has_tables=True,
            tables_likely_corrupted=True,
            has_math=True,
            math_preserved=True,
            has_figures=True,
            figure_captions_present=True,
            heading_structure_detected=True,
        )
        assert flags.has_tables is True
        assert flags.tables_likely_corrupted is True
        assert flags.has_math is True
        assert flags.math_preserved is True
        assert flags.has_figures is True
        assert flags.figure_captions_present is True
        assert flags.heading_structure_detected is True

    def test_high_quality_extraction_flags(self) -> None:
        """Given high-quality extraction (JATS), when flags set, then positive indicators True."""
        flags = QualityFlags(
            has_tables=True,
            tables_likely_corrupted=False,
            has_math=True,
            math_preserved=True,
            has_figures=True,
            figure_captions_present=True,
            heading_structure_detected=True,
        )
        # High quality: content present and preserved
        assert flags.has_tables and not flags.tables_likely_corrupted
        assert flags.has_math and flags.math_preserved
        assert flags.has_figures and flags.figure_captions_present
        assert flags.heading_structure_detected

    def test_low_quality_extraction_flags(self) -> None:
        """Given low-quality extraction (scanned PDF), when flags set, then corruption flags True."""
        flags = QualityFlags(
            has_tables=True,
            tables_likely_corrupted=True,
            has_math=True,
            math_preserved=False,
            heading_structure_detected=False,
        )
        # Low quality: content present but corrupted/missing
        assert flags.has_tables and flags.tables_likely_corrupted
        assert flags.has_math and not flags.math_preserved
        assert not flags.heading_structure_detected
