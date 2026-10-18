# Final repository checks (Phase 8, Repo-1)

**Result: green against the Phase 1 baseline.** No new test failure, mypy and ruff at the baseline counts with nothing in a touched file, every touched Python file formatted. Run 2026-10-18 at `positional-binding-check` `60c75af3` (the working tree also held only the six unrelated `.project`/`.gitignore` edits and this evidence). SysIDE 0.8.4; licence key from `.env`.

## Tests

| Run | Baseline (`ccd57d83`, `evidence/baseline-ccd57d83.md`) | Final (`60c75af3`) |
|---|---|---|
| `uv run pytest tests/` | 6 failed, 3647 passed, 8 skipped, 14 deselected, 1 xfailed (run with `--ignore=tests/learning`) | 6 failed, 3936 passed, 8 skipped, 17 deselected, 1 xfailed (learning tests included) |

The 6 failures are the baseline's 6, node for node: three in `tests/test_check.py` (pandoc probe), `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations` (no `PIL`), and two in `tests/test_index.py` (the stale `/home/reid/1cfe/agentic-mbse` path). The 3 extra deselected tests are this item's slow tree tests.

**Slow tests:** `POSITIONAL_BINDING_FUSION_TEA_REPO=/home/reid/src/fusion-tea POSITIONAL_BINDING_DC3_REPO=/home/reid/src/dc3 uv run pytest tests/ -m slow -rs` → 2 failed, 13 passed, 2 skipped.

- Ran and passed: `tests/test_validation/test_positional_binding_trees.py` (3, the fusion-tea and dc3 comparisons), 9 in `tests/test_research/`, and 1 in `tests/test_equations.py`.
- Skipped (2): `tests/test_corpus_integration.py:33` and `:49`, "got empty parameter set for (pdf_path)".
- Failed (2): `tests/test_corpus_integration.py::test_ground_truth_scoring` ("PDF not found at .../tests/corpus/pdfs/...") and `tests/test_equations.py::TestCorpusEquations::test_hawker_recall` (0 equations). Both need corpus PDFs that are not in this checkout (`tests/corpus/pdfs/` does not exist). They touch nothing this item changed. The Phase 1 baseline did not run the slow lane, so there is no recorded base result to compare; not re-run at `ccd57d83`.

**Which of this item's test modules need the SysIDE licence.** Each was run with `SYSIDE_LICENSE_KEY=` (blank):

- Need it, and fail loudly without it (error or failures, never a silent skip): `tests/learning/test_syside_input_redefinition.py`, `tests/test_sysml/test_parameter_redefinition_extraction.py`, `tests/test_validation/test_positional_binding.py`, `test_positional_binding_native_values.py`, `test_positional_binding_policy.py` (27 of 31), `test_positional_examples.py` (3 of 4).
- Do not need it: `test_positional_binding_rule.py`, `test_positional_pins.py`, `test_positional_binding_reference.py`, `tests/test_shipped_text.py`, `tests/test_packaged_guidance_contract.py`.
- `test_positional_binding_trees.py` is slow-only; it loads models, so it needs the licence too.

## Type and lint checks

- `uv run mypy src/`: 97 errors in 19 files, equal to the baseline. None is in this item's new modules (`parameter_redefinition_*`, `positional_*`, `project_root.py`); the touched `level2_structure.py`, `runner.py` and `common.py` keep only their pre-existing errors (Phase 5 notes).
- `uv run ruff check src/ tests/`: 118 errors, equal to the baseline count (all pre-existing, 117 in `tests/`).
- The 30 Python files this branch adds or changes under `src/`, `tests/` and `scripts/` (`git diff --name-only ccd57d83`): `ruff check` passes and `ruff format --check` reports all 30 formatted. New and changed test and script files are clean under `mypy --follow-imports=silent` (checked per phase).

## Siblings

sysml-codegen `8396cb23`, dc3 `60b44d5`, fusion-tea `f96ad312` (checkout HEADs): no working-tree changes before or after this session's runs. Every read went through `git archive`, `ls-tree`, `cat-file`, `rev-parse`, `ls-remote` or `status`.
