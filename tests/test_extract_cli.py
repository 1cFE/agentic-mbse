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


def _make_extraction_result(tmp_path, md_content="# Test\n\nSome content."):
    """Create a mock ExtractionResult with a real markdown file on disk."""
    from agentic_mbse.extraction.base import ExtractionResult

    output_dir = tmp_path / "report"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / "full_document.md"
    md_path.write_text(md_content)
    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        backend_used="pymupdf",
    )


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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
            structure_only=False,
            model=None,
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
# Structural pass (L3) integration
# ---------------------------------------------------------------------------


class TestStructuralPass:
    """Tests for L3 Claude structural pass integration."""

    def test_enhance_triggers_structural_pass(self, tmp_path):
        """--enhance runs L3 (structure) then L4 (AI repair) in order."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        struct_meta = {"headers_inserted": 3, "headers_skipped": 1, "warnings": [], "phase_a": {}}
        call_order = []

        def mock_enhance(md, pdf_path, out_dir, **kw):
            call_order.append("enhance_structure")
            return md, struct_meta

        def mock_repair(md, pdf_path, problems, **kw):
            call_order.append("repair_document")
            return md, {"repairs": 1, "rejections": 0}

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=True,
            max_repair_pages=None,
            structure_only=False,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=True),
            patch("agentic_mbse.extraction.claude_structure.enhance_structure", side_effect=mock_enhance),
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[object()]),
            patch("agentic_mbse.extraction.ai_repair.repair_document", side_effect=mock_repair),
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        assert call_order == ["enhance_structure", "repair_document"]

    def test_enhance_skips_structure_when_not_needed(self, tmp_path):
        """--enhance with well-structured doc skips L3, still runs L4."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=True,
            max_repair_pages=None,
            structure_only=False,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=False),
            patch("agentic_mbse.extraction.claude_structure.enhance_structure") as mock_enhance,
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[object()]),
            patch(
                "agentic_mbse.extraction.ai_repair.repair_document",
                return_value=("fixed", {"repairs": 1, "rejections": 0}),
            ) as mock_repair,
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_enhance.assert_not_called()
        mock_repair.assert_called_once()

    def test_structure_only_skips_ai_repair(self, tmp_path):
        """--structure-only runs L3 without L4."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        struct_meta = {"headers_inserted": 2, "headers_skipped": 0, "warnings": [], "phase_a": {}}

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=False,
            max_repair_pages=None,
            structure_only=True,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=True),
            patch(
                "agentic_mbse.extraction.claude_structure.enhance_structure",
                return_value=("modified", struct_meta),
            ) as mock_enhance,
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[]),
            patch("agentic_mbse.extraction.ai_repair.repair_document") as mock_repair_fn,
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_enhance.assert_called_once()
        mock_repair_fn.assert_not_called()

    def test_model_flag_passed_through(self, tmp_path):
        """--model sonnet overrides both Phase A and Phase B."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        struct_meta = {"headers_inserted": 1, "headers_skipped": 0, "warnings": [], "phase_a": {}}

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=True,
            max_repair_pages=None,
            structure_only=False,
            model="sonnet",
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=True),
            patch(
                "agentic_mbse.extraction.claude_structure.enhance_structure",
                return_value=("modified", struct_meta),
            ) as mock_enhance,
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[]),
            patch("agentic_mbse.extraction.ai_repair.repair_document"),
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_enhance.assert_called_once()
        _, kwargs = mock_enhance.call_args
        assert kwargs["phase_a_model"] == "sonnet"
        assert kwargs["phase_b_model"] == "sonnet"

    def test_structure_failure_continues_pipeline(self, tmp_path):
        """L3 failure -> warning, pipeline continues to L4."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=True,
            max_repair_pages=None,
            structure_only=False,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=True),
            patch(
                "agentic_mbse.extraction.claude_structure.enhance_structure",
                side_effect=RuntimeError("Claude subprocess failed"),
            ),
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[object()]),
            patch(
                "agentic_mbse.extraction.ai_repair.repair_document",
                return_value=("fixed", {"repairs": 1, "rejections": 0}),
            ) as mock_repair,
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_repair.assert_called_once()

    def test_default_mode_no_structural_pass(self, tmp_path):
        """Default mode (no --enhance/--structure-only) never calls L3 or L4."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=False,
            max_repair_pages=None,
            structure_only=False,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure") as mock_needs,
            patch("agentic_mbse.extraction.claude_structure.enhance_structure") as mock_enhance,
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[]),
            patch("agentic_mbse.extraction.ai_repair.repair_document") as mock_repair,
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_needs.assert_not_called()
        mock_enhance.assert_not_called()
        mock_repair.assert_not_called()

    def test_enhance_and_structure_only_skips_ai_repair(self, tmp_path):
        """--enhance --structure-only together: structure_only wins, L4 skipped."""
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        mock_result = _make_extraction_result(tmp_path)

        struct_meta = {"headers_inserted": 2, "headers_skipped": 0, "warnings": [], "phase_a": {}}

        args = MockArgs(
            path=str(pdf),
            output=None,
            backend="pymupdf",
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            fix_tables=False,
            no_tables=True,
            enhance=True,
            max_repair_pages=None,
            structure_only=True,
            model=None,
        )

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result),
            patch("agentic_mbse.extraction.claude_structure.needs_claude_structure", return_value=True),
            patch(
                "agentic_mbse.extraction.claude_structure.enhance_structure",
                return_value=("modified", struct_meta),
            ) as mock_enhance,
            patch("agentic_mbse.extraction.quality_gates.detect_problems", return_value=[object()]),
            patch("agentic_mbse.extraction.ai_repair.repair_document") as mock_repair,
        ):
            result = cmd_extract(args)

        assert result == EXIT_SUCCESS
        mock_enhance.assert_called_once()
        mock_repair.assert_not_called()


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
