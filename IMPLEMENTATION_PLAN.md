# Implementation Plan — Iteration 2 (Phantom Headings)

## Status Summary

Specs 01 and 02 are **partially implemented**. The core detector guards (section number caps, font_differs requirements, alpha_count minimum, multi-word font_differs gate) and postprocess guards (section number caps, figure/table rejection, numbered bibliographic detection) are all in place and tested.

**Remaining blockers**: 3 papers fail acceptance criteria. Root causes are well understood.

### Current vs Target Heading Counts

| Paper | Baseline | Current | Spec Target | Status |
|-------|----------|---------|-------------|--------|
| sparc_overview | 5 | 44 | ≤ 20 | **FAIL** — ~24 numberless reference entries survive |
| delene_2001 | 16 | 29 | 10–25 | **FAIL** — 4 over ceiling (addresses, unnumbered refs) |
| energy_amplifier | 96 | 94 | 50–130 | PASS |
| aries_cost_account | 64 | 17 | heading_regression_pct ≤ -30% | **FAIL** — -73% vs -30% threshold |
| hawker_2020 | 14 | 21 | ≤ -20% regression | PASS |
| helios_design | 7 | 26 | ≤ -20% regression | PASS |
| hsu_2020 | 4 | 17 | ≤ -20% regression | PASS |

### Root Causes for Remaining Failures

1. **sparc_overview (44 → target ≤20)**: Reference entries survive as headings like `## Control. Fusion...` (no leading number) because `_is_noise_header()` gates all bibliographic checks behind `^\d{1,3}\.\s+`. The detector stripped the reference number, so postprocess sees numberless text. ~24 phantom headings are journal citations without leading numbers.

2. **delene_2001 (29 → target 10–25)**: 4 remaining phantoms include address lines (e.g., "5285 Port Royal Road") and unnumbered bibliographic entries. Spec 02 requirement #3 (address-line rejection) is **not yet implemented**.

3. **aries_cost_account (17, -73%)**: The combination of Pattern 2 font_differs guard + bibliographic noise filters correctly removed phantom reference entries, but the -30% regression threshold in papers.jsonl is too tight for a paper where most "headings" were phantoms. The 17 remaining headings need manual verification — if they're all legitimate, the threshold should be relaxed.

---

## Tasks

### Task 1 [DONE]: Extend bibliographic detection to numberless reference entries [spec-02]
- **Implementation**: Added ungated bibliographic detection in `_is_noise_header()` (lines 371-414) that works independently of the `^\d{1,3}\.\s+` prefix check. The implementation uses a signal-based approach:
  - Counts 5 independent bibliographic signals: multiple journal abbreviations, volume/issue pattern, page range, multiple author initials, year in parentheses
  - Rejects if ≥2 signals detected OR if 1 journal abbreviation + any supporting signal (volume/issue, page range, or year)
  - This dual-condition approach balances precision (avoiding false positives on headings like "General. Introduction") with recall (catching citations like "Control. Fusion 51 (12)")
- **Tests**: Added 14 new unit tests in `tests/test_postprocess.py::TestRejectNoiseHeaders` (lines 710-756) covering:
  - Positive cases: journal+volume/issue, journal+page range, multiple journal abbrevs, author initials+journal, year+journal, volume/issue+page range
  - Negative cases: single journal abbrev alone, volume/issue alone, author initials alone, year alone (all preserved to avoid false positives)
  - Edge cases: legitimate sections with one abbreviation (e.g., "3.2 Design. Methodology") preserved
- **Files modified**:
  - `src/agentic_mbse/extraction/postprocess.py`: Added numberless bibliographic detection logic
  - `tests/test_postprocess.py`: Added 14 new tests, all passing
- **Verification**: All 54 noise header tests pass. Next step is corpus validation to measure impact on sparc_overview heading count.

### Task 2: Add address-line rejection to `_is_noise_header()` [spec-02]
- **What**: In `_is_noise_header()` in `postprocess.py`, add patterns to reject headings that look like address lines, as specified in spec 02 requirement #3:
  - ZIP code pattern: `\b\d{5}\b` (5 consecutive digits not at start-of-line section position)
  - Street keywords: match if heading contains a street keyword ("Road", "Avenue", "Ave", "Street", "Boulevard", "Blvd", "Drive", "Highway", "Hwy", "Suite", "SW", "NW", "SE", "NE") AND a multi-digit number
  - State abbreviation: 2-letter uppercase after comma (`, [A-Z]{2}\b`) combined with ZIP or street keyword
  - **Implementation**: A single combined check — reject if heading matches `\b\d{5}\b` AND contains a street/state keyword, OR if heading matches `\d+\s+\w+\s+(Road|Avenue|Street|Boulevard|Drive|Highway|Suite)` pattern
- **Why**: Spec 02 explicitly requires address rejection. delene_2001 has "5285 Port Royal Road" and similar address fragments surviving as headings.
- **Verified by**: New unit tests in `tests/test_postprocess.py` for address patterns. delene_2001 heading count should drop toward 10–25 range.
- **Depends on**: None (independent of Task 1)

