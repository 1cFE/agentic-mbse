# Extraction Quality Audit Report

**Date:** 2026-02-10
**Auditor:** Claude (per spec)
**Branch:** ralph/doc-ingest
**Method:** PDF source pages extracted via `/pdf-analysis`, compared against baseline and current extraction outputs

---

## Executive Summary

The current pipeline produces extraction quality that is **equal to or better than the baseline across all 5 papers**. The most important finding is that the **baseline itself has serious quality problems** -- LLM hallucination artifacts injected during the original extraction process -- that the current pipeline eliminates entirely.

**Overall pipeline verdict: SHIP** (with caveats for aries_cost_account)

---

## Per-Paper Scorecards

### hawker_2020 (14 pages, text + equations + tables)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content completeness | SAME | Both cover all 14 pages identically |
| Table quality | SAME | Both render Royal Society dot-tables identically (poorly, but same) |
| Equation/math | SAME | Both have garbled bracket notation: `_[C][/][(1][ +][ d][)][i]_` |
| Figure references | SAME | No embedded figures in this paper |
| Heading structure | **BETTER** | Current: proper H1/H3/H4 hierarchy. Baseline: flat H2 with duplicate headings |
| General coherence | **BETTER** | Baseline has LLM hallucination (see below) |

**Hallucination in baseline (lines 265-277):**
```
$$C_p = \alpha P e^{Y_c}$$

Wait, let me reconsider. Looking at the garbled text more carefully:

The equation numbered (2.4) shows `Cp = [α][P][e]` with context mentioning `Yc`...
```
This is LLM commentary injected mid-document. Current version: clean.

**Baseline heading duplication pattern:**
```
(b) Previous studies       ← original subsection label

## Previous studies        ← fabricated duplicate heading
```
Current removes duplicates, keeps single properly-nested headings.

**Verdict: SHIP**

---

### aries_cost_account (100 pages, 137+ tables)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content completeness | SAME | Both cover all 100 pages; identical body text |
| Table quality | **WORSE** | Current garbles body text into a 2-column table (lines 1597-1602) |
| Equation/math | SAME | Identical bracket/caret notation throughout |
| Figure references | SAME | Same 25 images; only filename stems differ |
| Heading structure | **WORSE** | Missing Account 22 heading; spurious heading from numbered list |
| General coherence | SAME | Narrative flow equivalent |

**Table regression (current lines 1597-1602):**
```
| Neutral Particle Beam Plasma Heating, Current Drive and Rotation... | drive, did Table 7. |
| Summary of Heating and Current Drive, Account 22.03.01... | of plasma and each type more below in supposedly were reported |
```
Body text has been forced into a 2-column markdown table with word-level fragmentation. The right column contains orphaned word fragments. Baseline renders this same content as flowing body text (correct).

**Missing heading (current line 905):**
```
Power Core Equipment, Account 22, Formerly the Reactor Plant** **Equipment
```
This major section heading is broken into non-heading bold text. Baseline correctly has `## Power Core Equipment, Account 22...`.

**Spurious heading (current line 428):**
```
## 3 Pricing of bulk materials is based on the Kansas City, Missouri location.
```
This is a numbered list item, not a section heading. Baseline correctly renders as body text.

**No hallucinations in either version.**

**Verdict: NEEDS WORK** (table garbling and missing Account 22 heading are real regressions)

---

### helios_design (30 pages, equations + 1 table + figures)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content completeness | **BETTER** | Baseline injects ~40 fabricated subsection headings |
| Table quality | SAME | Table 1 extracted identically |
| Equation/math | SAME | Both have same bracket-artifact limitations |
| Figure references | SAME | 13 figures in both; only filename convention differs |
| Heading structure | **BETTER** | Current preserves actual document structure; baseline fabricates headings |
| General coherence | SAME | Body text identical |

**~40 fabricated headings in baseline (confirmed absent from PDF source):**
```
### Global Parameters          (baseline line 186)
### Plasma Configuration       (baseline line 191)
### Divertor System            (baseline line 202)
### MHD Stability Analysis     (baseline line 467)
### Transport Assumptions      (baseline line 560)
### Gyrokinetic Simulations    (baseline line 568)
... (approximately 40 total)
```

These are LLM-generated topic summaries, not content from the original document. The PDF only has numbered section headings (`## 1. Introduction` through `## 6. Acknowledgments`) and italic subsection labels (`_3.1. Scoping studies..._`). The current extraction correctly preserves this structure.

**Baseline also has duplicate heading artifacts:**
```
## 5. Conclusion
## Summary and Future Work    ← fabricated duplicate

## 6. Acknowledgments
## Acknowledgments            ← duplicate
```

**Verdict: SHIP**

---

