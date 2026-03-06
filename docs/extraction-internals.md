# PDF Extraction Pipeline: Developer Guide

Developer documentation for the PDF extraction pipeline in `src/agentic_mbse/extraction/`. For CLI usage and user-facing options, see [extraction.md](extraction.md).

## Table of Contents

- [Development Methodology](#development-methodology)
- [Architecture Overview](#architecture-overview)
- [Module Reference](#module-reference)
- [The Quality Gate](#the-quality-gate)
- [Ensemble Table Detection](#ensemble-table-detection)
- [Claude Enhancement](#claude-enhancement)
- [Budget System](#budget-system)
- [Key Design Decisions](#key-design-decisions)
- [Known Limitations](#known-limitations)
- [Test Corpus and Ground Truth](#test-corpus-and-ground-truth)
- [Adding New Components](#adding-new-components)

---

## Development Methodology

This pipeline was built through a structured 4-stage research process, not top-down design. The methodology matters because every threshold, heuristic, and architectural choice traces to a specific experiment. A previous attempt (97 commits, ~25,900 lines on the `ralph/doc-ingest` branch) failed due to premature abstraction — writing pipeline code before understanding the tools.

### Stage 1: Tool Deep-Dives

Each extraction tool was evaluated independently against a 14-document test corpus:

**Stage 1A — pymupdf4llm** (9 configurations tested):
- Discovered that the default `IdentifyHeaders` detector catastrophically misses headings on 6/14 documents when papers use identical font sizes for headings and body text, differentiated only by bold weight.
- Built `CompositeHeaderDetector` — a union of font-size detection and bold+numbering pattern matching. Zero regressions vs default, improved heading detection on 10/13 documents.
- Confirmed `table_strategy="lines"` is correct (`lines_strict` eliminates 100% of tables on one test document; `text` mode is 15x slower with massive over-detection).
- Found `ignore_code=True` eliminates 610 spurious code fences in patent documents.
- Evidence: `.project/active/pymupdf4llm-deep-dive/findings.md`

**Stage 1B — Pandoc** (16 configurations tested):
- Confirmed Pandoc does NOT support PDF as input — eliminating an entire approach early.
- Discovered arXiv ID detection from PDF page 1 (`pdftotext` + regex) is 100% reliable and takes <1 second.
- Found that stripping `<figure>` HTML tags before conversion fixes table/figure mangling.
- Best configuration produces clean markdown with perfect headings, tables, and LaTeX math.
- Only ~50% of papers have arXiv HTML source, making this a shortcut rather than universal.
- Evidence: `.project/active/pandoc-deep-dive/findings.md`

**Stage 1C — Docling & GMFT** (15 experiments):
- GMFT is fast (~2s per document), zero artifacts, correct structured output for grid-lined tables.
- Docling timed out (>300s) on 10/15 documents. Timeout driver is content complexity (TableFormer runs per detected table), not page count.
- Single-page Docling extraction works (7-9s per page) even when full-document extraction times out.
- Evidence: `.project/active/docling-deep-dive/findings.md`

**Stage 1D — Claude Vision** (8 experiments, 75 pages, $15.30 total spend):
- Pure vision is the optimal mode at $0.078/page. Adding supplemental text (+22% cost) produces no quality improvement — Claude ignores the text and extracts from the image.
- Claude's LaTeX equation transcription is irreplaceable. No other tool in the evaluation produces renderable LaTeX from PDF equations.
- Focused repair prompts don't work — Claude rewrites entire pages from vision regardless of "edit only" instructions.
- Evidence: `.project/active/claude-headless-deep-dive/findings.md`

### Stage 2: Ground Truth Comparison

Manual ground truth was established for 7 documents (4 fully reviewed, 3 partially reviewed). Stored in `tests/corpus/ground_truth.jsonl`.

The definitive scorecard:

| Method | Heading Accuracy | Table Accuracy | Cost/doc |
|--------|:---:|:---:|:---:|
| Claude vision | Best (+1 to +4 error) | Best (exact/near) | $1.09 |
| Pandoc (HTML) | Perfect (exact) | Poor (3/53 tables) | Free |
| Docling | Moderate (+3 to +7) | Exact (where completed) | Free |
| GMFT | N/A (tables only) | Mixed (exact to +32) | Free |
| pymupdf4llm | Poor (+2 to +45) | Poor (0 to +84) | Free |

This crystallized the architecture: pymupdf4llm as always-run base, Claude as targeted enhancer for the worst pages, GMFT for table detection, Pandoc as a free early exit for arXiv papers.

Evidence: `tests/corpus/comparison_report.md`

### Stage 3: Pipeline Experimentation

Four complete pipeline implementations were built as standalone scripts (`tests/corpus/pipelines/`):

| Pipeline | Description | Table Error | Cost/doc |
|----------|-------------|:---:|:---:|
| H1 | pymupdf4llm + GMFT table replacement | 1% | $0.00 |
| H3 | pymupdf4llm + Claude for equation pages | — | ~$0.30 |
| H5 | Quality-gated multi-layer (winner) | 8% | $0.12 |
| H6 | Pandoc arXiv HTML shortcut | — | $0.00 |

**H5 won.** Quality gate selectivity: only 10.7% of pages routed to Claude (8/75 in dev set). The remaining pages are kept as pymupdf4llm output. Cost is 12x cheaper than full Claude extraction ($1.46/doc).

A follow-up table detection spike then raised table recall from 46% to 86% by removing a self-inflicted 0.98 confidence threshold and adding Img2Table as a second-pass detector. Claude was confirmed as a perfect false-positive filter (caught all 5 FPs tested).

Evidence: `.project/active/pipeline-experimentation/findings.md`, `.project/active/table-image-spike/findings.md`, `.project/active/table-image-spike/findingsv2.md`

### Stage 4: Production Implementation

The experiment code from Stage 3 was promoted to production modules, not rewritten into a framework. Three implementation items, each audited before merging:

| Item | Modules | Tests |
|------|---------|:---:|
| 1. Types, metrics, quality gate, budget | `types.py`, `metrics.py`, `quality_gate.py`, `pipeline.py` (stub) | 47 |
| 2. Enhancement components | `claude_enhance.py`, `tables.py`, `pandoc_convert.py`, `pymupdf_backend.py` (refactored) | 84 |
| 3. Pipeline orchestration + CLI | `pipeline.py` (full), `extract_cli.py` (rewritten) | 77 |

2,484 lines of legacy code were deleted (superseded modules from the prior attempt).

Evidence: `.project/concepts/doc-extraction/requirements.md`, `.project/concepts/doc-extraction/design.md`

---

## Architecture Overview

The pipeline is a data pipeline, not an object graph. Functions transform typed data in sequence. No abstract base classes, no registry patterns, no plugin systems.

```
PDF ──→ arXiv check? ──yes──→ Pandoc HTML → markdown (done)
                      │
                      no
                      ↓
        pymupdf4llm per-page extraction
                      │
                  list[PageResult]
                      │
        Ensemble table detection (GMFT → Img2Table → Docling)
                      │
                  dict[int, list[DetectedTable]]
                      │
        Table filtering + Claude table enhancement
                      │
        Quality gate (per-page assessment)
                      │
                  list[PageAssessment]
                      │
        Budget allocation (severity-ranked, dollar-capped)
                      │
        Claude page enhancement (targeted pages only)
                      │
        Route per page → merge → PipelineResult
```

Entry point: `extract_pdf()` in `pipeline.py`. Returns a `PipelineResult` with markdown, metrics, per-page decisions, and cost records.

### Module Map

All production code lives in `src/agentic_mbse/extraction/` (~3,900 lines across 14 modules):

| Module | Purpose |
|--------|---------|
| `pipeline.py` | 8-step orchestrator, budget allocation, `PipelineConfig` |
| `types.py` | Data types: `PageAction`, `PageResult`, `DetectedTable`, `PageAssessment`, `PageDecision`, `CostRecord`, `PipelineResult` |
| `metrics.py` | `ExtractionMetrics` computation and ground truth scoring |
| `quality_gate.py` | Per-page quality assessment, routing decisions, heading anomaly detection |
| `tables.py` | Ensemble table detection, filtering, Claude table enhancement, markdown table manipulation |
| `claude_enhance.py` | Claude vision page extraction via CLI, output validation |
| `pandoc_convert.py` | arXiv ID detection, HTML fetch, Pandoc HTML-to-markdown conversion |
| `pymupdf_backend.py` | pymupdf4llm wrapper with `CompositeHeaderDetector`, per-page extraction |
| `postprocess.py` | Legacy deterministic text transforms (not used by the pipeline — see [Design Decisions](#postprocesspy-is-deliberately-not-called)) |
| `base.py` | Shared utilities: output directory management, subprocess timeout handling, `ExtractionResult` |
| `index.py` | Section parsing and INDEX.md generation (orthogonal to pipeline) |
| `docling_backend.py` | DOCX extraction via Docling (not part of PDF pipeline) |
| `pandoc_backend.py` | DOCX extraction via Pandoc (not part of PDF pipeline) |
| `extract_cli.py` | CLI entry point, file discovery, backend routing |

---

## Module Reference

### pipeline.py — Orchestrator

The `extract_pdf()` function coordinates all 8 steps:

1. **arXiv shortcut** — Calls `detect_arxiv_id()` + `convert_arxiv_html()`. On success, returns immediately with a `PipelineResult` sourced from `"pandoc_arxiv"`.
2. **Base extraction** — Calls `extract_pages()` from `pymupdf_backend.py`. This is the only step that can cause a hard failure.
3. **Ensemble table detection** — Calls `detect_tables_ensemble()`. Error-isolated: a crash here means no table data, but the pipeline continues.
4. **Table filtering and enhancement** — Calls `filter_tables()` then `enhance_table_with_claude()` for tables that need it. Budget is deducted from the shared pool.
5. **Quality gate** — Calls `assess_page()` for each page, plus `assess_heading_anomaly()` at document level.
6. **Budget allocation** — `allocate_budget()` ranks pages by severity, selects the top N that fit within the remaining dollar budget.
7. **Claude page enhancement** — Calls `extract_page_with_claude()` for selected pages. Each result is validated before acceptance.
8. **Route and merge** — `route_page()` maps each page to a `PageAction`, then the merge logic assembles the final markdown.

**Error isolation**: Steps 3–7 wrap in try/except. Only Step 2 propagates errors. This means a GMFT crash, Claude timeout, or Pandoc error can never lose the base extraction.

**Configuration**: `PipelineConfig` is a dataclass with sensible defaults matching Stage 3's proven values:

```python
@dataclass
class PipelineConfig:
    budget_usd: float = 2.0        # Per-document Claude budget
    model: str = "sonnet"          # Claude model
    enable_tables: bool = True     # GMFT + Img2Table
    enable_img2table: bool = True  # Img2Table second pass
    enable_docling: bool = False   # Docling third pass (off by default)
    dry_run: bool = False          # Skip Claude calls
    html_path: Path | None = None  # Override arXiv HTML path
```

### quality_gate.py — Per-Page Assessment

The quality gate is purely deterministic — no ML or API calls. It scores each page on three dimensions:

**Math garbling** (severity 0–4):
- `~~text~~` strikethroughs: pymupdf4llm marks garbled math this way → severity 2.0
- `\ufffd` replacement characters → severity 2.0
- `[/]`, `[+]`, `[-]` bracket-encoded operators outside tables → severity 0.3–1.0
- High density of Unicode math symbols (U+2200–U+22FF range) → severity 0.5

All thresholds trace to Stage 3 quality gate experiments. Strikethroughs at severity 2.0 were the strongest single signal for pages that needed Claude re-extraction.

**Table anomalies**:
- `<br>` artifacts in pipe table rows → route to GMFT replacement or strip
- Auto-generated `ColN` headers → these are false-positive tables (pymupdf4llm misinterprets diagrams as tables) → route to strip

**Low text density**: Pages with <200 characters after markdown extraction are likely image-heavy pages that need Claude vision re-extraction.

**Document-level heading anomaly**: If the entire document has 0 headings or >3 headings per page, all page severity scores get a +0.5 boost. This raises the priority of Claude enhancement for documents where pymupdf4llm's heading detection failed entirely.

The `route_page()` function maps assessments to actions using a priority-ordered decision table:

| Priority | Condition | Action |
|:---:|-----------|--------|
| 1 | needs_claude AND within_budget | CLAUDE_REPLACE |
| 2 | has `ColN` headers AND GMFT available | GMFT_REPLACE |
| 3 | has `ColN` headers, no GMFT | STRIP_FALSE |
| 4 | has `<br>` artifacts AND GMFT available | GMFT_REPLACE |
| 5 | has `<br>` artifacts, no GMFT | STRIP_BROKEN |
| 6 | GMFT detected tables, pymupdf4llm found none | GMFT_APPEND |
| 7 | otherwise | KEEP |

When both math and table issues exist on a page, Claude wins (full-page replacement handles both).

### tables.py — Ensemble Table Detection

Table detection uses three complementary detectors that operate on fundamentally different principles:

| Detector | Method | What it catches | Speed |
|----------|--------|-----------------|-------|
| GMFT | Deep learning (PubTables-1M trained) | Grid-lined tables, standard layouts | ~2s/doc |
| Img2Table | OpenCV text-alignment heuristics | Borderless tables, space-aligned data | ~5s/doc |
| Docling | DocLayNet-trained ML detection | Catches tables both others miss | Slow |

The ensemble runs in order: GMFT on all pages → Img2Table only on pages where GMFT found nothing → Docling (optional) on remaining empty pages.

**No confidence threshold.** The Stage 3 table spike proved that a 0.98 confidence threshold was rejecting 7 real tables (10/11 filtered detections were legitimate). Instead, secondary heuristic filters catch obvious false positives:
- Tables with `avg_cell_length > 80` (prose paragraphs misidentified as tables)
- Single-row tables with >4 columns (layout artifacts)

For the rest, Claude acts as the false-positive filter: when Claude returns 0 rows or identifies an image as not-a-table, the detection is dropped.

**Table enhancement flow:**
1. Detector finds a table region and saves a cropped image
2. If DataFrame extraction fails (`extraction_failed=True`), send the cropped image to Claude
3. If DataFrame extraction succeeds but looks suspect (single row, garbled columns), send to Claude
4. Claude extracts a pipe table from the image, or returns empty (= false positive)

On the test corpus, 7/15 GMFT-detected tables on one document had extraction failures — Claude recovered all 7 from the cropped images. Table enhancement costs ~$0.076/table (Sonnet) and is deducted from the shared document budget before page enhancement.

### claude_enhance.py — Claude Vision

Claude enhancement operates in two modes, both using pure vision (image only, no supplemental text):

**Page extraction** (`extract_page_with_claude()`):
- Renders a full page at 200 DPI as PNG
- Sends to `claude -p` CLI with a 15-line extraction prompt (ATX headings, pipe tables, LaTeX math, figure placeholders)
- Validates output: checks length ratio vs original, rejects empty or unreasonably short results
- Cost: ~$0.078/page (Sonnet)

**Table extraction** (via `tables.py`):
- Uses cropped table images from the detection step
- Sends to Claude with a table-specific prompt ("Extract this table as a markdown pipe table")
- Cost: ~$0.076/table (Sonnet)

The Stage 1D experiments showed that "edit only" or "repair" prompts don't work — Claude rewrites entire pages from vision regardless. Full-page replacement is the correct strategy.

**CLI invocation**: `claude -p` with `--output-format json --dangerously-skip-permissions --no-session-persistence`. The `CLAUDECODE` env var is unset to avoid nested session guards. Timeout: 120s.

### pymupdf_backend.py — Base Extraction

The `extract_pages()` function wraps pymupdf4llm with the proven configuration:

```python
page_chunks=True          # Per-page output (pipeline's unit of work)
table_strategy="lines"    # Not "lines_strict" (eliminates real tables)
ignore_code=True          # Eliminates spurious code fences
force_text=True           # Force text extraction even on image-only pages
write_images=False        # No image extraction
dpi=150                   # Resolution for internal rendering
```

The `CompositeHeaderDetector` combines two detection approaches:
1. **Bold pattern matching**: Detects `"1 Introduction"`, `"2.1 Methods"`, all-caps titles
2. **Font-size fallback** (`IdentifyHeaders`): Catches documents where headings differ by font size

The union of both approaches gives zero regressions vs either alone and improves heading detection on 10/13 corpus documents.

### pandoc_convert.py — arXiv Shortcut

When a PDF is detected as an arXiv paper with available HTML, Pandoc conversion produces perfect headings and equations at zero cost. This is the "free lunch" path that skips the entire PDF pipeline.

**Detection sequence** (<1s):
1. Extract page 1 text via pymupdf
2. Regex match for `arXiv:\d{4}\.\d{4,5}(v\d+)?`
3. HTTP HEAD to `https://arxiv.org/html/{id}` to verify HTML availability
4. Fallback: check PDF Creator metadata for `arXiv` string

**Pandoc configuration** (from Stage 1B's 16-configuration evaluation):
- Pre-process: strip `<figure>` tags and CSS transform wrappers (fixes table/figure output)
- Flags: `-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`
- Post-process: strip `\hspace{0pt}` and HTML comment artifacts

### types.py — Data Types

The type system reflects the actual per-page data flow proven in Stage 3:

```
PageResult → PageAssessment → PageDecision → merged markdown
```

Key types:

- **`PageAction`** (enum): KEEP, GMFT_REPLACE, GMFT_APPEND, STRIP_FALSE, STRIP_BROKEN, CLAUDE_REPLACE
- **`PageResult`**: `{page_num: int, markdown: str}` — output of base extraction
- **`DetectedTable`**: `{markdown, confidence, num_rows, num_cols, avg_cell_length, image_path, extraction_failed, detector, source}` — tracks both detection provenance and extraction method
- **`PageAssessment`**: `{page_num, needs_claude, needs_gmft, reasons, severity, math_garble_score, table_anomaly, heading_anomaly, low_text_density}` — quality gate output
- **`PageDecision`**: `{page_num, action, reasons, details}` — recorded for auditability
- **`CostRecord`**: `{page_num, cost_usd, input_tokens, output_tokens, model, elapsed_seconds, table_index}` — `table_index` distinguishes table-level from page-level costs
- **`PipelineResult`**: `{markdown, metrics, decisions, cost, total_cost_usd, source, elapsed_seconds, error}`

---

## Budget System

The per-document Claude budget (default $2.00) is a first-class constraint on the orchestrator. It is shared between table enhancement and page enhancement:

1. **Table enhancement runs first** (higher ROI at ~$0.076/table). Each table Claude call is deducted from the budget.
2. **Page enhancement runs second** with the remaining budget. Pages are ranked by severity (highest first). The `allocate_budget()` function selects the top N pages that fit within the remaining dollars at ~$0.078/page.
3. Pages that exceed the budget fall back to GMFT replacement (if table issues) or are kept as-is.

Budget is a resource constraint on the orchestrator, not a property of individual enhancers. The enhancer functions (`extract_page_with_claude()`, `enhance_table_with_claude()`) don't know about budgets — they process what they're given and report cost.

The default $2.00/document was chosen based on Stage 3 data: the H5 pipeline averaged $0.12/doc on the 4-paper dev set, with the most expensive document (math-heavy, 25 pages) costing ~$0.60. The $2.00 cap provides headroom for larger documents while preventing runaway costs.

---

## Key Design Decisions

### Data pipeline over object graph

The pipeline is implemented as functions transforming typed data in sequence. There are no abstract base classes, no detector registries, no plugin systems. The pipeline shape is code.

**Rationale**: The previous attempt built elaborate abstractions (`RepairRequest` objects, `ExtractionResult` pipelines, region-based repair strategies) before understanding what the pipeline needed to do. All of those abstractions were wrong. Stage 3's experiment scripts used plain functions and dataclasses, and they worked. The production code promotes that pattern directly.

### Full-page replacement over element-level patching

When Claude enhances a page, it replaces the entire page's markdown. There is no line-level splicing or surgical editing.

**Rationale**: Stage 1D tested "focused repair" and "edit only" prompts extensively. Claude ignores repair instructions and rewrites entire pages from vision regardless. Attempting surgical edits adds cost (supplemental text is +22% more expensive) without improving quality. Full-page replacement is simpler, cheaper, and more reliable.

### Per-page routing as the fundamental unit

Pages are assessed, routed, and enhanced individually. The pipeline never operates on the full document as a unit (except for document-level heading anomaly detection, which adjusts per-page scores).

**Rationale**: Stage 3 proved that only ~10% of pages in a typical document need enhancement. Full-document processing (the previous attempt's approach) wastes Claude budget on pages that are already fine, or applies GMFT table replacement to pages without table issues.

### postprocess.py is deliberately not called

The existing `postprocess.py` module (bold header promotion, noise header rejection, ligature repair, page number stripping) is not called by the new pipeline. The old `extract()` function still calls it for backward compatibility.

**Rationale**: Several postprocess transforms are a "promote-then-demote" anti-pattern (SC-5 from the design spec): `promote_bold_headers()` aggressively promotes bold text to headings, then `reject_noise_headers()` filters out false positives. The new pipeline relies on `CompositeHeaderDetector` (which runs inside pymupdf4llm during extraction) for heading detection, and the quality gate + Claude for pages where headings are wrong.

Stage 3 experiments did NOT use postprocess() — the pipeline scripts called `extract_pages()` directly. So the production pipeline without postprocess() matches what Stage 3 proved.

### No confidence threshold on table detection

GMFT detections are kept regardless of confidence score. Claude acts as the false-positive filter instead.

**Rationale**: The Stage 4 table spike proved the 0.98 confidence threshold was rejecting 7 real tables out of 11 filtered detections. Removing it raised recall from 46% to 71%. Claude caught all 5 actual false positives when asked to extract from cropped images (returning empty = "this is not a table"). A statistical filter is redundant when you have a perfect semantic filter.

### Optional dependencies everywhere

Only pymupdf4llm is required. GMFT, Img2Table, Docling, Pandoc, and Claude are all optional with graceful degradation. Each is guarded by `try/except ImportError` or runtime availability checks.

**Rationale**: NFR-1 from the requirements. The pipeline should be useful to someone who just installs the base package and runs `agentic-mbse extract paper.pdf`. Each optional dependency adds capability without being a prerequisite.

---

## Known Limitations

These are documented gaps from the experimentation stages. They are accepted trade-offs, not bugs.

1. **Heading over-detection on bold-heavy documents.** Papers that use bold text liberally (not just for headings) trigger the CompositeHeaderDetector's bold pattern matcher. Example: paischer_2025 detects 55 headings vs 23 ground truth. The quality gate detects this (heading density anomaly) and boosts Claude priority, but may not fix all pages within budget.

2. **Space-aligned tables without grid lines.** Tables that rely on column alignment rather than pipe characters or borders are invisible to all detectors. Example: aries_cost_account has 4 borderless tables (out of 28) that neither GMFT nor Img2Table catches. Docling (optional third pass) covers these.

3. **GMFT over-detection on non-journal documents.** Report-style documents with table-of-contents or numbered lists can trigger false GMFT detections. Example: delene_2001 produces 255 rows vs 150 ground truth. The heuristic filters catch some (avg_cell_length > 80), and Claude catches the rest as a FP filter, but this costs budget.

4. **Math symbol metric is misleading.** `math_symbol_count` in `ExtractionMetrics` counts Unicode math symbols (U+2200–U+22FF). pymupdf4llm scores 8–21 (garbled Unicode fragments) while Claude scores 0–1 (clean ASCII LaTeX). The metric penalizes the better output. Use it for detecting garbling, not for measuring quality.

5. **~50% arXiv HTML availability.** The Pandoc shortcut only works for arXiv papers with HTML source. Non-arXiv papers and older arXiv papers without HTML fall through to the full PDF pipeline.

---

## Test Corpus and Ground Truth

### Corpus

14 unique PDFs in `tests/corpus/pdfs/` covering: text-heavy scientific papers, table-heavy reports, math-heavy physics papers, and a 241-page technical document. The corpus was used throughout all 4 development stages.

### Ground Truth

Human-verified metrics for 7 documents stored in `tests/corpus/ground_truth.jsonl`:

- **Dev set** (4 papers, full ground truth): hawker_2020, hsu_2020, hansen_2025, paischer_2025
- **Hold-out set** (3 papers, partial ground truth): aries_cost_account, delene_2001, energy_amplifier

Ground truth fields: page count, heading count, heading levels, table row count, has_math, has_figures.

### Test Suite

961 tests total across the project. The extraction-specific tests cover:

- **Quality gate**: Every signal (strikethroughs, replacement chars, bracket operators, `<br>` artifacts, `ColN` headers, low density, heading anomaly) has unit tests with synthetic markdown
- **Routing**: All 6 `PageAction` values tested with mock assessments
- **Table filtering**: Each rejection heuristic (avg_cell_length, single-row) has unit tests
- **Table quality assessment**: Extraction failure and suspect quality triggers tested
- **Pipeline orchestration**: All 8 steps tested with mocked dependencies
- **CLI**: Argument parsing, backend routing, output file generation
- **Metrics**: `compute_metrics()` and `score_against_ground_truth()` with known inputs

### Integration Testing

`tests/test_corpus_integration.py` runs the full pipeline against corpus PDFs. These tests are heavier (require PDF files, may invoke external tools) and are separated from the unit test suite.

---

## Adding New Components

The pipeline's design supports evolution without architectural rewrites. Here's how to add common extensions:

### Adding a new quality gate signal

1. Add a detection function in `quality_gate.py` (e.g., `_count_missing_figures()`)
2. Include it in `assess_page()`, setting appropriate `needs_claude`/`needs_gmft` flags and severity
3. Add unit tests with synthetic markdown that triggers the signal
4. No changes needed to routing, merging, or orchestration

### Adding a new table detector

1. Add a `_detect_<name>()` function in `tables.py`
2. Call it from `detect_tables_ensemble()` at the appropriate tier
3. Guard with `try/except ImportError` for optional dependencies
4. Use the same `DetectedTable` type with a different `detector` field

### Swapping Claude for a different LLM

1. Modify `invoke_claude()` in `claude_enhance.py` to call the new model
2. Update cost constants in `PipelineConfig`
3. The budget system and routing logic don't change — they operate on dollar amounts, not model-specific parameters

### Adding a new page action

1. Add a value to the `PageAction` enum in `types.py`
2. Add a routing rule in `route_page()` in `quality_gate.py`
3. Add merge handling in `extract_pdf()`'s step 8
4. Add unit tests for the new route

---

## References

| Resource | Location |
|----------|----------|
| User-facing CLI docs | `docs/extraction.md` |
| Development strategy | `.project/concepts/doc-extraction-development-strategy.md` |
| Requirements spec | `.project/concepts/doc-extraction/requirements.md` |
| Design spec | `.project/concepts/doc-extraction/design.md` |
| pymupdf4llm findings | `.project/active/pymupdf4llm-deep-dive/findings.md` |
| Pandoc findings | `.project/active/pandoc-deep-dive/findings.md` |
| Docling/GMFT findings | `.project/active/docling-deep-dive/findings.md` |
| Claude vision findings | `.project/active/claude-headless-deep-dive/findings.md` |
| Pipeline experiment findings | `.project/active/pipeline-experimentation/findings.md` |
| Table detection spike (v1) | `.project/active/table-image-spike/findings.md` |
| Table detection spike (v2) | `.project/active/table-image-spike/findingsv2.md` |
| Ground truth comparison | `tests/corpus/comparison_report.md` |
| Ground truth data | `tests/corpus/ground_truth.jsonl` |
| Stage 3 experiment scripts | `tests/corpus/pipelines/` |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` |
