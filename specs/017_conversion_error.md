
## Purpose
Provide a typed exception for converters to raise with structured failure categories and details, enabling outcome classification without string parsing.

## Requirements
- Subclass Python `Exception`
- Store failure category as typed field (not inferred from message)
- Store optional structured details dict for converter-specific metadata
- Support standard exception message for logging
- Be raised by all converters on conversion failure

## Acceptance Criteria
- **Given** PDF converter detects no text, **when** error raised, **then** `category="needs_ocr"`
- **Given** HTML converter detects paywall, **when** error raised, **then** `category="source_validation_failed"` (or validation returns is_valid=False, no exception)
- **Given** pandoc fails, **when** error raised, **then** `category="unsupported_format"`
- **Given** unexpected exception, **when** caught by orchestrator, **then** wrapped in `ConversionError(category="unknown")`
- **Given** conversion error, **when** logged, **then** message includes both human-readable text and category
- **Given** conversion error with details, **when** serialized to provenance, **then** details dict is preserved

## Interfaces
**Exception Class:**
```python
class ConversionError(Exception):
    def __init__(
        self,
        message: str,
        category: FailureCategory,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.category = category
        self.details = details or {}

