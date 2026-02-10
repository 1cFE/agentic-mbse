# Goals — Document Ingestion Quality

## Table Extraction
- Tables in academic papers should extract with correct row/column structure
- Multi-page tables should be detected and merged where possible
- Table captions should be preserved and associated with their tables
- Complex layouts (merged cells, nested headers) should degrade gracefully

## Heading Detection
- Section headings should be detected accurately across different formatting styles
- Numbered headings (1.1, 1.2.3) should preserve hierarchy
- Unnumbered headings (bold, all-caps, underlined) should be promoted to proper markdown headings
- Table of contents entries should NOT be promoted to headings

## Multi-Format Support
- PDF extraction should work reliably across different academic paper layouts
- The extraction pipeline should handle single-column and two-column layouts
- Papers with heavy mathematical notation should not break the pipeline

## Character Fidelity
- Extracted text should preserve the original content with minimal loss
- Ligatures (fi, fl, ff, etc.) should be resolved to their component characters
- Unicode characters should be preserved, not replaced with placeholders

## Regression Safety
- No change should regress existing corpus metrics below established thresholds
- All corpus tests must pass after every change
- Per-paper heading thresholds accommodate known limitations of text-based detection
