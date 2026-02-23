# Implementation Plan: Claude Headless Direct Extraction (Stage 1D)

**Status:** Complete
**Created:** 2026-02-22
**Last Updated:** 2026-02-22 (Phase 1 complete)

## Source Documents

- **Spec:** `spec.md`
- **Development Strategy:** `../../concepts/doc-extraction-development-strategy.md` (Stage 1D)
- **pymupdf4llm Findings:** `../pymupdf4llm-deep-dive/findings.md` (baseline gaps driving this work)
- **Docling Findings:** `../docling-deep-dive/findings.md` (Docling/GMFT baselines for comparison)
- **Pandoc Findings:** `../pandoc-deep-dive/findings.md` (arXiv HTML path — the equation quality bar)

## Implementation Strategy

**This is a learning test with a fundamentally different tool.** Stages 1A-1C characterized what libraries can do. Stage 1D asks: what happens if we just ask Claude to extract a document directly from page images?

This is expensive work — every experiment costs real API tokens. The plan is deliberately conservative: start with the cheapest configuration (1 page, pure vision, 4 papers), establish whether the quality ceiling justifies further investigation, then expand only where the data warrants it.

The phases are: **setup → baseline → explore → synthesize**. The explore phase is open-ended but cost-aware.

**Key difference from 1A-1C:** We cannot iterate as freely. A pymupdf4llm experiment on 15 papers takes seconds. A Claude experiment on 4 papers (75 pages) takes minutes and costs money. Every experiment must have a clear question it's answering.

---

## Phase 0: Setup

### Goal

Build the experiment orchestration script, verify `claude -p` accepts image inputs, design the extraction prompt, and render the initial page image set.

### 0.1 Verify Claude Headless with Images

Before building anything, confirm that `claude -p` can process image files:

```bash
# Render a single test page
python claude/skills/pdf-analysis/scripts/extract_page.py \
  tests/corpus/pdfs/hsu_2020.pdf 0 --mode image --output /tmp/test_page.png

# Test claude -p with the image
claude -p "Describe what you see in this image." /tmp/test_page.png --output-format json
```

**What to verify:**
- Does `claude -p` accept image paths as positional arguments after the prompt?
- Does it accept multiple image paths (needed for multi-page experiments)?
- What does `--output-format json` return? Does it include token usage?
- What's the latency for a single page image?

If positional image args don't work, investigate alternatives:
- `--file` flag (mentioned in `claude --help`)
- Piping image data via stdin
- Embedding image paths in the prompt text

**This is the riskiest step.** If `claude -p` can't process images, the entire experiment architecture changes. Do this first.

### 0.2 Design the Extraction Prompt

The prompt is the critical variable. Start with the baseline prompt from the development strategy, saved as a file:

Create `tests/corpus/prompts/extract_baseline.txt`:
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
- Preserve table structure including merged cells (use colspan/rowspan if needed)
- If text is ambiguous or partially obscured, include best guess with [?] marker

OUTPUT:
- Output ONLY the markdown content, no commentary or explanation
- Pages should flow continuously (no page break markers unless a table/section splits)
```

This is the starting point. The prompt may need iteration based on what Claude actually produces — that's part of the exploration.

### 0.3 Build the Experiment Script

Create `tests/corpus/claude_extract_experiment.py` that:

1. **Renders pages to images** — Using pymupdf (same as `extract_page.py --mode image`), saves to a temp directory
2. **Invokes `claude -p`** — With the prompt + image paths, captures stdout
3. **Parses output** — Extract markdown text and (if available) token usage from JSON output
4. **Computes metrics** — Via existing `compute_metrics()` from `metrics.py`
5. **Saves results** — To `tests/corpus/runs/{config_name}/{slug}/`:
   - `output.md` — Raw markdown from Claude
   - `metrics.json` — Same format as 1A-1C runs
   - `cost.json` — Token counts (input, output, total), estimated cost, wall-clock time

**CLI interface** (mirror `experiment.py` where possible):

```
claude_extract_experiment.py <config_name>
    --slugs slug1,slug2          # Papers to process (default: 4-paper subset)
    --pages-per-call N           # Pages sent in one claude -p invocation (default: 1)
    --prompt-file path           # Path to extraction prompt (default: prompts/extract_baseline.txt)
    --supplemental-text          # Also provide pymupdf4llm text alongside images
    --dpi N                      # Image render DPI (default: 200)
    --model model                # Claude model (default: sonnet, for cost efficiency)
    --compare <other_run>        # Compare metrics against another run
    --timeout N                  # Seconds per claude -p call (default: 300)
    --list                       # List existing runs
