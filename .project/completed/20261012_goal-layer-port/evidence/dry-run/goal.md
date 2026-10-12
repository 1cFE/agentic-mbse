# Goal: Does the supplied drain pump keep the sump basin from overflowing at the design inflow?

Procedure is in `work/orchestration/GOAL_RUNBOOK.md` § Grounding a goal; this file does not restate it.

Unwrapped prose, ISO dates, newest entry last. Nothing here is edited in place once the goal is grounded — corrections go in § Amendments.

## Status

`grounded` — 2026-10-11. The operator agreed in advance to `grounded` once all five field classes (grounding evidence, answer contract, invariants, limits, reserved gates) are filled; they are filled below.

## Question

Can the station model report whether the supplied drain pump keeps the sump basin from overflowing at the design inflow?

## Consumer

The station's design reviewer, who decides whether to keep the supplied pump.

## Answered when

The model reports, for the supplied pump, whether its installed capacity covers the flow needed at the design inflow.

Read concretely: the station model carries an executable check that compares `pump.installed_flow_capacity` (supplied) with the required flow computed from the basin at `basin.design_inflow`, and the model's supported execution route yields a definite covers / does-not-cover result for the supplied pump. A hand calculation outside the model does not answer the goal.

## Invariants

- **Package:** `Drainage` (`models/library/drainage.sysml`) and `Station` (`models/designs/station/station.sysml`) as seeded at `e24e41c`. The basin's supplied values (`area` 12.0 m², `design_inflow` 0.30 m³/s, `allowed_rise_rate` 0.005 m/s) and the pump's supplied `installed_flow_capacity` 0.25 m³/s are the design under evaluation and do not move under a comparison. The `RequiredPumpFlow` equation (`required_flow = inflow − allowed_rise_rate · basin_area`) is used as seeded; reinterpreting it is a "new or reinterpreted equation" trigger (`GOAL_RUNBOOK.md` § Review scope and evidence reuse).
- **Comparison:** "covers" means installed capacity ≥ required flow at the design inflow, the overflow criterion being that the basin level rises no faster than `allowed_rise_rate` (the meaning stated in `RequiredPumpFlow`'s doc). Changing the criterion, the inflow case, or the supplied values changes comparison meaning.
- **Modeling requirements:** `modeling_project/REQUIREMENTS.md@e24e41c` holds no PR entries, so none apply beyond `MODELING_GUIDE.md`. This is a model-changing goal; the design-choice pattern (`design-choices.md`, toolkit `docs/patterns/`) applies directly. Design choices this goal **preserves**:

  | Quantity | Unit | Role (current = intended) | Binding location |
  |---|---|---|---|
  | `pump.installed_flow_capacity` | m³/s | chosen — installed capacity, supplied by the design | `station.sysml`, `part pump` |
  | `basin.area`, `basin.design_inflow`, `basin.allowed_rise_rate` | m², m³/s, m/s | chosen — supplied basin design and design case | `station.sysml`, `part basin` |
  | `required_flow` | m³/s | calculated — physical demand | `station.sysml`, `calc demand : RequiredPumpFlow` |

  No sizing or selection policy is authorized. Installed capacity must not be bound to required flow, directly, through a calc, or through a margin or default. An insufficient pump is reported as a shortfall, never enlarged. Any change to these roles is a design-choice change requiring focused independent design review before dependent implementation.

## Grounding evidence

- `models/designs/station/station.sysml@e24e41c` — the station already supplies the pump (0.25 m³/s) and computes `required_flow` via `RequiredPumpFlow`, but carries no check comparing them. The model therefore does not yet report fit; that is the gap this goal addresses.
- `models/library/drainage.sysml@e24e41c` — `RequiredPumpFlow`, `SumpBasin`, `DrainPump`; no capacity-fit constraint def exists.
- `modeling_project/REQUIREMENTS.md@e24e41c` — no project requirements recorded.
- `knowledge/KNOWLEDGE.md@e24e41c`, `knowledge/SOURCE_INDEX.md@e24e41c` — no domain insights or registered sources; the station values are fixture inputs, not sourced data (doc comment in `station.sysml`).
- `work/BACKLOG.md@e24e41c` — no existing work items; nothing in the repository already answers the question.
- Design-choice pattern, toolkit `docs/patterns/design-choices.md` (installed package; unpinned; no native digest) — § Validated Pattern gives the sump/pump "evaluate the supplied design" form with a one-sided `assert constraint`.

## Limits

| Limit | This goal |
|---|---|
| Retry cap | 2 retries (3 attempts) |
| Checkpoint revision cap | 2 revisions (3 submissions) |
| Round limit | 6 rounds |
| Time or iteration limit | none |

Runbook defaults, restated explicitly at the operator's direction.

## Reserved gates

- The goal close.
- Any change to the goal's question.

## Close rule

Owner-held. The owner closes this goal on § Answered when.

## Amendments

None.
