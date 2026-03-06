"""Tests for agentic_mbse.cli.extract_cli — Phase 2 (pipeline + CLI rewrite)."""

import subprocess
import warnings
from pathlib import Path
from unittest.mock import patch

from agentic_mbse.cli.extract_cli import (
    cmd_extract,
    discover_documents,
    select_backend,
)
from agentic_mbse.extraction.metrics import compute_metrics
from agentic_mbse.extraction.types import (
    CostRecord,
    PageAction,
    PageDecision,
    PipelineResult,
)
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS


class MockArgs:
    """Mock argparse namespace with new pipeline flags."""

    def __init__(self, **kwargs):
        # Set defaults for all expected attributes
        defaults = dict(
            path="/nonexistent",
            output=None,
            backend=None,
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            budget=2.0,
            no_tables=False,
            no_img2table=False,
            no_equations=False,
            docling=False,
            model="sonnet",
            html_path=None,
            dry_run=False,
            profile=False,
            check=False,
            check_json=False,
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


def _make_pipeline_result(
    markdown: str = "# Test\n\nSome content.",
    error: str | None = None,
    cost: list[CostRecord] | None = None,
) -> PipelineResult:
    """Create a mock PipelineResult."""
    return PipelineResult(
        markdown=markdown,
        metrics=compute_metrics(markdown),
        decisions=[PageDecision(page_num=0, action=PageAction.KEEP)],
        cost=cost or [],
        total_cost_usd=sum(c.cost_usd for c in (cost or [])),
        source="pdf_pipeline",
        error=error,
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

    def test_pdf_auto_returns_none(self):
        """select_backend() returns None for .pdf — pipeline handles PDFs."""
        result = select_backend(Path("x.pdf"), requested=None)
        assert result is None

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
        result = select_backend(Path("x.docx"), requested=None)
        assert result is None


# ---------------------------------------------------------------------------
# cmd_extract — basic dispatch
# ---------------------------------------------------------------------------


class TestCmdExtract:
    def test_returns_failure_for_nonexistent_path(self):
        args = MockArgs(path="/nonexistent/does/not/exist")
        assert cmd_extract(args) == EXIT_FAILURE

    def test_returns_failure_when_no_documents_found(self, tmp_path):
        (tmp_path / "readme.txt").touch()
        args = MockArgs(path=str(tmp_path))
        assert cmd_extract(args) == EXIT_FAILURE

    def test_index_post_processing_for_docx(self, tmp_path):
        """--index calls generate_index on successful DOCX extraction."""
        from agentic_mbse.extraction.base import ExtractionResult

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx content")
        md_path = tmp_path / "report" / "full_document.md"

        mock_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=md_path,
            backend_used="pandoc",
        )

        args = MockArgs(path=str(docx), backend="pandoc", index=True)

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
# PDF pipeline path
# ---------------------------------------------------------------------------


class TestCmdExtractPdf:
    """Verify PDF files route through extract_pdf() with correct config."""

    def _make_args(self, tmp_path, **overrides):
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"fake pdf content")
        defaults = dict(
            path=str(pdf),
            output=str(tmp_path / "out"),
        )
        defaults.update(overrides)
        return MockArgs(**defaults)

    def test_pdf_uses_pipeline(self, tmp_path):
        """PDF file calls extract_pdf(), not old backend path."""
        args = self._make_args(tmp_path)
        mock_result = _make_pipeline_result()

        with (
            patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline,
            patch("agentic_mbse.cli.extract_cli._run_extraction") as mock_run,
        ):
            rc = cmd_extract(args)
        assert rc == EXIT_SUCCESS
        mock_pipeline.assert_called_once()
        mock_run.assert_not_called()

    def test_pdf_budget_flag(self, tmp_path):
        """--budget 0 maps to PipelineConfig(claude_budget_usd=0)."""
        args = self._make_args(tmp_path, budget=0)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].claude_budget_usd == 0

    def test_pdf_dry_run_flag(self, tmp_path):
        """--dry-run maps to PipelineConfig(dry_run=True)."""
        args = self._make_args(tmp_path, dry_run=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].dry_run is True

    def test_pdf_no_tables_flag(self, tmp_path):
        """--no-tables maps to enable_tables=False."""
        args = self._make_args(tmp_path, no_tables=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].enable_tables is False

    def test_pdf_no_img2table_flag(self, tmp_path):
        """--no-img2table maps to enable_img2table=False."""
        args = self._make_args(tmp_path, no_img2table=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].enable_img2table is False

    def test_pdf_no_equations_flag(self, tmp_path):
        """--no-equations maps to enable_equations=False."""
        args = self._make_args(tmp_path, no_equations=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].enable_equations is False

    def test_pdf_docling_flag(self, tmp_path):
        """--docling maps to enable_docling=True."""
        args = self._make_args(tmp_path, docling=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].enable_docling is True

    def test_pdf_model_flag(self, tmp_path):
        """--model sonnet maps to claude_model='sonnet'."""
        args = self._make_args(tmp_path, model="sonnet")
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].claude_model == "sonnet"

    def test_pdf_html_path_flag(self, tmp_path):
        """--html-path /tmp/a.html maps to arxiv_html_path."""
        args = self._make_args(tmp_path, html_path="/tmp/a.html")
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            cmd_extract(args)
        _, kwargs = mock_pipeline.call_args
        assert kwargs["config"].arxiv_html_path == Path("/tmp/a.html")

    def test_pdf_output_files(self, tmp_path):
        """Pipeline writes output.md, metrics.json, decisions.json."""
        args = self._make_args(tmp_path)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result):
            cmd_extract(args)

        out_dir = tmp_path / "out" / "paper"
        assert (out_dir / "output.md").exists()
        assert (out_dir / "metrics.json").exists()
        assert (out_dir / "decisions.json").exists()

    def test_pdf_cost_json_only_when_claude_used(self, tmp_path):
        """cost.json present iff result.cost non-empty."""
        # No cost
        args = self._make_args(tmp_path)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result):
            cmd_extract(args)

        out_dir = tmp_path / "out" / "paper"
        assert not (out_dir / "cost.json").exists()

        # With cost
        cost = [CostRecord(page_num=0, cost_usd=0.05, model="sonnet")]
        mock_result2 = _make_pipeline_result(cost=cost)
        args2 = self._make_args(tmp_path, force=True)

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result2):
            cmd_extract(args2)

        assert (out_dir / "cost.json").exists()

    def test_pdf_error_reports_failure(self, tmp_path):
        """PipelineResult(error=...) → FAIL in output, exit FAILURE, no artifacts written."""
        args = self._make_args(tmp_path)
        mock_result = _make_pipeline_result(error="corrupt PDF")

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result):
            rc = cmd_extract(args)
        assert rc == EXIT_FAILURE
        # No output.md written on error — allows automatic retry on next run
        out_dir = tmp_path / "out" / "paper"
        assert not (out_dir / "output.md").exists()

    def test_pdf_skip_when_output_exists(self, tmp_path):
        """PDF skip check: existing output.md → skip unless --force."""
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"fake pdf content")
        out_dir = tmp_path / "out" / "paper"
        out_dir.mkdir(parents=True)
        (out_dir / "output.md").write_text("# Old output")

        args = MockArgs(path=str(pdf), output=str(tmp_path / "out"))

        with patch("agentic_mbse.cli.extract_cli.extract_pdf") as mock_pipeline:
            rc = cmd_extract(args)
        mock_pipeline.assert_not_called()
        assert rc == EXIT_SUCCESS

    def test_pdf_force_reprocesses(self, tmp_path):
        """--force processes even if output.md exists."""
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"fake pdf content")
        out_dir = tmp_path / "out" / "paper"
        out_dir.mkdir(parents=True)
        (out_dir / "output.md").write_text("# Old output")

        args = MockArgs(path=str(pdf), output=str(tmp_path / "out"), force=True)
        mock_result = _make_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result) as mock_pipeline:
            rc = cmd_extract(args)
        mock_pipeline.assert_called_once()
        assert rc == EXIT_SUCCESS

    def test_pdf_index_post_processing(self, tmp_path):
        """--index runs generate_index on pipeline output."""
        args = self._make_args(tmp_path, index=True)
        mock_result = _make_pipeline_result()

        with (
            patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result),
            patch(
                "agentic_mbse.extraction.index.generate_index",
                return_value=tmp_path / "out" / "paper" / "INDEX.md",
            ) as mock_index,
        ):
            cmd_extract(args)
        mock_index.assert_called_once()


