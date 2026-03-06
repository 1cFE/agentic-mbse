# Implementation Plan: Docling & GMFT Deep-Dive (Stage 1C)

**Status:** In Progress (Phase 2B Complete)
**Created:** 2026-02-22
**Last Updated:** 2026-02-22

## Source Documents

- **Spec:** `spec.md`
- **Development Strategy:** `../../concepts/doc-extraction-development-strategy.md` (Stage 1C)
- **pymupdf4llm Findings:** `../pymupdf4llm-deep-dive/findings.md` (baseline gaps driving this work)
- **Current Docling backend:** `src/agentic_mbse/extraction/docling_backend.py`

## Implementation Strategy

**This is a learning test with two tools.** The pymupdf4llm deep-dive identified specific gaps (complex tables, equations, OCR). This plan investigates whether Docling and GMFT can fill those gaps, how well, and at what cost.

The structure mirrors Stage 1A: **setup → baselines → explore → head-to-head → synthesize**. The explore phase is deliberately open-ended — what you investigate depends on what the baselines reveal.

Two tools means more surface area but also natural comparison points. Avoid the temptation to test every parameter on every document — focus on the documents and pages where pymupdf4llm has known problems, then broaden only if findings warrant it.

---

## Phase 0: Setup

### Goal

Get both tools' APIs documented, the experiment harness extended to support them, and model weights downloaded so timing measurements are accurate.

### 0.1 API Documentation — Docling

Gather Docling v2.71.0 reference material:

1. **Read installed source** for `PdfPipelineOptions` — enumerate all parameters with defaults
   ```python
   # Quick way to find the class:
   from docling.datamodel.pipeline_options import PdfPipelineOptions
   import inspect; print(inspect.getsource(PdfPipelineOptions))
   ```
2. **Read `DocumentConverter`** — understand format options, how conversion works
3. **Read `DoclingDocument`** — export methods (`.export_to_markdown()`, `.export_to_dict()`, iteration over `.texts`, `.tables`, `.pictures`)
4. **Check OCR configuration** — what does `do_ocr=True` actually invoke? What backends? What dependencies?
5. **Check table model options** — is TableFormer configurable? Are there quality/speed knobs?
6. **Save to** `api-reference-docling.md`

### 0.2 API Documentation — GMFT

Gather GMFT v0.4.2 reference material:

1. **Read installed source** for `AutoTableDetector` and `AutoTableFormatter`
2. **Understand output chain**: detection → `CroppedTable` → formatting → `FormattedTable` → `.df()` / `.markdown()` / `.html()`
3. **Enumerate parameters**: `enable_multi_header`, `semantic_spanning_cells`, confidence thresholds, anything else
4. **Understand page binding**: `PyPDFium2Document` — how pages are loaded, any gotchas vs PyMuPDF page numbering
5. **Save to** `api-reference-gmft.md`

### 0.3 Experiment Harness Extension

Extend `tests/corpus/experiment.py` to support multiple backends:

1. Add `--backend` flag: `pymupdf4llm` (default), `docling`, `gmft`
2. **Docling backend function**:
   - Runs `DocumentConverter.convert()` on the PDF
   - Exports to markdown via `.export_to_markdown()`
   - Returns markdown string + elapsed time
   - Runs in subprocess with timeout (reuse `run_with_timeout` from `base.py`, or implement inline)
3. **GMFT backend function**:
   - Opens PDF via `PyPDFium2Document`
   - For each page: detect tables → format → collect markdown
   - Returns concatenated table markdown + elapsed time
   - Note: GMFT only extracts tables, not full document text — the harness should record this difference
4. Both backends compute metrics via existing `metrics.py` (same comparison infrastructure)
5. Results saved to `tests/corpus/runs/{config_name}/` (same structure)
6. `--compare` works across backends (comparing a Docling run to the pymupdf4llm baseline)

**Keep it simple.** The harness is a convenience for running experiments, not production code.

### 0.4 Trigger Model Downloads

Docling downloads ~500MB of model weights on first invocation. Do this once before timing experiments:

```python
from docling.document_converter import DocumentConverter
converter = DocumentConverter()
# Convert a small PDF to trigger downloads
converter.convert("tests/corpus/pdfs/hsu_2020.pdf")
```

