---
id: 0006
title: Each check lives in one repo: agentic-mbse keeps no copy of a generator check, and execution-target no longer folds any code
date: 2026-10-23
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[OWNER] (goal, Reid, 2026-10-23); which checks were copies is [AGENT]"
seams: [agentic-mbse, sysml-codegen, l2, l6, execution-target, validate-report]
supersedes: null
promoted_to: null
---

## Decision

[OWNER] Reid, 2026-10-23: "each check lives in one repo". sysml-codegen is the only place that decides what the generator accepts. agentic-mbse's validator checks only what holds for any SysML model (syntax, structure, traceability) and the project's own conventions (ADR-002, manifests, design-attribute completeness). The hand-copied generator checks are deleted, and `tests/test_validation/test_no_generator_copies.py` fails if a validation module cites a generator diagnostic, rule or commit again.

## Why

- A copy has to change in two repos whenever the generator changes, and it goes stale: `L6_ATTR_REDEF_EXPR_DROPPED` warned about a drop the generator had already stopped doing.
- `sysml-codegen check` already gives the generation answer (ADR 0004), so a copy adds nothing a project that generates does not already run.

## What changed

- Removed from L6 (`validation/level6_architecture.py`): `L6_MISSING_QUALIFIED_NAME`, `L6_INVALID_QUALIFIED_NAME`, `L6_CALC_DEF_NO_OUTPUT`, `L6_INVALID_BINDING_FORMAT`, `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_CALC_DEF_NO_INSTANTIATION`, `L6_ATTR_REDEF_EXPR_DROPPED`, and the "Bindings validated" metric.
- Removed from L2 (`validation/level2_structure.py`): `L2_SELF_NAMED_BINDING` (the copy of the generator's self-binding refusal).
- Removed from `validation/execution_target.py`: `FOLDED_UNDER_NATIVE` and `fold`. Nothing is left to fold, so `native` changes no result. The setting keeps one job: `generated` tells the workflow to run `sysml-codegen check`. The JSON report drops its `summarized` list (schema `validate-report/v3`).
- Kept: ADR-002 checks (`validation/adr002.py`, comments no longer cite generator commits), the L2 positional-binding check, `L6_CALC_DEF_NO_DIRECTION`, `L6_DESIGN_ATTR_INCOMPLETE` / `L6_DESIGN_ATTR_UNEXTRACTABLE`, the constraint checks over `sysml/executable_profile.py` (one shared implementation that sysml-codegen imports, not a copy), and the manifest checks.

## Invariants established

1. Amends ADR 0004 invariant 1: L6 keeps no legacy convention check that overlaps generator behaviour. No module under `src/agentic_mbse/validation/` cites a generator diagnostic name, rule or commit; a pointer to `sysml-codegen check` is allowed.
2. Amends ADR 0005: `execution-target` lowers no code under any target. ADR 0005 invariant 1's "under `native` only the four legacy codes are lowered" now reads "no code is lowered".

## Rejected alternatives

- Keeping the copies as "conventions": not chosen, because each one encodes a decision the generator makes and was kept in step by hand.
