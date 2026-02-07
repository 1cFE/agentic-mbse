"""Tests for agentic_mbse.cli.extract_cli — Phase 2."""

import hashlib
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from agentic_mbse.cli.extract_cli import (
    cmd_extract,
    discover_documents,
    select_backend,
)
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS


class MockArgs:
    """Mock argparse namespace."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ---------------------------------------------------------------------------
# discover_documents
# ---------------------------------------------------------------------------


class TestDiscoverDocuments:
    def test_single_pdf(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        assert discover_documents(pdf) == [pdf]

    def test_single_docx(self, tmp_path):
        docx = tmp_path / "report.docx"
        docx.touch()
        assert discover_documents(docx) == [docx]

    def test_directory_flat_listing(self, tmp_path):
        (tmp_path / "a.pdf").touch()
        (tmp_path / "b.docx").touch()
        (tmp_path / "c.txt").touch()  # ignored
        result = discover_documents(tmp_path)
        assert len(result) == 2
        # Should be sorted
        assert result[0].name == "a.pdf"
        assert result[1].name == "b.docx"

    def test_nonexistent_path(self):
        result = discover_documents(Path("/nonexistent/path"))
        assert result == []

    def test_unsupported_extension(self, tmp_path):
        txt = tmp_path / "report.txt"
        txt.touch()
        result = discover_documents(txt)
        assert result == []

    def test_directory_ignores_subdirectories(self, tmp_path):
        (tmp_path / "a.pdf").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "b.pdf").touch()  # should be ignored (flat listing)
        result = discover_documents(tmp_path)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# select_backend
# ---------------------------------------------------------------------------


class TestSelectBackend:
    def test_forced_backend(self):
        result = select_backend(Path("x.pdf"), requested="pymupdf")
        assert result == "pymupdf"

    def test_auto_selects_pymupdf_for_pdf_when_only_pymupdf(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: name == "pymupdf"
        )
        result = select_backend(Path("x.pdf"), requested=None)
        assert result == "pymupdf"

    def test_auto_prefers_docling_for_pdf(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: True
        )
        result = select_backend(Path("x.pdf"), requested=None)
        assert result == "docling"

    def test_auto_prefers_docling_for_docx(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: True
        )
        result = select_backend(Path("x.docx"), requested=None)
        assert result == "docling"

    def test_auto_fallback_pandoc_for_docx(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available",
            lambda name: name == "pandoc",
        )
        result = select_backend(Path("x.docx"), requested=None)
        assert result == "pandoc"

    def test_returns_none_when_nothing_available(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: False
        )
        result = select_backend(Path("x.pdf"), requested=None)
        assert result is None


# ---------------------------------------------------------------------------
# cmd_extract
# ---------------------------------------------------------------------------


class TestCmdExtract:
    def test_returns_failure_for_nonexistent_path(self):
        args = MockArgs(
            path="/nonexistent/does/not/exist",
            output=None,
            backend=None,
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )
        assert cmd_extract(args) == EXIT_FAILURE

    def test_returns_failure_when_no_documents_found(self, tmp_path):
        (tmp_path / "readme.txt").touch()
        args = MockArgs(
            path=str(tmp_path),
            output=None,
            backend=None,
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )
        assert cmd_extract(args) == EXIT_FAILURE

    def test_skips_already_processed(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        # Write summary.json with matching hash
        file_hash = "md5:" + hashlib.md5(b"fake pdf content").hexdigest()
        summary = {"file_hash": file_hash, "processing_completed": True}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        # Should succeed (skip is not a failure)
        with patch("agentic_mbse.cli.extract_cli._run_extraction") as mock_run:
            result = cmd_extract(args)
            mock_run.assert_not_called()
        assert result == EXIT_SUCCESS

    def test_extracts_when_forced(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        # Write summary.json with matching hash
        file_hash = "md5:" + hashlib.md5(b"fake pdf content").hexdigest()
        summary = {"file_hash": file_hash, "processing_completed": True}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        from agentic_mbse.extraction.base import ExtractionResult

        mock_result = ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=output_dir / "full_document.md",
            backend_used="pymupdf",
        )

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=True,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with patch(
            "agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result
        ) as mock_run:
            result = cmd_extract(args)
            mock_run.assert_called_once()
        assert result == EXIT_SUCCESS

    def test_returns_failure_when_no_backend_available(self, tmp_path, monkeypatch):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")

        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: False
        )

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend=None,
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )
        assert cmd_extract(args) == EXIT_FAILURE

    def test_partial_failure_returns_failure(self, tmp_path):
        """When some docs succeed and some fail, exit code is FAILURE."""
        from agentic_mbse.extraction.base import ExtractionResult

        pdf1 = tmp_path / "good.pdf"
        pdf1.write_bytes(b"fake pdf 1")
        pdf2 = tmp_path / "bad.pdf"
        pdf2.write_bytes(b"fake pdf 2")

        success_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "good",
            markdown_path=tmp_path / "good" / "full_document.md",
            backend_used="pymupdf",
        )
        fail_result = ExtractionResult(
            success=False,
            output_dir=tmp_path / "bad",
            error="extraction failed",
            backend_used="pymupdf",
        )

        call_count = 0

        def mock_run_extraction(file_path, output_dir, backend, timeout):
            nonlocal call_count
            call_count += 1
            if file_path.name == "good.pdf":
                return success_result
            return fail_result

        args = MockArgs(
            path=str(tmp_path),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with patch(
            "agentic_mbse.cli.extract_cli._run_extraction",
            side_effect=mock_run_extraction,
        ):
            result = cmd_extract(args)
        assert result == EXIT_FAILURE

    def test_fallback_on_primary_failure(self, tmp_path, monkeypatch):
        """When primary backend fails and no --backend specified, tries fallback."""
        from agentic_mbse.extraction.base import ExtractionResult

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")

        fail_result = ExtractionResult(
            success=False,
            output_dir=tmp_path / "report",
            error="docling failed",
            backend_used="docling",
        )
        success_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=tmp_path / "report" / "full_document.md",
            backend_used="pymupdf",
        )

        calls = []

        def mock_run_extraction(file_path, output_dir, backend, timeout):
            calls.append(backend)
            if backend == "docling":
                return fail_result
            return success_result

        monkeypatch.setattr(
            "agentic_mbse.cli.extract_cli._is_available", lambda name: True
        )

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend=None,  # auto — allows fallback
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with patch(
            "agentic_mbse.cli.extract_cli._run_extraction",
            side_effect=mock_run_extraction,
        ):
            result = cmd_extract(args)
        assert result == EXIT_SUCCESS
        assert "docling" in calls
        assert "pymupdf" in calls

    def test_no_fallback_when_backend_forced(self, tmp_path, monkeypatch):
        """When --backend is specified, no fallback is attempted."""
        from agentic_mbse.extraction.base import ExtractionResult

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")

        fail_result = ExtractionResult(
            success=False,
            output_dir=tmp_path / "report",
            error="docling failed",
            backend_used="docling",
        )

        calls = []

        def mock_run_extraction(file_path, output_dir, backend, timeout):
            calls.append(backend)
            return fail_result

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="docling",  # forced — no fallback
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with patch(
            "agentic_mbse.cli.extract_cli._run_extraction",
            side_effect=mock_run_extraction,
        ):
            result = cmd_extract(args)
        assert result == EXIT_FAILURE
        assert calls == ["docling"]  # no pymupdf fallback

    def test_fix_tables_post_processing(self, tmp_path):
        """--fix-tables calls repair_tables on successful extraction."""
        from agentic_mbse.extraction.base import ExtractionResult

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        md_path = tmp_path / "report" / "full_document.md"

        mock_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=md_path,
            backend_used="pymupdf",
        )

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=True,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with (
            patch(
                "agentic_mbse.cli.extract_cli._run_extraction",
                return_value=mock_result,
            ),
            patch(
                "agentic_mbse.extraction.table_repair.repair_tables",
                return_value=True,
            ) as mock_repair,
        ):
            result = cmd_extract(args)
        assert result == EXIT_SUCCESS
        mock_repair.assert_called_once_with(md_path)

    def test_index_post_processing(self, tmp_path):
        """--index calls generate_index on successful extraction."""
        from agentic_mbse.extraction.base import ExtractionResult

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        md_path = tmp_path / "report" / "full_document.md"

        mock_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=md_path,
            backend_used="pymupdf",
        )

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=True,
            summarize=False,
            fix_tables=False,
            no_tables=False,
            enhance=False,
            max_repair_pages=None,
        )

        with (
            patch(
                "agentic_mbse.cli.extract_cli._run_extraction",
                return_value=mock_result,
            ),
            patch(
                "agentic_mbse.extraction.index.generate_index",
                return_value=tmp_path / "report" / "INDEX.md",
            ) as mock_index,
        ):
            result = cmd_extract(args)
        assert result == EXIT_SUCCESS
        mock_index.assert_called_once_with(
            md_path, summarize=False, force=False,
        )


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    def test_extract_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "extract" in result.stdout.lower()
        assert "--backend" in result.stdout
        assert "--force" in result.stdout
        assert "--timeout" in result.stdout
        assert "--index" in result.stdout