# ---------------------------------------------------------------------------
# DOCX path (preserved behavior)
# ---------------------------------------------------------------------------


class TestCmdExtractDocx:
    """Verify DOCX files still use backend selection path."""

    def test_docx_uses_backend_selection(self, tmp_path):
        """DOCX still goes through select_backend() + _run_extraction()."""
        from agentic_mbse.extraction.base import ExtractionResult

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx content")
        mock_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=tmp_path / "report" / "full_document.md",
            backend_used="pandoc",
        )

        args = MockArgs(path=str(docx), backend="pandoc")

        with (
            patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result) as mock_run,
            patch("agentic_mbse.cli.extract_cli.extract_pdf") as mock_pipeline,
        ):
            rc = cmd_extract(args)
        assert rc == EXIT_SUCCESS
        mock_run.assert_called_once()
        mock_pipeline.assert_not_called()

    def test_backend_flag_applies_to_docx(self, tmp_path):
        """--backend pandoc works for DOCX."""
        from agentic_mbse.extraction.base import ExtractionResult

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx content")
        mock_result = ExtractionResult(
            success=True,
            output_dir=tmp_path / "report",
            markdown_path=tmp_path / "report" / "full_document.md",
            backend_used="pandoc",
        )

        args = MockArgs(path=str(docx), backend="pandoc")

        with patch("agentic_mbse.cli.extract_cli._run_extraction", return_value=mock_result) as mock_run:
            rc = cmd_extract(args)
        assert rc == EXIT_SUCCESS
        # _run_extraction(file_path, output_dir, backend, timeout) — positional args
        call_args = mock_run.call_args[0]
        assert call_args[2] == "pandoc"


