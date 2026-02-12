"""Tests for AcademicHeaderDetector in pymupdf_backend."""

from pathlib import Path

import pytest

from agentic_mbse.extraction.pymupdf_backend import AcademicHeaderDetector


@pytest.fixture
def detector():
    """Create a detector using a real PDF from the test corpus."""
    corpus_dir = Path(__file__).parent / "corpus" / "pdfs"
    pdf_path = corpus_dir / "sparc_overview.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Test corpus PDF not found: {pdf_path}")

    return AcademicHeaderDetector(str(pdf_path))


class TestPattern2AllCapsHeaders:
    """Tests for Pattern 2: All-caps header detection."""

    def test_multi_word_allcaps_with_body_font_rejected(self, detector):
        """Body-font multi-word all-caps should be rejected (e.g., reference entries)."""
        # Override body font to match our test span
        detector.body_font_family = "TimesNewRoman"

        # Simulate a span with multi-word all-caps text in body font
        span = {
            "text": "AHN, J.-W., GRAY, T., HUGHES, J.",
            "font": "TimesNewRoman-Regular",
            "flags": 0,  # No bold, no italic
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "", "Body-font multi-word all-caps should be rejected"

    def test_multi_word_allcaps_with_bold_accepted(self, detector):
        """Bold multi-word all-caps should be accepted (e.g., section headers)."""
        detector.body_font_family = "TimesNewRoman"

        # Simulate a span with multi-word all-caps text in bold
        span = {
            "text": "SITE IMPROVEMENTS",
            "font": "TimesNewRoman-Bold",
            "flags": 16,  # Bold flag
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "## ", "Bold multi-word all-caps should be accepted as header"

    def test_multi_word_allcaps_with_different_font_accepted(self, detector):
        """Multi-word all-caps with different font family should be accepted."""
        detector.body_font_family = "TimesNewRoman"

        span = {
            "text": "EXECUTIVE SUMMARY",
            "font": "Helvetica-Regular",  # Different font family
            "flags": 0,
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "## ", "Different-font all-caps should be accepted"

    def test_single_word_allcaps_in_known_set_always_accepted(self, detector):
        """Single-word known all-caps headers are accepted regardless of font."""
        detector.body_font_family = "TimesNewRoman"

        # Body font
        span = {
            "text": "ABSTRACT",
            "font": "TimesNewRoman-Regular",
            "flags": 0,
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "## ", "Known single-word headers accepted in body font"

    def test_sparse_letter_allcaps_rejected(self, detector):
        """All-caps text with < 4 alphabetic chars should be rejected."""
        span = {
            "text": ", D. M. 2002",
            "font": "TimesNewRoman-Regular",
            "flags": 0,
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "", "Sparse-letter all-caps should be rejected"

    def test_long_allcaps_rejected(self, detector):
        """All-caps text longer than 60 chars should be rejected."""
        span = {
            "text": "A" * 65,  # 65 characters
            "font": "TimesNewRoman-Bold",
            "flags": 16,
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "", "Very long all-caps should be rejected"


class TestPattern1NumberedSections:
    """Tests for Pattern 1: Numbered section header detection."""

    def test_section_number_over_99_rejected(self, detector):
        """Section numbers > 99 should be rejected (e.g., years, addresses)."""
        span = {
            "text": "2020 Advanced Nuclear Plants",
            "font": "TimesNewRoman-Bold",
            "flags": 16,
            "size": 10.0,
        }

        result = detector(span, page=None)
        assert result == "", "Section numbers > 99 should be rejected"
