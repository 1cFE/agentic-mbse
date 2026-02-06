"""Tests for agentic_mbse.extraction.postprocess module."""

from pathlib import Path

from agentic_mbse.extraction.postprocess import (
    clean_header_artifacts,
    postprocess,
    promote_bold_headers,
    promote_figure_captions,
    promote_plain_headers,
    normalize_image_paths,
    repair_ligatures,
    strip_page_numbers,
    strip_running_headers,
)


# ---------------------------------------------------------------------------
# promote_bold_headers
# ---------------------------------------------------------------------------


class TestPromoteBoldHeaders:
    def test_basic_promotion(self):
        md = "**1 Introduction**"
        assert promote_bold_headers(md) == "## 1 Introduction"

    def test_depth_mapping_one_dot(self):
        md = "**2.1 Background**"
        assert promote_bold_headers(md) == "### 2.1 Background"

    def test_depth_mapping_two_dots(self):
        md = "**3.1.2 Details**"
        assert promote_bold_headers(md) == "#### 3.1.2 Details"

    def test_trailing_dot_after_number(self):
        md = "**1. Introduction**"
        assert promote_bold_headers(md) == "## 1 Introduction"

    def test_split_bold(self):
        """Handle **1.** **Introduction** pattern (seen in 2238)."""
        md = "**1.** **Introduction**"
        assert promote_bold_headers(md) == "## 1 Introduction"

    def test_appendix_letter(self):
        md = "**A Introduction**"
        assert promote_bold_headers(md) == "## A Introduction"

    def test_appendix_letter_with_subsection(self):
        md = "**A.1 Background**"
        assert promote_bold_headers(md) == "### A.1 Background"

    def test_bibliography_false_positive(self):
        """Should NOT match bibliography refs like **2**, 473 (2012)."""
        md = "**2**, 473 (2012)"
        assert promote_bold_headers(md) == "**2**, 473 (2012)"

    def test_mid_paragraph_bold_no_match(self):
        md = "This has **bold text** in the middle of a paragraph."
        assert promote_bold_headers(md) == md

    def test_multiline_document(self):
        md = (
            "Some preamble text.\n"
            "\n"
            "**1 Introduction**\n"
            "\n"
            "Content here.\n"
            "\n"
            "**2.1 Methods**\n"
            "\n"
            "More content.\n"
        )
        result = promote_bold_headers(md)
        assert "## 1 Introduction" in result
        assert "### 2.1 Methods" in result
        assert "Some preamble text." in result

    def test_preserves_non_bold_text(self):
        md = "Regular text stays.\n\n**1 Title**\n\nMore text."
        result = promote_bold_headers(md)
        assert "Regular text stays." in result
        assert "More text." in result

    def test_bold_without_number_not_matched(self):
        md = "**Introduction**"
        assert promote_bold_headers(md) == "**Introduction**"


# ---------------------------------------------------------------------------
# promote_plain_headers
# ---------------------------------------------------------------------------


class TestPromotePlainHeaders:
    def test_basic_plain_header(self):
        md = "\n\n1 Executive Summary\n\n"
        result = promote_plain_headers(md)
        assert "## 1 Executive Summary" in result

    def test_subsection_plain_header(self):
        md = "\n\n3.1 Global Status of Fusion Energy\n\n"
        result = promote_plain_headers(md)
        assert "### 3.1 Global Status of Fusion Energy" in result

    def test_rejects_toc_with_trailing_page_number(self):
        """TOC entries like '1 Executive Summary 4' should NOT be promoted."""
        md = "\n\n1 Executive Summary 4\n\n"
        result = promote_plain_headers(md)
        # Should not be promoted because of trailing page number
        assert "## 1" not in result

    def test_rejects_toc_with_dot_leaders(self):
        """TOC entries with dot leaders should NOT be promoted."""
        md = "\n\n3.1 Global Status . . . . . . . . . . . . . 5\n\n"
        result = promote_plain_headers(md)
        assert "###" not in result

    def test_not_standalone(self):
        """Numbers in running text should not match."""
        md = "There are 1 Executive at the company.\n"
        result = promote_plain_headers(md)
        assert "##" not in result

    def test_requires_blank_lines(self):
        """Must be between blank lines to match."""
        md = "Some text\n1 Executive Summary\nMore text"
        result = promote_plain_headers(md)
        assert "##" not in result


# ---------------------------------------------------------------------------
# clean_header_artifacts
# ---------------------------------------------------------------------------


class TestCleanHeaderArtifacts:
    def test_removes_redundant_bold(self):
        md = "## **1 Introduction**"
        assert clean_header_artifacts(md) == "## 1 Introduction"

    def test_removes_toc_page_number(self):
        md = "## 1 Executive Summary** **5"
        assert clean_header_artifacts(md) == "## 1 Executive Summary"

    def test_leaves_clean_headers_alone(self):
        md = "## 1 Introduction"
        assert clean_header_artifacts(md) == "## 1 Introduction"

    def test_handles_deeper_headers(self):
        md = "### **2.1 Background**"
        assert clean_header_artifacts(md) == "### 2.1 Background"


