# Spec: v4 Pipeline Output Quality Regressions

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-27 10:20 PST
**Updated:** 2026-02-27 21:00 PST
**Complexity:** MEDIUM
**Branch:** doc-ingest-clean

---

## Business Goals

### Why This Matters

The v4 pipeline's primary consumer is LLMs reading extracted domain knowledge. Noise lines waste context tokens and confuse downstream agents. Duplicate content is worse — the same table data appearing twice in different formats creates ambiguity about which version is authoritative. Garbled equations and tables rendered as unstructured text are worst — they are actively misleading.

The old pipeline (`extract()` → `postprocess()` → `full_document.md`) did not have the noise/duplication problems. The quality gate blind spots are new — the v4 pipeline introduced a quality gate that was supposed to route bad pages to Claude, but it misses entire classes of structural failures.

### Success Criteria

- [ ] `output.md` contains zero running headers and zero bare page numbers for the TEA cost analysis document
- [ ] No page contains the same table data in both flat-text and pipe-table format
- [ ] Pages where GMFT found tables that pymupdf missed are routed to Claude (not GMFT_APPEND) when budget allows
- [ ] Equation rendering failures (text fragments like `_C_ = _CEEDB_`) trigger Claude enhancement
- [ ] Output file size is smaller than or equal to the old `full_document.md` for equivalent content (currently 1846 vs 1448 lines — delta is noise + duplication)
- [ ] No regressions on existing test suite

### Priority

These are defects in the just-shipped EPIC-PDFV4-001 (Items 1-3 complete). Should be fixed before or as part of Item 4 (integration tests, cleanup, ship).

---

## Problem Statement

### Problem 1: Running Headers and Page Numbers in Output

**Current state:** The v4 pipeline output for the TEA cost analysis (12 pages) contains:
- 11 instances of the running header: `_L.S. Araiinejad and K. Shirvan ... Applied Energy 401 (2025) 126567_`
- 11 bare page numbers (2, 3, 4, ... 12) on standalone lines

The old pipeline output (`full_document.md`) has zero of both.

**Root cause:** The design (§2.4) decided `extract_pages()` should NOT call `postprocess()`. The rationale correctly identified that header promotion/demotion functions are a promote-then-demote anti-pattern (SC-5). But it also skipped `strip_page_numbers()` and `strip_running_headers()`, which are pure cleanup functions — NOT promote-then-demote. The design dismissed them as "cosmetic, not quality-affecting for downstream use."

**Why the design rationale was wrong:** 22 noise lines in a 12-page document is not cosmetic. Running headers are the single most repeated text pattern in the output. For an LLM reading this as domain knowledge, they are pure noise that displaces useful content in the context window. This also violates the pipeline's own **NFR-4 (No Silent Garbage)**: "The pipeline must never silently produce output that is worse than pymupdf4llm alone." The old pipeline stripped these; the new pipeline doesn't; therefore the new output is worse on this dimension.

**Evidence:**
- Design §2.4 line 143: "strip_page_numbers() / strip_running_headers() — page number and header removal... Acceptable: these are cosmetic, not quality-affecting for downstream use."
- `postprocess.py:161-244`: `strip_page_numbers()` and `strip_running_headers()` — pure `str→str` transforms with no promote-then-demote
- `output.md` (new): 11 running headers + 11 page numbers = 22 noise lines
- `full_document.md` (old): 0 running headers + 0 page numbers
- NFR-4 in requirements.md: "The pipeline must never silently produce output that is worse than pymupdf4llm alone."

### Problem 2: GMFT_APPEND Is the Wrong Action (Routing Bug)

**Current state:** When GMFT detects tables on a page where pymupdf4llm produced no pipe tables, the pipeline routes to `GMFT_APPEND` — appending the GMFT pipe table at the end of the page but **leaving the garbled text in place**. The user sees both versions: garbled text first, then a correct pipe table buried at the bottom.

6 of 12 pages in the TEA document are GMFT_APPEND (pages 2, 3, 6, 8, 9, 10 per `decisions.json`). This is the **dominant failure mode** — 50% of pages.

Example — Table 2 (Direct Costs) on page 2 (0-indexed):
- Lines 150–228: garbled flat-text rendering from pymupdf4llm (`COA Number and Name Description` → `**20** **Direct Costs**` → `21.1 Land & Land Rights` as flowing paragraphs)
- Lines 364–385: GMFT-appended pipe table with correct structure (`| COA | Number and Name | Description |`)

