# Epic: PDF Extraction Quality & Features

**Epic ID**: EPIC-PDFV4-002
**Status**: In Progress (Item 1 Phase 1 complete)
**Priority**: P1
**Created**: 2026-03-01
**Estimated Effort**: ~4.5 days

**Parent**: Builds on EPIC-PDFV4-001 (complete)
**Branch**: `doc-ingest-clean`

---

## Executive Summary

The v4 pipeline shipped with quality regressions versus v3 output (running headers, GMFT routing gaps, equation detection blind spots) and missing features (no image output of any kind). This epic fixes the regressions and builds a unified image output system that handles figures, table crops, and (future) equation crops through a single pipeline mechanism rather than three independent bolt-ons.

---

## Why This Epic?

**Current State**:
- Running headers and page numbers in output (v3 stripped these; 22 noise lines in 12-page doc)
- GMFT-detected tables on pymupdf-miss pages route to GMFT_APPEND instead of Claude
- Equation rendering failures don't trigger Claude enhancement (**fixed** — Phase 1 complete)
- `write_images=False` hardcoded — no figure extraction
- Table crop images from GMFT/Img2Table saved to temp dirs and discarded after use
- No OCR support for scanned PDFs (Docling deep-dive proved EasyOCR works)

**Future State**:
- Output cleaner than v3 (zero noise lines, no duplicate table content)
- Quality gate catches equation failures and GMFT/pymupdf table mismatches
- Unified image output: figures, table crops, and equation crops all land in `images/` via one mechanism
- Scanned PDFs get usable output via EasyOCR integration

---

## Design Rationale: Unified Image Output

The original quality regressions design (Component 4) proposed re-enabling `write_images=True` for pymupdf4llm figures. The IMGEXT backlog items independently proposed persisting table crops (001), figure extraction (003), and equation crops (002). These are **four points on the same image pipeline that doesn't exist yet**.

Implementing them separately means touching `pipeline.py`, `_postprocess_final()`, and `PipelineResult` three times for three image types with slightly different plumbing each time. Instead, this epic builds one image output system that all sources feed into.

### Core Pattern: ImageCollector

A lightweight accumulator that travels through the pipeline, gathering images from all sources:

```python
@dataclass
class ImageCollector:
    output_dir: Path                        # e.g., output/images/
    entries: list[ImageEntry] = field(default_factory=list)

    def add(self, source_path: Path, rel_name: str, kind: str, page_num: int) -> str:
        """Register an image. Returns the markdown reference string."""
        ...

    def persist(self) -> int:
        """Copy all source files to output_dir. Returns count."""
        ...

@dataclass
class ImageEntry:
    source_path: Path       # temp file or absolute pymupdf path
    rel_name: str           # "page_003_fig_1.png"
    kind: str               # "figure" | "table_crop" | "equation_crop"
    page_num: int
```

Each pipeline step adds entries:

| Step | Source | What it contributes |
|------|--------|-------------------|
| Step 2 (extract_pages) | pymupdf4llm `write_images=True` | Figure entries (absolute paths) |
| Step 3b (table filter/enhance) | `DetectedTable.image_path` | Table crop entries (from tmpdir) |
| (future) Step 3c | Equation detector | Equation crop entries |
| Step 7b (postprocess) | `collector.persist()` | Copy all to `images/`, normalize paths |

This means IMGEXT-001 (table crops) and IMGEXT-003 (figures) collapse into a single work item, and IMGEXT-002 (equations) becomes pure detector work — the image plumbing is already in place.

---

## Backlog Items

### Item 1: Quality Regressions — Gate & Routing Fixes [1 day]

**Type**: Bug fix
**Status**: Phase 1 complete, Phases 2-3 remaining
**Active work**: `.project/active/v4-output-quality-regressions/` (spec, design, plan ready)

**Scope** (remaining):
1. ~~Equation-fragment detection in quality gate~~ — **DONE** (Phase 1, 2026-03-01)
2. GMFT cross-reference step: boost severity when GMFT found tables that pymupdf missed → routes to CLAUDE_REPLACE instead of GMFT_APPEND (Phase 2 of existing plan)
3. Postprocess cleanup: wire `strip_running_headers()`, `strip_page_numbers()`, `repair_ligatures()` into pipeline step 7b (Phase 3 of existing plan)

**Out of Scope**:
- Image extraction (moved to Item 2) — Phase 4 of existing plan is superseded
- Table crop persistence (Item 2)

**Success Criteria**:
- [x] Equation fragments trigger Claude enhancement (severity >= 1.0)
- [ ] Zero running headers and page numbers in TEA document output
- [ ] GMFT-missed-table pages route to CLAUDE_REPLACE when budget allows
- [ ] No page has same table in both flat-text and pipe-table format
- [ ] Output line count <= v3 for equivalent content
- [ ] No test regressions

**Dependencies**: None
**Deliverables**: Updated quality_gate.py, pipeline.py, postprocess integration, tests

---

### Item 2: Unified Image Output Pipeline [1 day]

**Type**: Feature (replaces IMGEXT-001 + IMGEXT-003 + quality regressions Phase 4)
**Status**: Needs design

**Objective**: Build the image collector pattern and enable all current image sources — pymupdf4llm figures and GMFT/Img2Table table crops — in a single pass.

