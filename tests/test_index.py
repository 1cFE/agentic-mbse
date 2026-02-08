"""Tests for agentic_mbse.extraction.index — Phase 5."""

import subprocess

from agentic_mbse.extraction.index import (
    Section,
    build_hierarchy,
    format_index_md,
    generate_index,
    parse_index_sections,
    parse_sections,
    read_lines,
    read_section,
)

# ---------------------------------------------------------------------------
# parse_sections
# ---------------------------------------------------------------------------


class TestParseSections:
    def test_parses_numbered_headers(self):
        content = "## 1 Introduction\nText\n## 2 Methods\nMore text"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[0].section_num == "1"
        assert sections[0].title == "Introduction"
        assert sections[1].section_num == "2"

    def test_respects_max_depth(self):
        content = "## 1 Top\n### 1.1 Sub\n#### 1.1.1 Deep"
        sections = parse_sections(content, max_depth=2)
        assert len(sections) == 2  # excludes 1.1.1

    def test_calculates_line_ranges(self):
        content = "## 1 Intro\nLine 2\nLine 3\n## 2 Body\nLine 5"
        sections = parse_sections(content, max_depth=3)
        assert sections[0].line_start == 1
        assert sections[0].line_end == 3
        assert sections[1].line_start == 4
        assert sections[1].line_end == 5

    def test_extracts_content(self):
        content = "## 1 Intro\nHello world\n## 2 Body\nGoodbye"
        sections = parse_sections(content, max_depth=3)
        assert "Hello world" in sections[0].content

    def test_handles_bold_format(self):
        content = "### **7 Language**\nText\n### **7.2 Root**\nMore"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[0].section_num == "7"
        assert sections[0].title == "Language"

    def test_handles_empty_content(self):
        sections = parse_sections("", max_depth=3)
        assert sections == []

    def test_handles_no_sections(self):
        sections = parse_sections("Just plain text\nNo headers here", max_depth=3)
        assert sections == []

    def test_period_numbered_h2(self):
        content = "## 1. Introduction\nText\n## 2. Methods\nMore text"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[0].section_num == "1"
        assert sections[0].title == "Introduction"
        assert sections[1].section_num == "2"
        assert sections[1].title == "Methods"

    def test_period_numbered_subsections(self):
        content = "## 1. Top\n### 2.1. Background\nText"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[1].section_num == "2.1"
        assert sections[1].title == "Background"

    def test_mixed_period_and_bare(self):
        content = "## 1 Introduction\nText\n## 2. Methods\nText\n## 3 Results\nText"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 3
        assert sections[0].section_num == "1"
        assert sections[1].section_num == "2"
        assert sections[2].section_num == "3"

    # --- Unnumbered header fallback ---

    def test_unnumbered_headers_get_synthetic_nums(self):
        content = "## Overview\nText\n## Methods\nMore text"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[0].section_num == "1"
        assert sections[0].title == "Overview"
        assert sections[1].section_num == "2"
        assert sections[1].title == "Methods"

    def test_unnumbered_with_subsections(self):
        content = "## Introduction\nText\n### Background\nText\n### Prior Work\nText\n## Results\nText"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 4
        assert sections[0].section_num == "1"
        assert sections[1].section_num == "1.1"
        assert sections[1].title == "Background"
        assert sections[2].section_num == "1.2"
        assert sections[2].title == "Prior Work"
        assert sections[3].section_num == "2"

    def test_unnumbered_fallback_not_used_when_numbered_exist(self):
        """If ANY numbered header exists, the fallback never runs."""
        content = "## 1 Introduction\nText\n## Unnumbered\nText"
        sections = parse_sections(content, max_depth=3)
        # The numbered pattern matches "## 1 Introduction"; "## Unnumbered" doesn't match
        assert len(sections) == 1
        assert sections[0].section_num == "1"

    def test_unnumbered_respects_max_depth(self):
        content = "## Top\n### Sub\n#### Deep\n##### TooDeep"
        sections = parse_sections(content, max_depth=2)
        assert len(sections) == 2
        assert sections[0].section_num == "1"
        assert sections[1].section_num == "1.1"

    def test_unnumbered_line_ranges(self):
        content = "## Overview\nLine 2\nLine 3\n## Details\nLine 5"
        sections = parse_sections(content, max_depth=3)
        assert sections[0].line_start == 1
        assert sections[0].line_end == 3
        assert sections[1].line_start == 4
        assert sections[1].line_end == 5

    def test_unnumbered_build_hierarchy(self):
        content = "## Introduction\nText\n### Background\nText\n### Prior Work\nText"
        sections = parse_sections(content, max_depth=3)
        build_hierarchy(sections)
        assert sections[1].breadcrumb == "1 Introduction"
        assert sections[0].subsections == ["1.1", "1.2"]

    def test_unnumbered_round_trip(self, tmp_path):
        """generate_index → read_section round-trip on unnumbered doc."""
        doc = tmp_path / "full_document.md"
        doc.write_text("## Overview\nHello world\n## Methods\nGoodbye world")
        idx = generate_index(doc, summarize=False)
        assert idx is not None

        result = read_section(tmp_path, "1")
        assert result is not None
        assert "Hello world" in result

        result2 = read_section(tmp_path, "2")
        assert result2 is not None
        assert "Goodbye world" in result2

    def test_unnumbered_counter_resets(self):
        """Deeper counters reset when a shallower header appears."""
        content = "## A\n### A1\n### A2\n## B\n### B1"
        sections = parse_sections(content, max_depth=3)
        assert [s.section_num for s in sections] == ["1", "1.1", "1.2", "2", "2.1"]


