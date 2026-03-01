# Spec: PDF Extraction Pipeline v4 — Item 2: Enhancement Components

**Status:** Complete (audited 2026-02-23)
**Owner:** Reid W
**Created:** 2026-02-23 17:48 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`
**Epic:** EPIC-PDFV4-001, Item 2
**Dependencies:** Item 1 (Types, Metrics & Quality Gate) — COMPLETE

---

## Business Goals

### Why This Matters

Item 1 built the pipeline's "decision brain" — the type system, quality gate, and routing logic that determines what happens to each page. But it has nothing to route *to*. Item 2 builds the enhancement components: ensemble table detection, Claude vision extraction, arXiv/Pandoc conversion, and per-page base extraction. These are the concrete actions the pipeline takes to improve PDF extraction quality beyond raw pymupdf4llm output.

Without Item 2, the pipeline can assess pages but cannot enhance them. This blocks Item 3 (orchestration) and Item 4 (integration tests + cleanup).

### Success Criteria

- [ ] All 4 enhancement modules (`tables.py`, `claude_enhance.py`, `pandoc_convert.py`, refactored `pymupdf_backend.py`) are independently testable with mocked dependencies
- [ ] All unit tests pass with no external dependencies (no PDFs, no network, no Claude, no GMFT)
- [ ] Graceful degradation works: missing GMFT → empty dict; missing Pandoc → None; missing Claude → skip

### Priority

P1 — on the critical path. Item 3 (Pipeline + CLI) depends on all Item 2 deliverables.

---

## Problem Statement

### Current State

- `pymupdf_backend.py` has `extract()` returning full-document `ExtractionResult` — no per-page `list[PageResult]` output
- `table_extraction.py` has single-detector GMFT extraction — no ensemble (Img2Table, Docling), no Claude FP filter, no table quality assessment
- `ai_repair.py` has `render_page_image()` — needs to move to a focused `claude_enhance.py` with page-level extraction and output validation
- No arXiv detection or Pandoc conversion exists in production code (only Stage 1B experiment scripts)
- Stage 3 experiment scripts (`tests/corpus/pipelines/shared.py`) have working implementations of table utilities, but they're not production modules

### Desired Outcome

Four production modules and one refactor that provide all enhancement capabilities the pipeline orchestrator (Item 3) needs. Each component:
- Accepts well-defined input types from Item 1's type system
- Returns well-defined output types
- Degrades gracefully when optional dependencies are absent
- Is independently unit-testable

---

## Scope

### In Scope

1. **`pymupdf_backend.py` refactor** (~30 lines added)
   - New `extract_pages(pdf_path) → list[PageResult]`
   - Uses `page_chunks=True` with full-document `IdentifyHeaders` calibration
   - Preserves existing `extract()` and `CompositeHeaderDetector`

2. **`tables.py`** (~400 lines) — Ensemble table detection and enhancement
   - Detection: `detect_tables_ensemble()`, `_detect_gmft()`, `_detect_img2table()`, `_detect_docling()`
   - Filtering: `filter_tables()` — secondary FP filters (prose cells, layout artifacts)
   - Quality: `assess_table_quality()` — flags extraction-failed and suspect tables
   - Enhancement: `enhance_table_with_claude()` — cropped image → markdown via Claude CLI
   - Markdown utilities: `strip_pipe_tables()`, `replace_tables()`, `insert_tables_at_end()`, `has_br_in_tables()`, `has_col_headers()`, `count_pipe_rows()`

3. **`pandoc_convert.py`** (~120 lines) — arXiv detection and Pandoc conversion
   - `detect_arxiv_id(pdf_path) → str | None`
   - `check_arxiv_html(arxiv_id) → str | None`
   - `convert_arxiv_html(html_source, pandoc_path) → str`
   - Pre-processing: strip `<figure>` tags, CSS transform wrappers
   - Post-processing: strip `\hspace{0pt}`, HTML comment artifacts

4. **`claude_enhance.py`** (~100 lines) — Claude vision page extraction
   - `render_page_image(pdf_path, page_num, dpi, output_dir) → Path`
   - `extract_page_with_claude(pdf_path, page_num, model, prompt, image_path, timeout) → (str, CostRecord)`
   - `validate_claude_output(claude_markdown, original_markdown, page_num) → (bool, str)`

5. **Unit tests** for each module
   - `tests/test_tables.py` — filter tests, quality assessment, table utilities, mocked Claude
   - `tests/test_pandoc_convert.py` — arXiv detection, HTML stripping, graceful degradation
   - `tests/test_claude_enhance.py` — sanity check tests (empty, truncated, prompt leak)

### Out of Scope

- Pipeline orchestration / `extract_pdf()` wiring (Item 3)
- CLI changes (Item 3)
- Integration tests against real corpus PDFs (Item 4)
- Deleting deprecated modules (Item 4)
- Docling MCP integration beyond a stub that returns empty on ImportError
- Batch processing or parallelization

### Edge Cases & Considerations

- **`extract_pages()` vs `extract()` heading calibration**: `page_chunks=True` uses the same `IdentifyHeaders` document-wide scan, so per-page headings SHOULD match full-document output. A unit test comparing per-page join vs full-document output should verify this.
- **GMFT extraction failure**: 7/15 tables on aries detected but DataFrame extraction returns null. `DetectedTable.extraction_failed=True` with `image_path` set — Claude enhancement handles these.
- **Claude returning 0 rows**: This is the FP filter signal. A table detection that Claude identifies as not-a-table should be dropped (markdown=""), not treated as an error.
- **Short pages and validate_claude_output**: Pages with < 200 chars original text are exempt from the >50% drop check, since Claude may legitimately produce more or less for figure-only pages.
- **Img2Table availability**: Part of the `gmft` package, guarded by `try/except ImportError` separately from GMFT's `AutoTableDetector` since it's a different submodule.

---

## Requirements

### Functional Requirements

> All requirements below are from the epic, design document, and prior experiments.

#### FR-EXT-1: Per-Page Base Extraction
`extract_pages()` MUST return `list[PageResult]` with 0-indexed page numbers. It MUST use `page_chunks=True` with the same `CompositeHeaderDetector` and BEST_V1 config as `extract()`. The existing `extract()` function MUST be preserved.

**Source:** Design §4.3, Epic Item 2 scope point 1

#### FR-EXT-2: Ensemble Table Detection
`detect_tables_ensemble()` MUST run detectors in order: GMFT (all pages) → Img2Table (GMFT-empty pages only) → Docling (optional, remaining pages). Each detector MUST be independently guarded by `try/except ImportError` returning empty dict. No confidence threshold — all detections kept. Cropped images MUST be saved for all detections (needed for Claude enhancement).

**Source:** Design §4.4, Requirements FR-4, Table spike v2 findings

#### FR-EXT-3: Secondary Table Filters
`filter_tables()` MUST reject tables with `avg_cell_length > 80` (prose blocks) and single-row tables with `>4` columns (layout artifacts). Tables with `extraction_failed=True` MUST pass through (Claude handles them). No confidence-based filtering.

**Source:** Design §4.4 `filter_tables()`, Stage 2 ground truth (hsu_2020 prose avg 85-120, data tables avg 5-20)

#### FR-EXT-4: Table Quality Assessment
`assess_table_quality()` MUST flag tables where `extraction_failed=True` (primary trigger) and tables with suspect quality indicators (secondary trigger). MUST return `(needs_enhancement, reasons)`.

**Source:** Design §4.4 `assess_table_quality()`, Table spike Track 1 (7/15 aries GMFT extraction failures)

#### FR-EXT-5: Claude Table Enhancement
`enhance_table_with_claude()` MUST use a table-specific prompt ("Extract this table as a markdown pipe table..."). MUST require `table.image_path` to be set. When Claude returns empty/0-row output, the returned `DetectedTable` MUST have `markdown=""` (FP filter signal). Returned table MUST have `source="claude_cropped"`.

**Source:** Design §4.4 `enhance_table_with_claude()`, Table spike (47 calls, zero reasoning leakage)

#### FR-EXT-6: Table Markdown Utilities
`strip_pipe_tables()` MUST remove pipe-table blocks (lines starting with `|` with ≥2 pipes) while preserving non-table content. `replace_tables()` MUST strip existing tables and append GMFT tables. `insert_tables_at_end()` MUST append tables after page content. `has_br_in_tables()`, `has_col_headers()`, `count_pipe_rows()` MUST detect their respective patterns.

**Source:** Design §4.4 utilities, Stage 3 `shared.py:322-430`

#### FR-EXT-7: arXiv Detection
`detect_arxiv_id()` MUST extract arXiv IDs from PDF page 1 text via regex (`arXiv:\d{4}\.\d{4,5}(v\d+)?`), with fallback to PDF Creator metadata field. MUST return `None` if no arXiv signal found.

**Source:** Design §4.2, Requirements FR-2

#### FR-EXT-8: arXiv HTML Check
`check_arxiv_html()` MUST perform HTTP HEAD to verify HTML availability. Timeout: 5 seconds. MUST return `None` on failure (silent skip).

**Source:** Design §4.2

#### FR-EXT-9: Pandoc Conversion
`convert_arxiv_html()` MUST pre-process (strip `<figure>` tags, CSS transform wrappers), run Pandoc with Stage 1B config (`html-native_divs-native_spans`, `markdown-header_attributes`, `--wrap=none`, `--markdown-headings=atx`), and post-process (strip `\hspace{0pt}`, HTML comment artifacts).

**Source:** Design §4.2, Stage 1B iter-16 config

#### FR-EXT-10: Page Image Rendering
`render_page_image()` MUST render a single PDF page to PNG at configurable DPI (default 200). MUST support optional output directory. Moves from `ai_repair.py`.

**Source:** Design §4.6, existing `ai_repair.py:122-143`

#### FR-EXT-11: Claude Page Extraction
`extract_page_with_claude()` MUST use pure vision mode (page image only, no supplemental text). MUST return `(markdown, CostRecord)`. The prompt SHOULD default to the `extract_baseline.txt` content embedded as a constant.

**Source:** Design §4.6, Stage 1D (supplemental text provides no benefit)

#### FR-EXT-12: Claude Output Validation
`validate_claude_output()` MUST reject: (1) empty/whitespace-only output, (2) >50% character drop vs original (unless original < 200 chars), (3) output containing literal prompt text. MUST return `(accept, reason)`.

**Source:** Design §4.6 NFR-4, Stage 1D (Claude output typically 80-120% of pymupdf character count)

### Non-Functional Requirements

#### NFR-EXT-1: Graceful Degradation
Every optional dependency (GMFT, Img2Table, Docling, Pandoc, Claude) MUST be guarded by lazy import with `try/except ImportError` or `shutil.which()` check. Missing dependency → silent skip returning empty/None. No `ImportError` or `FileNotFoundError` should propagate to the caller.

**Source:** Requirements NFR-1, Design §11

#### NFR-EXT-2: Error Isolation
A failure in any single detector or enhancement call MUST NOT crash the component. Each detector in the ensemble MUST be independently wrapped. A GMFT crash on one page MUST NOT prevent detection on other pages.

**Source:** Requirements NFR-3, Design §5.3

#### NFR-EXT-3: No Side Effects on Existing Code
Adding `extract_pages()` to `pymupdf_backend.py` MUST NOT change the behavior of `extract()` or `CompositeHeaderDetector`. Moving `render_page_image()` to `claude_enhance.py` is a copy (not move) for now — `ai_repair.py` deletion is Item 4.

---

## Acceptance Criteria

### Core Functionality

- [x] `extract_pages()` returns `list[PageResult]` with per-page markdown from pymupdf4llm
- [x] `detect_tables_ensemble()` calls GMFT → Img2Table (on GMFT-empty pages) → Docling (optional) in sequence
- [x] `filter_tables()` rejects prose blocks (`avg_cell_length > 80`) and layout artifacts (1 row, >4 cols)
- [x] `filter_tables()` passes through `extraction_failed=True` tables without filtering
- [x] `assess_table_quality()` flags extraction-failed tables for Claude enhancement
- [x] `enhance_table_with_claude()` returns `DetectedTable` with `source="claude_cropped"` (mocked in tests)
- [x] `enhance_table_with_claude()` requires `table.image_path` to be set
- [x] Claude returning empty → `DetectedTable.markdown=""` (FP filter signal)
- [x] `validate_claude_output()` rejects empty output, >50% character drop, and prompt leaks
- [x] `validate_claude_output()` accepts short pages (< 200 chars original) regardless of ratio
- [x] `detect_arxiv_id()` extracts arXiv IDs from page 1 text
- [x] `convert_arxiv_html()` strips `<figure>` tags and `\hspace{0pt}` artifacts
- [x] Table markdown utilities (`strip_pipe_tables`, `replace_tables`, `insert_tables_at_end`) produce correct output

### Graceful Degradation

- [x] `ImportError` for GMFT → `_detect_gmft()` returns empty dict
- [x] `ImportError` for Img2Table → `_detect_img2table()` returns empty dict
- [x] Docling unavailable → `_detect_docling()` returns empty dict
- [x] Missing Pandoc → `convert_arxiv_html()` raises or returns None (caller handles)
- [x] Missing Claude → caller skips enhancement (claude_enhance functions are not called)

### Quality & Integration

- [x] All unit tests pass with no external dependencies (no PDFs, no network, no Claude, no GMFT)
- [x] Existing tests continue to pass (`pytest tests/`)
- [x] `extract()` and `CompositeHeaderDetector` behavior unchanged in `pymupdf_backend.py`

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 2)
- **Requirements:** `.project/concepts/doc-extraction/requirements.md` (FR-2 through FR-6, NFR-1/3/4)
- **Design:** `.project/concepts/doc-extraction/design.md` (§4.2-4.6, §11, §13)
- **Item 1 Deliverables:** `types.py`, `metrics.py`, `quality_gate.py`, `pipeline.py` (budget helpers)
- **Stage 3 Reference:** `tests/corpus/pipelines/shared.py` (table utilities, GMFT extraction, per-page extraction)
- **Table Spike Reference:** `.project/active/table-image-spike/findings.md`, `findingsv2.md`
- **Design:** `.project/active/pdf-extraction-v4-item2/design.md` (to be created)

---

## Deliverables

| File | Type | Est. Lines |
|------|------|:---:|
| `src/agentic_mbse/extraction/pymupdf_backend.py` | Refactor (add `extract_pages()`) | +30 |
| `src/agentic_mbse/extraction/tables.py` | New module | ~400 |
| `src/agentic_mbse/extraction/pandoc_convert.py` | New module | ~120 |
| `src/agentic_mbse/extraction/claude_enhance.py` | New module | ~100 |
| `tests/test_tables.py` | New tests | ~200 |
| `tests/test_pandoc_convert.py` | New tests | ~100 |
| `tests/test_claude_enhance.py` | New tests | ~150 |

---

**Next Steps:** After approval, proceed to `/_my_plan` to create the implementation plan with phases and checkboxes.
