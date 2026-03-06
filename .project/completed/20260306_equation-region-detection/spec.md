# Spec: Equation Region Detection

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-01 19:24 PST
**Completed:** 2026-03-01
**Complexity:** HIGH
**Branch:** doc-ingest-clean

---

## Business Goals

### Why This Matters

The v4 pipeline handles equations in two incomplete ways: the quality gate detects *garbled* equation text and routes those pages to Claude for full re-extraction, and pymupdf4llm renders equations as scattered italic fragments (e.g., `_C_ = _CEEDB_` for a scaling equation). Neither approach preserves the visual equation layout.

For math-heavy documents — techno-economic analyses, academic papers, CERN reports — equations are primary domain content, not decoration. An LLM reading extracted output cannot interpret `_Pnew_\n_C_ = _CEEDB_\n(2.2)` as a coherent equation. A cropped image of the original equation region, placed inline near the text transcription, gives both human and LLM readers a faithful visual reference.

The image collector infrastructure (Item 2) already supports `kind="equation_crop"` in its type definitions and requires zero plumbing changes to persist equation crops. This feature is the detector that feeds it.

### Success Criteria

- [x] Display equations detected on math-heavy corpus pages (hawker_2020, paischer_2025)
- [x] Equation crops saved to `images/` via the existing ImageCollector
- [x] Crops placed inline near their corresponding text in the output markdown
- [x] Acceptable false positive rate on non-equation content (see evaluation criteria below)
- [x] Graceful behavior when no equations are present in a document

### Priority

P2 within EPIC-PDFV4-002. Depends on Item 2 (image collector infrastructure, complete). Independent of Item 3 (profiling).

---

## Problem Statement

### Current State

1. **No equation region detection exists.** The pipeline has no mechanism to identify where equations appear on a PDF page or crop them as images. The `RegionType = Literal["table", "equation", "structure"]` in `base.py` is unused scaffolding.

2. **Quality gate detects symptoms, not regions.** `_assess_equation_fragments()` in `quality_gate.py` detects equation rendering failures at the text level (italic fragments followed by `(N.N)` equation numbers). It flags pages for Claude re-extraction but does not identify equation bounding boxes or produce crops.

3. **pymupdf4llm produces unreadable equation text.** Display equations are rendered as sequences of italic fragments with lost spatial layout. Even on Claude-replaced pages, equations appear as text transcriptions without visual representation.

4. **The image collector has no equation sources.** `ImageEntry.kind` documents `"equation_crop"` as a valid value, but nothing produces entries of that kind.

### Desired Outcome

A new pipeline step detects display equation regions on PDF pages, crops them as images, and registers them with the existing ImageCollector. The crops appear inline in the output markdown near the text where the equation was rendered, providing a visual reference alongside the (potentially garbled) text transcription. The detector follows the same structural patterns as table detection (`tables.py`) — a standalone module with a clear interface that the pipeline calls at the appropriate step.

---

## Scope

### In Scope

- **Equation detector module**: New `equations.py` (or similar) with a `detect_equations()` function returning `dict[int, list[DetectedEquation]]` (page-indexed)
- **`DetectedEquation` dataclass**: Bounding box, confidence, cropped image path, optional equation label — modeled after `DetectedTable`
- **Pipeline integration**: New step between table detection and quality gate, following the `_try_detect_*()` error-isolation pattern
- **ImageCollector registration**: Equation crops registered as `kind="equation_crop"`, named `page_{NNN}_eq_{M}.png`
- **Positional placement**: Equation crop images placed inline near the corresponding equation text in the output markdown
- **Pipeline gating**: `PipelineConfig` flag to enable/disable equation detection
- **Tests**: Unit tests for detector, integration tests against corpus math-heavy documents

### Out of Scope

- **LaTeX OCR / transcription**: No pix2tex or LaTeX-OCR transcription of detected equations. Crops are visual-only references placed near the existing text rendering.
- **Inline equation detection**: Only display (block) equations — inline math symbols embedded in running text are not targeted.
- **Quality gate changes**: The existing `_assess_equation_fragments()` and `_assess_math_garbling()` are complementary and unchanged.
- **Claude prompt changes**: Claude's equation handling on replaced pages is unaffected.
- **Performance optimization of the detector**: This feature establishes correct behavior; speed tuning is future work.

### Edge Cases & Considerations

- **No equations in document**: The detector MUST return an empty dict without error. The pipeline MUST handle zero equation detections identically to current behavior.
- **Overlapping regions**: An equation region may overlap with a figure or table region. The detector SHOULD avoid cropping regions already identified as tables by the table detection step.
- **Multi-line equations**: Some display equations span multiple lines (e.g., aligned systems, matrices). The detector MUST handle these as single regions, not crop each line separately.
- **Equation numbering**: Display equations often have labels like `(2.1)` in the right margin. The crop region SHOULD include the equation number when present.
- **Claude-replaced pages**: On pages routed to CLAUDE_REPLACE, the original pymupdf equation text is discarded. Equation crops for these pages are still valuable as visual references alongside Claude's text transcription.
- **Pages with many equations**: Some pages have 3-5 display equations. The detector MUST handle multiple equations per page.
- **Scanned/degraded PDFs**: Detection accuracy may be lower on scanned documents. The detector SHOULD still attempt detection; low-confidence results MAY be filtered.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and user's request unless marked [INFERRED].

1. **FR-1**: The pipeline MUST support a `detect_equations()` function that takes a PDF path and returns detected equation regions indexed by 0-based page number: `dict[int, list[DetectedEquation]]`.

2. **FR-2**: `DetectedEquation` MUST include at minimum: bounding box coordinates, confidence score, cropped image path (`Path | None`), and whether the equation is a display equation.