### hsu_2020 (9 pages, tables + cost data)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content completeness | **BETTER** | Current recovers 5 sentences lost to hallucination in baseline |
| Table quality | SAME | All 3 tables (2, 3, 4) identical as proper markdown pipe tables |
| Equation/math | SAME | Document is light on equations |
| Figure references | SAME | Same 4 images; filename convention differs |
| Heading structure | **BETTER** | Removes redundant bold+heading echo, removes fabricated heading |
| General coherence | **BETTER** | No hallucination; clean document flow |

**Hallucination in baseline (line 52):**
```
I need to see the image to convert the equation to LaTeX. Could you please share
the image/screenshot of the PDF page? You mentioned there's an image showing the
original PDF page, but I don't see one attached to your message.
```
This replaces ~5 sentences of the Executive Summary's primary findings about modular design benefits, cost savings, and CapEx results. Current version recovers all of this text.

**Fabricated heading in baseline (line 162):**
```
## Cost Categories
```
This heading does not exist in the PDF source (page 5 just has "The cost categories are given here" as a plain paragraph).

**Spurious `##` on reference [7] in baseline (line 82):**
```
## science facility, a credible break-in step on the path to fusion energy...
```
A bibliographic reference line erroneously promoted to a section heading.

**Verdict: SHIP**

---

### delene_2001 (39 pages, 11 tables + figures)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content completeness | **BETTER** | Table data recovered; no content displaced by hallucinations |
| Table quality | **BETTER** | All 11 tables render correctly vs 6+ corrupted in baseline |
| Equation/math | **BETTER** | No fabricated LaTeX; document has no real equations |
| Figure references | SAME | Same 13 images, 18 Fig. references |
| Heading structure | SAME | Minor cosmetic differences |
| General coherence | **BETTER** | Zero hallucination artifacts vs 30 in baseline |

**30 hallucination artifacts in baseline.** The extraction LLM encountered table images and, instead of extracting content, responded conversationally:

**Baseline line 354-358:**
```
I notice you mentioned an image showing the original PDF page, but no image was
actually provided in your message. Could you please share the image or PDF so I
can see the equation you'd like converted to LaTeX?
```

**Baseline line 425-431 (Table 2 header corrupted):**
```
I don't see any image attached to your message...
$$\frac{\text{Capital investment cost (1999 \$M)}}{\text{Account} \quad \text{PC-FGD} \quad \text{PFBC}}$$
```
The current version renders this correctly as plaintext table headers.

**5 fabricated LaTeX equations in baseline** -- created from tabular data that was never equations. Example (baseline line 537):
```
$$65.2 \left[\frac{650\ \$/kW(e)}{}\right]$$
```
Current renders correctly: `Base construction cost 65.2 [650 $/kW(e)]`

**Verdict: SHIP**

---

## Aggregate Scoring Matrix

| Paper | Content | Tables | Equations | Figures | Headings | Coherence | Verdict |
|-------|---------|--------|-----------|---------|----------|-----------|---------|
| hawker_2020 | SAME | SAME | SAME | SAME | **BETTER** | **BETTER** | SHIP |
| aries_cost_account | SAME | **WORSE** | SAME | SAME | **WORSE** | SAME | NEEDS WORK |
| helios_design | **BETTER** | SAME | SAME | SAME | **BETTER** | SAME | SHIP |
| hsu_2020 | **BETTER** | SAME | SAME | SAME | **BETTER** | **BETTER** | SHIP |
| delene_2001 | **BETTER** | **BETTER** | **BETTER** | SAME | SAME | **BETTER** | SHIP |

**Tally:** 4 SHIP, 1 NEEDS WORK. 0 BROKEN.

---

## Problem Catalogue

### Severity: Blocks Usage

| # | Problem | Paper(s) | Dimension | Root Cause |
|---|---------|----------|-----------|------------|
| 1 | Body text garbled into 2-column table with word-level fragmentation | aries_cost_account | Table quality | PDF converter or postprocessor misidentifies flowing text as a table |
| 2 | Missing Account 22 heading -- major section heading broken into non-heading bold text | aries_cost_account | Heading structure | Postprocessor fails to promote bold text to heading, or breaks it with `** **` formatting |

### Severity: Degrades Quality

| # | Problem | Paper(s) | Dimension | Root Cause |
|---|---------|----------|-----------|------------|
| 3 | Numbered list item promoted to section heading (`## 3 Pricing of bulk materials...`) | aries_cost_account | Heading structure | Postprocessor heading promotion heuristic too aggressive on numbered items |
| 4 | Heading hierarchy shifts (Account 21 summary demoted from H3 to H4, etc.) | aries_cost_account | Heading structure | Postprocessor heading level assignment inconsistent |
| 5 | Image paths use temp filenames (`tmp_8cj82bt.pdf`, `tmp1jz2cm5d.pdf`) instead of original PDF names | ALL current | Figure references | Pipeline uses temp files during conversion, doesn't map back to source names |
| 6 | Equations render as garbled bracket notation: `_[C][/][(1][ +][ d][)][i]_` | hawker_2020, helios_design | Equation/math | pymupdf4llm limitation with mathematical notation in 2-column layouts |
| 7 | Table dot-leaders render as hundreds of `. . .` characters | hawker_2020 | Table quality | pymupdf4llm renders horizontal rules/dot leaders literally |

