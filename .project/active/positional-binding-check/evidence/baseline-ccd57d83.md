# Baseline at `ccd57d83` (plan Phase 1, item 1)

**Recorded:** 2026-10-18 · **Branch HEAD:** `ff44256b` (`positional-binding-check`) · **Base:** `ccd57d831aa8c63d29768793627e640d2f54dc1f`

This is what "no new test failures" (plan G1) and "mypy count not above baseline" (G3) are measured against.

## No product change on the branch yet

- `git diff --stat ccd57d83 HEAD -- src scripts docs skills agents project_templates` is empty.
- Under `tests/`, only `tests/learning/__init__.py` and `tests/learning/test_syside_input_redefinition.py` differ (the learning test).
- So `uv run pytest tests/ --ignore=tests/learning` on HEAD is the `ccd57d83` result.

## pytest

`uv run pytest tests/ --ignore=tests/learning -q -p no:cacheprovider -rfE` (default markers, so slow tests are deselected):

- **6 failed, 3647 passed, 8 skipped, 14 deselected, 1 xfailed** in 110 s.

The 6 failing node IDs. None touches validation or SysML; each fails on this machine's environment:

- `tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown` (probe reports FAIL; pandoc path)
- `tests/test_check.py::TestProbePandoc::test_conversion_error`
- `tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]`
- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations` (`ModuleNotFoundError: No module named 'PIL'`)
- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs` (`FileNotFoundError: /home/reid/1cfe/agentic-mbse`, a stale hard-coded path)
- `tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs` (same)

`uv run pytest tests/learning` on HEAD before Phase 1: 43 passed.

## mypy

`uv run mypy src/`: **Found 97 errors in 19 files (checked 83 source files)**. That matches the learning test's count.

## ruff

`uv run ruff check src/ tests/`: **118 errors** (54 F541, 22 F401, 17 W293, 15 I001, 5 F841, 4 E712, 1 N806). All are pre-existing. 117 are under `tests/` (mostly `tests/corpus/pipelines/` and `tests/test_helpers.py`); one is `src/agentic_mbse/extraction/index.py`. G2 is therefore checked per touched file, not repo-wide.

## Environment

- SysIDE `0.8.4`.
- `agentic_mbse.__file__` = `/home/reid/src/agentic-mbse/src/agentic_mbse/__init__.py` (the editable install of this checkout).
- `SYSIDE_LICENSE_KEY` in `.env`: yes. In the shell environment: no (tests load it through `tests/conftest.py`'s `load_dotenv()`).
