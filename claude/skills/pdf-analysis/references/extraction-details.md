# PDF Extraction — Detailed Reference

## Backend Comparison

| Backend | Strengths | Weaknesses | Best For |
|---------|-----------|------------|----------|
| pymupdf4llm | Fast, no external deps, good text fidelity | Tables rendered as pseudo-text, no OCR | Text-heavy pages, quick extraction |
| Docling MCP | Excellent table structure, layout analysis | Slow, memory-heavy (8GB VM limit), single-page only | Pages with tables, complex layouts |
| Image + vision | Works on any page, handles diagrams/figures | Lossy, requires visual reconstruction | Diagrams, figures, scanned pages |

## pymupdf4llm Details

pymupdf4llm converts PDF pages to markdown using PyMuPDF's text extraction with layout awareness.

### Common Issues

- **Merged columns**: Multi-column layouts may interleave. Check output for coherence.
- **Table garbling**: Tables often appear as aligned text without structure. If table structure matters, escalate to Docling.
- **Headers/footers**: Page headers and footers are included in output. Strip them manually if needed.
- **Math notation**: LaTeX/MathML is not preserved. Complex equations may need image fallback.

### Checking Quality

After pymupdf4llm extraction, verify:
1. Text reads coherently (no column interleaving)
2. Tables are recognizable (even if not perfectly structured)
3. Key data points are present and correct
4. Section headings are preserved

If any check fails, escalate to the next backend in the fallback chain.

<!-- DOCLING_START -->
## Docling MCP Details

The Docling MCP server provides high-fidelity document conversion with table structure preservation.

### Memory Constraints

The Docling MCP server runs on an 8GB VM. Multi-page PDFs will cause out-of-memory errors or extreme slowness.

**Mandatory workflow:**
1. Extract the target page as a single-page PDF using pymupdf
2. Send only the single-page PDF to Docling
3. Never send the original multi-page document

### Single-Page Extraction

```python
import pymupdf

doc = pymupdf.open("paper.pdf")
single = pymupdf.open()
single.insert_pdf(doc, from_page=N, to_page=N)
single.save("/tmp/page_N.pdf")
single.close()
doc.close()
```

Or use the bundled script:
```bash
uv run python .claude/skills/pdf-analysis/scripts/extract_page.py paper.pdf N --mode pdf --output /tmp/page_N.pdf
```

### Docling MCP Invocation

After extracting the single-page PDF, use the Docling MCP tools in sequence:

1. **Convert**: `mcp__docling__convert_document_into_docling_document` with source `/tmp/page_N.pdf`
   - Returns a `document_key`
2. **Export**: `mcp__docling__export_docling_document_to_markdown` with the document key
   - Returns structured markdown with table formatting

### Docling Timeout Handling

If Docling does not respond within ~30 seconds or returns an error:
1. Do not retry the same page — fall back to image mode
2. Note the failure for the user
3. Render the page as PNG and use visual analysis

<!-- DOCLING_END -->

## Image Fallback Details

### Rendering Parameters

```python
import pymupdf

doc = pymupdf.open("paper.pdf")
page = doc[N]
pix = page.get_pixmap(matrix=pymupdf.Matrix(200/72, 200/72))  # 200 DPI
pix.save("/tmp/page_N.png")
doc.close()
```

- **200 DPI**: Good balance of quality and file size for most documents
- **300 DPI**: Use for small text or detailed figures (`--dpi 300`)
- **150 DPI**: Acceptable for large text, reduces file size

### Visual Reconstruction

When analyzing a page image, reconstruct the content as markdown:
- Identify section headings by font size and weight
- Reconstruct tables using column/row alignment
- Describe figures and diagrams in detail
- Preserve numerical values exactly as shown
- Note any text that is unclear or ambiguous

## Multi-Page Workflows

When extracting content spanning multiple pages:

1. Start with `--info` to get the page count
2. Extract pages sequentially, starting with pymupdf4llm
3. Only escalate individual pages that need better extraction
4. Combine results in order, noting page boundaries

### Batch Extraction Pattern

```bash
# Get page count
uv run python .claude/skills/pdf-analysis/scripts/extract_page.py document.pdf --info

# Extract specific pages
for page in 0 1 2 3; do
    uv run python .claude/skills/pdf-analysis/scripts/extract_page.py document.pdf $page --mode markdown
done
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| pymupdf4llm import error | `uv pip install pymupdf4llm` |
| Docling MCP not responding | Fall back to image mode; check if MCP server is running |
| Garbled table output | Escalate from pymupdf4llm to Docling |
| Scanned PDF (no text layer) | Use image mode directly |
| Large PDF causes OOM | Never send full PDF to Docling; use single-page extraction |
| Math/equations lost | Use image fallback for equation-heavy pages |
