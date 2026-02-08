# Spec: Document Extraction

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-03 00:16 UTC
**Complexity:** HIGH
**Branch:** pdf-extract

---

## Business Goals

### Why This Matters

agentic-mbse users need to ingest reference documents (specs, standards, technical reports) into their documentation corpus for AI-assisted systems engineering. Currently this requires a separate tool (m-scout) with its own virtual environment, manual path configuration, and multi-project orchestration. This creates friction and prevents agentic-mbse from being self-contained.

By bringing document extraction directly into agentic-mbse, users get a single command to convert PDFs and DOCX files into structured, indexed markdown ready for use by Claude agents.

### Success Criteria

- [ ] A user can run `agentic-mbse extract document.pdf` and get structured markdown with embedded image references
- [ ] A user can run `agentic-mbse extract document.docx` and get equivalent results
- [ ] Extraction works on large documents (500+ pages) without manual intervention
- [ ] The tool gracefully handles memory-constrained environments via timeout and fallback
- [ ] Output is immediately usable by existing agentic-mbse tooling (`generate_index.py`, `read_section.py`, Claude agents)

### Priority

High — this removes a key external dependency and unblocks self-contained document workflows.

---

## Problem Statement

### Current State

Document extraction lives in a separate project (m-scout) with:
- Its own Python virtual environment (`~/m-scout/pdf_env`)
- Hardcoded output paths that must be manually edited
- No DOCX support
- No integration with agentic-mbse's CLI or index generation
- Manual orchestration between two codebases (extract in m-scout, then run `generate_index.py` in agentic-mbse)

### Desired Outcome

A single, integrated extraction pipeline within agentic-mbse that handles PDF and DOCX files, produces structured markdown with images, and optionally generates navigable indexes with AI summaries — all from one CLI command.

---

## Scope

### In Scope

