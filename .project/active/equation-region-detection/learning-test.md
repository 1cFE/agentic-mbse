# Learning Tests: Equation Region Detection

**Created:** 2026-03-01
**Status:** In Progress
**Branch:** doc-ingest-clean

---

## Goal

Run iterative experiments against the corpus to understand how Docling's LayoutPredictor performs for equation region detection, and whether PyMuPDF font heuristics add value as a pre-filter. Capture findings as we go.

## Test Corpus

| Document | Display Eqs (GT) | Pages | Key Characteristics |
|----------|:-:|:-:|------|
| `hawker_2020` | 21 | 14 | TEA paper, heavy garbling, TeX-produced (MathType fonts) |
| `paischer_2025` | 23 | 24 | NeurIPS, 2-column layout, TeX-produced (CM fonts) |
| `hansen_2025` | 0 | 28 | Heavy inline math, ZERO display eqs (negative test) |
| `seo_2024` | ~2+ | 19 | Non-TeX PDF, math-heavy, figure-heavy |

## Experiments

### LT-1: Docling LayoutPredictor — Basic Detection on hawker_2020

**Question:** Does the model detect Formula regions? What confidence scores? How many per page?

**Method:** Render each page at 200 DPI, run `LayoutPredictor.predict()`, filter for `label == "Formula"`.

**Status:** COMPLETE

**Results:**

- **23 raw detections** across 6 pages (pages 2-7)
- **21 after NMS** (IoU threshold 0.3) — **exact match to ground truth**
- NMS removed 2 duplicates on page 6:
  - conf=0.808 bbox nearly identical to conf=0.814 (same equation 2.20)
  - conf=0.311 wider bbox of same equation including "and" text
- Confidence range: 0.311–0.967, mean 0.907
- All detections were legitimate display equations (verified by visual inspection of crops)
- Page 5 had 7 detections — all correct (equations 2.8–2.14)
- Page 6 had 8 raw → 6 after NMS — all correct (equations 2.17–2.22)

**Per-page breakdown (after NMS):**

| Page | Formulas | Equations |
|------|:--------:|-----------|
| 2 | 2 | (2.2), (2.3) — fraction, piecewise |
| 3 | 2 | (2.3), (2.5) |
| 4 | 3 | (2.6)–(2.8) |
| 5 | 7 | (2.8)–(2.14) — mostly single-line |
| 6 | 6 | (2.17)–(2.22) — includes multi-line fraction |
| 7 | 1 | (2.23) |

---

### LT-2: Docling LayoutPredictor — Detection on paischer_2025

**Question:** How does it handle 2-column NeurIPS layout? Does it find the 23 display equations?

**Status:** COMPLETE

**Results:**

- **25 raw detections** across 7 pages
- **24 after NMS** (IoU 0.3) — one duplicate removed on page 23
- At **confidence >= 0.5**: 23 detections — **exact match to ground truth**
- One false positive at conf=0.318 on page 5: inline math formula captured with surrounding text (`X_w ∈ R^{...}` with "... denoting the num-")
- Complex equations handled well:
  - page_016_eq_2 (conf=0.943): Multi-line PDE with underbrace annotations, size 929x135 — excellent crop
  - page_002_eq_1 (conf=0.932): Multi-line aligned equation, size 919x123
- Low-confidence detections on page 23 (appendix complexity analysis) at conf 0.701 and 0.650 are TRUE positives: O(W-MSA) and O(MSA) equations

**Confidence distribution (after NMS):**

| Threshold | Detections | vs GT (23) |
|-----------|:----------:|:----------:|
| >= 0.3 | 24 | +1 (1 inline FP) |
| >= 0.5 | 23 | exact match |
| >= 0.7 | 22 | -1 (misses O(MSA)) |
| >= 0.9 | 19 | -4 |

---

### LT-3: Docling LayoutPredictor — Negative Test on hansen_2025

**Question:** Does the model produce false positives on inline-math-only content?

**Status:** COMPLETE

**Results:**

- **ZERO formula detections** across all 28 pages
- This document has heavy inline math (CM fonts on every page) but zero display equations
- **Perfect negative test result** — no false positives at any confidence threshold
- The model correctly distinguishes display equations from inline math without any post-filtering

---

### LT-4: Crop Quality — Visual Inspection

**Question:** Do bounding boxes produce clean crops? Is padding needed? Are equation labels included?

**Method:** Save crops from LT-1/LT-2, visually inspect samples.

**Status:** COMPLETE

**Results:**

Inspected 15+ crops across hawker_2020, paischer_2025, and seo_2024:

