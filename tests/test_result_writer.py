"""Tests for ResultWriter.

Verifies that ResultWriter correctly writes markdown outputs, summary.json, and
delegates provenance writing to ProvenanceManager. Tests both success and failure paths.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from doc_ingest.outcome_classifier import ExtractionAttempt
from doc_ingest.provenance_manager import ProvenanceManager
from doc_ingest.result_writer import ResultWriter
from doc_ingest.types import (
    ConversionResult,
    DocumentIdentifiers,
    ExtractionResult,
    ProvenanceRecord,
    QualityFlags,
    SourceCandidate,
)


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory for tests."""
    return tmp_path / "output"


@pytest.fixture
def provenance_manager() -> ProvenanceManager:
    """Create ProvenanceManager instance for tests."""
    return ProvenanceManager()


@pytest.fixture
def result_writer(provenance_manager: ProvenanceManager) -> ResultWriter:
    """Create ResultWriter with provenance manager dependency."""
    return ResultWriter(provenance_manager)


@pytest.fixture
def sample_identifiers() -> DocumentIdentifiers:
    """Create sample document identifiers for testing."""
    return DocumentIdentifiers(
        doi="10.1234/test.doc",
        arxiv_id="2301.12345",
        zotero_key="TEST123",
    )


@pytest.fixture
def sample_source_candidate() -> SourceCandidate:
    """Create sample source candidate for testing."""
    return SourceCandidate(
        quality_tier=1,
        format="jats_xml",
        url="https://example.com/article.xml",
        discovered_via="openalex",
    )


@pytest.fixture
def sample_conversion_result() -> ConversionResult:
    """Create sample conversion result for testing."""
    return ConversionResult(
        markdown="# Test Document\n\nThis is extracted content.",
        warnings=["Table possibly corrupted"],
        quality_flags=QualityFlags(has_tables=True, tables_likely_corrupted=True),
        converter_name="JAXPandocConverter",
    )


@pytest.fixture
def successful_provenance(
    sample_identifiers: DocumentIdentifiers,
    sample_source_candidate: SourceCandidate,
    sample_conversion_result: ConversionResult,
) -> ProvenanceRecord:
    """Create provenance record for successful extraction."""
    attempt = ExtractionAttempt(
        source_url=sample_source_candidate.url or "",
        outcome="success",
        failure_category=None,
        converter_name="JAXPandocConverter",
        is_paywall=False,
    )

    return ProvenanceRecord(
        document_id=sample_identifiers,
        discovered_sources=[sample_source_candidate],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[attempt],
        outcome="success",
        final_converter="JAXPandocConverter",
        failure_category=None,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=2.0,
    )


@pytest.fixture
def failed_provenance(
    sample_identifiers: DocumentIdentifiers,
    sample_source_candidate: SourceCandidate,
) -> ProvenanceRecord:
    """Create provenance record for failed extraction."""
    attempt = ExtractionAttempt(
        source_url=sample_source_candidate.url or "",
        outcome="validation_failed",
        failure_category="source_validation_failed",
        converter_name=None,
        is_paywall=True,
    )

    return ProvenanceRecord(
        document_id=sample_identifiers,
        discovered_sources=[sample_source_candidate],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[attempt],
        outcome="failed",
        final_converter=None,
        failure_category="source_validation_failed",
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=1.0,
    )