# ---------------------------------------------------------------------------
# Legacy flags removed
# ---------------------------------------------------------------------------


class TestLegacyFlagsRemoved:
    """Verify legacy flags are not recognized."""

    def test_fix_tables_not_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True, text=True,
        )
        assert "--fix-tables" not in result.stdout

    def test_enhance_not_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True, text=True,
        )
        assert "--enhance" not in result.stdout

    def test_structure_only_not_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True, text=True,
        )
        assert "--structure-only" not in result.stdout

    def test_max_repair_pages_not_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True, text=True,
        )
        assert "--max-repair-pages" not in result.stdout


# ---------------------------------------------------------------------------
# Deprecation warnings for legacy flags
# ---------------------------------------------------------------------------


class TestDeprecationWarnings:
    """Legacy flags emit deprecation warnings pointing to new pipeline."""

    def _make_args(self, tmp_path, **overrides):
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"fake pdf content")
        defaults = dict(
            path=str(pdf),
            output=str(tmp_path / "out"),
            fix_tables=False,
            enhance=False,
            structure_only=False,
        )
        defaults.update(overrides)
        return MockArgs(**defaults)

    def test_fix_tables_emits_warning(self, tmp_path):
        """--fix-tables emits deprecation warning."""
        args = self._make_args(tmp_path, fix_tables=True)
        mock_result = _make_pipeline_result()

        with (
            patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            cmd_extract(args)
        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any("--fix-tables" in str(x.message) for x in dep_warnings)

    def test_enhance_emits_warning(self, tmp_path):
        """--enhance emits deprecation warning."""
        args = self._make_args(tmp_path, enhance=True)
        mock_result = _make_pipeline_result()

        with (
            patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            cmd_extract(args)
        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any("--enhance" in str(x.message) for x in dep_warnings)

    def test_structure_only_emits_warning(self, tmp_path):
        """--structure-only emits deprecation warning."""
        args = self._make_args(tmp_path, structure_only=True)
        mock_result = _make_pipeline_result()

        with (
            patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=mock_result),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            cmd_extract(args)
        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any("--structure-only" in str(x.message) for x in dep_warnings)


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
        # New flags
        assert "--budget" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--no-img2table" in result.stdout
        assert "--docling" in result.stdout
        assert "--html-path" in result.stdout