# ---------------------------------------------------------------------------
# build_hierarchy
# ---------------------------------------------------------------------------


class TestBuildHierarchy:
    def test_builds_breadcrumbs(self):
        content = "## 7 Language\nText\n## 7.2 Root\nText\n## 7.2.1 Overview\nText"
        sections = parse_sections(content, max_depth=3)
        build_hierarchy(sections)
        assert sections[2].breadcrumb == "7 Language > 7.2 Root"

    def test_builds_subsection_lists(self):
        content = "## 1 Top\nText\n## 1.1 Sub1\nText\n## 1.2 Sub2\nText"
        sections = parse_sections(content, max_depth=3)
        build_hierarchy(sections)
        assert sections[0].subsections == ["1.1", "1.2"]


# ---------------------------------------------------------------------------
# format_index_md
# ---------------------------------------------------------------------------


class TestFormatIndexMd:
    def test_produces_valid_frontmatter(self):
        sections = [
            Section(
                section_num="1",
                title="Intro",
                depth=1,
                line_start=1,
                line_end=10,
                content="Hello",
                summary="Summary text",
            )
        ]
        metadata = {
            "document": "test_doc",
            "generated": "2026-01-01T00:00:00Z",
            "source_checksum": "sha256:abc123",
            "total_lines": 100,
            "depth": 3,
            "section_count": 1,
        }
        result = format_index_md(sections, metadata)
        assert "---" in result
        assert "document: test_doc" in result
        assert "source_checksum: sha256:abc123" in result
        assert "## 1 Intro" in result
        assert "**Lines:** 1-10" in result
        assert "Summary text" in result


# ---------------------------------------------------------------------------
# generate_index
# ---------------------------------------------------------------------------


