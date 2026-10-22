# Baseline before Phase 1 (sysml-codegen side)

Recorded 2026-10-21 at sysml-codegen `529830cf` (worktree `/home/reid/src/subset-conformance/sysml-codegen`, branch `subset-profile-screen`, clean), with its editable `../agentic-mbse` at `6afedc47` (branch `retire-subset-profile`; `src/` identical to `e268357f`). License sourced from the worktree's `.env`. The agentic-mbse suite baseline is not in this file; the agent working in agentic-mbse records it.

## sysml-codegen suite

Command: `set -a; source .env; set +a; uv run --all-extras pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=<scratch>/base-codegen.xml`

Result: 11240 passed, 9 failed, 9 skipped, 124 deselected, in 252.5 s (wall 4:15, peak RSS 1.3 GB). This is the Item 2b Phase 10 exit count.

The 9 failures are the Item 2b base 9, by ID:

- `tests/study/test_study_cli.py::test_a_missing_or_unknown_tool_is_a_usage_error[argv1-invalid choice: 'bogus' (choose from indicators, preflight, verify, integrate)]`
- `tests/unit/test_check_ledger_4a.py::test_the_committed_ledger_covers_the_git_derived_set_exactly`
- `tests/unit/test_check_ledger_4a.py::test_the_candidate_set_is_read_from_the_diff_so_deletions_are_visible`
- `tests/unit/test_check_ledger_4a.py::test_an_uncovered_path_fails`
- `tests/unit/test_check_ledger_4a.py::test_an_orphan_row_fails`
- `tests/unit/test_check_ledger_4a.py::test_a_carried_row_that_does_not_exist_at_head_fails`
- `tests/unit/test_check_ledger_4a.py::test_a_row_with_no_reason_fails`
- `tests/unit/test_check_ledger_4a.py::test_an_executed_carried_delete_is_not_reported_as_a_missing_carried_row`
- `tests/unit/test_check_ledger_4a.py::test_the_paths_check_now_fails_on_either_axis`

Static checks: `uv run --extra dev mypy src/` "Success: no issues found in 92 source files"; `ruff check src/` passes; `ruff check src/ tests/` 94 errors (all under `tests/`, same as Item 2b's base).

## Byte manifest (123 subjects)

Commands (Item 2b Phase 0/9): `uv run --all-extras python scripts/package_manifest.py record <scratch>/manifest-head.json`, then `uv run --all-extras python scripts/package_manifest.py compare .project/active/subset-profile-screen/evidence/package-manifest-base.json`.

- 123 subjects, 3418 files, 6 refusing subjects (the same 6 as Item 2b's base), no missing snapshot sources.
- `compare` against the Item 2b base manifest: **0 differences**. So `package-manifest-base.json` in sysml-codegen remains the oracle for Phase 1.

## Refusal records (173)

Command: `uv run --all-extras python scripts/refusal_records.py compare` (compares against the committed `tests/expectations/subset_profile/refusal_records.json`).

- **0 of 173 entries differ.** The records hold only refusal-carrying log records (logger, level, message, `extra`), not the screen's report lines, so removing the screen should not touch them.

## dc3: `sysml-codegen check`

dc3 is at `60b44d5`, read-only. Its models root is `models/` (dc3 `CLAUDE.md:45`, `README.md:28`; `models/library/` and `models/designs/`). dc3's own environment resolves `../sysml-codegen` to `/home/reid/src/sysml-codegen`, not this worktree, so the command was run from the sysml-codegen worktree to use the branch under test:

`uv run sysml-codegen check --models /home/reid/src/dc3/models`

- **Exit 0. No refusal.** Generator line: `Generator: builds (140 modules)`.
- The screen section followed it: `Screen subset-profile/v2 ... verdict clear ...; 15 admitted, 30 omitted; 0 not assessed` with the `string-value-omission` remedy. After Phase 1 only the generator lines should remain.
- dc3 HEAD is the repaired tree, so this baseline shows "builds". The pre-repair dc3 baseline (`808464d`) was not checked here.
