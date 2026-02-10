"""PDF document converter using pymupdf4llm.

Converts PDF documents to markdown, with validation for scanned PDFs,
quality flag reporting for tables/math/headings, and typed error handling.
"""

import re

import pymupdf  # type: ignore[import-untyped]
import pymupdf4llm  # type: ignore[import-untyped]

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
        """Convert PDF to markdown using pymupdf4llm.

        Extracts text, detects tables and headings, and populates quality flags.
        Raises ConversionError for scanned PDFs or conversion failures.

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
            # Open PDF from bytes
            doc = pymupdf.open(stream=content, filetype="pdf")

            # Convert to markdown using pymupdf4llm
            md_text = pymupdf4llm.to_markdown(doc)

            # Detect quality characteristics
            quality_flags = self._detect_quality_flags(doc, md_text)

            # Detect potential warnings
            warnings = self._detect_warnings(doc, md_text)

            doc.close()

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

    def _detect_quality_flags(self, doc: pymupdf.Document, markdown: str) -> QualityFlags:
        """Detect quality characteristics from PDF and markdown.

        Checks for:
        - Tables: Presence of table-like structures in markdown
        - Table corruption: Complex tables that may be garbled
        - Headings: Markdown heading markers (# ## ###)

        Args:
            doc: Opened pymupdf Document
            markdown: Extracted markdown text

        Returns:
            QualityFlags with detected characteristics
        """
        flags = QualityFlags()

        # Detect tables: Look for markdown table syntax (|...|)
        # or pymupdf4llm table indicators
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

        # Table corruption heuristic: If PDF has tables but markdown doesn't,
        # or if markdown has malformed table rows
        if has_pdf_tables and not has_table_markers:
            flags.tables_likely_corrupted = True
        elif has_table_markers:
            # Check for malformed tables: rows with inconsistent column counts
            table_rows = table_pattern.findall(markdown)
            if len(table_rows) > 2:  # Need at least header + separator + 1 row
                column_counts = [len(row.split("|")) for row in table_rows[:10]]
                # If variance in column counts, likely corrupted
                if len(set(column_counts)) > 2:  # Allow some variation for edge formatting
                    flags.tables_likely_corrupted = True

        # Detect heading structure: Markdown headings (# ## ###)
        heading_pattern = re.compile(r"^#{1,6}\s+\S+", re.MULTILINE)
        flags.heading_structure_detected = bool(heading_pattern.search(markdown))

        # Math detection: pymupdf4llm doesn't preserve LaTeX well, but we can
        # detect common math indicators (equations, formulas)
        # Note: This is a basic heuristic; real math preservation would need different tools
        # Look for LaTeX syntax, Unicode math symbols, or common patterns
        math_indicators = re.compile(
            r"(\$.*?\$|\\[a-zA-Z]+|[∫∑∏∂√π≈≠≤≥±×÷·²³⁴⁰¹]|"
            r"equation|formula|theorem|proof)",
            re.IGNORECASE,
        )
        flags.has_math = bool(math_indicators.search(markdown))
        # pymupdf4llm doesn't preserve LaTeX, so math_preserved stays False

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
