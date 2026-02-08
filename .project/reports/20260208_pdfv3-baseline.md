# PDF Extraction v3 — Corpus Validation Baseline

**Date:** 2026-02-08
**Branch:** pdf-extract
**Pipeline version:** v2 + Workstream A bug fixes (commit 157d068)
**Evaluator:** Claude (automated extraction + manual spot-check)
**Epic:** `.project/backlog/epic_pdf-extraction-v3.md` — Item 1

---

## Executive Summary

Re-extracted all 12 corpus documents with the current pipeline (post-Workstream-A bug fixes) and recorded precise baseline metrics. The pipeline performs well on documents with numbered bold section headings (original 7-doc corpus) but fails systematically on documents with different heading conventions (new 5-doc corpus). Body text and image extraction remain strong across all document types.

**Key findings:**
- **Original 7 docs:** 7/7 produce non-empty INDEX; average grade B+
- **New 5 docs:** 1/5 produce non-empty INDEX (2244 only, with limited coverage); average grade C
- **Workstream A bug fixes:** Measurable improvement on 2243 (appendix regex tightening reduced false positives from 68 to ~35) and fusion-std (footer no longer promoted to header)
- **Structural quality remains the dominant gap** — body text, images, and tables are adequate or better

---

## 1. Automated Metrics

| ID | Short Name | Pages | Lines | Chars | Images | ## Hdrs | ### Hdrs | INDEX Sections | Pipe Table Lines | Backend |
|----|-----------|-------|-------|-------|--------|---------|----------|----------------|-----------------|---------|
| 2232 | Handley (Fusion Markets) | 17 | 1,608 | 81,818 | 6 | 7 | 8 | 15 | 0 | pymupdf |
| 2233 | Araiinejad (D-T MCF TEA) | 12 | 1,448 | 74,204 | 8 | 8 | 3 | 6 | 0 | pymupdf |
| 2235 | Global Fusion & AI | 30 | 1,268 | 100,065 | 2 | 6 | 18 | 27 | 293 | pymupdf |
| 2236 | Digital Twins | 66 | 3,281 | 278,932 | 31 | 19 | 15 | 62 | 309 | pymupdf |
| 2237 | LANL PJMIF | 60 | 2,910 | 180,620 | 19 | 31 | 15 | 47 | 117 | pymupdf |
| 2238 | Lampe CBFR | 40 | 2,228 | 83,083 | 40 | 20 | 0 | 5 | 0 | pymupdf |
| 2241 | Eester ICRH | 30 | 1,922 | 88,536 | 28 | 7 | 8 | 15 | 3 | pymupdf |
| 2243 | Rider Slides | 127 | 2,438 | 91,983 | 213 | 57 | 5 | 40 | 90 | pymupdf |
| 2244 | Helios Stellarator | 29 | 2,319 | 143,418 | 13 | 6 | 0 | 0 | 25 | pymupdf |
| safety | Fusion Safety Program | 14 | 407 | 11,318 | 27 | 0 | 0 | 0 | 0 | pymupdf |
| fusion-std | Fusion Standards | 4 | 542 | 18,322 | 4 | 0 | 0 | 0 | 0 | pymupdf |
| hazards | Afify Hazards | 8 | 480 | 35,278 | 3 | 0 | 0 | 0 | 0 | pymupdf |

**Notes:**
- All 12 documents extracted successfully (no extraction failures)
- 108 metric cells, no blanks
- All documents used pymupdf backend (Docling not attempted in this run)
- 2243 has 213 images because each slide is extracted as an image

---

## 2. Header Accuracy Spot-Check

For each document, headers were manually verified against the extracted markdown, checking the first 10 pages, last 5 pages, and known problem areas.

