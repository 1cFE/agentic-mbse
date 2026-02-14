Perfect! Now let me generate the eval report based on all the evidence:

# Eval Report — Iteration 1

## Per-Spec Results

### 01-switch-table-strategy-to-lines-strict.md
**Verdict:** PASS
**Evidence:**
- `table_strategy="lines_strict"` is set in pymupdf_backend.py:203
- aries_cost_account output contains 0 `<br>` HTML tags (grep returned 0)
- aries_cost_account output contains 0 `ColN` placeholder headers (grep returned 0)
- hsu_2020 pipe table row count = 64 (>= 50 required) — real tables preserved
- helios_design pipe table row count = 29 (>= 25 required) — real tables preserved
- All 4 corpus tests passed: `4 passed in 755.65s`
- Baselines updated — comparison report shows "No quality regressions detected!"

### 02-extend-guard2-all-depth1-sections.md
**Verdict:** PASS
**Evidence:**
- Guard 2 implementation in pymupdf_backend.py:134-139 now requires `font_differs` for all depth-1 sections that lack trailing period:
  - Logic: `single_digit_with_period = int(sec_num) <= 9 and has_period`
  - Only single-digit (<=9) sections WITH period are exempt from font check
  - All other depth-1 numbers (10+, or no period) require `font_differs`
- `## 30 M shots.` does NOT appear in hawker_2020 output (grep returned 0)
- `## 16. Steffen B. 2020` does NOT appear in hawker_2020 output (grep returned 0)
- hawker_2020 heading count = 5 (within bounds: 5-10) ✓
- aries_cost_account heading count = 13 (within bounds: 1-20) ✓
- delene_2001 heading count = 22 (within bounds: 10-25) ✓
- sparc_overview heading count = 14 (within bounds: 0-20) ✓
- energy_amplifier heading count = 70 (within bounds: 50-130) ✓
- All 4 corpus tests passed

### 03-add-corpus-pdf-woodruff-2026.md
**Verdict:** PASS
**Evidence:**
- PDF file exists at tests/corpus/pdfs/woodruff_2026.pdf (462011 bytes)
- Entry exists in tests/corpus/papers.jsonl: `{"slug": "woodruff_2026", "pdf_path": "tests/corpus/pdfs/woodruff_2026.pdf", "source": "pool", "has_tables": false, "has_math": false, "pages": 25, "heading_count_min": 30, "heading_count_max": 100}`
- Baseline metrics exist at tests/corpus/baseline/woodruff_2026/metrics.json (238 bytes)
- All 4 corpus tests passed (woodruff_2026 included in test run)
- Heading count = 82 (within bounds: 30-100) — reasonable for a 25-page deeply-nested paper
- Comparison report shows stable extraction: `82→82 (=)` with 89k chars
- No extraction failures or garbled text (test passed)

## Summary
- Specs passed: 3/3
- Critical failures: none
- Key observations:
  - `lines_strict` completely eliminated false-positive table detections (252 `<br>` tags → 0) while preserving all real ruled tables
  - Guard 2 extension successfully rejected both false positives in hawker_2020 without affecting legitimate numbered sections
  - woodruff_2026 extraction demonstrates pipeline handles deeply-nested heading structures (82 headings across H2/H3/H4)
  - All quality metrics stable across the 8-paper corpus with zero regressions
  - Extraction performance acceptable (8-672s depending on paper complexity)

## VERDICT: CONVERGED
**Evidence:** All specs passed. Cumulative improvements across iteration 1:
1. Eliminated garbage table artifacts via upstream parameter change (tool-level fix that generalizes)
2. Improved numbered section detection by extending font-difference requirement (reduces false positives for any body-font numbered text)
3. Expanded corpus from 7 to 8 papers, adding coverage for different publisher format and deeply-nested heading structures
4. All 4 corpus tests passing, all heading counts within established bounds, zero quality regressions vs baseline
