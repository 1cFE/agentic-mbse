"""Tests for ValidationResult dataclass (spec 010)."""

from src.doc_ingest.types import ValidationResult


def test_validation_result_valid_jats_xml():
    """Valid JATS XML with body content should set is_valid and has_body_content."""
    result = ValidationResult(is_valid=True, content_length=5000, has_body_content=True)

    assert result.is_valid is True
    assert result.content_length == 5000
    assert result.has_body_content is True
    assert result.detected_content_type is None  # Optional field defaults to None
    assert result.is_paywall is None
    assert result.is_truncated is None


def test_validation_result_paywall_detected():
    """HTML with paywall marker should set is_valid=False and is_paywall=True."""
    result = ValidationResult(is_valid=False, content_length=2048, is_paywall=True)

    assert result.is_valid is False
    assert result.content_length == 2048
    assert result.is_paywall is True
    assert result.has_body_content is None
    assert result.detected_content_type is None
    assert result.is_truncated is None


def test_validation_result_truncated_response():
    """Truncated response (< 1KB) should set is_valid=False, is_truncated=True."""
    result = ValidationResult(is_valid=False, content_length=512, is_truncated=True)

    assert result.is_valid is False
    assert result.content_length == 512
    assert result.is_truncated is True
    assert result.content_length < 1024  # Verification from spec
    assert result.has_body_content is None
    assert result.detected_content_type is None
    assert result.is_paywall is None


def test_validation_result_valid_pdf():
    """Valid PDF with minimal metadata should set is_valid and content_length."""
    result = ValidationResult(is_valid=True, content_length=102400)

    assert result.is_valid is True
    assert result.content_length == 102400
    assert result.content_length > 0  # Verification from spec
    # Optional fields may be None for PDF validation
    assert result.has_body_content is None
    assert result.detected_content_type is None
    assert result.is_paywall is None
    assert result.is_truncated is None


def test_validation_result_all_fields_set():
    """All optional fields can be set together."""
    result = ValidationResult(
        is_valid=True,
        content_length=10240,
        has_body_content=True,
        detected_content_type="application/xml",
        is_paywall=False,
        is_truncated=False,
    )

    assert result.is_valid is True
    assert result.content_length == 10240
    assert result.has_body_content is True
    assert result.detected_content_type == "application/xml"
    assert result.is_paywall is False
    assert result.is_truncated is False


def test_validation_result_serialization_preserves_fields():
    """Validation result should preserve all set fields when serialized.

    This test verifies the requirement that all set fields are preserved
    when serialized to provenance (e.g., via dataclasses.asdict).
    """
    from dataclasses import asdict

    result = ValidationResult(
        is_valid=True,
        content_length=8192,
        has_body_content=True,
        detected_content_type="text/html",
        is_paywall=False,
        is_truncated=False,
    )

    serialized = asdict(result)

    assert serialized["is_valid"] is True
    assert serialized["content_length"] == 8192
    assert serialized["has_body_content"] is True
    assert serialized["detected_content_type"] == "text/html"
    assert serialized["is_paywall"] is False
    assert serialized["is_truncated"] is False


def test_validation_result_partial_fields_serialization():
    """Serialization should include None values for unset optional fields."""
    from dataclasses import asdict

    result = ValidationResult(is_valid=False, content_length=100, is_truncated=True)

    serialized = asdict(result)

    # All fields present in serialized dict
    assert "is_valid" in serialized
    assert "content_length" in serialized
    assert "has_body_content" in serialized
    assert "detected_content_type" in serialized
    assert "is_paywall" in serialized
    assert "is_truncated" in serialized

    # Set fields have correct values
    assert serialized["is_valid"] is False
    assert serialized["content_length"] == 100
    assert serialized["is_truncated"] is True

    # Unset optional fields are None
    assert serialized["has_body_content"] is None
    assert serialized["detected_content_type"] is None
    assert serialized["is_paywall"] is None
