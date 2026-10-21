# Plan: Retire the copied generator rules

**Status:** In progress
**Created:** 2026-10-21
**Spec:** [spec.md](spec.md). **Inventory:** [scope-report.md](scope-report.md) (line numbers are from agentic-mbse `main` `e268357f`), [codegen-part.md](codegen-part.md).

## Order and why

sysml-codegen reads agentic-mbse through an editable path dependency on `../agentic-mbse`, which is this worktree. So sysml-codegen has to stop using the copy (and take its 154 case models) before agentic-mbse deletes anything under `src/`. Guidance and workflow text touch only `docs/`, `skills/` and `project_templates/`, so they run alongside Phase 1.

| Phase | Repo | What |
|---|---|---|
| 0 | both | Baselines |
| 1 | sysml-codegen | Take in the case models; remove the screen step and the agreement tests |
| 2 | agentic-mbse | Guidance: the three structural limits, fix the four calc-owned assert examples |
| 3 | agentic-mbse | Workflow: run `sysml-codegen check` early |
| 4 | agentic-mbse | Move Item 4's helpers, then delete the copy and rewire L6 |
| 5 | both | Documentation: ADR, promises, epic, shipped docs |
| 6 | both | Verification and fresh-agent audit |

## Phase 0: Baselines

- [x] agentic-mbse suite on `e268357f` (record failures). sysml-codegen suite on 2b HEAD (expect the 9 base failures). Byte manifest (123 subjects) and refusal records (173) on 2b HEAD, using the Item 2b Phase 9 commands. `sysml-codegen check` on dc3's models (`/home/reid/src/dc3`), recorded. Record into `evidence/baseline.md`.

## Phase 1: sysml-codegen stops using the copy

- [x] Copy the 154 case models from agentic-mbse `src/agentic_mbse/sysml/subset_cases/` into sysml-codegen test fixtures; point `tests/helpers/subset_profile/cases.py:415-418` at them. Rename helpers and folders from "subset_profile" to what they are now (generator refusal cases) only where it is cheap and clear.
- [x] Remove the 2b screen step: `subset_screen.py`, `cli/report.py`, the screen call in `run_check` and `_report_after_the_seal`, comments, the screen-only and screen parts of mixed tests, `CLAUDE.md:77`, `docs/architecture/reference/02-orchestration.md:83,87`.
- [x] Remove the agreement-test half of Item 2a: `subset_profile_adapter.py`, the screen half of each stored case, `disagreements.json`, the agreement / reason-mapping / screen-mutation / tripwire / record-coverage / occurrence-parity tests, `_upstream_pins.py` `SUBSET_PROFILE_VERSION`. Keep the generator half (see spec R8).
- [x] `git grep` sysml-codegen for `subset_profile`, `occurrence_extraction`, `subset_extraction`, `subset_facts`, `conformance_case`, `subset_cases`: only history remains.
- [x] Byte manifest and generator-owned refusal fields unchanged; suite at base failures. Update the 2b spec, plan and audit notes with a short pointer to this plan.

## Phase 2: Guidance

- [x] Probe with `sysml-codegen check`: assert inside a calc usage owned by a part (expect refused), `[*]` part multiplicity (refused), `Real[0..*]` calc input (refused), attribute-valued multiplicity `[N]` (record what happens; decides D-d). Keep the probes as evidence.
- [x] Add the three limits to `project_templates/MODELING_GUIDE.md.template` and the matching section of `skills/sysml-conventions/SKILL.md`, with a short correct/incorrect example each; `docs/patterns/constraints.md` and `docs/patterns/adr002-calculations.md` say the same in place.
- [x] Correct the calc-owned assert examples: `constraints.md:157-169`, `syntax-reference.md:58-77`, `semantic-operators.md:466-474` and `:497-517`. Keep what each section teaches (the `assert` prefix, calc structure) but put the assert on a part.
- [x] Shipped-text tests pass; update any that pin the old text.

## Phase 3: Workflow runs the check early

- [x] `project_templates/MODELING_PROCESS.md.template` Process Selection: a row for projects that target generated code (`execution-target = "generated"`): run `sysml-codegen check <models>` when the first model pieces build, at each phase, and before any claim that the model generates; its exit code is the answer (0 builds, 1 refused, 2 usage). A parked project runs it once early, records the result, and does not block (R5).
- [x] Point to it from `skills/design-model`, `plan-model` (an early checkpoint and a final row), `implement-model`, `model-validation` (replace the "does not exist yet" text, add the command beside `validate`), `toolkit-awareness`.
- [x] `tests/test_shipped_text.py:219` asserts the opposite today; change it to assert the new text.

## Phase 4: Delete the copy (only after Phase 1 is committed)

