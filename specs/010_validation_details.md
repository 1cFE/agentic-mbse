
## Purpose
Provide a typed structure for converters to report source validation results, including content length, format detection, paywall detection, and truncation detection.

## Requirements
- Store validation outcome (is_valid boolean)
- Store content length for size analysis
- Optionally store format-specific checks: body content presence, detected content type, paywall status, truncation status
- Be returned by all converter `validate_source()` calls
- Support structured analysis in outcome classification

## Acceptance Criteria
- **Given** valid JATS XML with body content, **when** validated, **then** `is_valid=True`, `has_body_content=True`
- **Given** HTML with paywall marker, **when** validated, **then** `is_valid=False`, `is_paywall=True`
- **Given** truncated response (< 1KB), **when** validated, **then** `is_valid=False`, `is_truncated=True`, `content_length < 1024`
- **Given** valid PDF, **when** validated, **then** `is_valid=True`, `content_length > 0`, optional fields may be None
- **Given** validation result, **when** serialized to provenance, **then** all set fields are preserved

## Interfaces
**Data Structure:**
```python
@dataclass
class ValidationResult:
    is_valid: bool
    content_length: int
    has_body_content: bool | None = None
    detected_content_type: str | None = None
    is_paywall: bool | None = None
    is_truncated: bool | None = None

