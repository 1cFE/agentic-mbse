# Findings: Docling & GMFT Deep-Dive (Stage 1C)

**Status:** Phase 2 — Exploration Complete
**Last Updated:** 2026-02-22

---

## Docling Baseline Observations

### Runs Completed

| Run | Config | Docs Completed | Docs Timed Out |
|-----|--------|---------------|----------------|
| `docling_baseline` | defaults (do_ocr=True) | 5/15 | 10/15 |
| `docling_no_ocr` | do_ocr=False | 4/15 | 11/15 (run stopped early) |
| `docling_aries_p8` | page 8 only, no OCR | 1/1 | — |
| `docling_paischer_p8` | page 8 only, no OCR | 1/1 | — |
| `docling_schulte_ocr` | page 3, OCR+force_full_page | 1/1 | — |
| `docling_sparc_p1_5` | pages 1-5, no OCR | 1/1 | — |

### Performance: Docling vs pymupdf4llm

| Document | Pages | pymupdf4llm | Docling (OCR) | Docling (no OCR) | GMFT |
|----------|-------|-------------|---------------|------------------|------|
| hsu_2020 | 9 | 1.3s | 15.1s | 11.7s | 1.8s |
| hawker_2020 | 14 | 5.2s | 18.5s | 16.6s | 1.7s |
| tajima | 16 | 7.3s | 65.6s | — | 1.8s |
| seo_2024 | 19 | 18.0s | 25.8s | 12.0s | 2.1s |
| sparc_overview | 25 | 14.9s | **TIMEOUT** | **TIMEOUT** | 2.7s |
| woodruff_2026 | 25 | 6.3s | **TIMEOUT** | **TIMEOUT** | 2.3s |
| paischer_2025 | 24 | 24.8s | **TIMEOUT** | **TIMEOUT** | 2.4s |
| hansen_2025 | 28 | 3.2s | 26.1s | 11.3s | 2.4s |
| helios_design | 30 | 6.3s | **TIMEOUT** | **TIMEOUT** | 2.9s |
| delene_2001 | 39 | 4.5s | **TIMEOUT** | **TIMEOUT** | 4.8s |
| araiinejad_2024 | 50 | 10.5s | **TIMEOUT** | **TIMEOUT** | 6.1s |
| aries_cost_account | 100 | 53.8s | **TIMEOUT** | **TIMEOUT** | 10.1s |
| energy_amplifier | 241 | 791.7s | **TIMEOUT** | **TIMEOUT** | 32.2s |

**Key observation:** Timeout is at 300s. The pattern is NOT purely page count — hansen_2025 (28pp) completes in 26s while helios_design (30pp) and sparc_overview (25pp) time out. The driver is content complexity: documents with many tables, figures, or diagrams trigger TableFormer per detection, dramatically increasing processing time. hansen_2025 is text-heavy with minimal tabular content; sparc_overview has complex figures and tables.

**Single-page extraction works well:** 7-9 seconds per page regardless of document size. This is the viable path for Docling in a pipeline.

### Per-Document Quality Notes

#### hsu_2020 (9pp, tables)
- **Headings:** 6 detected (vs 4 pymupdf4llm) — Docling finds headings pymupdf4llm misses
- **Tables:** Clean pipe tables, no `<br>` artifacts. Proper column headers ("Average", "Low", "High") instead of pymupdf4llm's generic "Col1", "Col5"
- **Text flow:** Clean paragraphs, no page number artifacts. References have proper markdown links
- **Images:** Replaced with `<!-- image -->` placeholder (expected, `generate_picture_images=True` extracts separately)
- **Overall:** Docling output is clearly better than pymupdf4llm for this document

#### hawker_2020 (14pp, math-heavy)
- **Headings:** 17 detected (vs 14 pymupdf4llm, vs 5-10 expected) — some over-detection
- **Tables:** Table 1 (LCOE comparison) has dot-leader artifacts (". . . . .") same as pymupdf4llm — these are in the PDF content itself
- **Math:** `<!-- formula-not-decoded -->` — Docling DETECTS formulas but doesn't decode them with default config. **Must test `do_formula_enrichment=True`**
- **Math text:** Garbled spacing ("B 0 = 12 . 2 T" should be "B₀ = 12.2 T") — same issue as pymupdf4llm
- **Overall:** Slightly better structure, but math handling needs formula enrichment enabled

