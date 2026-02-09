
## Purpose
Execute the extraction loop by iterating source candidates in quality order, fetching content, validating via converter, attempting conversion, and recording all attempts with outcomes.

## Requirements
- Iterate sources in order (sorted by quality tier)
- For each source: fetch content, validate, convert
- On fetch failure: record attempt with `outcome="fetch_failed"`, continue to next source
- On validation failure: record attempt with `outcome="validation_failed"`, continue
- On conversion success: record attempt with `outcome="success"`, stop iteration
- On conversion error: record attempt with typed `failure_category`, continue
- Return all attempts and successful result (if any)

## Acceptance Criteria
- **Given** 3 sources (JATS, arXiv HTML, PDF), **when** JATS succeeds, **then** return 1 attempt with `outcome="success"`, do not attempt remaining sources
- **Given** 3 sources where first two fail validation, **when** PDF succeeds, **then** return 3 attempts (2 validation_failed, 1 success)
- **Given** all sources fail, **when** orchestration completes, **then** return all attempts with no successful result
- **Given** fetch raises `FetchError`, **when** recorded, **then** attempt has `outcome="fetch_failed"`
- **Given** converter raises `ConversionError(category="needs_ocr")`, **when** recorded, **then** attempt has `failure_category="needs_ocr"`
- **Given** converter raises unexpected exception, **when** recorded, **then** attempt has `failure_category="unknown"`

## Interfaces
**API:**
```python
class ExtractionOrchestrator:
    def __init__(self, registry: ConverterRegistry):
        """Inject converter registry."""
    
    def orchestrate(
        self,
        sources: list[SourceCandidate],
        fetch_fn: Callable[[SourceCandidate], bytes],
    ) -> tuple[list[ExtractionAttempt], ConversionResult | None]:
        """Execute extraction loop. Returns (all_attempts, result_or_None)."""

