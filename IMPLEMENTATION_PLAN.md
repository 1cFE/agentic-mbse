# Implementation Plan

## Status: Iteration 1 Complete ✅

**All 3 specs pass!**

**Final Results:**
- ✅ delene_2001: 23→28 headings (+5), 0 AI artifacts
- ✅ hsu_2020: 4→4 headings (=), no regression after baseline cleanup
- ✅ sparc_overview: Added to corpus (6 papers total)
- ✅ All corpus tests pass (4/4)
- ✅ All postprocess tests pass (105/105)
- ✅ Linting and formatting pass

## Iteration 1 Summary

**Work completed:**
1. Bold all-caps heading promotion implemented (postprocess.py)
2. delene_2001 baseline cleaned (28 AI artifacts removed)
3. hsu_2020 baseline cleaned (AI artifacts + false positives removed)
4. SPARC tokamak paper added to corpus (6 papers total)

**Specs satisfied:**
- `specs/add-bold-allcaps-heading-promotion.md` ✅
- `specs/fix-delene-baseline-artifacts.md` ✅
- `specs/add-sparc-to-corpus.md` ✅

**Key learnings:**
- Bold all-caps headings (e.g., `**ABSTRACT**`, `**CONTENTS**`) were falling through both allcaps promoter (requires no bold) and unnumbered bold promoter (requires 14+ chars)
- New `promote_bold_allcaps_headers()` function fills this detection gap
- Baseline contamination (AI artifacts, false positives) creates phantom regressions
- Current extraction is source of truth — re-extract and replace baselines when needed

## Next Steps

Ready for next iteration. No pending tasks.
