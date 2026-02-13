# Fix Phantom Headings in AcademicHeaderDetector

## Purpose
Eliminate false-positive heading classifications from the `AcademicHeaderDetector.__call__()` method by tightening Pattern 1 (numbered sections) and Pattern 2 (all-caps) to reject common non-header text.

## Background

Investigation in iteration 2 identified two buggy code paths in `src/agentic_mbse/extraction/pymupdf_backend.py`:

### Pattern 1 (numbered section headers) — lines 114-132
The regex `^\d+(\.\d+)*\.?\s+(.+)` matches ANY text starting with digits, including:
- **Year numbers in references**: "2020 A community plan..." → section 2020
- **Footnote numbers**: "1 The heat produced..." → section 1, "13 The project ITER..." → section 13
- **Table/figure captions**: "52 Table 2.2 - Averaged cross sections" → section 52

The fallback condition `title_text[0].isupper()` fires for all of these because academic text starts with capitals. There is no upper bound on section numbers, so 2020 is treated the same as 2.

**Evidence from learning tests:**
- sparc_overview: ~55 of 83 pre-postprocess headings are reference entries matched by Pattern 1 (years like 2014, 2007, 2020 treated as section numbers)
- energy_amplifier: footnotes numbered 1-18 matched as section headers, plus table/figure captions starting with numbers

### Pattern 2 (all-caps headers) — lines 134-143
Python's `str.isupper()` returns `True` when ALL cased characters are uppercase, ignoring non-cased characters (digits, punctuation, spaces). This means:
- `", D. M. 2002"` → `isupper()=True` (only D, M are cased, both uppercase) → promoted as multi-word all-caps header
- `"(6), S404-S413."` → `isupper()=True` (only S is cased) → promoted
- Author initial fragments like `", J. W., B"` → `isupper()=True` → promoted

The multi-word branch (`elif len(words) <= 6: return "## "`) accepts these without checking that the text contains meaningful all-caps words.

**Evidence from learning tests:**
- sparc_overview page 23: 46 phantom headings from reference entry fragments — primarily author initial sequences and citation fragments passing `isupper()` + word count check
- All phantom headings had `font_differs=False` (same font family, not bold, not italic)

## Requirements

- Pattern 1 MUST reject section numbers > 99 at the top level (depth=1). Real academic papers don't have section "2020" or section "5285". For subsections (depth >= 2), the existing logic is fine (e.g., 2.1, 3.14 are valid).
- Pattern 1 MUST require `font_differs=True` for standalone single-digit section numbers (1, 2, 3...) that are ambiguous with footnotes. Footnotes "1 The heat produced..." use body font; real section headers use a differentiated font. The exception is when the number is followed by a clearly section-like pattern (e.g., "1. Introduction" with a period after the number).
- Pattern 2 MUST require a minimum count of alphabetic characters (>= 4) before accepting `isupper()`, to reject sparse-letter fragments like ", D. M. 2002".
- All existing legitimate headings must be preserved: numbered sections (1. Introduction, 2.1 Background, etc.), known all-caps headers (ABSTRACT, REFERENCES, etc.), and titles.

## Investigation Steps

1. Read `src/agentic_mbse/extraction/pymupdf_backend.py` lines 86-155 (the `__call__` method)
2. **Learning test**: Before implementing, run the detector on sparc_overview and energy_amplifier to count phantom vs legitimate headings produced by each pattern path. The learning test should call the detector on every span and tag each result with which pattern matched (1, 2, or 3). This establishes the "before" count.
   - Command: Write a script that instruments the detector to log which pattern fires for each heading, run it on sparc_overview and energy_amplifier, count phantoms vs legitimate per pattern
3. Implement the fixes:
   - Pattern 1: Add `if depth == 1 and int(sec_num) > 99: return ""` to reject absurd section numbers
   - Pattern 1: For single-digit top-level sections without a period (e.g., "1 Title" not "1. Title"), require `font_differs` to distinguish from footnotes
   - Pattern 2: Before the `isupper()` check, count alphabetic characters with `sum(c.isalpha() for c in text)` and require >= 4
4. Re-run the detector on the same papers and verify phantom count drops while legitimate headings are preserved

## Acceptance Criteria

- **sparc_overview**: heading_count <= 20 (currently 75, only ~7 are legitimate). The legitimate headings are: title + sections 1-6 + REFERENCES = 8. With some tolerance for borderline cases, <= 20 is the target.
- **energy_amplifier**: heading_count in range 50-130 (currently 126, many legitimate subsections 2.1-6.6 exist, but ~30 are phantom footnotes/table-fragments that should be removed)
- **delene_2001**: heading_count in range 15-40 (currently 68, but ~30 are phantom reference entries, table headers, and address fragments)
- **No regressions**: hawker_2020, aries_cost_account, helios_design, hsu_2020 heading counts must not decrease by more than 20% from current values
- All 4 corpus tests pass: `uv run pytest tests/test_corpus.py --run-corpus -v`
- Zero math symbols in headings: `grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md` returns empty

## Verification

```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check per-paper heading counts
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/output.md
python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/output.md
python3 tests/corpus/metrics.py tests/corpus/current/delene_2001/output.md

# Check for math noise in headings
grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md

# Comparison report
python3 tests/corpus/compare.py
```

## Constraints

- Do NOT modify postprocess.py in this spec (that's spec 02)
- Do NOT add new format-specific patterns — the fix must be tightening existing logic
- Preserve the existing 3-pattern structure of the detector; only add guards within each pattern
- All existing unit tests must pass: `uv run pytest tests/ -v`
