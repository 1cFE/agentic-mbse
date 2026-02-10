"""Core data model types for document ingestion."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    pass

# Source format types
SourceFormat = Literal["jats_xml", "arxiv_html", "publisher_html", "pdf", "docx"]

# Failure categories for conversion errors (spec 006)
FailureCategory = Literal[
    "needs_ocr",
    "table_corruption",
    "no_source_found",
    "source_validation_failed",
    "conversion_timeout",
    "unsupported_format",
    "api_error",
    "network_error",
    "unknown",
]

# Quality tier mapping (lower number = better quality)
QUALITY_TIERS: dict[SourceFormat, int] = {
    "jats_xml": 1,  # Structured XML, semantic tags, tables preserved
    "arxiv_html": 2,  # HTML5 with MathML, clean structure
    "publisher_html": 3,  # Varies by publisher, often good tables
    "pdf": 4,  # Visual rendering, table/heading detection fragile
    "docx": 5,  # Legacy, rare in academic corpus
}


@dataclass
class QualityFlags:
    """Quality indicators for document extraction.

    Converters populate these flags to report extraction quality characteristics
    such as table preservation, math rendering, and structure detection.

    All fields default to False to ensure consistent JSON serialization (all keys
    present even when features are absent).
    """

    has_tables: bool = False
    tables_likely_corrupted: bool = False
    has_math: bool = False
    math_preserved: bool = False
    has_figures: bool = False
    figure_captions_present: bool = False
    heading_structure_detected: bool = False


@dataclass
class DocumentIdentifiers:
    """Unique identifier for a document across multiple identifier types.

    At least one identifier must be present. Priority order for determining
    the primary identifier: doi > arxiv_id > pmc_id > local_path.

    The zotero_key is for user reference only and does not participate in
    priority ordering or cache keying.
    """

    doi: str | None = None
    arxiv_id: str | None = None
    pmc_id: str | None = None
    local_path: str | None = None
    zotero_key: str | None = None

    def __post_init__(self) -> None:
        """Validate that at least one identifier is present."""
        if not any([self.doi, self.arxiv_id, self.pmc_id, self.local_path]):
            raise ValueError("At least one identifier required")

    def primary_identifier(self) -> tuple[str, str]:
        """Returns (type, value) for highest-priority identifier.

        Priority order: doi > arxiv_id > pmc_id > local_path.
        Zotero key is excluded from priority ordering.

        Returns:
            Tuple of (identifier_type, identifier_value)
            where identifier_type is one of: "doi", "arxiv", "pmc", "local"

        Raises:
            ValueError: If no identifiers are present (should not happen
                       after __post_init__ validation)
        """
        if self.doi:
            return ("doi", self.doi)
        if self.arxiv_id:
            return ("arxiv", self.arxiv_id)
        if self.pmc_id:
            return ("pmc", self.pmc_id)
        if self.local_path:
            return ("local", self.local_path)
        raise ValueError("At least one identifier required")

    def display_key(self) -> str:
        """Returns 'type:value' for reports and logs.

        Uses the primary identifier to generate a human-readable key.

        Returns:
            String in format "type:value", e.g., "doi:10.1103/PhysRevLett.116.061102"
        """
        id_type, id_value = self.primary_identifier()
        return f"{id_type}:{id_value}"


@dataclass(order=True)
class SourceCandidate:
    """A candidate source for document extraction.

    Represents a discovered source with format type, location, quality ranking,
    and discovery provenance. Sources are sortable by quality tier for deterministic
    prioritization (lower tier = better quality).

    Exactly one of url or local_path must be present (mutually exclusive).
    """

    # Primary sort key (lower = better quality)
    quality_tier: int

    # Secondary sort key for deterministic ordering within same tier
    # Using url if present, else local_path
    _sort_key: str = ""

    # Source identification
    format: SourceFormat = "pdf"
    url: str | None = None
    local_path: str | None = None
    discovered_via: str = "unknown"

    # Optional metadata from discovery
    http_content_type: str | None = None
    publisher: str | None = None
    license: str | None = None

    def __post_init__(self) -> None:
        """Validate location and set sort key."""
        # Validate exactly one of url or local_path
        if self.url is None and self.local_path is None:
            raise ValueError("Either url or local_path must be provided")
        if self.url is not None and self.local_path is not None:
            raise ValueError("url and local_path are mutually exclusive")

        # Set sort key for secondary sorting (url preferred, fallback to local_path)
        self._sort_key = self.url if self.url is not None else (self.local_path or "")


@dataclass
class ValidationResult:
    """Validation result for source content checks.

    Provides structured validation outcomes from converter `validate_source()` calls,
    including content length, format detection, paywall detection, and truncation checks.

    Used by converters to report validation failures with specific reasons (e.g.,
    paywall detected, content truncated) before attempting conversion.

    Spec 010: ValidationResult enables structured outcome classification and supports
    provenance tracking of validation failures.

    Attributes:
        is_valid: Whether the source passed validation checks
        content_length: Size of the content in bytes
        has_body_content: Whether body/article content is present (format-specific)
        detected_content_type: MIME type or format detected during validation
        is_paywall: Whether a paywall marker was detected
        is_truncated: Whether the content appears truncated (e.g., < 1KB for expected full document)
    """

    is_valid: bool
    content_length: int
    has_body_content: bool | None = None
    detected_content_type: str | None = None
    is_paywall: bool | None = None
    is_truncated: bool | None = None


@dataclass
class ConversionResult:
    """Output of a successful document conversion.

    Encapsulates the extracted markdown text, non-fatal warnings (e.g., "table possibly
    malformed"), quality flags indicating extraction characteristics, and the name of
    the converter that produced the result.

    All converters must return a ConversionResult on success, providing provenance
    and quality metadata for downstream processing.
    """

    markdown: str
    warnings: list[str]
    quality_flags: QualityFlags
    converter_name: str


class ConversionError(Exception):
    """Typed exception for converter failures with structured failure categories.

    Raised by converters to signal conversion failures with explicit categorization,
    enabling outcome classification without string parsing. Supports optional structured
    details for converter-specific metadata.

    Spec 017: ConversionError provides typed failure categories to the orchestrator
    for proper outcome classification and provenance tracking.

    Attributes:
        category: The failure category (e.g., "needs_ocr", "unsupported_format")
        details: Optional dict of converter-specific metadata (e.g., {"pages": 0})

    Examples:
        >>> raise ConversionError(
        ...     "No text detected in PDF",
        ...     category="needs_ocr",
        ...     details={"pages": 120}
        ... )
        >>> try:
        ...     convert_document()
        ... except Exception as e:
        ...     raise ConversionError(
        ...         f"Unexpected failure: {e}",
        ...         category="unknown"
        ...     ) from e
    """

    def __init__(
        self,
        message: str,
        category: FailureCategory,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ConversionError with message, category, and optional details.

        Args:
            message: Human-readable error message for logging
            category: Typed failure category from FailureCategory literal
            details: Optional dict of converter-specific metadata
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}

    def __repr__(self) -> str:
        """Return detailed representation including category and details."""
        details_str = f", details={self.details}" if self.details else ""
        return f"ConversionError(category={self.category!r}{details_str}, message={str(self)!r})"


# Document outcome types (from spec 006)
DocumentOutcome = Literal["success", "partial", "failed"]


@dataclass
class ProvenanceRecord:
    """Complete provenance record for a document extraction.

    Captures the complete decision trail: what sources were discovered, what was
    attempted, what worked, what failed and why. Enables debugging, triage reporting,
    and resumability.

    Spec 009: ProvenanceRecord structure supports atomic persistence, UTF-8 encoding,
    and structured metadata for triage analysis.

    Attributes:
        document_id: Document identifiers (DOI, arXiv ID, etc.)
        discovered_sources: List of SourceCandidate found during discovery
        discovery_errors: API failures or timeout messages from discovery phase
        discovery_cached: Whether discovery result came from cache
        attempts: List of ExtractionAttempt records (one per source tried)
        outcome: Final document extraction result
        final_converter: Name of converter that produced output (if success/partial)
        failure_category: Typed category if extraction failed
        created_at: ISO 8601 timestamp of extraction
        pipeline_version: Version of agentic-mbse pipeline
        total_elapsed_seconds: Total time for extraction (discovery + all attempts)
    """

    document_id: "DocumentIdentifiers"
    discovered_sources: list["SourceCandidate"]
    discovery_errors: list[str]
    discovery_cached: bool
    attempts: list[Any]  # List of ExtractionAttempt, but avoid circular import
    outcome: DocumentOutcome
    final_converter: str | None
    failure_category: FailureCategory | None
    created_at: str  # ISO 8601 timestamp
    pipeline_version: str
    total_elapsed_seconds: float