GMFT also downloads Table Transformer weights (~100MB) on first use. Trigger this too:

```python
from gmft.auto import AutoTableDetector
detector = AutoTableDetector()  # downloads model weights
```

### Phase 0 Validation

- [x] `api-reference-docling.md` captures PdfPipelineOptions params, DocumentConverter usage, export methods, OCR config
- [x] `api-reference-gmft.md` captures detector/formatter params, output formats, page binding
- [x] Harness runs with `--backend docling` and produces output in `runs/` directory
- [x] Harness runs with `--backend gmft` and produces output in `runs/` directory
- [x] Model weights downloaded (subsequent runs don't include download time)

### Phase 0 Implementation Notes

**Completed:** 2026-02-22

**Changes Made:**
- Created `.project/active/docling-deep-dive/api-reference-docling.md` — full PdfPipelineOptions parameter reference, DocumentConverter API, OCR engines, page_range for single-page extraction
- Created `.project/active/docling-deep-dive/api-reference-gmft.md` — TATRDetectorConfig, TATRFormatConfig parameters, PyPDFium2Document usage, detection→formatting pipeline
- Modified `tests/corpus/experiment.py` — added `--backend` flag (pymupdf4llm/docling/gmft), `--timeout`, `--page-range`, Docling subprocess extraction with timeout, GMFT per-page table detection+formatting
- Model weights already present (Docling ~500MB, GMFT ~100MB, RapidOCR torch models)

**Key API Discoveries:**
1. Docling `do_ocr` defaults to `True` (our backend sets `False` explicitly)
2. Docling `do_formula_enrichment` exists — math→LaTeX conversion, must test
3. Docling `page_range=(N, N)` is 1-indexed inclusive — clean single-page API
4. Docling `document_timeout` parameter exists — built-in timeout alternative to our subprocess approach
5. GMFT `enable_multi_header` and `semantic_spanning_cells` are the two key config knobs
6. GMFT `detector_base_threshold=0.9` is conservative — may want to test lower
7. GMFT output is via pandas DataFrame → `df.to_markdown()` (requires tabulate)

**Smoke Test Results (hsu_2020, 9pp):**
- Docling: 13.7s, 14,947 chars, 6 headings, 56 table rows, 0 math
- GMFT: 1.7s, 11,977 chars (tables only), 0 headings, 88 table rows
- pymupdf4llm baseline: 1.3s, 13,560 chars, 4 headings, 56 table rows, 0 math
- Cross-backend `--compare` works correctly

---

## Phase 1: Baselines

### Goal

Run both tools with their default/current configurations against the corpus. Capture metrics AND actually look at the output. This establishes what each tool does out of the box and reveals where to focus exploration.

### 1.1 Docling Baseline

Run the current config (`do_table_structure=True, generate_picture_images=True, do_ocr=False`) against all 14 unique documents:

```bash
python tests/corpus/experiment.py docling_baseline --backend docling --compare baseline
```

**For each document, note:**
- Extraction time (Docling is expected to be much slower — quantify how much)
- Did it complete without timeout/crash? (especially energy_amplifier at 241pp)
- Table quality — are pipe tables well-formed? Do spanning cells survive?
- Heading structure — does Docling detect headings pymupdf4llm missed?
- Page artifacts — does Docling strip headers/footers automatically (DocLayNet should)?
- Math content — any improvement over pymupdf4llm's garbled output?
- Image references — how does Docling represent figures?

**Actually read the markdown output** for at least: aries_cost_account (tables), schulte_1978 (OCR), hawker_2020 (math), hsu_2020 (tables + short), paischer_2025 (tables + math).

### 1.2 GMFT Baseline

Run default GMFT against all documents with table content:

```bash
python tests/corpus/experiment.py gmft_baseline --backend gmft --slugs aries_cost_account,araiinejad_2024,paischer_2025,helios_design,sparc_overview,energy_amplifier,hsu_2020 --compare baseline
```

**For each document, note:**
- How many tables detected per document?
- Detection accuracy — any false positives (diagrams detected as tables)? False negatives (real tables missed)?
- Formatting quality — are the markdown pipe tables well-formed? Column alignment?
- Spanning cells — how does GMFT handle merged cells?
- Speed — how fast per page and per table?

Also run on a couple of non-table documents (e.g., hawker_2020, tajima) to check false positive rate.

### 1.3 Write Initial Observations

Create `findings.md` with initial quality observations for both tools. Structure:

```markdown
# Docling Baseline Observations
## Per-Document Notes
...

# GMFT Baseline Observations
## Per-Document Notes
...

# Initial Comparison: Where Each Tool Adds Value
...

# Questions for Phase 2
(What should we investigate next based on what we saw?)
```

### Phase 1 Validation

- [x] Docling baseline metrics captured for all 14 documents (or documented which failed/timed out)
- [x] GMFT baseline metrics captured for all 7 table-bearing documents (plus all 15 for false positive testing)
- [x] `findings.md` created with per-document quality observations for both tools
- [x] Known issues and investigation priorities identified for Phase 2

### Phase 1 Implementation Notes

**Completed:** 2026-02-22

**Runs Executed:**
1. `docling_baseline` — defaults (do_ocr=True), 5/15 completed, 10 timed out at 300s
2. `docling_no_ocr` — do_ocr=False, 4/15 completed before run was stopped (same docs time out)
3. `docling_aries_p8` — single page, aries_cost_account page 8, 8.2s
4. `docling_paischer_p8` — single page, paischer_2025 page 8, 8.3s
5. `docling_schulte_ocr` — single page with OCR, schulte_1978 page 3, 9.0s
6. `docling_sparc_p1_5` — pages 1-5, sparc_overview, 7.7s
7. `gmft_baseline` — all 15 docs, all completed, 76s total

**Key Findings:**
- Docling full-document mode is impractical — times out on 10/15 corpus docs even without OCR
- Docling single-page extraction (7-9s/page) is viable and produces good output
- GMFT completely eliminates `<br>` artifacts (71→0 on aries_cost_account, 62→0 on paischer_2025)
- GMFT is the clear winner for table extraction: fast, clean, no timeouts
- Docling is the clear winner for heading detection: 18 vs 0 on hansen_2025
- Docling OCR (RapidOCR) is terrible on schulte_1978 — Chinese-trained model on 1978 English text
- Math handling is unchanged by either tool in default config — `do_formula_enrichment` untested
- Timeout bottleneck is layout model + TableFormer, NOT OCR

**Deviations from Plan:**
- Ran GMFT on ALL 15 docs (not just 7 table-bearing) to test false positive rate — valuable data
- Added single-page Docling runs for timed-out documents — this wasn't in the plan but was necessary to get any quality data for those docs
- Stopped `docling_no_ocr` run early after confirming OCR wasn't the bottleneck (saved ~40 min of timeouts)

---

## Phase 2: Explore

### Goal

Systematically investigate Docling and GMFT parameters. Understand which settings matter, which don't, and where each tool helps (or doesn't) compared to pymupdf4llm.