#### tajima (16pp, text-heavy, older formatting)
- **Headings:** 21 detected (vs 10 pymupdf4llm) — significant improvement in heading detection on older-format docs
- **Tables:** 27 table rows detected (pymupdf4llm: 0) — Docling is finding tabular content pymupdf4llm misses
- **Time:** 65.6s (with OCR) — 9x slower than pymupdf4llm's 7.3s. OCR step adds significant overhead even though this is born-digital

#### hansen_2025 (28pp, math-heavy, text-heavy)
- **Headings:** 18 detected (vs 0 pymupdf4llm!) — pymupdf4llm completely fails on heading detection for this document, Docling succeeds
- **Tables:** 15 rows (vs 0 pymupdf4llm) — Docling finds tables pymupdf4llm misses
- **Math symbols:** 11 detected (similar to pymupdf4llm's 12)
- **OCR vs no-OCR:** 26.1s vs 11.3s — OCR doubles extraction time on born-digital docs (still runs, just finds nothing)
- **Overall:** Major Docling win on heading detection for this document format

#### seo_2024 (19pp, figure-heavy, math-heavy)
- **Headings:** 24 detected (vs 11 pymupdf4llm) — better heading detection
- **Tables:** 0 rows (vs 14 pymupdf4llm) — pymupdf4llm's 14 rows may be false positives (detecting figure captions/labels as tables)
- **Figures:** 57 figure references (same as pymupdf4llm)
- **Overall:** Better heading detection, fewer false table detections

#### aries_cost_account page 8 (single-page extraction)
- **Table:** Clean cost account table with proper Account/Title/LSA columns
- **Spanning cells:** Hierarchical indentation preserved (CAS 21 sub-items, CAS 22 sub-items)
- **No `<br>` artifacts** — the 71 artifacts in pymupdf4llm are eliminated
- **Prose after table:** Clean, well-structured paragraphs
- **Time:** 8.2s for 1 page — viable for targeted extraction

#### paischer_2025 page 8 (single-page extraction)
- **Table:** Structure preserved but **spanning-row headers duplicated across ALL columns** — "SOTA Reduced Numerical modelling" and "Classical Regression Techniques" appear in every cell of those rows instead of being section headers
- **Data cells:** Clean, proper ± notation, correct numeric values
- **GMFT is better here** — properly handles section headers without duplication
- **Time:** 8.3s for 1 page

#### schulte_1978 page 3 (OCR mode)
- **OCR quality: TERRIBLE**
  - "FUSIOi4" → should be "FUSION"
  - "STAidDARD" → should be "STANDARD"
  - "Wi 11 ke" → should be "Willke"
  - "~ormerly" → should be "formerly"
  - "Battel le" → should be "Battelle"
  - "Pub1 ic" → should be "Public"
- **Root cause:** RapidOCR uses Chinese-trained PaddleOCR model by default. Completely wrong for 1978 English technical documents
- **Must test:** EasyOCR or Tesseract backend for English text
- **Only 464 chars extracted** from a full page — extremely sparse

#### sparc_overview pages 1-5 (no OCR)
- **Headings:** 3 detected on 5 pages — "Overview of the SPARC tokamak", "1. Introduction", "2. SPARC and the high-field path"
- **Author affiliations:** Wrapped in code fences (``` ```) — incorrect categorization as code
- **Math text:** Same space garbling as pymupdf4llm ("B 0 = 12 . 2 T", "R 0 = 1 . 85 m")
- **HTML entities:** `&gt;` instead of `>` in equations ("Q &gt; 2" instead of "Q > 2")
- **Text quality:** Clean paragraphs, good flow
- **Time:** 7.7s for 5 pages — viable for targeted extraction

### Docling Summary

**Strengths:**
1. Better heading detection than pymupdf4llm (18 vs 0 on hansen_2025, 21 vs 10 on tajima)
2. Clean table output — no `<br>` artifacts
3. Single-page extraction works (7-9s per page)
4. Detects formula locations (even without enrichment)

**Weaknesses:**
1. **Full-document extraction is impractical** — times out on 10/15 corpus documents at 300s, even without OCR
2. Spanning-row headers duplicated across all columns in complex tables
3. OCR quality is terrible with default RapidOCR backend
4. Math text has same space garbling as pymupdf4llm
5. 3-12x slower than pymupdf4llm even when it completes
6. Author affiliations mis-categorized as code blocks
7. HTML entities in output (`&gt;` instead of `>`)

---

## GMFT Baseline Observations

### Run Summary

All 15 documents processed in total 76s. Zero failures.

| Document | Pages | Time | Tables Detected | Table Rows | `<br>` Count |
|----------|-------|------|----------------|------------|-------------|
| hawker_2020 | 14 | 1.7s | — | 40 | 0 |
| aries_cost_account | 100 | 10.1s | — | 175 | 0 |
| helios_design | 30 | 2.9s | — | 26 | 0 |
| hsu_2020 | 9 | 1.8s | — | 88 | 0 |
| delene_2001 | 39 | 4.8s | — | 202 | 0 |
| sparc_overview | 25 | 2.7s | — | 39 | 0 |
| energy_amplifier | 241 | 32.2s | — | 798 | 0 |
| woodruff_2026 | 25 | 2.3s | — | 194 | 0 |
| araiinejad_2024 | 50 | 6.1s | — | 303 | 0 |
| paischer_2025 | 24 | 2.4s | — | 52 | 0 |
| hansen_2025 | 28 | 2.4s | — | 42 | 0 |
| seo_2024 | 19 | 2.1s | — | 0 | 0 |
| woodruff_2026b | 25 | 2.4s | — | 194 | 0 |
| tajima | 16 | 1.8s | — | 0 | 0 |
| schulte_1978 | 10 | 1.1s | — | 3 | 0 |

### Per-Document Quality Notes

#### hsu_2020 (tables)
- **6 tables detected** including cover page (Table 1) and cost data tables (Tables 2, 5, 6)
- Tables 2 and 5 (system params, capital costs): **Excellent** — clean pipe tables, proper numeric alignment, no artifacts
- Table 6 (COE): Clean, subscripts like C_AC, C_SCR rendered as CAC, CSCR (acceptable)
- Table 1 (cover page): Detected cover info as table — bonus structure but unexpected
- **Table 3 (page 6)**: Garbage — detected CAS description text as a single-row table with mangled multi-column content
- **Table 4 (page 7)**: Same problem — cost category descriptions mis-detected as table
- **Overall:** Excellent on real data tables, some false positives on text-heavy structured content

#### aries_cost_account (tables, 100pp)
- **175 table rows** detected across 100 pages (vs 137 pymupdf4llm with `<br>` artifacts)
- Table 1 (page 4, IPD deflator): **Perfect** — clean Year/IPD numeric table
- Table 2 (page 5, account structure): Readable but long text cells get concatenated within cells
- Table 3+ (page 8+, LSA factors): Clean multi-column numeric tables
- **Zero `<br>` artifacts** (vs 71 in pymupdf4llm)
- **10.1s for 100 pages** — extremely fast

#### paischer_2025 (tables + math, 24pp)
- **4 tables** detected across 24 pages
- Table 1 (page 7, method comparison): Clean, checkmarks (✗) preserved, proper structure
- Table 2 (page 8, results): Complex multi-level header. GMFT handles section headers properly (not duplicated like Docling). Some `\n` in column headers ("f \nOOD (↑)")
- Table 3 (page 10, scalability): Clean, proper units and metrics
- Table 4 (page 23, ablation): Clean, Greek symbols (ϕ) preserved
- **Zero `<br>` artifacts** (vs 62 in pymupdf4llm)
- **Math symbols preserved:** ✗, ↑, ↓, ±, ϕ, Q̄

#### hawker_2020 (non-table doc)
- **40 table rows detected** on a document marked as `has_tables: false`
- Detected 3 tables containing LCOE comparison data — these ARE tables, just small ones
- **Severe dot-leader artifacts** — the PDF uses visual dot leaders for alignment, and GMFT captures them literally: "........................................ onshore wind" with fields full of dots
- Tables are technically correct but extremely polluted with alignment dots

#### delene_2001 (non-table doc)
- **202 table rows** detected — but this is almost entirely Table of Contents, List of Figures, and List of Tables
- These ARE visually tabular content but not useful data tables
- Some legitimate data tables detected in later pages
- Highlights need for **confidence threshold tuning** or **TOC detection filtering**

#### schulte_1978 (OCR-quality doc)
- **3 table rows** — minimal detection on a low-quality scanned document
- Table 1 (page 3): Title page info detected as table. OCR errors preserved from text layer ("FUSIOi4", "~ormerly")
- GMFT doesn't do OCR — it reads existing (corrupted) text layer

#### seo_2024, tajima (text-only docs)
- **0 tables detected** on both — correct! No false positives on pure text documents

### GMFT Summary

**Strengths:**
1. **Blazing fast** — 76s for entire 15-doc corpus (vs pymupdf4llm's ~950s, Docling's hours of timeouts)
2. **Zero `<br>` artifacts** — completely eliminates the 333-artifact problem from pymupdf4llm
3. Clean DataFrame-based output — always proper pipe tables
4. **No timeouts or crashes** — processes 241-page energy_amplifier in 32s
5. Good handling of complex multi-level headers (paischer_2025 Table 2)
6. Mathematical symbols preserved (checkmarks, arrows, subscripts, Greek)
7. High detection accuracy on actual data tables

**Weaknesses:**
1. **Tables only** — no text, headings, or full-document extraction
2. **False positives on structured text**: TOC, List of Figures, figure captions detected as tables (delene_2001: 202 rows from non-table doc)
3. **Dot-leader artifacts**: Tables with visual alignment dots get polluted (hawker_2020)
4. **`\n` in column headers**: Multi-line headers encoded with literal newlines
5. Column header rows sometimes concatenated vertically when `enable_multi_header=False`
6. No OCR capability — reads existing (possibly corrupted) text layer

---

## Initial Comparison: Where Each Tool Adds Value

### Table Extraction

| Aspect | pymupdf4llm | Docling | GMFT |
|--------|-------------|---------|------|
| Speed | Fast (1-18s most docs) | Very slow (timeouts on >50% docs) | Fastest (1-32s all docs) |
| `<br>` artifacts | 333 total | 0 | 0 |
| Table structure | OK for simple tables | Good, but spanning rows duplicated | Best for complex tables |
| Numeric alignment | Good | Good | Excellent (right-aligned) |
| Column headers | Generic ("Col1") sometimes | Proper names | Proper names |
| Spanning cells | Lost → `<br>` | Duplicated across columns | Properly handled |

**Winner for table extraction: GMFT** — fast, clean, no artifacts, handles complex tables well.

### Heading Detection

| Document | pymupdf4llm | Docling |
|----------|-------------|---------|
| hansen_2025 | **0** | 18 |
| tajima | 10 | 21 |
| hawker_2020 | 14 | 17 |
| seo_2024 | 11 | 24 |
| hsu_2020 | 4 | 6 |

**Winner for heading detection: Docling** — dramatically better, especially on documents where pymupdf4llm fails completely (hansen_2025: 0 vs 18).

### Math Handling

**Phase 2 update:** `do_formula_enrichment=True` DOES produce LaTeX output. Quality varies by equation complexity:

| Equation Type | Quality | Example |
|---------------|---------|---------|
| Simple fractions | **Excellent** | `$$C _ { p } = \frac { \alpha P _ { e } } { Y _ { c } }$$` |
| Cases/piecewise | **Very good** | `$$C _ { i } = \begin{cases} ... \end{cases}$$` — proper `\begin{cases}` with text annotations |
| Sums/fractions | **Good** | `$$E _ { i } = \frac { ( 3 6 5 \times 2 4 \times 6 0 \times 6 0 ) } { ... }$$` — readable but over-spaced |
| Complex with text | **Poor** | LCOE equation: garbled `\intertext{}` content, spaces in variable names ("L C O" for "LCOE") |

**Characteristics:**
- All formulas have character-level spacing (`C _ { p }` instead of `C_p`) — post-processable with regex
- Heavy performance overhead: hawker_2020 (14pp) times out at 300s vs 18.5s without formula enrichment
- Single-page extraction viable: 22.1s for 3 pages (~7.4s/page) with formulas
- 21 `<!-- formula-not-decoded -->` markers in baseline → 4 `$$...$$` LaTeX blocks on 3 pages

**Conclusion:** Formula enrichment produces usable LaTeX for simple-to-medium equations. Complex equations with surrounding text get garbled. Must be used in single-page mode due to performance overhead. Post-processing to clean spacing is needed but feasible.

### OCR (schulte_1978)

**Phase 2 update — critical findings:**

1. The "OCR errors" originally observed are from the **PDF's own corrupt embedded text layer**, not from Docling's OCR processing. Running with `do_ocr=False` produces identical output to the default OCR (which was a no-op because no OCR engines were installed).

2. After installing EasyOCR, re-testing with `force_full_page_ocr=True` produced **dramatically better results**:

| Aspect | Corrupt PDF Layer | EasyOCR |
|--------|-------------------|---------|
| "FUSIOi4" | garbled | "FUSION" |
| "o f  t h i s" | spaced chars | "of this" |
| "conirnon s a t i s f a c t i o n" | garbled | "common satisfaction" |
| "revisc?d wittlout" | garbled | "revised without" |
| "commun i ty" | split | "community" |
| Total chars (full doc) | 7,137 (corrupt layer) | 50,752 (OCR'd) |

3. **schulte_1978 structure:** 10 PDF pages, 7 with content, 3 blank backs (duplex scan of 1978 doc). All blank pages correctly return 0 chars.

4. **Remaining EasyOCR errors** are minor l/I/T substitutions: "Battele" (Battelle), "FormerIy" (Formerly), "RichTand" (Richland), "ma intain" (maintain). Much better than the completely illegible corrupt text layer.

5. **TOC table explosion:** Docling's table structure model creates massive tables from the TOC page, duplicating content across many columns (~48K of the 50K chars are inflated TOC). Body text quality is excellent.

6. **Performance:** 43.8s for 10 pages (full doc), 11-15s per single page. Viable for targeted use.

**Recommended EasyOCR config:**
```python
EasyOcrOptions(lang=["en"], force_full_page_ocr=True, confidence_threshold=0.5)
```

---

## Phase 2 Answers (Exploration Results)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| 1 | Does `do_formula_enrichment=True` produce LaTeX? | **Yes**, quality varies by complexity | `docling_formula_p2_4`: 4 LaTeX equations on 3 pages, simple=excellent, complex=garbled |
| 2 | Does EasyOCR/Tesseract improve schulte_1978? | **Yes, dramatically** — EasyOCR produces readable English text | `docling_easyocr_schulte_full`: 50,752 chars (vs 7,137 corrupt), most words correct, minor l/I/T substitution errors |
| 3 | Can per-page Docling replace full-document? | **Partially** — text/tables good, headings degraded | `docling_hsu_p1-p9`: 14,931 chars (vs 14,947), but only 3 headings (vs 6) |
| 4 | Can GMFT false positives be filtered by threshold? | **No** — threshold 0.95 loses 12-30% real tables | `gmft_threshold_95`: aries lost 52 tables (-30%), energy_amplifier lost 103 (-13%) |
| 5 | Does `enable_multi_header=True` improve GMFT? | **No** — worse for markdown (tuple format) | `gmft_multiheader`: headers become `(nan, 'Method')` instead of `Method` |
| 6 | Does `semantic_spanning_cells=True` help? | **Marginal** — fills some hierarchical codes, occasional errors | `gmft_spanning`: aries fills CAS codes but also introduces "Or," errors |
| 7 | Does `TableFormerMode.FAST` reduce timeouts? | **No** — only 15-35% faster, same docs time out | `docling_fast`: hsu 9.6s (vs 15.1s), but sparc/paischer/helios still timeout |

---

## Experiment Log

### docling_baseline (2026-02-22)
- **Config:** defaults (do_ocr=True, do_table_structure=True)
- **Result:** 5/15 completed. hawker_2020 (18.5s), hsu_2020 (15.1s), tajima (65.6s), hansen_2025 (26.1s), seo_2024 (25.8s). All others timed out at 300s.
- **Finding:** OCR adds ~2-10s overhead on born-digital docs. Full-document mode impractical for most corpus docs.

### docling_no_ocr (2026-02-22)
- **Config:** do_ocr=False
- **Result:** 4/15 completed (run stopped early). hawker_2020 (16.6s), hsu_2020 (11.7s), hansen_2025 (11.3s), seo_2024 (12.0s). Same docs time out.
- **Finding:** OCR is NOT the bottleneck. Layout model + TableFormer processing is the performance driver.

### docling_aries_p8 (2026-02-22)
- **Config:** page 8 only, do_ocr=False
- **Result:** 8.2s, 4,805 chars, 1 heading, 16 table rows
- **Finding:** Single-page extraction works perfectly. Clean cost table with proper structure.

### docling_paischer_p8 (2026-02-22)
- **Config:** page 8 only, do_ocr=False
- **Result:** 8.3s, 8,088 chars, 0 headings, 18 table rows
- **Finding:** Spanning-row headers duplicated across all columns. GMFT handles this better.

### docling_schulte_ocr (2026-02-22)
- **Config:** page 3 only, do_ocr=True, force_full_page_ocr=True
- **Result:** 9.0s, 464 chars
- **Finding:** OCR quality is terrible with RapidOCR Chinese model. "FUSIOi4", "STAidDARD", "Wi 11 ke".

### docling_sparc_p1_5 (2026-02-22)
- **Config:** pages 1-5, do_ocr=False
- **Result:** 7.7s, 18,188 chars, 3 headings, 0 tables
- **Finding:** Good heading detection. Math text garbled same as pymupdf4llm. Author list in code fences.

### gmft_baseline (2026-02-22)
- **Config:** defaults (AutoTableDetector + AutoTableFormatter, all defaults)
- **Result:** 15/15 completed. 76s total. Zero `<br>` artifacts anywhere.
- **Finding:** Consistently fast, clean table output. False positives on TOC/list pages. Dot-leader artifacts on tables with visual separators.

---

### Phase 2 Experiments

### docling_formula (2026-02-22)
- **Config:** do_formula_enrichment=True, do_ocr=False. hawker_2020 + hansen_2025.
- **Result:** hawker_2020 TIMEOUT at 300s. hansen_2025 completed in 15.8s (identical metrics to baseline — no formulas in this document).
- **Finding:** Formula enrichment adds significant overhead. hansen_2025 has no inline formulas to decode.

### docling_formula_p2_4 (2026-02-22)
- **Config:** do_formula_enrichment=True, do_ocr=False, pages 2-4. hawker_2020 only.
- **Result:** 22.1s, 14,975 chars, 3 headings, 24 table rows, 5 math symbols.
- **Finding:** **Formula enrichment works!** 4 LaTeX equations produced on 3 pages. Quality: simple equations excellent (`C_p = α P_e / Y_c`), complex equations garbled (`\intertext{}` content). All have character-level spacing (`C _ { p }` not `C_p`). See Math Handling section for full analysis.

### gmft_multiheader (2026-02-22)
- **Config:** enable_multi_header=True. All 15 docs.
- **Result:** 15/15 completed. Same table counts. paischer_2025 +15.3% chars.
- **Finding:** **Worse for markdown.** Column headers become raw Python tuples: `(nan, 'Method')` instead of `Method`. Designed for DataFrame analysis, not markdown display. Default (False) is better for our use case.

### gmft_spanning (2026-02-22)
- **Config:** semantic_spanning_cells=True. 5 table-heavy docs.
- **Result:** All completed. Minimal metric changes.
- **Finding:** **Marginal improvement.** Fills hierarchical account codes in aries_cost_account (empty cells → "20 21", "22", "26"). But occasional errors: "Or," instead of correct code. Header merging changes behavior on multi-row headers. Not a clear win.

### docling_fast (2026-02-22)
- **Config:** TableFormerMode.FAST, do_ocr=False. 5 docs (mix of completing and timing-out).
- **Result:** hawker_2020 17.3s (-1.2s), hsu_2020 9.6s (-5.5s). sparc_overview, paischer_2025, helios_design still TIMEOUT.
- **Finding:** **15-35% speedup, same quality** (hsu_2020 output identical). Does NOT solve the timeout problem. Layout model (DocLayNet) is the bottleneck, not TableFormer mode.

### docling_schulte_noocr (2026-02-22)
- **Config:** do_ocr=False, page 3 only. schulte_1978.
- **Result:** 6.8s, 464 chars — **identical output to do_ocr=True run**.
- **Finding:** **OCR is a no-op.** No OCR engines installed (rapidocr, easyocr, pytesseract all missing). Corrupt text comes from PDF's embedded text layer, not from Docling's OCR. To fix schulte_1978, must install EasyOCR + force_full_page_ocr=True.

### gmft_threshold_95 (2026-02-22)
- **Config:** detector_base_threshold=0.95. 5 docs.
- **Result:** aries_cost_account lost 52 tables (-30%), energy_amplifier lost 103 (-13%). hawker_2020 unchanged.
- **Finding:** **Too aggressive.** Default 0.9 is well-calibrated. Higher threshold loses real tables. False positives (TOC, lists) need post-processing, not threshold tuning.

### docling_hsu_p1-p9 (2026-02-22)
- **Config:** do_ocr=False, individual page extraction (9 runs). hsu_2020.
- **Result:** 6.7-8.9s per page (64.4s total vs 15.1s full-doc). Concatenated: 14,931 chars, 3 headings.
- **Finding:** **Per-page viable for text/tables but loses headings.** Full-doc: 14,947 chars, 6 headings. Per-page: 14,931 chars, 3 headings. 4.3x slower (repeated model init). Missing blank lines between pages cause heading run-on. In a pipeline where pymupdf4llm provides headings, per-page Docling is acceptable.

### docling_easyocr_schulte_p3 (2026-02-22)
- **Config:** EasyOCR, lang=["en"], force_full_page_ocr=True, page 3 only. schulte_1978.
- **Result:** 15.2s, 371 chars, 0 headings (first run — model download included).
- **Finding:** **Dramatic OCR quality improvement.** "FUSION" (not "FUSIOi4"), "STANDARD" (not "STAidDARD"), "Willke" (not "Wi 11 ke"). Minor l/I/T substitution errors remain ("Battele", "FormerIy", "RichTand").

### docling_easyocr_schulte_full (2026-02-22)
- **Config:** EasyOCR, lang=["en"], force_full_page_ocr=True, full document. schulte_1978.
- **Result:** 43.8s, 50,752 chars, 4 headings, 48 table rows.
- **Finding:** 7x more text than corrupt text layer (50K vs 7K chars). Body text (foreword, abstract) reads cleanly. TOC page explodes into massive table with duplicated columns (~48K of 50K). Blank backs (pages 4,6,8) correctly return 0 chars. **EasyOCR is the answer for OCR-quality documents.**

### docling_easyocr_schulte_p5 (2026-02-22)
- **Config:** EasyOCR, lang=["en"], force_full_page_ocr=True, page 5 only. schulte_1978.
- **Result:** 12.1s, 587 chars, 1 heading (Foreword).
- **Finding:** Body text quality confirmed excellent. "In preparation of this document..." reads cleanly vs "I n  preparation o f  t h i s  document" from corrupt layer.
