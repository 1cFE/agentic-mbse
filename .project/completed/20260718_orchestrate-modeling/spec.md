# Spec: Orchestrate Modeling

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-07-17T14:11:52-07:00
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic

---

## Problem

Agentic MBSE provides commands for individual modeling stages, including specification, design,
planning, implementation, review, and audit. A user still has to choose and coordinate those stages,
carry intent between them, and manage the branch between a single work item and an epic. The software
workflow in `agentic-project-init` now provides a judgment-led orchestrator for the equivalent coding
pipeline. Agentic MBSE needs a modeling counterpart that can carry an objective through the full
model-building flow without turning the orchestration command into a workflow engine.

## Success Criteria

- [x] A user can give `/orchestrate-modeling` a modeling objective and have it drive either one work
  item or an epic through the appropriate modeling stages.
- [x] The overall model-building flow is documented clearly enough that the orchestrating agent can
  choose an entry point, route optional stages, sequence dependent epic items, and know when the run
  is complete.
- [x] The owner aligns once at launch; after that, the orchestrator completes the run autonomously
  unless it reaches an owner-reserved gate or discovers evidence against a premise the work depends on.
- [x] The completed run produces the applicable modeling artifacts, implemented model changes,
  validation evidence, and an independent review or audit trail.
- [x] The orchestration stays thin: stage selection and ordinary execution decisions rely on agent
  judgment rather than an exhaustive encoded state machine.
- [x] The command is installed and discoverable in target repositories through the same supported
  paths as the existing modeling commands.

## Known Requirements

- **[NEED]** `/orchestrate-modeling` must support both a single modeling work item and an epic with
  multiple work items.
- **[NEED]** The feature must include clear documentation of the overall model-building flow.
- **[NEED]** The orchestrator must lean on the intelligence of the agent, and the command itself must
  not be overengineered.
- **[INFERRED]** The run must use the software orchestrator's autonomy pattern: one initial alignment
  checkpoint, autonomous handling of execution details, parking of owner-reserved gates, and explicit
  surfacing of evidence that conflicts with a premise. This four-part decomposition came from the
  reference and was ratified by the owner on 2026-07-17.
- **[INFERRED]** The orchestrator should decide the appropriate entry point and stage path from the
  supplied objective and current project state instead of requiring the user to prescribe the route.
- **[INFERRED]** Epic runs should order work items by their dependencies and carry the original modeling
  intent into every item and stage.
- **[INFERRED]** Authoring and independent review or audit should use separate agent contexts so the
  orchestrator does not treat an implementing agent's self-assessment as certification.
- **[HARD]** The command must be registered in the repository's command installation surfaces; target
  repositories receive shipped commands through `MBSE_COMMANDS` in `src/agentic_mbse/cli/__init__.py`
  and the development replication list in `scripts/replicate_setup.sh`.

## Non-Goals

- Building a deterministic workflow engine that encodes every possible route, decision, or recovery
  state in the command.
- Replacing the existing stage commands with one monolithic modeling prompt.
- Copying software-specific stages or quality criteria where they do not serve model development.

## Open Questions / Deferred to design

- Define the canonical modeling pipeline and the roles of existing commands such as `research`,
  `backlog`, `spec-model`, `design-model`, `review-model`, `plan-model`, `implement-model`, and
  `audit-models`, including optional entry and exit points.
- Decide where the canonical flow documentation lives so the orchestrator and the individual commands
  can reference one source without duplicating it.
- Choose the smallest mechanism for launching fresh stage agents, continuing a stage after it returns
  a question to the orchestrator, and recognizing stage completion.
- Define the durable run trail needed for long epic runs, including stage briefs, decisions, validation
  results, and enough recovery information to resume after interruption.
- Set the exact finish boundary for a successful run and decide whether closing or archiving completed
  work remains an explicit owner action.
- Decide which independent epic work may run concurrently and how shared-model consistency is checked
  before integration.

---

## Related Artifacts

- **Reference implementation:** **[REFERENT]**
  `/home/reid/agentic-project-init/claude-pack/commands/_my_orchestrate.md` — the behavior and
  judgment bar to adapt, not a template to copy mechanically.
- **Reference mechanism:** `/home/reid/agentic-project-init/claude-pack/scripts/orchestrate-stage.sh`
- **Project research:** `.project/research/20260703-112157_command-refresh-from-agentic-project-init.md`
- **Related epic:** `.project/backlog/epic_command-refresh.md` (relationship and ownership not yet decided)
- **Design:** `.project/active/orchestrate-modeling/design.md`
- **Reviews:** `.project/active/orchestrate-modeling/spec-review.md`,
  `.project/active/orchestrate-modeling/design-review.md`

---

**Next Steps:** After approval, proceed to `my-design`.