### Task 3: Recalibrate baselines and regression thresholds [spec-01, spec-02]
- **What**: After Tasks 1 and 2 are implemented, recalibrate the test infrastructure:
  1. **Inspect aries_cost_account**: Manually review the 17 remaining headings in `tests/corpus/current/aries_cost_account/full_document.md` to confirm they're all legitimate. If so, the -73% drop is correct behavior (the paper had ~47 phantom headings).
  2. **Update papers.jsonl**: Change `heading_regression_pct` for aries_cost_account from `-30` to a value that accommodates the legitimate heading count (e.g., `-80` or remove the percentage check and use absolute bounds).
  3. **Consider absolute bounds**: The specs define absolute targets (sparc_overview ≤20, delene_2001 10–25, energy_amplifier 50–130). Add these as fields in papers.jsonl (e.g., `heading_count_min`, `heading_count_max`) and check them in the corpus test, providing a more direct acceptance gate than percentage regression.
  4. **Update baselines if needed**: The baselines in `tests/corpus/baseline/*/metrics.json` were from the Layer 1-4 pipeline. If percentage regression tests remain, update baselines to reflect current pipeline output so regressions are measured from the right starting point.
- **Why**: The current test checks percentage regression against stale baselines from a different pipeline architecture. Without recalibration, corpus tests will fail on correct behavior. The specs define absolute targets that the test infrastructure doesn't currently enforce.
- **Verified by**: `uv run pytest tests/test_corpus.py --run-corpus -v` passes all 4 tests. aries_cost_account no longer flagged as regression.
- **Depends on**: Tasks 1 and 2

### Task 4: Full corpus validation and acceptance criteria check [spec-01, spec-02]
- **What**: Run the complete verification suite from both specs:
  1. `uv run pytest tests/test_corpus.py --run-corpus -v` — all 4 corpus tests pass
  2. `uv run pytest tests/ -v` — all unit tests pass
  3. `grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md` — zero math symbols in headings
  4. Per-paper heading counts: sparc_overview ≤20, delene_2001 10–25, energy_amplifier 50–130
  5. No-regression check: hawker_2020, helios_design, hsu_2020 heading counts not decreased by >20% from current values
  6. `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` — clean
- **Why**: Both specs define explicit acceptance criteria and verification commands. This task is the final gate before the iteration can be marked PASS.
- **Verified by**: All commands above return clean results.
- **Depends on**: Task 3

---

## Completed Tasks (Prior Iterations)

### Task A [DONE]: Pattern 1 — Reject section numbers > 99 [spec-01]
- Guard added at `pymupdf_backend.py:125-128`

### Task B [DONE]: Pattern 1 — Require font_differs for single-digit sections [spec-01]
- Guard added at `pymupdf_backend.py:130-138`

### Task C [DONE]: Pattern 2 — Alpha count ≥ 4 guard [spec-01]
- Guard added at `pymupdf_backend.py:150-154`

### Task D [DONE]: Pattern 2 — Require font_differs for multi-word all-caps [spec-01]
- Guard added at `pymupdf_backend.py:160-163`

### Task E [DONE]: Postprocess — Cap section numbers > 99 [spec-02]
- Guard added at `postprocess.py:107-113`

### Task F [DONE]: Postprocess — Reject Figure/Table/Equation references [spec-02]
- Guard added at `postprocess.py:115-117`

### Task G [DONE]: Noise filter — Report/figure labels and numbered bibliographic entries [spec-02]
- Patterns added at `postprocess.py:336-367`

### Task H [DONE]: Unit tests for detector and postprocess guards [spec-01, spec-02]
- 7 detector tests in `tests/test_academic_header_detector.py`
- 14+ noise filter tests in `tests/test_postprocess.py`

---

## Task Dependency Graph

```
Task 1 (numberless bib detection) ──┐
                                     ├── Task 3 (recalibrate) ── Task 4 (validate)
Task 2 (address rejection) ─────────┘
```

Tasks 1 and 2 are independent and can be done in parallel.
Task 3 depends on both 1 and 2.
Task 4 depends on 3.

## Risk Notes

- **aries_cost_account**: The -73% heading drop is likely correct behavior (most headings were phantoms). During Task 3, manually confirm the 17 remaining headings are legitimate. If real headings were lost, review whether font_differs guard or bibliographic patterns are too aggressive for this paper's formatting.
- **sparc_overview numberless detection**: Requiring ≥2 bibliographic signals before rejecting is critical to avoid false positives. A heading like "General. Introduction" could match journal abbreviation pattern but is a legitimate heading. The dual-signal requirement prevents this.
- **energy_amplifier stability**: Currently passing (94 in range 50–130) but is a 241-page document. New noise filters could push it below 50 if over-aggressive. Monitor closely in Task 4.
- **Corpus re-extraction time**: energy_amplifier takes ~11 minutes to extract. Task 4 corpus validation will take ~15-20 minutes total. Plan accordingly.
