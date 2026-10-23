---
id: 0005
title: validate L6 never says whether a model generates; execution-target only folds four legacy generator-only codes under native, and a broken check or setting fails under every target
date: 2026-10-21
owner: Reid Westwood
status: amended
amended_by: [0006]
superseded_by: null
supersedes: 0003
provenance: "[AGENT] (direction ratified by owner, 2026-10-21; L6 details are spec D-a to D-c, agent-grade)"
surfaces: [validate L6, validate --execution-target, init --execution-target, "pyproject.toml tool.agentic-mbse"]
checked: 2026-10-21 @ 508aad86
---

## Promise

`agentic-mbse validate` L6 checks architecture (ADR-002 placement, manifests and its legacy checks) and makes no claim about whether the generator will build the model. `execution-target` changes how results are shown, never what they are: under `native` the four legacy generator-only codes (`L6_MISSING_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_CALC_DEF_NO_INSTANTIATION`) fold into one INFO summary, and every other code keeps its own severity. A broken check or an invalid setting (`L6_SETTING_INVALID`) is an error under every target.

## Authority

- [AGENT] (ratified by owner, 2026-10-21) `.project/adr/0004-generator-is-the-only-generation-authority.md`.
- `.project/adr/0005-execution-target-after-copy-retired.md` (amends ADR 0003); `.project/adr/0003-execution-target-setting.md` for the setting itself.
- `.project/completed/20261022_retire-subset-profile/spec.md` R1, D-a, D-b, D-c.

## Scope

Filed with the decision on 2026-10-21, before the L6 rewire; the rewire landed in plan Phase 4 (`7a68c702`) and the item's Phase 6 audit confirmed it. Every run that includes L6 ends, pass or fail, with a line saying L6 does not check generation and naming `sysml-codegen check` (Phase 6 fix). The pre-Item-3 `L6_DESIGN_ATTR_UNEXTRACTABLE` reports for String values come back (spec D-c).
