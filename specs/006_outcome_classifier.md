
## Purpose
Determine the final document extraction outcome (success, partial, failed) and assign a typed failure category based on extraction attempts and discovery errors.

## Requirements
- Classify outcome as "success", "partial", or "failed"
- Assign typed failure category from extraction attempts (not by parsing error strings)
- Use typed `failure_category` from `ConversionError` raised by converters
- Fallback to heuristic categorization for discovery-level failures
- Prioritize the most recent non-"unknown" failure category when multiple failures exist
- Handle edge cases: no attempts, no sources discovered, all validation failures

## Acceptance Criteria
- **Given** at least one attempt with `outcome="success"`, **when** classified, **then** return `("success", None)`
- **Given** all attempts failed and most recent has `failure_category="needs_ocr"`, **when** classified, **then** return `("failed", "needs_ocr")`
- **Given** no attempts and no discovery errors, **when** classified, **then** return `("failed", "no_source_found")`
- **Given** no attempts and discovery_errors is non-empty, **when** classified, **then** return `("failed", "api_error")`
- **Given** all attempts have `outcome="validation_failed"` and at least one has `is_paywall=True`, **when** classified, **then** return `("failed", "source_validation_failed")`
- **Given** all attempts have `outcome="fetch_failed"`, **when** classified, **then** return `("failed", "network_error")`
- **Given** all attempts have `outcome="timeout"`, **when** classified, **then** return `("failed", "conversion_timeout")`
- **Given** all attempts have `failure_category="unknown"`, **when** classified, **then** return `("failed", "unknown")`

## Interfaces
**API:**
```python
type DocumentOutcome = Literal["success", "partial", "failed"]
type FailureCategory = Literal[
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

class OutcomeClassifier:
    def classify(
        self,
        attempts: list[ExtractionAttempt],
        discovery_errors: list[str],
    ) -> tuple[DocumentOutcome, FailureCategory | None]:
        """Determine outcome and failure category. Returns (outcome, category_or_None)."""

