# PDF Extraction v2: PR Readiness Plan

**Date:** 2026-02-07
**Branch:** pdf-extract
**Status:** Pre-PR
**Context:** Code review identified 4 must-do items, 4 should-do items, and 3 nice-to-haves before merging to master.

---

## Background

A thorough code review of the `pdf-extract` branch (5 commits, ~4,500 lines across 22 files) found that:

- Architecture is clean: three layers map to separate modules with clear responsibilities
- Safety mechanisms (cross-validation, graceful degradation) are well-designed
- Measured improvements are real: 15/18 tables fixed, 7/7 indexes non-empty
- But the benchmark is stale (run before the final 2 commits), GMFT output hasn't been qualitatively verified, and several small code issues exist

This plan defines the specific work needed before opening the PR.

---

## Must-Do (Blocking PR)

### 1. Re-run corpus benchmark after final commits

The last benchmark was run at commit `b45cee3`. Two subsequent commits changed:
- `e559be9`: `extract_tabular_lines()` filter and tightened table caption regex in `ai_repair.py` and `quality_gates.py`
- `f34d8bc`: `dataframe_to_pipe_table()` integer-like float rendering, postprocessing wired into `extract_page.py`

**Work:**
- Run `uv run python scripts/benchmark_corpus.py` on the current HEAD
- Compare results row-by-row against the Phase 3 table in `pdf-extraction-v2.md` lines 668-677

**Acceptance criteria:**
- [ ] Benchmark completes without errors on all 7 documents
- [ ] GMFT fixes >= 15/18 detected table problems (no regression from Phase 3)
- [ ] All 7 documents produce non-empty INDEX.md files
- [ ] No document has fewer sections than the Phase 3 count
- [ ] Total corpus runtime < 300s (Phase 3 was ~144s; allow headroom)
- [ ] Results table pasted into this document under "Results" section below

### 2. Spot-check GMFT output quality

The benchmark counts tables fixed but does not verify the content is correct. A table "fixed" by GMFT could have wrong data, missing rows, or garbled cells.

**Work:**
- Open `full_document.md` for docs 2235, 2236, and 2237 (the three docs where GMFT fixed the most tables)
- For each doc, find 2-3 GMFT-generated pipe tables and compare against the source PDF
- Check: correct column headers, correct number of rows, no garbled cell content, numbers match the PDF

**Acceptance criteria:**
- [ ] At least 6 GMFT-generated tables manually verified across the 3 documents
- [ ] All verified tables have correct column headers matching the source PDF
- [ ] All verified tables have the correct number of data rows (within +/- 1 row for header/footer ambiguity)
- [ ] No verified table contains a number that differs from the source PDF by more than rounding
- [ ] Any quality issues found are documented here with page number and description

### 3. Add `hdr_info` callback to `extract_page.py`

The single-page skill script (`claude/skills/pdf-analysis/scripts/extract_page.py`) calls `pymupdf4llm.to_markdown()` without the custom `_academic_header_detector` callback or `table_strategy="lines"` that `pymupdf_backend.py` uses. This means Layer 3 repair prompts and interactive skill usage get lower-quality input.

**Work:**
- In `extract_page.py`, import `_academic_header_detector` from `pymupdf_backend`
- Pass `hdr_info=_academic_header_detector` and `table_strategy="lines"` to `pymupdf4llm.to_markdown()`
- Verify the import works (the skill script runs standalone, so the import path must resolve)

**Acceptance criteria:**
- [ ] `extract_page.py` passes `hdr_info` and `table_strategy` matching `pymupdf_backend.py`
- [ ] `uv run python claude/skills/pdf-analysis/scripts/extract_page.py <test_pdf> 0 --mode markdown` produces output with `##` headers (not `**bold**` headers) for a doc that has bold-numbered sections
- [ ] No circular import issues

### 4. Add page-map validation warning in `quality_gates.py`

If `detect_problems()` is called on markdown without `<!-- PAGE:N -->` markers, all lines get `page_num=-1` and GMFT silently skips every table. This is the exact class of bug that caused the Phase 3 crash. A runtime warning prevents silent failure.

**Work:**
- In `detect_problems()`, after building the page map, check if >50% of lines have `page_num == -1`
- If so, emit `warnings.warn("Over 50% of lines lack PAGE markers; page-specific repairs may target wrong pages", stacklevel=2)`
- Add a unit test that verifies the warning fires on marker-free markdown

**Acceptance criteria:**
- [ ] `detect_problems("plain markdown without markers")` emits a `UserWarning` containing "PAGE markers"
- [ ] `detect_problems(markdown_with_markers)` does NOT emit a warning
- [ ] Warning does not prevent detection from proceeding (non-blocking, informational only)
- [ ] Unit test added to `tests/test_quality_gates.py`

---

## Should-Do (Quality, Non-Blocking)

