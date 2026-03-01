# Spec: Cropped Table Image Extraction Spike

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-02-23 12:03 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

Tables are the highest-sensitivity content in technical documents — a single wrong number in a cost table or performance spec invalidates everything downstream. The current pipeline (H5) has two modes for Claude: expensive full-page replacement ($0.078/page) or nothing. Stage 1D found that focused repair prompts ("fix only the table") don't work because Claude rewrites the entire page from the full-page image regardless.

Cropped table images change the problem structurally: when the image IS the table, Claude can't get distracted by surrounding content. This should make Claude more accurate (all attention on the table) and more cost-effective (smaller images = fewer tokens). Combined with multi-pass strategies (vote/resolve between GMFT and Claude, or sequential review), this could address the two biggest remaining gaps: Claude being viewed as "redundant" for tables, and its cost/latency making broad use impractical.

Critically, automatic table detection and image export must work end-to-end for this to have pipeline value. GMFT misses space-aligned tables entirely (the biggest gap in aries_cost_account). PyMuPDF's `page.find_tables()` uses a different detection algorithm (line/text analysis vs GMFT's deep learning) and may catch what GMFT misses. This spike MUST test both detectors to understand the union of their detection coverage.

### Success Criteria

- [ ] SC-1: We know the detection coverage of GMFT vs PyMuPDF `find_tables()` vs their union — specifically, how many of aries_cost_account's ~28 tables does each find?
- [ ] SC-2: We know empirically whether Claude extracts tables more accurately from cropped images than from full-page images (comparison against ground truth)
- [ ] SC-3: We know whether independent multi-pass (GMFT + Claude vote/resolve) produces measurably better table accuracy than either tool alone
- [ ] SC-4: We know whether sequential multi-pass (Claude reviews GMFT output with table image) produces measurably better results than independent extraction
- [ ] SC-5: We have concrete recommendations for Stage 4 pipeline design: which detection strategy, which multi-pass strategy (if any) to adopt, and integration points

### Priority

Stage 3 addendum / pre-Stage 4 learning. Results directly inform whether Stage 4's pipeline design includes a `TableEnhancer` protocol, vote/resolve logic, or sequential review capability.

---

## Problem Statement

### Current State

The H5 pipeline routes pages to Claude only for full-page replacement at $0.078/page. For table issues specifically:

- **GMFT** extracts tables as DataFrames — accurate on grid-lined tables (40/40 hawker, 52/53 paischer) but over-detects on non-journal docs (42/15 hansen, 88/56 hsu) and misses space-aligned tables entirely
- **pymupdf4llm** misses gridless tables completely (0/40 hawker, 0/15 hansen, 0/150 delene) and produces `<br>` artifacts and false positives (137/53 paischer)
- **Claude full-page** is accurate (40/40 hawker, 56/56 hsu, 15/15 hansen, 55/53 paischer) but expensive and was never tested with just the table region
- **aries_cost_account** is the biggest gap: GT ~280 table rows, pymupdf4llm gets 137 (with artifacts), GMFT gets 175, neither catches space-aligned tables

Stage 1D's focused repair experiments found that Claude ignores "focus only on fixing the table" when given full-page images — it rewrites the entire page from vision. This closed the door on targeted table repair via full-page images.

GMFT's `CroppedTable` objects expose bounding boxes and a built-in `.image()` method, but the pipeline only uses confidence scores and DataFrames. The cropped image capability is untested.

### Desired Outcome

Empirical answers to:
1. Can we automatically detect and export table images — including space-aligned tables that GMFT misses?
2. Does Claude extract tables more accurately from cropped images than from full-page images?
3. Do multi-pass strategies (vote/resolve, sequential review) improve table accuracy beyond what either tool achieves alone?

---

## Scope

### In Scope