**Root cause:** `route_page()` rule 5 (`quality_gate.py:410-415`) fires when GMFT found tables and pymupdf produced no pipe tables. It routes to GMFT_APPEND because it interprets this as "pymupdf missed the table entirely." But the reality is pymupdf *attempted* to render the table and produced garbled text. The correct action is CLAUDE_REPLACE — have Claude re-extract the whole page from the image, which handles both the table AND surrounding content (equations, text flow).

The quality gate didn't flag these pages because there are no character-level garbling signals (no strikethroughs, no replacement chars, no bracket operators). Budget was NOT the constraint — only $0.45 of $2.00 was spent. The quality gate simply didn't flag these pages.

**Why this matters:** The duplication is the visible symptom, but the real problem is routing. Even if you deduplicate the text, the garbled rendering still lacks proper table formatting. The right fix is to send these pages to Claude.

**Evidence:**
- `decisions.json`: pages 2, 3, 6, 8, 9, 10 all `gmft_append` — 0 flagged for Claude
- `cost.json`: $0.45 spent of $2.00 budget (3 page replacements + 1 table enhancement)
- `quality_gate.py:410-415`: rule 5 routes to GMFT_APPEND without considering Claude
- `tables.py:132-143`: `insert_tables_at_end()` — pure append, no dedup
- Research: `.project/research/20260227-210000_extraction-quality-failures.md`

### Problem 3: Quality Gate Blind to Structural Failures

**Current state:** The quality gate detects character-level garbling (strikethroughs, replacement chars, bracket operators, Unicode math density). It is completely blind to:

1. **Tables rendered as unstructured text.** pymupdf4llm with `table_strategy="lines"` misses borderless tables (those with shading but no grid lines). The table content appears as flowing paragraphs. No quality gate signal fires.

2. **Equations rendered as text fragments.** Equation 2.2 in the PDF is a standard scaling formula. pymupdf4llm renders it as:
   ```
   (
   _Pnew_
   _C_ = _CEEDB_

   ) _n_

   (2.2)
   ```
   This is italic text fragments. None of the four garbling signals (strikethroughs, replacement chars, bracket operators, Unicode math density) fire because it looks like normal italic text.

3. **No cross-reference with GMFT results.** The quality gate and GMFT detection are independent pipeline steps. When GMFT finds tables on a page where pymupdf produced no pipe tables, that's a strong signal of structural failure. But the quality gate never sees GMFT results and can't factor them into severity scoring.

**Root cause:** The quality gate was designed and validated against the 14-document test corpus where the dominant failure mode was character-level garbling. The Araiinejad paper's dominant failure mode is structural — pymupdf renders tables/equations as text. The test corpus didn't adequately cover this pattern.

**Why this matters:** Pages 2 and 3 have both table failures AND equation failures. The quality gate assigns severity 0.0 to both. With a $2.00 budget and only $0.45 spent, Claude could have fixed all 6 problematic pages at ~$0.47 additional (with sonnet). The intelligence and budget were available — the signal was missing.

**Evidence:**
- `quality_gate.py:98-147`: `_assess_math_garbling()` — four signals, none detect text fragments
- `quality_gate.py:252-301`: `assess_page()` — no input for GMFT results
- `pipeline.py:289-301`: quality gate runs on raw pymupdf pages before table decisions
- `output.md` lines 288-298: equation 2.2 rendered as text fragments with severity 0.0

### Problem 4: Images Not Extracted or Linked

**Current state:** The v4 pipeline output contains zero inline image references. The old pipeline output (`full_document.md`) has 8 `![](images/...png)` references with corresponding PNG files in `images/`.

The old pipeline's `extract()` function (`pymupdf_backend.py:160-221`) calls pymupdf4llm with `write_images=True, image_path=str(images_dir)`. This extracts embedded images, saves them as PNGs, and inserts `![](images/filename.png)` markdown references inline.

The v4 pipeline's `extract_pages()` function (`pymupdf_backend.py:124-157`) calls pymupdf4llm with `write_images=False`. Images are never extracted, never saved, and no references appear in the markdown. On Claude-enhanced pages, Claude produces text placeholders like `[Figure 5: caption]`, but on KEEP and GMFT pages, figures are silently dropped entirely.

**Root cause:** `extract_pages()` was written for per-page processing where the image output directory wasn't established at extraction time. The `write_images=False` setting was carried over from Stage 3 experiment scripts that focused on text quality, not image fidelity. The design didn't account for image extraction as a requirement.

