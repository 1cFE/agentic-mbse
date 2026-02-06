"""Tests for agentic_mbse.extraction.ai_repair module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_mbse.extraction.ai_repair import (
    build_repair_prompt,
    cross_validate_numbers,
    extract_numbers,
    repair_document,
    repair_region,
)
from agentic_mbse.extraction.base import RepairRequest

# ---------------------------------------------------------------------------
# extract_numbers
# ---------------------------------------------------------------------------


class TestExtractNumbers:
    def test_integers(self):
        assert extract_numbers("There are 42 items and 7 groups") == {"42", "7"}

    def test_decimals(self):
        nums = extract_numbers("Temperature: 3.14 K, pressure: 0.5 MPa")
        assert "3.14" in nums
        assert "0.5" in nums

    def test_scientific_notation(self):
        nums = extract_numbers("Mass: 1.5e10 kg and 2.3E-4 mol")
        assert "1.5e+10" in nums or "15000000000" in nums
        assert "0.00023" in nums

    def test_negative_numbers(self):
        nums = extract_numbers("Temperature: -273.15 C")
        assert "-273.15" in nums

    def test_leading_dot_decimal(self):
        nums = extract_numbers("Value is .5 units")
        assert "0.5" in nums

    def test_no_numbers(self):
        assert extract_numbers("No numbers here") == set()

    def test_mixed_content(self):
        nums = extract_numbers("Table 1: LCOE = $47.50/MWh with 0.92 capacity factor")
        assert "1" in nums
        assert "47.5" in nums or "47.50" in nums
        assert "0.92" in nums

    def test_normalization_trailing_zeros(self):
        """3.140 and 3.14 should normalize to the same value."""
        a = extract_numbers("value is 3.140")
        b = extract_numbers("value is 3.14")
        assert a == b


# ---------------------------------------------------------------------------
# cross_validate_numbers
# ---------------------------------------------------------------------------


class TestCrossValidateNumbers:
    def test_matching_sets_accept(self):
        accept, warnings = cross_validate_numbers(
            "Values: 42, 3.14, 100",
            "Values: 42, 3.14, 100",
        )
        assert accept is True
        assert warnings == []

    def test_missing_numbers_reject(self):
        accept, warnings = cross_validate_numbers(
            "Values: 42, 3.14, 100",
            "Values: 42, 3.14",
        )
        assert accept is False
        assert len(warnings) == 1
        assert "100" in warnings[0]

    def test_extra_numbers_accept(self):
        """Repair found more numbers — that's fine."""
        accept, warnings = cross_validate_numbers(
            "Values: 42, 3.14",
            "Values: 42, 3.14, 100, 200",
        )
        assert accept is True
        assert warnings == []

    def test_empty_original_accept(self):
        accept, warnings = cross_validate_numbers("", "New data: 42")
        assert accept is True

    def test_both_empty_accept(self):
        accept, warnings = cross_validate_numbers("No numbers", "Also no numbers")
        assert accept is True


# ---------------------------------------------------------------------------
# build_repair_prompt
# ---------------------------------------------------------------------------


class TestBuildRepairPrompt:
    def test_table_prompt(self):
        req = RepairRequest(
            page_num=5,
            region_type="table",
            markdown_lines=(10, 20),
            original_text="| broken | table",
            confidence=0.9,
        )
        prompt = build_repair_prompt(req)
        assert "pipe table" in prompt.lower()
        assert "| broken | table" in prompt

    def test_equation_prompt(self):
        req = RepairRequest(
            page_num=3,
            region_type="equation",
            markdown_lines=(5, 8),
            original_text="garbled \ufffd\ufffd",
            confidence=0.9,
        )
        prompt = build_repair_prompt(req)
        assert "latex" in prompt.lower()

    def test_structure_prompt(self):
        req = RepairRequest(
            page_num=1,
            region_type="structure",
            markdown_lines=(0, 5),
            original_text="**1 Intro**",
            confidence=0.5,
        )
        prompt = build_repair_prompt(req)
        assert "heading" in prompt.lower()