3. **FR-3**: The detector MUST crop detected equation regions as PNG images and save them to a temporary directory, following the same pattern as `_save_table_image()` in `tables.py`.

4. **FR-4**: The pipeline MUST register equation crop images with the existing `ImageCollector` using `kind="equation_crop"`, with filenames following the convention `page_{NNN}_eq_{M}.png`.

5. **FR-5**: Equation crop image references MUST be placed inline near the corresponding equation text in the output markdown, not appended at the end of the page.

6. **FR-6**: The detector MUST target display (block) equations. Inline math symbols in running text are out of scope.

7. **FR-7**: `PipelineConfig` MUST include a flag to enable/disable equation detection (default: enabled when `extracted_images_dir` is set). [INFERRED]

8. **FR-8**: The detector MUST be error-isolated — a failure in equation detection MUST NOT crash the pipeline. The pipeline MUST use the `_try_detect_*()` wrapper pattern established by table detection.

9. **FR-9**: When no equations are detected (empty result), the pipeline MUST produce output identical to current behavior.

10. **FR-10**: Any new package dependencies required by the detector MUST be added as hard dependencies in `pyproject.toml`, not optional extras.

### Non-Functional Requirements

- Existing tests MUST continue to pass
- Pipeline with equation detection disabled MUST produce identical output to current behavior
- No changes to existing modules (quality_gate.py, tables.py) unless strictly necessary for integration

---

## Evaluation Criteria

The design phase MUST research detection approaches and define experiments. The following evaluation criteria — derived from the existing codebase and corpus — define what "good enough" means.

### Corpus Test Documents

The test corpus (`tests/corpus/papers.jsonl`) includes these math-heavy documents with ground truth:

| Document | Display Equations | Pages | Characteristics |
|----------|:-:|:-:|------|
| `hawker_2020` | 21 | 14 | TEA paper, heavy garbling in baseline, strikethroughs around symbols |
| `paischer_2025` | 23 | 24 | NeurIPS paper, 2-column layout, has ArXiv HTML for comparison |
| `sparc_overview` | — | 25 | Fusion physics, `[/]` garbled fractions, inline math |
| `seo_2024` | — | 19 | Math-heavy + figure-heavy |
| `woodruff_2026b` | — | 25 | Costing paper with math |
| `hansen_2025` | 0 | 28 | Heavy inline math, zero display equations — negative test case |

### Detection Accuracy

- **Recall**: On `hawker_2020` (21 display equations) and `paischer_2025` (23 display equations), the detector SHOULD find >= 80% of display equations. Manual spot-check against a sample of 5 pages per document.
- **Precision**: On `hansen_2025` (0 display equations, heavy inline math), the detector MUST produce zero false positives. On documents with both tables and equations, the detector MUST NOT misclassify tables as equations.
- **Primary metric**: The design SHOULD define a simple precision/recall scoring approach that can be run against the corpus without manual ground truth annotation for every equation.

### Crop Quality

- Cropped images MUST include the full equation with no clipping of symbols at region boundaries.
- Crops SHOULD include equation labels (e.g., `(2.1)`) when present.
- Crops MUST NOT include significant surrounding text (paragraph content above/below the equation).

### Integration Quality

- Equation crop images MUST appear in `images/` alongside table crops and figures when the pipeline runs on a math-heavy document.
- The inline markdown reference MUST be positioned within 5 lines of the corresponding equation text in the output (measured by proximity to the `(N.N)` equation number or the italic fragment cluster).

---

## Acceptance Criteria

### Core Detection

- [x] `detect_equations()` returns detected regions for `hawker_2020` (>= 80% of 21 display equations)
- [x] `detect_equations()` returns detected regions for `paischer_2025` (>= 80% of 23 display equations)
- [x] `detect_equations()` returns zero results for `hansen_2025` (inline math only, no display equations)
- [x] Equation crops include full equation content without clipping
- [x] Multi-line equations (aligned systems, matrices) are detected as single regions

### Pipeline Integration

- [x] Equation crops registered with ImageCollector as `kind="equation_crop"`
- [x] Equation crop PNGs saved to `images/` directory via `collector.persist()`
- [x] Inline `![](images/page_NNN_eq_M.png)` references appear near equation text in output
- [x] Pipeline with equation detection disabled produces identical output to current behavior
- [x] Equation detection failure is isolated — pipeline completes without equation crops on error

### Quality & Integration

- [x] Existing tests continue to pass
- [x] New detector dependencies added as hard dependencies in `pyproject.toml`
- [x] Unit tests for `DetectedEquation` dataclass and `detect_equations()` interface
- [x] Integration test running pipeline on a math-heavy corpus document with equation detection enabled

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-improvements.md` (EPIC-PDFV4-002, Item 4)
- **Dependency:** `.project/active/unified-image-output/` (Item 2, complete — provides ImageCollector)
- **Research (quality failures):** `.project/research/20260227-210000_extraction-quality-failures.md` — documents equation rendering failure modes
- **Key source files:**
  - `src/agentic_mbse/extraction/types.py:13-17` — `ImageEntry` with `kind="equation_crop"`
  - `src/agentic_mbse/extraction/tables.py` — structural template for detector module
  - `src/agentic_mbse/extraction/pipeline.py:320-388` — steps 3/3b (insertion point for 3c)
  - `src/agentic_mbse/extraction/pipeline.py:63-95` — `ImageCollector` (no changes needed)
  - `src/agentic_mbse/extraction/quality_gate.py:162-200` — `_assess_equation_fragments()` (complementary, unchanged)
  - `tests/corpus/papers.jsonl` — ground truth with `display_equations` counts

---

**Completed:** All acceptance criteria met. See `plan.md` for implementation details and `design.md` for architecture.