| ID | FP | FN | Pages Checked | Primary Issue |
|----|----|----|---------------|---------------|
| 2232 | 0 | 17 | 1-4, 15-17 | Italic sub-subsections (`_3.3.1 Title_`) not promoted to #### |
| 2233 | 6 | 23 | 1-6, 9-12 | Table content (COA account numbers) promoted to ##; real headers present but indexer missed some; italic subsections missed |
| 2235 | 0 | 5 | 1-10, 14-17, 27-30 | Missing sec 3.2, sec 4 parent heading, appendix headers |
| 2236 | 7 | 0 | 1-7, 59-66 | TOC entries duplicated as ## (6 entries); numbered list item promoted to ## |
| 2237 | 3 | 25+ | 1-14, 64-67 | TOC entries fused into single ## line (sections 10-12); ~20+ bold Cost Category sub-headings missed |
| 2238 | 7 | 11 | 1-18, 24-40 | Equation fragments promoted to ##; sections 5-6, Appendix, References missed; subsections A-H inconsistently handled |
| 2241 | 0 | 1 | 1-8, 25-30 | Near-perfect; only **Abstract** missed |
| 2243 | ~35 | ~50+ | 1-33, 58-62, 106-127 | Catastrophic: equation fragments/axis labels/table data promoted to ##; all ~127 slide titles missed |
| 2244 | 0 | 15 | 1-29 (all) | 6 top-level sections correct; all 15 italic subsections (`_3.1. Title_`) missed |
| safety | 0 | 12 | 1-14 (all) | Zero headers detected; all 12 slide titles in bold missed |
| fusion-std | 0 | 8 | 1-4 (all) | Zero headers detected; OCR scan, bold section headings missed; IAEA footer no longer promoted (bug fix A3) |
| hazards | 0 | 12 | 1-8 (all) | Zero headers detected; all section headings in bold missed |

**Patterns observed:**
1. **Italic subsection headers invisible** — affects 2232 (17 FN), 2233 (18 FN subsections), 2244 (15 FN). The pipeline only promotes `**bold**` patterns, not `_italic_` patterns.
2. **Unnumbered bold headers invisible** — affects safety (12 FN), fusion-std (8 FN), hazards (12 FN). `promote_bold_headers()` requires numbered prefixes (`\d+` or `[A-Z](\.\d+)*`).
3. **Table content as headers** — affects 2233 (6 FP) where COA account numbers look like section numbers.
4. **TOC entries duplicated** — affects 2236 (6 FP) where TOC page has numbered entries promoted to ##.
5. **Equation fragments as headers** — affects 2238 (3 FP), 2243 (~20+ FP) where mid-line equation text starts new lines.

---

## 3. Grading

### Rubric

| Grade | Meaning |
|-------|---------|
| A | Excellent — correct headers, clean body text, tables as pipes, usable INDEX |
| A- | Very good — minor issues (1-2 missed subsections, cosmetic artifacts) |
| B+ | Good — mostly correct structure, some false negatives, tables partially captured |
| B | Adequate — usable INDEX but incomplete, noticeable artifacts |
| B- | Passable — INDEX exists but sparse, body text usable, some structural gaps |
| C+ | Below average — few or no correct headers, body text mostly usable |
| C | Poor — no useful INDEX, significant body text issues |
| D+ | Bad — misleading INDEX (false positives), text artifacts throughout |
| D | Very bad — actively harmful INDEX, substantial content loss |

### Summary Table

| ID | Short Name | Structure | Tables | Body Text | Images | Overall | v3 Strategy Grade | v1 Eval Score | Delta |
|----|-----------|-----------|--------|-----------|--------|---------|-------------------|---------------|-------|
| 2232 | Handley | B+ | C | A- | A- | **B+** | B+ | 2.50/5 | +2 tiers vs v1 |
| 2233 | Araiinejad | B- | C | B+ | A- | **B** | B | 2.25/5 | +2 tiers vs v1 |
| 2235 | Global Fusion | B+ | B+ | B | A- | **B+** | B+ | 2.50/5 | +2 tiers vs v1 |
| 2236 | Digital Twins | B+ | B+ | A- | A | **B+** | B+ | 3.50/5 | +1 tier vs v1 |
| 2237 | LANL PJMIF | B | B | A- | A- | **B+** | B+ | 3.25/5 | +1 tier vs v1 |
| 2238 | Lampe CBFR | C | C | C+ | A- | **C+** | C+ | 2.00/5 | +1 tier vs v1 |
| 2241 | Eester ICRH | A- | C | B+ | A | **A-** | A- | 2.75/5 | +3 tiers vs v1 |
| 2243 | Rider Slides | D | B- | C+ | B+ | **D+** | D | — | +1 tier (bug fix) |
| 2244 | Helios Stellarator | C+ | C | A- | A- | **C+** | C+ | — | unchanged |
| safety | Fusion Safety | D+ | — | B | A | **C+** | C+ | — | unchanged |
| fusion-std | Fusion Standards | D+ | — | C+ | B | **D+** | D+ | — | unchanged |
| hazards | Afify Hazards | C+ | — | B+ | B | **B-** | B- | — | unchanged |