```

**Implementation notes:**
- ~~Use `subprocess.run(["claude", "-p", prompt, *image_paths, "--output-format", "json"], ...)`~~
- **REVISED (see Implementation Notes 0.1):** Pipe prompt via stdin, reference image paths in prompt text for Read tool. Use `--allowedTools Read --dangerously-skip-permissions --no-session-persistence`. Must unset `CLAUDECODE` env var.
- Parse JSON output for `result` (markdown text), `total_cost_usd`, and `usage`/`modelUsage` (token counts) fields
- For `--supplemental-text`: render pages AND extract pymupdf4llm text, prepend text to prompt as context
- Process pages sequentially within a paper, concatenate results
- For multi-page calls (5pp, 10pp): list all image paths in the prompt, one invocation per batch

**Keep it simple.** This is experiment tooling. No retry logic, no parallelism, no caching. Fail fast and let the operator decide what to do.

### 0.4 Render Initial Page Image Set

Pre-render all pages for the 4-paper initial subset at 200 DPI:

| Paper | Pages | Total Images |
|-------|-------|--------------|
| hawker_2020 | 14 | 14 |
| hsu_2020 | 9 | 9 |
| hansen_2025 | 28 | 28 |
| paischer_2025 | 24 | 24 |
| **Total** | **75** | **75** |

Save to `tests/corpus/page_images/{slug}/page_{N:03d}.png` (0-indexed). These are reused across all experiments — render once.

### 0.5 Initial 4-Paper Subset Rationale

Per the development strategy, these papers were chosen to probe specific gaps:

| Paper | Pages | Why Selected |
|-------|-------|-------------|
| hawker_2020 | 14 | Math-heavy. pymupdf4llm produces equation garbling. Can Claude transcribe to LaTeX? |
| hsu_2020 | 9 | Table-heavy, small. Known good metrics — calibration target. |
| hansen_2025 | 28 | Heading detection failure (pymupdf4llm: 0 headings). Does Claude see section structure? |
| paischer_2025 | 24 | Complex tables + math. Over-detection in pymupdf4llm (137 false table rows). NeurIPS format. |

### Phase 0 Validation

- [x] `claude -p` confirmed working with image inputs (or alternative method documented)
- [x] Token usage / cost data confirmed extractable from output
- [x] Extraction prompt saved to `tests/corpus/prompts/extract_baseline.txt`
- [x] `tests/corpus/claude_extract_experiment.py` runs and produces output for at least 1 paper
- [x] Page images pre-rendered for all 75 pages of the 4-paper subset
- [x] Single-page smoke test: run 1 page of hsu_2020, verify metrics computation works

---

## Phase 1: Baseline — Pure Vision, 1 Page Per Call

### Goal

Run the simplest Claude extraction mode — one page image per `claude -p` call, no tool access, no supplemental text — on the 4-paper subset. Capture metrics AND actually look at the output. Compare against pymupdf4llm best_v1 and Docling baselines.

### What to Do

1. Run the experiment:
   ```bash
   python tests/corpus/claude_extract_experiment.py claude_vision_1pp \
     --slugs hawker_2020,hsu_2020,hansen_2025,paischer_2025 \
     --pages-per-call 1 \
     --compare best_v1
   ```

2. **Capture metrics** for all 4 papers via the harness

3. **Actually read the markdown output** for each paper. For each, note:
   - **Headings:** Are section headings detected? Correct hierarchy? Compare to pymupdf4llm (especially hansen_2025 where pymupdf4llm gets 0)
   - **Tables:** Are pipe tables well-formed? Clean columns? Compare to GMFT baseline
   - **Equations:** Does Claude produce `$...$` / `$$...$$` LaTeX? Or Unicode? Or English descriptions? This is the #1 question.
   - **Fidelity:** Spot-check 5-10 numerical values per paper against the PDF. Any fabricated numbers?
   - **Artifacts:** Running headers/footers included? Page numbers? Figure descriptions vs. placeholders?
   - **Completeness:** Is all text content present? Any dropped paragraphs or sections?

4. **Cost accounting:** From the `cost.json` files, compute:
   - Average input tokens per page
   - Average output tokens per page
   - Average cost per page (at current Sonnet pricing)
   - Total cost for this run
   - Projected cost for the full 15-paper corpus (573 pages)

5. **Write initial findings** to `findings.md`:
   - Per-paper quality observations
   - Equation quality assessment (the key differentiator)
   - Hallucination check results
   - Cost summary
   - How Claude compares to pymupdf4llm best_v1 and Docling on each metric
   - What this suggests investigating next

### Specific Comparisons to Make

| Metric | pymupdf4llm best_v1 | Docling baseline | Claude vision 1pp | Notes |
|--------|---------------------|------------------|-------------------|-------|
| hansen_2025 headings | 17 (composite) | 18 | ? | The heading detection test |
| hawker_2020 math_symbols | 11 | ? | ? | Can Claude produce LaTeX instead of Unicode? |
| hsu_2020 table_rows | 56 | 56 | ? | Calibration — should match |
| paischer_2025 table_rows | 137 (false!) | ? | ? | False positive test — should be much lower |

### Phase 1 Validation

- [x] `claude_vision_1pp` metrics captured for all 4 papers in `tests/corpus/runs/claude_vision_1pp/`
- [x] `findings.md` created with per-paper quality observations
- [x] Equation quality manually assessed on hawker_2020 and paischer_2025 (at least 3 equations each)
- [x] Hallucination check: 5+ numerical values spot-checked per paper against PDF source
- [x] Cost accounting complete: tokens per page, cost per page, projected corpus cost
- [x] Comparison table: Claude vs pymupdf4llm vs Docling (headings, tables, math, chars)
- [x] Known issues and priorities identified for Phase 2

---

## Phase 2: Explore

### Goal

Test two approaches for using Claude to improve pymupdf4llm output: **general repair** (give Claude the text + image, ask it to fix everything) and **focused synthesis** (give Claude the text + image, ask it to fix a specific known-broken feature). Both use single pages.

### Method

Same iterative loop as Stages 1A-1C:

```
1. IDENTIFY — What question are we investigating?
              (driven by Phase 1 observations and known pymupdf4llm gaps)

