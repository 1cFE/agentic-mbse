# Execution Facts

Append-only log of how this codebase and environment actually behave, discovered while working. Newest at the bottom.

The rules for writing an entry are in `README.md`, in this directory. Do not rewrite or reorder existing entries.

---

## [SysIDE 0.8.4] 2026-10-18

**Fact:** On a usage, `multiplicity` and `declared_multiplicity` return the same element, and neither (nor `is_ordered`) carries through a `:>>` redefinition; a redefining usage with no bounds of its own reads as no multiplicity.
**Evidence:** `.project/completed/20261018_exec-subset-profile/spikes/f1-findings.md` (Surprise 1); the `declared_multiplicity` mutant cannot be caught by any parity case (`evidence/occurrence-parity-controls.log`).

## [sysml-codegen b5663c07] 2026-10-18

**Fact:** `generate` stops at the first expression error, so a model holding several unsupported constructs reports only one; a probe fixture must isolate a single construct, or an earlier refusal hides the one under test (on dc3 `808464d` the 72 multiplicity refusals never surface because an expression refusal comes first).
**Evidence:** `.project/completed/20261018_exec-subset-profile/spikes/f1-findings.md`; design-review L3-4; `evidence/acceptance.md`.

## [sysml-codegen b5663c07] 2026-10-18

**Fact:** `SI_CONSTRAINT_BLOCKED` error lines carry no `[root-0/<file>:<line>]` location; the only location on the line is the shared executable profile's own `[file:line]` suffix. Other refusal codes end with the `root-0/` location when one was measured.
**Evidence:** Phase 7 notes in `.project/completed/20261018_exec-subset-profile/plan.md`; judge handling in `tests/helpers/subset_probe_judge.py`.

## [sysml-codegen git archive export] 2026-10-18

**Fact:** sysml-codegen commits absolute symlinks under `.claude/`, which Python's `tarfile` extraction refuses, and its study tests need a git work tree, so a `git archive` export fails 60 tests (53 failed, 7 errors) for environmental reasons alone.
**Evidence:** `scripts/subset_profile/probe.py` export step; `.project/completed/20261018_exec-subset-profile/evidence/same-generator.md` (identical 60 at every revision).

## [SysIDE 0.8.4] 2026-10-18

**Fact:** An unresolved type, supertype, `:>>` target or `:>` subsetting target does not raise or leave the reference empty: it points at a shared `<placeholder Classifier>` / `<placeholder Feature>` element whose `owning_relationship is None`. Inputs of such an owner silently lose their implied redefinitions and read as brand-new parameters, so a positional swap behind a typo passes unless the placeholder is detected.
**Evidence:** `tests/learning/test_syside_input_redefinition.py` (M1 and subsetting cases); `.project/completed/20261018_positional-binding-check/learning-findings.md`.

## [SysIDE 0.8.4 diagnostics] 2026-10-18

**Fact:** Load diagnostics come in three buckets, `diagnostics.parser`, `diagnostics.sema` and `diagnostics.validation`, and `agentic-mbse validate` L1 reads only `parser`. So `reference-error` ("No Type named 'Sbu' found.") and `redefinition-direction-conformance` pass every level today; `try_load_model` returns a model despite them.
**Evidence:** Item 4 Phase 1 notes in `.project/completed/20261018_positional-binding-check/plan.md`; fixture `tests/fixtures/positional_binding/l1/out_before_in.sysml`; backlog `VALIDATE-SEMA-DIAGNOSTICS`.

## [SysIDE 0.8.4] 2026-10-18

**Fact:** Anonymous elements (e.g. an unnamed `assert constraint` and its inputs) get a fresh random `element_id` on every load, so any sort or identity key that includes it is nondeterministic across runs; sort by location and names instead.
**Evidence:** Item 4 Phase 3 notes in `.project/completed/20261018_positional-binding-check/plan.md` (a test failed 1 run in 3 before the fix).

## [uv 0.12.23] 2026-10-20

**Fact:** A `pyproject.toml` holding only a `[tool...]` table and no `[project]` still makes uv treat that directory as its own project: `uv run` there creates a new `.venv` (warning "No requires-python value found"), `uv lock` succeeds and writes `uv.lock` instead of exiting 2, and a directory nested in another uv project stops using the parent's environment. That is why `init --execution-target` refuses to create the file under a parent `pyproject.toml`.
**Evidence:** Item 3 Phase 9 notes and § Audit fixes in `.project/completed/20261020_l6-subset-profile/plan.md`; ADR 0003.
