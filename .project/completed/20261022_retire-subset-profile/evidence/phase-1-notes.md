# Phase 1 notes (sysml-codegen stops using the copy)

Done 2026-10-21 on sysml-codegen branch `subset-profile-screen` (worktree `/home/reid/src/subset-conformance/sysml-codegen`), from `529830cf`. Nothing in agentic-mbse was edited except this `evidence/` folder. Baselines are in `baseline.md`, probes in `probes.md`.

## Commits (sysml-codegen)

1. `eab2e910` generate and check no longer run the subset screen; check reports only the generator's answer.
2. `c670e1a4` the agreement tests between the generator and the subset screen are removed; the generator half stays.
3. `0f47ea83` the 154 conformance case models move into sysml-codegen; every case now lives in `tests/fixtures`.
4. `75e0d32d` the conformance harness is renamed `subset_profile` -> `refusal_cases`.
5. `51078fd3` Item 2b plan Phase 11 entry, spec and audit header pointers to this plan.
6. `4e037a88` three open backlog items point at the renamed case store.

## Plan checkboxes this covers

- Phase 0, sysml-codegen half: done (`baseline.md`). The agentic-mbse suite baseline was not run by this agent.
- Phase 1, all five boxes: done. Order differs from the plan's list (below).
- Phase 2, first box (probes): done (`probes.md`).

## What changed, by plan box

- **Case models.** All 154 `model.sysml` files copied byte for byte from agentic-mbse `src/agentic_mbse/sysml/subset_cases/<id>/` into sysml-codegen `tests/fixtures/refusal_cases/<id>/`. Each stored answer took its `construct` from `case.json` and lost `home`. The generator outcome, codes, reasons, stubs and seams are unchanged in all 246 answers.
- **Agentic-mbse witnesses.** 58 moved cases named 65 agentic-mbse sites in `agentic_site_witnesses`. Measured before the move, 49 of those fire in the generator half (sites in `executable_profile.py`, `reference_use.py`, `constraint_extraction.py` that the generator calls). Those 49 now sit in the case's `generator.witnesses`, where the existing witness test checks they fire. The 16 that only the screen half fired were dropped with the screen (one is in `subset_extraction.py`).
- **Screen step.** `subset_screen.py` and `cli/report.py` deleted; `run_check` returns `Prepared | Refused` and `cmd_check` prints `prepare.log_generator_answer`, the same line `generate` prints before writing; `_report_after_the_seal` gone. `CLAUDE.md` and `docs/architecture/reference/02-orchestration.md` updated.
- **Agreement half.** `subset_profile_adapter.py`, the `SUBSET_PROFILE_VERSION` pin, `disagreements.json`, the screen half of every stored answer, the `screen` entries of `mutations.json` (schema now `subset-mutations/2`), and the agreement, disagreement-record, reason-mapping, record-coverage, screen-half, screen-mutation, tripwire, candidate-mark, occurrence-parity and site-reason-vocabulary tests are removed. The site account lost the adapter's 2 rows (now 489 sites). The live fixture-class check survives as `test_fixture_classes_live.py`.
- **Rename.** `tests/{helpers,conformance,expectations,fixtures}/subset_profile/` became `.../refusal_cases/`; `tests/fixtures/subset_profile_occurrence_seed/` became `tests/fixtures/occurrence_seed/`; `tests/unit/test_subset_case_answers.py` became `test_refusal_case_answers.py`.

## Verification (at `75e0d32d`; later commits touch only `.project/`)

- **Suite:** 8442 passed, 9 failed, 9 skipped, 124 deselected. The 9 failures are exactly the base 9 IDs in `baseline.md`. The 9 skips are the base skips. The pass count fell from 11240 because the removed tests are gone; no kept test fails or newly skips.
- **Byte manifest:** `scripts/package_manifest.py compare` against `.project/active/subset-profile-screen/evidence/package-manifest-base.json`: 0 differences (123 subjects), after each of commits 1-4.
- **Refusal records:** `scripts/refusal_records.py compare`: 0 of 173 differ, after each of commits 1-4. The records never carried screen output (they hold only refusal-carrying log records), so no field changed.
- **Static:** mypy `src/` clean (89 files, was 92: the two deleted screen modules and the adapter). `ruff check src/` clean; `ruff check src/ tests/` 94, the base count.
- **No reach into the copy:** the full suite was also run with an import blocker (a `sitecustomize.py` on `PYTHONPATH`) that fails any import of the retired agentic-mbse modules made from outside agentic-mbse: same result, 8442 passed, 9 base failures, and zero blocked imports recorded. agentic-mbse still imports `occurrence_extraction` itself, from `parameter_redefinition_extraction.py:39` (Item 4); that is its Phase 4 move.
- **`git grep`** in sysml-codegen for `subset_profile`, `occurrence_extraction`, `subset_extraction`, `subset_facts`, `conformance_case`, `subset_cases`, `subset_coverage`, `occurrence_facts`: hits only under `.project/active/subset-profile-screen/` (Item 2b's own records).
- **dc3:** `sysml-codegen check --models /home/reid/src/dc3/models` after Phase 1: exit 0, "Generator: builds (140 modules)", the same answer as the baseline, with no screen lines.
- **Probes:** all 12 re-run after Phase 1 give the same exit code and the same first generator line as before.

## Deviations from the plan

- **Order.** The plan lists "copy the case models" first. I removed the screen step first, then the agreement half, then moved the models, so each commit stays green on its own: the agreement tests read the screen half of the packaged `case.json` files until they were deleted. Commit 1 moved Item 2a's agreement rule from `cli/report.py` back into the test helper for one commit, until commit 2 deleted it.
- **Adapter.** The plan puts `subset_profile_adapter.py` in the agreement half; it went in commit 2 as planned, but after commit 1 it was imported only by tests, so its docstring said so for one commit.
- **One slip, fixed before the next commit.** Commit 2 at first removed `_rebind_everywhere` from the observe helper while `scripts/refusal_records.py` still imported it. The refusal-record script caught it. The function moved into that script, its only user, and commit 2 was amended before commit 3.

## Not done or not checked

- TEAx execution lane: not run.
- agentic-mbse suite: not run by this agent.
- The site account keeps its `matrix_row` and `rule` columns, which hold the copy's matrix-row and rule IDs as stored data. `witnesses.shared_rule_sites()` still uses the `rule` column to choose which sites the mutation test neutralizes. Removing the columns would mean redesigning which sites are mutated, so I left them.
- Schema names `subset-mutations/2` and `subset-fixture-classes/1` keep the word "subset".
- sysml-codegen backlog row `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` is now moot. I did not edit it; it belongs to Phase 5's documentation pass.
