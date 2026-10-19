# Repository checks at the end of Item 3 (Phase 11)

Recorded 2026-10-19 at branch HEAD `0ba0bf02` plus the uncommitted Phase 11 script fix (scripts only, no `src` change), against `evidence/baseline.md` (Phase 1, base `ebb3d467`). `SYSIDE_LICENSE_KEY` was present in `.env`, so no `syside`-marked test was skipped for want of a licence.

**Result: no new failure, mypy error or ruff finding.** Every number matches the baseline; only the number of passing tests grew.

| Check | Baseline (`ebb3d467`) | Now | Same set? |
|---|---|---|---|
| `uv run pytest tests/` | 6 failed, 3947 passed, 8 skipped, 17 deselected, 1 xfailed | 6 failed, 4411 passed, 8 skipped, 17 deselected, 1 xfailed (123.6 s) | Yes: the same six ids (pandoc, equation detection, index scripts) |
| `uv run mypy src/` | 97 errors in 19 files (89 source files) | 97 errors in 19 files (96 source files) | Yes: the error lines match the baseline listing once line numbers are removed |
| `uv run ruff check src/ tests/` | 118 findings | 118 findings | Yes: `--output-format concise` matches the baseline listing by file, rule and message once line and column are removed |
| `uv run pytest -m syside --collect-only -q` | n/a | 275 of 4443 tests collected | n/a |

The six failing tests:

- `tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown`
- `tests/test_check.py::TestProbePandoc::test_conversion_error`
- `tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]`
- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`
- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs`
- `tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs`

**Not run:** the slow corpus tests (`-m slow`, the 17 deselected), as in the baseline.

## After the audit fixes

Recorded 2026-10-19 at branch HEAD `41b14ca9` (the six audit-fix commits, `da603e0d`..`41b14ca9`), against the same baseline.

**Result: no new failure, mypy error or ruff finding.**

| Check | Baseline (`ebb3d467`) | Now | Same set? |
|---|---|---|---|
| `uv run pytest tests/` | 6 failed, 3947 passed, 8 skipped, 17 deselected, 1 xfailed | 6 failed, 4426 passed, 8 skipped, 17 deselected, 1 xfailed (126.8 s) | Yes: the same six ids as above |
| `uv run mypy src/` | 97 errors in 19 files | 97 errors in 19 files (96 source files) | Yes: error lines match the baseline listing with line numbers removed |
| `uv run ruff check src/ tests/` | 118 findings | 118 findings | Yes: concise output matches the baseline listing with line and column removed |
| `uv run pytest -m syside --collect-only -q` | n/a | ============= 284/4458 tests collected (4174 deselected) in 1.03s ============== | n/a |

Touched files pass `ruff check` and `ruff format --check`; `mypy src/` reports no error in a touched file that the baseline does not list. Not run: the slow corpus tests (`-m slow`).
