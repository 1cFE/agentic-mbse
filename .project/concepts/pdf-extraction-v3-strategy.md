# PDF Extraction v3: Claude as the Structural Backbone

**Author:** Reid Westwood
**Date:** 2026-02-07
**Status:** Proposed
**Branch:** pdf-extract
**Predecessor:** [pdf-extraction-v2.md](./pdf-extraction-v2.md)

---

## Executive Summary

The v2 pipeline achieves strong results on its training corpus (15/18 tables fixed, 7/7 indexes non-empty) but **fails catastrophically on documents outside its narrow design envelope**. A new corpus evaluation of 5 unseen documents produced 0/5 usable indexes, 0/5 correct header structures, and 68 garbage headers on a physics slide deck. The root cause is fundamental: regex-driven header promotion cannot generalize across document types. The fix is equally fundamental: **make Claude the structural authority instead of regex.**

---

## Algorithm Summary: Current Pipeline (v2)

### Block Diagram

```
                    ┌──────────────────────────────────────────────┐
                    │               INPUT: PDF file                │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │  LAYER 1: Deterministic Extraction            │
                    │  pymupdf_backend.py → postprocess.py         │
                    │                                              │
                    │  1. pymupdf4llm.to_markdown()                │
                    │     - hdr_info callback (bold + numbered)    │
                    │     - table_strategy="lines"                 │
                    │     - page_chunks=True → <!-- PAGE:N -->     │
                    │                                              │
                    │  2. postprocess() chain:                     │
                    │     strip_page_numbers       bare numbers    │
                    │     strip_running_headers    repeated lines  │
                    │     promote_bold_headers     **1 Foo** → ## 1 Foo
                    │     promote_plain_headers    1 Foo → ## 1 Foo│
                    │     clean_header_artifacts   remove TOC junk │
                    │     reject_noise_headers     demote garbage  │
                    │     normalize_image_paths    abs → relative  │
                    │     repair_ligatures         ﬁ → fi          │
                    │     promote_figure_captions  ![Fig N: ...]   │
                    │                                              │
                    │  Cost: $0  Time: ~2-5s/doc                   │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │  QUALITY GATES: detect_problems()            │
                    │  quality_gates.py                            │
                    │                                              │
                    │  Build page map from <!-- PAGE:N --> markers  │
                    │  Detect broken tables (whitespace-aligned,   │
                    │    inconsistent pipes, "Table N:" captions)  │
                    │  Detect garbled equations (U+FFFD clusters)  │
                    │                                              │
                    │  Output: list[RepairRequest]                 │
                    └──────────┬───────────────┬──────────────────┘
                               │               │
                    ┌──────────▼──────┐  ┌─────▼──────────────────┐
                    │ LAYER 2: GMFT   │  │ Remaining problems     │
                    │ table_extraction│  │ (equations, structure)  │
                    │                 │  │                         │
                    │ Table Transformer  │                         │
                    │ → DataFrames    │  │                         │
                    │ → pipe tables   │  │                         │
                    │                 │  │                         │
                    │ Cost: $0        │  │                         │
                    │ Time: ~1.4s/pg  │  │                         │
                    │ Hit rate: 83%   │  │                         │
                    └────────┬────────┘  └─────┬──────────────────┘
                             │                 │
                             └────────┬────────┘
                                      │
                    ┌─────────────────▼────────────────────────────┐
                    │  LAYER 3: AI Repair (--enhance only)         │
                    │  ai_repair.py                                │
                    │                                              │
                    │  For each remaining RepairRequest:           │
                    │    1. Render page as 200 DPI PNG              │
                    │    2. Build focused prompt (table/eq/struct)  │
                    │    3. Call claude -p (single turn)            │
                    │    4. Cross-validate numbers                  │
                    │    5. Accept or reject (keep original)        │
                    │                                              │
                    │  Cost: ~$0.03-0.08/page                      │
                    └─────────────────┬────────────────────────────┘
                                      │
                    ┌─────────────────▼────────────────────────────┐
                    │  INDEX GENERATION                            │
                    │  index.py → parse_sections() → INDEX.md      │
                    │                                              │
                    │  Requires ## headers in the markdown         │
                    └──────────────────────────────────────────────┘
```

