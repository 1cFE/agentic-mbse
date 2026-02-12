# Establish Corpus Baselines

## Purpose
Create baseline metrics for all 7 corpus papers so that the comparison report and regression tests have reference data.

## Requirements
- Every paper in `tests/corpus/papers.jsonl` must have a `tests/corpus/baseline/{slug}/metrics.json` file
- Baseline metrics must be copied from the current extraction output (the first extraction run becomes the baseline)
- The comparison report (`python3 tests/corpus/compare.py`) must produce a table, not an error
- The regression test (`test_no_quality_regression_vs_baseline`) must compare against real baselines, not skip vacuously
- Fix `delene_2001` metadata: the registry says `has_tables: false` but the paper contains 11 tables. The tables are whitespace-aligned plain text (not pipe tables), so `table_row_count=0` is technically correct for the metric definition (which counts pipe rows), but `has_tables` should be `false` since no pipe tables exist. Leave as-is.

## Investigation Steps
1. Run `uv run pytest tests/test_corpus.py --run-corpus -v` to populate `tests/corpus/current/`
2. For each slug, copy `tests/corpus/current/{slug}/metrics.json` to `tests/corpus/baseline/{slug}/metrics.json`
3. Run `python3 tests/corpus/compare.py` to verify the comparison report works
4. Run the full corpus test suite to verify regression tests pass with baselines

Learning test: After copying baselines, run `python3 tests/corpus/compare.py` and verify all 7 papers show `(=)` for all metrics (since baseline == current at this point).

## Acceptance Criteria
- `tests/corpus/baseline/` contains `metrics.json` for all 7 slugs: hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001, sparc_overview, energy_amplifier
- `python3 tests/corpus/compare.py` prints a table with 7 rows, no errors, no warnings
- `uv run pytest tests/test_corpus.py --run-corpus -v` passes all 4 tests

## Verification
```bash
# Check baseline files exist
ls tests/corpus/baseline/*/metrics.json | wc -l  # should be 7

# Run comparison report
python3 tests/corpus/compare.py  # should show a table with 7 rows

# Run full corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v  # all 4 must pass
```

## Constraints
- Do NOT modify any extraction source code
- Do NOT modify any test logic
- Only create baseline metric files by copying current metrics