2. HYPOTHESIZE — What configuration/prompt might answer it?

3. RUN — Execute via the harness (on targeted pages, not the full subset)

4. EVALUATE — Look at the results:
   - Compare against pymupdf4llm best_v1 output for the same page
   - INSPECT ACTUAL OUTPUT — did the specific feature improve?
   - Spot-check fidelity (numbers, equations, structure)
   - Note cost

5. RECORD — Update findings.md with:
   - What we tried and why
   - What we observed (metrics + manual inspection + cost)
   - What we concluded
   - What this suggests investigating next

6. DECIDE — Is the next experiment worth its cost?
```

### Track A: General Repair (`claude_pymupdf_1pp`)

**Question:** If Claude gets both the page image AND pymupdf4llm's text for that page, can it produce better markdown than either alone?

This is the `--supplemental-text` mode already in the harness. Claude receives pymupdf4llm's extracted text as context alongside the page image and is told to generally improve/correct the extraction.

**What to test:**
- Run on the 4-paper subset (same as Phase 1)
- Compare output against Phase 1 (vision-only) and pymupdf4llm best_v1
- Key question: does supplemental text help Claude avoid hallucination while still fixing equations/tables?

**What to look for:**
- Does Claude preserve accurate numerical values from the text while fixing formatting?
- Does it defer to the text for content it can't read clearly in the image?
- Or does it ignore the text and re-extract from scratch?

### Track B: Focused Synthesis

**Question:** Instead of asking Claude to fix everything, can we point it at a *specific* known-broken feature and get a targeted fix?

This is a different prompt pattern. Instead of "extract this page", it's: "Here is the extracted text for this page. Here is the page image. The equation/table marked below is broken. Produce a corrected version of just that feature."

**Why this matters:** General repair is expensive (~$0.085/page for the full page). If we only need Claude to fix equations on math-heavy pages and tables on table-heavy pages, we can target the spend where it matters and skip pages where pymupdf4llm is already good enough.

#### Known Broken Features to Test

These are specific, documented failures from the pymupdf4llm deep-dive (Stage 1A findings):

**Equations (garbled → LaTeX)**

| Paper | Issue | pymupdf4llm Output | What Claude Should Produce |
|-------|-------|-------------------|---------------------------|
| hawker_2020 | Complex equations → Unicode salad | Greek letters survive, multi-line equations garbled | Clean `$$...$$` LaTeX |
| paischer_2025 | Equations → `~~�~~` replacement chars | Strikethrough-wrapped Unicode replacement characters | Clean `$$...$$` LaTeX |
| energy_amplifier | Math symbols → strikethrough artifacts (277 instances) | `~~symbol~~` wrapping on math content | Clean inline `$...$` or display `$$...$$` |

**Tables (broken structure)**

| Paper | Issue | pymupdf4llm Output | What Claude Should Produce |
|-------|-------|-------------------|---------------------------|
| aries_cost_account | `<br>` artifacts + placeholder headers | `Col2`, `Col3` column names, `<br>` in cells | Clean pipe table with real headers |
| paischer_2025 | Diagrams falsely detected as tables (137 rows) | Garbled pipe table from architecture diagram | No table (or a note that this is a figure, not a table) |
| araiinejad_2024 | `<br>` artifacts + cell duplication | Duplicated content across cells | Clean pipe table with correct cell content |
| delene_2001 | Real tables undetected (0 rows) | Plain text where a table should be | Pipe table reconstructed from the image |
| woodruff_2026 | Real tables undetected (0 rows) | Plain text where a table should be | Pipe table reconstructed from the image |

#### Focused Synthesis Prompt Design

Create targeted prompts in `tests/corpus/prompts/`:

**`fix_equation.txt`** — Given a page image + extracted text, fix equations:
```
You are repairing the equation content in an extracted document page.