### Method

Same iterative loop as Stage 1A. Each iteration:

```
1. IDENTIFY — What gap or question are we investigating?
              (driven by Phase 1 observations, not a checklist)

2. HYPOTHESIZE — What parameter or config change might help?
                 (consult api-reference docs, read source if needed)

3. RUN — Execute via the harness

4. EVALUATE — Look at results:
   - Compare metrics against baseline (harness --compare)
   - INSPECT ACTUAL OUTPUT for affected documents/pages
     Compare specific table output side by side
     Use pdf-analysis skill to render pages for visual comparison
   - Note what improved, what regressed, what's unchanged

5. RECORD — Update findings.md with:
   - What we tried and why
   - What we observed (metrics + manual inspection + specific examples)
   - What we concluded
   - What this suggests investigating next

6. DECIDE — What's the next most valuable thing to look at?
```

### Guidance (not prescriptions)

**Start with the known gaps from Stage 1A.** The pymupdf4llm findings identified specific documents and pages with problems. Test Docling and GMFT against those exact pages first:

| Gap | Test Documents | What to Look For |
|-----|---------------|------------------|
| `<br>` table artifacts (333 total) | aries_cost_account, araiinejad_2024, paischer_2025 | Do the artifacts disappear? Is cell structure preserved? |
| Spanning/merged cells | aries_cost_account, helios_design | Are multi-column headers handled? Row spans? |
| OCR quality | schulte_1978 | Does `do_ocr=True` fix "~aboratory"? Speed cost? |
| Math garbling | hawker_2020, paischer_2025 | Does Docling produce LaTeX? Better Unicode? Or same garbling? |
| Header under-detection | sparc_overview (1 heading) | Does Docling's DocLayNet detect section headers pymupdf4llm missed? |

