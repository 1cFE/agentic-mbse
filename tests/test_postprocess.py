"""Tests for agentic_mbse.extraction.postprocess module."""

from pathlib import Path

from agentic_mbse.extraction.postprocess import (
    _is_noise_header,
    _is_toc_line,
    clean_header_artifacts,
    normalize_image_paths,
    postprocess,
    promote_allcaps_headers,
    promote_bold_allcaps_headers,
    promote_bold_headers,
    promote_figure_captions,
    promote_italic_numbered_headers,
    promote_plain_headers,
    promote_unnumbered_bold_headers,
    reject_noise_headers,
    repair_broken_ligatures,
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

    def test_header_followed_by_body_text(self):
        """Headings followed directly by body text (no blank line) should be promoted.

        Real-world case from sparc_overview line 440:
        Line 439: (blank)
        Line 440: 4. SPARC scenarios and performance projections
        Line 441: To ensure achievement of the SPARC mission...
        """
        md = "\n\n4. SPARC scenarios and performance projections\nTo ensure achievement of the SPARC mission of fusion gain"
        result = promote_plain_headers(md)
        assert "## 4 SPARC scenarios and performance projections" in result


# ---------------------------------------------------------------------------
# promote_italic_numbered_headers
# ---------------------------------------------------------------------------


class TestPromoteItalicNumberedHeaders:
    """Tests for italic numbered section header promotion.

    Handles patterns like: 4.1. _Full-performance H-mode discharge_
    which appear in the sparc_overview paper.
    """

    def test_basic_promotion(self):
        """Single italic numbered header between blank lines."""
        md = "\n\n4.1. _Full-performance H-mode discharge_\n\n"
        result = promote_italic_numbered_headers(md)
        assert "### 4.1 Full-performance H-mode discharge" in result

    def test_without_trailing_dot(self):
        """Italic header without trailing dot after section number."""
        md = "\n\n4.1 _Full-performance H-mode discharge_\n\n"
        result = promote_italic_numbered_headers(md)
        assert "### 4.1 Full-performance H-mode discharge" in result

    def test_depth_mapping(self):
        """Heading depth should be based on section number (4.1 = 1 dot = ###)."""
        md = "\n\n4.1. _Full-performance H-mode discharge_\n\n"
        result = promote_italic_numbered_headers(md)
        # 4.1 has 1 dot, so _header_depth returns 3 (###)
        assert result.strip() == "### 4.1 Full-performance H-mode discharge"

    def test_multiple_headers(self):
        """Multiple italic headers in same document."""
        md = (
            "scenarios are as follows.\n"
            "\n"
            "4.1. _Full-performance H-mode discharge_\n"
            "\n"
            "Since the full-performance H-mode scenario is the most demanding.\n"
            "\n"
            "4.2. _Full-performance L-mode discharge_\n"
            "\n"
            "The full-performance L-mode scenario.\n"
        )
        result = promote_italic_numbered_headers(md)
        assert "### 4.1 Full-performance H-mode discharge" in result
        assert "### 4.2 Full-performance L-mode discharge" in result

    def test_preserves_non_italic_text(self):
        """Should not affect regular italic text."""
        md = "This is _italic text_ in a paragraph.\n\n4.1. _Header Text_\n\n"
        result = promote_italic_numbered_headers(md)
        assert "This is _italic text_ in a paragraph." in result
        assert "### 4.1 Header Text" in result

    def test_requires_blank_lines(self):
        """Italic headers must be between blank lines."""
        # No blank line before
        md = "text before\n4.1. _Header Text_\n\ntext after"
        result = promote_italic_numbered_headers(md)
        assert "4.1. _Header Text_" in result
        assert "###" not in result

    def test_requires_uppercase_start(self):
        """Header title must start with uppercase letter."""
        md = "\n\n4.1. _lowercase header_\n\n"
        result = promote_italic_numbered_headers(md)
        # Should NOT match because title starts with lowercase
        assert "4.1. _lowercase header_" in result
        assert "###" not in result

    def test_sparc_overview_learning_test(self):
        """Learning test from sparc_overview corpus paper.

        Tests the exact pattern seen at lines 692, 784, 802 of
        tests/corpus/current/sparc_overview/full_document.md
        """
        md = (
            "scenarios are as follows.\n"
            "\n"
            "4.1. _Full-performance H-mode discharge_\n"
            "\n"
            "Since the full-performance H-mode scenario is the most demanding on many of the\n"
        )
        result = promote_italic_numbered_headers(md)
        assert "### 4.1 Full-performance H-mode discharge" in result
        # Original italic formatting should be gone
        assert "_Full-performance H-mode discharge_" not in result


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
# repair_broken_ligatures
# ---------------------------------------------------------------------------


class TestRepairBrokenLigatures:
    def test_feld_to_field(self):
        md = "|Magnetic feld on-axis|_B_0|6 T|"
        result = repair_broken_ligatures(md)
        assert result == "|Magnetic field on-axis|_B_0|6 T|"
        assert "feld" not in result

    def test_confnement_to_confinement(self):
        md = "Energy confnement time is critical."
        result = repair_broken_ligatures(md)
        assert result == "Energy confinement time is critical."
        assert "confnement" not in result

    def test_efciency_to_efficiency(self):
        md = "Thermal conversion efciency is 40%."
        result = repair_broken_ligatures(md)
        assert result == "Thermal conversion efficiency is 40%."
        assert "efciency" not in result

    def test_coefcient_to_coefficient(self):
        md = "Pearson correlation coefcient"
        result = repair_broken_ligatures(md)
        assert result == "Pearson correlation coefficient"
        assert "coefcient" not in result

    def test_multiple_broken_words(self):
        md = "The magnetic feld and confnement parameters show good efciency."
        result = repair_broken_ligatures(md)
        assert result == "The magnetic field and confinement parameters show good efficiency."
        assert "feld" not in result
        assert "confnement" not in result
        assert "efciency" not in result

    def test_author_names_preserved(self):
        """Verify author names like Cosfeld, Guttenfelder, Zehrfeld are NOT changed."""
        md = "J. Coenen, J. Cosfeld, A. Dinklage, W. Guttenfelder, and H. P. Zehrfeld"
        result = repair_broken_ligatures(md)
        assert result == md  # Should be unchanged
        assert "Cosfeld" in result
        assert "Guttenfelder" in result
        assert "Zehrfeld" in result

    def test_word_boundary_matching(self):
        """Whole-word matching prevents false positives in compound words."""
        md = "Newfeld and Greenfeld are locations, not fields."
        result = repair_broken_ligatures(md)
        # Should NOT change "feld" in Newfeld/Greenfeld as they're not whole-word matches
        assert result == md

    def test_no_broken_ligatures_unchanged(self):
        md = "Normal text with field, confinement, efficiency, coefficient."
        result = repair_broken_ligatures(md)
        assert result == md


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

    def test_embedded_bold_no_space_demoted(self):
        md = "## Design****Overview"
        assert reject_noise_headers(md) == "Design****Overview"

    # --- H1 equation fragments (energy_amplifier patterns) ---

    def test_h1_integral_symbol_demoted(self):
        """H1 with integral symbol (∫) should be demoted."""
        md = "# ∫ E 2"
        assert reject_noise_headers(md) == "∫ E 2"

    def test_h1_phi_psi_demoted(self):
        """H1 with Greek letters φ, ψ should be demoted."""
        md = "# φ ψ"
        assert reject_noise_headers(md) == "φ ψ"

    def test_h1_summation_demoted(self):
        """H1 with summation notation should be demoted."""
        md = "# ∑ n=1"
        assert reject_noise_headers(md) == "∑ n=1"

    def test_h1_greek_epsilon_demoted(self):
        """H1 with Greek epsilon (ε) should be demoted."""
        md = "# ε = 0.5"
        assert reject_noise_headers(md) == "ε = 0.5"

    def test_h1_greek_rho_demoted(self):
        """H1 with Greek rho (ρ) should be demoted."""
        md = "# ρ density"
        assert reject_noise_headers(md) == "ρ density"

    def test_h1_greek_sigma_demoted(self):
        """H1 with Greek sigma (σ) should be demoted."""
        md = "# σ cross section"
        assert reject_noise_headers(md) == "σ cross section"

    def test_h1_greek_lambda_demoted(self):
        """H1 with Greek lambda (λ) should be demoted."""
        md = "# λ wavelength"
        assert reject_noise_headers(md) == "λ wavelength"

    def test_h1_product_symbol_demoted(self):
        """H1 with product symbol (∏) should be demoted."""
        md = "# ∏ i=1"
        assert reject_noise_headers(md) == "∏ i=1"

    def test_h1_equation_mixed_symbols_demoted(self):
        """H1 with multiple equation symbols should be demoted."""
        md = "# ∫ φ(x) dx"
        assert reject_noise_headers(md) == "∫ φ(x) dx"

    # --- H1 legitimate headings must be preserved ---

    def test_h1_document_title_preserved(self):
        """Legitimate H1 document title should be preserved."""
        md = "# Energy Amplifier for Cleaner Nuclear Energy"
        assert reject_noise_headers(md) == "# Energy Amplifier for Cleaner Nuclear Energy"

    def test_h1_introduction_preserved(self):
        """Legitimate H1 introduction heading should be preserved."""
        md = "# 1 Introduction"
        assert reject_noise_headers(md) == "# 1 Introduction"

    def test_h1_long_section_title_preserved(self):
        """Legitimate H1 with long title should be preserved."""
        md = "# 2 Advanced Reactor Concepts and Safety Analysis"
        assert reject_noise_headers(md) == "# 2 Advanced Reactor Concepts and Safety Analysis"

    def test_h1_mixed_with_h2_preserved(self):
        """H1 legitimate and H2 noise should be handled independently."""
        md = "# 1 Introduction\n\n## ∫ E 2\n\n## 2 Methods"
        result = reject_noise_headers(md)
        assert "# 1 Introduction" in result
        assert "## 2 Methods" in result
        assert "## ∫ E 2" not in result
        assert "∫ E 2" in result

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


# ---------------------------------------------------------------------------
# promote_bold_allcaps_headers (learning test + unit tests)
# ---------------------------------------------------------------------------


class TestBoldAllCapsLearningTest:
    """Learning test demonstrating the gap between existing promoters.

    Bold all-caps headings like **ABSTRACT** fall through:
    - _ALLCAPS_HEADER_RE (requires no bold markers)
    - _UNNUMBERED_BOLD_HEADER_RE (requires 15+ chars)
    """

    def test_bold_abstract_fails_allcaps_promoter(self):
        """**ABSTRACT** not promoted by promote_allcaps_headers (requires no bold)."""
        md = "\n\n**ABSTRACT**\n\n"
        result = promote_allcaps_headers(md)
        # Should NOT be promoted - pattern requires no bold markers
        assert result == "\n\n**ABSTRACT**\n\n"

    def test_bold_abstract_fails_unnumbered_bold_promoter(self):
        """**ABSTRACT** not promoted by promote_unnumbered_bold_headers (too short)."""
        md = "**ABSTRACT**"
        result = promote_unnumbered_bold_headers(md)
        # Should NOT be promoted - only 8 chars, needs 15+
        assert result == "**ABSTRACT**"

    def test_bold_abstract_promoted_by_new_function(self):
        """**ABSTRACT** IS promoted by promote_bold_allcaps_headers."""
        md = "\n\n**ABSTRACT**\n\n"
        result = promote_bold_allcaps_headers(md)
        # Should be promoted to ## heading with title-casing
        assert result == "\n\n## Abstract\n\n"


class TestPromoteBoldAllCapsHeaders:
    """Unit tests for promote_bold_allcaps_headers function."""

    def test_single_word_known_heading(self):
        """Single-word known headings are promoted."""
        md = "\n\n**ABSTRACT**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## Abstract\n\n"

    def test_contents_heading(self):
        md = "\n\n**CONTENTS**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## Contents\n\n"

    def test_acronyms_heading(self):
        md = "\n\n**ACRONYMS**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## Acronyms\n\n"

    def test_references_heading(self):
        md = "\n\n**REFERENCES**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## References\n\n"

    def test_multi_word_heading(self):
        """Multi-word all-caps headings are promoted."""
        md = "\n\n**LIST OF TABLES**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## List Of Tables\n\n"

    def test_introduction_heading(self):
        md = "\n\n**INTRODUCTION**\n\n"
        assert promote_bold_allcaps_headers(md) == "\n\n## Introduction\n\n"

    def test_requires_blank_lines(self):
        """Must be between blank lines - no promotion without boundaries."""
        md = "text\n**ABSTRACT**\nmore text"
        # No blank lines before/after, should not promote
        assert promote_bold_allcaps_headers(md) == md

    def test_rejects_toc_entries_with_dot_leaders(self):
        """TOC entries with dot leaders are rejected."""
        md = "\n\n**ABSTRACT . . . . . 5**\n\n"
        assert promote_bold_allcaps_headers(md) == md

    def test_rejects_short_abbreviations(self):
        """Short all-caps abbreviations without spaces are rejected."""
        md = "\n\n**MW**\n\n"
        # Not a known single-word heading, no spaces, should not promote
        assert promote_bold_allcaps_headers(md) == md

    def test_rejects_short_abbreviation_hts(self):
        md = "\n\n**HTS**\n\n"
        assert promote_bold_allcaps_headers(md) == md

    def test_multiple_headings_in_document(self):
        """Multiple bold all-caps headings are all promoted."""
        md = (
            "Some text.\n"
            "\n"
            "**CONTENTS**\n"
            "\n"
            "Table of contents text.\n"
            "\n"
            "**ABSTRACT**\n"
            "\n"
            "Abstract text.\n"
            "\n"
            "**REFERENCES**\n"
            "\n"
            "References here.\n"
        )
        result = promote_bold_allcaps_headers(md)
        assert "## Contents" in result
        assert "## Abstract" in result
        assert "## References" in result

    def test_preserves_surrounding_content(self):
        """Content around promoted headings is preserved."""
        md = "Before\n\n**ABSTRACT**\n\nAfter"
        result = promote_bold_allcaps_headers(md)
        assert result == "Before\n\n## Abstract\n\nAfter"

    def test_title_casing_applied(self):
        """Headings are title-cased for readability."""
        md = "\n\n**LIST OF FIGURES**\n\n"
        result = promote_bold_allcaps_headers(md)
        # Should be title-cased
        assert "## List Of Figures" in result


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
