
## Purpose
Coordinate document extraction by orchestrating source discovery, extraction attempts, outcome classification, and provenance recording, with support for resumability and format overrides.

## Requirements
- Check for existing provenance and skip if `outcome="success"` (resumability)
- Retry failed/partial documents when re-run
- Call `SourceDiscoverer` to get candidate sources
- Call `ExtractionOrchestrator` to attempt extraction from sources in priority order
- Call `OutcomeClassifier` to determine final outcome and failure category
- Write provenance record via try/finally (crash-safe)
- Support `--format` override to skip discovery and force specific format
- Return extraction result with markdown and provenance

## Acceptance Criteria
- **Given** existing provenance with `outcome="success"`, **when** extract is called, **then** skip extraction and return cached result
- **Given** existing provenance with `outcome="failed"`, **when** extract is called, **then** retry extraction and update provenance
- **Given** `format_override="pdf"`, **when** extract is called, **then** skip discovery and only attempt PDF extraction
- **Given** extraction crashes after discovery, **when** finally block executes, **then** provenance.json is written with `outcome="failed"` and partial attempts
- **Given** successful extraction, **when** extract completes, **then** return `ExtractionResult` with markdown and provenance
- **Given** all sources fail, **when** extract completes, **then** provenance records all attempts and final failure category

## Interfaces
**API:**
```python
@dataclass
class ExtractionResult:
    markdown: str | None
    provenance: ProvenanceRecord

class SourceRouter:
    def __init__(
        self,
        discoverer: SourceDiscoverer,
        orchestrator: ExtractionOrchestrator,
        classifier: OutcomeClassifier,
        provenance_manager: ProvenanceManager,
    ):
        """Inject dependencies for testability."""
    
    def extract(
        self,
        identifiers: DocumentIdentifiers,
        output_dir: Path,
        format_override: str | None = None,
    ) -> ExtractionResult:
        """Coordinate extraction, return result with provenance."""