**Why this matters:** For a techno-economic analysis paper, the figures (cost breakdowns, sensitivity analyses, comparison charts) are critical domain knowledge. An LLM reading the extracted document has no access to the visual data — the figures are simply gone. The old pipeline preserved them; the new one silently drops them.

**Evidence:**
- `pymupdf_backend.py:143`: `write_images=False` in `extract_pages()`
- `pymupdf_backend.py:173-174`: `write_images=True, image_path=str(images_dir)` in old `extract()`
- `output.md`: 0 image references (grep for `!\[`)
- `full_document.md`: 8 image references with corresponding PNGs in `images/`

---

## Scope

### In Scope

- **Postprocess cleanup:** Eliminate running headers, bare page numbers, and Unicode ligatures from v4 pipeline output (pure `str→str` transforms already proven in `postprocess.py`)
- **Image extraction:** Enable `write_images=True` in `extract_pages()` so images are saved and linked inline, matching the old pipeline's behavior
- **Routing fix:** When GMFT finds tables that pymupdf missed, route to CLAUDE_REPLACE (if within budget) instead of GMFT_APPEND. Fall back to GMFT_APPEND only when Claude budget is exhausted.
- **Quality gate cross-reference:** Boost severity score on pages where GMFT detected tables but pymupdf produced no pipe tables. This ensures these pages compete for Claude budget.
- **Equation-fragment detection:** Add a quality gate signal for equation rendering failures (text fragments with isolated equation numbers like `(2.2)`)

### Out of Scope

- Re-integrating header promotion/demotion from `postprocess.py` (those ARE the promote-then-demote anti-pattern, correctly excluded by §2.4)
- Figure caption promotion (orthogonal, not a regression)
- New table detectors or changes to GMFT/Img2Table configuration
- Changes to Claude prompts or Claude output validation

### Constraints

- `strip_running_headers()` uses frequency counting across the full document (threshold=3 occurrences). This requires the joined final markdown, not per-page content — each header appears once per page, so per-page detection won't work.
- `strip_page_numbers()` uses blank-line-delimited regex, which works per-page or on joined output.
- The routing fix requires the quality gate to know about GMFT results. Currently these are independent pipeline steps (GMFT = step 3, quality gate = step 4). The fix either passes GMFT results into `assess_page()` or adds a post-assessment cross-reference step.
- Equation-fragment detection must avoid false positives on normal italic text in paragraphs. The signal should be scoped to short isolated lines with parenthesized equation numbers.

---

## Requirements

### Functional Requirements

#### Postprocess Cleanup (from original spec)

1. **FR-1**: The v4 pipeline output MUST NOT contain running headers (repeated short lines appearing on multiple pages). The existing `strip_running_headers()` in `postprocess.py` already solves this for the old pipeline.

2. **FR-2**: The v4 pipeline output MUST NOT contain bare page numbers on standalone lines. The existing `strip_page_numbers()` in `postprocess.py` already solves this for the old pipeline.

3. **FR-3**: Unicode ligature codepoints (U+FB00–FB04) SHOULD be replaced with ASCII equivalents. The existing `repair_ligatures()` in `postprocess.py` already solves this.

4. **FR-4**: The pipeline MUST NOT re-introduce the promote-then-demote header processing pattern from `postprocess.py` (`promote_bold_headers`, `promote_plain_headers`, `reject_noise_headers`). The design §2.4 rationale for excluding those is correct.

#### Image Extraction (regression)

5. **FR-5**: `extract_pages()` MUST extract embedded images and save them to an output directory, matching the old `extract()` behavior. Images MUST be linked inline in the per-page markdown with `![](images/filename.png)` references.

6. **FR-6**: The pipeline orchestrator MUST establish an images output directory and pass it to `extract_pages()`. Image paths in per-page markdown MUST be relative to the output directory so that `output.md` references resolve correctly.

#### Routing Fix (from research)

7. **FR-7**: When GMFT detects tables on a page where pymupdf4llm produced no pipe tables, the pipeline MUST route to CLAUDE_REPLACE (if within budget) instead of GMFT_APPEND. This replaces rule 5 in `route_page()`.

8. **FR-8**: When Claude budget is exhausted, GMFT_APPEND remains the fallback action — but this is now the degraded path, not the default.

9. **FR-9**: The v4 pipeline output MUST NOT contain the same table data in both flat-text and pipe-table format. When a proper pipe table is appended (GMFT_APPEND fallback), the corresponding flat-text rendering SHOULD be removed. (This is the fallback when FR-7/FR-8 cannot be satisfied due to budget.)

#### Quality Gate Improvements (from research)

