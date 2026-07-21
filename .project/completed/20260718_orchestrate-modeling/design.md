# Design: Orchestrate Modeling

**Status:** Approved
**Owner:** Reid W
**Created:** 2026-07-17T14:27:31-07:00
**Updated:** 2026-07-18T08:42:25-07:00
**Branch:** constraint-exec-epic
**Commit:** 82fef09

## Overview

`/orchestrate-modeling` will be a thin, judgment-led coordinator that carries either one modeling
work item or a decomposed epic through the existing model-building commands after one owner alignment.

## Related Artifacts

- **Spec:** `.project/active/orchestrate-modeling/spec.md`
- **Research:** `.project/research/20260703-112157_command-refresh-from-agentic-project-init.md`
- **Reference:** `/home/reid/agentic-project-init/claude-pack/commands/_my_orchestrate.md`
- **Related epic:** `.project/backlog/epic_command-refresh.md` (not assigned to this work item)

## Research Findings

- The existing Standard flow is already made of usable stage boundaries: the spec is the first
  state-bearing artifact (`claude/commands/spec-model.md:11`), design produces a validated prototype
  (`claude/commands/design-model.md:70`), review is optional and advisory
  (`claude/commands/review-model.md:15`), and audit defines itself as the final quality stage
  (`claude/commands/audit-models.md:15`).
- Epic guidance already defines decomposition by independently validatable domain concern and records a
  dependency map (`project_templates/EPIC_GUIDE.md.template:65`,
  `project_templates/EPIC_GUIDE.md.template:81`). It should be reused, not reimplemented.
- `modeling_project/MODELING_PROCESS.md` is already tool-owned and read by modeling commands
  (`src/agentic_mbse/cli/__init__.py:79`, `claude/commands/design-model.md:35`). Its template currently
  describes a detailed design methodology, not the complete command flow
  (`project_templates/MODELING_PROCESS.md.template:9`,
  `project_templates/MODELING_PROCESS.md.template:67`).
- The project already treats deterministic state as facts for an agent to interpret. Work-item stage is
  derived from artifact existence, but only through spec, design, and plan
  (`src/agentic_mbse/pm/state.py:75`). This is enough for orientation, not a precise orchestration
  cursor.
- Commands and skills are tool-owned installation units. Command registration drives normal install,
  modification detection, dev symlinks, and `install-commands`
  (`src/agentic_mbse/cli/__init__.py:17`, `src/agentic_mbse/cli/__init__.py:596`,
  `src/agentic_mbse/cli/__init__.py:736`, `src/agentic_mbse/cli/__init__.py:1014`).
- The repository has no general headless stage helper. Its existing `claude -p` wrapper disables session
  persistence and only permits reads, so it is not an orchestration primitive
  (`src/agentic_mbse/extraction/claude_enhance.py:78`). Existing modeling commands already use Task
  agents for bounded parallel work (`claude/commands/design-model.md:54`).
- Epic creation is currently broken across the documented interfaces. `/backlog` instructs agents to
  call a nonexistent `pm add-to-backlog` with an `epic` scale (`claude/commands/backlog.md:39`), while
  the CLI only exposes `pm add-item`, accepts Trivial or Standard, and requires priority
  (`src/agentic_mbse/cli/pm_cli.py:491`). The underlying operation can only add an item to an epic that
  already exists (`src/agentic_mbse/pm/operations.py:906`).
- The documentation also disagrees on the finish boundary. The epic guide ends Standard work at
  implementation (`project_templates/EPIC_GUIDE.md.template:19`), while audit is the stated final stage.
  Closing is separately owner-confirmed and archives the item (`claude/commands/audit-models.md:92`,
  `src/agentic_mbse/pm/operations.py:949`).

## Core Concept

