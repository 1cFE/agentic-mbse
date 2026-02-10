"""Tests for ConversionError exception class."""

import pytest

from src.doc_ingest.types import ConversionError


class TestConversionError:
    """Tests for ConversionError exception class."""

    def test_basic_construction_with_message_and_category(self) -> None:
        """Given message and category, when constructed, then stores both."""
        error = ConversionError("No text found", category="needs_ocr")
        assert str(error) == "No text found"
        assert error.category == "needs_ocr"
        assert error.details == {}

    def test_construction_with_details(self) -> None:
        """Given details dict, when constructed, then stores details."""
        error = ConversionError(
            "No text found",
            category="needs_ocr",
            details={"pages": 120, "file_size": 1024000},
        )
        assert error.category == "needs_ocr"
        assert error.details == {"pages": 120, "file_size": 1024000}

    def test_none_details_defaults_to_empty_dict(self) -> None:
        """Given details=None, when constructed, then details is empty dict."""
        error = ConversionError("Failed", category="unknown", details=None)
        assert error.details == {}

    def test_is_exception_subclass(self) -> None:
        """Given ConversionError, when checked, then is Exception subclass."""
        error = ConversionError("Test", category="unknown")
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        """Given ConversionError raised, when caught, then attributes accessible."""
        with pytest.raises(ConversionError) as exc_info:
            raise ConversionError("Paywall detected", category="source_validation_failed")

        assert exc_info.value.category == "source_validation_failed"
        assert str(exc_info.value) == "Paywall detected"

    def test_repr_includes_category_and_message(self) -> None:
        """Given ConversionError, when repr called, then includes category and message."""
        error = ConversionError("Test error", category="needs_ocr")
        repr_str = repr(error)
        assert "needs_ocr" in repr_str
        assert "Test error" in repr_str

    def test_repr_includes_details_when_present(self) -> None:
        """Given ConversionError with details, when repr called, then includes details."""
        error = ConversionError("Test", category="unknown", details={"key": "value"})
        repr_str = repr(error)
        assert "details=" in repr_str
        assert "key" in repr_str

    def test_repr_omits_details_when_empty(self) -> None:
        """Given ConversionError without details, when repr called, then no details field."""
        error = ConversionError("Test", category="unknown")
        repr_str = repr(error)
        # Should not have ", details={}" in repr for cleaner output
        assert ", details={}" not in repr_str

    def test_all_failure_categories_accepted(self) -> None:
        """Given all valid failure categories, when constructed, then no type errors."""
        categories = [
            "needs_ocr",
            "table_corruption",
            "no_source_found",
            "source_validation_failed",
            "conversion_timeout",
            "unsupported_format",
            "api_error",
            "network_error",
            "unknown",
        ]
        for category in categories:
            error = ConversionError(f"Test {category}", category=category)  # type: ignore[arg-type]
            assert error.category == category

    def test_category_stored_as_attribute_not_just_in_message(self) -> None:
        """Given category, when accessed, then available as typed field not parsed from message."""
        error = ConversionError("Something went wrong", category="api_error")
        # Category is directly accessible, not inferred from message
        assert error.category == "api_error"
        # Message doesn't need to mention the category
        assert "api_error" not in str(error)

    def test_supports_exception_chaining(self) -> None:
        """Given original exception, when wrapped in ConversionError, then chain preserved."""
        original = ValueError("Invalid format")
        try:
            raise ConversionError("Conversion failed", category="unsupported_format") from original
        except ConversionError as e:
            assert e.__cause__ is original
            assert isinstance(e.__cause__, ValueError)

    def test_details_dict_can_hold_arbitrary_metadata(self) -> None:
        """Given converter-specific metadata, when stored in details, then retrievable."""
        details = {
            "converter": "pandoc",
            "format_detected": "docx",
            "error_code": 42,
            "warnings": ["table malformed", "image skipped"],
        }
        error = ConversionError("Conversion failed", category="table_corruption", details=details)
        assert error.details["converter"] == "pandoc"
        assert error.details["format_detected"] == "docx"
        assert error.details["error_code"] == 42
        assert len(error.details["warnings"]) == 2

    def test_acceptance_criteria_pdf_no_text(self) -> None:
        """Given PDF converter detects no text, when error raised, then category='needs_ocr'."""
        # Acceptance criteria from spec 017
        error = ConversionError("No text detected in PDF", category="needs_ocr")
        assert error.category == "needs_ocr"

    def test_acceptance_criteria_paywall(self) -> None:
        """Given HTML converter detects paywall, when error raised, then category='source_validation_failed'."""
        # Acceptance criteria from spec 017
        error = ConversionError("Paywall detected", category="source_validation_failed")
        assert error.category == "source_validation_failed"

    def test_acceptance_criteria_pandoc_failure(self) -> None:
        """Given pandoc fails, when error raised, then category='unsupported_format'."""
        # Acceptance criteria from spec 017
        error = ConversionError("Pandoc conversion failed", category="unsupported_format")
        assert error.category == "unsupported_format"

    def test_acceptance_criteria_unexpected_exception_wrapped(self) -> None:
        """Given unexpected exception, when wrapped, then category='unknown'."""
        # Acceptance criteria from spec 017
        try:
            raise RuntimeError("Something unexpected")
        except Exception as e:
            wrapped = ConversionError(f"Unexpected failure: {e}", category="unknown")
            assert wrapped.category == "unknown"
            assert "Unexpected failure" in str(wrapped)
