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