The orchestrator is an agent operating from a short map, not a workflow engine. It reads the objective,
the canonical modeling flow, and current filesystem state; aligns once with the owner; then delegates
each existing stage to a fresh Task agent. It supplies intent and provenance, evaluates the returned
artifact or question, and chooses the next stage. A Standard item runs through the complete item cycle.
An epic is decomposed into Standard items and executes the same cycle in dependency order. A static,
orchestrator-owned alignment brief preserves intent before the first stage exists. Existing artifacts
remain the durable state, and a fresh audit supplies the completion evidence.

## Key Bets

- **B1.** A capable agent with a clear stage map can make ordinary routing, decomposition, and repair
  decisions more faithfully than a fixed state machine. *If false → the thin command will behave
  inconsistently and a deterministic orchestration engine will be needed.*
- **B2.** The alignment brief, normal pipeline artifacts, backlog state, and git history give a
  restarted orchestrator enough context to resume safely. *If false → long epic runs will lose
  decisions or repeat work, requiring a dedicated run manifest.*
- **B3.** The current modeling commands are coherent enough to remain the units of delegation once their
  conflicting flow descriptions are reconciled. *If false → orchestration will need to duplicate or
  replace stage behavior, defeating the goal of a thin coordinator.*
- **B4.** Stage agents will honor a non-interactive overlay that requires them to return all blocking
  questions before writing their artifact. *If false → routine stage checkpoints will leak through to
  the owner or leave partial artifacts, and the Task-only delegation mechanism will not work reliably.*

## Key Decisions

- **D1. Canonical flow lives at the top of `MODELING_PROCESS.md`.** Add a concise command-level map to
  the existing tool-owned template, then let its detailed modeling methodology follow. Commands point
  there; epic detail stays in `EPIC_GUIDE.md`. *Rejected: a new pipeline skill or a full map embedded in
  the orchestrator (both create another source that can drift).*
- **D2. Delegate with fresh built-in Task agents.** Every call receives a self-contained brief and tells
  the agent to read and execute the relevant installed stage command in non-interactive orchestration
  context. If it returns questions, the orchestrator answers them and launches a fresh Task with the
  original brief plus those answers. No Task-session continuation capability is assumed. *Rejected:
  porting the software pipeline's shell helper and session protocol (new installation, permission,
  logging, and recovery machinery without evidence it is needed).*
- **D3. Repair epic registration rather than bypassing project state.** Add one narrow
  `agentic-mbse pm add-epic` operation, correct `/backlog` and `/status` to use real PM commands, and let
  the existing decomposition stage own epic files and item registration. The owner selected this
  approach on 2026-07-17. *Rejected: directly edit
  script-owned `BACKLOG.md` (breaks its ownership invariant), or support only pre-existing epics (does
  not meet the requested input scope).*
- **D4. A positive independent audit is the finish boundary.** The orchestrator repairs and re-audits
  failures. After two unsuccessful repair-and-audit rounds for the same finding, or sooner when a round
  makes no material progress, it parks dependent work and surfaces the failure. A materially new audit
  finding starts its own repair cycle. Close/archive remains an owner-reserved action. *Rejected:
  automatic closure, because every current close path requires explicit owner confirmation.*
- **D5. Do not add an orchestration-state subsystem.** On launch or restart, inspect project state and
  artifacts, then continue from the earliest incomplete obligation. Immediately after Align, write
  `work/orchestration/<objective-slug>.md` with the objective, input source, provenance grades, owner
  decisions, reserved gates, and premise conflicts. This static brief has no stage cursor or status and
  is linked from the eventual spec or epic. *Rejected: putting orchestrator-owned content in a
  stage-owned spec, or adding a run database before a concrete recovery failure demonstrates the need.*

## Architecture

The canonical route is:

```text
orient → align once → [research] → [decompose epic]
  → spec-model → design-model → [review-model] → plan-model
  → implement-model → audit-models → report; owner may close
```