INPUT:
- A page image from the source PDF
- The text extracted by a library (pymupdf4llm) for this page

TASK:
The extracted text has garbled equations. The library cannot parse mathematical
notation — equations appear as Unicode salad, strikethrough artifacts (~~text~~),
or replacement characters (�).

Using the page image as ground truth, find every equation in the extracted text
and replace it with correct LaTeX:
- Inline math: $...$
- Display math: $$...$$

OUTPUT:
- The full extracted text with equations corrected
- Do NOT change anything else — preserve all non-equation content exactly
- If an equation is ambiguous in the image, include your best guess with [?]
```

**`fix_table.txt`** — Given a page image + extracted text, fix a broken table:
```
You are repairing table content in an extracted document page.

INPUT:
- A page image from the source PDF
- The text extracted by a library (pymupdf4llm) for this page

TASK:
The extracted text has broken tables. Common problems:
- <br> artifacts inside table cells
- Placeholder column headers (Col2, Col3)
- Duplicated cell content
- Garbled content from diagrams falsely detected as tables

Using the page image as ground truth, fix the table(s) in the extracted text:
- Use pipe table format (| col1 | col2 |) with separator row
- Reconstruct correct headers from the image
- Remove <br> artifacts and duplicated content
- If a "table" is actually a diagram/figure, remove the pipe table and replace
  with [Figure N: <description>]

OUTPUT:
- The full extracted text with tables corrected
- Do NOT change anything else — preserve all non-table content exactly
```

**`add_table.txt`** — Given a page image + extracted text where a table was missed:
```
You are adding a missing table to an extracted document page.

INPUT:
- A page image from the source PDF
- The text extracted by a library (pymupdf4llm) for this page

TASK:
The page contains a table that the extraction library missed entirely. The table
content appears as unstructured text (or is missing).

Using the page image as ground truth, find the table and insert a properly
formatted pipe table in the correct location within the extracted text.