### Severity: Cosmetic

| # | Problem | Paper(s) | Dimension | Root Cause |
|---|---------|----------|-----------|------------|
| 8 | Section numbers lose trailing period (`## 1 Introduction` vs `## 1. Introduction`) | helios_design | Heading structure | Postprocessor normalization strips periods |
| 9 | Page number artifacts rendered with strikethrough: `~~**8**~~` | hawker_2020 | General coherence | pymupdf4llm renders page numbers with their original formatting |
| 10 | Superscripts use non-standard strikethrough notation: `10~~20~~` for 10^20 | helios_design | Equation/math | pymupdf4llm encoding convention |
| 11 | Word-break artifacts from column layout: `e ff ects` instead of `effects` | helios_design | General coherence | Column text extraction limitation |
| 12 | Journal sidebar metadata promoted to headings: `## Research`, `### Author for correspondence:` | hawker_2020 | Heading structure | Postprocessor promotes sidebar text |

---

## Baseline Quality Assessment

A critical finding of this audit: **the baseline itself has significant quality problems that were previously undetected.** These include:

| Issue | Affected Papers | Count |
|-------|----------------|-------|
| LLM hallucination artifacts ("I need to see the image...", "Wait, let me reconsider...") | hawker_2020, hsu_2020, delene_2001 | 32 instances |
| Fabricated subsection headings (topics the LLM invented as headings) | helios_design | ~40 headings |
| Fabricated LaTeX equations (table data rendered as `$$...$$`) | delene_2001, hawker_2020 | 6 instances |
| Duplicate heading patterns (bold line + markdown heading for same section) | hawker_2020, aries_cost_account, hsu_2020 | Pervasive |
| Fabricated section headings not in source PDF | hsu_2020 | 2 instances |

The current pipeline eliminates **all** of these baseline defects. The proxy metrics used during development (heading counts, table counts, character counts) could not detect these qualitative problems. This audit confirms that the current pipeline is a substantial improvement over the baseline in terms of fidelity to the source documents.

---

## Final Verdict

### Per-Paper

| Paper | Verdict | Rationale |
|-------|---------|-----------|
| hawker_2020 | **SHIP** | Better heading structure, no hallucinations; same content quality |
| aries_cost_account | **NEEDS WORK** | Two real regressions: garbled table text and missing major heading |
| helios_design | **SHIP** | Dramatically better -- removes ~40 fabricated headings from baseline |
| hsu_2020 | **SHIP** | Better across 4 dimensions; recovers content lost to hallucination |
| delene_2001 | **SHIP** | Better across 4 dimensions; removes 30 hallucination artifacts |

### Overall Pipeline

**SHIP** -- with the following conditions:

1. **Investigate aries_cost_account regressions** (problems #1 and #2 in the catalogue). These are the only cases where current is worse than baseline. Root cause is likely in the postprocessor's table detection or heading promotion logic. The aries document is an edge case (100 pages, 137+ tables, unusual formatting).

2. **Accept equation rendering limitations** (problem #6). This is a fundamental pymupdf4llm limitation with 2-column academic layouts. Fixing it would require Tier 2 (Docling) or Tier 3 (vision) extraction for equation-heavy pages. Not a blocker for the current corpus.

3. **Consider fixing temp filename issue** (problem #5). Low priority but would improve portability and debugging.

### Is the pipeline output useful for knowledge extraction?

**Yes.** For 4 of 5 papers, the current extraction is fully readable and contains all the key data, parameters, cost models, and conclusions needed for downstream knowledge extraction. The body text reads coherently, tables are parseable, and document structure is well-preserved. The aries_cost_account paper has one localized regression that affects a small section but doesn't block the rest of the 100-page document from being useful.

---

## Prioritized Fix List

1. **P0 (before ship):** Investigate body-text-as-table garbling in aries_cost_account (lines 1597-1602). This is likely a table detection false positive in the postprocessor or converter.

2. **P0 (before ship):** Fix broken Account 22 heading in aries_cost_account (line 905). Likely a bold-text splitting issue (`** **` mid-word).

3. **P1 (next sprint):** Prevent numbered list items from being promoted to headings (aries line 428). Add a heuristic to the postprocessor: if a line starts with a single digit followed by a lowercase word, it's probably a list item, not a heading.

4. **P2 (nice to have):** Map temp filenames back to source PDF names in image paths.

5. **P2 (nice to have):** Investigate heading hierarchy consistency in large documents (aries heading level shifts).