### What each layer is responsible for

| Layer | Handles | Mechanism | Failure Mode |
|-------|---------|-----------|--------------|
| L1: postprocess | Headers, page numbers, running headers, ligatures, image paths | Regex pattern matching | Only finds patterns it's programmed for |
| Quality Gates | Detecting what still needs fixing | Heuristic rules | Only detects problem types it knows about |
| L2: GMFT | Tables | ML model (Table Transformer) | Misses borderless/whitespace tables (~17%) |
| L3: AI Repair | Whatever L1+L2 missed | Claude vision + cross-validation | Only runs on problems detected by quality gates |

### v2 Results on Original Corpus (7 docs)

| Metric | v1 | v2 L1+L2 |
|--------|-----|----------|
| Docs with non-empty INDEX | 3/7 | **7/7** |
| Table problems fixed | 0 | **15/18 (83%)** |
| Total sections detected | 148 | **181** |
| Pipe table lines | 0 | **672** |
| Overall quality | 2.68/5 | ~3.5/5 |

---

## Critical Analysis

### The core problem: regex-driven structure detection doesn't generalize

The new corpus evaluation is the smoking gun. The pipeline was tuned against 7 documents that all share one property: **bold numbered section headings**. When tested on 5 new documents that lack this property, the results are catastrophic:

| Metric | Original 7 docs | New 5 docs |
|--------|-----------------|------------|
| Docs with usable INDEX | 5/7 (71%) | **0/5 (0%)** |
| Docs with correct headers | ~5/7 | **1/5 (20%)** |
| Real headers detected | ~180 | **6 of ~170+** |

The pipeline's structural detection is a house of cards built on one assumption: headers look like `**N Title**` or `N Title`. When that assumption fails — which it does for slide decks, Word conference papers, magazine articles, and arXiv papers with italic subsections — the entire downstream chain collapses:

```
No numbered patterns detected
  → No headers promoted to ##
    → INDEX.md is empty
      → Document is non-navigable
        → AI agents can't find content
```

Worse, the appendix regex (`[A-Z](\.\d+)* `) actively creates **garbage headers** from physics variables, producing a 52-entry INDEX of pure noise on the slide deck.

### New corpus results in detail

| Doc | Pages | Sections (INDEX) | ## Hdrs | False+ Hdrs | False- Hdrs | Grade |
|-----|-------|------------------|---------|-------------|-------------|-------|
| 2243 (slides, 127p) | 127 | 52 (all wrong) | 68 | **68** | **~127** | **D** |
| 2244 (arXiv, 29p) | 29 | 1 (wrong) | 6 | 0 | **15** | **C+** |
| Fusion Safety (slides, 14p) | 14 | 0 | 0 | 0 | **~12** | **C+** |
| fusion-standards (OCR, 4p) | 4 | 1 (false pos.) | 1 | **1** | **~6** | **D+** |
| hazards-afify (Word, 8p) | 8 | 0 | 0 | 0 | **13** | **B-** |

### Five specific failure modes discovered

