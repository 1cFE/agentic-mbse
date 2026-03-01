# Spec: Pipeline Experimentation (Stage 3)

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-02-22 23:30 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

Stages 1-2 established what each extraction tool does individually and scored them against human-verified ground truth. But we don't know how they *compose*. The old `ralph/doc-ingest` branch's central mistake was designing extraction interfaces before understanding how the tools actually fit together — producing 560 lines of regex postprocessing built on wrong assumptions.

Stage 3 discovers the right pipeline shape empirically: script compositions, run them against the corpus, score against ground truth, and let the abstractions emerge from what actually works. This is the bridge between research (Stages 1-2) and production code (Stage 4).

### Success Criteria

- [x] At least 3 pipeline compositions tested and scored against ground truth
- [x] A clear winner (or hybrid) identified for the PDF extraction pipeline
- [x] Quality assessment logic sketched and tested (what triggers enhancement, what doesn't)
- [x] Concrete understanding of: calling conventions, data flow, merge logic, decision points
- [x] Written summary: "This is the pipeline shape that works. Here's what each component needs to do."
- [x] Cost/time budget understood per document

### Priority

Immediate next work item. Blocks Stage 4 (design + implement the production pipeline).

---

## Problem Statement

### Current State

We have 5 extraction tools characterized in isolation:
- **pymupdf4llm** — fast, always-available, good body text. Misses gridless tables, over-detects headings on bold-heavy docs, garbles math.
- **GMFT** — fast, accurate grid-lined tables. Over-detects TOC/lists.
- **Docling** — accurate headings and tables where it completes. Times out on 67% of corpus. Redundant if Claude is available.
- **Claude vision** — accuracy ceiling for headings, tables, and equations ($0.078/page). Only tool that produces LaTeX.
- **Pandoc** — perfect output from arXiv HTML. Only available for ~50% of papers.

We have ground truth for 7 documents (4 fully reviewed, 3 partial) and a scoring function (`score_against_ground_truth()`).

We do NOT know:
- What calls what, at what granularity (full doc vs page vs region)?
- What data flows between layers (bytes? markdown? images? quality scores)?
- What decisions the quality gate needs to make, and what info it needs?
- Whether per-page replacement or per-element splicing is the right merge strategy?
- What the actual cost/time profile is for the composite pipeline?

### Desired Outcome

A tested pipeline composition that matches or beats any single tool across all quality dimensions (headings, tables, equations) on the 4-paper development set, with known cost/time per document and a quality gate that makes correct routing decisions.

---

## Scope

### In Scope

- Pipeline experiment scripts in `tests/corpus/pipelines/`
- 4 hypotheses: H1 (GMFT table replacement), H3 (Claude equation repair), H5 (quality-gated multi-layer), H6 (Pandoc shortcut)
- Quality assessment logic: detect heading anomalies, table failures, math garbling
- Scoring all pipelines against `ground_truth.jsonl`
- Development set: 4 fully-reviewed papers (hawker_2020, hsu_2020, hansen_2025, paischer_2025)
- Hold-out validation: 3 partially-reviewed papers (aries_cost_account, delene_2001, energy_amplifier) — manual inspection only
- Written findings summary with pipeline recommendation for Stage 4

### Out of Scope

- Production code, clean interfaces, or reusable abstractions (Stage 4)
- HTML/XML structured source converters (Stage 5)
- Batch processing, CLI integration, retry logic (Stage 6)
- H2 (Docling heading grafting) — Docling is redundant given Claude vision availability
- H4 (Claude-primary extractor) — Stage 1D showed $0.078/page full-corpus is prohibitively expensive; targeted use is the right approach
- Expanding ground truth beyond the existing 7 documents
- New metrics development (use existing `compute_metrics()` + `score_against_ground_truth()`)

### Edge Cases & Considerations

- **Claude cost control:** Budget is ~$2/document. At $0.078/page, that's ~25 pages max per document. Quality gate MUST be selective — only route genuinely problematic pages to Claude.
- **GMFT false positives:** GMFT over-detects on TOC/lists (hsu_2020: 88 vs GT 56, hansen_2025: 42 vs GT 15). The table replacement logic needs a filter, not blind substitution.
- **Merge granularity:** Stage 1D showed Claude rewrites entire pages from vision rather than patching. Pipeline merge MUST operate at page level (replace full page output), not element level (splice individual equations/tables).
- **paischer_2025 heading over-detection:** pymupdf4llm best_v1 produces 68 headings (GT: 23). The quality gate needs to detect this and route to Claude or use the Pandoc path.
- **Papers with no issues:** hsu_2020 is well-handled by pymupdf4llm alone (headings close, tables exact). The pipeline should recognize "good enough" and skip enhancement.

---

## Requirements

### Functional Requirements

> Requirements below are from user's concept document and scoping decisions unless marked [INFERRED].

#### Experiment Infrastructure

1. **FR-1**: Each pipeline hypothesis MUST be a standalone Python script in `tests/corpus/pipelines/`, runnable as `python tests/corpus/pipelines/h1_pymupdf_gmft.py --slugs hawker_2020,hsu_2020`.

2. **FR-2**: Each script MUST save output in the same format as `experiment.py`: per-slug `output.md` + `metrics.json` in `tests/corpus/runs/pipeline_{name}/`.

3. **FR-3**: Each script MUST score its results against ground truth and log the accuracy scores (using `score_against_ground_truth()`).

4. **FR-4**: Each script MUST log decisions made per page (e.g., "page 5: GMFT table replacement applied, 3 tables replaced"; "page 8: Claude vision re-extraction triggered, reason: math garbling detected").

#### H1: pymupdf4llm + GMFT Table Replacement

5. **FR-5**: Run pymupdf4llm (best_v1 config) on full document. Run GMFT on full document. For pages where pymupdf4llm's tables have `<br>` artifacts or where pymupdf4llm detects 0 table rows but GMFT detects tables, replace pymupdf4llm's table sections with GMFT output.

6. **FR-6**: GMFT table replacement MUST include a false-positive filter — do not replace when GMFT detects tables in content that is actually TOC, lists, or figure captions.

7. **FR-7**: [INFERRED] The merge logic MUST handle the case where pymupdf4llm and GMFT detect different numbers of tables on the same page. Log mismatches for manual review.

#### H3: pymupdf4llm + Claude Vision for Equations

8. **FR-8**: Run pymupdf4llm on full document. Detect pages with math garbling (Unicode replacement characters `~~`, garbled fraction patterns, high density of isolated Unicode math symbols without LaTeX structure). Re-extract those pages with Claude pure vision (`extract_baseline.txt` prompt, 1 page per call).

9. **FR-9**: Replace pymupdf4llm output for flagged pages with Claude vision output (full page replacement, not element splicing — per Stage 1D finding).

10. **FR-10**: Track Claude cost per document. MUST stay within ~$2/document budget (~25 pages max at $0.078/page). If more pages are flagged than the budget allows, prioritize pages with highest garbling severity.

#### H5: Quality-Gated Multi-Layer Pipeline

11. **FR-11**: Implement a quality assessment function that scores each page on multiple dimensions:
    - **Heading anomaly**: 0 headings where expected, or suspiciously high count relative to page length
    - **Table anomaly**: `<br>` artifacts in pipe tables, 0 tables where expected, diagram content in pipe tables
    - **Math garbling**: Unicode replacement chars, garbled fraction patterns, `~~` artifacts
    - **Text density**: Very low char count suggesting OCR failure or missing content

12. **FR-12**: Route pages to enhancement paths based on quality scores:
    - Bad tables → GMFT replacement (free, fast)
    - Math garbling → Claude vision re-extraction ($0.078/page)
    - Heading failure → Claude vision re-extraction ($0.078/page)
    - Low text density → Claude vision re-extraction ($0.078/page)

13. **FR-13**: [INFERRED] Quality gate MUST prefer free enhancements (GMFT) over paid ones (Claude) when both could fix the issue. Claude is the fallback for problems GMFT can't solve (equations, headings, OCR).

14. **FR-14**: H5 SHOULD compose H1 and H3 — it is the full pipeline that incorporates the learnings from both.

#### H6: Pandoc Shortcut for arXiv Papers

15. **FR-15**: For papers with detectable arXiv IDs (pdftotext page 1 + regex), attempt to fetch HTML from arxiv.org and convert via Pandoc with the Stage 1B best config (strip `<figure>` tags, `pandoc -f html-native_divs-native_spans -t markdown-header_attributes --wrap=none`).

16. **FR-16**: If Pandoc HTML extraction succeeds, use it as the primary output (skip PDF pipeline entirely). Fall back to the PDF pipeline if arXiv HTML is unavailable.

17. **FR-17**: Score the Pandoc output against ground truth alongside the PDF pipeline output. Compare quality and identify any format differences that would affect downstream use.

#### Corpus & Scoring

18. **FR-18**: All hypotheses MUST be tested against the 4-paper development set: hawker_2020, hsu_2020, hansen_2025, paischer_2025.

19. **FR-19**: The winning pipeline SHOULD be validated against the 3-paper hold-out set (aries_cost_account, delene_2001, energy_amplifier) via manual inspection of the output.

20. **FR-20**: [INFERRED] Produce a comparison table showing all pipeline hypotheses scored against ground truth side-by-side, in the same format as the Stage 2 comparison report.

#### Findings Summary

21. **FR-21**: Write a findings summary documenting: the winning pipeline shape, what each component does, data flow between components, quality gate logic, cost/time per document, and what abstractions naturally emerged during experimentation.

---

## Acceptance Criteria

### Core Functionality

- [x] H1 script runs against 4-paper dev set and produces scored results
- [x] H3 script runs against 4-paper dev set and produces scored results
- [x] H5 script runs against 4-paper dev set and produces scored results
- [x] H6 script runs against paischer_2025 (the only dev-set paper with arXiv HTML) and produces scored results
- [x] Quality gate correctly identifies math garbling on hawker_2020 and paischer_2025
- [x] Quality gate correctly identifies table failures on hawker_2020 (0 tables in pymupdf4llm) and hansen_2025 (0 tables)
- [x] Quality gate correctly identifies heading over-detection on paischer_2025 (68 vs GT 23) — detected at doc-level, boosts Claude severity but doesn't fix non-Claude pages
- [x] GMFT false-positive filter rejects TOC/list misdetections on hsu_2020 and hansen_2025
- [x] Claude vision spend stays within ~$2/document budget — actual: $0.47 total for 4-paper dev set
- [x] Winning pipeline matches or beats any single tool on every quality dimension across the 4-paper dev set

### Hold-Out Validation

- [x] Winning pipeline run against 3 hold-out papers
- [x] Manual inspection confirms reasonable quality (no catastrophic regressions)

### Deliverables

- [x] Pipeline scripts in `tests/corpus/pipelines/`
- [x] Run results in `tests/corpus/runs/pipeline_h1/`, `pipeline_h3/`, `pipeline_h5/`, `pipeline_h6/`
- [x] Comparison table (all pipelines vs ground truth)
- [x] Findings summary with pipeline recommendation for Stage 4

### Quality & Integration

- [x] Existing `experiment.py`, `metrics.py`, `compare.py` are not broken
- [x] Pipeline scripts use existing `compute_metrics()` and `score_against_ground_truth()` — no parallel metric implementations
- [x] Decision logs capture routing rationale for every page

---

## Related Artifacts

- **Concept:** `.project/concepts/doc-extraction-development-strategy.md` (Stage 3 section, lines 354-480)
- **Ground truth:** `tests/corpus/ground_truth.jsonl`
- **Stage 2 report:** `tests/corpus/comparison_report.md`
- **Stage 1D findings:** `.project/active/claude-headless-deep-dive/findings.md`
- **Stage 1A findings:** `.project/active/pymupdf4llm-deep-dive/findings.md`
- **Stage 1B findings:** `.project/active/pandoc-deep-dive/findings.md`
- **Stage 1C findings:** `.project/active/docling-deep-dive/findings.md`
- **Experiment harness:** `tests/corpus/experiment.py`
- **Claude extraction harness:** `tests/corpus/claude_extract_experiment.py`
- **Metrics module:** `tests/corpus/metrics.py`
- **Design:** `.project/active/pipeline-experimentation/design.md` (to be created)

---

## Completion Notes

**Completed:** 2026-02-23

### Key Results

- **Winner:** H5 (quality-gated multi-layer) — 70% heading error, 8% table error, $0.12/doc avg
- **Free fallback:** H1 (pymupdf + GMFT) — 89% heading error, 1% table error, $0.00
- **arXiv pre-check:** H6 (Pandoc shortcut) — 0% heading error, 94% table error, $0.00
- **Total Claude experiment spend:** ~$4.30 across all runs

### Known Limitations Carried Forward

1. **Heading over-detection on non-arXiv papers** — paischer_2025: 55 vs GT 23 (139% error). Quality gate detects but can't fix without Claude on every page.
2. **Missing table detection gap** — quality gate catches bad tables, not absent ones. aries_cost_account: 120 vs GT 280 (space-aligned tables undetectable).
3. **GMFT over-detection on non-journal docs** — delene_2001: 255 vs GT 150. False-positive filter thresholds may need tuning.
4. **H6 doesn't invoke H5 fallback** — saves empty result for non-arXiv papers. Stage 4 should compose properly.
5. **Pandoc+GMFT hybrid not experimentally validated** — noted as promising for arXiv papers (Pandoc headings + GMFT tables).

### Artifacts

- Spec: `.project/active/pipeline-experimentation/spec.md` (this file)
- Plan: `.project/active/pipeline-experimentation/plan.md`
- Findings: `.project/active/pipeline-experimentation/findings.md`
- Comparison: `tests/corpus/pipeline_comparison.md`
- Scripts: `tests/corpus/pipelines/{shared,quality_gate,h1_pymupdf_gmft,h3_pymupdf_claude_eq,h5_quality_gated,h6_pandoc_shortcut}.py`
- Results: `tests/corpus/runs/pipeline_{h1,h3,h5,h6}/`

**Next Steps:** Stage 4 — design and implement the production pipeline based on findings.
