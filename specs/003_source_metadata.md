
## Purpose
Represent a candidate source for document extraction with format type, location (URL or local path), quality tier ranking, discovery provenance, and optional metadata like HTTP content type and publisher.

## Requirements
- Store source format (e.g., "jats_xml", "arxiv_html", "pdf")
- Store location as either URL or local path (mutually exclusive)
- Assign quality tier ranking (1=best, 5=worst) based on format
- Record discovery method (e.g., "openalex_api", "local_file")
- Optionally store HTTP content type, publisher, license from discovery metadata
- Be sortable by quality tier for deterministic source prioritization

## Acceptance Criteria
- **Given** a JATS XML source from OpenAlex, **when** created, **then** `format="jats_xml"`, `quality_tier=1`, `discovered_via="openalex_api"`
- **Given** a PDF source from arXiv, **when** created, **then** `format="pdf"`, `quality_tier=4`, `discovered_via="arxiv_api"`
- **Given** a local PDF file, **when** created, **then** `local_path="/path/to/file.pdf"`, `url=None`, `discovered_via="local_file"`
- **Given** two sources with the same quality tier, **when** sorted, **then** secondary sort is by URL (lexicographic) or local_path if URL is None
- **Given** a source with `http_content_type="application/pdf"`, **when** serialized, **then** the field is preserved

## Interfaces
**Data Structure:**
```python
@dataclass
class SourceCandidate:
    format: str  # SourceFormat literal: "jats_xml" | "arxiv_html" | "publisher_html" | "pdf" | "docx"
    url: str | None
    local_path: str | None
    quality_tier: int
    discovered_via: str
    http_content_type: str | None = None
    publisher: str | None = None
    license: str | None = None

