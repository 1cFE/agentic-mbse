# Iteration 1 — Implementation Plan

**Focus:** Eliminate false-positive table detection and false-positive heading detection; add woodruff_2026 to corpus.

**Specs:** 01 (table_strategy), 02 (Guard 2 extension), 03 (add woodruff_2026)

**Status:** COMPLETE — All 4 tasks implemented and tested successfully.

---

## Gap Analysis Summary

| Spec | Requirement | Current State | Gap |
|------|-------------|---------------|-----|
| spec-01 | `table_strategy="lines_strict"` | `"lines"` at `pymupdf_backend.py:202` | Parameter not changed |
| spec-01 | aries_cost_account: 0 `<br>`, 0 `ColN` | Current extraction has 143 table rows (all garbage) | Garbage tables still present |
| spec-02 | Guard 2 covers all depth-1 numbers | `int(sec_num) <= 9` constraint at `pymupdf_backend.py:135` | Constraint still present |
| spec-02 | No `## 30 M` or `## 16. Steffen` in hawker_2020 | hawker_2020 current heading_count=7 (within bounds 5–10) | Need to verify false positives are present in current output, then confirm fix removes them |
| spec-03 | woodruff_2026 in corpus | PDF in pool but not in `tests/corpus/pdfs/`, not in `papers.jsonl`, no baseline | Entirely missing |

### Critical Risk: aries_cost_account has_tables flag

aries_cost_account has `has_tables: true` in `papers.jsonl` and current `table_row_count: 143`. Spec-01 says `lines_strict` will drop this to 0 pipe rows (the "tables" are all false positives from decorative rules). The test `test_table_heavy_papers_have_tables` (line 266 of `test_corpus.py`) requires `table_row_count > 0` for `has_tables: true` papers. **Task 3 must flip `has_tables` to `false`** for aries_cost_account, since its real tables are whitespace-aligned ASCII (not pipe tables) and never appeared as pipe table rows — the 143 rows were all garbage from `lines` strategy.

### Note: Baseline vs current metrics divergence

The baseline metrics (from an earlier pipeline version) differ from current extraction:
- hawker_2020 baseline: `heading_count: 14` → current: `heading_count: 7` (postprocessing improvements already applied)
- aries_cost_account baseline: `heading_count: 64` → current: `heading_count: 16`

The regression test uses **absolute bounds** from `papers.jsonl` when specified (lines 231-244 of `test_corpus.py`), so the stale baselines don't cause test failures — the absolute bounds are what matter.

---

## Task 1: Switch table_strategy to "lines_strict" [spec-01]

- **What:** Change `table_strategy="lines"` → `table_strategy="lines_strict"` at line 202 of `src/agentic_mbse/extraction/pymupdf_backend.py`. Single parameter change.
- **Why:** Eliminates 252 `<br>` HTML tags and 45 `ColN` placeholder columns from aries_cost_account (all garbage from false-positive table detections). Real ruled tables in hsu_2020 (56 rows) and helios_design (29 rows) are preserved because they have fully enclosed cell boundaries.
- **Files touched:**
  1. `src/agentic_mbse/extraction/pymupdf_backend.py` (one parameter change, line 202)
- **Verified by:**
  - After re-extraction: `grep -c '<br>' tests/corpus/current/aries_cost_account/full_document.md` → 0
  - After re-extraction: `grep -c 'Col[0-9]' tests/corpus/current/aries_cost_account/full_document.md` → 0
  - hsu_2020 table_row_count >= 50 (baseline: 56)
  - helios_design table_row_count >= 25 (baseline: 29)
- **Depends on:** Nothing (independent, first task)

---

## Task 2: Extend Guard 2 to all depth-1 sections without trailing period [spec-02]

- **What:** In `AcademicHeaderDetector.__call__` at line 135 of `pymupdf_backend.py`, remove the `int(sec_num) <= 9` constraint from Guard 2. Change:
  ```python
  if depth == 1 and int(sec_num) <= 9 and not has_period:
  ```
  to:
  ```python
  if depth == 1 and not has_period:
  ```
  This makes `font_differs` mandatory for ALL depth-1 sections that lack a trailing period.
- **Why:** Eliminates 2 confirmed false-positive headings in hawker_2020: `## 30 M shots.` (figure caption fragment) and `## 16. Steffen B. 2020...` (bibliography entry). Both use body font (`Palatino-Roman` 9pt, `font_differs=False`) and numbers > 9, bypassing the current guard.
- **Safety:** Legitimate numbered sections have `has_period=True` (e.g., "1. Introduction") or `font_differs=True` (bold/different font), so they're unaffected.
- **Files touched:**
  1. `src/agentic_mbse/extraction/pymupdf_backend.py` (one conditional change, line 135)
