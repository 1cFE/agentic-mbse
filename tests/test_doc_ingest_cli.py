"""Tests for document ingestion CLI."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from doc_ingest.cli import (
    EXIT_FATAL,
    EXIT_SUCCESS,
    cmd_extract,
    create_document_identifiers,
    parse_identifier,
    validate_arxiv_id,
    validate_doi,
    validate_pmc_id,
)
from doc_ingest.types import DocumentIdentifiers, ExtractionResult, ProvenanceRecord


# -------------------------------------------------------------------------
# Test Helpers
# -------------------------------------------------------------------------


def create_mock_provenance(
    identifiers: DocumentIdentifiers,
    outcome: str = "success",
    failure_category: str | None = None,
) -> ProvenanceRecord:
    """Create a mock ProvenanceRecord for testing.

    Args:
        identifiers: Document identifiers
        outcome: Extraction outcome ("success", "partial", "failed")
        failure_category: Optional failure category

    Returns:
        ProvenanceRecord with minimal fields populated
    """
    return ProvenanceRecord(
        document_id=identifiers,
        discovered_sources=[],
        discovery_errors=[],
        discovery_cached=False,
        attempts=[],
        outcome=outcome,  # type: ignore[arg-type]
        final_converter="test_converter" if outcome == "success" else None,
        failure_category=failure_category,  # type: ignore[arg-type]
        created_at="2024-01-01T00:00:00Z",
        pipeline_version="0.1.0",
        total_elapsed_seconds=60.0,
    )


# -------------------------------------------------------------------------
# Identifier Validation Tests
# -------------------------------------------------------------------------


class TestIdentifierValidation:
    """Test identifier validation functions."""

    def test_validate_doi_valid(self):
        """Valid DOI formats should pass validation."""
        assert validate_doi("10.1234/example")
        assert validate_doi("10.1000/xyz123")
        assert validate_doi("10.12345/foo.bar.baz")

    def test_validate_doi_invalid(self):
        """Invalid DOI formats should fail validation."""
        assert not validate_doi("10.1234")  # Missing suffix
        assert not validate_doi("not-a-doi")
        assert not validate_doi("11.1234/example")  # Wrong prefix
        assert not validate_doi("")

    def test_validate_arxiv_id_valid(self):
        """Valid arXiv ID formats should pass validation."""
        assert validate_arxiv_id("2301.12345")
        assert validate_arxiv_id("2301.12345v2")
        assert validate_arxiv_id("1234.5678")

    def test_validate_arxiv_id_invalid(self):
        """Invalid arXiv ID formats should fail validation."""
        assert not validate_arxiv_id("2301.123")  # Too few digits
        assert not validate_arxiv_id("2301.123456")  # Too many digits
        assert not validate_arxiv_id("not-arxiv")
        assert not validate_arxiv_id("")

    def test_validate_pmc_id_valid(self):
        """Valid PMC ID formats should pass validation."""
        assert validate_pmc_id("PMC1234567")
        assert validate_pmc_id("pmc1234567")  # Case-insensitive
        assert validate_pmc_id("PMC123")

    def test_validate_pmc_id_invalid(self):
        """Invalid PMC ID formats should fail validation."""
        assert not validate_pmc_id("1234567")  # Missing PMC prefix
        assert not validate_pmc_id("PMCABC")  # Non-numeric suffix
        assert not validate_pmc_id("not-pmc")
        assert not validate_pmc_id("")

    def test_parse_identifier_doi(self):
        """DOI identifiers should be parsed correctly."""
        result = parse_identifier("10.1234/example")
        assert result == ("doi", "10.1234/example")

    def test_parse_identifier_arxiv(self):
        """arXiv identifiers should be parsed correctly."""
        result = parse_identifier("2301.12345")
        assert result == ("arxiv", "2301.12345")

    def test_parse_identifier_pmc(self):
        """PMC identifiers should be parsed correctly."""
        result = parse_identifier("PMC1234567")
        assert result == ("pmc", "PMC1234567")

        # Case normalization
        result = parse_identifier("pmc1234567")
        assert result == ("pmc", "PMC1234567")

    def test_parse_identifier_local(self, tmp_path: Path):
        """Local file paths should be parsed correctly."""
        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        result = parse_identifier(str(test_file))
        assert result is not None
        assert result[0] == "local"
        assert Path(result[1]) == test_file.absolute()

    def test_parse_identifier_invalid(self):
        """Invalid identifiers should return None."""
        result = parse_identifier("invalid-identifier")
        assert result is None

        result = parse_identifier("")
        assert result is None

    def test_create_document_identifiers_doi(self):
        """DOI should create DocumentIdentifiers with doi field."""
        ids = create_document_identifiers("10.1234/example")
        assert ids is not None
        assert ids.doi == "10.1234/example"
        assert ids.arxiv_id is None
        assert ids.pmc_id is None
        assert ids.local_path is None

    def test_create_document_identifiers_arxiv(self):
        """arXiv ID should create DocumentIdentifiers with arxiv_id field."""
        ids = create_document_identifiers("2301.12345")
        assert ids is not None
        assert ids.doi is None
        assert ids.arxiv_id == "2301.12345"
        assert ids.pmc_id is None
        assert ids.local_path is None

    def test_create_document_identifiers_pmc(self):
        """PMC ID should create DocumentIdentifiers with pmc_id field."""
        ids = create_document_identifiers("PMC1234567")
        assert ids is not None
        assert ids.doi is None
        assert ids.arxiv_id is None
        assert ids.pmc_id == "PMC1234567"
        assert ids.local_path is None

    def test_create_document_identifiers_local(self, tmp_path: Path):
        """Local file path should create DocumentIdentifiers with local_path field."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        ids = create_document_identifiers(str(test_file))
        assert ids is not None
        assert ids.doi is None
        assert ids.arxiv_id is None
        assert ids.pmc_id is None
        assert Path(ids.local_path) == test_file.absolute()

    def test_create_document_identifiers_invalid(self):
        """Invalid identifier should return None."""
        ids = create_document_identifiers("invalid")
        assert ids is None


