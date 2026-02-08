"""Tests for claude_structure module."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_mbse.extraction.claude_structure import (
    DocumentStyle,
    HeaderInsertion,
    _call_claude,
    _chunk_by_pages,
    _parse_json_response,
    apply_insertions,
    detect_document_style,
    enhance_structure,
    needs_claude_structure,
    repair_structure,
    strip_detected_headers,
)

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _build_md(num_pages: int, headers: list[str] | None = None) -> str:
    """Build markdown with PAGE markers and optional headers sprinkled in.

    Headers are distributed across pages starting from page 2.
    """
    lines: list[str] = []
    header_iter = iter(headers or [])
    for p in range(1, num_pages + 1):
        lines.append(f"<!-- PAGE:{p} -->")
        lines.append("")
        # Try to place one header per page (starting page 2)
        if p >= 2:
            hdr = next(header_iter, None)
            if hdr:
                lines.append(hdr)
                lines.append("")
        lines.append(f"Body text for page {p}.")
        lines.append("")
    return "\n".join(lines)


def _build_lines(num_pages: int) -> list[str]:
    """Build a list of lines with PAGE markers and filler content."""
    lines: list[str] = []
    for p in range(1, num_pages + 1):
        lines.append(f"<!-- PAGE:{p} -->")
        lines.append("")
        lines.append(f"Content for page {p}.")
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# TestDocumentStyle
# ---------------------------------------------------------------------------


class TestDocumentStyle:
    def test_to_dict_from_dict_round_trip(self):
        style = DocumentStyle(
            doc_type="academic_paper",
            heading_convention="numbered_bold",
            has_toc=True,
            running_headers=["Author Name"],
            page_number_format="bare",
        )
        assert DocumentStyle.from_dict(style.to_dict()) == style

    def test_json_serialization(self):
        style = DocumentStyle(
            doc_type="slide_deck",
            heading_convention="slide_titles",
            has_toc=False,
            running_headers=["Footer Text", "Company Name"],
            page_number_format="none",
        )
        json_str = json.dumps(style.to_dict())
        assert DocumentStyle.from_dict(json.loads(json_str)) == style

    def test_missing_optional_fields_use_defaults(self):
        d = {"doc_type": "unknown", "heading_convention": "unknown"}
        style = DocumentStyle.from_dict(d)
        assert style.has_toc is False
        assert style.running_headers == []
        assert style.page_number_format == "none"


# ---------------------------------------------------------------------------
# TestParseJsonResponse
# ---------------------------------------------------------------------------


class TestParseJsonResponse:
    def test_bare_json(self):
        assert _parse_json_response('{"key": "val"}') == {"key": "val"}

    def test_fenced_json(self):
        assert _parse_json_response('```json\n{"key": "val"}\n```') == {"key": "val"}

    def test_prose_wrapped_json(self):
        raw = 'Here is the result:\n{"key": "val"}\nDone.'
        assert _parse_json_response(raw) == {"key": "val"}

    def test_array_json(self):
        raw = '```json\n[{"a": 1}, {"b": 2}]\n```'
        assert _parse_json_response(raw) == [{"a": 1}, {"b": 2}]

    def test_invalid_json_returns_none(self):
        assert _parse_json_response("not json at all") is None

    def test_empty_string_returns_none(self):
        assert _parse_json_response("") is None


# ---------------------------------------------------------------------------
# TestNeedsClaudeStructure
# ---------------------------------------------------------------------------


class TestNeedsClaudeStructure:
    def test_sparse_headers_returns_true(self):
        # 1 header across 20 pages → 0.05/page → True
        md = _build_md(num_pages=20, headers=["## Introduction"])
        assert needs_claude_structure(md) is True

    def test_dense_headers_returns_false(self):
        # 10 headers across 20 pages with mixed levels → 0.5/page → False
        headers = [
            "## Section 1",
            "### Subsection 1.1",
            "## Section 2",
            "### Subsection 2.1",
            "## Section 3",
            "### Subsection 3.1",
            "## Section 4",
            "### Subsection 4.1",
            "## Section 5",
            "### Subsection 5.1",
        ]
        md = _build_md(num_pages=20, headers=headers)
        assert needs_claude_structure(md) is False

    def test_high_noise_fraction_returns_true(self):
        # Mix of valid and noise headers — noise fraction > 0.3
        headers = [
            "## A >= 15",  # noise (math operator)
            "## 1 x",  # noise (number + short word)
            "## Real Section Title",
            "## B [ref]",  # noise (brackets)
            "## Another Valid Header",
            "## C + D",  # noise
            "## 42 Fig",  # noise
            "### Good Subsection Here",
            "## E = F",  # noise
            "## Yet Another Section",
        ]
        md = _build_md(num_pages=20, headers=headers)
        assert needs_claude_structure(md) is True

    def test_zero_depth_variance_with_enough_headers_returns_true(self):
        # 5 ## headers, no ### → flat → True (hpp >= 0.1 AND zero depth variance)
        headers = ["## S1", "## S2", "## S3", "## S4", "## S5"]
        md = _build_md(num_pages=20, headers=headers)
        assert needs_claude_structure(md) is True

    def test_zero_depth_variance_sparse_does_not_double_trigger(self):
        # 1 ## header across 20 pages → sparse triggers, depth_variance irrelevant
        md = _build_md(num_pages=20, headers=["## Only"])
        assert needs_claude_structure(md) is True

    def test_corpus_profile_2241_returns_false(self):
        # 2241 (ICRH): 7 ## + 8 ### across 30 pages → 0.5/page, mixed levels → False
        headers = [
            "## Introduction",
            "### Background",
            "## Experimental Setup",
            "### Materials",
            "### Methods",
            "## Results",
            "### Performance Data",
            "### Analysis",
            "## Discussion",
            "### Comparison",
            "## Conclusions",
            "### Future Work",
            "## References",
            "### Acknowledgments",
            "## Appendix",
        ]
        md = _build_md(num_pages=30, headers=headers)
        assert needs_claude_structure(md) is False

    def test_no_pages_returns_true(self):
        # Edge case: no PAGE markers at all
        md = "Just some text with no page markers."
        assert needs_claude_structure(md) is True


# ---------------------------------------------------------------------------
# TestChunking
# ---------------------------------------------------------------------------


class TestChunking:
    def test_small_doc_single_chunk(self):
        lines = _build_lines(num_pages=10)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) == 1
        assert chunks[0].start_page == 1

    def test_50_pages_chunks_with_overlap(self):
        lines = _build_lines(num_pages=50)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        # stride = 25 - 3 = 22; pages 1-25, 23-47, 45-50 → 3 chunks
        assert len(chunks) == 3
        # Overlap: chunk 1 starts before chunk 0 ends
        assert chunks[1].start_page < chunks[0].end_page

    def test_100_pages_correct_count(self):
        lines = _build_lines(num_pages=100)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        # stride = 25 - 3 = 22; ceil(100/22) = 5
        assert len(chunks) >= 4

    def test_overlap_pages_in_adjacent_chunks(self):
        lines = _build_lines(num_pages=50)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) >= 2
        # Overlap text appears in both adjacent chunks
        chunk0_text = "\n".join(lines[chunks[0].start_line : chunks[0].end_line])
        chunk1_text = "\n".join(lines[chunks[1].start_line : chunks[1].end_line])
        # The overlap pages should appear in both
        overlap_start = chunks[1].start_page
        overlap_marker = f"<!-- PAGE:{overlap_start} -->"
        assert overlap_marker in chunk0_text
        assert overlap_marker in chunk1_text

    def test_chunk_text_field_matches_lines(self):
        lines = _build_lines(num_pages=10)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) == 1
        expected = "\n".join(lines[chunks[0].start_line : chunks[0].end_line])
        assert chunks[0].text == expected


# ---------------------------------------------------------------------------
# TestApplyInsertions
# ---------------------------------------------------------------------------


class TestApplyInsertions:
    def test_single_insertion_before(self):
        md = "Some intro text\n\nThe main body starts here."
        ins = [
            HeaderInsertion(
                anchor_text="The main body starts",
                level=2,
                title="Introduction",
                insert_position="before",
            )
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert "## Introduction" in result
        assert inserted == 1 and skipped == 0

    def test_single_insertion_after(self):
        md = "Abstract paragraph here.\n\nMore text below."
        ins = [
            HeaderInsertion(
                anchor_text="Abstract paragraph",
                level=2,
                title="Methods",
                insert_position="after",
            )
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert "## Methods" in result
        assert inserted == 1

    def test_multiple_insertions_reverse_order(self):
        md = "First section content\n\nSecond section content\n\nThird section content"
        ins = [
            HeaderInsertion(
                anchor_text="First section",
                level=2,
                title="Section A",
                insert_position="before",
            ),
            HeaderInsertion(
                anchor_text="Third section",
                level=2,
                title="Section C",
                insert_position="before",
            ),
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert "## Section A" in result
        assert "## Section C" in result
        assert inserted == 2 and skipped == 0
        # Order must be preserved: Section A before Section C
        assert result.index("## Section A") < result.index("## Section C")

    def test_anchor_not_found_skips_with_warning(self):
        md = "Some text here."
        ins = [
            HeaderInsertion(
                anchor_text="nonexistent text",
                level=2,
                title="Missing",
                insert_position="before",
            )
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert inserted == 0 and skipped == 1
        assert any("not found" in w for w in warnings)

    def test_ambiguous_anchor_skips_with_warning(self):
        md = "Repeated line\n\nRepeated line"
        ins = [
            HeaderInsertion(
                anchor_text="Repeated line",
                level=2,
                title="Ambiguous",
                insert_position="before",
            )
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert skipped == 1
        assert any("ambiguous" in w.lower() for w in warnings)

    def test_duplicate_header_prevention(self):
        md = "## Introduction\n\nThe content starts here."
        ins = [
            HeaderInsertion(
                anchor_text="The content starts",
                level=2,
                title="Introduction",
                insert_position="before",
            )
        ]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert skipped == 1
        assert result.count("## Introduction") == 1  # not duplicated


# ---------------------------------------------------------------------------
# TestStripDetectedHeaders
# ---------------------------------------------------------------------------


class TestStripDetectedHeaders:
    def test_removes_matching_lines(self):
        md = "Content A\n\nAuthor Name\n\nContent B\n\nAuthor Name\n\nContent C"
        result = strip_detected_headers(md, ["Author Name"])
        assert "Author Name" not in result
        assert "Content A" in result and "Content C" in result

    def test_preserves_non_matching(self):
        md = "Content A\n\nDifferent Text\n\nContent B"
        result = strip_detected_headers(md, ["Author Name"])
        assert "Different Text" in result

    def test_case_insensitive_match(self):
        md = "Content\n\nauthor name\n\nMore content"
        result = strip_detected_headers(md, ["Author Name"])
        assert "author name" not in result

    def test_whitespace_collapsed_match(self):
        md = "Content\n\nAuthor   Name\n\nMore content"
        result = strip_detected_headers(md, ["Author Name"])
        assert "Author   Name" not in result

    def test_empty_patterns_no_change(self):
        md = "Content A\n\nContent B"
        result = strip_detected_headers(md, [])
        assert result == md


# ---------------------------------------------------------------------------
# TestCallClaude (Phase 2)
# ---------------------------------------------------------------------------


class TestCallClaude:
    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_successful_call(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"result": true}')
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text == '{"result": true}'
        assert warnings == []

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_retry_on_failure(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),  # first attempt fails
            MagicMock(returncode=0, stdout='{"ok": true}'),  # retry succeeds
        ]
        text, warnings = _call_claude("prompt", [], model="haiku", retries=1)
        assert text == '{"ok": true}'
        assert mock_run.call_count == 2

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_timeout_returns_none(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=120)
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text is None
        assert any("timed out" in w for w in warnings)

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_claude_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text is None
        assert any("not found" in w for w in warnings)

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_all_retries_exhausted(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        text, warnings = _call_claude("prompt", [], model="haiku", retries=1)
        assert text is None
        assert mock_run.call_count == 2  # initial + 1 retry

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_empty_image_paths_no_images_in_cmd(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"ok": true}')
        text, warnings = _call_claude("test prompt", [], model="haiku")
        assert text == '{"ok": true}'
        # Command should be just claude -p --model haiku prompt, no image filenames
        actual_cmd = mock_run.call_args[0][0]
        assert actual_cmd == ["claude", "-p", "--model", "haiku", "test prompt"]
        # cwd should be None when no images
        assert mock_run.call_args[1]["cwd"] is None


# ---------------------------------------------------------------------------
# TestDetectDocumentStyle (Phase 2)
# ---------------------------------------------------------------------------


class TestDetectDocumentStyle:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_valid_response(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '{"doc_type":"academic_paper","heading_convention":"numbered_bold",'
            '"has_toc":true,"running_headers":[],"page_number_format":"bare"}',
            [],
        )
        md = "<!-- PAGE:1 -->\nTitle\n<!-- PAGE:2 -->\nBody\n<!-- PAGE:3 -->\nMore"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "academic_paper"
        assert (tmp_path / "style.json").exists()

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_cache_hit(self, mock_claude, mock_render, tmp_path):
        cache = {
            "doc_type": "slide_deck",
            "heading_convention": "slide_titles",
            "has_toc": False,
            "running_headers": ["Footer"],
            "page_number_format": "none",
        }
        (tmp_path / "style.json").write_text(json.dumps(cache))
        style, warnings = detect_document_style("md", Path("test.pdf"), tmp_path)
        assert style.doc_type == "slide_deck"
        mock_claude.assert_not_called()

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_malformed_json_fallback(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["claude -p failed"])
        md = "<!-- PAGE:1 -->\nText"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "unknown"
        assert len(warnings) > 0

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_timeout_fallback(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["timed out"])
        style, warnings = detect_document_style("<!-- PAGE:1 -->\nX", Path("t.pdf"), tmp_path)
        assert style.doc_type == "unknown"

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_fewer_than_3_pages_handled(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '{"doc_type":"word_doc","heading_convention":"unnumbered_bold",'
            '"has_toc":false,"running_headers":[],"page_number_format":"none"}',
            [],
        )
        md = "<!-- PAGE:1 -->\nShort doc"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "word_doc"


# ---------------------------------------------------------------------------
# TestRepairStructure (Phase 3)
# ---------------------------------------------------------------------------


class TestRepairStructure:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_single_chunk_valid_response(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '[{"anchor_text":"The reactor design","level":2,'
            '"title":"Reactor Design","insert_position":"before"}]',
            [],
        )
        style = DocumentStyle(
            doc_type="academic_paper",
            heading_convention="unnumbered_bold",
        )
        md = "<!-- PAGE:1 -->\nIntro text\n<!-- PAGE:2 -->\nThe reactor design uses..."
        insertions, warnings = repair_structure(md, Path("test.pdf"), style)
        assert len(insertions) == 1
        assert insertions[0].title == "Reactor Design"

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_multi_chunk_dedup(self, mock_claude, mock_render):
        # 50-page doc → multiple chunks; same insertion in overlap → deduplicated
        mock_render.return_value = Path("/tmp/page.png")
        # Both chunks return the same insertion for text in overlap zone
        mock_claude.side_effect = [
            (
                '[{"anchor_text":"Shared overlap text","level":2,'
                '"title":"Overlap Section","insert_position":"before"}]',
                [],
            ),
            (
                '[{"anchor_text":"Shared overlap text","level":2,'
                '"title":"Overlap Section","insert_position":"before"}]',
                [],
            ),
            # Third chunk returns a different insertion
            (
                '[{"anchor_text":"Unique chunk 3 text","level":2,'
                '"title":"Third Section","insert_position":"before"}]',
                [],
            ),
        ]
        style = DocumentStyle(
            doc_type="academic_paper",
            heading_convention="unnumbered_bold",
        )
        # Build 50-page md with shared text in overlap zone (pages 23-25)
        lines = []
        for p in range(1, 51):
            lines.append(f"<!-- PAGE:{p} -->")
            lines.append("")
            if p == 24:
                lines.append("Shared overlap text appears here")
            elif p == 46:
                lines.append("Unique chunk 3 text appears here")
            else:
                lines.append(f"Content for page {p}.")
            lines.append("")
        md = "\n".join(lines)
        insertions, warnings = repair_structure(md, Path("test.pdf"), style)
        # Dedup: "Overlap Section" should appear only once
        overlap_insertions = [i for i in insertions if i.title == "Overlap Section"]
        assert len(overlap_insertions) == 1

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_invalid_anchor_rejected(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '[{"anchor_text":"nonexistent text in doc","level":2,'
            '"title":"Bad","insert_position":"before"}]',
            [],
        )
        style = DocumentStyle(
            doc_type="academic_paper",
            heading_convention="unnumbered_bold",
        )
        md = "<!-- PAGE:1 -->\nActual content here"
        insertions, warnings = repair_structure(md, Path("test.pdf"), style)
        assert len(insertions) == 0
        assert any("anchor" in w.lower() for w in warnings)

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_malformed_json_skips_chunk(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["parse failed"])
        style = DocumentStyle(
            doc_type="academic_paper",
            heading_convention="unnumbered_bold",
        )
        insertions, warnings = repair_structure("<!-- PAGE:1 -->\nText", Path("t.pdf"), style)
        assert len(insertions) == 0
        assert len(warnings) > 0


# ---------------------------------------------------------------------------
# TestEnhanceStructure (Phase 3)
# ---------------------------------------------------------------------------


class TestEnhanceStructure:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_happy_path(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        # Phase A returns style, Phase B returns insertions
        mock_claude.side_effect = [
            (
                '{"doc_type":"academic_paper","heading_convention":"unnumbered_bold",'
                '"has_toc":false,"running_headers":[],"page_number_format":"none"}',
                [],
            ),
            (
                '[{"anchor_text":"The main results","level":2,'
                '"title":"Results","insert_position":"before"}]',
                [],
            ),
        ]
        md = "<!-- PAGE:1 -->\nIntro\n\nThe main results show that..."
        result, metadata = enhance_structure(md, Path("test.pdf"), tmp_path)
        assert "## Results" in result
        assert metadata["headers_inserted"] == 1

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_phase_a_failure_graceful(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["claude unavailable"])
        md = "<!-- PAGE:1 -->\nSome text"
        result, metadata = enhance_structure(md, Path("test.pdf"), tmp_path)
        assert metadata["phase_a"]["doc_type"] == "unknown"
        assert metadata["headers_inserted"] == 0

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_running_headers_stripped(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        # Phase A detects running headers; Phase B returns no insertions
        mock_claude.side_effect = [
            (
                '{"doc_type":"academic_paper","heading_convention":"numbered_bold",'
                '"has_toc":false,"running_headers":["Journal Title"],'
                '"page_number_format":"bare"}',
                [],
            ),
            ("[]", []),
        ]
        md = (
            "<!-- PAGE:1 -->\nIntro text\n\nJournal Title\n\n"
            "<!-- PAGE:2 -->\nMore content\n\nJournal Title\n\nBody"
        )
        result, metadata = enhance_structure(md, Path("test.pdf"), tmp_path)
        assert "Journal Title" not in result
        assert "Intro text" in result
        assert "More content" in result
