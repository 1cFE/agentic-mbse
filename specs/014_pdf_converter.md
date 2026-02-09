
## Purpose
Extract markdown from PDF documents using pymupdf4llm, with validation for scanned PDFs, quality flag reporting for table/math preservation, and typed error categorization.

## Requirements
- Implement `Converter` interface with `can_convert()`, `validate_source()`, `convert()`, and `name` property
- Validate PDF content for extractable text (detect scanned PDFs)
- Convert PDF to markdown using pymupdf4llm
- Report quality flags: table detection, table corruption likelihood, heading structure
- Raise typed `ConversionError` with category "needs_ocr" for scanned PDFs
- Raise typed `ConversionError` with category "table_corruption" when tables are garbled
- Handle large PDFs with memory efficiency

## Acceptance Criteria
- **Given** PDF with extractable text, **when** validated, **then** return `ValidationResult(is_valid=True)`
- **Given** scanned PDF with no text, **when** validated, **then** return `ValidationResult(is_valid=False, has_body_content=False)`
- **Given** scanned PDF, **when** converted, **then** raise `ConversionError(category="needs_ocr")`
- **Given** PDF with tables, **when** converted successfully, **then** `quality_flags.has_tables=True`
- **Given** PDF with garbled tables, **when** converted, **then** `quality_flags.tables_likely_corrupted=True` or raise `ConversionError(category="table_corruption")`
- **Given** PDF with headings, **when** converted, **then** `quality_flags.heading_structure_detected=True`
- **Given** PDF conversion, **when** result returned, **then** `converter_name="PyMuPDF4LLMConverter"`

## Interfaces
**Converter Implementation:**
```python
class PyMuPDF4LLMConverter(Converter):
    @property
    def name(self) -> str:
        return "PyMuPDF4LLMConverter"
    
    def can_convert(self, source: SourceCandidate) -> bool:
        return source.format == "pdf"
    
    def validate_source(self, content: bytes) -> ValidationResult:
        # Check if PDF has extractable text
    
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        # Extract using pymupdf4llm, populate quality flags