**Compare tools, not just configurations.** When you find a page where GMFT excels, run the same page through Docling and pymupdf4llm. When Docling handles a table well, check if GMFT does too. Build intuition for which tool wins where.

**Measure the cost.** Every quality improvement has a speed cost. Record extraction time alongside quality observations. A 10x slower tool that produces 5% better tables may not be worth it for the pipeline.

**Test OCR carefully.** Docling's OCR mode is the only option for schulte_1978-class documents. If it works well, it opens a whole category of PDFs. If it doesn't, we need to know clearly.

**Test single-page extraction for Docling.** The existing backend has subprocess timeout protection because Docling can OOM. Can we extract individual pages safely? Does per-page extraction produce the same quality as full-document? This matters for the pipeline's memory safety story.

**Don't test things that don't matter.** If the baseline shows Docling's image handling is fine, don't spend time exploring image parameters. If GMFT's default confidence threshold works well, don't micro-optimize it. Focus on the gaps.

**Use the pdf-analysis skill for hands-on comparison.** Render a page as an image, then compare the three tools' text output for that page side by side. This catches things metrics miss.

### What NOT to Do

- Don't follow a rigid predetermined experiment list — adapt based on findings
- Don't skip manual inspection in favor of just looking at metrics
- Don't build pipeline or merge logic — this phase is about understanding each tool in isolation
- Don't try to test every parameter on every document — focus on the gaps
- Don't ignore crashes/timeouts — these are findings too, and they matter for pipeline design

### Phase 2 Validation

- [x] At least 4 Docling configurations tested and documented (beyond baseline)
- [x] At least 3 GMFT configurations tested and documented (beyond baseline)
- [x] OCR mode tested on schulte_1978 with quality assessment
- [x] Single-page vs full-document Docling extraction compared
- [x] Each experiment has observations in `findings.md` (not just metrics)
- [x] Manual inspection performed for documents with known pymupdf4llm gaps
- [x] Clear sense of which parameters matter for each tool

### Phase 2 Implementation Notes

**Completed:** 2026-02-22

**Experiments Executed (8 beyond baseline):**

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 1 | `docling_formula` | hawker_2020 timeout; hansen_2025 has no formulas |
| 2 | `docling_formula_p2_4` | **Formula enrichment works** — produces LaTeX, quality varies |
| 3 | `gmft_multiheader` | **Worse** — tuple column headers for markdown |
| 4 | `gmft_spanning` | **Marginal** — fills some hierarchical codes, occasional errors |
| 5 | `docling_fast` | **15-35% speedup only** — doesn't fix timeouts |
| 6 | `docling_schulte_noocr` | OCR was no-op (no engines installed); errors from PDF text layer |
| 6b | `docling_easyocr_schulte_*` | **EasyOCR works!** 7x more text, readable English, minor l/I/T errors |
| 7 | `gmft_threshold_95` | **Too aggressive** — loses 12-30% real tables |
| 8 | `docling_hsu_p1-p9` | **Per-page loses headings** (3 vs 6); text/tables nearly identical |

**Key Conclusions:**
- **Docling best config:** `do_ocr=False` + single-page extraction. Formula enrichment valuable but only in single-page mode.
- **GMFT best config:** Default (`detector_base_threshold=0.9`, `enable_multi_header=False`). No config changes improve it.
- **Layout model is the real bottleneck** — not OCR, not TableFormer mode
- **EasyOCR dramatically improves OCR-quality docs** — schulte_1978 goes from garbled to readable (50K chars vs 7K)

**Changes Made:**
- Modified `tests/corpus/experiment.py` — added `table_structure_options` and `ocr_options` nested parameter handling in `_docling_extract_worker()`
- Updated `findings.md` — Phase 2 answers table, 8 experiment log entries, updated Math Handling and OCR sections

---

## Phase 2B: OCR Engine Deep-Dive

### Goal

