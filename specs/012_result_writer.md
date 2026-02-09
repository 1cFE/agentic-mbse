
## Purpose
Write extraction outputs to the file system, including markdown content, legacy summary.json, and provenance records, with deterministic directory naming based on document hash.

## Requirements
- Write `output.md` with extracted markdown
- Write `summary.json` with legacy extraction metadata (for backward compatibility)
- Delegate provenance writing to `ProvenanceManager`
- Compute deterministic document hash from primary identifier
- Create output directory structure: `output_dir/{document_hash}/`
- Handle write failures gracefully (don't corrupt existing files)

## Acceptance Criteria
- **Given** successful extraction, **when** written, **then** `output_dir/{hash}/output.md` contains markdown
- **Given** successful extraction, **when** written, **then** `output_dir/{hash}/summary.json` exists with hash, source path, quality flags
- **Given** extraction with warnings, **when** summary.json is written, **then** warnings are included in summary
- **Given** failed extraction, **when** result writer is called, **then** only provenance.json is written (no output.md)
- **Given** document hash "abc123", **when** written twice with same content, **then** second write is idempotent (no change)

## Interfaces
**API:**
```python
class ResultWriter:
    def __init__(self, provenance_manager: ProvenanceManager):
        """Inject provenance manager for delegation."""
    
    def write(
        self,
        output_dir: Path,
        result: ExtractionResult,
    ) -> None:
        """Write output.md, summary.json, and delegate provenance writing."""