For a Standard objective, the orchestrator enters at the earliest stage not already satisfied. For an
epic, decomposition produces a dependency DAG. Each item runs the whole Standard cycle. Items may run
concurrently only when their dependencies and write surfaces do not overlap; each parallel wave ends
with integrated model validation. After all work-item audits pass, a fresh agent checks epic success
criteria and cross-item integration.

Each self-contained stage handoff cites the alignment brief and contains the relevant decisions,
reserved gates, upstream artifact paths, and the specific job for that stage. Stage agents do not
interact with the owner. They return all blocking questions before writing an artifact. The orchestrator
answers by launching a fresh Task with the original handoff plus the answers, then applies this decision
policy:

1. Decide and record ordinary execution detail.
2. Park work that depends on an owner-reserved gate; continue independent work.
3. Surface evidence against an aligned premise and stop only when all remaining work depends on it.

The orchestration overlay supersedes routine approval pauses inside stage commands. It does not
supersede source conflicts, changes to aligned scope or semantics, intentional major baseline
deviations, or close/archive approval.

## Required Invariants

- The initial owner alignment is the only planned checkpoint.
- The orchestrator writes its alignment brief before any pipeline stage proceeds; later governing
  artifacts link to it rather than owning its content.
- Every Standard item retains the full spec-to-audit artifact chain.
- Authoring and audit use fresh agent contexts.
- Epic items represent complete domain concerns, never workflow phases.
- Dependency and write-surface independence are both required for parallel item execution.
- `BACKLOG.md` state changes go through PM operations.
- Source conflicts and premise surprises are never resolved silently.
- A run is not reported complete without positive independent evidence.

## Component Overview

- **Canonical flow documentation** — `project_templates/MODELING_PROCESS.md.template`; owns the short
  entry, branch, stage, review, audit, and close map.
- **Orchestrator command** — `claude/commands/orchestrate-modeling.md`; owns orientation, one-time
  alignment, Task delegation, decision tiers, epic scheduling, and final reporting.
- **Epic registration repair** — PM CLI/operation plus corrected backlog commands; gives the existing
  epic decomposition path a valid deterministic mutation interface.
- **Alignment brief** — `work/orchestration/<objective-slug>.md`; an orchestrator-owned, immutable input
  record that exists before spec or epic authoring and contains no run cursor.
- **Existing modeling stages** — remain responsible for their own artifacts and domain-specific quality
  work. Small edits reconcile their entry/exit wording with the canonical map.
- **Installation and tests** — register the new tool-owned command in both installation paths and verify
  listing, normal copy, dev symlink, hash protection, and manifest parity.

## Non-Goals

- Encoding stage transitions in a new workflow engine.
- Rewriting the existing stage commands inside the orchestrator.
- Porting software-only PR, code-quality, or pre-PR stages.
- Tracking Task session IDs or adding a run database in the first version.
- Automatically closing or archiving audited work.

## Implementation Notes

- The command should stay self-contained enough to appear in `install-commands --list`; the canonical
  target document is present after full `init`.
- Create `work/orchestration/` on first use. Do not add a template or a PM state type for it.
- The PM interface is `agentic-mbse pm add-epic --name <name> --priority <P0-P3> --file <path>` with an
  optional `--goal <G-XXX>`; it registers an already-written epic file and rejects duplicate names.
- Correct stale flow facts encountered on the touched path, including the `Levels 4-8` reference in
  `claude/commands/plan-model.md:109` and `/backlog clear` in
  `project_templates/README.md.template:148`. The README template correction reaches new projects only;
  existing projects receive the canonical flow through tool-owned `MODELING_PROCESS.md` on re-init.
- Preserve command frontmatter conventions and include Task in `allowed-tools`.
- Do not reuse the extraction `invoke_claude` helper; its permissions and no-session contract are wrong
  for authoring stages.
- Keep the parent context light: use stage final results as the primary signal and read artifacts only
  when a routing or quality decision requires their detail.

## Potential Risks