# ---------------------------------------------------------------------------
# repair_region
# ---------------------------------------------------------------------------


class TestRepairRegion:
    @patch("agentic_mbse.extraction.ai_repair.render_page_image")
    @patch("agentic_mbse.extraction.ai_repair.subprocess.run")
    def test_successful_table_repair(self, mock_run, mock_render):
        mock_render.return_value = Path("/tmp/test_page.png")
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="| Fixed | Table |\n| --- | --- |\n| 42 | 3.14 |",
        )

        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(0, 3),
            original_text="| broken 42 3.14",
            confidence=0.9,
        )
        repaired, warnings = repair_region(req, Path("test.pdf"))
        assert repaired is not None
        assert "| Fixed | Table |" in repaired

    @patch("agentic_mbse.extraction.ai_repair.render_page_image")
    @patch("agentic_mbse.extraction.ai_repair.subprocess.run")
    def test_cross_validation_rejects_missing_number(self, mock_run, mock_render):
        mock_render.return_value = Path("/tmp/test_page.png")
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="| Col |\n| --- |\n| 99 |",  # Missing 42 from original
        )

        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(0, 3),
            original_text="| value 42 |",
            confidence=0.9,
        )
        repaired, warnings = repair_region(req, Path("test.pdf"))
        assert repaired is None
        assert any("Cross-validation" in w for w in warnings)

    @patch("agentic_mbse.extraction.ai_repair.render_page_image")
    def test_render_failure_returns_none(self, mock_render):
        mock_render.side_effect = RuntimeError("page out of range")

        req = RepairRequest(
            page_num=999,
            region_type="table",
            markdown_lines=(0, 3),
            original_text="broken",
            confidence=0.9,
        )
        repaired, warnings = repair_region(req, Path("test.pdf"))
        assert repaired is None
        assert any("render" in w.lower() for w in warnings)


# ---------------------------------------------------------------------------
# repair_document
# ---------------------------------------------------------------------------


class TestRepairDocument:
    @patch("agentic_mbse.extraction.ai_repair.repair_region")
    def test_successful_splice(self, mock_repair):
        mock_repair.return_value = ("| Fixed | Table |\n| --- | --- |", [])

        md = "Before\nbroken table\nAfter"
        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 2),
            original_text="broken table",
            confidence=0.9,
        )
        result_md, meta = repair_document(md, Path("test.pdf"), [req])
        assert "| Fixed | Table |" in result_md
        assert "Before" in result_md
        assert "After" in result_md
        assert meta["repairs"] == 1
        assert meta["rejections"] == 0

    @patch("agentic_mbse.extraction.ai_repair.repair_region")
    def test_rejection_inserts_comment(self, mock_repair):
        mock_repair.return_value = (None, ["Number mismatch"])

        md = "Before\nbroken table\nAfter"
        req = RepairRequest(
            page_num=0,
            region_type="table",
            markdown_lines=(1, 2),
            original_text="broken table",
            confidence=0.9,
        )
        result_md, meta = repair_document(md, Path("test.pdf"), [req])
        assert "<!-- AI repair flagged" in result_md
        assert meta["rejections"] == 1
        assert meta["repairs"] == 0

    def test_empty_requests_noop(self):
        md = "Unchanged text"
        result_md, meta = repair_document(md, Path("test.pdf"), [])
        assert result_md == md
        assert meta["repairs"] == 0

    @patch("agentic_mbse.extraction.ai_repair.repair_region")
    def test_max_pages_limits_repairs(self, mock_repair):
        mock_repair.return_value = ("fixed", [])

        md = "Line0\nLine1\nLine2\nLine3\nLine4"
        reqs = [
            RepairRequest(0, "table", (1, 2), "broken1", 0.9),
            RepairRequest(1, "table", (3, 4), "broken2", 0.8),
        ]
        _, meta = repair_document(md, Path("test.pdf"), reqs, max_pages=1)
        assert meta["repairs"] == 1
