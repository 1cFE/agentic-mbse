# Spec: Pandoc Deep-Dive (Stage 1B)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-22 11:22 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

The current `pandoc_backend.py` (136 lines) handles DOCX only, using a single hardcoded configuration. Pandoc actually supports a wide range of input formats — including PDF and HTML — with dozens of output-shaping options. We don't know what Pandoc can do well because we've never systematically tested it.

More importantly: most recent arXiv papers have **HTML versions available** that are semantically richer than PDFs. If Pandoc can produce high-quality markdown from arXiv HTML, that's a potentially superior extraction path that bypasses all the PDF extraction headaches (garbled equations, broken tables, lost structure). We need evidence to know.

This is Stage 1B of the [development strategy](../../concepts/doc-extraction-development-strategy.md). It runs alongside or after Stage 1A (pymupdf4llm deep-dive) and feeds into the pipeline assembly in Stage 3.

### Success Criteria

- [ ] Documented, reproducible method for discovering arXiv IDs and HTML links from a PDF — tested against a real paper, with the process and reasoning captured
- [ ] Findings report documenting every Pandoc configuration tested, with quality observations and comparative metrics
- [ ] Clear, evidence-backed answer to: "How does Pandoc HTML→markdown compare to pymupdf4llm PDF→markdown?"
- [ ] Clear, evidence-backed answer to: "How does Pandoc PDF→markdown compare to pymupdf4llm PDF→markdown?"
- [ ] A recommended set of Pandoc configurations per input format, backed by experimental evidence

### Priority

Active Stage 1 work. Informs pipeline assembly (Stage 3) and source routing decisions (Stage 5).

---

## Problem Statement

### Current State

Pandoc is installed (v3.1.3) and integrated as a DOCX-only backend. Its capabilities for HTML and PDF input are untested. Meanwhile, arXiv HTML — a high-fidelity structured source available for most recent papers — is completely unexploited.

We also don't know how Pandoc's PDF reader compares to pymupdf4llm. The development strategy notes "Pandoc can also read PDFs (poorly)" but that claim is undocumented.

### Desired Outcome

A **findings report** and **tested wrapper** that answer:
1. What quality does Pandoc produce from arXiv HTML, and how does it compare to PDF extraction?
2. What quality does Pandoc produce from PDF input? Is it ever useful?
3. Which Pandoc output options (`--wrap`, `--markdown-headings`, math rendering, table format) matter?

The report is the primary deliverable — it captures institutional knowledge. The code is secondary.

---

## Scope

### In Scope

- **arXiv HTML discovery test**: Can a Claude agent find the arXiv ID and HTML link from just the PDF? (Test with LL7Q6PSU / Paischer / arXiv:2510.07314v1)
- **arXiv HTML download**: Fetch the HTML version of LL7Q6PSU for use as test input
- **Pandoc HTML→markdown experimentation**: Many iterations with different Pandoc configurations, documenting quality after each run
- **Pandoc PDF→markdown experimentation**: Test Pandoc as a PDF reader, compare against pymupdf4llm baseline
- **Cross-format quality comparison**: Side-by-side comparison of the same paper extracted via Pandoc HTML, Pandoc PDF, and pymupdf4llm PDF
- **Findings report**: Living document updated after each experiment, capturing parameters, observations, metrics, and surprises
- **Updated PandocConverter**: Evolve the existing backend based on experimental findings

### Out of Scope

- **DOCX conversion** — de-prioritized, no test data on hand
- **JATS XML conversion** — de-prioritized, no test data on hand
- **Source discovery APIs** (OpenAlex, arXiv API) — Stage 5
- **Docling investigation** — Stage 1C
- **Pipeline assembly** — Stage 3
- **Batch processing or CLI changes**

### Edge Cases & Considerations

