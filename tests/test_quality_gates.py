"""Tests for agentic_mbse.extraction.quality_gates module."""

from agentic_mbse.extraction.quality_gates import (
    detect_broken_tables,
    detect_garbled_equations,
    detect_problems,
)

# ---------------------------------------------------------------------------
# detect_broken_tables
# ---------------------------------------------------------------------------


class TestDetectBrokenTables:
    def test_valid_table_not_flagged(self):
        md = "| Header 1 | Header 2 |\n| --- | --- |\n| cell 1 | cell 2 |\n"
        assert detect_broken_tables(md) == []

    def test_inconsistent_columns_flagged(self):
        md = "| Header 1 | Header 2 |\n| --- | --- |\n| cell 1 | cell 2 | extra |\n"
        results = detect_broken_tables(md)
        assert len(results) == 1
        assert results[0].region_type == "table"
        assert results[0].confidence == 0.9

    def test_missing_separator_flagged(self):
        md = "| Header 1 | Header 2 |\n| cell 1 | cell 2 |\n"
        results = detect_broken_tables(md)
        assert len(results) == 1

    def test_non_pipe_table_near_caption(self):
        md = (
            "Table 1: Material Properties\n"
            "\n"
            "Material     Density     Strength\n"
            "Steel        7850        400\n"
            "Aluminum     2700        300\n"
        )
        results = detect_broken_tables(md)
        assert len(results) == 1
        assert results[0].confidence == 0.8

    def test_no_tables_empty_result(self):
        md = "Just some plain text with no tables at all.\n\nAnother paragraph."
        assert detect_broken_tables(md) == []

    def test_line_numbers_correct(self):
        md = "Preamble\n\n| A | B |\n| 1 | 2 |\n\nMore text\n"
        results = detect_broken_tables(md)
        assert len(results) == 1
        assert results[0].markdown_lines == (2, 4)


# ---------------------------------------------------------------------------
# detect_garbled_equations
# ---------------------------------------------------------------------------


class TestDetectGarbledEquations:
    def test_replacement_chars_detected(self):
        md = "The LCOE is \ufffd\ufffd\ufffd\ufffd per MWh."
        results = detect_garbled_equations(md)
        assert len(results) == 1
        assert results[0].region_type == "equation"
        assert results[0].confidence == 0.9

    def test_bracket_soup_detected(self):
        md = "Energy balance: _[C][AC][Tp]_ equation"
        results = detect_garbled_equations(md)
        assert len(results) == 1
        assert results[0].region_type == "equation"
        assert results[0].confidence == 0.7

    def test_clean_text_not_flagged(self):
        md = "Normal text with no garbled equations or special characters."
        assert detect_garbled_equations(md) == []

    def test_single_replacement_char_not_flagged(self):
        """A single U+FFFD is not a cluster."""
        md = "A single \ufffd replacement character."
        assert detect_garbled_equations(md) == []

    def test_context_lines_included(self):
        md = (
            "Line 0\n"
            "Line 1\n"
            "Line 2\n"
            "The equation \ufffd\ufffd\ufffd\ufffd is garbled\n"
            "Line 4\n"
            "Line 5\n"
        )
        results = detect_garbled_equations(md)
        assert len(results) == 1
        # Should include 2 lines before and 2 after
        assert results[0].markdown_lines[0] <= 1
        assert results[0].markdown_lines[1] >= 5


# ---------------------------------------------------------------------------
# detect_problems (orchestrator)
# ---------------------------------------------------------------------------


class TestDetectProblems:
    def test_combines_detectors(self):
        md = "| A | B |\n| 1 | 2 |\n\nGarbled: \ufffd\ufffd\ufffd\ufffd stuff\n"
        results = detect_problems(md)
        assert len(results) == 2
        types = {r.region_type for r in results}
        assert "table" in types
        assert "equation" in types

    def test_sorted_by_confidence_descending(self):
        md = "| A | B |\n| 1 | 2 |\n\nGarbled: \ufffd\ufffd\ufffd\ufffd stuff\n"
        results = detect_problems(md)
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_clean_markdown_empty_result(self):
        md = (
            "# Title\n"
            "\n"
            "Normal paragraph with no issues.\n"
            "\n"
            "| Header | Data |\n"
            "| --- | --- |\n"
            "| value | 42 |\n"
        )
        assert detect_problems(md) == []