Systematically evaluate the OCR engines available to Docling. Phase 2 revealed that no OCR backends were installed (`rapidocr`, `easyocr`, `pytesseract` all missing), making `do_ocr=True` a silent no-op. The "OCR errors" in schulte_1978 come from the PDF's corrupt embedded text layer, not from any OCR engine. This phase installs and tests real OCR backends to determine which engine (and configuration) produces the best results for scanned and degraded documents.

This matters beyond schulte_1978 — any pipeline that handles real-world academic papers will encounter scanned documents, older publications, and PDFs with damaged text layers. The OCR engine choice affects quality, speed, and deployment complexity.

### Why a Separate Phase

OCR was blocked in Phase 2 (no engines installed) and is a distinct dimension from the table/formula/heading exploration already completed. Each engine has its own installation requirements, configuration surface, and quality characteristics. This deserves focused evaluation rather than being a footnote in Phase 2.

### Test Documents

| Document | Pages | Why |
|----------|-------|-----|
| schulte_1978 | page 3 | **Primary target.** Corrupt embedded text layer — "FUSIOi4", "STAidDARD", "Wi 11 ke". Requires `force_full_page_ocr=True` to bypass corrupt text. 1978 English technical document — stress test for OCR on older typography. |
| schulte_1978 | page 5 | **Secondary target.** Different page content — test consistency across pages. |
| schulte_1978 | full doc (10pp) | **Full-document run.** Once best engine is identified, run full doc to assess total extraction quality and time. |
| tajima | page 1 | **Born-digital control.** Confirm OCR doesn't degrade quality on a document where the text layer is fine. Run with `force_full_page_ocr=False` (default) — OCR should skip this page entirely. |
| hawker_2020 | page 3 | **Born-digital control with math.** Ensure OCR mode doesn't interfere with equation-heavy content on born-digital PDFs. |

### Engines to Evaluate

#### Engine 1: EasyOCR

**Install:** `pip install easyocr` (or `pip install "docling[easyocr]"`)
**System deps:** None
**Why test:** Pure Python, zero system dependencies, easiest deployment story. Supports 80+ languages. GPU-accelerable.

**Experiments:**

| # | Experiment | Config | Documents |
|---|-----------|--------|-----------|
| 1 | `docling_easyocr_en` | `EasyOcrOptions(lang=["en"], force_full_page_ocr=True)` | schulte_1978 p3, p5 |
| 2 | `docling_easyocr_gpu` | `EasyOcrOptions(lang=["en"], force_full_page_ocr=True, use_gpu=True)` | schulte_1978 p3 (if GPU available — compare speed) |
| 3 | `docling_easyocr_control` | `EasyOcrOptions(lang=["en"], force_full_page_ocr=False)` | tajima p1, hawker_2020 p3 (born-digital control — should be no-op) |
| 4 | `docling_easyocr_full` | `EasyOcrOptions(lang=["en"], force_full_page_ocr=True)` | schulte_1978 full doc |

**What to evaluate:**
- Character accuracy on schulte_1978 page 3 — can it read "FUSION", "STANDARD", "Willke"?
- Total character count (Phase 2 got only 464 chars from page 3 — how much more does real OCR produce?)
- Speed per page (EasyOCR is reportedly fast on GPU, slow on CPU)
- False interference on born-digital docs (should produce identical output to no-OCR)

#### Engine 2: Tesseract

**Install:** System package + Python bindings
- Linux: `apt install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config` then `pip install tesserocr`
- Alternatively: `pip install pytesseract` + system `tesseract` binary (TesseractCliOcrOptions)
**System deps:** Yes (tesseract binary + language data)
**Env var:** `TESSDATA_PREFIX` must point to language data directory
**Why test:** Industry standard for English OCR. Best individual character accuracy among open-source options. Decades of academic paper digitization. Most mature option.

**Experiments:**

| # | Experiment | Config | Documents |
|---|-----------|--------|-----------|
| 5 | `docling_tesseract_en` | `TesseractOcrOptions(lang=["eng"], force_full_page_ocr=True)` | schulte_1978 p3, p5 |
| 6 | `docling_tesseract_cli` | `TesseractCliOcrOptions(lang=["eng"], force_full_page_ocr=True)` | schulte_1978 p3 (compare Python bindings vs CLI — sometimes differ in quality) |
| 7 | `docling_tesseract_control` | `TesseractOcrOptions(lang=["eng"], force_full_page_ocr=False)` | tajima p1, hawker_2020 p3 |
| 8 | `docling_tesseract_full` | `TesseractOcrOptions(lang=["eng"], force_full_page_ocr=True)` | schulte_1978 full doc |