OUTPUT:
- The full extracted text with the missing table added
- Use pipe table format (| col1 | col2 |) with separator row
- Do NOT change anything else — preserve all non-table content exactly
```

#### Experiment Plan

Run focused synthesis on **individual pages** with known issues. This is cheap — one `claude -p` call per page, targeting only pages where we know there's a problem.

| Experiment | Paper | Pages | Prompt | Question | Est. Cost |
|-----------|-------|-------|--------|----------|-----------|
| `focused_eq_hawker` | hawker_2020 | 2-3 math-heavy pages | `fix_equation.txt` | Can Claude fix garbled equations to LaTeX? | ~$0.25 |
| `focused_eq_paischer` | paischer_2025 | 2-3 math-heavy pages | `fix_equation.txt` | Same, on NeurIPS format with `~~�~~` | ~$0.25 |
| `focused_table_aries` | aries_cost_account | 2-3 table pages | `fix_table.txt` | Can Claude fix `<br>` artifacts and headers? | ~$0.25 |
| `focused_table_paischer` | paischer_2025 | 1-2 diagram pages | `fix_table.txt` | Can Claude identify false table detection? | ~$0.17 |
| `focused_table_delene` | delene_2001 | 2-3 table pages | `add_table.txt` | Can Claude reconstruct undetected tables? | ~$0.25 |

**Total focused synthesis: ~$1.17** (much cheaper than full-page re-extraction of 75 pages)

**Page selection:** Before running, identify the specific pages by inspecting pymupdf4llm output in `tests/corpus/runs/best_v1/` for each paper. Find the pages with the worst equation garbling / table breakage. Document which pages and why in findings.md.

### Guidance

**Run Track A first.** General repair on the full 4-paper subset gives a broad comparison point. Then Track B tests whether targeted prompts do better on specific features.

**Iterate on focused prompts if output format is wrong.** If Claude adds commentary, changes non-target content, or misunderstands the task — adjust the prompt. Save variants as separate files.

**Consider model choice.** The default is Sonnet. If focused synthesis quality is borderline on Sonnet, try the same pages with Opus. The per-page cost is low enough that a few Opus calls are affordable.

**Follow equation quality closely.** This is the #1 differentiator from Stage 1A. Manually compare Claude's LaTeX output against the source equations. If focused equation repair works well, it's a strong signal for the Stage 3 pipeline.

**Watch for hallucination patterns.** Focused synthesis should have LESS hallucination risk than full extraction (Claude is editing existing text, not generating from scratch). Verify this — spot-check numerical values in fixed tables against the PDF.

**Know when to stop.** If Track A (general repair) is clearly better than Track B (focused synthesis) on the same pages, the focused approach isn't worth the prompt engineering effort. Conversely, if focused synthesis nails equations but general repair doesn't, that's a clear pipeline signal.

### What NOT to Do

- Don't test pages-per-call variations — single page is the unit of work
- Don't skip manual inspection in favor of just looking at metrics
- Don't ignore cost — document the tradeoff for each approach
- Don't build postprocessing or prompt chains — this phase characterizes raw Claude output
- Don't expand to the full 15-paper corpus — stay on the 4-paper subset + targeted pages
- Don't run Docling MCP experiments unless the server is already configured and running

### Phase 2 Validation

- [x] Track A: `claude_pymupdf_1pp` run on 4-paper subset, compared against Phase 1 and best_v1
- [x] Track B: At least 3 focused synthesis experiments run on targeted pages
- [x] Equation repair assessed: Claude LaTeX output vs source on hawker_2020 and paischer_2025
- [x] Table repair assessed: at least 2 table experiments (broken table fix + missing table add)
- [x] False table detection assessed: paischer_2025 diagram pages
- [x] Each experiment has observations in `findings.md` (not just metrics)
- [x] Cost tracked for every experiment (total spend documented)
- [x] Clear comparison: general repair vs focused synthesis on the same pages

---

## Phase 3: Synthesize

### Goal

Consolidate what we learned into the deliverables from the spec: comparison table, equation assessment, hallucination assessment, cost projection, and pipeline recommendation.

### What to Do

1. **Finalize findings.md** — Add a "Final Assessment" section covering:

   **a. Cross-Tool Comparison Table**
   For each of the 4 papers, side-by-side metrics:
   ```
   | Paper | Metric | pymupdf4llm | Docling | GMFT | Claude (best) |
   ```
   Include: headings, table_rows, math_symbols, char_count, extraction_time, cost.

   **b. Equation Quality Assessment**
   Manual comparison of Claude LaTeX vs. source equations for hawker_2020 and paischer_2025. Include actual examples:
   ```
   Source equation (page image): [reference]
   Claude output: $$E = mc^2$$
   pymupdf4llm output: E = mc²
   Verdict: [correct / partially correct / wrong]
   ```

   **c. Hallucination Risk Assessment**
   Summary of all numerical spot-checks. Any fabricated values? Any systematic patterns (e.g., rounding, approximation, invention)?

   **d. Cost Projection**
   ```
   | Configuration | Tokens/page | Cost/page | Cost for 4-paper subset | Projected 15-paper corpus |
   ```

   **e. General Repair vs Focused Synthesis**
   Which approach produces better results? When is each appropriate? Cost comparison.

   **f. Pipeline Recommendation**
   Clear statement of where Claude headless adds value in the Stage 3 pipeline:
   - "Use Claude for X" (specific document/page characteristics)
   - "Don't use Claude for Y" (where libraries are sufficient)
   - "Claude is cost-effective when Z" (break-even analysis)
   - Implications for Stage 2 (gap analysis) and Stage 3 (pipeline assembly)

2. **Document what we didn't test** — Experiments deferred and why (Docling MCP, full corpus, Opus model, etc.)

3. **Update the development strategy** — Add a note to Stage 1D with status and pointer to findings

### Phase 3 Validation

- [x] `findings.md` has a "Final Assessment" section with all 6 subsections above
- [x] Cross-tool comparison table covers all 4 papers and all tools
- [x] Equation quality manually assessed with actual examples (not just metrics)
- [x] Hallucination risk explicitly addressed with spot-check evidence
- [x] Cost projection complete with per-page and per-corpus estimates
- [x] Pipeline recommendation is clear and actionable
- [x] Total experiment spend documented

---

## Key Resources

| Resource | Location | Use |
|----------|----------|-----|
| Development strategy (1D spec) | `../../concepts/doc-extraction-development-strategy.md` | Experiment matrix, prompt design, key questions |
| pymupdf4llm findings | `../pymupdf4llm-deep-dive/findings.md` | Baseline gaps, best_v1 config |
| Docling findings | `../docling-deep-dive/findings.md` | Docling/GMFT baselines |
| Pandoc findings | `../pandoc-deep-dive/findings.md` | arXiv HTML equation quality bar |
| Experiment harness (library) | `tests/corpus/experiment.py` | Pattern for the Claude experiment script |
| Metrics module | `tests/corpus/metrics.py` | `compute_metrics()` for comparable results |
| Comparison tool | `tests/corpus/compare.py` | Baseline comparison |
| Page rendering | `claude/skills/pdf-analysis/scripts/extract_page.py` | `render_image()` for page→PNG |
| pymupdf4llm best_v1 runs | `tests/corpus/runs/best_v1/` | Comparison baseline (pymupdf4llm) |
| Docling baseline runs | `tests/corpus/runs/docling_baseline/` | Comparison baseline (Docling) |
| GMFT baseline runs | `tests/corpus/runs/gmft_baseline/` | Comparison baseline (GMFT) |
| Corpus registry | `tests/corpus/papers.jsonl` | Paper metadata |
| Corpus PDFs | `tests/corpus/pdfs/` | Source documents |
| Claude CLI help | `claude --help` | Headless mode flags |

---

## Cost Budget

Rough estimates based on Sonnet pricing (~$3/MTok input, ~$15/MTok output) and ~1,500 input tokens per page image:

> **UPDATE (Phase 0 finding):** A single page image consumed ~61K input tokens via the Read tool workaround, not ~1,500. The estimates below are likely **10-40x too low**. The test call on hsu_2020 page 0 (a light cover page) cost $0.076. Phase 1 will calibrate actual per-page costs on content-heavy pages.

| Experiment | Pages | Description | Est. Cost |
|------------|-------|-------------|-----------|
| claude_vision_1pp (Phase 1) | 75 | Pure vision baseline, 4 papers | ~$6.40 |
| claude_pymupdf_1pp (Track A) | 75 | General repair, 4 papers | ~$8.00 (more input tokens) |
| Focused synthesis (Track B) | ~12-15 | Targeted pages with known issues | ~$1.20 |
| **Total (3 experiment groups)** | | | **~$15.60** |

These are rough — actual costs depend on output length (which varies by page content) and whether image token counts are higher than estimated. Phase 1 will calibrate these numbers.

**Budget guidance:** If Phase 1 costs significantly more than expected, reduce the Phase 2 experiment count accordingly. The goal is learning, not completeness.

---

## Implementation Notes

### Phase 0 Progress (2026-02-22)

#### 0.1 Claude Headless Image Verification — COMPLETE

**Critical finding: `claude -p` does NOT accept image files as positional args or via `--file`.**

The plan assumed `subprocess.run(["claude", "-p", prompt, *image_paths, ...])` — this does not work. Positional args after the prompt are not image inputs.

**Working method: Read tool workaround.** The prompt references image file paths by absolute path, and Claude uses its built-in Read tool (which supports images natively) to load them. This requires:
- Prompt piped via **stdin** (not as positional arg)
- `--allowedTools Read` to permit the Read tool
- `--dangerously-skip-permissions` to avoid interactive prompts
- `--no-session-persistence` to avoid session file accumulation
- Environment must have `CLAUDECODE` unset (nested session guard)

**Subprocess invocation pattern (revised from plan):**
```python
import subprocess, os

