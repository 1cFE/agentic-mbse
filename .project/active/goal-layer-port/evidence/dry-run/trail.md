# Trail: sump-overflow

What happened, and what was decided.

Append-only, newest entry last, ISO dates. **No entry is ever edited in place.** A correction is `### Amendment YYYY-MM-DD — amends <entry heading>`, stating what changed and why.

This file logs judgment, not routine stage motion. Native workflows keep their own stage records; entries here cite them by path or native id and never restate their content. Procedure is in `work/orchestration/GOAL_RUNBOOK.md`; entry shapes are in `work/orchestration/goal-templates/trail.md`.

## Round 1 — supplied-pump-fit-check

### Strategy revision — 2026-10-11

- **Approach:** make the station model report fit by evaluating the supplied design: add a one-sided capacity-covers-demand constraint to the library and assert it in the station between the supplied `pump.installed_flow_capacity` and the computed `required_flow`, following the design-choice pattern's § Validated Pattern. Then read the check's result for the supplied pump through the supported execution route.
- **Assumptions:** `RequiredPumpFlow` (`models/library/drainage.sysml@e24e41c`) is accepted as seeded for the overflow criterion; the supplied values in `models/designs/station/station.sysml@e24e41c` are the design under evaluation; the project's execution route (syside via `uv run`) can evaluate the asserted constraint or its operands. Design-choice roles are as tabulated in `goal.md` § Invariants and are preserved, not changed.
- **Abandonment conditions:** the check cannot be expressed without binding installed capacity to demand or otherwise changing a design-choice role; the execution route cannot yield a definite result for the asserted check; or the seeded equation proves wrong for the overflow criterion (a reinterpretation, which needs independent source/math review and may change comparison meaning).
- **Intended model increment:** a `CapacityCoversDemand`-style constraint def in `Drainage` and an `assert constraint` in `station` comparing supplied installed capacity with required flow; installed capacity stays a supplied value.
- **Intended study question:** for the supplied pump at the design inflow, does installed capacity cover required flow? No committed study is planned unless the evaluation needs one; no study layer is installed in this target.

**Design-choice record (round):** no role changes. `pump.installed_flow_capacity` stays chosen/supplied; `required_flow` stays calculated; the new constraint reads both and binds neither. No sizing or selection policy is introduced.

### T-001 scope

- **Objective:** add a one-sided capacity-fit check so the station model reports whether the supplied pump's installed capacity covers the required flow at the design inflow.
- **Why now:** the first step of the strategy; grounding evidence shows `station.sysml@e24e41c` computes `required_flow` but has no check against `pump.installed_flow_capacity`, so the model cannot yet answer the question.
- **Scope:** authorized — a new constraint def in `models/library/drainage.sysml`; an `assert constraint` in `models/designs/station/station.sysml`; a model test under `tests/models/` exercising a sufficient and an insufficient supplied pump with the selected design unchanged (design-choice pattern § Acceptance); the native work record via the modeling PM (`/quick-model`). Excluded — any change to supplied basin or pump values, to `RequiredPumpFlow`, or to any design-choice role; any sizing, margin, or selection policy; source registration or reinterpretation of the equation.
- **Inputs:** `goal.md`; `models/library/drainage.sysml@e24e41c`; `models/designs/station/station.sysml@e24e41c`; design-choice pattern § Validated Pattern and § Acceptance; `modeling_project/MODELING_PROCESS.md` § Process Selection. No narrower constraint.
- **Done when:** the model parses and validates with the check asserted, and the execution route yields a definite covers / does-not-cover result for the supplied pump, with the insufficient-pump case failing and the supplied design unchanged (positive); or a bounded negative showing the route cannot yield a definite result.
- **Stop when:** a strategy blocker (the check needs a design-choice role change, or the equation must be reinterpreted), an owner gate (a change to the goal's question), or a declared limit.

**Review selection (coordinator, before dispatch):** `MODELING_PROCESS.md` § Process Selection row 1 — the change follows an existing validated pattern (`design-choices.md` § Validated Pattern), introduces no new or reinterpreted equation or source, changes no ownership, interface, or binding semantics of existing elements, and changes no design-variable role; the new library def is additive with one consumer (`station`). No independent review is triggered before the work; the main agent edits and verifies, and design-choice compliance (compliant | violated | unverified) is recorded at return from the actual bindings and the acceptance test. If the work turns out to need anything beyond this, the trigger is re-assessed before dependent implementation.

### T-001 start — 2026-10-11

T-001 capacity-fit check · modeling PM via `/quick-model` on `models/library/drainage.sysml` and `models/designs/station/station.sysml` · expected artifact: asserted capacity-fit constraint in the station, an acceptance test under `tests/models/`, and the native work record.
