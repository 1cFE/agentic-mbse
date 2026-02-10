"""Converter registry for format-to-converter mapping.

Provides a registry that maps source formats to their corresponding converter
implementations, enabling the ExtractionOrchestrator to select the appropriate
converter for each source candidate.
"""

from doc_ingest.converters.base import Converter
from doc_ingest.types import SourceFormat


class ConverterRegistry:
    """Registry mapping source formats to converter instances.

    Maintains a dictionary of format -> converter mappings, allowing the
    ExtractionOrchestrator to look up the appropriate converter for each
    source candidate's format.

    Example:
        >>> registry = ConverterRegistry()
        >>> registry.register("pdf", PyMuPDF4LLMConverter())
        >>> registry.register("jats_xml", JATSPandocConverter())
        >>> converter = registry.get("pdf")
        >>> result = converter.convert(pdf_bytes)
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._converters: dict[SourceFormat, Converter] = {}

    def register(self, format: SourceFormat, converter: Converter) -> None:
        """Register a converter for a source format.

        Args:
            format: Source format type (e.g., "pdf", "jats_xml")
            converter: Converter instance to handle this format

        Example:
            >>> registry.register("pdf", PyMuPDF4LLMConverter())
        """
        self._converters[format] = converter

    def get(self, format: SourceFormat) -> Converter | None:
        """Get the converter for a source format.

        Args:
            format: Source format type to look up

        Returns:
            Converter instance if registered, None otherwise

        Example:
            >>> converter = registry.get("pdf")
            >>> if converter is None:
            ...     print("No converter registered for PDF")
        """
        return self._converters.get(format)

    def has_converter(self, format: SourceFormat) -> bool:
        """Check if a converter is registered for the given format.

        Args:
            format: Source format type to check

        Returns:
            True if a converter is registered, False otherwise

        Example:
            >>> if registry.has_converter("pdf"):
            ...     print("PDF converter available")
        """
        return format in self._converters