- [x] Move `safe_location` with `_qualified_name`, `_element_ref` and `_IdentityError` into `sysml/fact_refs.py` (or a small `sysml/element_refs.py`); update `parameter_redefinition_extraction.py:39,53`, `tests/test_sysml/test_parameter_redefinition_extraction.py:372-373`, `tests/learning/test_syside_input_redefinition.py:950`. Move `scripts/subset_profile/isolated_tree.py` next to `scripts/positional_binding/run_trees.py`. Item 4 tests unchanged and passing. Commit alone.
- [x] Rewire L6 (`level6_architecture.py`): no contract run, no advisories, no `string_subjects`; replace `subset_presentation.present()` with the small fold that `execution-target` still needs (4 legacy codes under `native`, `execution_target.py:204-222`); keep `L6_SETTING_INVALID`. Remove the retired L6 codes from `types.py:111-125`. Move `UNSET_NOTE` used by `init` (`cli/__init__.py:26,734`) into `execution_target.py` and reword it.
- [x] Delete the copy's modules, tests, helpers, fixtures (keep `tests/fixtures/subset_profile/inventory/scanner.toml` and `cases/conditional_operator.sysml` by moving them next to the tests that still read them), `scripts/subset_profile/`, `scripts/l6_subset/` (check `record_reconstruct_texts.py` first), and the pre-merge gate with its test, in one commit. Edit the mixed tests listed in scope-report § 1b.
- [x] `invocation_allowlist.py:8` docstring. `git grep` for the retired names: only history remains. Suite, mypy, ruff clean apart from base failures.
- [x] Re-run sysml-codegen's suite against this branch (its `../agentic-mbse`): still at base failures.

## Phase 5: Documentation

- [x] `.project/adr/0004-...`: generator is the only refusal authority; supersedes ADR 0001; records the options weighed and the design page as the source. Update ADR 0001's status, `adr/INDEX.md`.
- [x] ADR 0003 amended: what the setting does now (D-a). Product promises: P-0001 retired; P-0003 amended; `product/INDEX.md`.
- [x] Epic `backlog/epic_executable-subset-contract.md`: Item 1 retired by this work; 2a keeps its generator half; 2b's screen step removed; 3's display removed; Item 5 loses scope 4 and its profile-dependent checks, and scope 5's assert corrections are done here; Item 6 scope 1 done here, the rest rewritten without the profile. Owner decisions section notes 2026-10-21. `BACKLOG.md`: drop `SUBSET-PROFILE-TYPING-AND-LITERAL-CANDIDATES` as moot (one line, why).
- [x] Shipped docs: `README.md:19-30`, `CLAUDE.md:124`, `skills/model-validation/SKILL.md`, `docs/research-seam.md:350,415` check. sysml-codegen docs if anything remains.
- [x] `CURRENT_WORK.md` row.

## Phase 6: Verify

- [ ] Both suites; byte and refusal identity; TEAx 124/124 if the runtime is available; dc3 `check` answer unchanged.
- [ ] Fresh-agent audit of both branches against this spec; fix blockers.
- [ ] Summary for the owner: what changed, what to merge in which order (sysml-codegen first), PR #21 to close.

## Implementation notes

- **Phases 0-1 (sysml-codegen, 2026-10-21):** commits `eab2e910`, `c670e1a4`, `0f47ea83`, `75e0d32d`, `51078fd3`, `4e037a88` on `subset-profile-screen`. Suite 8442 passed with the same 9 base failures; byte manifest 0/123 differ; refusal records 0/173 differ (the records never held screen output); dc3 `check` exit 0, unchanged. 49 of the 65 copy-side witnesses fire in the generator run and moved into the stored answers; the 16 that fired only in the screen run were dropped. Details: [evidence/phase-1-notes.md](evidence/phase-1-notes.md), [evidence/baseline.md](evidence/baseline.md), [evidence/probes.md](evidence/probes.md). Left for Phase 6 cleanup: the site account's `rule` and `matrix_row` columns still hold the copy's rule IDs; `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` is moot.
- **Phase 5 records:** commits `e058db3f`..`b4ce5f2f`. ADR 0004 supersedes ADR 0001; ADR 0005 amends ADR 0003 (ADR bodies are immutable once filed). P-0004 supersedes P-0001; P-0005 supersedes P-0003 rather than amending it, because P-0003's one-line promise no longer holds; P-0005 needs its check stamp after Phase 4.

**Phase 0 (agentic-mbse half).** Suite baseline in `evidence/suite-baseline-agentic.md`: 5 failed, 4447 passed, all five environment tests outside this item's paths.