### 5. Add thousand-separator stripping to `extract_numbers()`

`extract_numbers("1,234.56")` currently yields `{"1", "234.56"}` because the comma splits the number. Financial and cost tables (common in our corpus — doc 2237 is a cost study) use this format. This causes false cross-validation rejections when Layer 3 returns `"1234.56"`.

**Work:**
- In `ai_repair.py`, strip commas and underscores from input text before regex matching: `text = text.replace(",", "").replace("_", "")`
- Add tests for thousand-separator numbers

**Acceptance criteria:**
- [ ] `extract_numbers("$1,234.56")` returns a set containing `"1234.56"`
- [ ] `extract_numbers("1_000_000")` returns a set containing `"1000000"`
- [ ] Existing `test_ai_repair.py` tests still pass
- [ ] New test added for thousand-separator edge case

### 6. Type-narrow `RepairRequest.region_type`

Currently a bare `str` with values `"table" | "equation" | "structure"` by convention only. A typo silently passes through filtering logic.

**Work:**
- Add `RegionType = Literal["table", "equation", "structure"]` to `base.py`
- Change `RepairRequest.region_type` type annotation to `RegionType`
- No runtime enforcement needed — the `Literal` type provides IDE/mypy checking

**Acceptance criteria:**
- [ ] `RepairRequest.region_type` annotated as `Literal["table", "equation", "structure"]`
- [ ] `uv run mypy src/agentic_mbse/extraction/base.py` passes (or has no new errors)
- [ ] All existing tests pass unchanged

### 7. Clean up defensive `getattr()` calls in `extract_cli.py`

Lines 220-222 use `getattr(args, "no_tables", False)` for flags that are registered in argparse. This is dead defensive code that obscures the real interface.

**Work:**
- Replace `getattr(args, "no_tables", False)` with `args.no_tables`
- Same for `args.enhance` and `args.max_repair_pages`
- Verify all three flags are registered in `register_extract_subcommand()`

**Acceptance criteria:**
- [ ] No `getattr()` calls remain for `no_tables`, `enhance`, or `max_repair_pages`
- [ ] `uv run agentic-mbse extract --help` shows all three flags
- [ ] `uv run pytest tests/test_extraction.py` passes

### 8. Add targeted edge-case tests

The code review identified specific gaps where real-world data could break the pipeline silently.

**Work — add these tests:**

| Test | File | What it validates |
|------|------|-------------------|
| Page map with no markers | `test_quality_gates.py` | `_build_page_map(["line1", "line2"])` returns `[-1, -1]` |
| Page map with 0-indexed marker | `test_quality_gates.py` | `<!-- PAGE:0 -->` handled correctly (or rejected) |
| Overlapping repair requests | `test_table_extraction.py` | Two requests with overlapping `markdown_lines` don't corrupt output |
| Header >80 chars | `test_postprocess.py` | Plain header promotion with a 120-character title |
| Bracketed section title | `test_postprocess.py` | `_is_noise_header("5 [Critical Path]")` — document whether this is noise or not |

**Acceptance criteria:**
- [ ] At least 5 new tests added across the test files listed
- [ ] Each test has a docstring explaining the edge case
- [ ] All new and existing tests pass: `uv run pytest tests/test_postprocess.py tests/test_quality_gates.py tests/test_table_extraction.py tests/test_ai_repair.py -v`

---

## Nice-to-Have (v2.1, Not Blocking)

### 9. Formal scored evaluation using the original rubric

The v1 evaluation scored the pipeline on 5 dimensions (markdown structure, index quality, image extraction, table extraction, equation handling) with a 1-5 scale. No equivalent scored evaluation exists for v2. This would provide a real "2.68 → X.XX" number.

**Acceptance criteria (if done):**
- [ ] Each of the 7 documents scored on the same 5 dimensions as the v1 evaluation
- [ ] Overall score computed as weighted average
- [ ] Score comparison table (v1 vs v2) added to the concept doc

### 10. Integration test with real GMFT

Mocked tests missed the Phase 3 CPU crash bug. A real GMFT test would catch integration regressions.

**Acceptance criteria (if done):**
- [ ] Test marked `@pytest.mark.slow` and skipped when GMFT not installed
- [ ] Uses a small fixture PDF (2-3 pages with one table)
- [ ] Verifies `enhance_tables()` produces a pipe table with correct row count

### 11. Thread-safe GMFT singleton

The module-level `_detector`/`_formatter` cache has a race condition on first load. Low risk for CLI usage but prevents future server-context use.

**Acceptance criteria (if done):**
- [ ] `_get_detector()` and `_get_formatter()` use `threading.Lock()` with double-check pattern
- [ ] Comment added explaining the singleton is designed for CLI (short-lived process) usage

---

## Results

*To be filled in after executing the plan.*

### Benchmark Results (Item 1)