# -------------------------------------------------------------------------
# CLI Command Tests
# -------------------------------------------------------------------------


class TestCmdExtract:
    """Test cmd_extract command handler."""

    def test_extract_success(self, tmp_path: Path, capsys):
        """Successful extraction should return EXIT_SUCCESS and write output."""
        output_dir = tmp_path / "output"

        # Create mock extraction result
        identifiers = DocumentIdentifiers(doi="10.1234/example")
        mock_provenance = create_mock_provenance(identifiers, outcome="success")
        mock_result = ExtractionResult(
            markdown="# Test Document\n\nContent here.",
            provenance=mock_provenance,
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_result

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify success
            assert exit_code == EXIT_SUCCESS

            # Verify router was called
            mock_router.extract.assert_called_once()
            call_args = mock_router.extract.call_args
            assert call_args.kwargs["identifiers"].doi == "10.1234/example"
            assert call_args.kwargs["output_dir"] == output_dir.absolute()

            # Verify writer was called
            mock_writer.write.assert_called_once()
            write_args = mock_writer.write.call_args
            assert write_args.kwargs["result"] == mock_result

            # Verify output messages
            captured = capsys.readouterr()
            assert "Extracting: 10.1234/example" in captured.out
            assert "Success:" in captured.out

    def test_extract_invalid_identifier(self, tmp_path: Path, capsys):
        """Invalid identifier should return EXIT_FATAL with error message."""
        output_dir = tmp_path / "output"

        exit_code = cmd_extract(
            identifier="invalid-identifier",
            output_dir=output_dir,
        )

        # Verify failure
        assert exit_code == EXIT_FATAL

        # Verify error message
        captured = capsys.readouterr()
        assert "Invalid identifier format: invalid-identifier" in captured.err
        assert "Expected DOI" in captured.err

    def test_extract_failed_outcome(self, tmp_path: Path, capsys):
        """Failed extraction should return EXIT_FATAL and report failure."""
        output_dir = tmp_path / "output"

        # Create mock failed extraction result
        identifiers = DocumentIdentifiers(doi="10.1234/example")
        mock_provenance = create_mock_provenance(
            identifiers, outcome="failed", failure_category="network_error"
        )
        mock_result = ExtractionResult(
            markdown=None,
            provenance=mock_provenance,
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_result

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify failure
            assert exit_code == EXIT_FATAL

            # Verify error message
            captured = capsys.readouterr()
            assert "Failed: failed" in captured.err
            assert "network_error" in captured.err

    def test_extract_with_format_override(self, tmp_path: Path, capsys):
        """Format override should be passed to router."""
        output_dir = tmp_path / "output"

        # Create mock extraction result
        identifiers = DocumentIdentifiers(doi="10.1234/example")
        mock_provenance = create_mock_provenance(identifiers, outcome="success")
        mock_result = ExtractionResult(
            markdown="# Test",
            provenance=mock_provenance,
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_result

            # Run command with format override
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
                format_override="pdf",
            )

            # Verify success
            assert exit_code == EXIT_SUCCESS

            # Verify format override was passed
            call_args = mock_router.extract.call_args
            assert call_args.kwargs["format_override"] == "pdf"

            # Verify output message
            captured = capsys.readouterr()
            assert "Format override: pdf" in captured.out

    def test_extract_creates_output_directory(self, tmp_path: Path):
        """Output directory should be created if it doesn't exist."""
        output_dir = tmp_path / "nonexistent" / "output"
        assert not output_dir.exists()

        # Create mock extraction result
        identifiers = DocumentIdentifiers(doi="10.1234/example")
        mock_provenance = create_mock_provenance(identifiers, outcome="success")
        mock_result = ExtractionResult(
            markdown="# Test",
            provenance=mock_provenance,
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_result

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify success
            assert exit_code == EXIT_SUCCESS

            # Verify directory was created
            assert output_dir.exists()

    def test_extract_pipeline_initialization_error(self, tmp_path: Path, capsys):
        """Pipeline initialization failure should return EXIT_FATAL."""
        output_dir = tmp_path / "output"

        # Mock pipeline creation to raise exception
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_create_pipeline.side_effect = Exception("Initialization failed")

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify failure
            assert exit_code == EXIT_FATAL

            # Verify error message
            captured = capsys.readouterr()
            assert "Failed to initialize pipeline" in captured.err

    def test_extract_router_exception(self, tmp_path: Path, capsys):
        """Router exception should return EXIT_FATAL."""
        output_dir = tmp_path / "output"

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.side_effect = Exception("Extraction failed")

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify failure
            assert exit_code == EXIT_FATAL

            # Verify error message
            captured = capsys.readouterr()
            assert "Extraction failed" in captured.err

    def test_extract_writer_exception(self, tmp_path: Path, capsys):
        """Writer exception should return EXIT_FATAL."""
        output_dir = tmp_path / "output"

        # Create mock extraction result
        identifiers = DocumentIdentifiers(doi="10.1234/example")
        mock_provenance = create_mock_provenance(identifiers, outcome="success")
        mock_result = ExtractionResult(
            markdown="# Test",
            provenance=mock_provenance,
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_result
            mock_writer.write.side_effect = Exception("Write failed")

            # Run command
            exit_code = cmd_extract(
                identifier="10.1234/example",
                output_dir=output_dir,
            )

            # Verify failure
            assert exit_code == EXIT_FATAL

            # Verify error message
            captured = capsys.readouterr()
            assert "Failed to write results" in captured.err