**Averages:**
- Original 7 docs: **B+** (range: C+ to A-)
- New 5 docs: **C** (range: D+ to C+)
- All 12 docs: **B-**

---

## 4. Per-Document Notes

### 2232 — Handley et al. (Fusion Markets, 17p)

**Overall: B+** | Structure B+ | Tables C | Body A- | Images A-

- 7 correct ## headers, 8 correct ### headers, 15 INDEX sections — good top-level structure
- 17 italic sub-subsections (`_3.3.1_`, `_5.1.1_`, etc.) rendered as italic text, not #### headers
- No false positive headers
- Tables rendered as space-separated text (no pipe tables)
- Body text clean with minor page-number artifacts
- 6 images extracted correctly
- v1 had INDEX: 1/5 (empty), now 15 sections — dramatic improvement from v2 header promotion

### 2233 — Araiinejad & Shirvan (D-T MCF TEA, 12p)

**Overall: B** | Structure B- | Tables C | Body B+ | Images A-

- 8 correct ## headers for sections 1-5, but INDEX confused by 6 false positive headers from table content (COA account numbers 20, 22.11, 22.12, 22.13, 30, 50 matched section-number patterns)
- 18 italic subsections (`_2.1._`, `_2.2._`, etc.) not promoted — significant structural gaps
- Line 420 has formatting corruption: `### 22.12 Blanket** **731.5`
- Economic parameter tables rendered as plain text (critical for TEA analysis)
- v1 had INDEX: 1/5 (empty), now 6 sections — improved but still has noise

### 2235 — Global Fusion & AI (30p)

**Overall: B+** | Structure B+ | Tables B+ | Body B | Images A-

- 6 ## + 18 ### headers, 27 INDEX sections — good coverage
- Missing section 4 parent heading and section 3.2; appendix headers not promoted
- 293 pipe table lines — GMFT table extraction working well
- Unicode ligature artifacts (eff → `e*orts`, ff → missing) — 100+ occurrences
- Appendix tables duplicated (GMFT extraction + pymupdf both present)
- v1 had INDEX: 3/5, now 27 sections — strong improvement

### 2236 — Digital Twins (66p)

**Overall: B+** | Structure B+ | Tables B+ | Body A- | Images A

- 19 ## + 15 ### headers, 62 INDEX sections — comprehensive but with 7 false positives
- 6 TOC entries duplicated as ## headers (cover page TOC has numbered lines)
- Line 167: numbered list item `1. The annual, global EPC market...` promoted to ##
- 309 pipe table lines — good table extraction
- Best image extraction: 31 images, all valid
- v1 had INDEX: 3/5, now 62 sections — dramatic improvement

### 2237 — LANL PJMIF (60p)

**Overall: B+** | Structure B | Tables B | Body A- | Images A-

- 31 ## + 15 ### headers, 47 INDEX sections — good but some issues
- 3 false positives: cover page doc ID as ##; sections 10-12 from TOC fused into single malformed header; inline "2020 Update" text promoted
- ~25 false negatives: bold Cost Category sub-headings (11-19, 21.01-21.17) rendered as bold only
- 117 pipe table lines — partial table coverage
- 19 images extracted correctly
- v1 had INDEX: 4/5, now 47 sections — good improvement

### 2238 — Lampe & Manheimer (CBFR, 40p)

**Overall: C+** | Structure C | Tables C | Body C+ | Images A-