**Track 0: Table Detection Coverage**
- Run both GMFT (`AutoTableDetector`) and PyMuPDF (`page.find_tables()`) on all 5 test papers
- For each detector: record which pages have tables, bounding boxes, confidence scores
- Save cropped table images from both detectors: GMFT via `CroppedTable.image(dpi=200)`, PyMuPDF via `page.get_pixmap(dpi=200, clip=tab.bbox)`
- Measure the **union** of detection: how many tables does each find, how many does only one find, how many do both find?
- Key question: does the union of GMFT + PyMuPDF close the gap on aries_cost_account (GT ~28 tables, ~280 rows)?

**Track 1: Cropped Image Extraction**
- Send cropped table images (from Track 0) to Claude with a table-specific extraction prompt
- Use the best-available image per table (GMFT preferred for grid-lined tables; PyMuPDF for tables only it detects)
- Measure: accuracy vs ground truth, cost per table, tokens per table, image dimensions
- Compare against: GMFT DataFrame extraction, Claude full-page extraction (from Stage 1D data)

**Track 2: Independent Multi-Pass (Vote/Resolve)**
- Run GMFT DataFrame extraction and Claude cropped-image extraction independently on the same tables
- Compare outputs: row counts, cell value agreement, structural differences
- Test resolution strategies: prefer higher row count, prefer Claude when disagree, cell-level comparison
- Measure: combined accuracy vs ground truth

**Track 3: Sequential Multi-Pass (Review/Fix)**
- Give Claude both the GMFT markdown table AND the cropped table image
- Prompt: "Here is a table extracted by a library tool. Review it against the original image and correct any errors."
- This tests whether Claude can operate as a reviewer/corrector rather than an independent extractor
- Compare against: Track 1 (independent Claude), Track 2 (vote/resolve), GMFT alone

**Test Corpus:**
- hawker_2020 (14pp, 3 tables, 40 GT rows) — dotted-line tables pymupdf4llm misses entirely
- hsu_2020 (9pp, 3 tables, 56 GT rows) — calibration target, all tools roughly agree
- hansen_2025 (28pp, 1 table, 15 GT rows) — space-aligned table
- paischer_2025 (24pp, 5 tables, 53 GT rows) — complex tables with LaTeX in cells
- aries_cost_account (100pp, 28 tables, ~280 GT rows) — biggest gap, space-aligned + nested hierarchies

### Out of Scope