**Scope**:
1. **`ImageCollector` + `ImageEntry`** in `types.py` (~40 lines): accumulator dataclass with `add()` and `persist()` methods
2. **`extract_pages()` figure enablement** (`pymupdf_backend.py`): add `extracted_images_dir` param, pass `write_images=True` when set. Collector gathers figure entries from pymupdf's absolute paths.
3. **Table crop persistence** (`pipeline.py` step 3b): after table detection/enhancement, add `DetectedTable.image_path` entries to collector. Insert `![Table N](images/...)` references alongside pipe tables.
4. **`PipelineConfig.extracted_images_dir`** field + CLI wiring: create `output_dir/images/`, pass to config
5. **`_postprocess_final()` update**: call `collector.persist()` to copy all images, then `normalize_image_paths()` for pymupdf absolute paths. Call `promote_figure_captions()` for figures.
6. **`PipelineResult`** update: add `image_count: int` field
7. **Tests**: figure extraction (mock pymupdf), table crop persistence, path normalization, collector unit tests

**Success Criteria**:
- [ ] Embedded figures saved to `images/` with inline `![](images/...)` references
- [ ] Table crop PNGs from GMFT/Img2Table saved alongside figures in `images/`
- [ ] Table crops referenced in markdown near their pipe tables
- [ ] Figure captions promoted from separate paragraphs to alt-text
- [ ] Image paths are relative in final output
- [ ] `PipelineResult.image_count` reflects total images
- [ ] No images saved when `extracted_images_dir` is None (backward compat)
- [ ] Claude-replaced pages: orphan figure files are acceptable; table crops for those pages still saved

**Dependencies**: Item 1 (uses `_postprocess_final()` established in Phase 3)
**Deliverables**: types.py (ImageCollector), updated pymupdf_backend.py, pipeline.py, extract_cli.py, tests

---

### Item 3: Equation Region Detection [2 days]

**Type**: Research + Implementation (was IMGEXT-002)
**Status**: Needs research

**Objective**: Detect equation regions on PDF pages, crop as images, feed into the image collector.

**Scope**:
1. **Research** (~0.5 day): evaluate equation detection approaches:
   - pymupdf block classification (`block["type"] == 1` for images — do equations get classified?)
   - pix2tex / LaTeX-OCR region proposals
   - YOLO-based layout detection (e.g., publaynet, doclaynet models)
   - Docling's layout model (already installed — does it detect equation regions?)
2. **Implement detector** (~1 day): build `detect_equations()` returning equation bounding boxes + crops
3. **Integrate** (~0.5 day): plug into image collector (step 3c), associate crops with LaTeX transcription in output

**Success Criteria**:
- [ ] Display equations detected on math-heavy corpus pages (hawker_2020, araiinejad TEA)
- [ ] Equation crops saved to `images/` via collector
- [ ] Crops associated with corresponding LaTeX in output markdown
- [ ] No false positives on non-equation content
- [ ] Graceful degradation if detector dependencies missing

**Dependencies**: Item 2 (image collector infrastructure)
**Deliverables**: New equation detection module, integration into pipeline, tests

---

### Item 4: OCR Integration [0.5 days]

**Type**: Implementation
**Status**: Ready (findings from Docling deep-dive Phase 2B)

**Objective**: Integrate EasyOCR into the pipeline for scanned/degraded PDFs.

**Background**: Docling deep-dive proved EasyOCR dramatically improves OCR-quality docs (schulte_1978: 50K chars vs 7K garbled). EasyOCR is English-trained, pip-only, consistent. `force_full_page_ocr=False` is safe for born-digital docs (identical output).

**Scope**:
1. Add `--ocr` / `--ocr-engine` CLI flag to extract command
2. Wire OCR engine selection through to Docling single-page extraction path
3. Default off (no behavior change for born-digital docs)
4. Auto-detect scanned pages? (stretch — if OCR is on, only apply to pages with low text density)

**Success Criteria**:
- [ ] `--ocr` flag enables OCR on scanned PDFs via Docling+EasyOCR
- [ ] Born-digital PDFs produce identical output with OCR enabled
- [ ] No new hard dependencies (EasyOCR optional, graceful degradation)
- [ ] schulte_1978 produces readable output with `--ocr`

**Dependencies**: None (independent of image items)
**Deliverables**: Updated extract_cli.py, pipeline.py OCR path, tests

---

## Item Dependency Graph

```
Item 1 (Quality: gate + routing + postprocess)
    │
    v
Item 2 (Unified image output: figures + table crops)
    │
    v
Item 3 (Equation region detection + crops)

Item 4 (OCR) ← independent, can run in parallel with any item
```

**Critical Path**: Item 1 → Item 2 → Item 3 (4 days)
**Parallel**: Item 4 can start anytime

---

## Relationship to Prior Work

| Prior Item | Disposition |
|------------|-------------|
| `v4-output-quality-regressions` spec/design/plan | **Kept** — Items 1 uses Phases 2-3 directly. Phase 4 (image extraction) superseded by Item 2's unified approach. |
| IMGEXT-001 (table crop persistence) | **Absorbed** into Item 2 |
| IMGEXT-003 (figure image extraction) | **Absorbed** into Item 2 |
| IMGEXT-002 (equation region detection) | **Becomes** Item 3 (unchanged scope, but image plumbing is free from Item 2) |
| `docling-deep-dive` Phases 3-4 | **Not needed** — OCR findings (Phase 2B) are sufficient for Item 4. Close as research-complete. |
| `pandoc-deep-dive` Phases 5-6 | **Not needed** — Pandoc findings already integrated into v4. Close as research-complete. |
| `iteration-loop` | **Not in scope** — independent, separate decision. |

---

**Last Updated**: 2026-03-01
