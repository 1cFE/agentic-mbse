"""Tests for agentic_mbse.extraction.table_repair module."""

from __future__ import annotations

from unittest.mock import MagicMock

from agentic_mbse.extraction.table_repair import find_broken_tables, repair_tables

# ---------------------------------------------------------------------------
# find_broken_tables
# ---------------------------------------------------------------------------


class TestFindBrokenTables:
    def test_detects_extra_column(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 | 3 |"
        broken = find_broken_tables(md)
        assert len(broken) == 1

    def test_detects_missing_column(self):
        md = "| A | B | C |\n|---|---|---|\n| 1 |"
        broken = find_broken_tables(md)
        assert len(broken) == 1

    def test_skips_valid_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        broken = find_broken_tables(md)
        assert len(broken) == 0

    def test_handles_multiple_tables(self):
        md = (
            "Some text\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
            "More text\n\n"
            "| X | Y | Z |\n|---|---|---|\n| 1 | 2 |\n"
        )
        broken = find_broken_tables(md)
        assert len(broken) == 1  # only the second table is broken

    def test_handles_no_tables(self):
        md = "# Heading\n\nJust some text with no tables."
        broken = find_broken_tables(md)
        assert len(broken) == 0

    def test_handles_empty_string(self):
        broken = find_broken_tables("")
        assert len(broken) == 0

    def test_table_with_no_separator_row(self):
        # A table block of pipe-lines without a separator row is still
        # considered a table block, but it's malformed (no separator).
        md = "| A | B |\n| 1 | 2 |"
        broken = find_broken_tables(md)
        assert len(broken) == 1  # no separator = broken

    def test_returns_table_text(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 | 3 |"
        broken = find_broken_tables(md)
        assert len(broken) == 1
        assert "| A | B |" in broken[0]
        assert "| 1 | 2 | 3 |" in broken[0]

    def test_valid_table_with_empty_cells(self):
        md = "| A | B |\n|---|---|\n|   |   |"
        broken = find_broken_tables(md)
        assert len(broken) == 0


# ---------------------------------------------------------------------------
# repair_tables
# ---------------------------------------------------------------------------


class TestRepairTables:
    def test_repair_calls_claude(self, tmp_path, monkeypatch):
        import agentic_mbse.extraction.table_repair as mod

        md_path = tmp_path / "full_document.md"
        md_path.write_text(
            "Some text\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 | 3 |\n\n"
            "More text\n"
        )

        # Mock subprocess.run for claude -p
        fixed_table = "| A | B |\n|---|---|\n| 1 | 2 |"

        def fake_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = fixed_table
            return result

        monkeypatch.setattr(mod.subprocess, "run", fake_run)

        repaired = repair_tables(md_path)
        assert repaired is True

        content = md_path.read_text()
        assert "| 1 | 2 | 3 |" not in content
        assert "| 1 | 2 |" in content

    def test_no_repair_when_all_valid(self, tmp_path):
        md_path = tmp_path / "full_document.md"
        md_path.write_text("| A | B |\n|---|---|\n| 1 | 2 |")

        repaired = repair_tables(md_path)
        assert repaired is False

    def test_no_repair_when_no_tables(self, tmp_path):
        md_path = tmp_path / "full_document.md"
        md_path.write_text("# Heading\n\nJust text, no tables here.")

        repaired = repair_tables(md_path)
        assert repaired is False

    def test_repair_handles_claude_failure(self, tmp_path, monkeypatch):
        import agentic_mbse.extraction.table_repair as mod

        md_path = tmp_path / "full_document.md"
        original = "Some text\n\n| A | B |\n|---|---|\n| 1 | 2 | 3 |\n\nMore text\n"
        md_path.write_text(original)

        def failing_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "claude not found"
            return result

        monkeypatch.setattr(mod.subprocess, "run", failing_run)

        repaired = repair_tables(md_path)
        # When claude fails, no replacement happens
        assert repaired is False
        assert md_path.read_text() == original

    def test_repair_handles_missing_claude(self, tmp_path, monkeypatch):
        import agentic_mbse.extraction.table_repair as mod

        md_path = tmp_path / "full_document.md"
        original = "| A | B |\n|---|---|\n| 1 | 2 | 3 |"
        md_path.write_text(original)

        def raise_not_found(cmd, **kwargs):
            raise FileNotFoundError("claude not found")

        monkeypatch.setattr(mod.subprocess, "run", raise_not_found)

        repaired = repair_tables(md_path)
        assert repaired is False
        assert md_path.read_text() == original