- Production code, module design, or type system work (this is experiment scripts only)
- Equation-focused experiments (Stage 1D already proved Claude's equation value)
- Haiku model comparison (use Sonnet throughout for consistency with prior data)
- Docling table image extraction (too slow, and GMFT is the pipeline's table detector)
- Batch processing, CLI integration, or any Stage 4+ implementation

### Edge Cases & Considerations

- **Multi-table pages:** When a detector finds 2-3 tables on one page, each table gets its own cropped image and separate Claude call. Track results per-table, not just per-page.
- **GMFT false positives:** Tables rejected by the false-positive filter (confidence < 0.98, avg cell length > 80) SHOULD still have their images saved for analysis to understand what's being filtered out.
- **PyMuPDF false positives:** `find_tables()` may also over-detect. Apply analogous filtering (minimum row/column count, minimum cell count) and record rejection reasons.
- **Detector overlap:** When both GMFT and PyMuPDF detect the same table, the bounding boxes may differ slightly. Use IoU (intersection over union) > 0.5 to identify overlapping detections. For overlapping tables, save images from both detectors and note which produces a tighter crop.
- **Coordinate systems:** GMFT uses PyPDFium2 coordinates (top-left origin); PyMuPDF uses its own coordinate space (also top-left origin). Both should be compatible for image cropping within their respective libraries. Cross-library bbox comparison (for overlap detection) may need normalization — test empirically.
- **Large tables spanning most of a page:** The cropped image may be nearly page-sized. Record image dimensions to understand the size distribution.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

**Track 0: Table Detection Coverage**

1. **FR-1**: The experiment MUST run GMFT `AutoTableDetector` on all 5 test papers and record per-page table bounding boxes, confidence scores, and save cropped images via `CroppedTable.image(dpi=200)`.
2. **FR-2**: The experiment MUST run PyMuPDF `page.find_tables()` on all 5 test papers and record per-page table bounding boxes, row/column counts, and save cropped images via `page.get_pixmap(dpi=200, clip=tab.bbox)`.
3. **FR-3**: The experiment MUST compare detection coverage between the two detectors: tables found by both, tables found by only GMFT, tables found by only PyMuPDF, and tables found by neither (against ground truth table counts).
4. **FR-4**: [INFERRED] The experiment SHOULD apply false-positive filtering to both detectors (GMFT: existing confidence/cell-length filter; PyMuPDF: analogous heuristics) and report pre-filter vs post-filter counts.

**Track 1: Cropped Image Extraction**

5. **FR-5**: The experiment MUST send cropped table images to Claude (Sonnet) with a table-specific extraction prompt and capture the resulting markdown pipe table.
6. **FR-6**: The experiment MUST compare Claude's cropped-image table extraction against ground truth (from `ground_truth.jsonl`) using row counts and, where feasible, cell-level spot-checks.
7. **FR-7**: The experiment MUST record per-table data: input tokens, output tokens, total cost, wall clock time, image dimensions (pixels).
8. **FR-8**: [INFERRED] The experiment MUST compare cropped-image results against existing Stage 1D full-page Claude data and GMFT DataFrame data for the same tables.

**Track 2: Independent Multi-Pass (Vote/Resolve)**

9. **FR-9**: The experiment MUST produce two independent markdown tables per detected table: one from GMFT DataFrame extraction and one from Claude cropped-image extraction.
10. **FR-10**: The experiment MUST implement at least two resolution strategies and measure accuracy of each:
    - Strategy A: Prefer Claude when row counts differ (Claude is the accuracy ceiling from Stage 2)
    - Strategy B: Cell-level comparison — flag cells where GMFT and Claude disagree, prefer Claude's value

**Track 3: Sequential Multi-Pass (Review/Fix)**

11. **FR-11**: The experiment MUST send Claude both the GMFT markdown table AND the cropped table image with a review/correction prompt.
12. **FR-12**: The experiment MUST measure whether Claude's review-mode output is more accurate than its independent extraction (Track 1) or the GMFT input alone.
13. **FR-13**: [INFERRED] The review prompt MUST instruct Claude to output ONLY the corrected markdown table (no commentary, no reasoning), addressing the reasoning-leakage issue found in Stage 1D Track B.

**Cross-Track**

14. **FR-14**: All experiment results MUST be saved in `tests/corpus/runs/` following the existing convention: `runs/{experiment_name}/{slug}/` with per-table output files and summary metrics.
15. **FR-15**: [INFERRED] The experiment MUST produce a findings document at `.project/active/table-image-spike/findings.md` with per-track results, cross-track comparison, and Stage 4 recommendations.

### Non-Functional Requirements

15. **NFR-1**: Experiment scripts SHOULD be runnable independently per track (e.g., `python track1_cropped_baseline.py --slugs hawker_2020`) for iterative development.
16. **NFR-2**: The experiment SHOULD reuse existing infrastructure from `tests/corpus/pipelines/shared.py` (GMFT extraction, metrics, ground truth scoring) rather than reimplementing.

---

## Acceptance Criteria

### Track 0: Table Detection
- [ ] GMFT and PyMuPDF `find_tables()` both run on all 5 test papers
- [ ] Cropped table images saved from both detectors
- [ ] Detection coverage comparison: per-paper counts of tables found by each detector and their union
- [ ] Clear answer: does the union close the gap on aries_cost_account?

### Track 1: Cropped Image Extraction
- [ ] Claude extraction run on cropped images with per-table accuracy data
- [ ] Side-by-side comparison: Claude-cropped vs GMFT-DataFrame vs Claude-full-page (Stage 1D) vs ground truth

### Track 2: Vote/Resolve
- [ ] Two resolution strategies implemented and scored against ground truth
- [ ] Clear answer: does vote/resolve beat the better individual tool, and by how much?

### Track 3: Sequential Review
- [ ] Claude receives GMFT output + table image and produces corrected table
- [ ] Accuracy compared against Track 1 (independent Claude) and GMFT alone
- [ ] Reasoning leakage assessed (does the stricter prompt eliminate it?)

### Cross-Track
- [ ] All results saved in `tests/corpus/runs/`
- [ ] Findings document produced with clear Stage 4 recommendations
- [ ] Answers to: "Which detectors should Stage 4 use?" and "Which multi-pass strategy (if any) should Stage 4 adopt?"

---

## Experiment Design Notes

### Track 0: Detection Strategy

Two detectors, different algorithms:

- **GMFT** (`AutoTableDetector`): Deep learning (Microsoft TATR model). Operates on PyPDFium2 page objects. Returns `CroppedTable` with `.rect.bbox`, `.confidence_score`, `.image()`.
- **PyMuPDF** (`page.find_tables()`): Heuristic (line/text analysis). Returns `Table` with `.bbox`, `.row_count`, `.col_count`, `.cells`. Image via `page.get_pixmap(clip=tab.bbox)`.

The key question is whether their detection is complementary (union > either alone) or redundant. aries_cost_account is the critical test case — GMFT gets ~175 rows (GT ~280), and we don't know what PyMuPDF `find_tables()` gets.

For overlap detection: normalize both detectors' bboxes to page-relative coordinates (0-1 range) and compute IoU. Tables with IoU > 0.5 are considered the same detection.

### Prompt Design

Two prompts needed:

1. **Track 1 prompt (cropped extraction):**
   ```
   Extract this table as a markdown pipe table.
   Rules:
   - Use | column headers | separated | by pipes |
   - Include separator row (|---|---|---|)
   - Preserve ALL numerical values exactly as printed
   - Preserve merged/spanning cells by repeating values
   - Output ONLY the markdown table, no commentary
   ```

2. **Track 3 prompt (sequential review):**
   ```
   A library tool extracted the following table from this image:

   {gmft_markdown}

   Review the extracted table against the image. Correct any errors:
   - Wrong numbers, missing rows, extra rows, garbled text
   - Output ONLY the corrected markdown table, no commentary
   - If the table is correct, output it unchanged
   ```

Track 2 uses the Track 1 prompt for Claude's independent extraction; no separate prompt needed.

### What We're Measuring

| Metric | How | Source |
|--------|-----|--------|
| Detection coverage | Tables found per detector vs GT table count | Track 0 output |
| Detection overlap | IoU between GMFT and PyMuPDF bboxes | Track 0 output |
| Table row accuracy | Row count vs ground truth | `ground_truth.jsonl` |
| Cell-level accuracy | Manual spot-check of 3-5 values per table on subset | Human review |
| Cost per table | `total_cost_usd` from Claude JSON response | Experiment output |
| Image dimensions | PIL `Image.size` at save time | Experiment output |
| Reasoning leakage | Grep for commentary/reasoning text in output | Automated check |

---

## Related Artifacts

- **Research:** `.project/research/20260223-table-images-from-pdfs.md`
- **Strategy:** `.project/concepts/doc-extraction-development-strategy.md` (Stage 3→4 transition)
- **Stage 1D findings:** `.project/active/claude-headless-deep-dive/findings.md` (full-page Claude, focused repair failures)
- **Stage 3 findings:** `.project/active/pipeline-experimentation/findings.md` (H5 pipeline, known table gaps)
- **Ground truth:** `tests/corpus/ground_truth.jsonl`
- **Existing infra:** `tests/corpus/pipelines/shared.py` (GMFT extraction, metrics, scoring)
- **Design:** `.project/active/table-image-spike/design.md` (to be created if warranted)

---

**Next Steps:** Given this is a spike (experiment scripts, not production code), we MAY proceed directly to implementation planning without a formal design document. The experiment scripts follow the established pattern from `tests/corpus/pipelines/`.