| ID | Doc | Sections | Table Problems | GMFT Fixed | Pipe Lines | Time |
|----|-----|----------|---------------|------------|------------|------|
| 2241 | Eester et al. (2026) | 15 | 0 | 0 | 3 | 20.4s |
| 2238 | Lampe & Manheimer (1998) | 6 | 1 | 1 | 7 | 14.9s |
| 2233 | Araiinejad & Shirvan (2025) | 6 | 0 | 0 | 0 | 19.6s |
| 2232 | Handley et al. (2021) | 15 | 0 | 0 | 0 | 18.2s |
| 2235 | FIA Global Fusion (2025) | 27 | 9 | 8 | 271 | 36.5s |
| 2236 | FAS Market Report | 62 | 1 | 1 | 309 | 35.8s |
| 2237 | LANL Cost Study | 50 | 6 | 5 | 82 | 27.2s |
| **TOTAL** | | | **17** | **15** | | **172.6s** |

**Comparison to Phase 3:**
- Regressions: None. All section counts identical. GMFT fixes identical (15).
- Improvements: Table problems reduced 18→17 (tightened caption regex in `f34d8bc` eliminated a false-positive detection on doc 2237). GMFT hit rate improved from 83% to 88% (15/17).

### GMFT Quality Spot-Check (Item 2)

| Doc | Page | Table Description | Cols Correct | Rows Correct | Data Correct | Notes |
|-----|------|-------------------|-------------|-------------|-------------|-------|
| 2235 | 9 | Costing Code Components (4-col institutional table) | Yes (4 cols) | Yes (~20 rows per page) | Yes | `<br>` tags from PDF wrapping; OCR artifacts (`uxes` for "fluxes") |
| 2235 | 25-31 | National Lab/University AI table (spans 6 pages) | Yes (4 cols) | Yes | Yes | Split into separate pipe tables at page breaks; some duplicate content from page continuation |
| 2236 | 8-9 | Acronyms table (62 rows) | Yes (2 cols) | Yes | Yes | Minor OCR: `Artifcial` missing 'i'; split at page break |
| 2236 | 41 | Major Investors in Fusion (Table 14, 20 rows) | Yes (6 cols) | Yes | Yes | Monetary values preserved; `<br>` wrapping in narrow cols |
| 2236 | 57-58 | Digital Twin Platform Providers (Table 20, ~27 rows) | Yes (5 cols) | Yes | Yes | `_>_13,000` for ">13,000" (OCR); Website col shows "Link" not URLs |
| 2237 | 21 | Radial Build geometry (10 rows) | Yes (5 cols) | Yes | Yes | Values match: Plasma 57.0 m³, First Wall 24.5 m³, etc. |
| 2237 | 18-19 | Materials Properties (15 rows) | Yes (6 cols) | Partial — bottom rows merged | Yes (where present) | Rows near bottom merged: "SS316 Nb3Sn" and "Incoloy GdBCO He NbTi" should be separate |
| 2237 | 46 | Financial Parameters (13 rows) | Empty headers | Yes | Yes | Side-by-side param layout; GMFT used empty headers |

### Issues Discovered

| Item | Severity | Description | Resolution |
|------|----------|-------------|------------|
| Row merging in 2237 materials table | Low | Bottom rows of materials table merged (e.g., "SS316 Nb3Sn" as one row instead of two) | Known GMFT limitation with dense tables; Layer 3 `--enhance` can fix |
| `<br>` word wrapping in narrow columns | Low | Investor names and descriptions split mid-word across lines | Cosmetic; data is correct |
| Empty headers in financial table | Low | GMFT used empty column headers for side-by-side parameter layout | Unusual table format; data values are correct |
| Multi-page table splitting | Low | Tables spanning page breaks rendered as separate pipe tables | Architecture limitation; each page is processed independently |
| Minor OCR artifacts | Low | `Artifcial` (missing 'i'), `uxes` (for "fluxes"), `_>_13,000` | Pre-existing OCR issues from pymupdf4llm, not GMFT |
| Triple table duplication in doc 2235 | Medium | Large multi-page tables (Fusion AI/ML Tools, National Lab/University AI Projects) appear 3x back-to-back: once as raw GMFT output with `~~strikethrough~~`/`<br>` formatting, twice as cleaner AI-repaired copies. Explains the unusually high 271 pipe-line count for this doc. | GMFT + Layer 3 repair outputs are concatenated rather than the repair replacing the original when a single table spans 6+ pages. Data is correct in all copies. Investigate in v2.1 — only affects `--enhance` path on very large multi-page tables |

---

## Exit Criteria

**PR is ready when:**
1. All 4 must-do acceptance criteria sections are fully checked off
2. Benchmark results show no regressions from Phase 3
3. GMFT spot-check finds no data correctness issues (or issues are documented and accepted)
4. Full test suite passes: `uv run pytest tests/ -v` with 0 failures
5. Results section above is filled in with actual data
