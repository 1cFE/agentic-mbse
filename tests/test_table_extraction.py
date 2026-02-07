"""Tests for agentic_mbse.extraction.table_extraction module."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.base import RepairRequest
from agentic_mbse.extraction.table_extraction import (
    dataframe_to_pipe_table,
    enhance_tables,
    is_gmft_available,
)

# ---------------------------------------------------------------------------
# dataframe_to_pipe_table
# ---------------------------------------------------------------------------


class TestDataframeToPipeTable:
    def test_basic_conversion(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [30, 25]})
        result = dataframe_to_pipe_table(df)
        assert "| Name | Age |" in result
        assert "| --- | --- |" in result
        assert "| Alice | 30 |" in result
        assert "| Bob | 25 |" in result

    def test_empty_dataframe(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame()
        assert dataframe_to_pipe_table(df) == ""

    def test_handles_nan_values(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"A": [1, None], "B": ["x", "y"]})
        result = dataframe_to_pipe_table(df)
        assert "| 1 | x |" in result
        assert "|  | y |" in result

    def test_single_column(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"Value": [10, 20, 30]})
        result = dataframe_to_pipe_table(df)
        lines = result.strip().split("\n")
        assert len(lines) == 5  # header + separator + 3 rows

    def test_numeric_columns(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"X": [1.5, 2.7], "Y": [3.14, 0.0]})
        result = dataframe_to_pipe_table(df)
        assert "1.5" in result
        assert "3.14" in result


# ---------------------------------------------------------------------------
# is_gmft_available
# ---------------------------------------------------------------------------


class TestIsGmftAvailable:
    def test_returns_false_when_not_installed(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "gmft":
                raise ImportError("No module named 'gmft'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        assert is_gmft_available() is False

    def test_returns_true_when_installed(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "gmft":
                return MagicMock()
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        assert is_gmft_available() is True


# ---------------------------------------------------------------------------
# enhance_tables
# ---------------------------------------------------------------------------


class TestEnhanceTables:
    def test_empty_requests_returns_unchanged(self):
        md = "Some markdown text."
        result_md, remaining = enhance_tables(md, MagicMock(), [])
        assert result_md == md
        assert remaining == []

    def test_non_table_requests_passed_through(self):
        md = "Some text"
        req = RepairRequest(
            page_num=0,
            region_type="equation",
            markdown_lines=(0, 1),
            original_text="garbled",
            confidence=0.9,
        )
        result_md, remaining = enhance_tables(md, MagicMock(), [req])
        assert len(remaining) == 1
        assert remaining[0].region_type == "equation"

    @patch("agentic_mbse.extraction.table_extraction.extract_tables_from_page")
    def test_replaces_broken_table(self, mock_extract):
        pd = pytest.importorskip("pandas")
        mock_df = pd.DataFrame({"Col1": ["a", "b"], "Col2": [1, 2]})
        mock_extract.return_value = [mock_df]

        md = "Before\n| broken | table\n| missing sep\nAfter"
        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 3),
            original_text="| broken | table\n| missing sep",
            confidence=0.9,
        )
        result_md, remaining = enhance_tables(md, MagicMock(), [req])
        assert "| Col1 | Col2 |" in result_md
        assert "| --- | --- |" in result_md
        assert remaining == []

    @patch("agentic_mbse.extraction.table_extraction.extract_tables_from_page")
    def test_gmft_failure_passes_to_remaining(self, mock_extract):
        mock_extract.return_value = []

        md = "Before\n| broken\nAfter"
        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 2),
            original_text="| broken",
            confidence=0.9,
        )
        result_md, remaining = enhance_tables(md, MagicMock(), [req])
        assert len(remaining) == 1

    @patch("agentic_mbse.extraction.table_extraction.extract_tables_from_page")
    def test_gmft_exception_passes_to_remaining(self, mock_extract):
        mock_extract.side_effect = RuntimeError("GMFT crashed")

        md = "Before\n| broken\nAfter"
        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 2),
            original_text="| broken",
            confidence=0.9,
        )
        result_md, remaining = enhance_tables(md, MagicMock(), [req])
        assert len(remaining) == 1

    @patch("agentic_mbse.extraction.table_extraction.extract_tables_from_page")
    def test_overlapping_repair_requests_dont_corrupt(self, mock_extract):
        """Two requests with overlapping markdown_lines should not corrupt output.

        When GMFT fixes one table, the other overlapping request should
        still reference valid content (even if indices shift). This test
        verifies that the output contains both fixed tables or at least
        does not lose content.
        """
        pd = pytest.importorskip("pandas")
        df1 = pd.DataFrame({"A": [1], "B": [2]})
        df2 = pd.DataFrame({"X": [10], "Y": [20]})
        mock_extract.side_effect = [[df1], [df2]]

        md = "Before\n| broken1\n| broken2\n| broken3\nAfter"
        req1 = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 3),
            original_text="| broken1\n| broken2",
            confidence=0.9,
        )
        req2 = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(2, 4),
            original_text="| broken2\n| broken3",
            confidence=0.8,
        )
        result_md, remaining = enhance_tables(md, MagicMock(), [req1, req2])
        # At minimum: no crash, "Before" and "After" preserved
        assert "Before" in result_md
        assert "After" in result_md
