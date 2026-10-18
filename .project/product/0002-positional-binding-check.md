---
id: 0002
title: validate L2 flags inputs bound by position to a differently named formal: new mismatches block, pinned legacy ones warn, and an uninspectable owner never reads clean
date: 2026-10-18
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[AGENT] (ratified by owner: D1 2026-10-15)"
surfaces: [validate L2, positional-pins.toml, docs/patterns/semantic-hazards.md]
checked: 2026-10-18 @ 1681edc8
---

## Promise

`agentic-mbse validate` (L2) reports `L2_POSITIONAL_BINDING` when a calc or constraint input without its own explicit redefinition binds by position to a differently named formal, the hazard where native SysIDE and the generated route give different values. New mismatches are errors; mismatches pinned in the project-root `positional-pins.toml` are warnings that do not by themselves fail L2. An owner whose type, supertype, redefinition or subsetting target does not resolve is reported as `L2_CHECK_UNVERIFIABLE`, never as clean.

## Authority

- [AGENT] (ratified by owner, 2026-10-15) D1 in `.project/backlog/epic_executable-subset-contract.md`.
- `.project/adr/0002-positional-pin-list-contract.md`.
- `.project/completed/20261018_positional-binding-check/spec.md` (reviewed), `.project/completed/20261018_positional-binding-check/design.md` (rev 1, reviewed).

## Evidence

- Rule, facts and pins: `src/agentic_mbse/validation/positional_binding.py`, `positional_pins.py`, `positional_check.py`; `src/agentic_mbse/sysml/parameter_redefinition_extraction.py`.
- SysIDE 0.8.4 behavior pinned by `tests/learning/test_syside_input_redefinition.py`.
- fusion-tea `f96ad312`: exactly the prototype's 125 identities; dc3 `808464d` and `60b44d5`: zero (`.project/completed/20261018_positional-binding-check/evidence/run-trees.md`).
- Register: `docs/patterns/semantic-hazards.md#positional-input-binding`.

## Scope

Calc and constraint usages and definitions, including requirement, case and assert-constraint owners; `subject`/`actor`/`stakeholder` parameters are excluded from the swap rule. The check does not evaluate values or compare routes.