- arXiv HTML may include MathML that Pandoc handles differently than inline LaTeX
- arXiv HTML may reference external assets (images, CSS) that affect conversion
- Pandoc PDF reader may produce very poor output — that's a valid finding worth documenting
- Different `--from` format specifiers (html, html5, html+tex_math_dollars) may affect math handling

---

## Requirements

### Functional Requirements

#### FR-1: Structured Source Discovery from PDF

A key deliverable of this task is **proving out the process of finding structured source alternatives (arXiv ID, HTML link) starting from only a PDF**. This directly informs Stage 5 source routing — if the process is reliable and documentable, it can be automated; if it's fragile, we need to know that too.

**The test:**

1. Start with ONLY the PDF of LL7Q6PSU (Paischer et al., "GyroSwin: 5D Surrogates...")
2. Attempt to discover: the arXiv identifier, and the arXiv HTML URL
3. Do NOT use the reference answer (arXiv:2510.07314v1, HTML at `arxiv.org/html/2510.07314v1`) — discover it independently

**What to document in the findings report:**

1. **Discovery method**: Exactly how was the arXiv ID found? Step by step. (PDF text search? PDF metadata fields? Web search from title/authors? DOI lookup? Some combination?)
2. **Which methods were tried and failed**: Dead ends are as informative as successes
3. **HTML link construction**: Once the arXiv ID is found, how do you get from ID to HTML URL? Is `arxiv.org/html/{id}` reliable? Does it work for all papers or only recent ones?
4. **Generalizability assessment**: Would this same discovery process work for other papers in the corpus? Try at least 2-3 other corpus PDFs and document whether they have arXiv HTML available
5. **Automation feasibility**: Could this process be scripted? What are the brittle parts? What would break?
6. **Time and effort**: How long did discovery take? How many steps? This matters for understanding whether automated discovery is worth the complexity.

**Why this is a key deliverable:** The development strategy (Stage 5) envisions automated source discovery via APIs. Before building that infrastructure, we need ground-truth understanding of what the discovery process actually looks like in practice. This hands-on test provides that.

#### FR-2: Test Data Acquisition

Acquire HTML source for the test paper:

1. Download arXiv HTML for LL7Q6PSU (2510.07314v1) and save to `tests/corpus/html/`
2. Ensure the corresponding PDF is available in `tests/corpus/pdfs/` (should already be there from Stage 1A corpus expansion, or download separately)
3. Record both source paths in `papers.jsonl` or equivalent tracking

The PDF for LL7Q6PSU is already planned for download in the pymupdf4llm-deep-dive spec (FR-1). If Stage 1A runs first, the PDF will already be present. If not, download it as part of this task.

#### FR-3: Pandoc HTML→Markdown Experimentation

Run **many iterations** of Pandoc converting arXiv HTML to markdown, varying configuration each time:

**Parameters to investigate:**

| Parameter | Variants to test |
|-----------|-----------------|
| `--from` | `html`, `html5`, `html+tex_math_dollars`, `html+tex_math_single_backslash` |
| `--wrap` | `none`, `auto`, `preserve` |
| `--markdown-headings` | `atx`, `setext` |
| `--columns` | default, 80, 120 |
| Math rendering | `--katex`, `--mathml`, `--webtex`, default (passthrough) |
| `--strip-comments` | on/off |
| `--standalone` | on/off |
| Table handling | `--pipe-tables`, `--grid-tables`, default |

This list is NOT exhaustive — explore `pandoc --list-extensions=markdown` and the Pandoc manual for additional relevant options.

**For each iteration:**
1. Record the exact command / configuration
2. Run Pandoc and capture output
3. Inspect output quality: headings, tables, equations, links, images, overall structure
4. Record observations in the findings report
5. Compare against pymupdf4llm PDF baseline (using existing metrics where applicable)

#### FR-4: Pandoc PDF→Markdown Experimentation

Test Pandoc as a PDF reader on corpus papers:

