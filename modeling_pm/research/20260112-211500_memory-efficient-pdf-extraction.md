---
date: 2026-01-12T21:15:00+00:00
researcher: Claude
topic: "Memory-efficient PDF extraction for large specifications"
tags: [research, tooling, pdf-extraction, docling, pymupdf]
status: complete
last_updated: 2026-01-12
---

# Research: Memory-Efficient PDF Extraction

**Date**: 2026-01-12T21:15:00+00:00
**Researcher**: Claude
**Research Type**: Tooling / Infrastructure

## Research Question

How can we extract the Part 1 SysML spec (5.4MB, ~300 pages) in a memory-efficient way when Docling is causing memory issues?

## Summary

- **Good news**: Part1 already extracted successfully using PyMuPDF fallback (47,797 lines, clean encoding)
- **Docling has known memory issues** with large documents (20GB+ for long docs per GitHub issues)
- **PyMuPDF4LLM** is the recommended alternative for memory-constrained environments
- **PDF splitting** (qpdf, pypdf) enables batch processing when tools can't handle full documents
- **Docling configuration** can reduce memory via `PyPdfiumDocumentBackend` and `page_range` batching

## Detailed Findings

### Current State

The Part1 spec extraction **completed successfully** with PyMuPDF:

```
/home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/
├── summary.json          # processor_used: "pymupdf", processing_completed: true
├── full_document.md      # 47,797 lines, 1.37MB, clean (0 garbled chars)
├── chunks/               # 118 chunks
└── images/               # 486 images
```

This suggests the m-scout processor automatically fell back to PyMuPDF when Docling failed.

### Docling Memory Issues

Docling has documented memory problems with large PDFs:

| GitHub Issue | Problem |
|--------------|---------|
| [#2077](https://github.com/docling-project/docling/issues/2077) | DoclingParseV4 accumulates 20GB+ for long documents |
| [#2786](https://github.com/docling-project/docling/issues/2786) | 3x memory increase between versions for 7000-page PDFs |
| [#1343](https://github.com/docling-project/docling/issues/1343) | Memory leak caused by EasyOCR |
| [#2209](https://github.com/docling-project/docling/issues/2209) | 13GB memory accumulation with DoclingParseV2 |

### Memory-Efficient Docling Configuration

If Docling quality is required:

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import gc

# Use PyPdfiumDocumentBackend for constant ~3.9GB memory
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False  # Major memory saver
pipeline_options.do_table_structure = False  # Moderate reduction

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            backend=PyPdfiumDocumentBackend,
            pipeline_options=pipeline_options
        )
    }
)

# Process in page ranges
for start in range(0, 300, 50):
    result = converter.convert("spec.pdf", page_range=(start, start + 50))
    markdown = result.document.export_to_markdown()
    # Save chunk
    del result
    gc.collect()
```

Key settings:
| Option | Impact |
|--------|--------|
| `backend=PyPdfiumDocumentBackend` | Constant ~3.9GB vs 20GB+ |
| `do_ocr=False` | Major memory reduction |
| `do_table_structure=False` | Moderate reduction |
| `page_range=(start, end)` | Enables chunked processing |

### PDF Splitting Approaches

#### qpdf (command-line)
```bash
# Split into 50-page chunks
qpdf --split-pages=50 large_spec.pdf chunk_%d.pdf

# Process each chunk, then merge markdown
cat chunk_*.md > full_document.md
```

#### pypdf (Python)
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("large_spec.pdf")
batch_size = 50

for start in range(0, len(reader.pages), batch_size):
    writer = PdfWriter()
    for page in range(start, min(start + batch_size, len(reader.pages))):
        writer.add_page(reader.pages[page])
    writer.write(f"batch_{start//batch_size:03d}.pdf")
```

### Alternative Tools

| Tool | Memory | Quality | Tables | Best For |
|------|--------|---------|--------|----------|
| **PyMuPDF4LLM** | Excellent | Good | Basic | Fast extraction, clean PDFs |
| **Docling + pypdfium2** | Good (~4GB) | Excellent | Excellent | Structured docs, tables |
| **Marker** | Moderate (~4.5GB) | Excellent | Good | OCR needed, multi-format |
| **pdfminer.six** | Poor | Basic | No | Not recommended for large files |

### PyMuPDF4LLM Usage

Native page-by-page processing:

```python
import pymupdf4llm

# Extract with page chunking - memory efficient
chunks = pymupdf4llm.to_markdown("large_spec.pdf", page_chunks=True)

# Combine
full_markdown = "\n\n".join(chunk["text"] for chunk in chunks)
```

## Code/Model References

- m-scout processor: `/home/reid/m-scout/tools/pdf_processing/processors/pdf_process.py:202-207` - fallback logic
- Part1 extraction output: `/home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/`
- Part1 summary: `processor_used: "pymupdf"` (automatic fallback)

## Feasibility Assessment

**Part1 extraction is already complete** using PyMuPDF fallback. Quality assessment:
- 47,797 lines extracted (comprehensive)
- 0 garbled characters (clean encoding)
- 118 chunks, 486 images captured

If Docling quality is specifically needed for better table/structure handling:
1. Use `PyPdfiumDocumentBackend` + `page_range` batching
2. Disable OCR if not needed
3. Process in 50-page batches with explicit `gc.collect()`

## Recommendations

### For Current Task (Part1)

**No action needed** - PyMuPDF extraction is complete and usable:
```bash
# Copy to agentic-mbse
cp /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/full_document.md \
   /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/
```

### For Future Large PDFs

1. **Default approach**: Let m-scout auto-fallback to PyMuPDF (works now)
2. **If Docling quality needed**:
   - Use `--page-batch-size` CLI option (if available)
   - Or split PDF with qpdf first, process chunks
3. **For very large docs (1000+ pages)**: Pre-split with qpdf, process in parallel

### Potential m-scout Enhancement

Consider adding a `--page-range` or `--batch-pages` flag to explicitly enable chunked processing:

```bash
# Hypothetical enhancement
python pdf_process.py --docling --batch-pages 50 large_spec.pdf
```

This would:
1. Split PDF into 50-page temporary files
2. Process each with Docling
3. Merge markdown output
4. Clean up temp files

## Open Questions

1. Is Docling's table extraction quality significantly better than PyMuPDF for these specs?
2. Should m-scout's auto-fallback behavior be documented more prominently?
3. Worth adding explicit batch-processing support to m-scout?

---

**Related:**
- Spec: `.project/active/extract-missing-pdf-specs/spec.md`
- Plan: `.project/active/extract-missing-pdf-specs/plan.md`
- Epic: `.project/backlog/epic_documentation-discoverability.md`
