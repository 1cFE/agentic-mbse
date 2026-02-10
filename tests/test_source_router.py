"""Unit tests for SourceRouter (spec 007)."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from doc_ingest.outcome_classifier import ExtractionAttempt, OutcomeClassifier
from doc_ingest.source_router import SourceRouter
from doc_ingest.types import (
    ConversionResult,
    DocumentIdentifiers,
    ProvenanceRecord,
    QualityFlags,
    SourceCandidate,
)


@pytest.fixture
def mock_discoverer():
    """Create mock SourceDiscoverer."""
    discoverer = Mock()
    discoverer.discover.return_value = ([], [])
    return discoverer


@pytest.fixture
def mock_orchestrator():
    """Create mock ExtractionOrchestrator."""
    orchestrator = Mock()
    orchestrator.orchestrate.return_value = ([], None)
    return orchestrator


@pytest.fixture
def mock_classifier():
    """Create real OutcomeClassifier (no mocking needed)."""
    return OutcomeClassifier()


@pytest.fixture
def mock_provenance_manager(tmp_path):
    """Create mock ProvenanceManager."""
    manager = Mock()
    manager._compute_hash.return_value = "test_hash_123"
    manager.load.return_value = None
    manager.write.return_value = None
    return manager


@pytest.fixture
def mock_fetcher():
    """Create mock WebFetcher."""
    fetcher = Mock()
    fetcher.fetch.return_value = b"test content"
    return fetcher


@pytest.fixture
def router(
    mock_discoverer, mock_orchestrator, mock_classifier, mock_provenance_manager, mock_fetcher
):
    """Create SourceRouter with mocked dependencies."""
    return SourceRouter(
        discoverer=mock_discoverer,
        orchestrator=mock_orchestrator,
        classifier=mock_classifier,
        provenance_manager=mock_provenance_manager,
        fetcher=mock_fetcher,
    )


def test_extract_success_returns_markdown(router, mock_discoverer, mock_orchestrator, tmp_path):
    """Test successful extraction returns markdown and provenance."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="test",
        )
    ]
    mock_discoverer.discover.return_value = (sources, [])

    conversion_result = ConversionResult(
        markdown="# Test Paper\n\nContent here.",
        warnings=[],
        quality_flags=QualityFlags(),
        converter_name="JATSConverter",
    )
    attempts = [
        ExtractionAttempt(
            source_url="https://example.com/paper.xml",
            outcome="success",
            converter_name="JATSConverter",
        )
    ]
    mock_orchestrator.orchestrate.return_value = (attempts, conversion_result)

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown == "# Test Paper\n\nContent here."
    assert result.provenance.outcome == "success"
    assert result.provenance.final_converter == "JATSConverter"
    assert result.provenance.failure_category is None
    assert len(result.provenance.attempts) == 1


def test_extract_all_sources_fail(router, mock_discoverer, mock_orchestrator, tmp_path):
    """Test all sources failing returns None markdown with failed outcome."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="test",
        )
    ]
    mock_discoverer.discover.return_value = (sources, [])

    attempts = [
        ExtractionAttempt(
            source_url="https://example.com/paper.xml",
            outcome="validation_failed",
            failure_category="source_validation_failed",
            converter_name="JATSConverter",
        )
    ]
    mock_orchestrator.orchestrate.return_value = (attempts, None)

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown is None
    assert result.provenance.outcome == "failed"
    assert result.provenance.failure_category == "source_validation_failed"
    assert result.provenance.final_converter is None


def test_extract_resumability_skip_success(router, mock_provenance_manager, tmp_path):
    """Test existing success skips extraction and returns cached markdown."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")

    # Create existing provenance with success outcome
    existing_provenance = ProvenanceRecord(
        document_id=identifiers,
        discovered_sources=[],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[],
        outcome="success",
        final_converter="JATSConverter",
        failure_category=None,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=5.0,
    )
    mock_provenance_manager.load.return_value = existing_provenance

    # Create mock markdown file
    doc_dir = tmp_path / "test_hash_123"
    doc_dir.mkdir()
    markdown_path = doc_dir / "output.md"
    markdown_path.write_text("# Cached Paper\n\nCached content.", encoding="utf-8")

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown == "# Cached Paper\n\nCached content."
    assert result.provenance == existing_provenance
    # Verify discovery and orchestration were NOT called
    assert not router._discoverer.discover.called
    assert not router._orchestrator.orchestrate.called


