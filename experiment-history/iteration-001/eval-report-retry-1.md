So the breakdown is:
- Baseline: 6 H2 headings = 6 total
- Current: 1 H1 + 3 H2 = 4 total

This is actually -2 total headings, but one got promoted to H1 (the title). The real loss is 6 H2 → 4 total, which is 2 "section heading" losses.

The spec constraint says "Do NOT reduce heading counts" — I interpret this to mean total heading count. The total went from 6 to 4, which is a reduction of 2. This violates the constraint.

However, let me check what the comparison report shows to understand if this is within normal variation:

Looking back at my earlier comparison output:
```
hsu_2020: 6→4 (-33%)
```

And the paper config allows `-50%` regression, so the test passes. But the spec says "Do NOT reduce" as a hard constraint, not "reduce within threshold".

This is a clear **FAIL** for spec 1.

Let me now prepare the full eval report:

# Eval Report — Iteration 1

## Per-Spec Results

### add-bold-allcaps-heading-promotion.md
**Verdict:** FAIL
**Evidence:**
- ✓ `delene_2001` heading count: 23 → 28 (+5), exceeds >=25 requirement
- ✓ `uv run pytest tests/test_postprocess.py -v`: 105/105 tests passed
- ✓ `uv run pytest tests/test_corpus.py --run-corpus -v`: 4/4 tests passed
- ✓ Most papers maintained or improved heading counts:
  - hawker_2020: 11→15 (+4)
  - aries_cost_account: 102→139 (+37)
  - delene_2001: 23→28 (+5)
  - sparc_overview: 6→6 (=)
- ✗ **CONSTRAINT VIOLATION**: hsu_2020 heading count decreased from 6→4 (-33%)
  - Spec explicitly states: "Do NOT reduce heading counts for hawker_2020, aries_cost_account, or hsu_2020"
  - Lost headings: "Project Information", citation artifact, "Cost Categories"
  - These appear to be baseline false positives, but the constraint is absolute
- ✓ No false positive headings introduced (manual inspection confirms legitimate headings)

**Failure reason:** The constraint "Do NOT reduce heading counts for hsu_2020" was violated. While the test suite passes due to -50% threshold allowance, the spec constraint is a hard requirement with no tolerance.

### add-sparc-to-corpus.md
**Verdict:** PASS
**Evidence:**
- ✓ `tests/corpus/pdfs/sparc_overview.pdf` exists (1.9M file)
- ✓ `tests/corpus/papers.jsonl` has 6 entries (verified with JSON parsing)
- ✓ Paper metadata correct: `{"slug": "sparc_overview", "source": "pool", "has_tables": true, "has_math": true, "pages": 25}`
- ✓ `tests/corpus/baseline/sparc_overview/full_document.md` exists (87K)
- ✓ `tests/corpus/baseline/sparc_overview/metrics.json` exists with heading_count=6 (exceeds >=3 requirement)
- ✓ Full metrics: `{"char_count": 88549, "heading_count": 6, "table_row_count": 5, "math_symbol_count": 18, "figure_ref_count": 25}`
- ✓ `uv run pytest tests/test_corpus.py --run-corpus -v`: 4/4 tests passed
- ✓ No regressions on existing 5 papers (all within thresholds)

### fix-delene-baseline-artifacts.md
**Verdict:** PASS
**Evidence:**
- ✓ Zero AI conversational artifacts in cleaned baseline:
  ```bash
  grep -c "I notice you mentioned|I need to see the image|..." → 0
  ```
- ✓ Baseline metrics after cleanup: `{"char_count": 67817, "heading_count": 23}`
- ✓ Current extraction metrics: `{"char_count": 67812, "heading_count": 28}`
- ✓ Character count regression: -5 chars (-0.01%), well within -3% threshold (required)
- ✓ All corpus tests pass: `uv run pytest tests/test_corpus.py --run-corpus -v` → 4/4 passed
- ✓ Comparison report shows delene_2001: `67k→67k (=)` with heading improvement `23→28 (+5)`
- ✓ All legitimate content from PDF preserved (tables extracted correctly as plain text)

## Summary
- Specs passed: 2/3
- Critical failures: **add-bold-allcaps-heading-promotion.md** failed due to hsu_2020 heading count reduction
- Key observations:
  - The bold all-caps promotion feature works correctly and recovered 5 headings in delene_2001
  - The hsu_2020 heading loss (6→4) appears unrelated to bold all-caps promotion — the lost headings ("Project Information", citation artifact, "Cost Categories") were baseline false positives that current extraction correctly rejects
  - However, the spec constraint is absolute: "Do NOT reduce" means zero tolerance for reduction, regardless of whether the baseline had false positives
  - SPARC paper integration succeeded without issues
  - Baseline artifact cleanup eliminated all AI hallucinations and normalized the regression metrics

## VERDICT: RETRY
**Reason:** Spec `add-bold-allcaps-heading-promotion.md` failed — hsu_2020 heading count decreased from 6→4, violating the explicit constraint "Do NOT reduce heading counts for hsu_2020". While the feature implementation is correct and tests pass, the constraint violation must be addressed.
