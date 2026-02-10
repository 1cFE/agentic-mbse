# Spec: Extraction Quality Audit

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-10 08:16 PST
**Complexity:** MEDIUM
**Branch:** ralph/doc-ingest

---

## Business Goals

### Why This Matters

The doc_ingest pipeline exists to produce high-quality structured markdown from academic PDFs — good enough for downstream knowledge extraction (populating domain models, extracting design parameters, building traceability). We have been measuring proxy metrics (heading counts, table row counts, character counts) and optimizing against them, but nobody has actually **read the output** to verify it's coherent, complete, and correct.

If the extraction is garbled, truncated, or full of artifacts, then the routing infrastructure, provenance tracking, and API discovery are all worthless. Quality is the only thing that matters.

### Success Criteria

- [ ] Every paper in the corpus has been audited with source PDF pages compared against both baseline and current output
- [ ] Each paper scored on 6 quality dimensions: content completeness, table quality, equation/math preservation, figure references, heading structure, general coherence
- [ ] Scoring uses BETTER / SAME / WORSE / BROKEN (not percentages)
- [ ] Specific examples cited for every WORSE or BROKEN score — exact sections, not vague summaries
- [ ] Final verdict: is the pipeline output actually useful for knowledge extraction?
- [ ] Known problems catalogued with severity (blocks usage vs. annoying vs. cosmetic)

### Priority

This is the fundamental quality gate for the doc_ingest branch. It SHOULD have been done before any metric optimization. Nothing ships without this passing.

---

## Problem Statement

### Current State

We have proxy metrics showing:
- Tables: meeting or exceeding baseline (good sign, but are they readable?)
- Headings: counts improved via postprocessor, but hierarchy/correctness unknown
- Character counts: within ~7% of baseline (but are the RIGHT characters there?)
- Equations/math: never measured at all
- General coherence: never measured at all

The metrics tell us almost nothing about whether someone can actually READ the output and extract knowledge from it.

### Desired Outcome

A rigorous, honest quality assessment that answers: **is the current pipeline producing extraction quality at least as good as the fusion-tea baseline, across all quality dimensions that matter for downstream use?**

---

## Scope

### In Scope

- Side-by-side comparison of all 5 corpus papers (baseline vs current output)
- PDF source page extraction via `/pdf-analysis` skill to verify what the source actually contains
- Assessment of 6 quality dimensions per paper (see Requirements)
- Identification of specific broken sections with examples
- Final quality verdict with prioritized problem list

### Out of Scope

- Fixing any problems found (separate work items after audit)
- Wiring Layer 3/4 Claude integration (separate feature)
- Expanding the test corpus (do after audit confirms methodology)
- Performance optimization

### Edge Cases & Considerations

- Some baseline extractions may themselves be imperfect — the audit should note when the baseline is wrong too
- Table quality varies enormously by paper — ARIES has 137+ tables, hawker has 0
- Math-heavy papers (helios, hawker) need equation-specific attention
- Multi-column layouts may cause paragraph interleaving artifacts

---

## Requirements

### Functional Requirements

#### FR-1: Per-Paper Quality Audit

For each of the 5 corpus papers, the audit MUST:

1. **Extract representative pages from the source PDF** using `/pdf-analysis` to establish ground truth
2. **Read corresponding sections** from both baseline and current extraction output
3. **Score each quality dimension** as BETTER / SAME / WORSE / BROKEN
4. **Cite specific examples** for any WORSE or BROKEN score — quote the actual text

Papers: `hawker_2020`, `aries_cost_account`, `helios_design`, `hsu_2020`, `delene_2001`

#### FR-2: Quality Dimensions

Each paper MUST be assessed on these 6 dimensions:

| Dimension | What to Check |
|-----------|--------------|
| **Content completeness** | Is all body text present? Paragraphs truncated? Sentences cut off mid-word? Content from all pages represented? |
| **Table quality** | Are tables readable with correct headers, aligned columns, and accurate data? Or garbled pipe-soup with merged cells and `<br>` artifacts? |
| **Equation/math** | Are equations preserved in any usable form? Unicode math intact? Or garbled symbols and broken formatting? |
| **Figure references** | Do figure references (`Figure N`, `Fig. N`) survive? Are captions associated with the right images? |
| **Heading structure** | Is the hierarchy correct (not just count)? Do sections flow logically? Are there false-positive promotions creating nonsense headings? |
| **General coherence** | Can you read a full section and understand it? Or is it full of running-header artifacts, page-break noise, column interleaving? |

#### FR-3: Problem Catalogue

The audit MUST produce a problem list with:
- **Severity**: Blocks usage / Degrades quality / Cosmetic
- **Paper(s) affected**: Which papers exhibit this problem
- **Dimension**: Which quality dimension it falls under
- **Example**: Quoted text showing the problem
- **Root cause** (if identifiable): Which pipeline stage causes it

#### FR-4: Final Verdict

The audit MUST conclude with:
- Per-paper verdict: SHIP / NEEDS WORK / BROKEN
- Overall pipeline verdict: same scale
- Prioritized list of what to fix (if NEEDS WORK or BROKEN)

### Non-Functional Requirements

- **NFR-1**: The audit MUST use `/pdf-analysis` skill to extract actual PDF pages as ground truth — do not rely solely on the markdown output
- **NFR-2**: The audit MUST examine the WORST sections of each paper, not just cherry-pick clean sections
- **NFR-3**: The audit SHOULD compare at least 3 representative sections per paper (intro, a content-heavy middle section, and a table/figure-heavy section)

---

## Acceptance Criteria

### Core Functionality

- [ ] All 5 papers audited with 6-dimension scoring
- [ ] PDF source pages extracted and compared for at least 3 sections per paper
- [ ] Every WORSE/BROKEN score has a specific quoted example
- [ ] Problem catalogue with severity ratings produced
- [ ] Final ship/no-ship verdict with rationale

### Quality & Integration

- [ ] Audit document is in `.project/active/extraction-quality-audit/audit-report.md`
- [ ] Problems are actionable — someone could pick up the list and fix them

---

## Audit Method

### For Each Paper:

1. Use `/pdf-analysis` to extract 3-5 representative pages from the source PDF
2. Read the corresponding sections in `tests/corpus/baseline/{slug}/full_document.md`
3. Read the corresponding sections in `tests/corpus/current/{slug}/full_document.md`
4. Score each dimension
5. Document problems found

### Section Selection Strategy:

- **First 2 pages**: Title, abstract, introduction — tests basic structure
- **A table-heavy section**: Tests table extraction quality (skip if paper has no tables)
- **A math/equation section**: Tests equation preservation (skip if paper has no math)
- **A late-document section**: Tests whether quality degrades as document progresses
- **The worst-looking section**: Actively seek out the ugliest part of the extraction

---

## Related Artifacts

- **Baseline extractions:** `tests/corpus/baseline/*/full_document.md`
- **Current extractions:** `tests/corpus/current/*/full_document.md`
- **Source PDFs:** `tests/corpus/pdfs/*.pdf`
- **Comparison script:** `tests/corpus/compare.py`
- **Postprocessor:** `src/agentic_mbse/extraction/postprocess.py`
- **PDF converter:** `src/doc_ingest/converters/pdf_converter.py`

---

**Next Steps:** Execute the audit per this spec. Produce `audit-report.md`.
