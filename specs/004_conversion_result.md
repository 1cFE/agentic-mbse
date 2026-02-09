
## Purpose
Encapsulate the output of a successful document conversion, including markdown text, non-fatal warnings, quality flags, and the name of the converter that produced it.

## Requirements
- Store extracted markdown text
- Store list of non-fatal warnings (e.g., "table possibly malformed")
- Include quality flags structure (from `002_quality_flags.md`)
- Record converter name for provenance (e.g., "JATSPandocConverter")
- Be returned by all successful converter invocations

## Acceptance Criteria
- **Given** a successful JATS conversion with a table warning, **when** result is created, **then** `markdown` contains extracted text, `warnings=["Table 2 missing column headers"]`, `converter_name="JATSPandocConverter"`
- **Given** a PDF conversion with no warnings, **when** result is created, **then** `warnings=[]` (empty list, not None)
- **Given** any conversion result, **when** serialized to JSON, **then** `quality_flags` is a nested object with all boolean fields
- **Given** a converter that produces a result, **when** `converter_name` is missing, **then** provenance record cannot be created (converter name is required)

## Interfaces
**Data Structure:**
```python
@dataclass
class ConversionResult:
    markdown: str
    warnings: list[str]
    quality_flags: QualityFlags  # From 002_quality_flags.md
    converter_name: str

