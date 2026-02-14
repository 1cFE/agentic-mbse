# Extend Guard 2 to All Depth-1 Sections Without Trailing Period

## Purpose
Eliminate false-positive numbered headings where body-text lines starting with numbers > 9 (e.g., "30 M shots.", "16. Steffen B. 2020...") are promoted to section headings despite using body font.

## Context (from learning tests)

In `AcademicHeaderDetector.__call__`, Guard 2 currently requires `font_differs` only for depth-1 section numbers 1–9 without a trailing period:

```python
if depth == 1 and int(sec_num) <= 9 and not has_period:
    if not font_differs:
        return ""
```

This lets numbers 10+ bypass the guard. Learning tests confirm both false positives in hawker_2020 are:
- **`## 30 M shots.`** (line 636): Font `Palatino-Roman` 9pt, not bold, not italic → `font_differs=False`
- **`## 16. Steffen B. 2020...`** (line 878): Font `Palatino-Roman` 9pt, not bold, not italic → `font_differs=False`

Both are body text (a figure caption continuation and a bibliography entry) that happen to start with a number. They pass because Guard 2 only checks `int(sec_num) <= 9`.

Legitimate numbered sections like "1. Introduction" in hawker_2020 use `has_period=True` (the text is "1. Introduction" with a period between the number and the space), so they are unaffected by extending Guard 2.

**The fix**: Remove the `int(sec_num) <= 9` constraint from Guard 2, making `font_differs` mandatory for ALL depth-1 sections that lack a trailing period (i.e., where the section number is NOT followed by a period-then-space in the original text).

This is safe because:
- Academic papers with "1. Introduction" format have `has_period=True` → not affected
- Academic papers with bold/different-font headings have `font_differs=True` → not affected
- Only body-font text starting with a bare number gets rejected — which is the correct behavior

**Note**: The postprocess `_is_noise_header()` function already catches many bibliographic entries (it has extensive reference detection). But it runs downstream, after font metadata is lost. Fixing this in the detector (where font info IS available) is the right layer — it prevents the false positive from ever being created, rather than trying to pattern-match it away later.

## Requirements
- Remove the `int(sec_num) <= 9` constraint from Guard 2 in `AcademicHeaderDetector.__call__`
- The two specific false positives in hawker_2020 must be eliminated
- Legitimate numbered section headings (e.g., "1. Introduction", "2. Model") must continue to be promoted
- All heading counts must remain within their `heading_count_min`/`heading_count_max` bounds
- The fix must generalize (reduce false positives for any paper with body-font numbered text)

## Investigation Steps

**Learning test 1 (CRITICAL — run before implementing):**

Test the impact of extending Guard 2 to all depth-1 numbers:

```python
# In AcademicHeaderDetector.__call__, Pattern 1, Guard 2:
# CURRENT:  if depth == 1 and int(sec_num) <= 9 and not has_period: require font_differs
# PROPOSED: if depth == 1 and not has_period: require font_differs
#
# For each corpus paper, extract with the modified detector,
# then run full postprocess pipeline, and count final headings.
# Compare against current counts and bounds.
```

**Learning test 2:** If Learning test 1 drops heading counts below minimums on any paper, try a hybrid: keep current `<= 9` behavior but also require `font_differs` for numbers >= 10 (no period case).

**Learning test 3:** Run full pipeline and verify:
```bash
uv run pytest tests/test_corpus.py --run-corpus -v
python3 tests/corpus/compare.py
```

## Acceptance Criteria
1. `## 30 M shots.` does NOT appear in hawker_2020 output (grep returns 0)
2. `## 16. Steffen B. 2020` does NOT appear in hawker_2020 output (grep returns 0)
3. hawker_2020 heading count is between 5 and 10
4. aries_cost_account heading count is between 1 and 20
5. delene_2001 heading count is between 10 and 25
6. sparc_overview heading count is at most 20
7. energy_amplifier heading count is between 50 and 130
8. All 4 corpus tests pass (`uv run pytest tests/test_corpus.py --run-corpus -v`)

## Verification
```bash
# Run corpus tests (the authoritative check)
uv run pytest tests/test_corpus.py --run-corpus -v

# Check comparison report
python3 tests/corpus/compare.py

# Verify specific false positives are gone
grep -c "^## 30 M" tests/corpus/current/hawker_2020/full_document.md  # must be 0
grep -c "^## 16\. Steffen" tests/corpus/current/hawker_2020/full_document.md  # must be 0

# Check per-paper heading counts
python3 tests/corpus/metrics.py tests/corpus/current/hawker_2020/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/aries_cost_account/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/delene_2001/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/full_document.md
```

## Constraints
- Do NOT add paper-specific or publisher-specific regex patterns — the fix must be in the detection logic
- Do NOT modify corpus test thresholds — the detector must produce correct headings within existing bounds
- Do NOT remove the numbered-section detection entirely — legitimate sections must still be detected
- The fix should be in `AcademicHeaderDetector.__call__` (upstream, where font metadata is available), not in `_is_noise_header` (downstream, where font information is lost)
- If tightening the gate causes heading counts to drop below minimums on any paper, the approach must be reconsidered — do NOT just adjust the bounds to fit
- Baselines should be updated after verifying correctness
