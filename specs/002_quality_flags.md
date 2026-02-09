
## Purpose
Provide a typed structure for converters to report extraction quality characteristics such as table preservation, math rendering, figure captions, and heading structure detection.

## Requirements
- Define boolean flags for common quality indicators: tables, math, figures, heading structure
- Include corruption/loss indicators (e.g., `tables_likely_corrupted`, `math_preserved`)
- Be populated by converters during extraction
- Be included in conversion results and provenance records
- Support future extension with additional flags

## Acceptance Criteria
- **Given** a JATS converter extracts a document with tables, **when** conversion completes, **then** `quality_flags.has_tables=True` and `quality_flags.tables_likely_corrupted=False`
- **Given** a PDF converter extracts a scanned document, **when** tables are garbled, **then** `quality_flags.has_tables=True` and `quality_flags.tables_likely_corrupted=True`
- **Given** an arXiv HTML converter extracts a math-heavy paper, **when** MathML is preserved, **then** `quality_flags.has_math=True` and `quality_flags.math_preserved=True`
- **Given** a converter that cannot detect figures, **when** conversion completes, **then** `quality_flags.has_figures=False` and `quality_flags.figure_captions_present=False`
- **Given** quality flags from any converter, **when** serialized to JSON, **then** all boolean fields are present (no missing keys)

## Interfaces
**Data Structure:**
```python
@dataclass
class QualityFlags:
    has_tables: bool = False
    tables_likely_corrupted: bool = False
    has_math: bool = False
    math_preserved: bool = False
    has_figures: bool = False
    figure_captions_present: bool = False
    heading_structure_detected: bool = False