# ---------------------------------------------------------------------------
# strip_page_numbers
# ---------------------------------------------------------------------------


class TestStripPageNumbers:
    def test_basic_removal(self):
        md = "Some content.\n\n42\n\nMore content."
        assert strip_page_numbers(md) == "Some content.\n\nMore content."

    def test_four_digit_number(self):
        md = "Some content.\n\n1234\n\nMore content."
        assert strip_page_numbers(md) == "Some content.\n\nMore content."

    def test_five_digit_not_removed(self):
        md = "Some content.\n\n12345\n\nMore content."
        assert strip_page_numbers(md) == md

    def test_number_in_content_not_removed(self):
        """Numbers that are part of content (not standalone) should stay."""
        md = "There are 42 items in the list."
        assert strip_page_numbers(md) == md

    def test_number_not_between_blanks(self):
        md = "Content\n42\nMore content"
        assert strip_page_numbers(md) == md

    def test_multiple_page_numbers(self):
        md = "Page one.\n\n1\n\nPage two.\n\n2\n\nPage three."
        result = strip_page_numbers(md)
        assert result == "Page one.\n\nPage two.\n\nPage three."

    def test_bold_page_number(self):
        """Bold page numbers like **40** should also be stripped."""
        md = "Some content.\n\n**40**\n\nMore content."
        assert strip_page_numbers(md) == "Some content.\n\nMore content."

    def test_multiple_bold_page_numbers(self):
        md = "Content A.\n\n**20**\n\nContent B.\n\n**22**\n\nContent C."
        result = strip_page_numbers(md)
        assert result == "Content A.\n\nContent B.\n\nContent C."


# ---------------------------------------------------------------------------
# strip_running_headers
# ---------------------------------------------------------------------------


