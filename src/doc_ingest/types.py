"""Core data model types for document ingestion."""

from dataclasses import dataclass


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
