"""PDF document converter using the proven extraction pipeline.

Uses the 4-layer extraction pipeline from agentic_mbse.extraction:
- Layer 1: pymupdf_backend with academic header detector
- Layer 1b: postprocess (header promotion, noise rejection, ligatures)

This replaces the previous raw pymupdf4llm approach, dramatically improving
heading detection and preserving page markers for downstream processing.
"""

import re
import tempfile
from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

from agentic_mbse.extraction.pymupdf_backend import extract
from doc_ingest.types import (
    ConversionError,
    ConversionResult,
    QualityFlags,
    SourceFormat,
    ValidationResult,
)


class PyMuPDF4LLMConverter:
    """PDF converter using pymupdf4llm for markdown extraction.

    Validates PDFs for extractable text (detects scanned documents) and converts
    native PDFs to markdown with quality flags for table/heading detection.

    Raises ConversionError with category="needs_ocr" for scanned PDFs.
    """

    @property
    def name(self) -> str:
        """Return converter name for provenance tracking."""
        return "PyMuPDF4LLMConverter"

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter handles PDF format.

        Args:
            format: Source format type

        Returns:
            True if format is "pdf", False otherwise
        """
        return format == "pdf"

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate PDF content for extractable text.

        Detects scanned PDFs (no extractable text) by checking text extraction
        from the first few pages. A PDF with less than 50 characters of text
        across the first 3 pages is considered scanned.

        Args:
            content: Raw PDF bytes

        Returns:
            ValidationResult with is_valid=False for scanned PDFs
        """
        try:
            # Open PDF from bytes
            doc = pymupdf.open(stream=content, filetype="pdf")

            # Check first 3 pages (or fewer if document is shorter)
            pages_to_check = min(3, len(doc))
            total_text = ""

            for page_num in range(pages_to_check):
                page = doc[page_num]
                total_text += page.get_text()

            doc.close()

            # Heuristic: Less than 50 chars suggests scanned PDF
            has_text = len(total_text.strip()) >= 50
            content_length = len(content)

            return ValidationResult(
                is_valid=has_text,
                content_length=content_length,
                has_body_content=has_text,
                detected_content_type="application/pdf",
            )

        except Exception:
            # Failed to open as PDF - invalid format
            return ValidationResult(
                is_valid=False,
                content_length=len(content),
                has_body_content=False,
                detected_content_type="unknown",
            )

    def convert(self, content: bytes) -> ConversionResult:
        """Convert PDF to markdown using the proven extraction pipeline.

        Uses Layer 1 (pymupdf_backend + postprocess) which provides:
        - Academic header detection (section numbering)
        - Header promotion from bold text
        - Noise rejection and ligature repair
        - Page markers for downstream processing

        Args:
            content: Raw PDF bytes

        Returns:
            ConversionResult with markdown, quality flags, and warnings

        Raises:
            ConversionError: If PDF is scanned (needs_ocr) or conversion fails
        """
        # Validate first
        validation = self.validate_source(content)
        if not validation.is_valid:
            raise ConversionError(
                "PDF contains no extractable text (likely scanned)",
                category="needs_ocr",
                details={"content_length": validation.content_length},
            )

        try:
            # Write content to temporary file (pymupdf_backend requires Path)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                tmp_pdf.write(content)
                tmp_pdf_path = Path(tmp_pdf.name)

            # Create temporary output directory for extraction
            with tempfile.TemporaryDirectory() as tmp_out:
                tmp_out_path = Path(tmp_out)

                # Layer 1: pymupdf_backend (custom header detector + page markers)
                extraction_result = extract(input_path=tmp_pdf_path, output_dir=tmp_out_path)

                if not extraction_result.success:
                    raise ConversionError(
                        f"Extraction backend failed: {extraction_result.error}",
                        category="unknown",
                        details={"backend_used": extraction_result.backend_used},
                    )

                # Read the extracted markdown
                md_path = tmp_out_path / "full_document.md"
                md_text = md_path.read_text()

                # Open PDF for quality flag detection
                doc = pymupdf.open(stream=content, filetype="pdf")

                # Compute quality flags from ACTUAL output (not heuristics)
                images_dir = tmp_out_path / "images"
                quality_flags = self._compute_quality_flags_from_output(
                    doc=doc, markdown=md_text, images_dir=images_dir
                )

                # Detect potential warnings
                warnings = self._detect_warnings(doc, md_text)

                doc.close()

                # Clean up temp PDF
                tmp_pdf_path.unlink()

                return ConversionResult(
                    markdown=md_text,
                    warnings=warnings,
                    quality_flags=quality_flags,
                    converter_name=self.name,
                )

        except ConversionError:
            # Re-raise ConversionErrors as-is
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise ConversionError(
                f"PDF conversion failed: {e}",
                category="unknown",
                details={"error_type": type(e).__name__},
            ) from e

    def _compute_quality_flags_from_output(
        self, doc: pymupdf.Document, markdown: str, images_dir: Path
    ) -> QualityFlags:
        """Compute quality flags from actual extraction output.

        This replaces heuristic-based detection with observation of the actual
        markdown produced by the extraction pipeline.

        Args:
            doc: Opened pymupdf Document (for PDF-level checks)
            markdown: Extracted markdown text (after postprocessing)
            images_dir: Directory containing extracted images

        Returns:
            QualityFlags with detected characteristics
        """
        flags = QualityFlags()

        # Detect tables: Look for markdown table syntax in output
        table_pattern = re.compile(r"\|.*\|")
        has_table_markers = bool(table_pattern.search(markdown))

        # Check if document has actual table structures via PyMuPDF
        has_pdf_tables = False
        for page in doc:
            tables = page.find_tables()
            if tables and len(tables.tables) > 0:
                has_pdf_tables = True
                break

        flags.has_tables = has_table_markers or has_pdf_tables

        # Table corruption: If PDF has tables but markdown doesn't
        # Note: Layer 2 (GMFT) will address this in TASK-WP-002
        if has_pdf_tables and not has_table_markers:
            flags.tables_likely_corrupted = True
        elif has_table_markers:
            # Check for malformed tables: rows with inconsistent column counts
            table_rows = table_pattern.findall(markdown)
            if len(table_rows) > 2:  # Need at least header + separator + 1 row
                column_counts = [len(row.split("|")) for row in table_rows[:10]]
                if len(set(column_counts)) > 2:
                    flags.tables_likely_corrupted = True

        # Heading detection: postprocessing promotes headers to markdown format
        # Check for markdown heading markers (# ## ###)
        heading_pattern = re.compile(r"^#{1,6}\s+\S+", re.MULTILINE)
        flags.heading_structure_detected = bool(heading_pattern.search(markdown))

        # Math detection: Unicode math symbols present in output
        math_indicators = re.compile(
            r"(\$.*?\$|\\[a-zA-Z]+|[∫∑∏∂√π≈≠≤≥±×÷·²³⁴⁰¹]|"
            r"equation|formula|theorem|proof)",
            re.IGNORECASE,
        )
        flags.has_math = bool(math_indicators.search(markdown))

        # Figure detection: Check if images were extracted
        flags.has_figures = any(images_dir.iterdir()) if images_dir.exists() else False

        return flags

    def _detect_warnings(self, doc: pymupdf.Document, markdown: str) -> list[str]:
        """Detect potential issues and generate warnings.

        Checks for:
        - Large page counts (may indicate memory concerns)
        - Missing figures (PDF has images but none in markdown)
        - Possible table corruption

        Args:
            doc: Opened pymupdf Document
            markdown: Extracted markdown text

        Returns:
            List of warning messages
        """
        warnings = []

        # Large PDF warning
        page_count = len(doc)
        if page_count > 100:
            warnings.append(f"Large PDF ({page_count} pages) - extraction may be incomplete")

        # Figure detection: Check if PDF has images
        has_images = False
        for page in doc:
            if len(page.get_images()) > 0:
                has_images = True
                break

        if has_images:
            # pymupdf4llm doesn't typically extract images, so this is expected
            warnings.append("PDF contains images - not extracted in markdown")

        return warnings
