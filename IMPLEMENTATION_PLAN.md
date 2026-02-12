# Implementation Plan — Iteration 1

**Focus:** Document structure fidelity — fix header detection across all 7 corpus papers.

**Current state:** The `experiment-init` commit reset the codebase to a clean baseline. The postprocess module has `promote_bold_headers`, `promote_plain_headers`, `clean_header_artifacts`, and `reject_noise_headers`. The pymupdf_backend uses the default font-size-based `IdentifyHeaders` (custom `_academic_header_detector` exists but is commented out — it only checks bold+numbered, which is too conservative). The `tests/corpus/baseline/` directory is empty (0 files). `tests/corpus/current/` has all 7 papers with metrics. All previous iteration work (italic header promotion, unnumbered bold headers, allcaps headers) was stripped.

**Status:** Task 1 completed. Tasks 2-4 pending.

---

## Task 1: Establish baselines [spec-01] — [DONE]

- **What:** Run corpus extraction to populate `tests/corpus/current/`, then copy metrics to `tests/corpus/baseline/{slug}/metrics.json` for all 7 papers.
- **Why:** The comparison report (`compare.py`) errors without baselines; the regression test (`test_no_quality_regression_vs_baseline`) passes vacuously. Spec 01 requires real baseline data so regression testing is meaningful.
- **Files created:**
  - `tests/corpus/baseline/hawker_2020/metrics.json`
  - `tests/corpus/baseline/aries_cost_account/metrics.json`
  - `tests/corpus/baseline/helios_design/metrics.json`
  - `tests/corpus/baseline/hsu_2020/metrics.json`
  - `tests/corpus/baseline/delene_2001/metrics.json`
  - `tests/corpus/baseline/sparc_overview/metrics.json`
  - `tests/corpus/baseline/energy_amplifier/metrics.json`
- **Verification results:**
  - ✅ `ls tests/corpus/baseline/*/metrics.json | wc -l` → 7
  - ✅ `python3 tests/corpus/compare.py` → table with 7 rows, all metrics show `(=)` (baseline == current)
  - ✅ `uv run pytest tests/test_corpus.py --run-corpus -v` → all 4 tests pass (762.49s)
  - ✅ `uv run pytest tests/test_extraction.py tests/test_postprocess.py tests/test_quality_gates.py -v` → all 144 extraction tests pass
  - ✅ `uv run ruff check src/ tests/ && uv run ruff format src/ tests/` → all checks passed
- **Outcome:** Baseline infrastructure is now operational. Regression testing has reference data for all 7 corpus papers.

---

## Task 2: Custom multi-signal header detector via hdr_info [spec-02] — PENDING

- **What:** Replace the default font-size-based `IdentifyHeaders` with a custom `hdr_info` callback in `pymupdf_backend.py` that uses font family, weight, italic flags, AND section-number patterns to classify headings. Must reject math symbols and short fragments.
- **Why:** The default detector fails structurally for academic papers (see experiment-log.md root cause analysis). sparc_overview headers are SMALLER than body text; energy_amplifier assigns 6 heading levels to math symbols; helios_design italic subsections are invisible.
- **Files touched:**
  - `src/agentic_mbse/extraction/pymupdf_backend.py` — replace/evolve `_academic_header_detector`, wire as `hdr_info=` parameter in `extract()` (uncomment and pass `hdr_info=_academic_header_detector`)
  - `tests/test_extraction.py` — update `test_extract_passes_expected_kwargs`: change assertion from `"hdr_info" not in call_kwargs` to verifying `hdr_info` IS passed (line 248)
- **Investigation steps (before implementing):**
  1. **Font metadata survey** — run the learning test from spec-02 to understand body vs header font properties across papers
  2. **Candidate detector on sparc_overview** — verify sections 1-6 get `## `, title gets `# `, body gets `""`
  3. **Candidate detector on energy_amplifier** — verify math symbols do NOT get heading prefixes
