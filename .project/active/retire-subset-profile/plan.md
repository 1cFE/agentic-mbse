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

- [ ] agentic-mbse suite on `e268357f` (record failures). sysml-codegen suite on 2b HEAD (expect the 9 base failures). Byte manifest (123 subjects) and refusal records (173) on 2b HEAD, using the Item 2b Phase 9 commands. `sysml-codegen check` on dc3's models (`/home/reid/src/dc3`), recorded. Record into `evidence/baseline.md`.

## Phase 1: sysml-codegen stops using the copy

- [ ] Copy the 154 case models from agentic-mbse `src/agentic_mbse/sysml/subset_cases/` into sysml-codegen test fixtures; point `tests/helpers/subset_profile/cases.py:415-418` at them. Rename helpers and folders from "subset_profile" to what they are now (generator refusal cases) only where it is cheap and clear.
- [ ] Remove the 2b screen step: `subset_screen.py`, `cli/report.py`, the screen call in `run_check` and `_report_after_the_seal`, comments, the screen-only and screen parts of mixed tests, `CLAUDE.md:77`, `docs/architecture/reference/02-orchestration.md:83,87`.
- [ ] Remove the agreement-test half of Item 2a: `subset_profile_adapter.py`, the screen half of each stored case, `disagreements.json`, the agreement / reason-mapping / screen-mutation / tripwire / record-coverage / occurrence-parity tests, `_upstream_pins.py` `SUBSET_PROFILE_VERSION`. Keep the generator half (see spec R8).
- [ ] `git grep` sysml-codegen for `subset_profile`, `occurrence_extraction`, `subset_extraction`, `subset_facts`, `conformance_case`, `subset_cases`: only history remains.
- [ ] Byte manifest and generator-owned refusal fields unchanged; suite at base failures. Update the 2b spec, plan and audit notes with a short pointer to this plan.

## Phase 2: Guidance

- [ ] Probe with `sysml-codegen check`: assert inside a calc usage owned by a part (expect refused), `[*]` part multiplicity (refused), `Real[0..*]` calc input (refused), attribute-valued multiplicity `[N]` (record what happens; decides D-d). Keep the probes as evidence.
- [ ] Add the three limits to `project_templates/MODELING_GUIDE.md.template` and the matching section of `skills/sysml-conventions/SKILL.md`, with a short correct/incorrect example each; `docs/patterns/constraints.md` and `docs/patterns/adr002-calculations.md` say the same in place.
- [ ] Correct the calc-owned assert examples: `constraints.md:157-169`, `syntax-reference.md:58-77`, `semantic-operators.md:466-474` and `:497-517`. Keep what each section teaches (the `assert` prefix, calc structure) but put the assert on a part.
- [ ] Shipped-text tests pass; update any that pin the old text.

## Phase 3: Workflow runs the check early

- [ ] `project_templates/MODELING_PROCESS.md.template` Process Selection: a row for projects that target generated code (`execution-target = "generated"`): run `sysml-codegen check <models>` when the first model pieces build, at each phase, and before any claim that the model generates; its exit code is the answer (0 builds, 1 refused, 2 usage). A parked project runs it once early, records the result, and does not block (R5).
- [ ] Point to it from `skills/design-model`, `plan-model` (an early checkpoint and a final row), `implement-model`, `model-validation` (replace the "does not exist yet" text, add the command beside `validate`), `toolkit-awareness`.
- [ ] `tests/test_shipped_text.py:219` asserts the opposite today; change it to assert the new text.

## Phase 4: Delete the copy (only after Phase 1 is committed)

- [ ] Move `safe_location` with `_qualified_name`, `_element_ref` and `_IdentityError` into `sysml/fact_refs.py` (or a small `sysml/element_refs.py`); update `parameter_redefinition_extraction.py:39,53`, `tests/test_sysml/test_parameter_redefinition_extraction.py:372-373`, `tests/learning/test_syside_input_redefinition.py:950`. Move `scripts/subset_profile/isolated_tree.py` next to `scripts/positional_binding/run_trees.py`. Item 4 tests unchanged and passing. Commit alone.
- [ ] Rewire L6 (`level6_architecture.py`): no contract run, no advisories, no `string_subjects`; replace `subset_presentation.present()` with the small fold that `execution-target` still needs (4 legacy codes under `native`, `execution_target.py:204-222`); keep `L6_SETTING_INVALID`. Remove the retired L6 codes from `types.py:111-125`. Move `UNSET_NOTE` used by `init` (`cli/__init__.py:26,734`) into `execution_target.py` and reword it.
- [ ] Delete the copy's modules, tests, helpers, fixtures (keep `tests/fixtures/subset_profile/inventory/scanner.toml` and `cases/conditional_operator.sysml` by moving them next to the tests that still read them), `scripts/subset_profile/`, `scripts/l6_subset/` (check `record_reconstruct_texts.py` first), and the pre-merge gate with its test, in one commit. Edit the mixed tests listed in scope-report § 1b.
- [ ] `invocation_allowlist.py:8` docstring. `git grep` for the retired names: only history remains. Suite, mypy, ruff clean apart from base failures.
- [ ] Re-run sysml-codegen's suite against this branch (its `../agentic-mbse`): still at base failures.

## Phase 5: Documentation

- [ ] `.project/adr/0004-...`: generator is the only refusal authority; supersedes ADR 0001; records the options weighed and the design page as the source. Update ADR 0001's status, `adr/INDEX.md`.
- [ ] ADR 0003 amended: what the setting does now (D-a). Product promises: P-0001 retired; P-0003 amended; `product/INDEX.md`.
- [ ] Epic `backlog/epic_executable-subset-contract.md`: Item 1 retired by this work; 2a keeps its generator half; 2b's screen step removed; 3's display removed; Item 5 loses scope 4 and its profile-dependent checks, and scope 5's assert corrections are done here; Item 6 scope 1 done here, the rest rewritten without the profile. Owner decisions section notes 2026-10-21. `BACKLOG.md`: drop `SUBSET-PROFILE-TYPING-AND-LITERAL-CANDIDATES` as moot (one line, why).
- [ ] Shipped docs: `README.md:19-30`, `CLAUDE.md:124`, `skills/model-validation/SKILL.md`, `docs/research-seam.md:350,415` check. sysml-codegen docs if anything remains.
- [ ] `CURRENT_WORK.md` row.

## Phase 6: Verify

- [ ] Both suites; byte and refusal identity; TEAx 124/124 if the runtime is available; dc3 `check` answer unchanged.
- [ ] Fresh-agent audit of both branches against this spec; fix blockers.
- [ ] Summary for the owner: what changed, what to merge in which order (sysml-codegen first), PR #21 to close.

## Implementation notes

(Filled in per phase.)