**Phase 2.** Probes in `evidence/probes.md` (written by the Phase 0-1 agent). Two deviations from the plan's wording, both following the probes:
- Limit 3 reads "a calculation input receives one value", not "do not declare a sequence input": a `Real[0..*]` input bound to one scalar builds (probe g2); what is refused is a sequence reaching the input (g1, g3, and `guidance-examples/s_bad3`, a feature across three parts).
- Limit 2 counts a number or an `Integer` attribute of the owning part def with a fixed value as exact; a package-level attribute is refused (f1). Surprise, beyond the probes: a count given as `default := 2` and redefined to 3 in a usage or a specializing part def builds two parts with no warning (`guidance-examples/m_attr`, `m_attr_spec`). The guidance says so, and `mbse-concepts.md` "Parameterized Multiplicity Pattern" (which taught exactly that override for trade studies) now shows it as incorrect for generated code. `[N]` in the cost-aggregation examples (`adr002-calculations.md`, `mbse-concepts.md`) became `[3]`.
- Every new or corrected example was run through `sysml-codegen check` as a full model (`evidence/guidance-examples/`). The `semantic-operators.md` prefix example now uses a `Real` attribute in kelvin, because the original `Temperature` type does not load and a quantity type is refused.
- New shipped-text tests pin the three limits and scan every shipped `sysml` fence for an `assert constraint` inside a calc body that is not labelled incorrect.

**Phase 3.** `MODELING_PROCESS.md.template` has a Process Selection row and a "Generated code" section (command, exit codes, when to run, parked, missing); the five skills point to it; the modelling guide's checklist has a line for it.
- The real command is `sysml-codegen check --models <path>` (`--models`/`-m` is required; there is no positional argument), so the text says `uv run sysml-codegen check --models models/`.
- Exit 2 is ambiguous in practice: `uv run` also exits 2 when `sysml-codegen` is not installed ("Failed to spawn"). The text says so.
- "Parked" is defined as: the project's work record or `OVERVIEW.md` says generation is set aside. There is no setting for it. Assumption, for the owner to confirm.
- `test_shipped_text.py`: the inverted assertion now applies only to README, in its own test that Phase 5 replaces (README is outside Phases 2-3's paths); model-validation gets a test pinning the new text. The profile-version assertions are untouched for Phase 4. `model-validation/SKILL.md` keeps its profile description until Phase 4/5; only the "does not exist yet" clause changed.
- Suite after Phases 2-3: 5 failed (the same five as the baseline), 4459 passed (12 new tests).

**Phase 4 and the shipped-doc part of Phase 5.** Commits `c5139617` (helpers move), `7a68c702` (L6 rewire), `2f49eb7b` (delete the copy), `0dcfeb66` (docstrings), `9a21b46c` (shipped docs).
- Item 4's helpers live in a new `sysml/element_refs.py` as `element_ref`, `ElementIdentityError` and `safe_location`, not in `fact_refs.py`, because `fact_refs.py` is the pure, SysIDE-free half. The tripwire test that pinned the private names in `subset_extraction` is gone.
- Deviation: `isolated_tree.py` was not moved. `scripts/positional_binding/run_trees.py` used four of its helpers (about 20 lines), which now sit in `run_trees.py`; the rest of that file built the codegen tree for the deleted gate.
- L6: `subset_presentation.py` is replaced by `execution_target.fold()` and `FOLDED_UNDER_NATIVE` (the four codes). Every other issue keeps its severity, in check order (the old tiered ordering went with the presentation). Under `native` the metric line reads "N folded; each is listed in --json-report"; under unset it prints the reworded `UNSET_NOTE`. String design attributes report `L6_DESIGN_ATTR_UNEXTRACTABLE` again (D-c); no kept test expected the suppression.
- Assumptions for the owner: L6's title is now "Architecture & Codegen Conventions" (it was "Architecture & Generator Subset"; before Item 3, "Architecture & Pipeline Readiness"). The JSON report's per-level key `profile` is now `detail`, still under `validate-report/v1`; nothing in either repo reads it.
- The scanner TOML was not kept: the executable-profile computed-reason test states its five expected reason sets inline. The conditional-spelling learning test holds its model inline. The reconstruct-texts record now keeps only the 122 files still in this repo (a pure deletion from the JSON), so the relocation map and the one-shot recorder went.
- Shipped docs: README, CLAUDE.md and `model-validation/SKILL.md` rewritten; `docs/research-seam.md:350,415` name only `execution-target` as a key, so unchanged.
- Verification: agentic-mbse suite 5 failed (the five baseline IDs), 3567 passed; 892 fewer passing tests than after Phases 2-3 (4459), all from deleted tests (729 in the copy's own test files, the rest in `test_l6_contract.py`, `test_l6_advisories.py` and single tests). mypy 88 errors and ruff 118, both unchanged from base. sysml-codegen suite against this branch: 8442 passed, the same 9 base failures. `git grep` for the retired names outside history finds only `.project/` records (ADR 0001, P-0001, the epic, `CURRENT_WORK.md`, `execution/ENTRIES.md:27`). `validate --level=6` on a fixture project: under `native` the anonymous-return ERROR folds into the summary; under `generated` it shows as an ERROR; the String attribute reports UNEXTRACTABLE in both.
- Now unused in `src/`: `reference_use.invocation_uses` and `InvocationUse` were read only by the subset facts. Left in place (tests still cover them); removing them is a Phase 6 audit question.
