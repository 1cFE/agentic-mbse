"""Tests for agentic_mbse.extraction.postprocess module."""

from pathlib import Path

from agentic_mbse.extraction.postprocess import (
    _is_noise_header,
    _is_toc_line,
    clean_header_artifacts,
    normalize_image_paths,
    postprocess,
    promote_bold_headers,
    promote_figure_captions,
    promote_plain_headers,
    reject_noise_headers,
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

    def test_appendix_physics_variable_not_promoted(self):
        """Physics notation like **A ≥ 15** should NOT match appendix pattern."""
        md = "**A ≥ 15**"
        assert promote_bold_headers(md) == "**A ≥ 15**"

    def test_appendix_symbol_title_not_promoted(self):
        """Symbol-starting titles like **D µ or T µ** should NOT match."""
        md = "**D µ or T µ**"
        assert promote_bold_headers(md) == "**D µ or T µ**"

    def test_appendix_comparison_not_promoted(self):
        """Comparison notation like **N << Z** should NOT match."""
        md = "**N << Z**"
        assert promote_bold_headers(md) == "**N << Z**"

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

    def test_rejects_journal_footer_as_header(self):
        """Journal footers like '24 IAEA BULLETIN, 4/1995' should NOT be promoted."""
        md = "\n\n24 IAEA BULLETIN, 4/1995\n\n"
        result = promote_plain_headers(md)
        assert "##" not in result

    def test_rejects_high_section_number(self):
        """Addresses like '5285 Port Royal Road' should NOT be promoted (year numbers, etc)."""
        md = "\n\n5285 Port Royal Road\n\n"
        result = promote_plain_headers(md)
        assert "##" not in result
        # Should preserve original text
        assert "5285 Port Royal Road" in result

    def test_rejects_year_as_section(self):
        """Year numbers like '2050 The capital-related...' should NOT be promoted."""
        md = "\n\n2050 The capital-related portion\n\n"
        result = promote_plain_headers(md)
        assert "##" not in result
        assert "2050 The capital-related portion" in result

    def test_rejects_figure_table_caption(self):
        """Figure/Table references like '52 Table 2.2 - Averaged...' should NOT be promoted."""
        test_cases = [
            "\n\n52 Table 2.2 - Averaged cross sections\n\n",
            "\n\n12 Figure 11 excludes the cost\n\n",
            "\n\n5 Fig. 2 shows the results\n\n",
            "\n\n8 Equation 3 demonstrates\n\n",
        ]
        for md in test_cases:
            result = promote_plain_headers(md)
            assert "##" not in result, f"Failed for: {md.strip()}"

    def test_valid_subsection_still_promoted(self):
        """Subsections like '2.1 Background' should still work."""
        md = "\n\n2.1 Background\n\n"
        result = promote_plain_headers(md)
        assert "### 2.1 Background" in result

    def test_legitimate_sections_below_100_still_promoted(self):
        """Legitimate section numbers ≤ 99 should still be promoted."""
        test_cases = [
            ("\n\n21 Account Summary\n\n", "## 21 Account Summary"),
            ("\n\n99 Final Chapter\n\n", "## 99 Final Chapter"),
            ("\n\n1 Introduction\n\n", "## 1 Introduction"),
        ]
        for md, expected in test_cases:
            result = promote_plain_headers(md)
            assert expected in result, f"Failed for: {md.strip()}"


class TestIsTocLine:
    def test_slash_year_pattern(self):
        """Publication date patterns like '4/1995' should be detected as TOC-like."""
        assert _is_toc_line("IAEA BULLETIN, 4/1995") is True

    def test_slash_year_modern(self):
        assert _is_toc_line("Nuclear Fusion Review, 2/2024") is True

    def test_normal_title_not_toc(self):
        assert _is_toc_line("Global Status of Fusion Energy") is False


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

    def test_page_marker_does_not_block_detection(self):
        """A running header on the line after <!-- PAGE:N --> should still be removed."""
        blocks = [
            "Content A.\nWith more text.",
            "<!-- PAGE:2 -->\nAuthor Name",
            "Content B.\nWith more text.",
            "<!-- PAGE:3 -->\nAuthor Name",
            "Content C.\nWith more text.",
            "<!-- PAGE:4 -->\nAuthor Name",
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "Author Name" not in result
        assert "Content A" in result
        assert "Content C" in result

    def test_page_markers_preserved_after_strip(self):
        """PAGE markers themselves should not be removed by running header detection."""
        blocks = [
            "Content A.\nWith more text.",
            "<!-- PAGE:2 -->\nAuthor Name",
            "Content B.\nWith more text.",
            "<!-- PAGE:3 -->\nAuthor Name",
            "Content C.\nWith more text.",
            "<!-- PAGE:4 -->\nAuthor Name",
        ]
        md = "\n\n".join(blocks)
        result = strip_running_headers(md, threshold=3)
        assert "<!-- PAGE:2 -->" in result
        assert "<!-- PAGE:3 -->" in result
        assert "<!-- PAGE:4 -->" in result

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
        md = "![a](/output/images/fig1.png)\n![b](/output/images/fig2.png)\n"
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
# reject_noise_headers
# ---------------------------------------------------------------------------


class TestRejectNoiseHeaders:
    def test_short_title_demoted(self):
        """Headers with very short title portion (< 4 chars) should be demoted."""
        md = "## 3 ab"
        assert reject_noise_headers(md) == "3 ab"

    def test_math_operators_demoted(self):
        """Headers containing math operators should be demoted."""
        md = "## 5.2 E[X] = sum"
        assert reject_noise_headers(md) == "5.2 E[X] = sum"

    def test_brackets_demoted(self):
        md = "## _[C][AC]_ pattern"
        assert reject_noise_headers(md) == "_[C][AC]_ pattern"

    def test_table_row_with_pipe_demoted(self):
        md = "## value | other | third"
        assert reject_noise_headers(md) == "value | other | third"

    def test_page_number_artifact_demoted(self):
        """Number + tiny word (page artifact) should be demoted."""
        md = "## 42 Fig"
        assert reject_noise_headers(md) == "42 Fig"

    def test_legitimate_header_preserved(self):
        md = "## 1 Introduction"
        assert reject_noise_headers(md) == "## 1 Introduction"

    def test_longer_legitimate_header_preserved(self):
        md = "### 2.1 Global Status of Fusion Energy"
        assert reject_noise_headers(md) == "### 2.1 Global Status of Fusion Energy"

    def test_toc_line_with_dot_leaders_demoted(self):
        """TOC lines with dot leaders should be demoted."""
        md = "## 1. INTRODUCTION................................................................................................................... 1"
        assert (
            reject_noise_headers(md)
            == "1. INTRODUCTION................................................................................................................... 1"
        )

    def test_toc_line_with_trailing_page_number_demoted(self):
        """TOC lines with trailing page numbers should be demoted."""
        md = "## Executive Summary 4"
        assert reject_noise_headers(md) == "Executive Summary 4"

    def test_combined_toc_line_demoted(self):
        """Combined TOC lines should be demoted."""
        md = "## 1. INTRODUCTION... 1 2. ANALYSIS PROCEDURES... 2 3. PLANT DESIGNS... 2"
        assert (
            reject_noise_headers(md)
            == "1. INTRODUCTION... 1 2. ANALYSIS PROCEDURES... 2 3. PLANT DESIGNS... 2"
        )

    def test_curly_braces_demoted(self):
        md = "## 3 f{x} + g{y}"
        assert reject_noise_headers(md) == "3 f{x} + g{y}"

    def test_tab_separated_demoted(self):
        md = "## value\tother\tthird"
        assert reject_noise_headers(md) == "value\tother\tthird"

    def test_multiline_mixed(self):
        md = "## 1 Introduction\n\n## 3 = 4\n\n## 2 Methods"
        result = reject_noise_headers(md)
        assert "## 1 Introduction" in result
        assert "## 2 Methods" in result
        assert "## 3 = 4" not in result
        assert "3 = 4" in result

    # --- Unicode math/science symbols ---

    def test_unicode_ge_demoted(self):
        md = "## T ≥ 10 keV"
        assert reject_noise_headers(md) == "T ≥ 10 keV"

    def test_unicode_nabla_demoted(self):
        md = "## ∇B drift instability"
        assert reject_noise_headers(md) == "∇B drift instability"

    def test_unicode_mu_demoted(self):
        md = "## µ = 1.2 T·m"
        assert reject_noise_headers(md) == "µ = 1.2 T·m"

    def test_unicode_tilde_demoted(self):
        md = "## ~500 MW thermal"
        assert reject_noise_headers(md) == "~500 MW thermal"

    def test_unicode_bullet_demoted(self):
        md = "## • Key findings"
        assert reject_noise_headers(md) == "• Key findings"

    def test_greater_than_demoted(self):
        md = "## Q > 10 plasma gain"
        assert reject_noise_headers(md) == "Q > 10 plasma gain"

    # --- Embedded bold markers ---

    def test_embedded_bold_space_demoted(self):
        md = "## 1000 shots/second** **at 3 MJ"
        assert reject_noise_headers(md) == "1000 shots/second** **at 3 MJ"

    # --- Report/figure labels ---

    def test_ornl_report_label_demoted(self):
        """ORNL figure labels like 'ORNL 99-1407 EFG' should be demoted."""
        md = "## ORNL 99-1407 EFG"
        assert reject_noise_headers(md) == "ORNL 99-1407 EFG"

    def test_doe_report_label_demoted(self):
        """DOE report labels should be demoted."""
        md = "## DOE/ER-1234"
        assert reject_noise_headers(md) == "DOE/ER-1234"

    def test_anl_report_label_demoted(self):
        """ANL report labels should be demoted."""
        md = "## ANL-2020-42"
        assert reject_noise_headers(md) == "ANL-2020-42"

    # --- Numbered sentences referencing figures/tables ---

    def test_numbered_figure_reference_demoted(self):
        """Numbered sentences like '12. Figure 11 excludes...' should be demoted."""
        md = "## 12. Figure 11 excludes the cost"
        assert reject_noise_headers(md) == "12. Figure 11 excludes the cost"

    def test_numbered_table_reference_demoted(self):
        """Numbered table references should be demoted."""
        md = "## 5. Table 3 shows the results"
        assert reject_noise_headers(md) == "5. Table 3 shows the results"

    def test_numbered_equation_reference_demoted(self):
        """Numbered equation references should be demoted."""
        md = "## 8. Equation 2 defines the relationship"
        assert reject_noise_headers(md) == "8. Equation 2 defines the relationship"

    def test_embedded_bold_no_space_demoted(self):
        md = "## Design****Overview"
        assert reject_noise_headers(md) == "Design****Overview"

    # --- Reference entries (bibliographic citations) ---

    def test_reference_with_journal_abbrev_demoted(self):
        """Reference with journal abbreviation should be demoted."""
        md = "## 1. Control. Fusion 51 (12), 124017."
        assert reject_noise_headers(md) == "1. Control. Fusion 51 (12), 124017."

    def test_reference_with_author_initials_demoted(self):
        """Reference with author initials should be demoted."""
        md = "## 5. J.G. Delene and C.R. Hudson, Cost Estimate Guidelines"
        assert (
            reject_noise_headers(md) == "5. J.G. Delene and C.R. Hudson, Cost Estimate Guidelines"
        )

    def test_reference_with_us_department_demoted(self):
        """Reference with U.S. Department should be demoted."""
        md = "## 2. Annual Energy Outlook 1998, U.S. Department of Energy"
        assert (
            reject_noise_headers(md) == "2. Annual Energy Outlook 1998, U.S. Department of Energy"
        )

    def test_reference_with_university_demoted(self):
        """Reference with university name should be demoted."""
        md = "## 17. Personal communication from R. Miller, University of California"
        assert (
            reject_noise_headers(md)
            == "17. Personal communication from R. Miller, University of California"
        )

    def test_reference_with_year_in_parens_demoted(self):
        """Reference with year in parentheses should be demoted."""
        md = "## 10. Advanced Design Nuclear Power Plants (2001)"
        assert reject_noise_headers(md) == "10. Advanced Design Nuclear Power Plants (2001)"

    def test_legitimate_numbered_section_preserved(self):
        """Legitimate section 1-10 without bibliographic indicators preserved."""
        md = "## 1. Introduction"
        assert reject_noise_headers(md) == "## 1. Introduction"

    def test_legitimate_subsection_preserved(self):
        """Subsections like '4.1 Methods' should be preserved."""
        md = "## 4.1 Research Methods"
        assert reject_noise_headers(md) == "## 4.1 Research Methods"

    # --- Legitimate headers still preserved ---

    def test_tritium_management_preserved(self):
        md = "## 3 Tritium Management Strategy"
        assert reject_noise_headers(md) == "## 3 Tritium Management Strategy"

    def test_appendix_letter_preserved(self):
        md = "## A Safety Requirements"
        assert reject_noise_headers(md) == "## A Safety Requirements"

    def test_unnumbered_section_preserved(self):
        md = "## Overview"
        assert reject_noise_headers(md) == "## Overview"

    # --- H1 noise rejection ---

    def test_h1_math_symbol_demoted(self):
        """H1 headers with math symbols should be demoted (energy_amplifier use case)."""
        md = "# ∫ E·dl = 0"
        assert reject_noise_headers(md) == "∫ E·dl = 0"

    def test_h1_equation_fragment_demoted(self):
        """H1 equation fragments with equals signs should be demoted."""
        md = "# T = ½mv²"
        assert reject_noise_headers(md) == "T = ½mv²"

    def test_h1_sum_symbol_demoted(self):
        """H1 with summation symbol should be demoted."""
        md = "# ∑ᵢ xᵢ"
        assert reject_noise_headers(md) == "∑ᵢ xᵢ"

    def test_h1_brackets_demoted(self):
        """H1 with brackets (math notation) should be demoted."""
        md = "# [x, y] = xy - yx"
        assert reject_noise_headers(md) == "[x, y] = xy - yx"

    def test_h1_short_fragment_demoted(self):
        """H1 with very short text should be demoted."""
        md = "# 42 x"
        assert reject_noise_headers(md) == "42 x"

    def test_h1_legitimate_title_preserved(self):
        """Legitimate H1 document titles should be preserved."""
        md = "# Fusion Energy Research and Development"
        assert reject_noise_headers(md) == "# Fusion Energy Research and Development"

    # --- Numberless bibliographic entries (Task 1) ---

    def test_numberless_journal_citation_with_volume_issue_demoted(self):
        """Numberless journal citation with journal abbrev + volume/issue should be demoted."""
        # Example: "Control. Fusion 51 (12), 124017."
        md = "## Control. Fusion 51 (12), 124017."
        assert reject_noise_headers(md) == "Control. Fusion 51 (12), 124017."

    def test_numberless_journal_with_page_range_demoted(self):
        """Journal citation with journal abbrev + page range should be demoted."""
        md = "## Nucl. Fusion 45(3), S404-S413."
        assert reject_noise_headers(md) == "Nucl. Fusion 45(3), S404-S413."

    def test_numberless_multiple_journal_abbrevs_demoted(self):
        """Multiple journal abbreviations signal a bibliographic entry."""
        md = "## J. Appl. Phys. Lett. 89 (2006)"
        assert reject_noise_headers(md) == "J. Appl. Phys. Lett. 89 (2006)"

    def test_numberless_author_initials_with_journal_demoted(self):
        """Multiple author initials combined with journal pattern should be demoted."""
        md = "## R. W. Moir, Phys. Plasmas 15 (2008)"
        assert reject_noise_headers(md) == "R. W. Moir, Phys. Plasmas 15 (2008)"

    def test_numberless_year_parens_with_journal_demoted(self):
        """Year in parentheses combined with journal abbreviation should be demoted."""
        md = "## Plasma Phys. Control. Fusion (2020)"
        assert reject_noise_headers(md) == "Plasma Phys. Control. Fusion (2020)"

    def test_numberless_volume_issue_with_page_range_demoted(self):
        """Volume/issue pattern + page range is strong bibliographic signal."""
        md = "## 51(12), 124-130."
        assert reject_noise_headers(md) == "51(12), 124-130."

    def test_single_journal_abbrev_alone_preserved(self):
        """Single journal abbreviation alone should NOT trigger rejection (avoid false positive)."""
        # Example: "General. Introduction" could match pattern but is legitimate
        md = "## General. Introduction"
        assert reject_noise_headers(md) == "## General. Introduction"

    def test_single_volume_issue_alone_preserved(self):
        """Volume/issue pattern alone is not enough (need 2 signals)."""
        md = "## Section 51(12) Analysis"
        assert reject_noise_headers(md) == "## Section 51(12) Analysis"

    def test_author_initials_alone_preserved(self):
        """Author initials alone without other bibliographic signals preserved."""
        md = "## R. W. Requirements"
        assert reject_noise_headers(md) == "## R. W. Requirements"

    def test_year_alone_preserved(self):
        """Year in parentheses alone is not enough."""
        md = "## Planning (2020) Framework"
        assert reject_noise_headers(md) == "## Planning (2020) Framework"

    def test_complex_numberless_reference_demoted(self):
        """Complex reference with multiple signals should be demoted."""
        # Has: journal abbrevs (Nucl. Eng.), volume/issue (40(2)), page range (201-215)
        md = "## Nucl. Eng. Des. 40(2), 201-215"
        assert reject_noise_headers(md) == "Nucl. Eng. Des. 40(2), 201-215"

    def test_sparc_overview_phantom_example_demoted(self):
        """Actual phantom from sparc_overview corpus paper."""
        md = "## Control. Fusion Energy 51 (2009), 124017."
        assert reject_noise_headers(md) == "Control. Fusion Energy 51 (2009), 124017."

    def test_legitimate_section_with_abbrev_preserved(self):
        """Legitimate section that happens to have one abbreviation is preserved."""
        # Only one signal (single abbrev), not enough for rejection
        md = "## 3.2 Design. Methodology"
        assert reject_noise_headers(md) == "## 3.2 Design. Methodology"

    def test_combined_references_header_with_numbered_entry_demoted(self):
        """REFERENCES header combined with numbered bibliography entry should be demoted."""
        md = "## **REFERENCES** 1. Electric Power Annual 1998 Volume 1, U.S. Department of Energy, Energy Information"
        assert (
            reject_noise_headers(md)
            == "**REFERENCES** 1. Electric Power Annual 1998 Volume 1, U.S. Department of Energy, Energy Information"
        )

    def test_h1_mixed_with_h2_noise(self):
        """Mixed H1 and H2 noise headers should be demoted appropriately."""
        md = "# ∇×B = µ₀J\n\n## 1 Introduction\n\n# E = mc²\n\n## 2 Methods"
        result = reject_noise_headers(md)
        assert "## 1 Introduction" in result
        assert "## 2 Methods" in result
        assert "# ∇×B = µ₀J" not in result
        assert "∇×B = µ₀J" in result
        assert "# E = mc²" not in result
        assert "E = mc²" in result

    # --- Address line rejection (Task 2) ---

    def test_address_with_zip_and_road_demoted(self):
        """Address with ZIP code and street keyword should be demoted."""
        # From delene_2001 corpus
        md = "## 5285 Port Royal Road"
        assert reject_noise_headers(md) == "5285 Port Royal Road"

    def test_address_with_numbered_street_demoted(self):
        """Numbered street address should be demoted."""
        md = "## 1000 Independence Avenue SW"
        assert reject_noise_headers(md) == "1000 Independence Avenue SW"

    def test_address_with_suite_demoted(self):
        """Address with suite number should be demoted."""
        md = "## 1234 Corporate Blvd Suite 200"
        assert reject_noise_headers(md) == "1234 Corporate Blvd Suite 200"

    def test_address_with_state_abbrev_and_street_demoted(self):
        """Address with state abbreviation and street keyword should be demoted."""
        md = "## Springfield Street, VA 22150"
        assert reject_noise_headers(md) == "Springfield Street, VA 22150"

    def test_address_with_state_and_zip_demoted(self):
        """Address with state abbreviation and ZIP should be demoted."""
        md = "## Oak Ridge, TN 37831"
        assert reject_noise_headers(md) == "Oak Ridge, TN 37831"

    def test_zip_without_street_keyword_preserved(self):
        """ZIP code alone without street keywords preserved (avoid false positive)."""
        # Could be a section number like "10000 Iterations Analysis"
        md = "## 10000 Iterations Analysis"
        assert reject_noise_headers(md) == "## 10000 Iterations Analysis"

    def test_street_keyword_without_number_preserved(self):
        """Street keyword without numbered address pattern preserved."""
        # Could be legitimate like "Highway Safety Analysis"
        md = "## Highway Safety Analysis"
        assert reject_noise_headers(md) == "## Highway Safety Analysis"

    def test_state_abbrev_alone_preserved(self):
        """State abbreviation alone without address context preserved."""
        md = "## VA Requirements"
        assert reject_noise_headers(md) == "## VA Requirements"

    def test_legitimate_section_with_abbreviation_preserved(self):
        """Legitimate section with abbreviation that happens to match street pattern preserved."""
        # "Dr." is a street abbreviation but in context it's "Doctor"
        md = "## 3 Dr. Smith's Research"
        assert reject_noise_headers(md) == "## 3 Dr. Smith's Research"

    def test_building_address_with_parkway_demoted(self):
        """Building address with Parkway should be demoted."""
        md = "## 456 Research Parkway"
        assert reject_noise_headers(md) == "456 Research Parkway"

    def test_address_with_directional_demoted(self):
        """Address with directional indicator (SW/NW/etc) should be demoted."""
        md = "## 789 Technology Drive NW"
        assert reject_noise_headers(md) == "789 Technology Drive NW"

    def test_address_with_abbreviated_street_demoted(self):
        """Address with abbreviated street type should be demoted."""
        md = "## 2020 Main St."
        assert reject_noise_headers(md) == "2020 Main St."


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


# ---------------------------------------------------------------------------
# Edge-case tests (PR readiness item 8)
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_long_header_over_80_chars_not_promoted(self):
        """Plain header promotion intentionally skips titles >80 chars.

        The regex uses .{2,80} to avoid false-positive promotion of very
        long lines (e.g., paragraph text that happens to start with a number).
        A 120-character title should NOT be promoted — this is by design.
        """
        long_title = "A" * 120
        md = f"\n\n1 {long_title}\n\n"
        result = promote_plain_headers(md)
        # Should NOT be promoted — too long for the safety heuristic
        assert f"## 1 {long_title}" not in result

    def test_bracketed_section_title_is_noise(self):
        """Document whether '5 [Critical Path]' is treated as noise.

        The brackets trigger the math-operator noise check in _is_noise_header,
        so this IS classified as noise. This is the expected behavior since
        brackets in headers are more commonly OCR artifacts than real content.
        """
        assert _is_noise_header("5 [Critical Path]") is True