env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}

prompt = f"Read the image at {image_path} and extract content..."
result = subprocess.run(
    ['claude', '-p', '--model', 'sonnet', '--output-format', 'json',
     '--dangerously-skip-permissions', '--no-session-persistence',
     '--allowedTools', 'Read'],
    input=prompt, capture_output=True, text=True, timeout=120, env=env
)
```

**Token/cost data confirmed available** in `--output-format json` response:
- `total_cost_usd` field (e.g., `0.076` for one cover page)
- `usage.input_tokens`, `usage.output_tokens`
- `modelUsage.{model}.costUSD` breakdown
- `duration_ms` for API timing

**Latency:** ~16s wall clock for a single page (cover page, light content). Expect longer for content-heavy pages.

**Token cost surprise:** A single page image consumed ~61K input tokens (not the ~1,500 estimated in the plan). This is because image tokens in the Claude API are much larger than text tokens. The plan's cost estimates ($2.60 per 75-page run) are likely **significantly underestimated** — actual costs may be 10-40x higher. Phase 1 will calibrate.

**Alternative considered but deferred:** The Claude Agent SDK (Python) supports streaming input with base64 image content blocks, which would be more direct. But the Read tool approach is simpler and sufficient for experiment tooling.

**Reference:** Working pattern derived from `/home/reid/1cfe/agentic-mbse_doc-ingest/lib.sh` `claude_generate()`.

#### 0.2 Extraction Prompt — COMPLETE

Saved to `tests/corpus/prompts/extract_baseline.txt` per plan spec. No changes from the planned prompt text.

#### 0.3 Experiment Script — IN PROGRESS

Building `tests/corpus/claude_extract_experiment.py`. Key deviations from plan:
- Prompt piped via stdin (not positional arg) — see 0.1 findings
- Image paths referenced in prompt text for Read tool consumption
- For multi-page calls: all image paths listed in prompt, Claude reads each sequentially
- `--output-format json` used to capture cost/token data alongside result text

#### 0.4 Page Image Rendering — COMPLETE

- Created `tests/corpus/scripts/render_pages.sh`
- Rendered all 75 pages for 4-paper subset at 200 DPI
- Output: `tests/corpus/page_images/{slug}/page_{NNN}.png` (0-indexed)
- Total size: 31 MB
- Verified: hawker_2020 (14), hsu_2020 (9), hansen_2025 (28), paischer_2025 (24)

#### Files Created So Far

| File | Purpose |
|------|---------|
| `tests/corpus/prompts/extract_baseline.txt` | Baseline extraction prompt |
| `tests/corpus/scripts/render_pages.sh` | Page image rendering script |
| `tests/corpus/scripts/test_claude_image.sh` | Verification script for claude -p + images |
| `tests/corpus/page_images/{slug}/page_{NNN}.png` | Pre-rendered page images (75 total, not committed) |

### Phase 0 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Created `tests/corpus/claude_extract_experiment.py` (310 lines) — full experiment harness
  - CLI with all planned flags: config_name, --slugs, --pages-per-call, --prompt-file, --supplemental-text, --dpi, --model, --compare, --timeout, --list
  - Subprocess invocation via stdin-piped prompt + Read tool workaround (per 0.1 findings)
  - Saves output.md + metrics.json + cost.json per slug (compatible with existing runs/)
  - Batches pages by --pages-per-call, processes sequentially, concatenates markdown
  - Comparison table with cost column (extends experiment.py's print_comparison pattern)
- Prompt file (`tests/corpus/prompts/extract_baseline.txt`) — unchanged from plan
- Page images (`tests/corpus/page_images/`) — 75 pre-rendered PNGs (unchanged from prior session)
- Verification scripts (`tests/corpus/scripts/`) — unchanged from prior session

**Smoke Test Results (hsu_2020, 9pp, 1pp mode, Sonnet):**
- table_rows=56 (exact match vs best_v1), headings=4 (vs 5 in best_v1), math=0 (expected)
- Cost: $0.76 total, ~$0.085/page, 208s wall clock (~23s/page avg)
- Output: clean markdown with proper headings, pipe tables, figure placeholders, references
- Token reporting: `usage.input_tokens` only shows stdin prompt tokens (36), not image tokens consumed via Read tool. `total_cost_usd` reflects true cost.

**Issues:**
- `usage.input_tokens` underreports (excludes Read tool image consumption). Added `modelUsage` capture and docstring note.
- Cost is ~$0.085/page (Sonnet), confirming the 0.1 finding that estimates were 10-40x low. Projected cost for 4-paper subset (75pp): ~$6.40. For full corpus (573pp): ~$49.

### Phase 1 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Created `findings.md` with full Phase 1 analysis (cross-tool comparison, equation assessment, hallucination check, cost summary)
- Ran `claude_vision_1pp` on all 4 papers (75 pages, $5.84 total)
- hawker_2020 required a separate run (timed out on first attempt during multi-paper run)

**Key Findings:**
1. **Equation quality is the #1 result.** Claude produces clean, correct LaTeX from page images — 21 display equations + ~93 inline in hawker alone. No other tool in 1A-1D does this.
2. **Table detection is accurate:** matches Docling (40, 56, 15 rows), avoids pymupdf4llm's false positives (paischer: 55 real vs 137 false).
3. **No hallucinated numerical values** across 20+ spot-checks on all 4 papers.
4. **math_symbol_count metric is misleading** — counts Unicode math symbols, not LaTeX. Claude scores 0-1 but has vastly superior equation coverage.
5. **Cost: $0.078/page avg**, projected $44.70 for full corpus. Prohibitive for full extraction, viable for targeted use.
6. **Character count 20-28% lower** than pymupdf4llm on some papers — mostly from cleaner output (no artifacts), not content loss.

**Issues:**
- hawker_2020 timed out during the initial 4-paper run. Had to run separately. Consider increasing timeout for math-heavy papers.
- "GyroSwim" typo in paischer table cells (14 instances) — small-font OCR error.
- Running headers partially included despite prompt instruction to omit them.

### Phase 2 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Modified `tests/corpus/claude_extract_experiment.py`:
  - Added `pymupdf4llm` import and per-page text extraction (`extract_page_text()`)
  - Fixed supplemental text to work per-page (was only provided to first batch)
  - Added `--pages` CLI flag for selecting specific pages
  - Added `_page_num_from_image()` helper, `get_pdf_path()` helper
- Created focused synthesis prompts:
  - `tests/corpus/prompts/fix_equation.txt`
  - `tests/corpus/prompts/fix_table.txt`
  - `tests/corpus/prompts/add_table.txt`
- Rendered page images for aries_cost_account (6 pages) and delene_2001 (5 pages)
- Ran Track A (`claude_pymupdf_1pp`) on all 4 papers (75pp, $7.16)
- Ran 5 Track B experiments on 14 targeted pages ($2.12)
- Updated `findings.md` with full Phase 2 analysis

**Key Findings:**
1. General repair (Track A) does NOT work — supplemental text is ignored, output identical to pure vision, costs 22% more
2. Focused synthesis (Track B) does NOT surgically edit — Claude rewrites entire pages from vision regardless of prompt instructions
3. Pure vision is the optimal Claude extraction mode — no benefit from supplemental text or focused prompts
4. Focused prompts occasionally help (equation repair on paischer Eq 1 was better), but not consistently
5. Reasoning/commentary leaks into all focused synthesis outputs — a systematic output format issue
6. Total Phase 2 spend: $9.28

**Deviations:**
- Track B focused synthesis experiments were more expensive per page than estimated ($0.15 vs $0.08) due to supplemental text token overhead
- Added aries_cost_account and delene_2001 experiments (not in original 4-paper subset) by rendering targeted page images
- Smoke test run (`claude_pymupdf_smoke`) was added to verify harness changes before the full Track A run

### Phase 3 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added "Final Assessment" section to `findings.md` with all 6 subsections:
  a. Cross-tool comparison table (4 papers × 5 tools × 7 metrics)
  b. Equation quality assessment with 3 side-by-side examples (pymupdf4llm vs Claude LaTeX)
  c. Hallucination risk assessment (20+ spot-checks, 0 hallucinations found)
  d. Cost projection (per-page, per-document, targeted vs full extraction)
  e. General repair vs focused synthesis comparison (neither helps, pure vision is optimal)
  f. Pipeline recommendation (pymupdf4llm primary + Claude vision on targeted pages)
- Updated development strategy (`doc-extraction-development-strategy.md`) with Stage 1D COMPLETE status and findings pointer
- Updated `findings.md` status to "Phase 2 complete" and added "What We Did NOT Test" section
**Deviations:**
- None — Phase 3 is a synthesis/documentation phase, no experiments were run

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete** (2026-02-22)