- PDF extraction with dual-backend strategy (Docling primary, PyMuPDF4LLM fallback)
- DOCX extraction with format-aware backend selection (Docling primary, Pandoc fallback)
- Image extraction with embedded markdown references
- Table reconstruction (best effort, leveraging Docling's ML-based structure detection)
- Configurable timeout on primary extractor with automatic fallback
- Two-pass table repair using Claude headless mode (opt-in)
- Integration with existing `generate_index.py` as optional post-processing step
- LLM-based section summarization option in index generation
- New `agentic-mbse extract` CLI subcommand
- Benchmarking suite for extraction quality validation

### Out of Scope

- OCR for scanned/image-only PDFs
- Physical chunking into separate files (agentic-mbse philosophy: `full_document.md` + `INDEX.md`)
- Batch/interactive sequential processing workflows
- Embedding/vector database integration
- PPTX, XLSX, or other format support (can be added later — Docling supports them)

### Edge Cases & Considerations

- Very large PDFs (1000+ pages) may exhaust memory with Docling
- Some PDFs have no extractable text (scanned images) — should fail gracefully with clear message
- DOCX files with embedded OLE objects or complex formatting may lose fidelity
- Tables spanning multiple pages may break across extraction boundaries
- Image-heavy documents may produce large output directories

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

#### Format Support

1. **FR-1**: MUST support PDF input format
2. **FR-2**: MUST support DOCX input format

#### PDF Extraction

3. **FR-3**: MUST extract images from PDFs and embed file references directly into the output markdown (e.g., `![](images/figure_NNN.png)`)
4. **FR-4**: MUST attempt the best available document extractor first (Docling), with a configurable timeout to handle memory limitations
5. **FR-5**: MUST fall back to a reliable extraction method (PyMuPDF4LLM) when the primary extractor fails or times out
6. **FR-6**: SHOULD reconstruct tables with best available fidelity (Docling's `do_table_structure=True` for PDFs)

#### DOCX Extraction

7. **FR-7**: MUST extract DOCX files to markdown with images and tables preserved
8. **FR-8**: SHOULD use a format-aware fallback strategy: Docling primary, Pandoc fallback (Pandoc is proven best-in-class for DOCX)

#### Index Generation

9. **FR-9**: MUST offer an option to generate a file index with section headers, summaries, and line number mapping (integrate existing `generate_index.py`)
10. **FR-10**: The index MUST offer an option for LLM-based section summarization (existing capability in `generate_index.py`)

#### Table Repair

11. **FR-11**: SHOULD offer a two-pass methodology to fix broken tables using Claude headless mode (`claude -p`), invoked as an opt-in post-processing step

#### Fallback & Resilience

12. **FR-12**: MUST implement configurable timeout on primary extractor (Docling) to handle memory-constrained environments
13. **FR-13**: MUST automatically fall back to the secondary extractor when the primary fails, times out, or runs out of memory
14. **FR-14**: [INFERRED] SHOULD produce a `summary.json` metadata file tracking processing status, extractor used, and basic statistics

#### CLI Integration

15. **FR-15**: [INFERRED] MUST provide an `agentic-mbse extract` CLI subcommand
16. **FR-16**: [INFERRED] SHOULD support both single-file and directory input (process all PDFs/DOCX in a directory)

#### Output Structure

17. **FR-17**: [INFERRED] MUST produce a `full_document.md` as the primary output
18. **FR-18**: [INFERRED] MUST save extracted images to an `images/` subdirectory alongside the markdown
19. **FR-19**: [INFERRED] When index generation is requested, MUST produce an `INDEX.md` in the same output directory

### Non-Functional Requirements

#### Benchmarking

20. **NFR-1**: During implementation, MUST assemble a representative set of test documents (PDF and DOCX) covering diverse layouts: text-heavy, table-heavy, image-heavy, large (500+ pages), and mixed content
21. **NFR-2**: MUST benchmark each extractor combination against the test set, measuring: extraction quality/readability, processing time, and peak memory usage
22. **NFR-3**: Final sequencing of fallback strategies (which extractor is primary, timeout thresholds, fallback order) MUST be adjusted based on benchmark results rather than assumed

#### Performance

23. **NFR-4**: [INFERRED] Fallback extractor (PyMuPDF4LLM for PDF, Pandoc for DOCX) SHOULD complete within 2 minutes for a 500-page document
24. **NFR-5**: [INFERRED] Default timeout for primary extractor SHOULD be configurable (suggested default: 10 minutes)

#### Dependencies

25. **NFR-6**: [INFERRED] Heavy dependencies (Docling) SHOULD be optional extras (`uv add agentic-mbse[extract]` or similar) so they don't bloat the base install
26. **NFR-7**: [INFERRED] Pandoc system binary dependency SHOULD be documented clearly, with a helpful error message if not found

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse extract document.pdf` produces `document/full_document.md` with embedded image references
- [ ] `agentic-mbse extract document.docx` produces equivalent output
- [ ] Images are saved to `document/images/` and referenced in markdown
- [ ] Tables are rendered as markdown tables in output
- [ ] When Docling times out or fails, extraction automatically retries with fallback backend
- [ ] `agentic-mbse extract document.pdf --index` produces `document/INDEX.md` with section headers and line numbers
- [ ] `agentic-mbse extract document.pdf --index --summarize` produces INDEX.md with LLM-generated section summaries
- [ ] `agentic-mbse extract document.pdf --fix-tables` runs two-pass table repair via Claude headless mode

### Benchmarking

- [ ] A benchmark suite exists with representative test documents
- [ ] Benchmark results are documented with quality, time, and memory measurements
- [ ] Fallback ordering reflects benchmark findings

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] New extraction functionality has its own test suite
- [ ] Output is compatible with existing `read_section.py`
- [ ] `summary.json` metadata is produced for each extraction

---

## Related Artifacts

- **Existing code to integrate:** `scripts/generate_index.py`, `scripts/read_section.py`
- **Reference implementation:** `~/m-scout/tools/pdf_processing/`
- **Learnings:** `.project/completed/20260116_syside-084-upgrade/plan.md` (external tool orchestration friction)
- **Design:** `.project/active/document-extraction/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