def test_extract_resumability_retry_failed(
    router, mock_discoverer, mock_orchestrator, mock_provenance_manager, tmp_path
):
    """Test existing failed provenance triggers retry."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")

    # Create existing provenance with failed outcome
    existing_provenance = ProvenanceRecord(
        document_id=identifiers,
        discovered_sources=[],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[],
        outcome="failed",
        final_converter=None,
        failure_category="network_error",
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=2.0,
    )
    mock_provenance_manager.load.return_value = existing_provenance

    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="test",
        )
    ]
    mock_discoverer.discover.return_value = (sources, [])

    conversion_result = ConversionResult(
        markdown="# Test Paper\n\nRetried successfully.",
        warnings=[],
        quality_flags=QualityFlags(),
        converter_name="JATSConverter",
    )
    attempts = [
        ExtractionAttempt(
            source_url="https://example.com/paper.xml",
            outcome="success",
            converter_name="JATSConverter",
        )
    ]
    mock_orchestrator.orchestrate.return_value = (attempts, conversion_result)

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown == "# Test Paper\n\nRetried successfully."
    assert result.provenance.outcome == "success"
    # Verify discovery and orchestration WERE called (retry happened)
    mock_discoverer.discover.assert_called_once()
    mock_orchestrator.orchestrate.assert_called_once()


def test_extract_format_override_skips_discovery(
    router, mock_discoverer, mock_orchestrator, tmp_path
):
    """Test format override skips discovery and uses specified format."""
    # Arrange
    identifiers = DocumentIdentifiers(local_path="/tmp/paper.pdf")

    conversion_result = ConversionResult(
        markdown="# PDF Paper\n\nExtracted from PDF.",
        warnings=[],
        quality_flags=QualityFlags(),
        converter_name="PDFConverter",
    )
    attempts = [
        ExtractionAttempt(
            source_url="/tmp/paper.pdf",
            outcome="success",
            converter_name="PDFConverter",
        )
    ]
    mock_orchestrator.orchestrate.return_value = (attempts, conversion_result)

    # Act
    result = router.extract(identifiers, tmp_path, format_override="pdf")

    # Assert
    assert result.markdown == "# PDF Paper\n\nExtracted from PDF."
    # Verify discovery was NOT called
    mock_discoverer.discover.assert_not_called()
    # Verify orchestrator was called with format-override source
    mock_orchestrator.orchestrate.assert_called_once()
    called_sources = mock_orchestrator.orchestrate.call_args[0][0]
    assert len(called_sources) == 1
    assert called_sources[0].format == "pdf"
    assert called_sources[0].discovered_via == "format_override"


def test_extract_provenance_written_on_crash(
    router, mock_discoverer, mock_orchestrator, mock_provenance_manager, tmp_path
):
    """Test provenance is written even if extraction crashes."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="test",
        )
    ]
    mock_discoverer.discover.return_value = (sources, [])

    # Simulate crash during orchestration
    mock_orchestrator.orchestrate.side_effect = RuntimeError("Unexpected error")

    # Act & Assert
    with pytest.raises(RuntimeError):
        router.extract(identifiers, tmp_path)

    # Verify provenance was written despite crash
    mock_provenance_manager.write.assert_called_once()
    written_provenance = mock_provenance_manager.write.call_args[0][1]
    assert written_provenance.outcome == "failed"
    assert written_provenance.failure_category in ["no_source_found", "unknown"]


