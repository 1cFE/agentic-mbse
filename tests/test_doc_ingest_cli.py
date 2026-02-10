"""Tests for document ingestion CLI."""

from pathlib import Path
from unittest.mock import Mock, patch

from doc_ingest.cli import (
    EXIT_FATAL,
    EXIT_PARTIAL,
    EXIT_SUCCESS,
    cmd_clear_cache,
    cmd_extract,
    cmd_extract_batch,
    cmd_retry_failed,
    cmd_triage_report,
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


# -------------------------------------------------------------------------
# Batch Commands Tests
# -------------------------------------------------------------------------


class TestExtractBatch:
    """Test cmd_extract_batch for batch document extraction."""

    def test_extract_batch_all_success(self, tmp_path: Path, capsys):
        """All successful extractions should return EXIT_SUCCESS."""
        # Create JSONL input file
        input_file = tmp_path / "input.jsonl"
        input_file.write_text(
            '{"doi": "10.1234/one"}\n{"arxiv_id": "2301.12345"}\n{"doi": "10.1234/two"}\n'
        )

        output_dir = tmp_path / "output"

        # Create mock extraction results
        identifiers_one = DocumentIdentifiers(doi="10.1234/one")
        identifiers_two = DocumentIdentifiers(arxiv_id="2301.12345")
        identifiers_three = DocumentIdentifiers(doi="10.1234/two")

        mock_result_one = ExtractionResult(
            markdown="# One",
            provenance=create_mock_provenance(identifiers_one, outcome="success"),
        )
        mock_result_two = ExtractionResult(
            markdown="# Two",
            provenance=create_mock_provenance(identifiers_two, outcome="success"),
        )
        mock_result_three = ExtractionResult(
            markdown="# Three",
            provenance=create_mock_provenance(identifiers_three, outcome="success"),
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.side_effect = [mock_result_one, mock_result_two, mock_result_three]

            # Run command
            exit_code = cmd_extract_batch(
                input_file=input_file,
                output_dir=output_dir,
            )

            # Verify success
            assert exit_code == EXIT_SUCCESS

            # Verify all extractions were attempted
            assert mock_router.extract.call_count == 3
            assert mock_writer.write.call_count == 3

            # Verify output
            captured = capsys.readouterr()
            assert "Total: 3" in captured.out
            assert "Success: 3" in captured.out
            assert "Failed: 0" in captured.out

    def test_extract_batch_partial_success(self, tmp_path: Path, capsys):
        """Partial successes should return EXIT_PARTIAL and generate triage report."""
        # Create JSONL input file
        input_file = tmp_path / "input.jsonl"
        input_file.write_text('{"doi": "10.1234/one"}\n{"arxiv_id": "2301.12345"}\n')

        output_dir = tmp_path / "output"

        # Create mock extraction results
        identifiers_one = DocumentIdentifiers(doi="10.1234/one")
        identifiers_two = DocumentIdentifiers(arxiv_id="2301.12345")

        mock_result_one = ExtractionResult(
            markdown="# One",
            provenance=create_mock_provenance(identifiers_one, outcome="success"),
        )
        mock_result_two = ExtractionResult(
            markdown=None,
            provenance=create_mock_provenance(
                identifiers_two,
                outcome="failed",
                failure_category="paywall",
            ),
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.side_effect = [mock_result_one, mock_result_two]

            # Run command
            exit_code = cmd_extract_batch(
                input_file=input_file,
                output_dir=output_dir,
            )

            # Verify partial success
            assert exit_code == EXIT_PARTIAL

            # Verify output
            captured = capsys.readouterr()
            assert "Total: 2" in captured.out
            assert "Success: 1" in captured.out
            assert "Failed: 1" in captured.out
            assert "Triage report:" in captured.out

    def test_extract_batch_invalid_json(self, tmp_path: Path, capsys):
        """Invalid JSON lines should return EXIT_PARTIAL."""
        # Create JSONL input file with invalid JSON
        input_file = tmp_path / "input.jsonl"
        input_file.write_text('{"doi": "10.1234/one"}\ninvalid json line\n{"doi": "10.1234/two"}\n')

        output_dir = tmp_path / "output"

        # Create mock extraction results
        identifiers_one = DocumentIdentifiers(doi="10.1234/one")
        identifiers_two = DocumentIdentifiers(doi="10.1234/two")

        mock_result_one = ExtractionResult(
            markdown="# One",
            provenance=create_mock_provenance(identifiers_one, outcome="success"),
        )
        mock_result_two = ExtractionResult(
            markdown="# Two",
            provenance=create_mock_provenance(identifiers_two, outcome="success"),
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.side_effect = [mock_result_one, mock_result_two]

            # Run command
            exit_code = cmd_extract_batch(
                input_file=input_file,
                output_dir=output_dir,
            )

            # Verify partial success
            assert exit_code == EXIT_PARTIAL

            # Verify error message
            captured = capsys.readouterr()
            assert "Invalid JSON on line 2" in captured.err

    def test_extract_batch_missing_input_file(self, tmp_path: Path, capsys):
        """Missing input file should return EXIT_FATAL."""
        input_file = tmp_path / "nonexistent.jsonl"
        output_dir = tmp_path / "output"

        # Run command
        exit_code = cmd_extract_batch(
            input_file=input_file,
            output_dir=output_dir,
        )

        # Verify failure
        assert exit_code == EXIT_FATAL

        # Verify error message
        captured = capsys.readouterr()
        assert "Input file not found" in captured.err

    def test_extract_batch_empty_lines_skipped(self, tmp_path: Path):
        """Empty lines in JSONL should be skipped."""
        # Create JSONL input file with empty lines
        input_file = tmp_path / "input.jsonl"
        input_file.write_text('{"doi": "10.1234/one"}\n\n{"doi": "10.1234/two"}\n   \n')

        output_dir = tmp_path / "output"

        # Create mock extraction results
        identifiers_one = DocumentIdentifiers(doi="10.1234/one")
        identifiers_two = DocumentIdentifiers(doi="10.1234/two")

        mock_result_one = ExtractionResult(
            markdown="# One",
            provenance=create_mock_provenance(identifiers_one, outcome="success"),
        )
        mock_result_two = ExtractionResult(
            markdown="# Two",
            provenance=create_mock_provenance(identifiers_two, outcome="success"),
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.side_effect = [mock_result_one, mock_result_two]

            # Run command
            exit_code = cmd_extract_batch(
                input_file=input_file,
                output_dir=output_dir,
            )

            # Verify only 2 documents were processed
            assert exit_code == EXIT_SUCCESS
            assert mock_router.extract.call_count == 2


class TestTriageReport:
    """Test cmd_triage_report for analyzing provenance records."""

    def test_triage_report_generates_report(self, tmp_path: Path, capsys):
        """Triage report should be generated from provenance records."""
        import json
        from dataclasses import asdict

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create mock provenance files
        doc_dir1 = output_dir / "abc123"
        doc_dir1.mkdir()
        provenance1 = create_mock_provenance(
            DocumentIdentifiers(doi="10.1234/one"),
            outcome="success",
        )
        (doc_dir1 / "provenance.json").write_text(json.dumps(asdict(provenance1)))

        doc_dir2 = output_dir / "def456"
        doc_dir2.mkdir()
        provenance2 = create_mock_provenance(
            DocumentIdentifiers(arxiv_id="2301.12345"),
            outcome="failed",
            failure_category="paywall",
        )
        (doc_dir2 / "provenance.json").write_text(json.dumps(asdict(provenance2)))

        # Run command
        exit_code = cmd_triage_report(
            output_dir=output_dir,
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS

        # Verify report was created
        report_path = output_dir / "triage_report.md"
        assert report_path.exists()

        # Verify report content
        report_content = report_path.read_text()
        assert "Document Extraction Triage Report" in report_content
        assert "**Total documents**: 2" in report_content
        assert "**Successful**: 1" in report_content
        assert "**Failed**: 1" in report_content
        assert "paywall" in report_content

    def test_triage_report_missing_output_dir(self, tmp_path: Path, capsys):
        """Missing output directory should return EXIT_FATAL."""
        output_dir = tmp_path / "nonexistent"

        # Run command
        exit_code = cmd_triage_report(
            output_dir=output_dir,
        )

        # Verify failure
        assert exit_code == EXIT_FATAL

        # Verify error message
        captured = capsys.readouterr()
        assert "Output directory not found" in captured.err

    def test_triage_report_custom_path(self, tmp_path: Path):
        """Custom report path should be used."""
        import json
        from dataclasses import asdict

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        report_path = tmp_path / "custom_report.md"

        # Create mock provenance file
        doc_dir = output_dir / "abc123"
        doc_dir.mkdir()
        provenance = create_mock_provenance(
            DocumentIdentifiers(doi="10.1234/one"),
            outcome="success",
        )
        (doc_dir / "provenance.json").write_text(json.dumps(asdict(provenance)))

        # Run command
        exit_code = cmd_triage_report(
            output_dir=output_dir,
            report_path=report_path,
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS
        assert report_path.exists()


class TestRetryFailed:
    """Test cmd_retry_failed for retrying failed documents."""

    def test_retry_failed_retries_only_failures(self, tmp_path: Path, capsys):
        """Only failed/partial documents should be retried."""
        import json
        from dataclasses import asdict

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create mock provenance files
        doc_dir_success = output_dir / "abc123"
        doc_dir_success.mkdir()
        provenance_success = create_mock_provenance(
            DocumentIdentifiers(doi="10.1234/success"),
            outcome="success",
        )
        (doc_dir_success / "provenance.json").write_text(json.dumps(asdict(provenance_success)))

        doc_dir_failed = output_dir / "def456"
        doc_dir_failed.mkdir()
        identifiers_failed = DocumentIdentifiers(doi="10.1234/failed")
        provenance_failed = create_mock_provenance(
            identifiers_failed,
            outcome="failed",
            failure_category="paywall",
        )
        (doc_dir_failed / "provenance.json").write_text(json.dumps(asdict(provenance_failed)))

        # Create mock retry result
        mock_retry_result = ExtractionResult(
            markdown="# Retry Success",
            provenance=create_mock_provenance(identifiers_failed, outcome="success"),
        )

        # Mock pipeline components
        with patch("doc_ingest.cli.create_pipeline") as mock_create_pipeline:
            mock_router = Mock()
            mock_writer = Mock()
            mock_create_pipeline.return_value = (mock_router, mock_writer)
            mock_router.extract.return_value = mock_retry_result

            # Run command
            exit_code = cmd_retry_failed(
                output_dir=output_dir,
            )

            # Verify success
            assert exit_code == EXIT_SUCCESS

            # Verify only failed document was retried
            assert mock_router.extract.call_count == 1
            assert mock_writer.write.call_count == 1

            # Verify output
            captured = capsys.readouterr()
            assert "Retried: 1" in captured.out
            assert "Success: 1" in captured.out

    def test_retry_failed_no_failures_found(self, tmp_path: Path, capsys):
        """No failures should return EXIT_SUCCESS with message."""
        import json
        from dataclasses import asdict

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create only successful provenance
        doc_dir = output_dir / "abc123"
        doc_dir.mkdir()
        provenance = create_mock_provenance(
            DocumentIdentifiers(doi="10.1234/success"),
            outcome="success",
        )
        (doc_dir / "provenance.json").write_text(json.dumps(asdict(provenance)))

        # Run command (no mock needed, should not retry anything)
        exit_code = cmd_retry_failed(
            output_dir=output_dir,
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS

        # Verify message
        captured = capsys.readouterr()
        assert "No failed documents found" in captured.out

    def test_retry_failed_missing_output_dir(self, tmp_path: Path, capsys):
        """Missing output directory should return EXIT_FATAL."""
        output_dir = tmp_path / "nonexistent"

        # Run command
        exit_code = cmd_retry_failed(
            output_dir=output_dir,
        )

        # Verify failure
        assert exit_code == EXIT_FATAL

        # Verify error message
        captured = capsys.readouterr()
        assert "Output directory not found" in captured.err


class TestClearCache:
    """Test cmd_clear_cache for cache invalidation."""

    def test_clear_cache_specific_identifier(self, tmp_path: Path, capsys):
        """Specific identifier should be cleared."""
        cache_dir = tmp_path / ".cache"
        cache_dir.mkdir()

        # Create mock cache files
        from doc_ingest.discovery_cache import DiscoveryCache

        cache = DiscoveryCache(cache_dir=cache_dir, ttl_days=30)
        cache.put("doi:10.1234/one", [])
        cache.put("doi:10.1234/two", [])

        # Run command
        exit_code = cmd_clear_cache(
            cache_dir=cache_dir,
            identifier="doi:10.1234/one",
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS

        # Verify only one identifier was cleared
        assert cache.get("doi:10.1234/one") is None
        assert cache.get("doi:10.1234/two") is not None

        # Verify output
        captured = capsys.readouterr()
        assert "Cleared cache entry: doi:10.1234/one" in captured.out

    def test_clear_cache_all(self, tmp_path: Path, capsys):
        """All cache entries should be cleared."""
        cache_dir = tmp_path / ".cache"
        cache_dir.mkdir()

        # Create mock cache files
        from doc_ingest.discovery_cache import DiscoveryCache

        cache = DiscoveryCache(cache_dir=cache_dir, ttl_days=30)
        cache.put("doi:10.1234/one", [])
        cache.put("doi:10.1234/two", [])

        # Run command
        exit_code = cmd_clear_cache(
            cache_dir=cache_dir,
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS

        # Verify all entries were cleared
        assert cache.get("doi:10.1234/one") is None
        assert cache.get("doi:10.1234/two") is None

        # Verify output
        captured = capsys.readouterr()
        assert "Cleared all 2 cache entries" in captured.out

    def test_clear_cache_expired_only(self, tmp_path: Path, capsys):
        """Only expired cache entries should be cleared."""
        cache_dir = tmp_path / ".cache"
        cache_dir.mkdir()

        # Create mock cache files with different ages
        import json
        import time

        # Recent entry (not expired)
        recent_file = cache_dir / "recent.json"
        recent_data = {
            "timestamp": time.time() - (10 * 24 * 3600),  # 10 days old
            "identifier_key": "doi:10.1234/recent",
            "sources": [],
        }
        recent_file.write_text(json.dumps(recent_data))

        # Old entry (expired)
        old_file = cache_dir / "old.json"
        old_data = {
            "timestamp": time.time() - (40 * 24 * 3600),  # 40 days old
            "identifier_key": "doi:10.1234/old",
            "sources": [],
        }
        old_file.write_text(json.dumps(old_data))

        # Run command
        exit_code = cmd_clear_cache(
            cache_dir=cache_dir,
            max_age_days=30,
        )

        # Verify success
        assert exit_code == EXIT_SUCCESS

        # Verify only old entry was cleared
        assert recent_file.exists()
        assert not old_file.exists()

        # Verify output
        captured = capsys.readouterr()
        assert "Cleared 1 expired cache entries" in captured.out

    def test_clear_cache_missing_cache_dir(self, tmp_path: Path, capsys):
        """Missing cache directory should return EXIT_FATAL."""
        cache_dir = tmp_path / "nonexistent"

        # Run command
        exit_code = cmd_clear_cache(
            cache_dir=cache_dir,
        )

        # Verify failure
        assert exit_code == EXIT_FATAL

        # Verify error message
        captured = capsys.readouterr()
        assert "Cache directory not found" in captured.err
