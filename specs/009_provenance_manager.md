
## Purpose
Persist and load provenance records for documents, supporting crash-safe writes and enabling triage report generation.

## Requirements
- Write provenance records to JSON files (one per document)
- Store in `output_dir/{document_hash}/provenance.json`
- Load existing provenance records by document hash
- Support atomic writes to prevent corruption
- Include pipeline version and timestamps in records

## Acceptance Criteria
- **Given** a provenance record, **when** written, **then** file exists at `output_dir/{hash}/provenance.json`
- **Given** a corrupted write (process killed mid-write), **when** write uses atomic temp-file strategy, **then** either old file intact or new file complete (no partial JSON)
- **Given** an existing provenance file, **when** loaded, **then** return `ProvenanceRecord` instance
- **Given** a missing provenance file, **when** loaded, **then** return None
- **Given** a provenance record with Unicode in identifiers, **when** serialized, **then** UTF-8 encoding preserved

## Interfaces
**API:**
```python
class ProvenanceManager:
    def write(self, output_dir: Path, record: ProvenanceRecord) -> None:
        """Write provenance.json for document (atomic write via temp file)."""
    
    def load(self, output_dir: Path, document_hash: str) -> ProvenanceRecord | None:
        """Load existing provenance record, or None if not found."""

