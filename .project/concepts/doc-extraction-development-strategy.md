# Development Strategy: Clean Document Extraction Infrastructure

**Created:** 2026-02-22
**Status:** Active (revised 2026-02-22)
**Branch:** `doc-ingest-clean` (fresh from `main`)

---

## Guiding Principles

The `ralph/doc-ingest` branch produced 97 commits and ~25,900 lines of experimental code. The full audit (`.project/research/20260221-094043_doc-ingest-branch-full-audit.md`) surfaced clear lessons:

1. **Understand tools deeply before building pipelines.** The single highest-value change on the old branch was `table_strategy="lines_strict"` — one parameter discovered through reading pymupdf4llm's API. Meanwhile, 560 lines of regex-based postprocessing was built without fully understanding the upstream tools.
2. **Build and test incrementally.** The BART loop infrastructure was well-engineered but jumped straight to orchestrating agents before the extraction fundamentals were solid.
3. **Don't accumulate heuristics.** The promote-then-demote anti-pattern (add header promoters, then add noise filters to reject their false positives) produced fragile code. Prefer structured approaches over regex accumulation.
4. **Let abstractions emerge from usage.** Writing clean wrapper classes before understanding the pipeline composition leads to wrong interfaces. Experiment first, then design the code.

This strategy has four phases: **understand the tools** (Stage 1), **establish ground truth and compare** (Stage 2), **experiment with compositions** (Stage 3), then **design and build the real thing** (Stage 4+).

---

## Stage 0: Prerequisites

**Goal:** Ensure the development environment has all necessary tools available.

### Requirements

- [ ] `pymupdf4llm` installed and working (`uv sync` should cover this)
- [ ] Pandoc system binary available (`pandoc --version`)
- [ ] Docling MCP server configured (via `scripts/setup-docling.sh` or `agentic-mbse init --no-docling` to skip)
- [ ] pdf-analysis skill installed in `.claude/skills/pdf-analysis/` (already present on this branch)
- [ ] Test PDFs accessible — the corpus lives in `tests/corpus/pdfs/` (15 PDFs, 14 unique)

### Actions

1. Verify `uv run python -c "import pymupdf4llm; print(pymupdf4llm.__version__)"` works
2. Verify `pandoc --version` returns a version
3. Verify Docling MCP is running or decide to defer it
4. Collect 3-5 representative test PDFs covering: text-heavy, table-heavy, math-heavy, scanned/OCR-needed

### References

- pdf-analysis skill: `claude/skills/pdf-analysis/SKILL.md`
- Docling setup: `scripts/setup-docling.sh` (342 lines, Linux-only currently)
- Existing extraction backends on main: `src/agentic_mbse/extraction/`

---

## Stage 1: Deep-Dive into Extraction Methods

**Goal:** Build fundamental understanding of each extraction method by experimenting directly with their APIs. Understand what each does well, what it does poorly, and which parameters matter.

This is a **pure research** stage. The deliverables are knowledge (captured in research notes and experiment runs) and comparable metrics across all methods. No production code is written here — we don't yet know enough about how the pipeline will compose to design the right interfaces.

### 1A: pymupdf4llm — STATUS: COMPLETE

pymupdf4llm is the fast, always-available baseline. It converts PDF pages to markdown using font metadata for heading detection.

**What we investigated:**
- `to_markdown()` parameters: `hdr_info`, `table_strategy`, `ignore_code`, `write_images`, `page_chunks`, `dpi`, `force_text`
- 9 parameter configurations tested across the full 15-PDF corpus
- Custom header detectors: academic (bold-only), bold (+ Roman numerals), composite (font-size + bold union)

**Key findings:**
- **CompositeHeaderDetector** is the clear winner — zero regressions vs default, +10/13 docs improved (e.g., hansen_2025: 0→17 headings, delene_2001: 4→26)
- **`table_strategy="lines"`** (default) is correct — `lines_strict` eliminates 100% of aries_cost_account tables (137→0), `text` is 15x slower with massive over-detection
- **`ignore_code=True`** eliminates 610 code fences in tajima patent doc
- **Known remaining gaps:** math garbling (Unicode salad), `<br>` artifacts in tables (333 across 7 docs), sparc_overview heading detection (non-bold, same-size headers = 1 heading found)

**Evidence:** `.project/active/pymupdf4llm-deep-dive/findings.md` (530 lines), `tests/corpus/runs/{baseline,lines_strict,no_headers,ignore_code,hdr_academic,hdr_bold,hdr_composite,best_v1,best_v2_strict,table_text}/`

### 1B: Pandoc (Structured Sources) — STATUS: COMPLETE

Pandoc is the converter for structured formats (HTML, JATS XML, DOCX). Not viable for PDF input.

**What we investigated:**
- Confirmed Pandoc 3.1.3 does NOT support PDF as input format
- arXiv ID discovery: `pdftotext` page 1 + regex is 100% reliable, <1s per paper
- 16 Pandoc configurations tested on arXiv HTML (paischer_2025)
- Pre-processing + flag combinations for optimal HTML→markdown conversion

