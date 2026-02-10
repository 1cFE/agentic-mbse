# Experiment Log — doc-ingest

## Goals
# Goals — Document Ingestion Quality

## Table Extraction
- Tables in academic papers should extract with correct row/column structure
- Multi-page tables should be detected and merged where possible
- Table captions should be preserved and associated with their tables
- Complex layouts (merged cells, nested headers) should degrade gracefully

## Heading Detection
- Section headings should be detected accurately across different formatting styles
- Numbered headings (1.1, 1.2.3) should preserve hierarchy
- Unnumbered headings (bold, all-caps, underlined) should be promoted to proper markdown headings
- Table of contents entries should NOT be promoted to headings

## Multi-Format Support
- PDF extraction should work reliably across different academic paper layouts
- The extraction pipeline should handle single-column and two-column layouts
- Papers with heavy mathematical notation should not break the pipeline

## Character Fidelity
- Extracted text should preserve the original content with minimal loss
- Ligatures (fi, fl, ff, etc.) should be resolved to their component characters
- Unicode characters should be preserved, not replaced with placeholders

## Regression Safety
- No change should regress existing corpus metrics below established thresholds
- All corpus tests must pass after every change
- Per-paper heading thresholds accommodate known limitations of text-based detection

---

## Iteration 1

### Starting State
- Corpus: 5 papers (hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001)
- All 4 corpus tests pass (188 doc_ingest tests total)
- Comparison report: helios_design headings 52→7 (-87%, expected — baseline from Claude Layer 3 vision), delene chars -6.2% (baseline contaminated with AI artifacts)

### Specs
1. **fix-delene-baseline-artifacts** — Clean 25+ Claude Layer 3 hallucination artifacts from delene_2001 baseline (AI conversation text injected during failed equation repair). Eliminates phantom -6.2% char regression.
2. **add-bold-allcaps-heading-promotion** — Fix heading detection gap: bold all-caps single-word headings (`**ABSTRACT**`, `**CONTENTS**`) fall through both allcaps promoter (no bold markers) and unnumbered bold promoter (14-char minimum). Target: delene headings 23→25+.
3. **add-sparc-to-corpus** — Add SPARC tokamak paper (25 pages, tables + math) from pool. Progressive challenge: corpus 5→6 papers.

### Key Learnings
_(to be filled by eval agent)_

