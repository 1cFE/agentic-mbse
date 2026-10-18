# Repository checks at the final implementation revision

The R2 mutation tests the audit asked for (M1) are in `r2-mutations.md`: 14 mutations, all caught.

agentic-mbse `ce0ad1ffbc4070004d8a7a5a1b3e834f4e483508` (the final implementation revision after the audit fixes; first recorded at `9b123cf3`), 2026-10-18, Python 3.12.3, SysIDE 0.8.4, `SYSIDE_LICENSE_KEY` loaded from `.env` by `tests/conftest.py`.

**"Green" here is the orchestrator's definition** (plan § Standing Rules, 2026-10-18): no new failures relative to the `main` baseline at `8b027bbc` (118 ruff errors, 98 mypy errors in 20 files at that merge; 97 in 19 at the branch's start; 3 environment-dependent pytest failures), and every new or modified file passes `ruff check`, `ruff format --check` and `mypy`. The baseline cleanup is out of Item 1's scope.

| Check | Result | Against the baseline |
|---|---|---|
| `uv run pytest tests/` | 3507 passed, 3 failed, 1 skipped, 14 deselected (slow), 1 xfailed | Same 3 failures. +5 passing tests from the audit fixes (3502 at `9b123cf3`) |
| `uv run pytest tests/ -m ""` (slow included) | At `9b123cf3`: 3512 passed, 5 failed, 3 skipped, 1 xfailed. Not re-run at `ce0ad1ff`: the audit fixes add no slow test and touch no slow test's code | The same 3, plus 2 slow corpus tests (below) |
| `uv run ruff check src/ tests/` | 118 errors | Baseline 118; none in Item 1's files or the audit-fix files |
| `uv run ruff format --check src/ tests/` | 76 files would be reformatted | All pre-existing; every Item 1 file is formatted |
| `uv run mypy src/` | 97 errors in 19 files | Baseline at the branch start; none in Item 1's modules, which also pass `mypy --strict` (re-checked for `subset_profile.py` and the two changed test helpers) |

## The failures, all environmental

- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs` and `::test_read_section_script_runs`: point at a stale path `/home/reid/1cfe/agentic-mbse`.
- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`: needs PIL, which is not installed.
- Slow only: `tests/test_corpus_integration.py::test_ground_truth_scoring` and `tests/test_equations.py::TestCorpusEquations::test_hawker_recall`: the corpus PDFs are not present under `tests/corpus/pdfs/`.

## Skipped and expected-failure tests, and why

- `tests/test_corpus_integration.py:33`, `:49` (slow): empty parameter set, because the corpus PDFs are absent.
- `tests/test_sysml/test_adr002.py:281`: needs fusion_modeling CATF models that are not in this repo.
- xfail `tests/test_packaged_guidance_contract.py::test_built_wheel_carries_every_packaged_file_unchanged[docs]`: a known packaging gap that predates Item 1 (the wheel omits `docs/syside/python/v0.8.4/syside/`).

No Item 1 test is skipped.

## Which Item 1 tests need the SysIDE license

Measured by running each of Item 1's 21 new test files with `SYSIDE_LICENSE_KEY` set empty. The license-dependent ones fail loudly without it; none skips silently.

| Needs the license (loads models with SysIDE) | Pure (no license) |
|---|---|
| `test_subset_probe_evidence.py` (its SysIDE half: the evaluator on each probe's model; 145 pure checks pass without it) | `test_subset_matrix.py` (67) |
| `test_sysml/test_conditional_operator_spelling.py` | `test_subset_site_account.py` (15) |
| `test_sysml/test_invocation_uses.py` | `test_subset_probe_judge.py` (46) |
| `test_sysml/test_occurrence_extraction_roots.py` | `test_sysml/test_executable_profile_computed_reasons.py` (5) |
| `test_sysml/test_occurrence_parity.py` (its 34 seed comparisons; 35 pure checks pass) | `test_sysml/test_invocation_allowlist.py` (4) |
| `test_sysml/test_subset_extraction.py` | `test_sysml/test_occurrence_facts.py` (26) |
| `test_sysml/test_subset_profile_rules_instantiation.py` (54 of 55) | `test_sysml/test_subset_extraction_no_reinterpretation.py` (3) |
| `test_sysml/test_subset_profile_rules_modelwide.py` | `test_sysml/test_subset_profile_coupling.py` (5), `_evaluate.py` (23), `_hygiene.py` (1), `_records.py` (40), `_version.py` (2), `_vocabulary.py` (13) |

The recorded script runs (probes, parity, codegen suite, acceptance trees, `validate` diff) also need the license; each records only that a key was present.