def test_write_success_creates_all_files(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that successful extraction writes output.md, summary.json, and provenance.json."""
    result = ExtractionResult(
        markdown="# Test Document\n\nExtracted content here.",
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    # Compute expected document hash
    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    doc_dir = output_dir / document_hash

    # Verify all three files exist
    assert (doc_dir / "output.md").exists(), "output.md should be created for success"
    assert (doc_dir / "summary.json").exists(), "summary.json should be created for success"
    assert (doc_dir / "provenance.json").exists(), "provenance.json should be created via manager"


def test_write_success_markdown_content(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that output.md contains the correct markdown content."""
    markdown_content = "# Test Document\n\nThis is the extracted markdown."
    result = ExtractionResult(
        markdown=markdown_content,
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    output_md_path = output_dir / document_hash / "output.md"

    actual_content = output_md_path.read_text(encoding="utf-8")
    assert actual_content == markdown_content, "output.md should contain exact markdown content"


def test_write_success_summary_json_structure(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that summary.json has correct structure and required fields."""
    result = ExtractionResult(
        markdown="# Test",
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    summary_path = output_dir / document_hash / "summary.json"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Verify required fields
    assert summary["document_hash"] == document_hash
    assert summary["source_info"]["doi"] == "10.1234/test.doc"
    assert summary["source_info"]["arxiv_id"] == "2301.12345"
    assert summary["source_info"]["zotero_key"] == "TEST123"
    assert summary["backend_used"] == "JAXPandocConverter"
    assert summary["outcome"] == "success"
    assert summary["statistics"]["total_elapsed_seconds"] == 2.0
    assert summary["statistics"]["num_attempts"] == 1
    assert summary["statistics"]["num_sources_discovered"] == 1


def test_write_success_summary_no_warnings_field(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that summary.json does not include warnings field (not in data model)."""
    result = ExtractionResult(
        markdown="# Test",
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    summary_path = output_dir / document_hash / "summary.json"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Verify warnings field is NOT present (ExtractionAttempt doesn't have warnings)
    assert "warnings" not in summary


def test_write_failure_skips_markdown_and_summary(
    result_writer: ResultWriter,
    output_dir: Path,
    failed_provenance: ProvenanceRecord,
) -> None:
    """Test that failed extraction only writes provenance.json (no output.md or summary.json)."""
    result = ExtractionResult(
        markdown=None,  # Failed extraction has no markdown
        provenance=failed_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(failed_provenance.document_id)
    doc_dir = output_dir / document_hash

    # Verify only provenance.json exists
    assert (doc_dir / "provenance.json").exists(), "provenance.json should always be written"
    assert not (doc_dir / "output.md").exists(), "output.md should NOT be created for failure"
    assert not (doc_dir / "summary.json").exists(), "summary.json should NOT be created for failure"


def test_write_creates_output_directory(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that write creates output directory if it doesn't exist."""
    # Ensure output_dir doesn't exist initially
    assert not output_dir.exists()

    result = ExtractionResult(
        markdown="# Test",
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    # Verify directory was created
    assert output_dir.exists()
    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    assert (output_dir / document_hash).exists()


def test_write_is_idempotent(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that writing the same result twice is idempotent (no errors, same content)."""
    result = ExtractionResult(
        markdown="# Test Document",
        provenance=successful_provenance,
    )

    # Write once
    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    output_md_path = output_dir / document_hash / "output.md"
    first_content = output_md_path.read_text(encoding="utf-8")

    # Write again
    result_writer.write(output_dir, result)

    second_content = output_md_path.read_text(encoding="utf-8")

    # Content should be identical
    assert second_content == first_content, "Second write should produce identical content"


def test_write_handles_unicode_in_markdown(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that ResultWriter correctly handles Unicode characters in markdown."""
    unicode_markdown = "# Test Document\n\n这是中文内容。μ-calculus, λ-abstraction."
    result = ExtractionResult(
        markdown=unicode_markdown,
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    output_md_path = output_dir / document_hash / "output.md"

    actual_content = output_md_path.read_text(encoding="utf-8")
    assert actual_content == unicode_markdown, "Unicode characters should be preserved in output.md"


def test_summary_statistics_fields(
    result_writer: ResultWriter,
    output_dir: Path,
    sample_identifiers: DocumentIdentifiers,
    sample_source_candidate: SourceCandidate,
) -> None:
    """Test that summary.json includes correct statistics fields."""
    # Create provenance for testing
    attempt = ExtractionAttempt(
        source_url=sample_source_candidate.url or "",
        outcome="success",
        failure_category=None,
        converter_name="JAXPandocConverter",
        is_paywall=False,
    )

    provenance = ProvenanceRecord(
        document_id=sample_identifiers,
        discovered_sources=[sample_source_candidate],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[attempt],
        outcome="success",
        final_converter="JAXPandocConverter",
        failure_category=None,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=1.5,
    )

    result = ExtractionResult(
        markdown="# Test",
        provenance=provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(sample_identifiers)
    summary_path = output_dir / document_hash / "summary.json"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Verify statistics fields are present
    assert "statistics" in summary
    assert summary["statistics"]["total_elapsed_seconds"] == 1.5
    assert summary["statistics"]["num_attempts"] == 1
    assert summary["statistics"]["num_sources_discovered"] == 1


def test_summary_includes_all_identifier_types(
    result_writer: ResultWriter,
    output_dir: Path,
    successful_provenance: ProvenanceRecord,
) -> None:
    """Test that summary.json includes all present identifier types."""
    result = ExtractionResult(
        markdown="# Test",
        provenance=successful_provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(
        successful_provenance.document_id
    )
    summary_path = output_dir / document_hash / "summary.json"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Verify all identifier types from sample_identifiers are present
    assert "doi" in summary["source_info"]
    assert "arxiv_id" in summary["source_info"]
    assert "zotero_key" in summary["source_info"]


def test_summary_omits_missing_identifiers(
    result_writer: ResultWriter,
    output_dir: Path,
    sample_source_candidate: SourceCandidate,
) -> None:
    """Test that summary.json omits identifier fields that are None."""
    # Create identifiers with only DOI
    identifiers = DocumentIdentifiers(doi="10.1234/test")

    attempt = ExtractionAttempt(
        source_url=sample_source_candidate.url or "",
        outcome="success",
        failure_category=None,
        converter_name="Converter",
        is_paywall=False,
    )

    provenance = ProvenanceRecord(
        document_id=identifiers,
        discovered_sources=[sample_source_candidate],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[attempt],
        outcome="success",
        final_converter="Converter",
        failure_category=None,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version="0.1.0",
        total_elapsed_seconds=1.5,
    )

    result = ExtractionResult(
        markdown="# Test",
        provenance=provenance,
    )

    result_writer.write(output_dir, result)

    document_hash = result_writer.provenance_manager._compute_hash(identifiers)
    summary_path = output_dir / document_hash / "summary.json"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Verify only DOI is present in source_info
    assert "doi" in summary["source_info"]
    assert "arxiv_id" not in summary["source_info"]
    assert "pmc_id" not in summary["source_info"]
    assert "local_path" not in summary["source_info"]
    assert "zotero_key" not in summary["source_info"]