| # | Failure Mode | Severity | Docs Affected | Root Cause |
|---|-------------|----------|---------------|------------|
| 1 | **Unnumbered bold headers invisible** | CRITICAL | 4/5 | `promote_bold_headers()` requires `\d+` or `[A-Z](\.\d+)*` prefix. Unnumbered `**Title**` patterns are never promoted. |
| 2 | **Italic subsection headers invisible** | HIGH | 1/5 | `promote_bold_headers()` only matches `**bold**`. Italic `_3.1. Title_` patterns have no promotion path. |
| 3 | **Appendix regex over-matches on physics content** | HIGH | 1/5 | `[A-Z](\.\d+)* ` matches single capital letters (physics variables A, D, N) at line starts, creating dozens of false headers. |
| 4 | **PAGE markers block running header removal** | MEDIUM | 2/5 | `<!-- PAGE:N -->` on the line before a running header creates a multi-line block, which `strip_running_headers()` skips. |
| 5 | **Page footers promoted to section headers** | MEDIUM | 1/5 | `24 IAEA BULLETIN, 4/1995` matches `\d+ Title` pattern. No heuristic distinguishes page footers from section headers. |

### Why more regex won't fix this

The instinct is to add more patterns: italic headers, unnumbered bold headers, etc. But this path leads to a whack-a-mole of heuristics:

1. Add unnumbered bold header promotion → now every bold line is a header candidate → need heuristics to reject bold emphasis, bold table cells, bold figure labels
2. Add italic header promotion → `_3.1. Title_` works, but what about `_emphasis in a paragraph_`?
3. Each new pattern creates a new class of false positives
4. The appendix regex is already proof: a pattern that works for appendices creates 68 false positives on physics content

**The fundamental issue is that "is this line a section heading?" is a semantic question, not a syntactic one.** Regex can't answer it. You need to understand the document.

### What IS working well

Before throwing everything out, acknowledge what the pipeline does right:

| Component | Grade | Notes |
|-----------|-------|-------|
| Body text extraction | A | Paragraphs, lists, citations, references — all excellent across every document type |
| Image extraction | A | Paths normalized, figures with captions promoted |
| Page markers | A | `<!-- PAGE:N -->` provides reliable page mapping |
| Ligature repair | B+ | Unicode ligatures correctly decomposed (missing-character ligatures can't be fixed) |
| GMFT table extraction | B+ | 83% hit rate on target corpus, correct data in verified tables |
| Cross-validation safety | A | Catches hallucinated numbers, reject-by-default is the right policy |

### The real gap

The pipeline has a clear division:

- **Text quality**: Already good enough (B+ across all doc types)
- **Table quality**: Addressed by GMFT + Layer 3 (B to A- depending on doc)
- **Structural quality**: Broken for anything outside the narrow "numbered bold headers" format

Structure is what makes the difference between "wall of extracted text" and "navigable document." It's also what enables the INDEX, which is what enables downstream AI consumption.

---

## New Strategy: Claude as the Structural Backbone

The insight is simple: **Claude can read.** It can look at extracted markdown and understand what's a heading, what's a paragraph, what's a table caption, and what's a physics variable — regardless of formatting convention. Instead of trying to encode that understanding into regex, we should use Claude directly.

### Revised Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │               INPUT: PDF file                │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │  LAYER 1: Fast Extraction (simplified)       │
                    │                                              │
                    │  pymupdf4llm + lightweight postprocess:      │
                    │    - strip_page_numbers                      │
                    │    - normalize_image_paths                   │
                    │    - repair_ligatures                        │
                    │    - promote_figure_captions                 │
                    │                                              │
                    │  NOTE: Header promotion regex REMOVED from   │
                    │  this layer. No more bold/plain/appendix     │
                    │  regex — that's Claude's job now.            │
                    │                                              │
                    │  Cost: $0   Time: ~2-5s/doc                  │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │  LAYER 2: GMFT Table Enhancement             │
                    │  (unchanged — keep what works)               │
                    │                                              │
                    │  Cost: $0   Time: ~1-2s/table                │
                    └──────────────────┬───────────────────────────┘
                                       │
              ┌────────────────────────▼────────────────────────────────┐
              │  LAYER 3: Claude Structural + Quality Pass   (NEW)     │
              │                                                        │
              │  PHASE A — Document Style Detection                    │
              │  ┌──────────────────────────────────────────────────┐  │
              │  │  Send to Claude:                                 │  │
              │  │  - Page 1-3 as images (thumbnails)               │  │
              │  │  - First ~200 lines of extracted markdown        │  │
              │  │  Ask: "What is this document's heading           │  │
              │  │   convention? Return the heading scheme."        │  │
              │  │                                                  │  │
              │  │  Claude returns structured JSON:                 │  │
              │  │  {                                               │  │
              │  │    "doc_type": "slide_deck" | "paper" | ...,    │  │
              │  │    "heading_convention": "unnumbered_bold" |     │  │
              │  │      "numbered_bold" | "italic_subsections" ..., │  │
              │  │    "has_toc": true/false,                        │  │
              │  │    "running_headers": ["IAEA BULLETIN..."],      │  │
              │  │    "page_number_format": "bold" | "plain" | ...  │  │
              │  │  }                                               │  │
              │  └───────────────────────┬──────────────────────────┘  │
              │                          │                             │
              │  PHASE B — Full Structure Repair                       │
              │  ┌───────────────────────▼──────────────────────────┐  │
              │  │  Send to Claude:                                 │  │
              │  │  - The FULL extracted markdown                   │  │
              │  │  - The style detection result from Phase A       │  │
              │  │  - A sample page image every ~10 pages for       │  │
              │  │    grounding (visual cross-reference)            │  │
              │  │                                                  │  │
              │  │  Ask: "Add proper markdown ## headers to this    │  │
              │  │   document. Return a list of insertions:         │  │
              │  │   {line: N, level: 2, title: '...'}"            │  │
              │  │                                                  │  │
              │  │  Claude returns a structured diff, NOT the       │  │
              │  │  full document — cheaper and more reliable.      │  │
              │  └───────────────────────┬──────────────────────────┘  │
              │                          │                             │
              │  PHASE C — Targeted Repair (enhanced Layer 3)          │
              │  ┌───────────────────────▼──────────────────────────┐  │
              │  │  For any remaining quality issues:               │  │
              │  │  - Tables GMFT missed → page image + text       │  │
              │  │  - Garbled equations → page image + context     │  │
              │  │  - Suspicious content → page image + text       │  │
              │  │                                                  │  │
              │  │  Same cross-validation as before for tables.    │  │
              │  └───────────────────────┬──────────────────────────┘  │
              │                          │                             │
              │  Cost: ~$0.50-2.00 per document total                  │
              └────────────────────────┬───────────────────────────────┘
                                       │
              ┌────────────────────────▼────────────────────────────────┐
              │  INDEX GENERATION                                      │
              │  Now works reliably because Claude added proper headers │
              └────────────────────────────────────────────────────────┘
```

---

## Three Workstreams

### A. Bug Fixes (things that are conceptually right but broken)

Targeted fixes to the existing pipeline — low effort, high value. These improve the baseline regardless of whether the Claude structural layer is implemented.

| # | Bug | Fix | Effort |
|---|-----|-----|--------|
| A1 | **PAGE markers block running header removal** — `<!-- PAGE:N -->` on the line before a running header creates a multi-line block, which `strip_running_headers()` skips | Before `strip_running_headers()`, strip `<!-- PAGE:N -->` lines into their own blocks so they don't form multi-line groups with adjacent content | ~30 min |
| A2 | **Appendix regex over-matches on physics** — `[A-Z](\.\d+)* ` matches physics variables (A, D, N) at line starts, creating dozens of false headers | Tighten to require the title portion to start with an uppercase word (not symbol): `^\*\*([A-Z](?:\.\d+)*)\s+([A-Z][a-z].+?)\*\*\s*$`. Also require minimum title length (>3 words) | ~30 min |
| A3 | **Page-footer-as-header false positive** — `24 IAEA BULLETIN, 4/1995` matched `\d+ Title` pattern | In `promote_plain_headers()`, reject lines where the "title" portion contains known non-header patterns (journal names, "BULLETIN", year patterns like `N/NNNN`) | ~30 min |
| A4 | **Thousand-separator stripping in cross-validation** — `extract_numbers("1,234.56")` yields `{"1", "234.56"}` instead of `{"1234.56"}` | Strip `,` and `_` from input text before regex matching in `extract_numbers()` | ~15 min |

### B. Claude as the Universal Structure Layer

This is the big conceptual shift. Instead of regex-driven header promotion being the core mechanism with Claude as a patch, **Claude becomes the primary structural engine** and regex becomes a fast-path optimization for the common case.

#### B1. `claude_structure.py` — new module (~200 lines)

Two main functions:

```python
@dataclass
class DocumentStyle:
    doc_type: str          # "slide_deck" | "paper" | "report" | "article" | "proceedings"
    heading_convention: str # "numbered_bold" | "unnumbered_bold" | "italic_subsections" | "mixed"
    has_toc: bool
    running_headers: list[str]   # detected running headers/footers
    page_number_format: str      # "bold" | "plain" | "none"

@dataclass
class HeaderInsertion:
    line: int           # 0-indexed line number in the markdown
    level: int          # heading level (1-4)
    title: str          # heading text

def detect_document_style(
    md_text: str,
    pdf_path: Path,
    first_n_pages: int = 3,
) -> DocumentStyle:
    """Send first few pages (images) + extracted text to Claude.
    Returns structured description of the document's conventions."""

def repair_structure(
    md_text: str,
    pdf_path: Path,
    style: DocumentStyle,
    sample_every_n_pages: int = 10,
) -> str:
    """Send full markdown + style info + periodic page images to Claude.
    Returns markdown with proper ## headers inserted."""
```

Key design decisions:

1. **Two-phase approach**: Detect style first (cheap, ~3 page images), then fix structure (more expensive, full text). The style detection result lets you craft a much more targeted prompt for the structure pass.

2. **Structured diff output, not full rewrite**: Ask Claude to return `[{line: N, level: 2, title: "Introduction"}]` rather than the full document. This is:
   - Cheaper (smaller output)
   - Safer (less room for accidental content changes)
   - Auditable (you can log exactly what Claude changed)

3. **Visual grounding**: Send a page image every ~10 pages alongside the text. This lets Claude cross-reference: "the extracted text says `**A ≥ 15**` but the page image shows this is a chart label, not a heading."

4. **Running header identification**: Phase A also identifies running headers/footers by looking at repeating patterns across page images. This replaces the fragile frequency-threshold heuristic.

#### B2. Integration into the pipeline

Two modes:

| Mode | Layers | Cost | When to use |
|------|--------|------|-------------|
| `--enhance` (default for single docs) | L1 + L2 + L3 (Claude) | ~$0.50-2.00/doc | Single reference documents, any format |
| `--fast` (for batch/budget) | L1 + L2 only | $0 | Batch processing large corpora, numbered-section papers |

The key insight: **for single document extraction, the user almost always wants the best result**, and $1-2 per document is negligible for reference documents they'll consult repeatedly. The `--fast` flag is for batch processing large corpora.

#### B3. Hybrid fast-path optimization

For documents where regex header promotion works well (the original corpus type), we can skip the expensive Claude pass:

```python
def needs_claude_structure(md_text: str) -> bool:
    """Quick check: did regex promotion find a reasonable number of headers?

    If Layer 1 found >=5 headers and they look plausible (not noise),
    skip Claude structural pass. Otherwise, escalate.
    """
    headers = re.findall(r'^## ', md_text, re.MULTILINE)
    if len(headers) >= 5:
        # Check for noise: if >50% of headers contain math symbols, flag
        noise_count = sum(1 for h in headers if re.search(r'[≥≤µ∑∫=\[\]]', h))
        if noise_count / len(headers) < 0.3:
            return False  # Regex did a good job, skip Claude
    return True  # Regex found nothing or garbage, need Claude
```

This means the numbered-section papers from the original corpus still extract for free in ~5 seconds, while slide decks and unnumbered papers automatically escalate to Claude.

### C. Claude as Fallback Quality Sweep

Beyond structure, Claude can serve as a general-purpose quality check for anything the deterministic pipeline gets wrong. This replaces the narrow "detect specific problem types → fix those" approach with a broader "look at what we got and fix whatever's wrong" approach.

#### C1. Page-level quality sampling

For every N-th page (configurable, default every 5th page), render the page image alongside the extracted text and ask Claude:

> "Compare this page image to the extracted markdown below. Rate the extraction quality 1-5. If there are issues, return the corrected markdown for this page region."

This catches problems the quality gates don't know about:

- Tables that quality gates didn't detect (unusual formats)
- Garbled equations that don't match the U+FFFD heuristic
- Column interleaving in multi-column layouts
- OCR artifacts
- Missing content

#### C2. Full-document quality report

After all repairs, one final Claude call with the complete markdown:

> "Review this extracted document. Identify any remaining quality issues: garbled text, obviously wrong numbers, broken tables, missing sections. Return a JSON list of issues with line numbers."

This serves as both a quality report and a trigger for additional targeted repairs.

---

## Cost Model

| Component | Cost per 65-page doc | When it runs |
|-----------|---------------------|--------------|
| Layer 1 (pymupdf + postprocess) | $0 | Always |
| Layer 2 (GMFT) | $0 | Always (if installed) |
| Style detection (3 page images) | ~$0.05 | `--enhance` |
| Structure repair (full text + ~7 images) | ~$0.30-0.50 | `--enhance`, when `needs_claude_structure()` is true |
| Quality sampling (~13 pages checked) | ~$0.50-1.00 | `--enhance` |
| Targeted repairs (~5 problem pages) | ~$0.25-0.40 | `--enhance`, when issues detected |
| **Total with `--enhance`** | **~$1.00-2.00** | |
| **Total with `--fast`** | **$0** | |

For a reference document that a team will consult for months, $1-2 is nothing. For batch-processing 100 papers for a literature review, $100-200 may be relevant — hence the `--fast` mode.

---

## Expected Impact

### What this solves from the new corpus evaluation

| Failure Mode | Current Result | With New Strategy |
|-------------|---------------|-------------------|
| Unnumbered bold headers (4/5 docs) | 0 detected | Claude identifies them from page images |
| Italic subsection headers (2244) | 0 detected | Claude identifies them from page images |
| Appendix regex false positives (2243) | 68 garbage headers | Regex removed from default path; Claude doesn't confuse physics variables with headers |
| Footer promoted to header (fusion-standards) | Misleading INDEX | Claude recognizes footers from visual context |
| Running header not stripped (2/5) | Survived in output | Claude identifies running headers in style detection phase; bug fix A1 also addresses the deterministic path |
| Garbage INDEX (2/5 actively misleading) | Actively harmful | Claude produces correct headers → correct INDEX |

### Expected grades on new corpus

| Doc | Current Grade | Expected Grade | Key Improvement |
|-----|--------------|----------------|-----------------|
| 2243 (slides, 127p) | D | B | Slide titles as headers, equation fragments left alone |
| 2244 (arXiv, 29p) | C+ | A- | All 21 sections properly headed (both bold and italic) |
| Fusion Safety (slides, 14p) | C+ | B+ | Slide titles detected, bullet structure preserved |
| fusion-standards (OCR, 4p) | D+ | C+ | Real sections found, footer demoted (OCR issues remain — not a structure problem) |
| hazards-afify (Word, 8p) | B- | A- | 13 sections properly headed, running headers stripped |

### Expected grades on original corpus (no regression)

| Doc | Current Grade | Expected Grade | Notes |
|-----|--------------|----------------|-------|
| 2232 (Handley) | B+ | A- | Claude may catch subsections regex missed |
| 2233 (Araiinejad) | B | B+ | Minimal change; already had numbered sections |
| 2235 (FIA Global) | B+ | A- | GMFT tables preserved; Claude validates structure |
| 2236 (FAS Market) | B+ | A- | TOC handling improved |
| 2237 (LANL Cost) | B+ | A- | 15/18 tables + Claude fixes remaining structure |
| 2238 (Lampe) | C+ | B | OCR noise in scanned paper — limited improvement possible |
| 2241 (Eester) | A- | A- | Already clean; no change expected |

---

## Execution Plan

### Phase 1: Bug Fixes (half day)

Fix the 4 concrete bugs from workstream A. These improve the baseline for all modes (both `--fast` and `--enhance`).

**Deliverables:**
- [x] Fix A1: PAGE marker splitting before running header removal
- [x] Fix A2: Tighten appendix regex
- [x] Fix A3: Reject footer-as-header patterns
- [x] Fix A4: Thousand-separator stripping in cross-validation
- [x] Tests for each fix
- [ ] Re-run on new corpus to verify improvements (at least fusion-standards, hazards-afify)

### Phase 2: Claude Structure Module (1 day)

Build `claude_structure.py` with `detect_document_style()` and `repair_structure()`. Wire into the pipeline as the new Layer 3 Phase A+B.

**Deliverables:**
- [ ] `src/agentic_mbse/extraction/claude_structure.py` (~200 lines)
- [ ] `DocumentStyle` and `HeaderInsertion` dataclasses
- [ ] `detect_document_style()` with page image rendering + Claude call
- [ ] `repair_structure()` with full-text + sampled images + Claude call
- [ ] `needs_claude_structure()` fast-path check
- [ ] Integration into `extract_cli.py` pipeline
- [ ] Tests with mocked Claude responses
- [ ] Test against original 7-doc corpus (verify no regression in `--fast` mode)
- [ ] Test against new 5-doc corpus (verify dramatic improvement with `--enhance`)

### Phase 3: Quality Sweep Integration (half day)

Add page-level quality sampling and the final quality report pass. Wire into `--enhance`.

**Deliverables:**
- [ ] Page-level quality sampling (every N-th page) in `claude_structure.py` or new `claude_quality.py`
- [ ] Final quality report generation
- [ ] Integration into `--enhance` pipeline
- [ ] Cost reporting before execution (`--enhance` shows estimated cost)
- [ ] `--yes` flag to skip cost confirmation

### Phase 4: Benchmarking and Ship (half day)

Run full 12-doc corpus (7 original + 5 new). Document results. Update scope statement.

**Deliverables:**
- [ ] Full benchmark: 12 documents, both `--fast` and `--enhance` modes
- [ ] Results table with per-document grades
- [ ] Cost actuals vs estimates
- [ ] Updated PR description (remove "numbered sections only" caveat)
- [ ] Updated `--help` text
- [ ] Full test suite passes

---

## Design Principles

1. **Claude is the structural authority.** Regex is a fast-path optimization, not the primary mechanism. When in doubt, ask Claude.

2. **Structured diffs, not full rewrites.** Claude returns specific changes (insert header at line N, replace lines M-P with corrected table), not the entire document. This minimizes the blast radius of errors.

3. **Visual grounding.** Every Claude call that affects content includes page images for cross-reference. Claude can't hallucinate a section heading if the page image shows it's a chart label.

4. **Cross-validation stays.** For numerical content (tables), the reject-by-default cross-validation mechanism remains. Claude's vision is good but not perfect for dense numerical data.

5. **Graceful degradation.** If `claude` CLI isn't available, the pipeline falls back to regex-only (current behavior). The `--fast` flag explicitly opts into this mode.

6. **Cost transparency.** Before running `--enhance`, report the estimated cost and get confirmation (or allow `--yes` to skip).

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude structural pass halluccinates headers that don't exist | Low | Medium | Visual grounding with page images; structured diff output (line-level insertions, not full rewrite) makes hallucinations obvious |
| Full-document text exceeds Claude context window | Low | Medium | 65-page doc = ~50K tokens, well within limits. For 200+ page docs, chunk into sections with overlapping context |
| Claude API cost higher than estimated | Medium | Low | Cost transparency: report before execution, enforce `--max-repair-pages` budget. User said "not concerned about cost" |
| Claude CLI not available in all environments | Medium | Low | Graceful fallback to `--fast` mode. Clear error message. |
| Structured diff output has off-by-one line errors | Medium | Medium | Anchor insertions to content markers (PAGE comments, unique text snippets) rather than raw line numbers |
| Style detection gets document type wrong | Low | Low | Provide the full first 200 lines + 3 page images — Claude has ample context. Worst case: structure repair is slightly less targeted but still works |
| Regression on original corpus in `--fast` mode | Low | High | Bug fixes only improve regex behavior; no existing patterns removed in `--fast` mode. Full regression test before shipping. |
| `--enhance` default for single docs surprises users who expect free extraction | Medium | Medium | Clear cost estimate before execution. Default remains free (no `--enhance`); consider making `--enhance` default only after v3 is proven. |

---

## Open Questions

1. **Should `--enhance` become the default?** Arguments for: it produces dramatically better results, cost is negligible for reference docs. Arguments against: surprising users with API costs, requires `claude` CLI. **Current recommendation: keep as opt-in, revisit after benchmarking v3.**

2. **Should the fast-path check (`needs_claude_structure()`) be configurable?** Some users might want Claude structural pass even on well-structured docs for validation. A `--force-enhance` flag could skip the fast-path check.

3. **How to handle very long documents (200+ pages)?** Chunking strategy for the structure repair pass needs design. One approach: process in ~50-page windows with 5-page overlap, merge headers across windows.

4. **Should quality sampling be exhaustive or sampled?** Every-5th-page sampling catches ~80% of issues at 20% of the cost. Every-page sampling catches everything but costs 5x more. Make configurable with `--sample-rate`.

5. **Interaction with the interactive skill (`/pdf-analysis`).** The skill currently uses a 3-tier approach (pymupdf → Docling MCP → vision). Should it use the new Claude structural pass as well? Probably yes — the skill would benefit from the same quality improvement. But the skill is interactive (human in the loop), so it can use Claude's judgment more aggressively.

---

## Status Log

### 2026-02-07: Phase 1 complete — all Workstream A bug fixes shipped

All four bug fixes from Workstream A are implemented and tested. Changes in `postprocess.py`:

| Fix | Change | Tests Added |
|-----|--------|-------------|
| A1: PAGE markers block running header removal | Normalize `<!-- PAGE:N -->` into standalone blocks at the top of `strip_running_headers()` before paragraph splitting | 2 (marker isolation, marker preservation) |
| A2: Appendix regex over-matches on physics | Tightened `_APPENDIX_HEADER_RE` title group from `(.+?)` to `([A-Z][a-z].+?)` — requires capitalized-word title start | 3 (physics variable, symbol title, comparison operator) |
| A3: Page footers promoted to section headers | Two-part fix: (1) reordered `postprocess()` chain so `strip_page_numbers` and `strip_running_headers` run before header promotion, (2) added slash-year pattern (`\b\d{1,2}/\d{4}\b`) to `_is_toc_line()` | 4 (journal footer rejection, slash-year detection x3) |
| A4: Thousand-separator stripping | Already fixed in prior commit (e559be9) | Already covered |

Full test suite: 799 passed, 1 skipped, 0 failures. Next step: re-run on affected docs (hazards-afify, fusion-standards, 2243) to verify improvements, then proceed to Phase 2 (Claude structural module).
