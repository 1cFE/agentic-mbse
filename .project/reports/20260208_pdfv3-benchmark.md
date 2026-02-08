# PDF Extraction v3 — Corpus Benchmark Report

**Date:** 2026-02-08
**Branch:** pdf-extract
**Pipeline version:** v3 (L3 Claude structural pass + index fixes)
**Baseline reference:** `.project/reports/20260208_pdfv3-baseline.md`
**Epic:** `.project/backlog/epic_pdf-extraction-v3.md` — Item 4

---

## Executive Summary

Ran the full v3 pipeline (`--enhance --index --force`) on all 12 corpus documents. The critical success factor — at least 4/5 new corpus documents produce usable INDEX files — is **met**. Zero regressions on the original 7-doc corpus.

**Headline results:**
- **New corpus:** 4/5 usable INDEX (safety, fusion-std, 2244, hazards). 2243 (slide deck) remains the lone gap.
- **Original corpus:** 7/7 INDEX section counts match baseline exactly. Zero regressions.
- **Code fixes shipped alongside:** Unicode noise detection, period-numbered headers, unnumbered header fallback (21 new tests, 881 total passing).

---

## 1. Per-Document Results

### New Corpus (5 docs)

| ID | Short Name | Pages | L3 Gate | Style Detected | Headers Inserted | Skipped | INDEX Sections | Baseline Sections | Wall Clock | Usable INDEX? |
|----|-----------|-------|---------|----------------|-----------------|---------|----------------|-------------------|------------|---------------|
| safety | Fusion Safety Program | 14 | triggered | slide_deck (unnumbered_bold) | 10 | 1 | 10 | 0 | 25s | **YES** |
| fusion-std | Fusion Standards | 4 | triggered | academic_paper (unnumbered_bold) | 5 | 1 | 5 | 0 | 21s | **YES** |
| 2244 | Helios Stellarator | 29 | triggered | academic_paper (numbered_bold) | 9 | 0 | 15 | 0 | 63s | **YES** |
| hazards | Afify Hazards | 8 | triggered | academic_paper (unnumbered_bold) | 20 | 0 | 20 | 0 | 29s | **YES** |
| 2243 | Rider Slides | 127 | NOT triggered | — | 0 | 0 | 20 (junk) | 40 (junk) | 29s | **NO** |

### Original Corpus (7 docs)

| ID | Short Name | Pages | L3 Gate | Headers Inserted | INDEX Sections | Baseline Sections | Wall Clock | Regression? |
|----|-----------|-------|---------|-----------------|----------------|-------------------|------------|-------------|
| 2241 | Eester ICRH | 30 | skipped | 0 | 15 | 15 | 10m (smoke test w/ L4) | No |
| 2232 | Handley | 17 | skipped | 0 | 15 | 15 | 12s | No |
| 2233 | Araiinejad | 12 | skipped | 0 | 10 | 10 | 15s | No |
| 2235 | Global Fusion | 30 | skipped | 0 | 27 | 27 | ~2m | No |
| 2236 | Digital Twins | 66 | skipped | 0 | 67 | 67 | ~3m | No |
| 2237 | LANL PJMIF | 60 | skipped | 0 | 51 | 51 | ~7m | No |
| 2238 | Lampe CBFR | 40 | triggered | 9 (6 skipped) | 14 | 14 | ~5m | No |

---

## 2. Critical Success Factor Evaluation

> **At least 4/5 new corpus documents produce usable INDEX files with correct heading structure, with zero regressions on the original 7-doc corpus.**

| Criterion | Result |
|-----------|--------|
| 4/5 new corpus usable INDEX | **4/5 — PASS** (safety, fusion-std, 2244, hazards) |
| Zero regressions on original 7 docs | **0 regressions — PASS** |

---

## 3. Baseline Comparison

### New Corpus — Grade Changes

| ID | Baseline Grade | v3 Grade | Delta | Key Change |
|----|---------------|----------|-------|------------|
| safety | C+ | **B+** | +2 tiers | 0→10 INDEX sections via L3 structural pass |
| fusion-std | D+ | **B-** | +3 tiers | 0→5 INDEX sections via L3 structural pass |
| 2244 | C+ | **B+** | +2 tiers | 0→15 INDEX sections via L3 structural pass |
| hazards | B- | **A-** | +2 tiers | 0→20 INDEX sections via L3 structural pass |
| 2243 | D+ | **D+** | unchanged | Slide deck — gate not triggered, INDEX still junk |

