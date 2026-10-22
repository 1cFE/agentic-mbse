# agentic-mbse suite baseline

Run before any Phase 2 or 3 edit, on branch `retire-subset-profile` at `6afedc47` (base `main` `e268357f` plus the item's planning commits, which touch only `.project/`).

Command: `uv run pytest tests/ -q -p no:cacheprovider` (default markers, so slow corpus tests are deselected).

Result: 5 failed, 4447 passed, 8 skipped, 17 deselected, 1 xfailed, in 132 s.

Failing tests (none of them read shipped guidance text; they are environment tests for pandoc and the index scripts):

- `tests/test_check.py::TestProbePandoc::test_conversion_error`
- `tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown`
- `tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]`
- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs`
- `tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs`

Not checked: why these five fail. They are outside this item's paths.
