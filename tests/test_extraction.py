"""Tests for agentic_mbse.extraction package."""

import hashlib
import json
import time
from pathlib import Path
from unittest.mock import MagicMock

from agentic_mbse.extraction.base import (
    TIMEOUT,
    ExtractionResult,
    ProcessCrashedError,
    _Timeout,
    check_processing_needed,
    get_output_dir,
    run_with_timeout,
    sanitize_filename,
    write_summary,
)

# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------


class TestSanitizeFilename:
    def test_removes_extension(self):
        assert sanitize_filename("report.pdf") == "report"

    def test_replaces_spaces_and_special_chars(self):
        assert sanitize_filename("My Report (v2).pdf") == "My_Report__v2_"

    def test_replaces_hyphens(self):
        assert sanitize_filename("my-report.pdf") == "my_report"

    def test_truncates_long_names(self):
        name = "a" * 150 + ".pdf"
        result = sanitize_filename(name)
        assert len(result) <= 100

    def test_handles_no_extension(self):
        assert sanitize_filename("report") == "report"

    def test_preserves_underscores(self):
        assert sanitize_filename("my_report.pdf") == "my_report"


# ---------------------------------------------------------------------------
# get_output_dir
# ---------------------------------------------------------------------------


class TestGetOutputDir:
    def test_default_alongside_input(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        result = get_output_dir(pdf)
        assert result == tmp_path / "report"

    def test_custom_output_base(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        out = tmp_path / "output"
        result = get_output_dir(pdf, output_base=out)
        assert result == out / "report"

    def test_sanitizes_directory_name(self, tmp_path):
        pdf = tmp_path / "My Report (v2).pdf"
        pdf.touch()
        result = get_output_dir(pdf)
        assert result == tmp_path / "My_Report__v2_"


# ---------------------------------------------------------------------------
# check_processing_needed
# ---------------------------------------------------------------------------


class TestCheckProcessingNeeded:
    def test_needed_when_no_output_dir(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        assert check_processing_needed(pdf, tmp_path / "report") is True

    def test_not_needed_when_hash_matches(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        # Write summary.json with matching hash
        file_hash = "md5:" + hashlib.md5(b"fake pdf content").hexdigest()
        summary = {"file_hash": file_hash, "processing_completed": True}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        assert check_processing_needed(pdf, output_dir) is False

    def test_needed_when_hash_differs(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"new content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        summary = {"file_hash": "md5:oldhash", "processing_completed": True}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        assert check_processing_needed(pdf, output_dir) is True

    def test_needed_when_force(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        file_hash = "md5:" + hashlib.md5(b"fake pdf content").hexdigest()
        summary = {"file_hash": file_hash, "processing_completed": True}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        assert check_processing_needed(pdf, output_dir, force=True) is True

    def test_needed_when_processing_incomplete(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        file_hash = "md5:" + hashlib.md5(b"fake pdf content").hexdigest()
        summary = {"file_hash": file_hash, "processing_completed": False}
        (output_dir / "summary.json").write_text(json.dumps(summary))

        assert check_processing_needed(pdf, output_dir) is True


# ---------------------------------------------------------------------------
# write_summary
# ---------------------------------------------------------------------------


class TestWriteSummary:
    def test_writes_valid_json(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        result = ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=output_dir / "full_document.md",
            image_count=5,
            char_count=12000,
        )
        write_summary(pdf, output_dir, result, "pymupdf")

        summary_path = output_dir / "summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text())

        assert summary["source_file"] == "report.pdf"
        assert summary["source_format"] == "pdf"
        assert summary["backend_used"] == "pymupdf"
        assert summary["processing_completed"] is True
        assert summary["file_hash"].startswith("md5:")
        assert summary["statistics"]["total_images"] == 5
        assert summary["statistics"]["total_characters"] == 12000
        assert summary["statistics"]["file_size_bytes"] == len(b"fake pdf content")
        assert summary["error"] is None
        assert "processed_at" in summary

    def test_writes_error_summary(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf content")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        result = ExtractionResult(
            success=False,
            output_dir=output_dir,
            error="Extraction failed: corrupt file",
        )
        write_summary(pdf, output_dir, result, "pymupdf")

        summary = json.loads((output_dir / "summary.json").read_text())
        assert summary["processing_completed"] is False
        assert summary["error"] == "Extraction failed: corrupt file"

    def test_detects_docx_format(self, tmp_path):
        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        output_dir = tmp_path / "report"
        output_dir.mkdir()

        result = ExtractionResult(success=True, output_dir=output_dir)
        write_summary(docx, output_dir, result, "pandoc")

        summary = json.loads((output_dir / "summary.json").read_text())
        assert summary["source_format"] == "docx"


# ---------------------------------------------------------------------------
# PyMuPDF Backend
# ---------------------------------------------------------------------------


class TestPymupdfBackend:
    def test_extract_produces_markdown_and_images(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pymupdf_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        chunks = [{"metadata": {"page": 0}, "text": "# Title\n\nSome content\n"}]
        mock_to_markdown = MagicMock(return_value=chunks)
        monkeypatch.setattr(
            pymupdf_backend, "_get_to_markdown", lambda: mock_to_markdown
        )

        result = pymupdf_backend.extract(pdf, output_dir)

        assert result.success is True
        assert result.markdown_path == output_dir / "full_document.md"
        written = (output_dir / "full_document.md").read_text()
        # Page marker is inserted, then the content
        assert "<!-- PAGE:0 -->" in written
        assert "# Title" in written
        assert "Some content" in written
        assert (output_dir / "images").is_dir()

    def test_extract_passes_hdr_info_and_table_strategy(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pymupdf_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        chunks = [{"metadata": {"page": 0}, "text": "Content here"}]
        mock_to_markdown = MagicMock(return_value=chunks)
        monkeypatch.setattr(
            pymupdf_backend, "_get_to_markdown", lambda: mock_to_markdown
        )

        result = pymupdf_backend.extract(pdf, output_dir)
        assert result.success is True
        assert result.backend_used == "pymupdf"

        # Verify hdr_info, table_strategy, and page_chunks were passed
        call_kwargs = mock_to_markdown.call_args[1]
        assert call_kwargs["hdr_info"] is pymupdf_backend._academic_header_detector
        assert call_kwargs["table_strategy"] == "lines"
        assert call_kwargs["page_chunks"] is True

    def test_extract_applies_postprocess(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pymupdf_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        # Bold header should be promoted by postprocess
        chunks = [{"metadata": {"page": 0}, "text": "**1 Introduction**\n\nContent.\n"}]
        mock_to_markdown = MagicMock(return_value=chunks)
        monkeypatch.setattr(
            pymupdf_backend, "_get_to_markdown", lambda: mock_to_markdown
        )

        result = pymupdf_backend.extract(pdf, output_dir)
        assert result.success is True
        written = (output_dir / "full_document.md").read_text()
        assert "## 1 Introduction" in written
        assert "**1 Introduction**" not in written

    def test_extract_returns_error_on_failure(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pymupdf_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        mock_to_markdown = MagicMock(side_effect=RuntimeError("parse error"))
        monkeypatch.setattr(
            pymupdf_backend, "_get_to_markdown", lambda: mock_to_markdown
        )

        result = pymupdf_backend.extract(pdf, output_dir)
        assert result.success is False
        assert result.error is not None
        assert "parse error" in result.error

    def test_counts_images(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pymupdf_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        images_dir = output_dir / "images"
        images_dir.mkdir()
        # Pre-create some images that pymupdf4llm would write
        (images_dir / "img_001.png").write_bytes(b"png")
        (images_dir / "img_002.png").write_bytes(b"png")

        chunks = [{"metadata": {"page": 0}, "text": "Content with images"}]
        mock_to_markdown = MagicMock(return_value=chunks)
        monkeypatch.setattr(
            pymupdf_backend, "_get_to_markdown", lambda: mock_to_markdown
        )

        result = pymupdf_backend.extract(pdf, output_dir)
        assert result.success is True
        assert result.image_count == 2


# ---------------------------------------------------------------------------
# run_with_timeout
# ---------------------------------------------------------------------------


def _fast_multiply(x):
    return x * 2


def _slow_func():
    time.sleep(60)


def _failing_func():
    raise ValueError("boom")


class TestRunWithTimeout:
    def test_returns_result_on_success(self):
        result = run_with_timeout(_fast_multiply, (5,), timeout=10)
        assert result == 10

    def test_returns_timeout_sentinel_on_timeout(self):
        result = run_with_timeout(_slow_func, (), timeout=1)
        assert isinstance(result, _Timeout)
        assert result is TIMEOUT

    def test_returns_exception_on_error(self):
        result = run_with_timeout(_failing_func, (), timeout=10)
        assert isinstance(result, ValueError)


# ---------------------------------------------------------------------------
# Docling Backend
# ---------------------------------------------------------------------------


class TestDoclingBackend:
    def test_extract_returns_error_on_timeout(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import docling_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        # Make _docling_extract_inner sleep forever to trigger timeout
        def slow_inner(input_path, output_dir):
            time.sleep(60)

        monkeypatch.setattr(docling_backend, "_docling_extract_inner", slow_inner)

        result = docling_backend.extract(pdf, output_dir, timeout=1)
        assert result.success is False
        assert "timed out" in result.error

    def test_extract_returns_error_on_crash(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import docling_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        # Simulate a process crash by having run_with_timeout raise ProcessCrashedError
        def mock_run_with_timeout(func, args=(), timeout=600):
            raise ProcessCrashedError(exit_code=-9)

        monkeypatch.setattr(docling_backend, "run_with_timeout", mock_run_with_timeout)

        result = docling_backend.extract(pdf, output_dir, timeout=1)
        assert result.success is False
        assert "crashed" in result.error
        assert "-9" in result.error

    def test_extract_returns_error_on_exception(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import docling_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        def failing_inner(input_path, output_dir):
            raise RuntimeError("docling crashed")

        monkeypatch.setattr(docling_backend, "_docling_extract_inner", failing_inner)

        result = docling_backend.extract(pdf, output_dir, timeout=10)
        assert result.success is False
        assert "docling crashed" in result.error

    def test_extract_returns_result_on_success(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import docling_backend

        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        output_dir = tmp_path / "output"

        expected = ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=output_dir / "full_document.md",
            image_count=3,
            char_count=500,
            backend_used="docling",
        )

        def ok_inner(input_path, output_dir):
            return expected

        monkeypatch.setattr(docling_backend, "_docling_extract_inner", ok_inner)

        result = docling_backend.extract(pdf, output_dir, timeout=10)
        assert result.success is True
        assert result.backend_used == "docling"
        assert result.image_count == 3

    def test_rewrite_image_paths(self):
        from agentic_mbse.extraction.docling_backend import _rewrite_image_paths

        images_dir = Path("/tmp/output/images")
        md = "![fig](/tmp/output/images/figure_001.png)"
        result = _rewrite_image_paths(md, images_dir)
        assert result == "![fig](images/figure_001.png)"


# ---------------------------------------------------------------------------
# Pandoc Backend
# ---------------------------------------------------------------------------


class TestPandocBackend:
    def test_extract_fails_when_pandoc_missing(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pandoc_backend

        monkeypatch.setattr(pandoc_backend, "_pandoc_available", lambda: False)

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        output_dir = tmp_path / "output"

        result = pandoc_backend.extract(docx, output_dir)
        assert result.success is False
        assert "pandoc" in result.error.lower()

    def test_extract_calls_pandoc_subprocess(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pandoc_backend

        monkeypatch.setattr(pandoc_backend, "_pandoc_available", lambda: True)

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        output_dir = tmp_path / "output"

        # Mock subprocess.run to write a fake markdown file
        def fake_run(cmd, **kwargs):
            md_path = output_dir / "full_document.md"
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text("# Test\n\nContent here\n")

            class FakeResult:
                returncode = 0
                stderr = ""

            return FakeResult()

        monkeypatch.setattr(pandoc_backend.subprocess, "run", fake_run)

        result = pandoc_backend.extract(docx, output_dir)
        assert result.success is True
        assert result.backend_used == "pandoc"
        assert result.markdown_path == output_dir / "full_document.md"
        assert result.char_count > 0

    def test_extract_handles_pandoc_failure(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pandoc_backend

        monkeypatch.setattr(pandoc_backend, "_pandoc_available", lambda: True)

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        output_dir = tmp_path / "output"

        def failing_run(cmd, **kwargs):
            class FakeResult:
                returncode = 1
                stderr = "Unknown input format"

            return FakeResult()

        monkeypatch.setattr(pandoc_backend.subprocess, "run", failing_run)

        result = pandoc_backend.extract(docx, output_dir)
        assert result.success is False
        assert "Unknown input format" in result.error

    def test_image_paths_are_relative(self, tmp_path, monkeypatch):
        from agentic_mbse.extraction import pandoc_backend

        monkeypatch.setattr(pandoc_backend, "_pandoc_available", lambda: True)

        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        output_dir = tmp_path / "output"

        media_dir = output_dir / "media"

        def fake_run(cmd, **kwargs):
            output_dir.mkdir(parents=True, exist_ok=True)
            md_path = output_dir / "full_document.md"
            # Pandoc writes media refs with the media dir path
            md_path.write_text(f"![diagram]({media_dir}/image1.png)\n")
            # Also create the media file
            media_dir.mkdir(parents=True, exist_ok=True)
            (media_dir / "image1.png").write_bytes(b"fake png")

            class FakeResult:
                returncode = 0
                stderr = ""

            return FakeResult()

        monkeypatch.setattr(pandoc_backend.subprocess, "run", fake_run)

        result = pandoc_backend.extract(docx, output_dir)
        assert result.success is True
        assert result.image_count == 1

        md_content = (output_dir / "full_document.md").read_text()
        assert "images/image1.png" in md_content
        # Media dir should have been cleaned up
        assert not media_dir.exists()
        # Image should have been moved
        assert (output_dir / "images" / "image1.png").exists()

    def test_rewrite_image_paths(self):
        from agentic_mbse.extraction.pandoc_backend import _rewrite_image_paths

        media_dir = Path("/tmp/output/media")
        images_dir = Path("/tmp/output/images")
        md = "![fig](/tmp/output/media/image1.png)"
        result = _rewrite_image_paths(md, media_dir, images_dir)
        assert result == "![fig](images/image1.png)"

    def test_rewrite_image_paths_no_false_positive(self):
        from agentic_mbse.extraction.pandoc_backend import _rewrite_image_paths

        media_dir = Path("/tmp/output/media")
        images_dir = Path("/tmp/output/images")
        md = "The media team provided results. ![fig](media/image1.png)"
        result = _rewrite_image_paths(md, media_dir, images_dir)
        assert "The media team provided results." in result
        assert "![fig](images/image1.png)" in result