**Key findings:**
- **Best config:** Pre-process to strip `<figure>` tags, then `pandoc -f html-native_divs-native_spans -t markdown-header_attributes --wrap=none`
- This fixes the two biggest Pandoc problems (tables and figures pass through as raw HTML when wrapped in `<figure>`)
- **Math conversion is excellent** — MathML → LaTeX `$...$` is reliable and accurate
- **All 23 headings, all 5 tables, all figures** convert cleanly with the recommended config
- 2/4 test papers had arXiv HTML available (recent papers); 2/4 were journal-only

**Evidence:** `.project/active/pandoc-deep-dive/findings.md`, `tests/corpus/pandoc-experiments/iter-01..16/`

### 1C: Docling & GMFT — STATUS: COMPLETE

Docling is the ML-based heavy hitter; GMFT is the fast table-specific extractor.

**What we investigated (Phase 1):**
- Docling baseline with/without OCR on full corpus
- Single-page extraction viability
- GMFT baseline on full corpus
- OCR quality with different backends

**Key findings so far:**
- **Docling full-document extraction is impractical** — times out (300s) on 10/15 corpus docs, even without OCR. Driven by content complexity (TableFormer), not page count.
- **Docling single-page extraction works** — 7-9s per page, viable for targeted use
- **Docling heading detection is superior** — hansen_2025: 18 vs 0 (pymupdf4llm), tajima: 21 vs 10
- **GMFT is blazing fast** — entire 15-doc corpus in 76s, zero crashes, zero `<br>` artifacts
- **GMFT handles complex tables well** — proper spanning cells, math symbols preserved
- **Docling OCR with RapidOCR is terrible for English** — Chinese-trained model produces "FUSIOi4" for "FUSION"
- Investigating alternative OCR backends (EasyOCR, Tesseract)

**Evidence:** `.project/active/docling-deep-dive/findings.md`, `tests/corpus/runs/{docling_baseline,docling_no_ocr,gmft_baseline,...}/`

### 1D: Claude Headless Direct Extraction — STATUS: COMPLETE

> **Findings:** `.project/active/claude-headless-deep-dive/findings.md`
>
> **Key results:** Claude pure vision produces clean LaTeX equations (the only tool to do so), accurate tables (no false positives), and reliable headings. Cost is $0.078/page (Sonnet). General repair and focused synthesis approaches showed no improvement over pure vision — supplemental text is ignored. Recommended pipeline: pymupdf4llm primary + Claude vision on targeted equation/table/heading-failure pages. Total experiment spend: $15.30.

**Depends on:** 1A, 1B, 1C (for baseline comparison)

Stages 1A-1C characterize what *libraries* can do. Stage 1D asks: **what happens if we just ask Claude to extract a document directly?** This establishes an upper bound on LLM-native extraction and reveals where Claude fits in the pipeline.

#### Experiment Architecture

**1. Python orchestration script** (`tests/corpus/claude_extract_experiment.py`)
- Renders pages to images (via pymupdf)
- Invokes `claude -p` with extraction prompt + image paths
- Captures markdown output, runs `compute_metrics()` for comparable results
- Saves to `tests/corpus/runs/claude_*/` in same format as 1A-1C

**2. Extraction prompts** specifying: output format (ATX headings, pipe tables, LaTeX math), fidelity rules (exact numbers, equation transcription), tool-use instructions for assisted variants.

#### Experiment Matrix

| Experiment | Pages/Call | Tool Access | Rationale |
|------------|-----------|-------------|-----------|
| `claude_vision_1pp` | 1 | Built-in vision only | Baseline: pure vision, no tools |
| `claude_vision_5pp` | 5 | Built-in vision only | Does cross-page context help? |
| `claude_vision_10pp` | 10 | Built-in vision only | Quality vs attention tradeoff |
| `claude_docling_1pp` | 1 | Docling MCP + vision | Does the combination beat either alone? |
| `claude_docling_5pp` | 5 | Docling MCP + vision | Docling for complex pages, vision for simple |
| `claude_pymupdf_1pp` | 1 | pymupdf4llm text + vision | Can Claude fix library output using vision? |
| `claude_pymupdf_5pp` | 5 | pymupdf4llm text + vision | Cross-page context with library assist |

**Initial subset** (4 papers covering key gaps from 1A-1C):

| Paper | Pages | Why |
|-------|-------|-----|
| hawker_2020 | 14 | Math-heavy, known equation garbling |
| hsu_2020 | 9 | Table-heavy, good reference |
| hansen_2025 | 28 | Heading detection failure (0 headings in pymupdf4llm) |
| paischer_2025 | 24 | Complex tables + math, NeurIPS format |

#### Key Questions