10. **FR-10**: The quality gate MUST accept GMFT detection results as input. When GMFT found tables on a page that pymupdf rendered without pipe tables, the page severity MUST be boosted (recommended: +1.5). This ensures these pages compete for Claude budget alongside pages with character-level garbling.

11. **FR-11**: The quality gate SHOULD detect equation-fragment rendering failures. Heuristic: isolated lines matching `^\s*\(\d+(\.\d+)?\)\s*$` (equation numbers) preceded by short lines with heavy italic content and fragmented math-like text (e.g., `_C_ = _CEEDB_`). Severity boost: +1.0.

### Non-Functional Requirements

- NFR-4 compliance: output MUST be at least as clean as the old `extract()` path for page numbers, running headers, and ligatures
- No new external dependencies
- Existing tests continue to pass
- Claude cost increase from routing fix MUST stay within the existing $2.00/doc budget (estimated: +$0.47/doc with sonnet for 6 additional pages)

---

## Acceptance Criteria

### Postprocess Cleanup

- [ ] TEA cost analysis `output.md` has 0 running header lines (was 11)
- [ ] TEA cost analysis `output.md` has 0 bare page number lines (was 11)
- [ ] Output contains no Unicode ligatures (U+FB00–FB04)

### Image Extraction

- [ ] TEA cost analysis `output.md` has inline image references (`![](images/...)`) matching the old pipeline (was 8 in `full_document.md`, currently 0)
- [ ] Image PNG files are saved to the output `images/` directory
- [ ] Image paths in `output.md` resolve correctly relative to the output directory

### Routing & Quality Gate

- [ ] Pages where GMFT found tables and pymupdf produced no pipe tables are routed to CLAUDE_REPLACE (not GMFT_APPEND) when within budget
- [ ] On the TEA document, pages 2, 3, 6, 8, 9, 10 are routed to CLAUDE_REPLACE instead of GMFT_APPEND (given $2.00 budget)
- [ ] Table 2 (Direct Costs) is rendered as a proper pipe table without garbled flat-text duplication
- [ ] Equation 2.2 is rendered as LaTeX ($$...$$), not as text fragments
- [ ] Total Claude spend on the TEA document stays within $2.00 budget
- [ ] No page contains the same table data in both flat-text and pipe-table format

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] GMFT_REPLACE pages are not affected (they already strip + replace)
- [ ] CLAUDE_REPLACE pages are not affected (Claude output doesn't contain running headers)
- [ ] KEEP pages with no tables are not affected
- [ ] Quality gate severity scores for GMFT-missed-table pages are higher than before

---

## Related Artifacts

- **Research:** `.project/research/20260227-210000_extraction-quality-failures.md` — root cause analysis that identified Problems 2 and 3
- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (EPIC-PDFV4-001, Item 4)
- **Design (parent):** `.project/concepts/doc-extraction/design.md` — §2.4 is the design decision that caused Problem 1; FR-7 GMFT_APPEND definition that caused Problem 2
- **Requirements (parent):** `.project/concepts/doc-extraction/requirements.md` — NFR-4 (No Silent Garbage)
- **Existing cleanup code:** `src/agentic_mbse/extraction/postprocess.py` — `strip_page_numbers()`, `strip_running_headers()`, `repair_ligatures()`
- **Key source files:**
  - `pymupdf_backend.py:143` — `write_images=False` disables image extraction (Problem 4)
  - `pymupdf_backend.py:173-174` — old `extract()` with `write_images=True` (reference)
  - `quality_gate.py:410-415` — rule 5 that routes to GMFT_APPEND (Problem 2)
  - `quality_gate.py:98-147` — `_assess_math_garbling()` blind to text fragments (Problem 3)
  - `quality_gate.py:252-301` — `assess_page()` has no GMFT input (Problem 3)
  - `tables.py:132-143` — `insert_tables_at_end()` pure append (Problem 2 fallback)
  - `pipeline.py:289-301` — quality gate step runs before table routing
- **Evidence (fusion-tea repo):**
  - `knowledge/sources/tea_dt_mfe_cost_analysis/output.md` — current broken output
  - `knowledge/sources/tea_dt_mfe_cost_analysis/full_document.md` — old pipeline output (no duplication)
  - `knowledge/sources/tea_dt_mfe_cost_analysis/decisions.json` — routing decisions
  - `knowledge/sources/tea_dt_mfe_cost_analysis/cost.json` — $0.45 of $2.00 spent

---

**Next Steps:** After approval, proceed to `/_my_design`