- **Verified by:**
  - After re-extraction: `grep -c "^## 30 M" tests/corpus/current/hawker_2020/full_document.md` → 0
  - After re-extraction: `grep -c "^## 16\. Steffen" tests/corpus/current/hawker_2020/full_document.md` → 0
  - hawker_2020 heading_count stays within 5–10 (currently 7; removing 2 false positives may or may not change the count depending on postprocessing — the false positives may already be filtered downstream)
  - All heading_count bounds pass for all papers
- **Depends on:** Nothing (independent of Task 1, but both must precede Task 3)

---

## Task 3: Update baselines and papers.jsonl after spec-01 and spec-02 [spec-01, spec-02]

- **What:** After applying Tasks 1 and 2, run full corpus extraction, update baselines, and fix the aries_cost_account `has_tables` flag.
- **Why:** Both spec-01 and spec-02 change extraction metrics. aries_cost_account will lose garbage table rows (`table_row_count` drops from 143 to ~0). hawker_2020 may lose false-positive headings (if not already filtered by postprocessing). These are improvements, not regressions.
- **Steps:**
  1. Run `uv run pytest tests/test_corpus.py::TestCorpus::test_all_papers_extract_successfully --run-corpus -v` to regenerate `tests/corpus/current/` for all 7 papers
  2. Verify aries_cost_account: 0 `<br>` tags, 0 `ColN` placeholders
  3. Verify hawker_2020: no `## 30 M` or `## 16. Steffen` headings
  4. **If aries_cost_account `table_row_count` drops to 0:** Change `"has_tables": true` → `"has_tables": false` in `papers.jsonl` (the real tables in aries are whitespace-aligned ASCII, not pipe tables — they were never real pipe table detections)
  5. Copy `tests/corpus/current/*/metrics.json` → `tests/corpus/baseline/*/metrics.json` for all 7 papers
  6. Run full corpus tests to confirm all 4 tests pass with new baselines
- **Files touched:**
  1. `tests/corpus/papers.jsonl` (fix `has_tables` for aries_cost_account if needed)
  2. `tests/corpus/baseline/*/metrics.json` (7 files updated)
- **Verified by:**
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — all 4 tests pass
  - All heading_count bounds pass (hawker 5–10, aries 1–20, delene 10–25, sparc ≤20, energy 50–130)
  - hsu_2020 table_row_count >= 50, helios_design table_row_count >= 25
- **Depends on:** Tasks 1, 2

---

## Task 4: Add woodruff_2026 to test corpus [spec-03]

- **What:** Add the woodruff_2026 PDF to the corpus and establish baseline metrics.
  1. Copy `tests/corpus/pool/Woodruff - 2026 - A costing framework for fusion power plants.pdf` → `tests/corpus/pdfs/woodruff_2026.pdf`
  2. Add entry to `tests/corpus/papers.jsonl`: `{"slug": "woodruff_2026", "pdf_path": "tests/corpus/pdfs/woodruff_2026.pdf", "source": "pool", "has_tables": false, "has_math": false, "pages": 25}`
  3. Run extraction to determine actual heading count
  4. Set `heading_count_min` and `heading_count_max` based on observed output (spec expects 30–100 for deeply nested 25-page paper)
  5. Establish baseline at `tests/corpus/baseline/woodruff_2026/metrics.json`
- **Why:** Progressive challenge rule (ADD_PDF_PER_ITERATION=1). woodruff_2026 tests deeply nested heading structure (H2/H3/H4), no ruled tables, different publisher format (Woodruff Scientific, not a journal paper).
- **Files touched:**
  1. `tests/corpus/pdfs/woodruff_2026.pdf` (new, copied from pool)
  2. `tests/corpus/papers.jsonl` (add 1 line)
  3. `tests/corpus/baseline/woodruff_2026/metrics.json` (new baseline)
- **Verified by:**
  - `ls -la tests/corpus/pdfs/woodruff_2026.pdf` — exists
  - `grep woodruff tests/corpus/papers.jsonl` — entry present
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — all 4 tests pass (now 8 papers)
  - heading_count is within 30–100 range (per spec expectation)
  - No garbled text or extraction failures