def test_extract_no_sources_found(router, mock_discoverer, mock_orchestrator, tmp_path):
    """Test no sources discovered results in failed outcome with no_source_found category."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    mock_discoverer.discover.return_value = ([], [])

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown is None
    assert result.provenance.outcome == "failed"
    assert result.provenance.failure_category == "no_source_found"
    assert len(result.provenance.attempts) == 0


def test_extract_discovery_errors_reported(router, mock_discoverer, mock_orchestrator, tmp_path):
    """Test discovery errors are included in provenance."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    discovery_errors = ["OpenAlex API timeout", "arXiv API rate limit"]
    mock_discoverer.discover.return_value = ([], discovery_errors)

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown is None
    assert result.provenance.outcome == "failed"
    assert result.provenance.failure_category == "api_error"
    assert result.provenance.discovery_errors == discovery_errors


def test_extract_format_override_without_local_path(router, mock_orchestrator, tmp_path):
    """Test format override creates stub URL when no local_path present."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")

    conversion_result = ConversionResult(
        markdown="# Test Paper",
        warnings=[],
        quality_flags=QualityFlags(),
        converter_name="JATSConverter",
    )
    attempts = [
        ExtractionAttempt(
            source_url="stub://doi/10.1234/test",
            outcome="success",
            converter_name="JATSConverter",
        )
    ]
    mock_orchestrator.orchestrate.return_value = (attempts, conversion_result)

    # Act
    result = router.extract(identifiers, tmp_path, format_override="jats_xml")

    # Assert
    assert result.markdown == "# Test Paper"
    # Verify orchestrator was called with stub URL
    called_sources = mock_orchestrator.orchestrate.call_args[0][0]
    assert len(called_sources) == 1
    assert called_sources[0].url == "stub://doi/10.1234/test"
    assert called_sources[0].format == "jats_xml"


def test_extract_provenance_includes_all_attempts(
    router, mock_discoverer, mock_orchestrator, tmp_path
):
    """Test provenance includes all extraction attempts."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="test",
        ),
        SourceCandidate(
            quality_tier=2,
            format="arxiv_html",
            url="https://arxiv.org/html/1234.5678",
            discovered_via="test",
        ),
    ]
    mock_discoverer.discover.return_value = (sources, [])

    # First attempt fails, second succeeds
    attempts = [
        ExtractionAttempt(
            source_url="https://example.com/paper.xml",
            outcome="validation_failed",
            failure_category="source_validation_failed",
            converter_name="JATSConverter",
        ),
        ExtractionAttempt(
            source_url="https://arxiv.org/html/1234.5678",
            outcome="success",
            converter_name="ArXivConverter",
        ),
    ]
    conversion_result = ConversionResult(
        markdown="# Test Paper",
        warnings=[],
        quality_flags=QualityFlags(),
        converter_name="ArXivConverter",
    )
    mock_orchestrator.orchestrate.return_value = (attempts, conversion_result)

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.markdown == "# Test Paper"
    assert result.provenance.outcome == "success"
    assert len(result.provenance.attempts) == 2
    assert result.provenance.attempts[0].outcome == "validation_failed"
    assert result.provenance.attempts[1].outcome == "success"


def test_extract_provenance_timestamps_recorded(
    router, mock_discoverer, mock_orchestrator, tmp_path
):
    """Test provenance includes timestamps and elapsed time."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = []
    mock_discoverer.discover.return_value = (sources, [])

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.provenance.created_at is not None
    assert result.provenance.total_elapsed_seconds >= 0
    # Verify timestamp is ISO 8601 format
    datetime.fromisoformat(result.provenance.created_at)


def test_extract_pipeline_version_recorded(router, mock_discoverer, mock_orchestrator, tmp_path):
    """Test provenance includes pipeline version."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    sources = []
    mock_discoverer.discover.return_value = (sources, [])

    # Act
    result = router.extract(identifiers, tmp_path)

    # Assert
    assert result.provenance.pipeline_version == "0.1.0"
