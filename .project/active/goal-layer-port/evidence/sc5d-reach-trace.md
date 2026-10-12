# SC5(d): Reach Trace to the Design-Choice Pattern

**Item:** goal-layer-port (`WRAP-SPLIT` Item 2), Phase 8. **Checked:** 2026-10-11, against the files at `7a5a3a3`.

**Result.** Every route in design Appendix E holds in the final files. Each reaches `docs/patterns/design-choices.md` in at most two named hops. No gap was found, so no pointer was added (D4).

## How to read the table

- **Route starts at** is the line in the skill or goal file that sends the reader on.
- **Hop 1** is the section or line that line names. Where the starting line names the pattern itself, it is hop 1.
- **Hop 2** is the pattern, `docs/patterns/design-choices.md`.
- `MODELING_PROCESS.md` lines are in `project_templates/MODELING_PROCESS.md.template`, installed as `modeling_project/MODELING_PROCESS.md`. Its design-choice lines are the "Process Selection" row (`:24`), the "Architecture & Design" clause (`:60`) and the technical-pattern row (`:76`). All three name `design-choices.md`.

## Trace

| From | Route starts at | Hop 1 | Hop 2 | Holds |
|---|---|---|---|---|
| `spec-model` | `skills/spec-model/SKILL.md:15` "Use “Process Selection” in `modeling_project/MODELING_PROCESS.md`" | `MODELING_PROCESS.md:24`, the design-choice row: "against the design-choice pattern (`design-choices.md`; see Technical Patterns)" | `design-choices.md` | yes |
| `design-model` | `skills/design-model/SKILL.md:21`, reads "Architecture & Design" and uses "its technical-pattern table" | `MODELING_PROCESS.md:60` clause and `:76` row | `design-choices.md` | yes |
| `implement-model` | `skills/implement-model/SKILL.md:25`, "Before changing calculations, bindings, … read the applicable reference selected by the technical-pattern table" | `MODELING_PROCESS.md:76` | `design-choices.md` | yes |
| `quick-model` | `skills/quick-model/SKILL.md:21`, "use the technical-pattern table … to load guidance for the constructs being changed" | `MODELING_PROCESS.md:76` | `design-choices.md` | yes |
| `review-model` | `skills/review-model/SKILL.md:29`, the A5 question | The question itself: "check the actual bindings against `design-choices.md`", where the `:76` row applies | `design-choices.md` | yes |
| `audit-models` | `skills/audit-models/SKILL.md:29`, "Read … relevant architecture/pattern rules in `modeling_project/MODELING_PROCESS.md`" | `MODELING_PROCESS.md:76` row (and the `:60` clause) | `design-choices.md` | yes |
| `model-validation` | `skills/model-validation/SKILL.md:53`, the A5 bullet | The bullet itself: "check the actual bindings against `design-choices.md` and run its acceptance checks" | `design-choices.md` | yes |
| `sysml-conventions` | `skills/sysml-conventions/SKILL.md:213`, the A3 line | The line itself: "Its binding-side sibling is agentic-mbse `docs/patterns/design-choices.md`" | `design-choices.md` | yes |
| `orchestrate-modeling` | `skills/orchestrate-modeling/SKILL.md:39`, "Have the author apply “Process Selection” before editing" | `MODELING_PROCESS.md:24` | `design-choices.md` | yes |
| Goal template | `project_templates/goal.md.template:29`, § Invariants, "apply the design-choice pattern (`design-choices.md`; `GOAL_RUNBOOK.md` § Grounding a goal says where it is)" | `GOAL_RUNBOOK.md.template:85`, § Grounding a goal, with the resolver command | `design-choices.md` | yes |
| Goal runbook | `GOAL_RUNBOOK.md.template:85` (§ Grounding a goal) and `:74` (trigger row, § Review scope and evidence reuse) | `:85` names `design-choices.md` and its resolver command; `:74` names "the design-choice pattern", which `:85` defines | `design-choices.md` | yes |
| `run-goal` | `skills/run-goal/SKILL.md:58`, § Model changes, "the design-choice pattern (`GOAL_RUNBOOK.md` § Grounding a goal says where it is)" | `GOAL_RUNBOOK.md.template:85` | `design-choices.md` | yes |

## How a bare `design-choices.md` is located

The modeling-process rows name the pattern by file name, as every row of that table names its reference. The reader locates it the same way for all of them, so the lookup is not counted as a hop:

- `MODELING_PROCESS.md.template:67`: "Detailed references live in the toolkit's `docs/patterns/` directory; the guide provides navigation."
- `MODELING_GUIDE.md.template:279` gives the resolver command, `get_docs_dir() / "patterns"`, and `:292` lists `design-choices.md` in the Pattern Documentation Index.

The goal-layer route gives the resolver command itself, at `GOAL_RUNBOOK.md.template:85`. Both commands print a directory holding `design-choices.md` in this checkout (`sc2-sc3-install.txt`) and in a wheel install (`tests/test_packaged_guidance_contract.py::test_built_wheel_carries_the_resolver_reached_goal_layer_documents`).

## Reverse direction

The pattern points back at the review trigger, so a reader who starts at the rule reaches review routing. `design-choices.md` § Review names "Process Selection" in `modeling_project/MODELING_PROCESS.md` as the trigger's home (design D2).
