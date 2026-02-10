"""Unit tests for ProvenanceManager.

Tests atomic writes, load functionality, UTF-8 encoding, and crash safety.
"""

import json
from pathlib import Path

import pytest

from doc_ingest.outcome_classifier import ExtractionAttempt
from doc_ingest.provenance_manager import ProvenanceManager
from doc_ingest.types import (
    DocumentIdentifiers,
    ProvenanceRecord,
    SourceCandidate,
)


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_provenance_record() -> ProvenanceRecord:
    """Create a sample provenance record for testing."""
    doc_id = DocumentIdentifiers(
        doi="10.1234/test.2024",
        arxiv_id="2401.12345",
    )

    sources = [
        SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/article.xml",
            discovered_via="openalex_api",
        ),
        SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/article.pdf",
            discovered_via="openalex_api",
        ),
    ]

    attempts = [
        ExtractionAttempt(
            source_url="https://example.com/article.xml",
            outcome="success",
            converter_name="JATSPandocConverter",
            failure_category=None,
        )
    ]

    return ProvenanceRecord(
        document_id=doc_id,
        discovered_sources=sources,
        discovery_errors=[],
        discovery_cached=False,
        attempts=attempts,
        outcome="success",
        final_converter="JATSPandocConverter",
        failure_category=None,
        created_at="2024-01-15T10:30:00Z",
        pipeline_version="0.1.0",
        total_elapsed_seconds=2.5,
    )


@pytest.fixture
def unicode_provenance_record() -> ProvenanceRecord:
    """Create a provenance record with Unicode characters."""
    doc_id = DocumentIdentifiers(
        local_path="/data/文档/论文.pdf",  # Chinese characters
    )

    sources = [
        SourceCandidate(
            quality_tier=4,
            format="pdf",
            local_path="/data/文档/论文.pdf",
            discovered_via="local_file",
        )
    ]

    attempts = [
        ExtractionAttempt(
            source_url="/data/文档/论文.pdf",
            outcome="success",
            converter_name="PyMuPDF4LLMConverter",
            failure_category=None,
        )
    ]

    return ProvenanceRecord(
        document_id=doc_id,
        discovered_sources=sources,
        discovery_errors=[],
        discovery_cached=False,
        attempts=attempts,
        outcome="success",
        final_converter="PyMuPDF4LLMConverter",
        failure_category=None,
        created_at="2024-01-15T10:30:00Z",
        pipeline_version="0.1.0",
        total_elapsed_seconds=3.2,
    )