class TestGenerateIndex:
    def test_produces_index_file(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello\n## 2 Body\nWorld")
        result = generate_index(doc, summarize=False)
        assert result == tmp_path / "INDEX.md"
        assert result.exists()
        content = result.read_text()
        assert "## 1 Intro" in content
        assert "## 2 Body" in content

    def test_skips_when_checksum_matches(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello\n## 2 Body\nWorld")
        # Generate once
        generate_index(doc, summarize=False)
        # Generate again — should skip
        result = generate_index(doc, summarize=False)
        assert result is None

    def test_regenerates_when_forced(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello\n## 2 Body\nWorld")
        generate_index(doc, summarize=False)
        result = generate_index(doc, summarize=False, force=True)
        assert result is not None

    def test_returns_none_for_missing_doc(self, tmp_path):
        result = generate_index(tmp_path / "nonexistent.md")
        assert result is None

    def test_accepts_directory_path(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello")
        result = generate_index(tmp_path, summarize=False)
        assert result == tmp_path / "INDEX.md"


# ---------------------------------------------------------------------------
# parse_index_sections + read_lines + read_section
# ---------------------------------------------------------------------------


class TestParseIndexSections:
    def test_parses_line_ranges(self):
        index_content = (
            "---\ndocument: test\n---\n\n"
            "## 1 Intro\n**Lines:** 1-10\n\nSummary.\n\n"
            "## 2 Body\n**Lines:** 11-20\n\nMore.\n"
        )
        sections = parse_index_sections(index_content)
        assert "1" in sections
        assert sections["1"] == (1, 10, "Intro")
        assert "2" in sections
        assert sections["2"] == (11, 20, "Body")

    def test_period_numbered_index_sections(self):
        index_content = (
            "---\ndocument: test\n---\n\n"
            "## 1. Intro\n**Lines:** 1-10\n\nSummary.\n\n"
            "### 1.1. Background\n**Lines:** 3-8\n\nDetails.\n"
        )
        sections = parse_index_sections(index_content)
        assert "1" in sections
        assert sections["1"] == (1, 10, "Intro")
        assert "1.1" in sections
        assert sections["1.1"] == (3, 8, "Background")

    def test_round_trip_period_numbered(self, tmp_path):
        """generate_index on period-numbered doc → parse_index_sections round-trip."""
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1. Introduction\nHello\n## 2. Methods\nWorld")
        idx = generate_index(doc, summarize=False)
        assert idx is not None
        content = idx.read_text()
        sections = parse_index_sections(content)
        assert "1" in sections
        assert "2" in sections
        assert sections["1"][2] == "Introduction"
        assert sections["2"][2] == "Methods"


class TestReadLines:
    def test_reads_range(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("line1\nline2\nline3\nline4\nline5\n")
        result = read_lines(f, 2, 4)
        assert "line2" in result
        assert "line4" in result
        assert "line1" not in result

    def test_reads_with_context(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("line1\nline2\nline3\nline4\nline5\n")
        result = read_lines(f, 3, 3, context=1)
        assert "line2" in result
        assert "line4" in result


class TestReadSection:
    def test_reads_section_by_number(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello world\n## 2 Body\nGoodbye world")
        generate_index(doc, summarize=False)

        result = read_section(tmp_path, "1")
        assert result is not None
        assert "Hello world" in result

    def test_returns_none_for_missing_section(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello")
        generate_index(doc, summarize=False)

        result = read_section(tmp_path, "99")
        assert result is None

    def test_returns_none_when_no_index(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello")
        result = read_section(tmp_path, "1")
        assert result is None


# ---------------------------------------------------------------------------
# Script backward compatibility
# ---------------------------------------------------------------------------


class TestScriptBackwardCompat:
    def test_generate_index_script_runs(self):
        result = subprocess.run(
            ["python", "scripts/generate_index.py", "--help"],
            capture_output=True,
            text=True,
            cwd="/home/reid/1cfe/agentic-mbse",
        )
        assert result.returncode == 0
        assert "INDEX.md" in result.stdout or "index" in result.stdout.lower()

    def test_read_section_script_runs(self):
        result = subprocess.run(
            ["python", "scripts/read_section.py", "--help"],
            capture_output=True,
            text=True,
            cwd="/home/reid/1cfe/agentic-mbse",
        )
        assert result.returncode == 0
        assert "section" in result.stdout.lower()