- 20 ## headers but only 5 valid INDEX sections; 7 false positives including equation fragments
- Sections 5-6 not detected as ## headers (appear as plain text)
- Appendix and References headers rendered as bold only
- Subsections A-H within section 3 inconsistently handled (some ##, some bold-only)
- No pipe tables; equation-heavy content significantly garbled
- 40 images extracted — thorough
- v1 had INDEX: 1/5, now 5 sections — marginal improvement; equations remain problematic

### 2241 — Eester et al. (ICRH, 30p)

**Overall: A-** | Structure A- | Tables C | Body B+ | Images A

- 7 ## + 8 ### headers, 15 INDEX sections — accurate and properly nested
- Only 1 false negative (**Abstract** in bold, not promoted)
- 0 false positives — cleanest extraction in the corpus
- 3 pipe table lines (minimal table content in this paper)
- Dense mathematical content with some garbling
- 28 images extracted correctly
- v1 had INDEX: 4/5, now 15 sections — excellent

### 2243 — Rider (Slides, 127p)

**Overall: D+** | Structure D | Tables B- | Body C+ | Images B+

- 57 ## + 5 ### headers but INDEX (40 sections) is almost entirely false positives
- ~35 false positive headers: equation fragments (`## A >= 15`), axis labels (`## 1 10** **100`), table data (`## 1000 shots/second...`), diagram text (`## D compound`), NIF gain data, physics variables
- ~50+ false negative headers: virtually every slide title (127 slides) missed; all rendered as `**Bold Title**` only
- 90 pipe table lines — some tables correctly extracted (nuclear data tables)
- 213 images extracted (one per slide + embedded figures)
- Appendix regex fix (A2) reduced false positives from ~68 to ~35 — measurable improvement
- Body text from slides is fragmented but readable
- INDEX is actively misleading — worse than no INDEX

### 2244 — Swanson et al. (Helios Stellarator, 29p)

**Overall: C+** | Structure C+ | Tables C | Body A- | Images A-

- 6 correct ## headers (sections 1-5 + Acknowledgments), 0 ### headers, 0 INDEX sections
- 15 italic subsection headers (`_3.1._` through `_4.7._`) all missed — none promoted
- 0 false positives
- 25 pipe table lines — minimal table content
- Body text is clean and well-formatted
- 13 images extracted correctly
- INDEX is empty despite document having clear structure — the italic subsection convention is invisible to regex

### safety — Fusion Safety Program (14p)

**Overall: C+** | Structure D+ | Tables — | Body B | Images A

- 0 ## headers, 0 ### headers, 0 INDEX sections
- 12 slide titles in bold (`**Overview**`, `**Tritium**`, `**Dust**`, etc.) — all false negatives
- No tables in this document
- Body text is bullet-point lists from slides — readable
- 27 images extracted (slide backgrounds + embedded graphics)
- INDEX completely empty; document is not navigable

### fusion-std — Fusion Standards (4p)

**Overall: D+** | Structure D+ | Tables — | Body C+ | Images B

- 0 ## headers, 0 ### headers, 0 INDEX sections
- 8 bold section headings (`**Safety-related goals**`, `**Practical realization**`, etc.) — all false negatives
- No tables (sidebar box content is OCR-garbled)
- OCR artifacts: `**4**` from misread bullet characters (30+ occurrences), author name fragments
- IAEA page footer (`24 IAEA BULLETIN, 4/1995`) no longer promoted to ## header — bug fix A3 working
- 4 images extracted
- Overall poor due to OCR quality + zero structural detection

### hazards — Afify Hazards (8p)

**Overall: B-** | Structure C+ | Tables — | Body B+ | Images B

- 0 ## headers, 0 ### headers, 0 INDEX sections
- 12 bold section headings (`**Introduction to Fusion Hazards**`, `**STEP Safety Philosophies**`, etc.) — all false negatives
- No tables in this document
- Body text is clean and well-structured (Word doc origin)
- 3 images extracted (figures/diagrams)
- Despite zero structural detection, body text quality is high enough for reading
- Higher overall grade than fusion-std because text content is clean even without structure

---

## 5. Comparison to Prior Evaluations

### vs. v1 Evaluation Report (2026-02-06, 7 original docs)

The v1 report used a 1-5 numeric scale. Approximate letter-grade equivalents and current grades:

| ID | v1 Score | v1 Grade (approx) | v2+bugfix Grade | Change |
|----|----------|-------------------|-----------------|--------|
| 2232 | 2.50/5 | C+ | **B+** | +2 tiers |
| 2233 | 2.25/5 | C | **B** | +2 tiers |
| 2235 | 2.50/5 | C+ | **B+** | +2 tiers |
| 2236 | 3.50/5 | B | **B+** | +1 tier |
| 2237 | 3.25/5 | B- | **B+** | +1 tier |
| 2238 | 2.00/5 | C | **C+** | +1 tier |
| 2241 | 2.75/5 | C+ | **A-** | +3 tiers |

**All 7 original documents improved.** The biggest improvements are in documents where header promotion and INDEX generation went from non-functional (v1: empty INDEX for 4/7 docs) to functional (v2: all 7 have non-empty INDEX).

### vs. v3 Strategy Pre-Bug-Fix Grades (2026-02-07, 5 new docs)

| ID | Pre-Bug-Fix Grade | Post-Bug-Fix Grade | Change | Reason |
|----|-------------------|-------------------|--------|--------|
| 2243 | D | **D+** | +1 tier | Fix A2 (appendix regex tightening) reduced FP from ~68 to ~35 |
| 2244 | C+ | **C+** | unchanged | Bug fixes don't affect italic subsection detection |
| safety | C+ | **C+** | unchanged | Bug fixes don't affect unnumbered bold header detection |
| fusion-std | D+ | **D+** | unchanged | Fix A3 prevents footer promotion, but no positive headers added |
| hazards | B- | **B-** | unchanged | Bug fixes don't affect unnumbered bold header detection |

**Only 2243 improved from Workstream A bug fixes.** The remaining 4 documents have heading conventions (unnumbered bold, italic subsections) that fall entirely outside the regex pipeline's detection capability.

---

## 6. Bug Fix Impact Analysis

### Fix A1: PAGE Marker Isolation (strip before running header removal)

- **Observable impact:** Minor. Running headers now removed slightly more effectively when adjacent to PAGE markers. Most visible in multi-page documents where running headers appeared on every page. Quantifying the exact delta is difficult since running-header removal already caught most instances.

### Fix A2: Appendix Regex Tightening

- **Observable impact on 2243:** Reduced false positive headers from ~68 (pre-fix) to ~35 (post-fix). The tightened regex (`[A-Z][a-z].+?` title requirement) rejects single-letter physics variables (A, D, N) that previously matched. Still ~35 FP remaining from other patterns (equations, numbered text).
- **No observable impact on other docs:** Other documents don't have appendix-style false positives.

### Fix A3: Footer-as-Header Rejection

- **Observable impact on fusion-std:** The IAEA footer pattern (`24 IAEA BULLETIN, 4/1995`) is no longer promoted to ## header. Pre-fix, this was a false positive; post-fix, it's correctly left as plain text.
- **No observable impact on other docs:** Other documents don't have the slash-year footer pattern.

### Fix A4: Thousand-Separator Stripping (cross-validation)

- **Not directly observable in this baseline:** This fix affects Layer 3 AI repair cross-validation, which is only triggered with `--enhance`. Baseline extraction doesn't use AI repair.

---

## 7. Structural Quality by Document Type

| Document Type | Docs | Avg Structure Grade | Avg Overall Grade | Key Issue |
|--------------|------|--------------------|--------------------|-----------|
| Academic paper (numbered sections) | 2232, 2233, 2237, 2241 | B | B+ | Italic subsections missed; table content false positives |
| Academic paper (italic subsections) | 2244 | C+ | C+ | Top-level OK; all subsections invisible |
| Technical report | 2235, 2236 | B+ | B+ | Good coverage; some TOC duplication |
| Physics paper (scanned) | 2238 | C | C+ | Equation garbling; inconsistent subsection detection |
| Slide deck | 2243, safety | D/D+ | D+/C+ | Zero or garbage header detection; bold titles invisible |
| OCR scan | fusion-std | D+ | D+ | Zero detection; OCR artifacts compound the problem |
| Word doc (unnumbered) | hazards | C+ | B- | Zero header detection despite clean text |

**The pipeline has two clearly separated performance bands:**
1. **Numbered-section documents** (B to A-): regex header promotion works well
2. **Everything else** (D+ to C+): regex header promotion produces zero or garbage results

---

## Methodology Notes

- **Extraction:** `uv run agentic-mbse extract <path> --index --force` on each PDF
- **Metrics collection:** Automated via grep/wc/json-parse on output files
- **Spot-check:** Manual inspection of full_document.md + INDEX.md per document by sub-agents reading the extracted markdown. Each agent read first 10 pages, last 5 pages, and known problem areas (or entire document for short documents).
- **Grading:** Letter grades assigned using rubric from spec FR-4, with sub-grades for Structure, Tables, Body Text, and Images
- **All 12 documents graded consistently** using the same rubric, same pipeline version, same extraction flags

---

## Verification Checklist

- [x] All 12 PDFs successfully extracted with `--index --force` (no extraction failures)
- [x] Automated metrics table has all 9 metrics for all 12 documents (108 cells, no blanks)
- [x] Manual spot-check completed for all 12 documents with methodology notes
- [x] Overall grade assigned to all 12 documents
- [x] Sub-grades (Structure, Tables, Body Text, Images) assigned to all 12 documents
- [x] Report includes comparison column showing delta from prior evaluations
- [x] Report identifies which Workstream A bug fixes had observable impact
- [x] Report format supports row-by-row comparison for Item 4 benchmark
- [x] Report saved to `.project/reports/20260208_pdfv3-baseline.md`
- [x] No changes to source code (measurement only)
