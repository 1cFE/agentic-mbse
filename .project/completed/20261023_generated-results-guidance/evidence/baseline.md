# Baseline (plan Phase 0)

Recorded 2026-10-22, before any sysml-codegen change. Later phases compare against this file: a test failure not listed here is a new failure, and the byte-identity "before" records below are what Phase 2 compares against.

## Revisions

| Repo / tool | Revision | Note |
|---|---|---|
| agentic-mbse | `9abbe86f3558d2802e61f5c17d8ca98215e77e29` | branch `generated-results-guidance` |
| sysml-codegen `origin/main` | `6190f996f81d17e9e8c195120fa3a9bb2bedb6a5` | unchanged from the design and spike; `git diff --stat 6190f996 origin/main -- src` is empty |
| sysml-codegen branch | `native-generated-compare` | created with `git switch -c native-generated-compare origin/main`; `subset-profile-screen` left as it was |
| TEAx | `8d877460ac4f6f264561d916e40c1708adb13397` | same as the spike; `git status --short` empty |
| dc3 | `585ab080856cc252f45729d613f8106cdb4f974f` | `git status --short` shows one untracked folder that predates this work: `?? .project/active/toolkit-update-generator-check/`. Later "dc3 is clean" checks mean "no change from this". |
| SysIDE | 0.8.4 | same in the agentic-mbse venv and dc3's venv |

sysml-codegen `git status --short` was empty before the switch, so nothing was stashed or discarded.

## agentic-mbse base failures

Command (agentic-mbse root): `uv run pytest tests/ -q -rf -p no:randomly`. The `-p no:randomly` flag was added by habit and is not in the plan's command; it only disables a plugin and does not change the test set. Later runs may use either form.

Result: `5 failed, 3559 passed, 8 skipped, 17 deselected, 1 xfailed`. The count matches the plan's expected 5.

```
tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown
tests/test_check.py::TestProbePandoc::test_conversion_error
tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]
tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs
tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs
```

## sysml-codegen base failures

Command (sysml-codegen root, on `native-generated-compare` = `origin/main`, licence sourced): `uv run --extra dev pytest tests/ -q -rf`.

Result: `9 failed, 8503 passed, 9 skipped, 124 deselected`. The count matches the plan's expected 9. Skip count: 9.

```
tests/study/test_study_cli.py::test_a_missing_or_unknown_tool_is_a_usage_error[argv1-invalid choice: 'bogus' (choose from indicators, preflight, verify, integrate)]
tests/unit/test_check_ledger_4a.py::test_the_committed_ledger_covers_the_git_derived_set_exactly
tests/unit/test_check_ledger_4a.py::test_the_candidate_set_is_read_from_the_diff_so_deletions_are_visible
tests/unit/test_check_ledger_4a.py::test_an_uncovered_path_fails
tests/unit/test_check_ledger_4a.py::test_an_orphan_row_fails
tests/unit/test_check_ledger_4a.py::test_a_carried_row_that_does_not_exist_at_head_fails
tests/unit/test_check_ledger_4a.py::test_a_row_with_no_reason_fails
tests/unit/test_check_ledger_4a.py::test_an_executed_carried_delete_is_not_reported_as_a_missing_carried_row
tests/unit/test_check_ledger_4a.py::test_the_paths_check_now_fails_on_either_axis
```

The eight `test_check_ledger_4a.py` failures come from `git diff --name-status 1672c57 07531e64` exiting 128 (a commit that test reads is not in this checkout). Not investigated further; it is a base failure.

## Simkit lane smoke check

From the sysml-codegen root, licence sourced, `PYTHONPATH=src:/home/reid/src/subset-conformance/agentic-mbse/src:/home/reid/src/teax/packages/teax-simkit`, `PYTHONDONTWRITEBYTECODE=1`, interpreter `/home/reid/src/subset-conformance/agentic-mbse/.venv/bin/python`:

```
$ … -c "import sysml_codegen, agentic_mbse, simkit, syside, pytest; print(sysml_codegen.__file__, simkit.__file__); print(agentic_mbse.__file__)"
/home/reid/src/subset-conformance/sysml-codegen/src/sysml_codegen/__init__.py /home/reid/src/teax/packages/teax-simkit/simkit/__init__.py
/home/reid/src/subset-conformance/agentic-mbse/src/agentic_mbse/__init__.py

$ … -m pytest tests/unit/test_teax_discovery.py -p no:cacheprovider -q
tests/unit/test_teax_discovery.py .....                                  [100%]
5 passed in 0.04s
```

All three packages resolve to the subset-conformance checkouts and TEAx's `teax-simkit`, and sysml-codegen's `tests/` package imports under that interpreter. sysml-codegen `git status --short` stayed empty.

## Byte-identity "before" records (RG-1)

All under `/tmp/grg-impl/identity-before/`, generated from untouched `origin/main` code (`6190f996`).

1. **sysml-codegen fixtures.** `uv run --all-extras python scripts/package_manifest.py record /tmp/grg-impl/identity-before/fixtures.json` → exit 0, `recorded 122 subjects (116 generated)`. The run printed two `REGISTRY_CLASS_NAME_COLLISION` refusals, which are recorded subjects, not script failures. sha256 of `fixtures.json`: `bf6321eb40f3903c3a5dd192609c0ddc996e9877ad2bf5657c952087fb683aa8`.
2. **Spike models.** `spike/derisk/identity_record.sh before` (committed in Phase 1; first run from `/tmp/grg-impl/scripts/`) runs `uv run sysml-codegen generate --models <dir> --output /tmp/grg-impl/identity-before/spike/<case> --package-name <case>` from the sysml-codegen root for each case, logging to `log/spike_<case>.txt`:

   | case | source | generate exit |
   |---|---|---|
   | `default_count` | `spike/channel-trace/models/default_count` | 0 |
   | `default_count_literal` | `spike/channel-trace/models/default_count_literal` | 0 |
   | `s1_gen` | `spike/channel-trace/models/s1_gen` | 0 |
   | `s1_native` | `spike/channel-trace/models/s1_native` | 1: `SI_EXPRESSION_SOURCE_UNSUPPORTED … reference='-load'` |
   | `native_path_model` | `spike/native-path/model` | 1: same `-load` refusal |
   | `native_path_model_extra` | `spike/native-path/model_extra` | 1: `size(cells)` … only `NumericalFunctions::sum` is supported |
   | `gen_reversed` | `tests/fixtures/positional_binding/native_values/gen_reversed` | 0 |
   | `gen_byname` | `tests/fixtures/positional_binding/native_values/gen_byname` | 0 |

   127 files. For refused cases the "after" comparison is the refusal log text.
3. **dc3.** The same script runs `generate --models /home/reid/src/dc3/models --package-name dc3_models` → exit 0 (dc3 generates). 183 files.

File list with per-file sha256 for records 2 and 3: `/tmp/grg-impl/identity-before/tree-sha256.txt`, itself sha256 `bec3ae31ea7d4ef9c83e6822971d4e08570e1ae0b89927c23e4518e350912f53`. Tree digests (sha256 of the sorted `sha256sum` listing, taken from inside each folder): spike `bda9f08797b7a36eff45ee75d8e9f4caac33e697e05f8b63f55eb3d15f7ce829`, dc3 `6b38e3ade2e0e492a5e00cc45d07e3651621f36835758ed66333fb99a2b9ed22`.

**Phase 1 models.** They do not exist yet at Phase 0. Phase 1 changes no sysml-codegen code, so their "before" records are taken at the end of Phase 1, on the same untouched `6190f996` code, into `/tmp/grg-impl/identity-before/spike/derisk_<case>` (the script picks up `spike/derisk/models/*`). Phase 1's notes record that run.

`/tmp/` does not survive a reboot. If these records are lost before Phase 2, regenerate them from `origin/main` `6190f996` (a fresh worktree) before changing any code.