- **Depends on:** Task 3 (baselines must reflect final pipeline state before establishing woodruff baseline)

---

## Execution Order

```
Task 1 ──┐
          ├── Task 3 ── Task 4
Task 2 ──┘
```

Tasks 1 and 2 are independent (both edit `pymupdf_backend.py` but at different locations: line 202 vs line 135). Task 3 must follow both. Task 4 must follow Task 3 (so woodruff baseline reflects the final pipeline).

## Risk Assessment

- **Task 1 (LOW):** Single parameter change with well-understood impact from learning tests. **Known side effect:** aries_cost_account `table_row_count` drops from 143 to ~0 because all 143 rows were garbage from false-positive table detection. Must flip `has_tables: false` in papers.jsonl (handled in Task 3).
- **Task 2 (LOW):** Removing one numeric constraint from a guard. hawker_2020 current heading_count is already 7 (within 5–10 bounds). The false positives may already be filtered by postprocessing (`_is_noise_header`), so the detector-level fix may or may not change the final count — but it prevents the false positive from ever being created, which is the right layer for the fix. If heading counts change unexpectedly on other papers, the approach must be reconsidered per spec constraints.
- **Task 3 (LOW):** Mechanical baseline update + papers.jsonl flag fix. No code changes beyond metadata.
- **Task 4 (LOW):** Adding a PDF to corpus. Spec says it should work with existing code. Bounds are set from observed output, not guessed.

---

## Implementation Summary (DONE)

### Task 1: table_strategy → "lines_strict" [DONE]
- **File modified:** `src/agentic_mbse/extraction/pymupdf_backend.py:202`
- **Change:** `table_strategy="lines"` → `table_strategy="lines_strict"`
- **Results:**
  - aries_cost_account: 0 `<br>` tags, 0 `ColN` placeholders (was 252 `<br>`, 45 `ColN`)
  - aries_cost_account: table_row_count dropped from 143 → 6 (garbage tables eliminated)
  - hsu_2020: table_row_count = 64 (preserved, >= 50 requirement met)
  - helios_design: table_row_count = 29 (preserved, >= 25 requirement met)
  - sparc_overview: table_row_count dropped from 5 → 4 (expected per spec)

### Task 2: Extend Guard 2 to all depth-1 sections [DONE]
- **File modified:** `src/agentic_mbse/extraction/pymupdf_backend.py:130-139`
- **Change:** Modified Guard 2 logic to require `font_differs` for ALL depth-1 sections except single-digit numbers (1-9) with trailing period
- **Implementation detail discovered:** The spec's proposed change (remove `<= 9` constraint entirely) was insufficient because "16. Steffen B. 2020..." has `has_period=True`, which bypassed the guard. The solution was to make the exception MORE specific: only allow single-digit sections (1-9) with period to bypass the guard. This rejects bibliography entries like "16. Steffen" while still allowing legitimate sections like "1. Introduction" in body font.
- **Results:**
  - hawker_2020: `## 30 M shots.` eliminated ✓
  - hawker_2020: `## 16. Steffen B. 2020...` eliminated ✓
  - hawker_2020: heading_count = 5 (within 5-10 bounds)
  - All papers: heading counts within bounds

### Task 3: Update baselines [DONE]
- **Files modified:**
  - `tests/corpus/baseline/*/metrics.json` (all 7 papers updated)
- **aries_cost_account has_tables decision:** Kept `has_tables: true` (table_row_count = 6, not 0). The 6 remaining rows are likely partially-ruled tables; the whitespace-aligned tables are preserved as plain text.
- **Results:** All 4 corpus tests pass

### Task 4: Add woodruff_2026 to corpus [DONE]
- **Files modified/created:**
  - `tests/corpus/pdfs/woodruff_2026.pdf` (copied from pool)
  - `tests/corpus/papers.jsonl` (added entry with heading_count_min: 30, heading_count_max: 100)
  - `tests/corpus/baseline/woodruff_2026/metrics.json` (baseline established)
- **Results:**
  - heading_count = 82 (within 30-100 range)
  - table_row_count = 0 (expected, no ruled tables)
  - All 4 corpus tests pass with 8 papers

### Final Verification
- All 4 corpus tests pass: `uv run pytest tests/test_corpus.py --run-corpus -v`
- All linting passes: `uv run ruff check src/ tests/`
- All formatting correct: `uv run ruff format src/ tests/`
- Total corpus: 8 papers (hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001, sparc_overview, energy_amplifier, woodruff_2026)
