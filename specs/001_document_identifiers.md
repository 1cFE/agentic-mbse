
## Purpose
Provide a unified identification scheme for documents across multiple identifier types (DOI, arXiv ID, PMC ID, local paths, Zotero keys) with deterministic priority ordering.

## Requirements
- Support at least one identifier from: DOI, arXiv ID, PMC ID, local file path, Zotero key
- Determine a primary identifier using a fixed priority order (doi > arxiv_id > pmc_id > local_path)
- Generate a display-friendly key for reports and logs
- Validate that at least one identifier is present when created
- Provide stable cache keys based on primary identifier

## Acceptance Criteria
- **Given** a document with DOI "10.1103/PhysRevLett.116.061102" and arXiv ID "1602.03837", **when** `primary_identifier()` is called, **then** it returns `("doi", "10.1103/PhysRevLett.116.061102")`
- **Given** a document with only arXiv ID "1602.03837", **when** `primary_identifier()` is called, **then** it returns `("arxiv", "1602.03837")`
- **Given** a document with no identifiers, **when** constructed, **then** it raises `ValueError` with message "At least one identifier required"
- **Given** a document with DOI "10.1103/PhysRevLett.116.061102", **when** `display_key()` is called, **then** it returns `"doi:10.1103/PhysRevLett.116.061102"`
- **Given** two documents with the same primary identifier but different secondary identifiers, **when** cache keys are generated, **then** both map to the same cache entry

## Interfaces
**Data Structure:**
```python
@dataclass
class DocumentIdentifiers:
    doi: str | None = None
    arxiv_id: str | None = None
    pmc_id: str | None = None
    local_path: str | None = None
    zotero_key: str | None = None
    
    def primary_identifier(self) -> tuple[str, str]:
        """Returns (type, value) for highest-priority identifier."""
    
    def display_key(self) -> str:
        """Returns 'type:value' for reports."""