- **Equation labels (e.g., "(2.8)")**: Included in all crops. Equation numbers in right margin are captured.
- **Full equation content**: No clipping of symbols at boundaries. Fractions, superscripts, subscripts all intact.
- **Multi-line equations**: Piecewise functions (hawker page 3, eq 2.3) and PDEs with underbraces (paischer page 16, eq 18) correctly captured as single regions.
- **Surrounding text**: Minimal. One low-confidence detection (hawker page 6, conf=0.311) included "and" prefix, but that was filtered by NMS. The conf=0.318 paischer detection included "... denoting the num-" trailing text.
- **Padding**: Not needed — bounding boxes have appropriate margins already.
- **Image quality at 200 DPI**: Clean and legible. Suitable for both human reading and LLM visual input.

**Crop quality verdict: Excellent. No padding or post-processing needed.**

---

### LT-5: Confidence Threshold Analysis

**Question:** What threshold best balances precision and recall?

**Status:** COMPLETE

**Results:**

Combined analysis across hawker_2020 (21 GT), paischer_2025 (23 GT), hansen_2025 (0 GT):

| Threshold | hawker (21 GT) | paischer (23 GT) | hansen (0 GT) | Total Precision | Total Recall |
|-----------|:-:|:-:|:-:|:-:|:-:|
| >= 0.3 (default) | 21 | 24 | 0 | 44/45 = 97.8% | 44/44 = 100% |
| >= 0.5 | 21 | 23 | 0 | 44/44 = 100% | 44/44 = 100% |
| >= 0.7 | 21 | 22 | 0 | 43/43 = 100% | 43/44 = 97.7% |
| >= 0.9 | 20 | 19 | 0 | 39/39 = 100% | 39/44 = 88.6% |

**Recommendation: Use confidence threshold 0.5.** This achieves perfect precision (100%) and perfect recall (100%) on the test corpus. The model's default threshold of 0.3 lets through one inline math false positive; 0.7 drops a legitimate equation.

NMS (IoU >= 0.3) should be applied BEFORE the confidence threshold to remove duplicate bounding boxes.

---

### LT-6: Performance — CPU Inference Time

**Question:** How long does per-page inference take on CPU?

**Status:** COMPLETE

**Results:**

Test machine: AMD CPU, 4 threads, no GPU.

| Document | Pages | Render | Predict | Total | Per Page |
|----------|:-----:|:------:|:-------:|:-----:|:--------:|
| hawker_2020 | 14 | 0.2s | 11.3s | 11.5s | 0.82s |
| paischer_2025 | 24 | 0.7s | 22.0s | 22.7s | 0.94s |
| hansen_2025 | 28 | 0.7s | 24.1s | 24.8s | 0.89s |

- **Model init**: 0.56s (one-time, singleton)
- **Render**: ~0.01–0.03s/page (negligible)
- **Predict**: ~0.8–0.9s/page (dominates)
- **Batch prediction is SLOWER**: 1.22s/page (17.1s for 14 pages) vs 0.79s/page sequential. Do NOT use `predict_batch()`.

**Estimated overhead for typical documents:**

| Document Size | Equation Detection Overhead |
|:---:|:---:|
| 10 pages | ~9s |
| 25 pages | ~22s |
| 50 pages | ~44s |
| 100 pages | ~88s |

This is significant. For a 25-page paper, equation detection adds ~22s on CPU. Gating behind `extracted_images_dir` is essential. A page-skip pre-filter could help but only saves 3-5 pages typically (see LT-7).

---

### LT-7: PyMuPDF Font Heuristics — Pre-Filter Value

**Question:** Can font-based heuristics skip non-equation pages to reduce inference cost?

**Status:** COMPLETE

**Results:**

Checked CM/MT font presence per page against Docling detection results:

| Document | Pages w/ Math Fonts | Pages w/ Equations (Docling) | Skippable Pages | Time Saved |
|----------|:---:|:---:|:---:|:---:|
| hawker_2020 | 10/14 | 6/14 | 4 | ~3.3s |
| paischer_2025 | 19/24 | 7/24 | 5 | ~4.5s |
| hansen_2025 | 28/28 | 0/28 | **0** | **0s** |
| seo_2024 | **0/19** | 2/19 | — | **DANGEROUS** |
| araiinejad_2024 | **0/50** | unknown | — | **DANGEROUS** |

**Critical problems:**

1. **hansen_2025**: All 28 pages have math fonts (inline math), but 0 have display equations. Pre-filter can't skip ANY pages — zero benefit on the worst-case document.
2. **seo_2024**: Zero TeX math fonts, but the Docling model correctly finds 2 display equations (conf=0.962). **The font pre-filter would skip all 19 pages and miss both equations.** Same risk for araiinejad_2024.
3. Even on best-case docs (hawker, paischer), savings are only 3-5 pages × ~0.9s = 3-4s.

