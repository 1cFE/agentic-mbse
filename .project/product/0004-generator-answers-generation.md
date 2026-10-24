---
id: 0004
title: Only the generator answers whether a model generates: shipped guidance states its three structural limits, and the modelling workflow runs sysml-codegen check early when a project targets generated code
date: 2026-10-21
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
supersedes: 0001
provenance: "[AGENT] (ratified by owner, 2026-10-21)"
surfaces: [MODELING_GUIDE.md, MODELING_PROCESS.md, skills/sysml-conventions, skills/design-model, skills/plan-model, skills/implement-model, skills/model-validation, skills/toolkit-awareness, docs/patterns]
checked: 2026-10-21 @ 508aad86
---

## Promise

agentic-mbse never tells a modeller whether a model will generate; only `sysml-codegen check` or `generate` does. The shipped guidance states the generator's three structural limits with a correct and an incorrect example each (an `assert constraint` goes on a part, not inside a calculation; part counts are exact; a calculation input receives one value), and no shipped example teaches an assert inside a calculation as correct. When a project targets generated code, the installed `MODELING_PROCESS.md` and workflow skills run `sysml-codegen check --models <path>` as soon as the first model pieces exist, at each phase and before any claim that the model generates; a parked project runs it once early without blocking, and a missing generator is reported as "generation not checked".

## Authority

- [AGENT] (ratified by owner, 2026-10-21) `.project/adr/0004-generator-is-the-only-generation-authority.md`.
- `.project/completed/20261022_retire-subset-profile/spec.md` R3, R4 [INFERRED] (ratified by owner, 2026-10-21) and R5 [INFERRED: owner assumption stated in chat, not contradicted].

## Evidence

- `tests/test_shipped_text.py`: `test_guidance_states_the_three_generator_limits`, `test_pattern_docs_state_the_limits_in_place`, `test_no_shipped_example_teaches_an_assert_inside_a_calculation_as_correct`, `test_modeling_process_says_when_and_how_to_run_the_generation_check`, `test_workflow_skill_points_at_the_generation_check`, `test_model_validation_names_the_generation_check`.
- Every new or corrected example was run through `sysml-codegen check` (`.project/completed/20261022_retire-subset-profile/evidence/guidance-examples/`, `evidence/probes.md`).

## Scope

The workflow step only runs when the AI modelling skills are used. Nothing runs the check automatically; L6 does not call it (ADR 0004, option C not taken).

L6's copy of the generator rules was removed in plan Phase 4 (commits `7a68c702`, `2f49eb7b`), so the first sentence of the promise holds; every run that includes L6 now ends with a line pointing to `sysml-codegen check`.
