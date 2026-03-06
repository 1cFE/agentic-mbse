"""Tests for tables module — utilities, filtering, quality assessment,
ensemble detection, and Claude enhancement."""

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_mbse.extraction.tables import (
    _count_data_rows,
    _is_separator_row,
    _is_table_row,
    assess_table_quality,
    count_pipe_rows,
    detect_tables_ensemble,
    enhance_table_with_claude,
    filter_tables,
    has_br_in_tables,
    has_col_headers,
    insert_tables_at_end,
    replace_tables,
    strip_pipe_tables,
)
from agentic_mbse.extraction.types import CostRecord, DetectedTable

# ---------------------------------------------------------------------------
# Phase 2: Utilities, Filter, Quality Assessment
# ---------------------------------------------------------------------------


class TestIsTableRow:
    def test_real_table_row(self):
        assert _is_table_row("| a | b |")

    def test_separator_row(self):
        assert _is_table_row("|---|---|")

    def test_not_table_row_no_leading_pipe(self):
        assert not _is_table_row("text with | pipe | chars")

    def test_not_table_row_single_pipe(self):
        assert not _is_table_row("| only one pipe")

    def test_empty_line(self):
        assert not _is_table_row("")

    def test_equation_bar(self):
        assert not _is_table_row("where v|| is the parallel velocity")


class TestIsSeparatorRow:
    def test_simple_separator(self):
        assert _is_separator_row("|---|---|")

    def test_separator_with_colons(self):
        assert _is_separator_row("| :--- | ---: | :---: |")

    def test_separator_with_spaces(self):
        assert _is_separator_row("|  ---  |  ---  |")

    def test_data_row_not_separator(self):
        assert not _is_separator_row("| a | b |")

    def test_empty_not_separator(self):
        assert not _is_separator_row("")


class TestCountDataRows:
    def test_standard_table(self):
        # header + separator + 2 data rows = 2 data rows
        md = "| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        assert _count_data_rows(md) == 2

    def test_no_separator(self):
        # 3 rows, no separator → all are data (0 separators, subtract 0*2)
        md = "| a | b |\n| 1 | 2 |\n| 3 | 4 |"
        assert _count_data_rows(md) == 3

    def test_header_only(self):
        # header + separator, no data
        md = "| a | b |\n|---|---|"
        assert _count_data_rows(md) == 0

    def test_empty_string(self):
        assert _count_data_rows("") == 0

    def test_no_tables(self):
        assert _count_data_rows("just text\nno tables") == 0

    def test_single_data_row(self):
        md = "| Name | Age |\n|---|---|\n| Alice | 30 |"
        assert _count_data_rows(md) == 1


