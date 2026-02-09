
## Purpose
Extract markdown from HTML sources (arXiv HTML, publisher HTML) with format-specific validation including paywall detection, quality flag reporting for table/math preservation, and typed error categorization.

## Requirements
- Implement two HTML converters: `ArXivHTMLConverter` and `PublisherHTMLConverter`
- Validate HTML for body content presence and paywall markers
- Convert HTML to markdown (arXiv: preserve MathML; publisher: BeautifulSoup-based)
- Report quality flags: table preservation, math preservation, figure captions
- Raise typed `ConversionError` for unsupported HTML structures
- Handle encoding issues gracefully (UTF-8 with fallback)

## Acceptance Criteria
- **Given** arXiv HTML with MathML, **when** converted, **then** `quality_flags.has_math=True` and `quality_flags.math_preserved=True`
- **Given** publisher HTML with paywall marker, **when** validated, **then** return `ValidationResult(is_valid=False, is_paywall=True)`
- **Given** HTML with body content, **when** validated, **then** return `ValidationResult(is_valid=True, has_body_content=True)`
- **Given** truncated HTML (< 1KB), **when** validated, **then** return `ValidationResult(is_valid=False, is_truncated=True)`
- **Given** arXiv HTML, **when** converted, **then** `converter_name="ArXivHTMLConverter"`
- **Given** publisher HTML with tables, **when** converted, **then** `quality_flags.has_tables=True`

## Interfaces
**Converter Implementations:**
```python
class ArXivHTMLConverter(Converter):
    name = "ArXivHTMLConverter"
    
    def can_convert(self, source: SourceCandidate) -> bool:
        return source.format == "arxiv_html"
    
    def validate_source(self, content: bytes) -> ValidationResult:
        # Check for body content
    
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        # Extract with MathML preservation

class PublisherHTMLConverter(Converter):
    name = "PublisherHTMLConverter"
    PAYWALL_MARKERS = ["login required", "access denied", ...]
    
    def can_convert(self, source: SourceCandidate) -> bool:
        return source.format == "publisher_html"
    
    def validate_source(self, content: bytes) -> ValidationResult:
        # Check for paywall markers
    
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        # Extract with BeautifulSoup