- **Design approach (from spec-02):**
  - Section number pattern (`\d+\.?\s+[A-Z]` or `\d+\.\d+\.?\s+`) at span start = strong header signal
  - Font differentiation from dominant body font + short text (<120 chars) + standalone line = likely header
  - Bold flag (flags & 16) for bold section headers
  - Italic flag (flags & 2) combined with section numbering for italic subsections
  - Reject math operators (∫∑∏∂√≈≠≤≥±×÷→←∞)
  - Reject short fragments (single-word spans < 4 chars that aren't section numbers)
  - Depth mapping: top-level numbered sections → `## `, subsections (X.Y) → `### `, sub-sub (X.Y.Z) → `#### `, title (largest font, first page) → `# `
- **Note:** `claude/skills/pdf-analysis/scripts/extract_page.py` already imports `_academic_header_detector` by name and passes it as `hdr_info=`. When we evolve this function, the skill script automatically picks up the improved detector. No changes needed to `extract_page.py`.
- **Verified by:**
  - `python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md` → heading_count >= 10
  - `python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/full_document.md` → H1 count <= 5, heading_count 30-80
  - `grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md` → empty (no math in headings)
  - hawker_2020, aries_cost_account, hsu_2020, delene_2001 heading counts within -10% of baseline
  - `uv run pytest tests/ -v` — all unit tests pass (including updated test_extraction.py)
- **Depends on:** Task 1 (baselines must exist for regression checking)

---

## Task 3: Italic numbered header promotion in postprocess [spec-03] — PENDING

- **What:** Add `promote_italic_headers()` function to `postprocess.py` that promotes italic-wrapped numbered section headers (e.g., `_3.1. Scoping studies_`) to markdown headings. Wire into `postprocess()` orchestrator after `promote_bold_headers()`. Add comprehensive tests.
- **Why:** Safety net for papers where the custom header detector (Task 2) doesn't fully resolve italic subsections. helios_design has 15+ italic subsections like `_3.1. Scoping studies_` that need promotion.
- **Files touched:**
  - `src/agentic_mbse/extraction/postprocess.py` — add regex patterns, `promote_italic_headers()` function, wire into `postprocess()` after `promote_bold_headers()` and before `clean_header_artifacts()`
  - `tests/test_postprocess.py` — add `TestPromoteItalicHeaders` test class
- **Two variants to handle:**
  1. `_X.Y. Title text_` — entire heading in italic
  2. `X.Y. _Title text_` — number outside, title in italic
- **Design constraints:**
  - Must NOT promote italic text mid-paragraph (require blank line boundaries)
  - Must NOT promote TOC entries (trailing page numbers, dot leaders)
  - Correct depth: `_3.1. Title_` → `### 3.1 Title` (H3), `_3.4.1. Title_` → `#### 3.4.1 Title` (H4)
  - Multi-line italic headings should be handled
- **Verified by:**
  - `python3 tests/corpus/metrics.py tests/corpus/current/helios_design/full_document.md` → heading_count >= 20
  - `python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md` → heading_count >= 8
  - `grep '^### ' tests/corpus/current/helios_design/full_document.md | head -10` shows subsections like "### 3.1 Scoping studies..."
  - `uv run pytest tests/ -v` — all tests pass
  - No regressions on other papers (heading counts within -10% of baseline)
- **Depends on:** Task 1 (baselines), ideally done after Task 2 (since Task 2 may already detect some italic headers via hdr_info)

---

## Task 4: Update baselines to reflect improved detection [spec-01, spec-02, spec-03] — PENDING

- **What:** After Tasks 2 and 3, re-run corpus extraction and copy updated metrics to baselines. This captures the new (improved) heading counts as the reference point for future iterations.
- **Why:** Baselines from Task 1 reflect the OLD (broken) header detection. After fixing detection, baselines should reflect the new correct state so future regression testing compares against the improved pipeline.
- **Files touched:**
  - `tests/corpus/baseline/{slug}/metrics.json` (7 files updated)
- **Verified by:**
  - `python3 tests/corpus/compare.py` shows `(=)` for all metrics (baselines match current)
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — all 4 tests pass
  - Final heading counts meet iteration success criteria:
    - sparc_overview: heading_count >= 10
    - helios_design: heading_count >= 20
    - energy_amplifier: H1 count <= 5, total 30-80
    - No math symbols in any heading
- **Depends on:** Tasks 2 and 3

---

## Dependency Graph

```
Task 1 (baselines)
  ↓
Task 2 (custom hdr_info detector)  ←  primary fix
  ↓
Task 3 (italic postprocess)        ←  safety net
  ↓
Task 4 (rebase baselines)
```

## Success Criteria (from iteration-brief.md)

| Metric | Target | Source |
|--------|--------|--------|
| sparc_overview heading_count | >= 10 | spec-02, spec-03 |
| helios_design heading_count | >= 20 | spec-02, spec-03 |
| energy_amplifier H1 count | <= 5 | spec-02 |
| energy_amplifier total headings | 30-80 | spec-02 |
| Math symbols in headings | 0 | spec-02 |
| Regressions on other papers | None (within -10%) | spec-02, spec-03 |
| All corpus tests pass | Yes | spec-01 |
| All unit tests pass | Yes | all specs |