1. Run `pandoc --from=pdf` on at least 3 corpus PDFs (including LL7Q6PSU, one table-heavy, one text-heavy)
2. Compare output quality against pymupdf4llm baseline for the same documents
3. Document: Is Pandoc PDF ever competitive? Are there specific scenarios where it's useful?
4. Try relevant configuration variants (same output options as FR-3)

This is expected to produce poor results — that's a valid and useful finding. Document it clearly so we don't revisit the question.

#### FR-5: Findings Report

A living document at `.project/active/pandoc-deep-dive/findings.md`, updated progressively as experiments run:

1. **Experiment log**: Every configuration tested, with timestamp, exact command, and rationale for trying it
2. **Per-experiment observations**: What the output looked like. What was good, what was broken. With specific examples (quote snippets of output).
3. **Comparative analysis**: Side-by-side quality comparison — Pandoc HTML vs pymupdf4llm PDF vs Pandoc PDF for the same content
4. **Math handling assessment**: How does Pandoc handle MathML from arXiv HTML? How does this compare to pymupdf4llm's garbled Unicode from PDF?
5. **Cumulative conclusions**: Updated after each experiment batch — what we know so far
6. **Final recommendation**: Best Pandoc configurations per input format, with evidence

The report MUST include specific quality examples — not just metrics, but quoted markdown snippets showing "here's what the heading / table / equation actually looked like."

The report is as important as the code.

#### FR-6: [INFERRED] Updated PandocConverter

After experimentation concludes, update `src/agentic_mbse/extraction/pandoc_backend.py`:
- Add HTML input support (alongside existing DOCX)
- Use the best-discovered configuration per input format
- Code comments documenting why each parameter value was chosen, referencing findings

---

### Non-Functional Requirements

- **Reproducibility**: Each experiment SHOULD be reproducible from the configuration log in the findings report
- **Incremental**: Results accumulate — earlier findings are preserved when new experiments run
- **Low ceremony**: A Python script is fine for the harness. No framework needed.
- **Reuse existing infrastructure**: Use `tests/corpus/metrics.py` and `compare.py` where applicable for quantitative comparison

---

## Acceptance Criteria

### Core Functionality

- [ ] **Structured source discovery process documented end-to-end** — step-by-step method for finding arXiv ID and HTML from a PDF, including failed approaches
- [ ] Discovery process tested on LL7Q6PSU and at least 2 other corpus papers — generalizability assessed
- [ ] Automation feasibility assessment with identified brittle points
- [ ] arXiv HTML downloaded for LL7Q6PSU and available as test input
- [ ] At least 8 distinct Pandoc HTML→markdown configurations tested and documented
- [ ] At least 3 Pandoc PDF→markdown runs tested and documented
- [ ] Side-by-side quality comparison: Pandoc HTML vs pymupdf4llm PDF vs Pandoc PDF
- [ ] Findings report captures observations, quality examples, metrics, and reasoning for each configuration
- [ ] Final configuration recommendations backed by comparative evidence

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] Findings report is readable as a standalone document — someone unfamiliar with the project can understand the conclusions
- [ ] Math handling quality explicitly assessed and compared across extraction paths

---

## Related Artifacts

- **Concept**: `.project/concepts/doc-extraction-development-strategy.md` (Stage 1B, lines 75-93)
- **Sibling spec**: `.project/active/pymupdf4llm-deep-dive/spec.md` (Stage 1A — shares test corpus)
- **Existing backend**: `src/agentic_mbse/extraction/pandoc_backend.py` (136 lines, DOCX only)
- **Metrics tooling**: `tests/corpus/metrics.py`, `tests/corpus/compare.py`
- **Test corpus**: `tests/corpus/pdfs/`, `tests/corpus/papers.jsonl`
- **Test paper**: LL7Q6PSU / Paischer / arXiv:2510.07314v1 (HTML at `arxiv.org/html/2510.07314v1`)
- **Findings report**: `.project/active/pandoc-deep-dive/findings.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (lightweight — mostly harness design and experiment plan) then implementation.
