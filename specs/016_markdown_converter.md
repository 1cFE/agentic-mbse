
## Purpose
Extract markdown from structured document formats (JATS XML, DOCX) using pandoc, with format-specific validation, quality flag reporting for semantic structure preservation, and typed error categorization.

## Requirements
- Implement two converters: `JATSPandocConverter` and `DOCXPandocConverter`
- Validate JATS XML for article/body tags
- Validate DOCX for binary format integrity
- Convert to markdown via pandoc with format-specific options
- Report quality flags: table preservation, figure captions, heading structure
- Raise typed `ConversionError` for pandoc failures
- Handle pandoc stderr output as warnings

## Acceptance Criteria
- **Given** JATS XML with article tag, **when** validated, **then** return `ValidationResult(is_valid=True, has_body_content=True)`
- **Given** JATS XML missing body, **when** validated, **then** return `ValidationResult(is_valid=False, has_body_content=False)`
- **Given** valid JATS XML, **when** converted, **then** `quality_flags.heading_structure_detected=True`
- **Given** DOCX file, **when** converted, **then** use `pandoc -f docx -t markdown`
- **Given** pandoc fails with exit code 1, **when** converted, **then** raise `ConversionError(category="unsupported_format")`
- **Given** pandoc stderr output, **when** conversion succeeds, **then** include stderr in warnings
- **Given** JATS conversion, **when** result returned, **then** `converter_name="JATSPandocConverter"`

## Interfaces
**Converter Implementations:**
```python
class JATSPandocConverter(Converter):
    name = "JATSPandocConverter"
    
    def can_convert(self, source: SourceCandidate) -> bool:
        return source.format == "jats_xml"
    
    def validate_source(self, content: bytes) -> ValidationResult:
        # Check for XML article/body tags
    
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        # Convert via pandoc -f jats -t markdown

class DOCXPandocConverter(Converter):
    name = "DOCXPandocConverter"
    
    def can_convert(self, source: SourceCandidate) -> bool:
        return source.format == "docx"
    
    def validate_source(self, content: bytes) -> ValidationResult:
        # Check for DOCX magic bytes (ZIP header)
    
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        # Convert via pandoc -f docx -t markdown

