---
id: 0005
title: execution-target stays after the copy is retired: it folds four legacy L6 codes under native and tells the workflow a project targets generated code
date: 2026-10-21
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (keeping the setting ratified by owner, 2026-10-21; its two remaining jobs are spec D-a, agent-grade)"
seams: [l6, validate-cli, init, target-projects, modelling-workflow]
supersedes: null
promoted_to: null
---

## Decision

The `[tool.agentic-mbse] execution-target = "generated" | "native"` setting from ADR 0003 stays, with two jobs now that the copied generator rules are gone (ADR 0004). (1) Under `native`, L6 still folds the four legacy generator-only codes (`L6_MISSING_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_CALC_DEF_NO_INSTANTIATION`) into one INFO summary; every other code keeps its own severity. (2) `generated` is how the workflow skills and `MODELING_PROCESS.md` know a project targets generated code, so they run `sysml-codegen check`. The setting no longer sets the loudness of refused, omitted, excluded, unconfirmed or unverified findings, because L6 no longer produces any.

## Why

- The design page's keep-list kept the setting, and the owner approved that recommendation on 2026-10-21.
- It is already shipped: `init --execution-target` writes it, and `validate --execution-target` overrides it.
- Without it the workflow has no trigger for running `check`, and native projects would get the four legacy generator-only errors back.

## Invariants established

1. ADR 0003 invariants 1, 2 and 3 still hold: the settings key set is closed and a defect is an error (`L6_SETTING_INVALID`); no target makes an inspection failure pass; under `native` only the four legacy codes are lowered.
2. ADR 0003 invariant 4 still holds: the target changes how a result is shown, never the result.
3. The setting never makes L6 claim a model generates, under any target.

## Rejected alternatives

- Dropping the setting with the copy: not chosen, because it would remove the workflow's trigger and bring back the legacy generator-only errors for native projects.

Source: `.project/completed/20261022_retire-subset-profile/spec.md` D-a; plan Phase 4 (L6 rewire).