class TestStripRunningHeaders:
    def test_removes_repeated_lines(self):
        # Simulate a running header appearing 4 times
        # Use multi-line content blocks so they aren't treated as short standalone lines
        blocks = [
            "First paragraph of real content.\nWith a second line.",
            "Author Name",
            "Second paragraph of real content.\nWith a second line.",
            "Author Name",
            "Third paragraph of real content.\nWith a second line.",
            "Author Name",
            "Fourth paragraph of real content.\nWith a second line.",
            "Author Name",
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Author Name" not in result
        assert "First paragraph" in result
        assert "Fourth paragraph" in result

    def test_keeps_infrequent_lines(self):
        blocks = ["Content 1", "Author Name", "Content 2", "Author Name", "Content 3"]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Author Name" in result

    def test_strips_digits_for_normalization(self):
        """Headers like '2 Author Name' and 'Author Name 3' should normalize to same base."""
        blocks = [
            "Content A",
            "2 M. C. Handley, D. Slesinski",
            "Content B",
            "4 M. C. Handley, D. Slesinski",
            "Content C",
            "6 M. C. Handley, D. Slesinski",
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "M. C. Handley" not in result
        assert "Content A" in result

    def test_italic_running_headers(self):
        """Italic-wrapped running headers should be normalized and removed."""
        blocks = [
            "First paragraph.\nWith multiple lines.",
            "_L.S. Araiinejad and K. Shirvan  Applied Energy 401 (2025) 126567_",
            "Second paragraph.\nWith multiple lines.",
            "_L.S. Araiinejad and K. Shirvan  Applied Energy 401 (2025) 126567_",
            "Third paragraph.\nWith multiple lines.",
            "_L.S. Araiinejad and K. Shirvan  Applied Energy 401 (2025) 126567_",
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Araiinejad" not in result
        assert "First paragraph" in result

    def test_long_normalized_lines_not_affected(self):
        """Lines whose normalized form exceeds 120 chars should not be removed."""
        long_line = "A" * 121
        blocks = [long_line, long_line, long_line, long_line]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert long_line in result

    def test_padded_short_lines_are_caught(self):
        """Lines padded with whitespace should still be caught if normalized form is short."""
        padded = "Author Name" + " " * 80 + "Journal 2025"
        blocks = [
            "Content paragraph one.\nWith a second line.",
            padded,
            "Content paragraph two.\nWith a second line.",
            padded,
            "Content paragraph three.\nWith a second line.",
            padded,
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Author Name" not in result
        assert "Content paragraph one" in result

    def test_multiline_blocks_not_affected(self):
        block = "Line one\nLine two"
        blocks = [block, block, block, block]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Line one" in result


# ---------------------------------------------------------------------------
# normalize_image_paths
# ---------------------------------------------------------------------------


class TestNormalizeImagePaths:
    def test_absolute_to_relative(self):
        images_dir = Path("/tmp/output/report/images")
        md = "![fig](/tmp/output/report/images/figure_001.png)"
        result = normalize_image_paths(md, images_dir)
        assert result == "![fig](images/figure_001.png)"

    def test_no_false_match_in_text(self):
        images_dir = Path("/tmp/output/images")
        md = "The images directory is important. ![fig](images/fig.png)"
        result = normalize_image_paths(md, images_dir)
        assert "The images directory is important." in result

    def test_multiple_replacements(self):
        images_dir = Path("/output/images")
        md = (
            "![a](/output/images/fig1.png)\n"
            "![b](/output/images/fig2.png)\n"
        )
        result = normalize_image_paths(md, images_dir)
        assert "![a](images/fig1.png)" in result
        assert "![b](images/fig2.png)" in result


# ---------------------------------------------------------------------------
# repair_ligatures
# ---------------------------------------------------------------------------


class TestRepairLigatures:
    def test_fi_ligature(self):
        md = "The \ufb01rst result was signi\ufb01cant."
        result = repair_ligatures(md)
        assert result == "The first result was significant."

    def test_fl_ligature(self):
        md = "The \ufb02ow of air."
        result = repair_ligatures(md)
        assert result == "The flow of air."

    def test_ff_ligature(self):
        md = "E\ufb00ective strategies."
        result = repair_ligatures(md)
        assert result == "Effective strategies."

    def test_ffi_ligature(self):
        md = "E\ufb03cient operation."
        result = repair_ligatures(md)
        assert result == "Efficient operation."

    def test_ffl_ligature(self):
        md = "Ba\ufb04ed by wind."
        result = repair_ligatures(md)
        assert result == "Baffled by wind."

    def test_replacement_char_left_alone(self):
        md = "Some \ufffd garbled text."
        result = repair_ligatures(md)
        assert "\ufffd" in result

    def test_no_ligatures_unchanged(self):
        md = "Normal text without ligatures."
        assert repair_ligatures(md) == md


# ---------------------------------------------------------------------------
# promote_figure_captions
# ---------------------------------------------------------------------------


class TestPromoteFigureCaptions:
    def test_adjacent_caption(self):
        md = "![](images/figure_001.png)\nFigure 1: A diagram of the system."
        result = promote_figure_captions(md)
        assert result == "![Figure 1: A diagram of the system.](images/figure_001.png)"

    def test_caption_with_blank_line(self):
        md = "![](images/figure_002.png)\n\nFigure 2: Another diagram."
        result = promote_figure_captions(md)
        assert "![Figure 2: Another diagram.](images/figure_002.png)" in result

    def test_fig_abbreviation(self):
        md = "![](images/figure_003.png)\nFig. 3: Caption text."
        result = promote_figure_captions(md)
        assert "![Fig. 3: Caption text.](images/figure_003.png)" in result

    def test_no_adjacent_caption(self):
        md = "![](images/figure_001.png)\n\nSome unrelated paragraph.\n\nFigure 1: Caption."
        result = promote_figure_captions(md)
        # Should not match because there's an intervening paragraph
        assert "![](images/figure_001.png)" in result

    def test_image_with_existing_alt_text(self):
        """Images that already have alt text should not be modified."""
        md = "![Existing alt](images/fig.png)\nFigure 1: Caption."
        result = promote_figure_captions(md)
        assert "![Existing alt](images/fig.png)" in result


# ---------------------------------------------------------------------------
# postprocess (full chain)
# ---------------------------------------------------------------------------


class TestPostprocess:
    def test_full_chain(self):
        images_dir = Path("/tmp/out/images")
        md = (
            "**1 Introduction**\n"
            "\n"
            "The \ufb01rst paragraph.\n"
            "\n"
            "42\n"
            "\n"
            "![](/tmp/out/images/figure_001.png)\n"
            "Figure 1: A diagram.\n"
            "\n"
            "**2 Methods**\n"
        )
        result = postprocess(md, images_dir=images_dir)
        assert "## 1 Introduction" in result
        assert "## 2 Methods" in result
        assert "first" in result
        assert "\ufb01" not in result
        assert "![Figure 1: A diagram.](images/figure_001.png)" in result
        assert "/tmp/out/images" not in result
        # Page number should be stripped
        assert "\n\n42\n\n" not in result

    def test_full_chain_cleans_header_artifacts(self):
        md = "## **1 Introduction**\n\nContent.\n\n## 2 Title** **5\n\nMore content."
        result = postprocess(md)
        assert "## 1 Introduction" in result
        assert "## 2 Title" in result
        assert "** **5" not in result

    def test_full_chain_bold_page_numbers(self):
        md = "Content.\n\n**40**\n\nMore content."
        result = postprocess(md)
        assert "**40**" not in result
        assert "Content." in result
        assert "More content." in result

    def test_no_images_dir(self):
        md = "**1 Title**\n\nContent."
        result = postprocess(md)
        assert "## 1 Title" in result

    def test_empty_string(self):
        assert postprocess("") == ""
