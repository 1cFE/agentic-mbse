# Fix Phantom Headings in Postprocess Promoters

## Purpose
Tighten `promote_plain_headers()` and strengthen `reject_noise_headers()` in `src/agentic_mbse/extraction/postprocess.py` to eliminate phantom headings created by the postprocessing pipeline.

## Background

Investigation in iteration 2 identified that `promote_plain_headers()` creates phantom headings independently of the `AcademicHeaderDetector`. The `_PLAIN_HEADER_RE` regex matches any standalone line starting with digits followed by capitalized text, with no upper bound on the "section number":

```python
_PLAIN_HEADER_RE = re.compile(
    r"(?<=\n\n)(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z].{2,80})(?=\n\n)",
)
```

**Evidence from learning tests:**
- `"5285 Port Royal Road"` → matches as section 5285 ✓
- `"1000 Independence Avenue SW"` → matches as section 1000 ✓
- `"2050 The capital-related portion"` → matches as section 2050 ✓
- `"52 Table 2.2 - Averaged cross sections"` → matches as section 52 ✓
- `"12 Figure 11 excludes the cost"` → matches as section 12 ✓

None of these are caught by `_is_toc_line()` (which only checks for dot leaders and trailing page numbers) or `_is_noise_header()` (which checks for math symbols, pipe chars, and very short text — none of which apply here).

The `_is_noise_header()` function catches zero of the documented phantom heading patterns. It was designed for math/equation noise but doesn't address the structural phantoms (references, footnotes, table content, addresses).

## Requirements

### 1. Cap section numbers in `promote_plain_headers`
- `_PLAIN_HEADER_RE` must reject section numbers > 99 at the top level. The simplest fix: change the regex to limit the leading number, OR add a guard in `_replace_plain_header()` that checks `int(sec_num) > 99` for depth-1 sections.
- Subsection numbers like "2.1", "3.14" are fine — only the top-level integer needs bounding.

### 2. Reject figure/table reference patterns
- Lines matching `^\d+\s+(?:Figure|Fig\.|Table|Equation)\s` should NOT be promoted to headings. These are figure/table cross-references or captions starting with a number, not section headers.
- Add this check to `_replace_plain_header()` or `_is_toc_line()`.

### 3. Strengthen `_is_noise_header()` for structural phantoms
- Reject headings that look like address lines: contain common address indicators (ZIP code patterns `\b\d{5}\b`, "Road", "Avenue", "Street", state abbreviations)
- Reject headings where the "section number" is > 99 (these survived from the detector or plain header promotion)
- Reject headings that look like figure labels: match pattern `^[A-Z]{2,} \d{2,}[-–]\d+ [A-Z]+$` (e.g., "ORNL 99-1407 EFG")

## Investigation Steps

1. Read `src/agentic_mbse/extraction/postprocess.py`, focusing on `_PLAIN_HEADER_RE`, `_replace_plain_header()`, `_is_toc_line()`, `_is_noise_header()`, and `reject_noise_headers()`
2. **Learning test**: Extract delene_2001 with the current pipeline and count how many headings come from `promote_plain_headers` vs `AcademicHeaderDetector`. The test should:
   - Extract with AcademicHeaderDetector only (no postprocessing) → count headings
   - Apply only `promote_plain_headers` to the raw markdown → count added headings
   - Apply full postprocess → count final headings
   - Categorize each heading as legitimate vs phantom
   - This gives the "before" count for this spec
3. Implement the fixes in the order listed above (cap first, then rejections, then noise filter)
4. Re-run on all corpus papers and compare heading counts

## Acceptance Criteria

- **delene_2001**: heading_count in range 10-25 (currently 68; legitimate sections are: title + sections 1-7 + subsections 4.1-4.6 = ~14 real headings)
- **energy_amplifier**: phantom headings from `promote_plain_headers` should not contribute any new false positives (all table/figure caption promotions eliminated)
- **sparc_overview**: no additional phantom headings from postprocessing (currently adds 0, so this must remain 0)
- **No regressions**: hawker_2020, aries_cost_account, helios_design, hsu_2020 heading counts must not decrease by more than 20% from their values after spec 01 is applied
- All 4 corpus tests pass: `uv run pytest tests/test_corpus.py --run-corpus -v`
- All unit tests pass: `uv run pytest tests/ -v`

## Verification

```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check per-paper heading counts
python3 tests/corpus/metrics.py tests/corpus/current/delene_2001/output.md
python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/output.md
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/output.md

# Inspect actual headings to verify no phantoms remain
grep '^#' tests/corpus/current/delene_2001/full_document.md
grep '^#' tests/corpus/current/sparc_overview/full_document.md | head -20

# Comparison report
python3 tests/corpus/compare.py
```

## Constraints

- Do NOT modify `pymupdf_backend.py` in this spec (that's spec 01)
- Keep `_PLAIN_HEADER_RE` as simple as possible — prefer guard logic in `_replace_plain_header()` over complex regex
- The `_is_noise_header()` additions must be general-purpose, not paper-specific. Test that the new patterns would also catch similar phantoms in unseen documents.
- Postprocessing must remain pure functions (str → str), no network or ML calls
- All existing unit tests must pass
