"""Base converter interface for document format converters.

Defines the Converter protocol that all format-specific converters must implement.
Each converter is responsible for validating source content and converting it to markdown.
"""

from typing import Protocol

from doc_ingest.types import ConversionResult, SourceFormat, ValidationResult


class Converter(Protocol):
    """Protocol defining the converter interface.

    All format-specific converters (PDF, HTML, JATS, DOCX) must implement these methods
    to enable polymorphic handling by the ConverterRegistry and ExtractionOrchestrator.

    The converter lifecycle:
    1. can_convert(format) - Check if this converter handles the given format
    2. validate_source(content) - Verify content is valid and convertible
    3. convert(content) - Perform the actual conversion to markdown

    Converters should raise ConversionError for conversion failures with typed
    failure categories (e.g., "needs_ocr", "unsupported_format").
    """

    @property
    def name(self) -> str:
        """Return the converter name for provenance tracking.

        Returns:
            Converter name (e.g., "PyMuPDF4LLMConverter", "ArXivHTMLConverter")
        """
        ...

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter can handle the given source format.

        Args:
            format: Source format type (e.g., "pdf", "jats_xml", "arxiv_html")

        Returns:
            True if this converter supports the format, False otherwise
        """
        ...

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate source content before conversion.

        Checks if the content is valid, complete, and convertible. Detects issues
        like paywalls, truncation, missing body content, or scanned PDFs.

        Args:
            content: Raw content bytes to validate

        Returns:
            ValidationResult with is_valid flag and diagnostic details

        Examples:
            >>> result = converter.validate_source(pdf_bytes)
            >>> if not result.is_valid:
            ...     print(f"Validation failed: paywall={result.is_paywall}")
        """
        ...

    def convert(self, content: bytes) -> ConversionResult:
        """Convert source content to markdown.

        Performs the actual conversion, returning markdown text with quality flags
        and warnings. Should raise ConversionError for failures.

        Args:
            content: Raw content bytes to convert

        Returns:
            ConversionResult with markdown, warnings, and quality flags

        Raises:
            ConversionError: Conversion failed with typed failure category

        Examples:
            >>> result = converter.convert(pdf_bytes)
            >>> print(result.markdown)
            >>> if result.quality_flags.tables_likely_corrupted:
            ...     print("Warning: tables may be corrupted")
        """
        ...
