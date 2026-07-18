---
name: orchestrate-modeling
description: Drive a modeling objective or Epic through the appropriate model-building stages
skills: [epic-decomposition, project-structure, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Orchestrate Modeling Command

**Purpose:** Given a modeling objective, drive one Standard work item or an Epic through implemented,
independently audited model changes using judgment and the existing modeling commands.
**Input:** An artifact path or an inline modeling objective.
**Output:** The applicable pipeline artifacts, model and test changes, validation evidence, and audit
trail. The owner decides whether to close or archive completed work.

This is a thin coordination command. You hold the objective and quality bar, delegate each modeling
stage to a fresh Task agent, inspect the returned evidence, and choose what comes next. Do not copy the
stage commands into this command or turn the documented flow into a transition engine.

## What Matters Most

- **Stay on modeling intent.** Carry the aligned objective, authority sources, provenance, and scope
  boundaries into every item and stage. An artifact is useful only when it advances that intent.
- **Exercise engineering judgment.** Decide ordinary routing and execution details. Insert research or
  review when it reduces a real risk. Do not add ceremony merely because a stage exists.
- **Demand independent evidence.** Do not accept an implementing agent's self-assessment as completion.
  Standard work ends at a positive work item audit; Epic work ends at a positive Epic integration audit.
- **Keep context light.** Treat each Task result as the primary signal. Read detailed artifacts only
  when a routing, premise, or quality decision requires them.

## Orient

Read the supplied objective or artifact fully. Then read:

- `modeling_project/MODELING_PROCESS.md` for the canonical Standard and Epic flow;
- `work/BACKLOG.md`, relevant Epic files, and `work/active/` and `work/completed/` artifacts;
- `modeling_project/OVERVIEW.md`, `ARCHITECTURE.md`, and `REQUIREMENTS.md` as relevant;
- `knowledge/SOURCE_INDEX.md` and cited knowledge or research artifacts.

Decide whether the objective is Trivial, one Standard item, or an Epic. Identify the earliest
unsatisfied obligation from artifact contents and validation evidence, not filename presence alone.
On a resumed run, find the existing alignment brief and continue from that obligation. Do not repeat
completed stages or reopen settled owner decisions without new conflicting evidence.

## Align Once

Alignment is the only planned owner checkpoint. Before launching any stage, present a short alignment
message and wait for the reply. Cover:

- what the objective means and the outcome you intend to drive toward;
- whether this is Trivial, Standard, or Epic work and the proposed entry point;
- owner-reserved decisions that you must not make;
- provenance gaps, authority conflicts, and evidence against an apparent premise;
- inherited constraints that need an owner decision before being treated as fixed.

After the owner replies, create `work/orchestration/<objective-slug>.md` before launching any stage.
Create `work/orchestration/` on first use. This immutable alignment brief records:

- objective and input-source path or inline text;
- decision-carrying inputs graded as owner-stated, agent-inferred, or inherited, with owner quotes
  preserved where their wording carries force;
- owner decisions from Align and the reserved gates;
- premise conflicts already known and which conclusions remain parked.

Do not put a stage cursor, mutable status, or later execution log in this file. Link the eventual
Standard spec or Epic file to it. Record later execution decisions in the relevant stage artifact or
resulting model evidence.

## Delegate Stages

Every stage runs in a fresh Task agent. Give it a self-contained stage brief with:

- the installed command it must read and execute, such as `/spec-model` or `/audit-models`;
- the alignment-brief path and the objective relevant to this item;
- provenance grades for decision-carrying input;
- the item or Epic scope, upstream artifact paths, applicable decisions, and reserved gates;
- the one concrete job and the evidence that will demonstrate completion;
- this overlay: **Do not interact with the owner. Return all blocking questions before writing an
  artifact. Treat routine approval pauses as parent-orchestrator decisions. Preserve source conflicts,
  aligned-scope changes, major baseline deviations, reserved gates, and premise surprises as blockers.**

Evaluate the Task's final result and verify its claimed artifact or model evidence. If the Task returns
questions, classify them using the decision policy below. For questions you may answer, launch another
fresh Task agent with the original brief plus the answers. Do not continue a prior Task. Keep fresh
authoring and audit contexts, including after repairs.

## Choose and Run the Route

### Trivial route

For a genuinely Trivial change, delegate `/quick-model` in a fresh Task, verify its targeted validation
evidence, and report. If the work reveals a new interface, architectural choice, or broader scope,
reclassify it as Standard work and follow the full route.

### Standard route

Use the canonical flow and enter at the earliest incomplete obligation:

```text
[/research] → /spec-model → /design-model → [/review-model]
  → /plan-model → /implement-model → /audit-models → report
```

Use `/research` for a material knowledge gap or source conflict. Use `/review-model` when an independent
design critique adds confidence. All other shown stages are required unless existing positive evidence
already satisfies their contract. Ensure the spec links to the alignment brief.

Run `/audit-models` in a fresh context. If it fails, send the concrete findings to a fresh authoring
Task for repair, validate the repair, then launch another fresh audit Task. Apply the bounded repair
rule below.

### Epic route

If the Epic does not exist, delegate `/backlog` to write and approve the Epic file, register it with
`agentic-mbse pm add-epic`, and register each complete Standard item with `pm add-item`. Ensure the Epic
file links to the alignment brief.

Treat the decomposition as a dependency graph of domain concerns. Carry Epic intent and applicable
success criteria into every item brief. Execute serially unless two ready items have both independent
dependencies and non-overlapping model write surfaces. After a parallel wave, validate the integrated
tree before starting dependent work.

Run the complete Standard route for every item, including a fresh item audit. When all item audits are
positive, launch a fresh `/audit-models` Task in Epic scope. It must verify every epic success criterion,
every item audit, dependency handoffs, and cross-item integration. Repair and re-audit material Epic
findings under the same bounded rule.

## Decision Policy

Classify every mid-run decision into one tier:

1. **Execution detail:** Decide it, record the choice and rationale in the relevant durable artifact,
   and continue.
2. **Reserved gate:** Do not decide a choice the owner reserved during Align. Park dependent work,
   continue independent work, and surface the gate when all useful independent work is exhausted.
3. **Premise surprise:** When evidence conflicts with a premise the aligned work depends on, record and
   surface the conflict. Park dependent conclusions. Never silently resolve it in either direction.

A stage's routine request for approval is an execution detail under this overlay. Source conflicts,
changes to aligned scope or semantics, intentional major baseline deviations, and owner-held close or
archive decisions are not routine approvals.

## Bound Audit Repair

Track repair attempts by concrete finding. After two unsuccessful repair-and-audit rounds for the same
finding, park the dependent work and surface the failure with the attempted fixes and current evidence.
Park sooner when a round makes no material progress. A materially new finding starts its own bounded
cycle; do not use that distinction to relabel an unchanged failure.

## Finish

Report completion only when fresh independent evidence is positive for the entire scope. Summarize:

- what was modeled and which artifacts were produced;
- validation and audit results, including the Epic integration result when applicable;
- important execution decisions and premise evidence;
- any parked independent work or owner-reserved gate;
- the remaining owner action, if any.

Never archive work as part of this command. The owner decides whether to close after reading the report.

---

**Related Commands:** Canonical flow → `modeling_project/MODELING_PROCESS.md` | Decomposition →
`/backlog` | Final evidence → `/audit-models` | Owner-held archive → `/backlog close` or `/status close`