class TestCountPipeRows:
    def test_simple_table(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |"
        assert count_pipe_rows(md) == 3

    def test_no_tables(self):
        assert count_pipe_rows("Just some text\nNo tables here") == 0

    def test_mixed_content(self):
        md = "Text\n| a | b |\n|---|---|\nMore text"
        assert count_pipe_rows(md) == 2


class TestHasBrInTables:
    def test_br_present(self):
        md = "| cell with <br> break | other |"
        assert has_br_in_tables(md)

    def test_no_br(self):
        md = "| clean | table |\n|---|---|\n| 1 | 2 |"
        assert not has_br_in_tables(md)

    def test_br_outside_table(self):
        md = "text with <br> but no table rows"
        assert not has_br_in_tables(md)


class TestHasColHeaders:
    def test_col_headers_present(self):
        md = "| Col1 | Col2 | Col3 |\n|---|---|---|"
        assert has_col_headers(md)

    def test_no_col_headers(self):
        md = "| Name | Age |\n|---|---|"
        assert not has_col_headers(md)

    def test_col_in_text_not_table(self):
        md = "Col1 appears in text but not in a table row"
        assert not has_col_headers(md)


class TestStripPipeTables:
    def test_strip_simple_table(self):
        md = "Text before\n| a | b |\n|---|---|\n| 1 | 2 |\n\nText after"
        result = strip_pipe_tables(md)
        assert "| a |" not in result
        assert "Text before" in result
        assert "Text after" in result

    def test_preserve_non_table_content(self):
        md = "# Heading\n\nParagraph text\n\n## Another heading"
        result = strip_pipe_tables(md)
        assert result == md

    def test_strip_multiple_tables(self):
        md = (
            "Text\n| a | b |\n|---|---|\n\n"
            "Middle\n| c | d |\n|---|---|\n\nEnd"
        )
        result = strip_pipe_tables(md)
        assert "| a |" not in result
        assert "| c |" not in result
        assert "Middle" in result

    def test_preserve_equation_bars(self):
        md = "where v|| represents the parallel component\n| a | b |\n|---|---|"
        result = strip_pipe_tables(md)
        assert "v||" in result


class TestInsertTablesAtEnd:
    def test_single_table(self):
        page_md = "Some page content"
        tables = [
            DetectedTable(
                markdown="| a | b |\n|---|---|\n| 1 | 2 |",
                confidence=1.0,
                num_rows=1,
                num_cols=2,
                avg_cell_length=3.0,
            )
        ]
        result = insert_tables_at_end(page_md, tables)
        assert result.startswith("Some page content")
        assert "| a | b |" in result

    def test_multiple_tables(self):
        page_md = "Content"
        tables = [
            DetectedTable("| t1 |", 1.0, 1, 1, 2.0),
            DetectedTable("| t2 |", 1.0, 1, 1, 2.0),
        ]
        result = insert_tables_at_end(page_md, tables)
        assert "| t1 |" in result
        assert "| t2 |" in result

    def test_empty_tables_list(self):
        result = insert_tables_at_end("Content", [])
        assert result == "Content"


class TestReplaceTables:
    def test_replace_existing_table(self):
        md = "Text\n| old | table |\n|---|---|\n| x | y |\n\nMore text"
        tables = [
            DetectedTable(
                markdown="| new | data |\n|---|---|\n| 1 | 2 |",
                confidence=1.0,
                num_rows=1,
                num_cols=2,
                avg_cell_length=3.0,
            )
        ]
        result = replace_tables(md, tables)
        assert "| old |" not in result
        assert "| new | data |" in result
        assert "Text" in result
        assert "More text" in result


class TestFilterTables:
    def test_no_confidence_filter(self):
        """Low-confidence tables MUST pass (no confidence filter in production)."""
        t = DetectedTable(
            markdown="| a | b |\n|---|---|\n| 1 | 2 |",
            confidence=0.92,
            num_rows=3,
            num_cols=2,
            avg_cell_length=10.0,
        )
        kept, reasons = filter_tables([t])
        assert len(kept) == 1

    def test_prose_rejected(self):
        t = DetectedTable(
            markdown="| long prose cell... |",
            confidence=1.0,
            num_rows=3,
            num_cols=2,
            avg_cell_length=85.0,
        )
        kept, reasons = filter_tables([t])
        assert len(kept) == 0
        assert any("prose" in r.lower() for r in reasons)

    def test_layout_artifact_rejected(self):
        t = DetectedTable(
            markdown="| a | b | c | d | e |",
            confidence=1.0,
            num_rows=1,
            num_cols=5,
            avg_cell_length=5.0,
        )
        kept, reasons = filter_tables([t])
        assert len(kept) == 0
        assert any("layout artifact" in r.lower() for r in reasons)

    def test_extraction_failed_passes_through(self):
        t = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            extraction_failed=True,
            image_path=Path("/tmp/t.png"),
        )
        kept, reasons = filter_tables([t])
        assert len(kept) == 1
        assert any("extraction_failed" in r for r in reasons)

    def test_good_table_kept(self):
        t = DetectedTable(
            markdown="| a | b |\n|---|---|\n| 1 | 2 |",
            confidence=0.99,
            num_rows=3,
            num_cols=2,
            avg_cell_length=5.0,
        )
        kept, reasons = filter_tables([t])
        assert len(kept) == 1
        assert any("KEEP" in r for r in reasons)

    def test_mixed_tables(self):
        good = DetectedTable("| a |", 1.0, 3, 2, 5.0)
        prose = DetectedTable("| long... |", 1.0, 3, 2, 100.0)
        failed = DetectedTable(
            "", 1.0, 0, 0, 0.0, extraction_failed=True,
            image_path=Path("/tmp/t.png"),
        )
        kept, reasons = filter_tables([good, prose, failed])
        assert len(kept) == 2  # good + failed


class TestAssessTableQuality:
    def test_extraction_failed_triggers_enhancement(self):
        t = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            extraction_failed=True,
            image_path=Path("/tmp/t.png"),
        )
        needs, reasons = assess_table_quality(t)
        assert needs
        assert any("failed" in r.lower() for r in reasons)

    def test_good_table_no_enhancement(self):
        t = DetectedTable(
            markdown="| a | b |\n|---|---|\n| 1 | 2 |",
            confidence=1.0,
            num_rows=3,
            num_cols=2,
            avg_cell_length=3.0,
            image_path=Path("/tmp/t.png"),
        )
        needs, reasons = assess_table_quality(t)
        assert not needs

    def test_no_image_cant_enhance(self):
        t = DetectedTable(
            markdown="| a | b |",
            confidence=1.0,
            num_rows=1,
            num_cols=2,
            avg_cell_length=3.0,
            image_path=None,
        )
        needs, reasons = assess_table_quality(t)
        assert not needs

    def test_suspect_few_rows_triggers(self):
        t = DetectedTable(
            markdown="| a | b | c |",
            confidence=1.0,
            num_rows=1,
            num_cols=3,
            avg_cell_length=3.0,
            image_path=Path("/tmp/t.png"),
        )
        needs, reasons = assess_table_quality(t)
        assert needs
        assert any("suspect" in r.lower() for r in reasons)


# ---------------------------------------------------------------------------
# Phase 3: Detection and Enhancement
# ---------------------------------------------------------------------------


