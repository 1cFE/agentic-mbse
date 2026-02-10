# Implementation Plan

## Status: Awaiting Iteration 2 Brief

Iteration 1 complete. All specs satisfied. No active tasks.

Create `iteration-brief.md` for next iteration to continue.

## Maintenance

### Bug Fixes
- [DONE] Fixed test_extraction.py failing test - Updated `test_extract_passes_table_strategy_and_page_chunks` to match current implementation (no longer using `_academic_header_detector`)

---

## Archive: Iteration 1 (Complete ✅)

**Specs satisfied:**
- `specs/add-bold-allcaps-heading-promotion.md` ✅
- `specs/fix-delene-baseline-artifacts.md` ✅
- `specs/add-sparc-to-corpus.md` ✅

**Final results:**
- delene_2001: 23→28 headings (+5), 0 AI artifacts
- hsu_2020: 4→4 headings (=), no regression after baseline cleanup
- sparc_overview: Added to corpus (6 papers total)
- All corpus tests pass (4/4)
- All postprocess tests pass (105/105)

**Key learnings:**
- Bold all-caps headings (`**ABSTRACT**`, `**CONTENTS**`) fell through both allcaps promoter (requires no bold) and unnumbered bold promoter (requires 14+ chars)
- New `promote_bold_allcaps_headers()` fills this detection gap
- Baseline contamination (AI artifacts, false positives) creates phantom regressions
- Current extraction is source of truth — re-extract and replace baselines when needed