- **A stage agent follows its normal approval pauses.** B4 is tested through tabletop scenarios. The
  stage brief requires all blocking questions in one final response before artifact creation; the
  parent treats routine approvals as its responsibility and preserves only reserved gates.
- **Filesystem state is too coarse after interruption.** Resume by checking artifact contents and plan
  checkboxes, not only PM's derived stage. If dogfooding shows repeated work or lost gates, add one small
  run manifest in a later item rather than prebuilding it.
- **Parallel epic items edit shared model surfaces.** Serial execution is the safe default. Parallelize
  only after checking both dependency and file ownership, then validate the integrated tree after each
  wave.
- **The new PM operation creates inconsistent epic records.** Require a unique epic name, a valid
  priority, and an existing epic file path before updating `BACKLOG.md`; render through the existing
  parser/writer path used by `add_item` (`src/agentic_mbse/pm/operations.py:892`).
- **Flow documentation drifts again.** `MODELING_PROCESS.md` owns the complete map. Other commands and
  templates link to it and state only local predecessor/successor facts.
- **Epic audit becomes a vague project audit.** Extend `audit-models` with an explicit epic scope that
  checks every epic success criterion, item audit result, and cross-item integration obligation.

## Integration Strategy

Implementation adds capability around the current workflow instead of replacing it:

1. Repair epic registration with `pm add-epic` and align `/backlog` and `/status` with the real CLI.
2. Establish the concise canonical map in `MODELING_PROCESS.md`; correct touched stale references in
   the README, epic guide, plan, implementation, and audit commands.
3. Add `/orchestrate-modeling`, which reads that map and delegates existing commands through Task.
4. Extend `/audit-models` just enough to accept epic scope and produce final integration evidence.
5. Register and test the command through both `cmd_init` and `replicate_setup.sh`.

No existing artifact schema changes. The PM stage enum remains coarse by design. Existing commands stay
independently user-invocable; orchestration is an optional overlay.

## Validation Approach

- **PM operation tests:** add an epic to an empty and populated backlog; reject duplicate names, missing
  epic files, and invalid priorities; confirm rendered markdown and parser round-trip; cover CLI success
  and failure dispatch.
- **Installation tests:** assert the new command appears in `install-commands --list`, installs normally,
  symlinks in dev mode, participates in hash protection, and is present in both installation manifests.
- **Documentation contract checks:** assert the canonical map includes Standard and Epic branches,
  optional research/review, mandatory audit, and owner-held close; remove stale conflicting stage maps
  on touched surfaces.
- **Command review:** verify the orchestrator has exactly one planned owner checkpoint, writes the
  alignment brief before the first stage, names the three decision tiers, gives every Task a
  self-contained non-interactive brief, and contains no fixed state table or copied stage implementation.
- **Tabletop scenarios:** walk one standalone objective and one two-item dependency epic from empty
  project state to positive audit. Include a crash after Align but before spec, a returned stage question
  followed by fresh relaunch, two unsuccessful repairs of one audit finding, a reserved gate, and an
  interrupted/resumed run.
- **Regression:** run the focused PM/CLI tests, then the normal project test suite and Ruff checks.

## Next-Stage Handoff

Treat these as fixed:

- The command is prompt-led and uses built-in Task agents, not a shell or Python orchestration engine.
- `MODELING_PROCESS.md` is the canonical flow source.
- Standard work ends at a positive independent audit; closing stays with the owner.
- Epic work decomposes into complete Standard items, then receives a final epic integration audit.
- `pm add-epic` is included and `BACKLOG.md` remains script-owned.
- The immutable alignment brief and existing artifacts provide resume state for the first version.

The plan should resolve file-level sequencing for the PM repair, documentation reconciliation, command,
audit extension, installation, and tests. The first proof point is a tabletop epic from an empty backlog:
if epic registration or resume orientation cannot work without direct state edits, stop and revise the
design before writing the orchestrator prompt.

---

**Next Step:** After approval, proceed to `my-plan`.