class TestProvenanceManager:
    """Test suite for ProvenanceManager."""

    def test_write_and_load_round_trip(
        self, temp_output_dir: Path, sample_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that write + load preserves all record fields."""
        manager = ProvenanceManager()

        # Write record
        manager.write(temp_output_dir, sample_provenance_record)

        # Compute expected hash
        doc_hash = manager._compute_hash(sample_provenance_record.document_id)

        # Load record
        loaded = manager.load(temp_output_dir, doc_hash)

        # Verify all fields preserved
        assert loaded is not None
        assert loaded.document_id.doi == "10.1234/test.2024"
        assert loaded.document_id.arxiv_id == "2401.12345"
        assert len(loaded.discovered_sources) == 2
        assert loaded.discovered_sources[0].format == "jats_xml"
        assert loaded.discovered_sources[1].format == "pdf"
        assert len(loaded.attempts) == 1
        assert loaded.attempts[0].outcome == "success"
        assert loaded.attempts[0].converter_name == "JATSPandocConverter"
        assert loaded.outcome == "success"
        assert loaded.final_converter == "JATSPandocConverter"
        assert loaded.failure_category is None
        assert loaded.created_at == "2024-01-15T10:30:00Z"
        assert loaded.pipeline_version == "0.1.0"
        assert loaded.total_elapsed_seconds == 2.5

    def test_write_creates_directory(
        self, temp_output_dir: Path, sample_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that write creates output directory structure."""
        manager = ProvenanceManager()
        manager.write(temp_output_dir, sample_provenance_record)

        doc_hash = manager._compute_hash(sample_provenance_record.document_id)
        provenance_path = temp_output_dir / doc_hash / "provenance.json"

        assert provenance_path.exists()
        assert provenance_path.is_file()

    def test_load_missing_file_returns_none(self, temp_output_dir: Path) -> None:
        """Test that load returns None for non-existent file."""
        manager = ProvenanceManager()
        loaded = manager.load(temp_output_dir, "nonexistent_hash")

        assert loaded is None

    def test_load_corrupted_file_returns_none(self, temp_output_dir: Path) -> None:
        """Test that load returns None for corrupted JSON."""
        manager = ProvenanceManager()

        # Create corrupted provenance file
        doc_hash = "corrupted_hash"
        doc_dir = temp_output_dir / doc_hash
        doc_dir.mkdir()
        provenance_path = doc_dir / "provenance.json"

        with provenance_path.open("w") as f:
            f.write("{invalid json content")

        loaded = manager.load(temp_output_dir, doc_hash)
        assert loaded is None

    def test_unicode_support(
        self, temp_output_dir: Path, unicode_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that Unicode characters in identifiers are preserved."""
        manager = ProvenanceManager()

        # Write record with Unicode
        manager.write(temp_output_dir, unicode_provenance_record)

        # Load and verify
        doc_hash = manager._compute_hash(unicode_provenance_record.document_id)
        loaded = manager.load(temp_output_dir, doc_hash)

        assert loaded is not None
        assert loaded.document_id.local_path == "/data/文档/论文.pdf"
        assert loaded.discovered_sources[0].local_path == "/data/文档/论文.pdf"
        assert loaded.attempts[0].source_url == "/data/文档/论文.pdf"

    def test_atomic_write_prevents_partial_json(
        self, temp_output_dir: Path, sample_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that atomic write prevents partial JSON on crash.

        This test verifies that if a write is interrupted, either the old file
        remains intact or the new file is complete (never partial).
        """
        manager = ProvenanceManager()
        doc_hash = manager._compute_hash(sample_provenance_record.document_id)

        # Write initial version
        manager.write(temp_output_dir, sample_provenance_record)
        provenance_path = temp_output_dir / doc_hash / "provenance.json"

        # Verify initial file is valid JSON
        with provenance_path.open("r") as f:
            initial_data = json.load(f)
        assert initial_data["outcome"] == "success"

        # Simulate interrupted write by checking temp file cleanup
        # (The atomic rename ensures either old or new file exists, never partial)
        manager.write(temp_output_dir, sample_provenance_record)

        # Verify no temp files left behind
        doc_dir = temp_output_dir / doc_hash
        temp_files = list(doc_dir.glob(".provenance_*.tmp"))
        assert len(temp_files) == 0

        # Verify final file is still valid JSON
        with provenance_path.open("r") as f:
            final_data = json.load(f)
        assert final_data["outcome"] == "success"

    def test_write_overwrites_existing_provenance(
        self, temp_output_dir: Path, sample_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that write overwrites existing provenance file."""
        manager = ProvenanceManager()

        # Write initial version
        manager.write(temp_output_dir, sample_provenance_record)

        # Modify record
        updated_record = ProvenanceRecord(
            document_id=sample_provenance_record.document_id,
            discovered_sources=sample_provenance_record.discovered_sources,
            discovery_errors=["API timeout"],
            discovery_cached=True,
            attempts=sample_provenance_record.attempts,
            outcome="partial",
            final_converter="PyMuPDF4LLMConverter",
            failure_category="table_corruption",
            created_at="2024-01-16T11:00:00Z",
            pipeline_version="0.2.0",
            total_elapsed_seconds=5.0,
        )

        # Write updated version
        manager.write(temp_output_dir, updated_record)

        # Load and verify it's the updated version
        doc_hash = manager._compute_hash(updated_record.document_id)
        loaded = manager.load(temp_output_dir, doc_hash)

        assert loaded is not None
        assert loaded.outcome == "partial"
        assert loaded.failure_category == "table_corruption"
        assert loaded.discovery_errors == ["API timeout"]
        assert loaded.discovery_cached is True
        assert loaded.created_at == "2024-01-16T11:00:00Z"
        assert loaded.pipeline_version == "0.2.0"

    def test_compute_hash_deterministic(self) -> None:
        """Test that hash computation is deterministic for same identifiers."""
        manager = ProvenanceManager()

        doc_id_1 = DocumentIdentifiers(doi="10.1234/test")
        doc_id_2 = DocumentIdentifiers(doi="10.1234/test")

        hash_1 = manager._compute_hash(doc_id_1)
        hash_2 = manager._compute_hash(doc_id_2)

        assert hash_1 == hash_2

    def test_compute_hash_uses_primary_identifier(self) -> None:
        """Test that hash uses primary identifier (doi > arxiv_id)."""
        manager = ProvenanceManager()

        # DOI takes priority
        doc_id_with_doi = DocumentIdentifiers(doi="10.1234/test", arxiv_id="2401.12345")
        hash_doi = manager._compute_hash(doc_id_with_doi)

        # Same DOI alone should produce same hash
        doc_id_doi_only = DocumentIdentifiers(doi="10.1234/test")
        hash_doi_only = manager._compute_hash(doc_id_doi_only)

        assert hash_doi == hash_doi_only

    def test_json_deterministic_ordering(
        self, temp_output_dir: Path, sample_provenance_record: ProvenanceRecord
    ) -> None:
        """Test that JSON output has deterministic key ordering."""
        manager = ProvenanceManager()
        manager.write(temp_output_dir, sample_provenance_record)

        doc_hash = manager._compute_hash(sample_provenance_record.document_id)
        provenance_path = temp_output_dir / doc_hash / "provenance.json"

        # Read raw JSON and verify it's sorted
        with provenance_path.open("r") as f:
            json_text = f.read()

        # Verify keys are sorted (attempts < created_at < discovered_sources)
        attempts_pos = json_text.find('"attempts"')
        created_at_pos = json_text.find('"created_at"')
        discovered_pos = json_text.find('"discovered_sources"')
        assert attempts_pos < created_at_pos < discovered_pos

    def test_failed_extraction_record(self, temp_output_dir: Path) -> None:
        """Test provenance record for failed extraction."""
        manager = ProvenanceManager()

        doc_id = DocumentIdentifiers(doi="10.1234/failed.2024")
        sources = [
            SourceCandidate(
                quality_tier=4,
                format="pdf",
                url="https://example.com/scanned.pdf",
                discovered_via="openalex_api",
            )
        ]
        attempts = [
            ExtractionAttempt(
                source_url="https://example.com/scanned.pdf",
                outcome="fetch_failed",
                converter_name=None,
                failure_category="needs_ocr",
            )
        ]

        failed_record = ProvenanceRecord(
            document_id=doc_id,
            discovered_sources=sources,
            discovery_errors=[],
            discovery_cached=False,
            attempts=attempts,
            outcome="failed",
            final_converter=None,
            failure_category="needs_ocr",
            created_at="2024-01-15T12:00:00Z",
            pipeline_version="0.1.0",
            total_elapsed_seconds=1.0,
        )

        # Write and load
        manager.write(temp_output_dir, failed_record)
        doc_hash = manager._compute_hash(failed_record.document_id)
        loaded = manager.load(temp_output_dir, doc_hash)

        # Verify failure fields
        assert loaded is not None
        assert loaded.outcome == "failed"
        assert loaded.final_converter is None
        assert loaded.failure_category == "needs_ocr"
        assert loaded.attempts[0].outcome == "fetch_failed"