1. **Quality ceiling** — best markdown from images alone?
2. **Pages-per-call tradeoff** — cross-page context vs attention dilution?
3. **Tool-assisted vs pure vision** — does library text alongside images help or confuse?
4. **Cost/time profile** — tokens per page, dollars per document, viable at corpus scale?
5. **Gap coverage** — equations (the #1 gap from 1A), tables (vs GMFT), headings (vs Docling), OCR?

#### Prompt Design

```
You are extracting the content of a scientific/technical document from page images.
Produce clean markdown following these rules:

FORMAT:
- ATX headings (# ## ###) matching the document's section hierarchy
- Pipe tables (| col1 | col2 |) for tabular data, with separator row
- LaTeX math: inline $...$ and display $$...$$
- Figure placeholders: [Figure N: <caption text>]
- No page numbers, running headers, or footers

FIDELITY:
- Preserve ALL numerical values exactly as printed
- Preserve ALL equation content — transcribe to LaTeX
- Preserve table structure including merged cells
- If text is ambiguous or partially obscured, include best guess with [?] marker

OUTPUT:
- Output ONLY the markdown content, no commentary or explanation
- Pages should flow continuously
```

Tool-assisted variants add instructions for Docling MCP or pymupdf4llm text usage.

#### What to Measure

Same metrics as 1A-1C (via `compute_metrics()`), plus: token usage, equation accuracy (manual spot-check), hallucination rate (manual: numbers in output vs PDF).

**Evidence:** `tests/corpus/runs/claude_*/`, `.project/active/claude-headless-deep-dive/findings.md`

### Stage 1 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Old pymupdf_backend.py | Worktree: `src/agentic_mbse/extraction/pymupdf_backend.py` | AcademicHeaderDetector implementation |
| Old postprocess.py | Worktree: `src/agentic_mbse/extraction/postprocess.py` | Header promotion patterns (what to avoid) |
| Old docling_backend.py | Worktree: `src/agentic_mbse/extraction/docling_backend.py` | Subprocess + timeout pattern |
| Old pdf_converter.py | Worktree: `src/doc_ingest/converters/pdf_converter.py` | 2-layer PDF conversion with GMFT, 343 lines |
| Branch audit | `.project/research/20260221-094043_doc-ingest-branch-full-audit.md` | Quality assessment of all capability areas |
| Experiment harness | `tests/corpus/experiment.py` | Pattern for running experiments |
| Metrics module | `tests/corpus/metrics.py` | `compute_metrics()` for comparable measurements |
| Page extraction script | `claude/skills/pdf-analysis/scripts/extract_page.py` | Page rendering to images |
| Old ai_repair.py | Worktree: `src/agentic_mbse/extraction/ai_repair.py` | Cross-validation pattern |
| Old claude_structure.py | Worktree: `src/agentic_mbse/extraction/claude_structure.py` | Prior art on Claude document analysis |

### Stage 1 Definition of Done

- All four sub-stages (1A-1D) have findings documented with comparable metrics
- We can articulate: "pymupdf4llm is best for X, Docling for Y, GMFT for Z, Claude for W, Pandoc for V"
- Known gaps are catalogued with severity and which papers they affect
- No production code written — all output is research notes, experiment runs, and understanding

---

## Stage 2: Head-to-Head Comparison and Ground Truth — STATUS: COMPLETE

**Goal:** Consolidate all Stage 1 results into a single head-to-head comparison, establish ground truth for the test corpus, and produce a definitive scorecard that Stage 3's pipeline experiments optimize against.

**Completed:** 2026-02-22

**Deliverables:**
- `tests/corpus/ground_truth.jsonl` — Machine-readable ground truth for 7 documents (4 full, 3 partial)
- `tests/corpus/comparison_report.md` — 189-line head-to-head comparison with definitive scorecard
- `tests/corpus/metrics.py` — Extended with `GroundTruth`, `AccuracyScore`, `load_ground_truth()`, `score_against_ground_truth()`

**Key results:**
- Claude vision is the accuracy ceiling: ~12% heading error, ~1% table error
- pymupdf4llm best_v1 has heading over-detection on bold-heavy docs (+45 on paischer_2025) and misses gridless tables
- GMFT is exact for grid-lined tables but over-detects TOC/lists
- Docling is accurate where it completes but times out on 67% of corpus
- Pandoc from arXiv HTML is perfect but only available for ~50% of papers
- Recommended Stage 3 pipeline: Pandoc first → pymupdf4llm base → quality gate → Claude vision targeted → GMFT table fix

### Why This Stage Exists

Stage 1 produced metrics for each tool in isolation, spread across four separate findings documents. But the metrics are proxies — heading count, table rows, math symbols — and without ground truth we can't tell which tool is *right*:

- pymupdf4llm finds 14 headings in hawker_2020, Docling finds 17. Which is correct? Is one under-detecting, the other over-detecting, or both?
- pymupdf4llm finds 137 table rows in aries_cost_account, GMFT finds 175, `lines_strict` finds 0. What's the actual count?
- paischer_2025 gets 68 headings with CompositeHeaderDetector. Is that over-detection or are there really that many sections?

Without answers to these questions, the pipeline experiments in Stage 3 would be optimizing against unreliable targets. A pipeline that produces 68 headings might be perfect or terrible — we can't tell.

### Approach

#### Step 1: Build the comparison table

Consolidate Stage 1 results into a single table per document. For each paper in the corpus, collect the metric from every method that was tested:

| Document | Metric | pymupdf4llm (best_v1) | Docling | GMFT | Claude (1D) | Pandoc/HTML | Ground Truth |
|----------|--------|----------------------|---------|------|-------------|-------------|--------------|
| hawker_2020 | Headings | 14 | 17 | — | ? | — | **?** |
| hawker_2020 | Table rows | 0 | — | 40 | ? | — | **?** |
| hawker_2020 | Math symbols | 11 | 11 | — | ? | — | **?** |
| hansen_2025 | Headings | 17 | 18 | — | ? | — | **?** |
| hsu_2020 | Table rows | 56 | — | 88 | ? | — | **?** |
| paischer_2025 | Headings | 68 | — | — | ? | 23 (HTML) | **?** |
| ... | ... | ... | ... | ... | ... | ... | ... |

The **Ground Truth** column starts as `?` — that's what this stage fills in.

#### Step 2: Human review for ground truth

For each document in the initial subset (at minimum the 4 papers from Stage 1D: hawker_2020, hsu_2020, hansen_2025, paischer_2025), establish ground truth by manual inspection:

- **Heading count and hierarchy:** Open the PDF, count the actual section headings, note the levels. This is the definitive answer for "how many headings should the output have?"
- **Table count and row count:** Count the actual data tables (not TOC, not figure captions misdetected as tables). For key tables, note the dimensions (rows x columns).
- **Equation count:** Count display equations and note pages with significant inline math.
- **Content completeness:** Are there any sections that are consistently missing or garbled across all tools?

This doesn't need to be exhaustive for every paper — focus on the papers where tools disagree most, since those are the ones that matter for pipeline decisions.

#### Step 3: Score each method against ground truth

Once ground truth is established, score each method:

| Document | Dimension | Ground Truth | pymupdf4llm | Docling | GMFT | Claude | Best |
|----------|-----------|-------------|-------------|---------|------|--------|------|
| hawker_2020 | Headings | 12 | 14 (+2 false) | 17 (+5 false) | — | ? | pymupdf4llm |
| hansen_2025 | Headings | 16 | 17 (+1 false) | 18 (+2 false) | — | ? | pymupdf4llm |
| hsu_2020 | Tables | 6 tables, 48 rows | 56 rows (+8 noise) | — | 88 rows (+40 TOC) | ? | pymupdf4llm |
| paischer_2025 | Headings | 23 | 68 (+45 false!) | — | — | ? | Claude/Pandoc |

(Example values — actual ground truth TBD by human review.)

This immediately reveals things like: "paischer_2025's 68 headings from CompositeHeaderDetector is massively over-detecting — the real number is ~23 (matching Pandoc's HTML output)."

#### Step 4: Produce the definitive scorecard

Summarize into a per-method strengths/weaknesses table that Stage 3 uses as its optimization target:

| Method | Best For | Accuracy | Speed | Gaps |
|--------|----------|----------|-------|------|
| pymupdf4llm (best_v1) | Body text, simple headings | Headings: ~85% (false positives on math-heavy docs). Tables: mixed. | Fast (1-50s) | Equations, complex tables, non-bold headings |
| Docling (per-page) | Heading detection, clean tables | Headings: ~90%. Tables: good but spanning rows duplicate. | Slow (7-9s/page) | Full-doc timeout, OCR, math spacing |
| GMFT | Table extraction | Tables: ~83% (false positives on TOC). | Very fast (1-32s) | Tables only, no text/headings |
| Claude headless | Equations, OCR, holistic quality | ? (Stage 1D) | Slow, expensive | Cost at scale |
| Pandoc (arXiv HTML) | Papers with arXiv HTML | Headings: 100%. Math: 100%. Tables: 100% (with pre-process). | Fast (<1s) | Only ~50% of papers have HTML |

### What the Human Reviews

To keep this practical, the human review focuses on cases where tools disagree. Specifically:

**High priority (tools give very different answers):**
- paischer_2025 headings: pymupdf4llm says 68, Pandoc says 23 — which is right?
- aries_cost_account tables: pymupdf4llm says 137 rows, GMFT says 175, `lines_strict` says 0
- hawker_2020 headings: pymupdf4llm says 14, Docling says 17
- hansen_2025 headings: pymupdf4llm best_v1 says 17, Docling says 18, pymupdf4llm baseline says 0

**Medium priority (single tool seems off):**
- schulte_1978 headings: pymupdf4llm says 40 — is a 10-page OCR doc really that structured?
- delene_2001 GMFT tables: 202 rows — are these real data tables or TOC/list content?
- energy_amplifier headings: 99 headings with 64 at L1 — how many real L1 sections?

**Low priority (tools roughly agree):**
- hsu_2020: most tools agree on ~4-6 headings, ~50-90 table rows
- seo_2024: tools roughly agree

### Deliverables

1. **`tests/corpus/ground_truth.jsonl`** — Per-document ground truth in machine-readable format:
   ```json
   {"slug": "hawker_2020", "headings": 12, "heading_levels": {"2": 4, "3": 8}, "data_tables": 3, "table_rows": 28, "display_equations": 15, "notes": "Tables are small LCOE comparisons. Math throughout."}
   ```

2. **`tests/corpus/comparison_report.md`** — Human-readable head-to-head comparison with ground truth annotations and the definitive scorecard.

3. **Updated `compute_metrics()` or a new `score_against_ground_truth()`** — Function that compares an extraction's metrics against ground truth and produces accuracy scores (precision/recall for headings, table coverage, etc.)

### Stage 2 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| pymupdf4llm findings | `.project/active/pymupdf4llm-deep-dive/findings.md` | Per-document metrics for 9 configs |
| Docling findings | `.project/active/docling-deep-dive/findings.md` | Per-document metrics, quality notes |
| Pandoc findings | `.project/active/pandoc-deep-dive/findings.md` | arXiv HTML metrics (paischer_2025) |
| Claude headless findings | (Stage 1D, in progress) | Per-document metrics from Claude extraction |
| Experiment runs | `tests/corpus/runs/*/` | Raw metrics.json for every run |
| Test corpus PDFs | `tests/corpus/pdfs/` | The actual documents for manual review |

### Stage 2 Definition of Done

- Head-to-head comparison table covering at least the 4 initial-subset papers across all tested methods
- Ground truth established (by human review) for heading count, table count, and equation presence on those papers
- Each method scored against ground truth with clear accuracy characterization
- Definitive scorecard summarizing: best method per dimension, known failure modes, accuracy ranges
- `ground_truth.jsonl` committed with machine-readable ground truth for the reviewed papers
- Stage 3's pipeline experiments have concrete, trustworthy targets to optimize against

---

## Stage 3: Pipeline Experimentation

**Goal:** Discover how the extraction methods compose into a pipeline by scripting combinations and testing them against the corpus. Let the right abstractions emerge from what actually works, rather than designing interfaces upfront.

### Why This Stage Exists

After Stage 1, we know what each tool does individually. But we don't yet know:
- What calls what, at what granularity (full doc vs page vs region)?
- What data flows between layers (bytes? markdown? images? quality scores)?
- What decisions the quality gate needs to make, and what info it needs?
- Which settings should be pipeline-level config vs per-invocation?
- Whether the pipeline shape is even what we assumed (maybe Claude headless changes everything)

Writing clean `PyMuPDFExtractor` / `DoclingExtractor` / etc. classes before answering these questions would force us to guess the interfaces — and we'd almost certainly guess wrong. This stage is where we figure it out empirically.

### Approach

Build pipeline experiments as **scripts in `tests/corpus/`** (like `experiment.py`). These scripts are allowed to be messy — the goal is rapid iteration on composition hypotheses, not production code. But as patterns stabilize, reasonable abstractions will start to emerge organically.

Each experiment:
1. Scripts a specific pipeline composition (e.g., "pymupdf4llm → quality check → GMFT for broken tables")
2. Runs it against the corpus (or a subset)
3. Measures results with `compute_metrics()` and scores against Stage 2's ground truth
4. Records what worked, what didn't, and what the pipeline needed from each component

### Hypotheses to Test

These are the pipeline compositions we want to try. Listed roughly in order of complexity.

#### H1: pymupdf4llm + GMFT table replacement

**Composition:** Run pymupdf4llm (best_v1 config) on full doc. Run GMFT on full doc. For pages where pymupdf4llm's tables have `<br>` artifacts or failed validation, replace with GMFT's table output.

**What we learn:** Does GMFT's table output cleanly substitute into pymupdf4llm's markdown? What's the merge logic? How do we detect "this table needs replacement"?

**Expected outcome:** Eliminates the 333 `<br>` artifacts from 1A while keeping pymupdf4llm's text/heading quality.

#### H2: pymupdf4llm + Docling per-page for headings

**Composition:** Run pymupdf4llm on full doc. For documents where heading count is suspiciously low (e.g., sparc_overview at 1 heading), run Docling on first 5 pages to get heading structure. Graft Docling's heading hierarchy onto pymupdf4llm's text.

**What we learn:** Can we use Docling's superior heading detection (hansen_2025: 18 vs 0) without replacing the full text? What does "grafting headings" actually look like in practice?

**Expected outcome:** Fixes heading-deficient documents without Docling's timeouts or text quality issues.

#### H3: pymupdf4llm + Claude headless for equations

**Composition:** Run pymupdf4llm on full doc. Detect pages with math garbling (Unicode salad patterns). Render those pages as images. Send to Claude with "transcribe the equations on this page to LaTeX" prompt. Splice the LaTeX equations back into pymupdf4llm's text.

**What we learn:** Is equation splicing practical? Can we reliably detect garbled equations? Does Claude produce correct LaTeX? What's the cost per equation-heavy page?

**Expected outcome:** Fixes the #1 gap from 1A (math garbling) on papers like hawker_2020, energy_amplifier.

#### H4: Claude headless as primary extractor

**Composition:** Skip library extraction entirely. Render all pages to images. Send to Claude in batches of N pages. Concatenate output.

**What we learn:** Is this actually viable as the main extraction path? What's the cost/quality tradeoff vs the library-based approach? Does it eliminate the need for GMFT/Docling entirely?

**Expected outcome:** If Stage 1D shows Claude produces superior output, this tests whether a Claude-primary pipeline is practical at corpus scale.

#### H5: Quality-gated multi-layer pipeline

**Composition:** Run pymupdf4llm. Score each page on multiple quality dimensions (heading presence, table validity, math integrity, text density). Route pages to different enhancement paths based on scores:
- Low heading score → Docling heading detection
- Bad tables → GMFT replacement
- Math garbling → Claude equation transcription
- Low text density → Claude OCR / vision extraction

**What we learn:** What does the quality scoring function actually look like? Is per-page routing practical? What's the overhead of running quality assessment?

**Expected outcome:** A composite pipeline that matches or beats any single tool on every paper in the corpus.

#### H6: Structured source shortcut (arXiv HTML → Pandoc)

**Composition:** For papers with arXiv IDs (detected via pdftotext page 1), fetch HTML from arxiv.org, run through Pandoc with best config from 1B. Fall back to the PDF pipeline for papers without arXiv HTML.

**What we learn:** Does the structured source path integrate cleanly with the PDF pipeline? How do we handle the format difference in output (Pandoc markdown vs pymupdf4llm markdown)? Is it worth the complexity?

**Expected outcome:** Dramatically better output for the ~50% of recent papers that have arXiv HTML.

### What Emerges From This Stage

As we script these experiments, certain patterns will keep recurring:
- "Every pipeline needs to render pages to images" → page rendering utility
- "Every pipeline needs to detect quality issues" → quality assessment interface
- "Every pipeline needs to merge outputs from different sources" → merge/splice abstraction
- "Every pipeline records what it did" → provenance tracking shape
- "Some tools need full-doc input, others per-page" → two calling conventions

These recurring patterns become the natural interfaces for Stage 4's production code. We don't have to guess what a `Converter` protocol should look like — we'll have 6+ pipeline scripts showing us exactly what each component needs to provide and consume.

### Practical Setup

**Directory:** `tests/corpus/pipelines/` (new)
**Scripts:** One Python script per hypothesis (e.g., `h1_pymupdf_gmft.py`, `h2_pymupdf_docling_headings.py`)
**Results:** Output to `tests/corpus/runs/pipeline_h1/`, `pipeline_h2/`, etc.
**Comparison:** Use existing `compare.py` infrastructure + manual quality review

Each script should:
- Be runnable standalone: `python tests/corpus/pipelines/h1_pymupdf_gmft.py --slugs hawker_2020,hsu_2020`
- Save output in the same format as `experiment.py` (per-slug `output.md` + `metrics.json`)
- Log decisions made (e.g., "page 5: GMFT table replacement applied, 3 tables replaced")

### Stage 3 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| **Stage 2 ground truth** | `tests/corpus/ground_truth.jsonl` | **The optimization target — what "correct" looks like** |
| Stage 2 scorecard | `tests/corpus/comparison_report.md` | Per-method accuracy, where each tool wins/loses |
| Stage 1A findings | `.project/active/pymupdf4llm-deep-dive/findings.md` | Baseline metrics, known gaps per document |
| Stage 1C findings | `.project/active/docling-deep-dive/findings.md` | Where Docling adds value, per-page viability |
| Stage 1D findings | (in progress) | Claude headless quality ceiling, cost profile |
| Experiment harness | `tests/corpus/experiment.py` | Pattern for scripting experiments |
| Old quality_gates.py | Worktree: `src/agentic_mbse/extraction/quality_gates.py` | Broken table detection heuristics |
| Old table_extraction.py | Worktree: `src/agentic_mbse/extraction/table_extraction.py` | GMFT integration pattern |
| Old ai_repair.py | Worktree: `src/agentic_mbse/extraction/ai_repair.py` | Cross-validation safety pattern |
| Old claude_structure.py | Worktree: `src/agentic_mbse/extraction/claude_structure.py` | Claude heading detection approach |

### Stage 3 Definition of Done

- At least 3 pipeline hypotheses tested and **scored against Stage 2 ground truth**
- A clear winner (or hybrid) identified for the PDF extraction pipeline
- The quality assessment logic is sketched and tested (what triggers enhancement, what doesn't)
- We have a concrete understanding of: calling conventions, data flow, merge logic, decision points
- A written summary: "This is the pipeline shape that works. Here's what each component needs to do."
- Cost/time budget understood: how much does the full pipeline cost per document?

---

## Stage 4: Design and Implement the Pipeline

**Goal:** Take what worked in Stage 3 and build it properly into the codebase. Start with a thoughtful design phase, then implement with clean interfaces and good test coverage.

### Why Design First

Stage 3's experiment scripts will be messy — that's the point. But before turning them into production code, we need a design step:

1. **Identify the abstractions that emerged** — what are the actual interfaces each component uses?
2. **Decide what lives where** — new module? extension of existing `src/agentic_mbse/extraction/`? separate package?
3. **Define the type system** — extraction results, quality flags, failure categories, provenance records
4. **Plan the test strategy** — unit tests for components, integration tests against corpus

This is a brief, focused design document (not a multi-week architecture exercise). A spec or design doc that captures the decisions, then straight into implementation.

### What to Design

Based on what Stage 3 reveals, the design will likely cover:

**Component interfaces** — What does each extraction method need to expose? Stage 3 will show us whether we need:
- Full-document extraction (pymupdf4llm, GMFT)
- Per-page extraction (Docling, Claude headless)
- Structured source conversion (Pandoc)
- Quality assessment (per-page scoring)
- Targeted enhancement (table replacement, heading grafting, equation transcription)

**Data types** — What flows between components? The old branch's `types.py` (314 lines) is a starting reference, but Stage 3 may reveal we need different types or simpler ones.

**Pipeline orchestration** — How do the components compose? Stage 3's winning hypothesis defines this, but it needs to be generalized and made configurable.

**Provenance and resumability** — The old branch's provenance pattern (atomic JSON writes, crash-safe persistence) is well-designed and likely portable.

### What to Build

- **Clean extraction module** in `src/agentic_mbse/extraction/` — the interfaces and implementations that emerged from Stage 3
- **Quality assessment** — deterministic checks on extraction output
- **Pipeline orchestrator** — the composition logic from the winning Stage 3 hypothesis
- **Type system** — extraction results, quality flags, failure categories
- **Tests** — unit tests for each component, integration tests against corpus
- **CLI integration** — wire into `agentic-mbse extract`

### What to Carry Forward from Old Branch

The porting decisions depend on Stage 3 outcomes, but likely candidates:

**Port (proven, well-designed):**
- Type system patterns from `doc_ingest/types.py` — adapt to match Stage 3's actual needs
- Provenance Manager from `doc_ingest/provenance_manager.py` — atomic writes, crash safety
- Converter Protocol from `doc_ingest/converters/base.py` — if the interface still makes sense
- Cross-validation safety from `extraction/ai_repair.py` — extract_numbers, cross_validate
- GMFT integration from `extraction/table_extraction.py` — if H1 proves out

**Rebuild (Stage 3 showed us a better way):**
- pymupdf_backend.py — new wrapper matching actual pipeline usage
- postprocess.py — only the patterns that Stage 3 showed are necessary
- quality_gates.py — based on what actually triggers enhancement decisions

**Defer (not needed yet):**
- Source Router, CLI, batch processing — Stage 5+

### Stage 4 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Stage 3 results | `tests/corpus/pipelines/`, `tests/corpus/runs/pipeline_*/` | What compositions work, what interfaces emerged |
| Old types.py | Worktree: `src/doc_ingest/types.py` | Type system reference |
| Old converters/base.py | Worktree: `src/doc_ingest/converters/base.py` | Converter Protocol reference |
| Old provenance_manager.py | Worktree: `src/doc_ingest/provenance_manager.py` | Atomic persistence pattern |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Success criteria, failure categories |
| SourceRouter deep dive | `.project/research/20260222-100000_doc-ingest-router-deep-dive.md` | Architecture walkthrough |

### Stage 4 Definition of Done

- Pipeline produces markdown for all corpus PDFs with quality meeting or exceeding Stage 3's best results
- Clean, tested code in `src/agentic_mbse/extraction/`
- Type system is documented and stable
- Provenance tracking captures extraction decisions
- `agentic-mbse extract <pdf_path>` works end-to-end
- Test coverage for components and integration

---

## Stage 5: HTML and Structured Source Routes

**Goal:** Add the non-PDF extraction paths — JATS XML, arXiv HTML, publisher HTML — and the source discovery layer that finds them.

### 5A: HTML/XML Converters

Build converters for structured formats using the interfaces established in Stage 4.

- **JATS XML via Pandoc** — Highest fidelity. Use the Pandoc configuration from Stage 1B.
- **arXiv HTML** — HTML5 with MathML. Pre-process to strip `<figure>` tags, then Pandoc. Use the arXiv ID discovery from Stage 1B.
- **Publisher HTML** — Variable quality, paywall detection needed.

### 5B: Source Discovery

Given a document identifier (DOI, arXiv ID, PMC ID), discover structured alternatives via bibliographic APIs before falling back to PDF.

- **OpenAlex API** — Primary discovery. Batch-capable (50 DOIs/request). Returns PMC IDs, arXiv IDs, OA URLs.
- **arXiv API** — Check HTML availability via HEAD request. PDF always available as fallback.
- **PMC E-utilities** — Fetch JATS XML by PMC ID.
- **Discovery cache** — Cache API results locally (TTL-based) to avoid re-querying.

### 5C: Quality-Ordered Routing

The extraction orchestrator tries sources in quality order with early exit on first success:

```
JATS XML (tier 1) → arXiv HTML (tier 2) → Publisher HTML (tier 3) → PDF pipeline (tier 4)
```

For papers with structured sources, the pipeline automatically finds and uses them — dramatically better output without PDF extraction heuristics.

### Stage 5 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| HTML/XML research | `.project/research/html-trace.md` | Structured source landscape, API access patterns |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Source discovery design, quality tiering |
| Old html_converter.py | Worktree: `src/doc_ingest/converters/html_converter.py` | ArXiv + Publisher HTML implementations |
| Old markdown_converter.py | Worktree: `src/doc_ingest/converters/markdown_converter.py` | JATS + DOCX Pandoc implementations |
| Old source_discoverer.py | Worktree: `src/doc_ingest/source_discoverer.py` | Multi-API discovery + cache |
| Old API clients | Worktree: `src/doc_ingest/api_clients/` | OpenAlex, arXiv, PMC implementations |
| Old extraction_orchestrator.py | Worktree: `src/doc_ingest/extraction_orchestrator.py` | Quality-ordered extraction with early exit |
| Pandoc deep-dive (1B) | `.project/active/pandoc-deep-dive/findings.md` | Recommended Pandoc config, arXiv discovery |
| Discovery validation report | Worktree: `tests/corpus/discovery_validation.md` | Real API behavior validation |

### Stage 5 Definition of Done

- Can extract from: local PDF, local JATS XML, local HTML, arXiv ID (with API discovery), DOI (with API discovery)
- Quality tiering produces measurably better output for papers with structured sources
- Discovery cache prevents redundant API calls
- Paywall detection correctly rejects access-restricted pages
- All converters have unit tests with realistic input samples

---

## Stage 6: Triage, Batch Processing, and Polish

**Goal:** Build the operational tooling for processing document collections.

### What This Includes

- **Triage report generation** — Aggregate provenance records into a categorized Markdown report (success/partial/failed grouped by failure category)
- **Batch processing** — Process multiple documents from a JSONL manifest
- **Retry logic** — Re-process failed/partial documents, skip successes
- **Cache management** — Clear discovery cache, inspect provenance records
- **CLI commands** — `ingest`, `ingest-batch`, `triage-report`, `retry-failed`, `clear-cache`
- **Integration with fusion-tea** — Update `zotero_ingest.py` to use the new pipeline

### Stage 6 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Old CLI | Worktree: `src/doc_ingest/cli.py` (759 lines) | 5 subcommands, pipeline construction |
| Old outcome_classifier.py | Worktree: `src/doc_ingest/outcome_classifier.py` | Outcome + failure category logic |
| Old result_writer.py | Worktree: `src/doc_ingest/result_writer.py` | Persistence of markdown + provenance |
| Resilient ingestion concept, user stories | `.project/concepts/resilient-document-ingestion.md` (lines 29-57) | US-1 through US-7 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Stage 1 research takes too long | Timebox each sub-stage to 1-2 focused sessions. Don't pursue diminishing returns — capture findings and move on. |
| Stage 3 experimentation sprawls | Limit to 6 hypotheses max. Each hypothesis gets 1 session. If it doesn't work in a session, document why and move on. |
| Premature abstraction | Stage 3's whole purpose is to prevent this. Don't write interfaces until pipeline scripts prove what the interfaces need to be. |
| Porting bugs from old branch | Never copy code without understanding it. The old code is a *reference*, not a starting point. |
| Docling availability issues | Docling is always optional. The pipeline must work without it. |
| Claude headless costs too much | Stage 1D and Stage 3 (H3/H4) will reveal the real cost. If too expensive for full corpus, use Claude only for targeted enhancement (equations, OCR). |
| Ground truth is too expensive to establish | Focus on the 4 initial-subset papers and the specific dimensions where tools disagree. Don't try to annotate every page of every document. |
| Scope creep into source discovery before PDF pipeline is solid | Stages are sequential. Stage 5 (structured sources) only starts after Stage 4 (PDF pipeline) is done and tested. |

---

## Summary

| Stage | Focus | Key Deliverable |
|-------|-------|----------------|
| 0 | Prerequisites | Working dev environment with test PDFs |
| 1 | Tool research (1A-1D) | Findings + metrics for each extraction method. No production code. |
| 2 | Head-to-head comparison | Ground truth for test corpus. Definitive scorecard per method. |
| 3 | Pipeline experimentation | Scripted composition experiments. Discover what works, let abstractions emerge. |
| 4 | Design + implement | Thoughtful design from Stage 3 findings, then clean production code with tests. |
| 5 | HTML/XML routes | Structured source converters + source discovery + quality routing |
| 6 | Operational tooling | Batch processing, triage reports, retry, cache management |

**Key structural insight:** Stages 1-3 are research and experimentation. Stage 4 is the transition from research to production. Stages 5-6 extend the production code. The old branch's mistake was jumping from tool exploration directly to production code without the comparison, ground truth, and pipeline experimentation steps — and ended up optimizing against unreliable metrics with interfaces that didn't match actual usage patterns.