### Original Corpus — Grade Changes

| ID | Baseline Grade | v3 Grade | Delta |
|----|---------------|----------|-------|
| 2241 | A- | **A-** | unchanged |
| 2232 | B+ | **B+** | unchanged |
| 2233 | B | **B** | unchanged |
| 2235 | B+ | **B+** | unchanged |
| 2236 | B+ | **B+** | unchanged |
| 2237 | B+ | **B+** | unchanged |
| 2238 | C+ | **C+** | unchanged |

**Averages:**
- New corpus: D+/C+ → **B/B+** (excluding 2243) — significant improvement
- Original corpus: **B+** (unchanged) — zero regressions
- All 12: **B** (up from B-)

---

## 4. Code Fixes Applied (Pre-Benchmark)

Three bugs discovered during initial benchmark attempts, fixed before final run:

### Fix 1: Unicode noise detection in `_is_noise_header()`
- **File:** `src/agentic_mbse/extraction/postprocess.py:304`
- **Bug:** Character class only checked ASCII `[=+\[\]{}]`. 2243's garbage headers use Unicode symbols (`≥`, `∇`, `µ`, `~`, `•`) and embedded bold markers (`** **`).
- **Fix:** Extended to `[=+\[\]{}>~≥≤≈∇∆∑∏µ±×÷→←∞•]` + added `** **` / `****` check.
- **Impact:** Enables `needs_claude_structure()` to correctly detect noise in Unicode-heavy documents.

### Fix 2: Period-numbered headers in `parse_sections()`
- **File:** `src/agentic_mbse/extraction/index.py:73-82,304`
- **Bug:** Patterns only matched `## 1 Title`, not `## 1. Title`. Affected 2244 (period-numbered headers inserted by L3).
- **Fix:** Added `\.?` after each numeric capture group in all 5 regex patterns.
- **Impact:** Documents with period-numbered headers now produce correct INDEX.

### Fix 3: Unnumbered header fallback in `parse_sections()`
- **File:** `src/agentic_mbse/extraction/index.py` (new `_parse_unnumbered_sections()`)
- **Bug:** `parse_sections()` only matched numbered headers (`## 1 Title`). Docs with unnumbered headers (`## Overview`) from L3 produced empty INDEX.
- **Fix:** Two-pass approach: if no numbered headers found, fallback generates synthetic section numbers from heading depth counters.
- **Impact:** safety, fusion-std, hazards all go from 0 INDEX sections to 5-20.

**Tests added:** 21 new tests across 3 test files. 881 total passing, 0 failures.

---

## 5. Known Limitations

1. **2243 (slide decks):** The L3 gate doesn't trigger because slide content headers aren't Unicode noise — they're semantically valid text in the wrong role. A future improvement: if no real document sections exist, call Claude to manually identify logical section boundaries in slide decks.

2. **2238 junk INDEX entries:** L3 inserted 9 headers but 2 are body text promoted to headers (reference line, "160 MW..." fragment). These were present in baseline too. Could be improved with stricter Phase B prompting.

3. **Documents over 200 pages:** Not tested beyond 2243 (127p). Chunking should handle larger docs but no validation.

4. **Cost actuals not measured:** Claude API costs were not tracked per-document in this run. L3 uses Haiku for Phase A (~$0.01) and Sonnet for Phase B (~$0.10-0.50/chunk). Total per-doc estimated at $0.30-1.50.

---

## 6. Test Suite

```
881 passed, 1 skipped, 0 failures (15.98s)
```

The 1 skipped test is an existing syside adapter test (license key dependent).

---

## Verification Checklist

- [x] All 12 PDFs extracted with `--enhance --index --force`
- [x] INDEX section counts recorded for all 12 documents
- [x] Baseline comparison completed — zero regressions on original 7
- [x] 4/5 new corpus docs produce usable INDEX (critical success factor met)
- [x] Code fixes committed with 21 new tests
- [x] Full test suite passes (881 passed)
- [x] CLI help text reviewed — accurate for all flags
- [x] Known limitations documented