class TestDetectTablesEnsemble:
    @patch("agentic_mbse.extraction.tables._detect_docling", return_value={})
    @patch("agentic_mbse.extraction.tables._detect_img2table")
    @patch("agentic_mbse.extraction.tables._detect_gmft")
    def test_ensemble_calls_gmft_first(
        self, mock_gmft, mock_img2, mock_docling
    ):
        gmft_table = DetectedTable(
            "| a | b |", 0.99, 3, 2, 5.0, detector="gmft"
        )
        mock_gmft.return_value = {0: [gmft_table]}
        mock_img2.return_value = {}

        result = detect_tables_ensemble(Path("fake.pdf"))

        mock_gmft.assert_called_once()
        mock_img2.assert_called_once()
        # Img2Table receives page 0 in gmft_pages set
        call_args = mock_img2.call_args
        assert 0 in call_args[0][1]  # gmft_pages arg
        assert 0 in result
        assert result[0][0].detector == "gmft"

    @patch("agentic_mbse.extraction.tables._detect_docling", return_value={})
    @patch("agentic_mbse.extraction.tables._detect_img2table")
    @patch("agentic_mbse.extraction.tables._detect_gmft")
    def test_img2table_fills_gaps(self, mock_gmft, mock_img2, mock_docling):
        mock_gmft.return_value = {0: [DetectedTable("| a |", 1.0, 1, 1, 2.0)]}
        img2_table = DetectedTable(
            "| x | y |", 1.0, 2, 2, 3.0, detector="img2table"
        )
        mock_img2.return_value = {2: [img2_table]}

        result = detect_tables_ensemble(Path("fake.pdf"))

        assert 0 in result  # from GMFT
        assert 2 in result  # from Img2Table

    @patch("agentic_mbse.extraction.tables._detect_docling", return_value={})
    @patch("agentic_mbse.extraction.tables._detect_img2table")
    @patch("agentic_mbse.extraction.tables._detect_gmft")
    def test_img2table_disabled(self, mock_gmft, mock_img2, mock_docling):
        mock_gmft.return_value = {}

        detect_tables_ensemble(
            Path("fake.pdf"), enable_img2table=False
        )

        mock_img2.assert_not_called()


class TestDetectGmftGraceful:
    def test_gmft_not_installed(self):
        """ImportError for GMFT → returns empty dict."""
        with patch.dict("sys.modules", {
            "gmft.auto": None,
            "gmft.pdf_bindings.pdfium": None,
        }):
            from agentic_mbse.extraction import tables
            # Force reimport of the function to trigger ImportError
            result = tables._detect_gmft(Path("fake.pdf"))
            assert result == {}


class TestDetectImg2tableGraceful:
    def test_img2table_not_installed(self):
        """ImportError for Img2Table → returns empty dict."""
        with patch.dict("sys.modules", {
            "gmft.detectors.img2table": None,
        }):
            from agentic_mbse.extraction import tables
            result = tables._detect_img2table(Path("fake.pdf"), set())
            assert result == {}


class TestEnhanceTableWithClaude:
    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    def test_successful_extraction(self, mock_claude):
        mock_claude.return_value = {
            "result": "| a | b |\n|---|---|\n| 1 | 2 |",
            "total_cost_usd": 0.05,
            "usage": {"input_tokens": 2000, "output_tokens": 100},
            "model": "sonnet",
        }
        table = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=2,
            avg_cell_length=0.0,
            image_path=Path("/tmp/t.png"),
            extraction_failed=True,
        )

        enhanced, cost = enhance_table_with_claude(table)

        assert enhanced.source == "claude_cropped"
        assert enhanced.markdown != ""
        assert "| a | b |" in enhanced.markdown
        assert enhanced.num_rows == 1  # 1 data row (header + sep excluded)
        assert isinstance(cost, CostRecord)
        assert cost.cost_usd == 0.05

    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    def test_empty_response_marks_false_positive(self, mock_claude):
        mock_claude.return_value = {
            "result": "",
            "total_cost_usd": 0.03,
            "usage": {"input_tokens": 2000, "output_tokens": 10},
            "model": "sonnet",
        }
        table = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            image_path=Path("/tmp/t.png"),
            extraction_failed=True,
        )

        enhanced, cost = enhance_table_with_claude(table)

        assert enhanced.markdown == ""  # FP filter signal
        assert enhanced.source == "claude_cropped"

    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    def test_no_table_rows_marks_false_positive(self, mock_claude):
        """Claude returns text but no pipe table → FP signal."""
        mock_claude.return_value = {
            "result": "This image shows a chart, not a table.",
            "total_cost_usd": 0.04,
            "usage": {"input_tokens": 2000, "output_tokens": 50},
            "model": "sonnet",
        }
        table = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            image_path=Path("/tmp/t.png"),
            extraction_failed=True,
        )

        enhanced, cost = enhance_table_with_claude(table)

        assert enhanced.markdown == ""

    def test_no_image_path_raises(self):
        table = DetectedTable(
            markdown="",
            confidence=1.0,
            num_rows=0,
            num_cols=0,
            avg_cell_length=0.0,
            image_path=None,
        )

        with pytest.raises(ValueError, match="image_path"):
            enhance_table_with_claude(table)