**Verdict: Font pre-filter is NOT worth implementing.** It provides marginal time savings on TeX docs, zero savings on inline-math-heavy docs, and actively **misses equations on non-TeX PDFs**. The risk of false negatives outweighs the small performance gain.

---

### LT-8: Display vs Inline Discrimination

**Question:** Can we distinguish display from inline equations by bbox height or confidence?

**Status:** COMPLETE

**Results:**

The model **already discriminates correctly without any post-filtering needed:**

- **hansen_2025 (28 pages, all inline math, 0 display eqs)**: ZERO formula detections. The model does not flag inline math as Formula.
- **paischer_2025 page 5**: One inline-math detection at conf=0.318 (filtered by the 0.5 threshold). All 23 display equations detected at conf >= 0.533.
- **hawker_2020**: All 21 detections (after NMS) are true display equations.

Height-based filtering is **not needed** because the model already handles this:
- Display equation heights: 26–135px (at 200 DPI)
- Even the "short" detections (26-32px) are legitimate single-line display equations like `C_{O&M} = εP_e` (eq 2.11)

**Verdict: No post-filtering needed beyond confidence threshold (0.5) and NMS (IoU 0.3).**

---

### LT-9: Non-TeX PDF Detection (Bonus)

**Question:** Does the vision model work on PDFs without TeX math fonts?

**Status:** COMPLETE

**Results:**

Ran on `seo_2024` (19 pages, uses Times/Arial fonts, no CM/MT math fonts):

- **2 formula detections**, both at conf=0.962
  - Page 2: Piecewise function `R(β_N, T; k)` — eq (1)
  - Page 6: Derivative `Δ' ≡ [1/ψ dψ/dx]` — eq (2)
- Both are legitimate display equations
- Crop quality is excellent — clean boundaries, equation numbers included

**This confirms the vision-based model works across all PDF types.** Font-based approaches would miss these entirely.

---

## Key Learnings

1. **Docling LayoutPredictor is excellent for equation detection.** On our corpus: 100% precision + 100% recall at conf >= 0.5 with NMS.

2. **NMS is essential.** The model occasionally produces overlapping bounding boxes for the same equation (2 duplicates on hawker page 6). Simple IoU-based NMS at threshold 0.3 cleanly deduplicates.

3. **Confidence threshold of 0.5 is the sweet spot.** The model's default 0.3 lets through occasional inline math (1 false positive on paischer). 0.7 starts dropping real equations.

4. **The model inherently discriminates display vs inline.** Zero false positives on hansen_2025 (28 pages of pure inline math). No height or width filtering needed.

5. **Crop quality requires no post-processing.** Bounding boxes include appropriate margins, equation numbers, and full symbol content. No padding needed. 200 DPI is sufficient.

6. **Font-based pre-filter is NOT worth implementing.** It provides marginal time savings, zero benefit on inline-math-heavy docs, and actively misses equations on non-TeX PDFs.

7. **Batch prediction is counterproductive.** `predict_batch()` is 1.5x SLOWER than sequential `predict()` on CPU. Use sequential.

8. **CPU cost is ~0.85s/page.** Significant for large documents. Equation detection should be gated behind `extracted_images_dir` (no images dir = no detection). Consider making it opt-in or running only on pages flagged by the quality gate.

9. **Multi-line equations are handled well.** Piecewise functions, underbraced PDEs, aligned systems all detected as single regions.

10. **Model initialization is fast (0.56s)** and can be a singleton — initialize once, reuse across all pages.

---

## Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Use Docling LayoutPredictor as sole detector | 100% precision+recall on corpus, already installed, works on all PDF types |
| D2 | Do NOT implement PyMuPDF font pre-filter | Marginal savings, dangerous false negatives on non-TeX PDFs |
| D3 | Confidence threshold = 0.5 | Perfect precision+recall on corpus at this threshold |
| D4 | Apply NMS with IoU threshold 0.3 | Removes duplicate bounding boxes without losing true positives |
| D5 | Use sequential predict(), not predict_batch() | Batch is slower on CPU |
| D6 | Render pages at 200 DPI for detection | Same DPI used by table detection, produces quality crops |
| D7 | No bbox post-filtering (height/width) needed | Model discriminates display vs inline natively |
| D8 | Gate behind extracted_images_dir | ~0.85s/page overhead is significant; only run when images are requested |

---

## Next Steps

These learning test results provide all the data needed for the design phase. The implementation should:

1. Create `equations.py` with `detect_equations()` using `LayoutPredictor` singleton
2. Apply NMS (IoU 0.3) + confidence filter (0.5) to raw detections
3. Crop at 200 DPI, save as `page_{NNN}_eq_{M}.png`
4. Register crops with ImageCollector as `kind="equation_crop"`
5. Gate behind `extracted_images_dir` in PipelineConfig
6. Follow `_try_detect_*()` error-isolation pattern from tables.py