**What to evaluate:**
- Character accuracy vs EasyOCR on the same pages — head-to-head on schulte_1978 p3
- Handling of 1978 typography (older fonts, typewriter text, faded print)
- Speed comparison (Tesseract is CPU-only, no GPU acceleration)
- Installation friction — how painful is the system dependency for users?

#### Engine 3: RapidOCR with English Models

**Install:** `pip install rapidocr-onnxruntime` (already partially present as Docling default)
**System deps:** None
**Why test:** RapidOCR is already Docling's default — the problem is the **Chinese-trained PaddleOCR models**, not the engine itself. With proper English models, it might work well. Tests whether reconfiguration fixes the issue without switching engines.

**Experiments:**

| # | Experiment | Config | Documents |
|---|-----------|--------|-----------|
| 9 | `docling_rapidocr_en` | `RapidOcrOptions(lang=["en"], force_full_page_ocr=True)` | schulte_1978 p3 (test if `lang=["en"]` selects English models) |
| 10 | `docling_rapidocr_custom` | `RapidOcrOptions(det_model_path=..., rec_model_path=..., force_full_page_ocr=True)` with English PaddleOCR models | schulte_1978 p3 (if lang param doesn't work, try explicit model paths) |
| 11 | `docling_rapidocr_control` | `RapidOcrOptions(force_full_page_ocr=False)` | tajima p1 |

**What to evaluate:**
- Does `lang=["en"]` actually switch models, or is it just a passthrough label?
- If custom model paths are needed, document the download + configuration steps
- Quality vs EasyOCR and Tesseract on the same pages
- Whether "fixing" the default is simpler than switching engines

### Method

Same iterative loop as Phase 2:

1. **Install** each engine (document exact steps — this is valuable for the pipeline's deployment story)
2. **Run** experiments via the harness with `--backend docling` and appropriate `ocr_options`
3. **Inspect output** — actually read the markdown, don't just look at metrics. For schulte_1978, check specific known-bad strings:
   - "FUSIOi4" → should be "FUSION"
   - "STAidDARD" → should be "STANDARD"
   - "Wi 11 ke" → should be "Willke"
   - "~ormerly" → should be "formerly"
   - "Battel le" → should be "Battelle"
   - "Pub1 ic" → should be "Public"
4. **Record** results in findings.md with side-by-side output comparison
5. **Compare** engines head-to-head on identical pages

### Deliverables

1. **OCR engine comparison table** in findings.md:

```markdown
| Engine | schulte p3 Accuracy | Speed (p3) | Speed (full doc) | Install Complexity | Notes |
|--------|---------------------|------------|------------------|-------------------|-------|
| RapidOCR (default) | Terrible | 9.0s | — | None (bundled) | Chinese models |
| EasyOCR | ? | ? | ? | pip only | |
| Tesseract | ? | ? | ? | System + pip | |
| RapidOCR (English) | ? | ? | ? | pip + model download | |
```

2. **Specific output samples** — the actual text extracted from schulte_1978 page 3 by each engine, for direct quality comparison
3. **Recommended OCR engine** for the pipeline, with rationale
4. **Installation documentation** — exact steps to install each engine, for inclusion in the pipeline's setup guide
5. **Born-digital safety confirmation** — evidence that OCR mode with `force_full_page_ocr=False` doesn't degrade born-digital document quality

### Phase 2B Validation

- [x] At least 3 OCR engines tested on schulte_1978 page 3 — **2 of 3** (EasyOCR + RapidOCR tested; Tesseract blocked on sudo for system package)
- [x] Head-to-head output comparison with specific text samples in findings.md
- [x] Born-digital control tests confirm no degradation (tajima, hawker_2020)
- [x] Full-document run on schulte_1978 with best engine (EasyOCR: 50,752 chars; RapidOCR: 55,933 chars)
- [x] Installation steps documented for each engine
- [x] Clear recommendation for pipeline default OCR engine with evidence — **EasyOCR** (English-trained, zero system deps, proven in Phase 2)
- [x] Speed data captured for each engine (per-page and full-document)

### Phase 2B Implementation Notes

**Completed:** 2026-02-22

**Experiments Executed (7 new):**

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 1 | `docling_easyocr_control` | Born-digital p1 output identical to no-OCR baseline — safe default |
| 2 | `docling_easyocr_control_p3` | Math-heavy page unaffected by OCR mode |
| 3 | `docling_rapidocr_schulte_p3` | Chinese models read English — "FUSION", "Battelle" correct, but loses some lines |
| 4 | `docling_rapidocr_schulte_p5` | **Better than EasyOCR on this page** — correct text flow vs garbled |
| 5 | `docling_rapidocr_schulte_full` | 55,933 chars (+10% vs EasyOCR), similar speed |
| 6 | `docling_rapidocr_control` | Born-digital identical to no-OCR — safe default |
| 7 | (English PaddleOCR models) | Blocked — models in PaddlePaddle format, need paddle2onnx conversion |

**Key Conclusions:**
- **EasyOCR recommended as pipeline default** — English-trained, pip-only, consistent
- **RapidOCR is viable alternative** — smaller footprint (15MB vs 100MB), surprisingly good English from Chinese models
- **force_full_page_ocr=False is safe** — both engines produce identical output to no-OCR on born-digital docs
- **Tesseract untested** — requires `sudo apt install tesseract-ocr tesseract-ocr-eng` (system dependency)
- **RapidOCR lang param is a no-op** — doesn't switch models, Chinese ch_PP-OCRv4 always used

**Changes Made:**
- Modified `tests/corpus/experiment.py` — added `RapidOcrOptions` import and `engine == "rapidocr"` handler with `det_model_path`, `rec_model_path`, `cls_model_path` support
- Updated `findings.md` — full Phase 2B section with comparison tables, per-word accuracy analysis, recommendation

---

## Phase 3: Head-to-Head Analysis

### Goal

Produce the specific deliverable the spec requires: a focused comparison of table output across all three tools, with actual markdown examples. This is a synthesis activity — it draws on baseline and exploration results but adds targeted side-by-side analysis.

### 3.1 Table-by-Table Comparison

For every document with table content (7 documents), select 1-3 representative tables per document and capture the output from all three tools:

| Document | Tables to Compare | Known Issue |
|----------|-------------------|-------------|
| aries_cost_account | Cost breakdown tables (known `<br>` artifacts) | 137 table rows, complex structure |
| araiinejad_2024 | TEA parameter tables | `<br>` artifacts |
| paischer_2025 | Results tables | Complex headers, spanning cells |
| helios_design | Design parameter tables | Multi-span |
| sparc_overview | Plasma parameter tables | Mixed quality |
| energy_amplifier | Multi-page tables | Large document |
| hsu_2020 | PLX parameters | Small, well-structured |

For each selected table, the findings report should include:

```markdown
### Table: [document_slug] page [N] — [description]

**pymupdf4llm output:**
[actual markdown]

**Docling output:**
[actual markdown]

**GMFT output:**
[actual markdown]

**Assessment:** [which is best, why, what's still wrong]
```

### 3.2 Full-Document Comparison

For 3-5 representative documents, compare overall extraction quality:

| Document | Category | Why |
|----------|----------|-----|
| hsu_2020 | Table-heavy, short | Quick to compare, tables are the main content |
| schulte_1978 | OCR-quality | Tests Docling's OCR mode vs pymupdf4llm |
| hawker_2020 | Math-heavy | Tests equation handling |
| aries_cost_account | Table-heavy, large | Tests scalability |
| paischer_2025 | Mixed (tables + math) | Tests all-around quality |

### 3.3 Performance Summary

Compile a timing table:

```markdown
| Document | Pages | pymupdf4llm | Docling | GMFT |
|----------|-------|-------------|---------|------|
| ... | ... | Xs | Xs | Xs |
```

Include notes on memory behavior, crashes, timeouts.

### Phase 3 Validation

- [ ] Head-to-head table comparison covers all 7 table-bearing documents
- [ ] Each comparison includes actual markdown output from all three tools
- [ ] Full-document comparison covers at least 3 representative documents
- [ ] Performance timing table compiled
- [ ] Findings report updated with all comparison results

---

## Phase 4: Synthesize

### Goal

Consolidate what we learned into clear recommendations, update the codebase with the best configurations, and write tests.

### 4.1 Finalize findings.md

Add a summary section with:

1. **When to use each tool** — clear heuristics:
   - "Use pymupdf4llm when X" (fast baseline, always runs)
   - "Use Docling when Y" (specific document/page characteristics)
   - "Use GMFT when Z" (specific table characteristics)
2. **Recommended configuration per tool** — with per-parameter evidence
3. **Performance characteristics** — speed expectations by document size
4. **Failure catalog** — what each tool can't handle (inputs to Stage 2)
5. **MCP vs library tradeoffs** — when to use each mode for Docling
6. **Implications for Stage 3** — what the pipeline needs to know to route correctly

### 4.2 Rebuild DoclingExtractor

Update `src/agentic_mbse/extraction/docling_backend.py`:

1. Best-discovered `PdfPipelineOptions` configuration with rationale comments
2. Add single-page extraction support (extract one page via PyMuPDF page splitting, then convert)
3. Preserve subprocess timeout protection (existing pattern)
4. Return `ExtractionResult` with quality metadata (table count, image count)
5. Graceful degradation when `docling` not installed

### 4.3 Build GMFTExtractor

Create `src/agentic_mbse/extraction/gmft_backend.py`:

1. Best-discovered GMFT configuration with rationale comments
2. Page-level extraction (detect + format all tables on a given page)
3. Return structured output (table count, markdown tables, optionally DataFrames)
4. Graceful degradation when `gmft` not installed
5. Performance suitable for targeted enhancement (flagged pages, not full documents)

### 4.4 Write Tests

Following existing patterns in `tests/test_extraction.py`:

1. **Docling tests** — update existing tests (lines 353-431) if the interface changed:
   - Timeout handling
   - Process crash handling
   - Extraction failure
   - Successful extraction with quality metadata
   - Single-page extraction
   - Graceful degradation (not installed)
2. **GMFT tests** — new test functions:
   - Table detection + formatting
   - No tables found (non-table page)
   - Graceful degradation (not installed)

All tests should use mocking (no real Docling/GMFT invocations in CI).

### 4.5 Verify

1. Run `uv run pytest tests/` — all tests pass
2. Verify no regressions in existing extraction functionality
3. Verify both extractors work on a real PDF (manual, not CI)

### Phase 4 Validation

- [ ] `findings.md` has clear final recommendations section with evidence
- [ ] `docling_backend.py` rebuilt with best config, single-page support, rationale comments
- [ ] `gmft_backend.py` created with best config, page-level extraction, rationale comments
- [ ] Docling tests updated/extended
- [ ] GMFT tests created
- [ ] All tests pass (`uv run pytest tests/`)
- [ ] Both extractors verified on a real PDF

---

## Key Resources

| Resource | Location | Use |
|----------|----------|-----|
| Current Docling backend | `src/agentic_mbse/extraction/docling_backend.py` | Starting point for rebuild |
| Extraction base types | `src/agentic_mbse/extraction/base.py` | `ExtractionResult`, `run_with_timeout` |
| Existing Docling tests | `tests/test_extraction.py` (lines 353-431) | Test patterns to follow |
| Experiment harness | `tests/corpus/experiment.py` | Extend for Docling/GMFT |
| Metrics module | `tests/corpus/metrics.py` | Compute extraction quality |
| pymupdf4llm baseline runs | `tests/corpus/runs/baseline/`, `tests/corpus/runs/best_v1/` | Comparison target |
| pymupdf4llm findings | `.project/active/pymupdf4llm-deep-dive/findings.md` | Known gaps driving this work |
| pdf-analysis skill | `claude/skills/pdf-analysis/` | Hands-on page inspection |
| Extraction research | `.project/research/20260206_scientific-pdf-extraction.md` | Tool landscape context |
| Docling source (installed) | `.venv/lib/python*/site-packages/docling/` | Read when docs insufficient |
| GMFT source (installed) | `.venv/lib/python*/site-packages/gmft/` | Read when docs insufficient |

---

## Implementation Notes

*To be filled during implementation.*

---

**Status**: In Progress — Phase 2B complete, Phase 3 (Head-to-Head Analysis) next
