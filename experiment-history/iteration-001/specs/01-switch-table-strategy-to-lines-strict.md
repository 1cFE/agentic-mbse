# Switch table_strategy from "lines" to "lines_strict"

## Purpose
Eliminate false-positive table detections that produce garbled markdown with `<br>` tags and `ColN` placeholder columns, by using pymupdf4llm's stricter table detection mode.

## Context (from learning tests)

The current pipeline calls `pymupdf4llm.to_markdown()` with `table_strategy="lines"`. This strategy treats any horizontal/vertical lines in the PDF as potential table boundaries — including decorative rules, text-box borders, and form field outlines. When these "tables" are extracted, pymupdf4llm produces malformed pipe tables with:

- `<br>` HTML tags (252 instances in aries_cost_account)
- `ColN` placeholder column headers (45 instances in aries_cost_account)
- Duplicated cell content across columns
- Body text forced into table cells

The `"lines_strict"` strategy requires fully enclosed cell boundaries (proper ruled tables) before detecting a table. Learning tests show:

| Paper | lines (current) | lines_strict | Impact |
|-------|----------------|--------------|--------|
| aries_cost_account | 137 pipe rows, 252 `<br>`, 45 `ColN` | 0 pipe rows, 0 `<br>`, 0 `ColN` | Eliminates all garbage tables |
| hsu_2020 | 56 pipe rows, 7 `<br>` | 56 pipe rows, 7 `<br>` | No change (real ruled tables preserved) |
| helios_design | 25 pipe rows, 3 `<br>` | 25 pipe rows, 3 `<br>` | No change |
| sparc_overview | 5 pipe rows, 0 `<br>` | 4 pipe rows, 0 `<br>` | -1 pipe row (marginal) |

The fix is a single parameter change in `pymupdf_backend.py` — a tool-level improvement that generalizes by design. No new regex patterns, no downstream string manipulation.

**Note on aries table data**: The real tables in aries_cost_account use whitespace-aligned ASCII formatting (not ruled lines), so they are not detected as pipe tables by either strategy. These tables appear as readable plain text, which is acceptable — they preserve the data, just not in pipe-table format. GMFT (Layer 2) could potentially improve these in a future iteration, but that's a separate concern from eliminating the garbage output.

## Requirements
- Change `table_strategy="lines"` to `table_strategy="lines_strict"` in `pymupdf_backend.py`
- All corpus tests must continue to pass
- No regression in papers with real ruled tables (hsu_2020, helios_design)
- aries_cost_account output must contain zero `<br>` tags and zero `ColN` placeholders from the table_strategy change
- Baselines must be updated to reflect the new extraction output

## Investigation Steps

**Learning test (CRITICAL — run before committing):**

After making the one-line change, run extraction on aries_cost_account and verify:
```python
import pymupdf4llm
result = pymupdf4llm.to_markdown(
    "tests/corpus/pdfs/aries_cost_account.pdf",
    table_strategy="lines_strict",
    page_chunks=True,
)
full_text = "\n".join(chunk["text"] for chunk in result)
assert '<br>' not in full_text, f"Still has {full_text.count('<br>')} <br> tags"
assert 'Col2' not in full_text and 'Col3' not in full_text
print("PASS: no garbage table artifacts")
```

Also verify hsu_2020 tables are preserved:
```python
result = pymupdf4llm.to_markdown(
    "tests/corpus/pdfs/hsu_2020.pdf",
    table_strategy="lines_strict",
    page_chunks=True,
)
full_text = "\n".join(chunk["text"] for chunk in result)
pipe_rows = len([l for l in full_text.split('\n') if l.strip().startswith('|')])
assert pipe_rows >= 50, f"Only {pipe_rows} pipe rows — real tables lost!"
print(f"PASS: {pipe_rows} pipe rows preserved")
```

## Acceptance Criteria
1. `table_strategy="lines_strict"` is set in `pymupdf_backend.py`
2. aries_cost_account output contains zero `<br>` HTML tags (grep returns 0)
3. aries_cost_account output contains zero `ColN` placeholder headers (grep returns 0)
4. hsu_2020 pipe table row count >= 50 (real tables preserved)
5. helios_design pipe table row count >= 25 (real tables preserved)
6. All 4 corpus tests pass (`uv run pytest tests/test_corpus.py --run-corpus -v`)
7. Baselines are updated to reflect new metrics

## Verification
```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check comparison report
python3 tests/corpus/compare.py

# Verify aries_cost_account is clean
grep -c '<br>' tests/corpus/current/aries_cost_account/full_document.md  # must be 0
grep -c 'Col[0-9]' tests/corpus/current/aries_cost_account/full_document.md  # must be 0

# Verify real tables preserved
python3 tests/corpus/metrics.py tests/corpus/current/hsu_2020/full_document.md  # table_row_count >= 50
python3 tests/corpus/metrics.py tests/corpus/current/helios_design/full_document.md  # table_row_count >= 25
```

## Constraints
- The ONLY change to `pymupdf_backend.py` is the `table_strategy` parameter value
- Do NOT add any postprocessing regex to clean up `<br>` or `ColN` — the fix is upstream
- Do NOT change `hdr_info` or any other pymupdf4llm parameters in the same change
- If baselines need updating, update them after verifying the new output is correct (fewer garbage tables = expected improvement, not a regression)
- The aries_cost_account heading_count_max may need adjustment if the loss of garbage pipe tables changes how postprocess detects/promotes headings — verify and adjust bounds if needed, but do NOT inflate bounds to mask real regressions
