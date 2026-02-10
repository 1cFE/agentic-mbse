"""Tests for ExtractionOrchestrator (spec 008).

Verifies extraction loop logic: quality-ordered source iteration, fetch → validate →
convert pipeline, outcome recording, and early exit on success.
"""

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from doc_ingest.converters.base import Converter
from doc_ingest.converters.registry import ConverterRegistry
from doc_ingest.extraction_orchestrator import ExtractionOrchestrator
from doc_ingest.types import (
    ConversionError,
    ConversionResult,
    QualityFlags,
    SourceCandidate,
    ValidationResult,
)
from doc_ingest.web_fetcher import FetchError


class TestExtractionOrchestrator:
    """Test suite for ExtractionOrchestrator.orchestrate()."""

    @pytest.fixture
    def registry(self) -> ConverterRegistry:
        """Create a fresh ConverterRegistry instance."""
        return ConverterRegistry()

    @pytest.fixture
    def orchestrator(self, registry: ConverterRegistry) -> ExtractionOrchestrator:
        """Create a fresh ExtractionOrchestrator with empty registry."""
        return ExtractionOrchestrator(registry)

    @pytest.fixture
    def mock_converter(self) -> Mock:
        """Create a mock converter with default success behavior."""
        converter = Mock(spec=Converter)
        converter.name = "MockConverter"
        converter.validate_source.return_value = ValidationResult(
            is_valid=True,
            content_length=1000,
            has_body_content=True,
        )
        converter.convert.return_value = ConversionResult(
            markdown="# Mock Document\n\nContent here.",
            warnings=[],
            quality_flags=QualityFlags(),
            converter_name="MockConverter",
        )
        return converter

    @pytest.fixture
    def mock_fetch_fn(self) -> Callable[[SourceCandidate], bytes]:
        """Create a mock fetch function that returns dummy bytes."""

        def fetch(source: SourceCandidate) -> bytes:
            return b"dummy content"

        return fetch

    # Success cases: early exit on first success

    def test_orchestrate_early_exit_on_first_success(
        self, registry: ConverterRegistry, mock_converter: Mock, mock_fetch_fn: Callable
    ) -> None:
        """Given 3 sources where first succeeds, then return 1 attempt and skip remaining sources."""
        # Setup: Register converter for JATS format
        registry.register("jats_xml", mock_converter)

        # Create 3 sources sorted by quality tier (JATS=1, arXiv=2, PDF=4)
        sources = [
            SourceCandidate(
                quality_tier=1,
                format="jats_xml",
                url="http://example.com/paper.jats.xml",
                discovered_via="openalex",
            ),
            SourceCandidate(
                quality_tier=2,
                format="arxiv_html",
                url="http://arxiv.org/html/2301.00001",
                discovered_via="arxiv_api",
            ),
            SourceCandidate(
                quality_tier=4,
                format="pdf",
                url="http://example.com/paper.pdf",
                discovered_via="openalex",
            ),
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: Only 1 attempt (JATS succeeded, others skipped)
        assert len(attempts) == 1
        assert attempts[0].outcome == "success"
        assert attempts[0].source_url == "http://example.com/paper.jats.xml"
        assert attempts[0].converter_name == "MockConverter"
        assert result is not None
        assert result.markdown == "# Mock Document\n\nContent here."

    def test_orchestrate_tries_all_sources_until_success(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given 3 sources where first two fail validation and third succeeds, then return 3 attempts."""
        # Setup: Create two converters - one that fails validation, one that succeeds
        failing_converter = Mock(spec=Converter)
        failing_converter.name = "FailingConverter"
        failing_converter.validate_source.return_value = ValidationResult(
            is_valid=False,
            content_length=500,
            has_body_content=False,
        )

        succeeding_converter = Mock(spec=Converter)
        succeeding_converter.name = "SucceedingConverter"
        succeeding_converter.validate_source.return_value = ValidationResult(
            is_valid=True,
            content_length=5000,
            has_body_content=True,
        )
        succeeding_converter.convert.return_value = ConversionResult(
            markdown="# PDF Content",
            warnings=[],
            quality_flags=QualityFlags(),
            converter_name="SucceedingConverter",
        )

        # Register converters
        registry.register("jats_xml", failing_converter)
        registry.register("arxiv_html", failing_converter)
        registry.register("pdf", succeeding_converter)

        # Create 3 sources
        sources = [
            SourceCandidate(
                quality_tier=1,
                format="jats_xml",
                url="http://example.com/paper.jats.xml",
            ),
            SourceCandidate(
                quality_tier=2, format="arxiv_html", url="http://arxiv.org/html/2301.00001"
            ),
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf"),
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: 3 attempts (2 validation_failed, 1 success)
        assert len(attempts) == 3
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].failure_category == "source_validation_failed"
        assert attempts[1].outcome == "validation_failed"
        assert attempts[1].failure_category == "source_validation_failed"
        assert attempts[2].outcome == "success"
        assert result is not None
        assert result.markdown == "# PDF Content"

    # All sources fail: return all attempts with no result

    def test_orchestrate_all_sources_fail_returns_all_attempts(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given all sources fail, then return all attempts with no successful result."""
        # Setup: Create converter that always fails validation
        failing_converter = Mock(spec=Converter)
        failing_converter.name = "FailingConverter"
        failing_converter.validate_source.return_value = ValidationResult(
            is_valid=False,
            content_length=100,
            has_body_content=False,
        )

        registry.register("jats_xml", failing_converter)
        registry.register("pdf", failing_converter)

        sources = [
            SourceCandidate(
                quality_tier=1, format="jats_xml", url="http://example.com/paper.jats.xml"
            ),
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf"),
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: All attempts recorded, no result
        assert len(attempts) == 2
        assert attempts[0].outcome == "validation_failed"
        assert attempts[1].outcome == "validation_failed"
        assert result is None

    # Fetch failures: outcome="fetch_failed"

    def test_orchestrate_fetch_error_records_fetch_failed(
        self, orchestrator: ExtractionOrchestrator
    ) -> None:
        """Given fetch raises FetchError, then record outcome="fetch_failed"."""

        def failing_fetch_fn(source: SourceCandidate) -> bytes:
            raise FetchError("Network timeout", category="timeout")

        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf")
        ]

        attempts, result = orchestrator.orchestrate(sources, failing_fetch_fn)

        # Verify: Fetch failure recorded
        assert len(attempts) == 1
        assert attempts[0].outcome == "fetch_failed"
        assert attempts[0].failure_category is None
        assert attempts[0].converter_name is None
        assert result is None

    # Conversion errors: preserve failure_category

    def test_orchestrate_conversion_error_preserves_category(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given converter raises ConversionError(category="needs_ocr"), then preserve category in attempt."""
        # Setup: Converter that raises ConversionError
        converter = Mock(spec=Converter)
        converter.name = "PDFConverter"
        converter.validate_source.return_value = ValidationResult(
            is_valid=True,
            content_length=10000,
            has_body_content=True,
        )
        converter.convert.side_effect = ConversionError(
            "No text detected in PDF", category="needs_ocr", details={"pages": 120}
        )

        registry.register("pdf", converter)

        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/scanned.pdf")
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: Failure category preserved
        assert len(attempts) == 1
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].failure_category == "needs_ocr"
        assert attempts[0].converter_name == "PDFConverter"
        assert result is None

    # Unexpected exceptions: wrap as category="unknown"

    def test_orchestrate_unexpected_exception_wraps_as_unknown(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given converter raises unexpected exception, then record failure_category="unknown"."""
        # Setup: Converter that raises unexpected exception
        converter = Mock(spec=Converter)
        converter.name = "BuggyConverter"
        converter.validate_source.return_value = ValidationResult(
            is_valid=True,
            content_length=1000,
            has_body_content=True,
        )
        converter.convert.side_effect = RuntimeError("Unexpected bug in converter")

        registry.register("pdf", converter)

        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf")
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: Exception wrapped as category="unknown"
        assert len(attempts) == 1
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].failure_category == "unknown"
        assert attempts[0].converter_name == "BuggyConverter"
        assert result is None

    # Source sorting: quality tier primary, URL secondary

    def test_orchestrate_sorts_sources_by_quality_tier(
        self, registry: ConverterRegistry, mock_converter: Mock, mock_fetch_fn: Callable
    ) -> None:
        """Given unsorted sources, then orchestrate processes them in quality tier order."""
        # Register converter for all formats
        registry.register("pdf", mock_converter)
        registry.register("jats_xml", mock_converter)
        registry.register("arxiv_html", mock_converter)

        # Create sources in reverse quality order (PDF=4, arXiv=2, JATS=1)
        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf"),
            SourceCandidate(
                quality_tier=2, format="arxiv_html", url="http://arxiv.org/html/2301.00001"
            ),
            SourceCandidate(
                quality_tier=1, format="jats_xml", url="http://example.com/paper.jats.xml"
            ),
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: Only JATS attempted (tier=1, best quality)
        assert len(attempts) == 1
        assert attempts[0].source_url == "http://example.com/paper.jats.xml"
        assert attempts[0].outcome == "success"

    # No converter registered for format

    def test_orchestrate_no_converter_for_format(
        self, orchestrator: ExtractionOrchestrator, mock_fetch_fn: Callable
    ) -> None:
        """Given source format has no registered converter, then record validation_failed."""
        # Empty registry - no converters registered
        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf")
        ]

        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: No converter → validation_failed with unsupported_format
        assert len(attempts) == 1
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].failure_category == "unsupported_format"
        assert attempts[0].converter_name is None
        assert result is None

    # Paywall detection: populate is_paywall field

    def test_orchestrate_paywall_detection_sets_flag(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given validation detects paywall, then attempt has is_paywall=True."""
        # Setup: Converter that detects paywall
        converter = Mock(spec=Converter)
        converter.name = "HTMLConverter"
        converter.validate_source.return_value = ValidationResult(
            is_valid=False,
            content_length=500,
            has_body_content=False,
            is_paywall=True,
        )

        registry.register("publisher_html", converter)

        sources = [
            SourceCandidate(
                quality_tier=3,
                format="publisher_html",
                url="http://publisher.com/paywalled.html",
            )
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: is_paywall flag populated
        assert len(attempts) == 1
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].is_paywall is True

    # Local path sources: use local_path in attempt record

    def test_orchestrate_local_path_source(
        self, registry: ConverterRegistry, mock_converter: Mock, mock_fetch_fn: Callable
    ) -> None:
        """Given source with local_path instead of url, then use local_path in attempt record."""
        registry.register("pdf", mock_converter)

        sources = [
            SourceCandidate(
                quality_tier=4,
                format="pdf",
                local_path="/path/to/local/paper.pdf",
                discovered_via="local_scan",
            )
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: local_path used as source_url
        assert len(attempts) == 1
        assert attempts[0].source_url == "/path/to/local/paper.pdf"
        assert attempts[0].outcome == "success"

    # Validation exception handling

    def test_orchestrate_validation_exception_wraps_as_unknown(
        self, registry: ConverterRegistry, mock_fetch_fn: Callable
    ) -> None:
        """Given validate_source raises unexpected exception, then record failure_category="unknown"."""
        # Setup: Converter with buggy validate_source
        converter = Mock(spec=Converter)
        converter.name = "BuggyValidator"
        converter.validate_source.side_effect = RuntimeError("Validation bug")

        registry.register("pdf", converter)

        sources = [
            SourceCandidate(quality_tier=4, format="pdf", url="http://example.com/paper.pdf")
        ]

        orchestrator = ExtractionOrchestrator(registry)
        attempts, result = orchestrator.orchestrate(sources, mock_fetch_fn)

        # Verify: Validation exception wrapped as unknown
        assert len(attempts) == 1
        assert attempts[0].outcome == "validation_failed"
        assert attempts[0].failure_category == "unknown"
        assert attempts[0].converter_name == "BuggyValidator"
        assert result is None
