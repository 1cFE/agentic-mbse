# Epic: Architecture Redesign — Commands (Phase 3C)

**Epic ID**: EPIC-ARCH-003
**Status**: Ready
**Priority**: P0
**Created**: 2026-02-02
**Concept**: `.project/concepts/architecture-redesign/` (main.md, workflows.md §§ 1–6, components.md § 1, delta-checklist.md § 3A)
**Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` §§ 3A.1–3A.5
**Depends On**: EPIC-ARCH-002 (Knowledge) — skills must exist before commands can reference them

---

## Executive Summary

Refactor all 9 existing commands to replace embedded knowledge with skill references (reducing average from 543 to ~250 lines), create 5 new commands that complete the behavioral layer, register everything in `cmd_init()`, evaluate agent status, and validate refactored commands against fusion-tea to verify no implicit knowledge was lost.

**Critical Success Factor**: All 14 commands install correctly via `agentic-mbse init`, average command length is under 300 lines, each refactored command passes a fusion-tea walkthrough with no knowledge loss, and `/status` works end-to-end with the PM dashboard (Epic 4 dependency).

---

## Why This Epic Comes Third

Commands are the behavioral layer — the user-facing workflows that orchestrate knowledge, project state, and model artifacts. They are the primary consumer of both Epic 1 (information architecture) and Epic 2 (knowledge layer):

- **Commands reference skills** (Epic 2). Skill references replace the 600+ lines of inline SysML knowledge in `design-model.md`, the 200+ lines of validation guidance in `implement-model.md`, etc. Without skills, refactoring would just rearrange the same inline content.
- **Commands reference the file structure** (Epic 1). They read from and write to `knowledge/`, `modeling_project/`, `work/`, `data/` — paths that must be settled.
- **Commands invoke AP-7 scripts** (Epic 4, parallel). Several refactored commands call PM operations (`add-insight`, `trace-element`, `promote-requirement`, `approve-research`). These calls are added during this epic even if Epic 4 implementation is incomplete — the command logic is correct, and the scripts become operational when Epic 4 delivers them.

The commands don't need the PM engine to be complete (Epic 4), but they do need the knowledge layer (Epic 2). The `/status` command is the sole convergence point: it depends on both Epic 3 (command) and Epic 4 (PM dashboard script).

---

## Open Design Questions (Must Resolve During This Epic)

Two questions from main.md § 5 are blocking. This epic must resolve both.

| # | Question | Impact if unresolved | Proposed resolution approach |
|---|----------|---------------------|------------------------------|
| Q12 | How to validate refactored commands don't lose knowledge? | Risk of silent regression — commands may lose nuanced guidance that was embedded in long prompts | D3.5: mandatory fusion-tea walkthrough for each refactored command. D2.5 extraction mapping (from Epic 2) provides the cross-reference baseline. |
| Q15 | Should there be a formal command template (structure all commands must follow)? | Inconsistency across 14 commands; harder to maintain | D3.1: establish pattern from first 2–3 refactored commands, document as convention. Not a rigid template — commands have different jobs — but a consistent structure (frontmatter, skill references, context reading, workflow phases, AP-7 calls). |

---

## Success Criteria

- [x] 9 existing commands refactored with skill references (average 114 lines)
- [x] 5 new commands created (`quick-model`, `review-model`, `analyze-models`, `status`, `formalize-intent`)
- [x] All 14 commands install correctly via `agentic-mbse init` and `replicate_setup.sh`
- [ ] Each refactored command passes a fusion-tea walkthrough with no knowledge loss (Q12 resolved)
- [x] Command structure convention documented (Q15 resolved) — `command-convention.md`
- [ ] `sysmlv2-doc-analyzer` agent status resolved (restored or confirmed deprecated)
- [ ] Agent doc path placeholders standardized across all agent files
- [ ] `/status` command works end-to-end with PM dashboard (requires Epic 4)
- [x] All existing agentic-mbse tests pass (`uv run pytest tests/`) — 342 passed, 1 skipped

---

## Deliverables

Five deliverables with a dependency structure (see [Sequencing](#sequencing) below).

### D3.1: Command Refactoring (9 existing commands)

**Type**: Implementation
**Status**: Complete
**Dependencies**: Epic 2 complete (skills exist, extraction mapping D2.5 available)
**Delta checklist**: § 3A.1 (9 items, each with multiple sub-changes)

**Objective**: Refactor each existing command to replace embedded knowledge with skill references, add AP-7 script calls where applicable, update paths to the new directory structure, and reduce each command to 200–300 lines.

**Design constraints**:
- Use D2.5 extraction mapping as the primary guide for what to remove from each command
- Skill references go in the command's frontmatter or an explicit "Skills referenced" section near the top
- Commands retain **workflow logic** (phases, user decision points, inter-stage data flow) — only shared knowledge moves to skills
- AP-7 script calls are added as concrete invocations the agent should make (e.g., `agentic-mbse pm add-insight ...`)
- New information architecture references are added (reading OVERVIEW.md for G-XXX goals, REQUIREMENTS.md for PR-XXX compliance, etc.)

**Refactoring approach**: Process commands in priority order (most bloated first, since they validate the skill reference pattern and yield the most extraction). Establish the structural convention from the first 2–3 commands before proceeding.

#### Command 1: `design-model.md` (1,345 → ~250 lines)

The largest command and primary source of skill extraction content. Sets the pattern for all subsequent refactoring.

**Current state**: 1,345 lines — ~600 lines SysML syntax patterns, ~200 lines validation guidance, ~150 lines file structure rules, ~100 lines citation patterns, ~295 lines workflow logic.

**Changes**:
1. Extract SysML syntax/patterns → `sysml-conventions` skill reference
2. Extract validation guidance → `model-validation` skill reference
3. Extract file structure rules → `project-structure` skill reference
4. Extract citation/source patterns → `source-traceability` skill reference
5. Add reading of `modeling_project/ARCHITECTURE.md` for existing AD-XXX decisions
6. Add reading of `modeling_project/REQUIREMENTS.md` for PR-XXX compliance
7. Add reference to `review.md` as optional output for `/review-model`
8. Update all directory path references to new 4-directory model

**What stays**: Design workflow phases (understand → analyze → design → prototype → validate → document), user decision points (architecture approach, interface decisions), inter-stage data flow (reads spec.md, produces design.md).

#### Command 2: `implement-model.md` (493 → ~250 lines)

**Changes**:
1. Extract SysML syntax → `sysml-conventions` skill reference
2. Extract validation → `model-validation` skill reference
3. Extract file structure → `project-structure` skill reference
4. Add inline knowledge capture flow: agent calls `agentic-mbse pm add-insight` when discovering domain insights (B-008 pattern)
5. Add traceability recording: agent calls `agentic-mbse pm trace-element` for significant model elements
6. Add requirement promotion: agent calls `agentic-mbse pm promote-requirement` for durable MR-XXX → PR-XXX patterns
7. Update directory path references

**What stays**: Implementation workflow (read plan → execute phases → validate each phase → handle deviations), backward navigation triggers, phase approval gates.

#### Command 3: `spec-model.md` (392 → ~250 lines)

**Changes**:
1. Extract to `project-structure` skill reference
2. Extract to `source-traceability` skill reference
3. Add reading of `knowledge/KNOWLEDGE.md` for DI-XXX insights
4. Add reading of `modeling_project/OVERVIEW.md` for G-XXX goals and AQ-XXX questions
5. Add YAML frontmatter generation for spec.md (Status, Scale, Epic, Owner, Created, Updated)
6. Add SV-XXX entry creation in VALIDATION_MATRIX.md for verification criteria
7. Update directory path references

**What stays**: Spec workflow (understand intent → identify scope → define success criteria → document MR-XXX requirements), scale assessment prompt, epic linkage.

#### Command 4: `plan-model.md` (676 → ~250 lines)

**Changes**:
1. Extract to `model-validation` skill reference
2. Add YAML frontmatter generation for plan.md (Status, Created, Updated, Related Artifacts)
3. Update directory path references

**What stays**: Planning workflow (read design → identify phases → order by dependency → scope each phase → identify risks → document plan), per-phase scope definition, risk assessment.

#### Command 5: `audit-models.md` (446 → ~300 lines)

**Changes**:
1. Extract to `model-validation` skill reference
2. Extract to `source-traceability` skill reference
3. Add `requirements-tracking` skill reference
4. Add decision promotion flow: agent calls `agentic-mbse pm register-decision` when user approves promoting a pattern to AD-XXX
5. Add SV-XXX status updates via `agentic-mbse pm update-validation`
6. Update directory path references

**What stays**: Audit workflow (select scope → run validation pyramid → review findings → promote patterns → update project docs), user decision point on which promotions to accept.

#### Command 6: `research.md` (243 → ~250 lines)

This command may grow slightly due to new workflow steps.

**Changes**:
1. Add `source-traceability` skill reference
2. Add approval workflow: agent calls `agentic-mbse pm approve-research` after user approves findings
3. Add DI-XXX insight suggestion and capture flow
4. Add knowledge supersession detection (flag conflicts with existing DI-XXX entries)
5. Add file save via script (not agent choosing path): `knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md`
6. Update directory path references

**What stays**: Research workflow (identify question → explore sources → synthesize findings → present to user), source exploration using specialist agents.

#### Command 7: `onboard.md` (577 → ~300 lines)

**Changes**:
1. Add `project-structure` skill reference
2. Add `source-traceability` skill reference
3. Add `epic-decomposition` skill reference
4. Add trigger for `/formalize-intent` after initial documents are placed in `modeling_project/intent/`
5. Add initial ARCHITECTURE.md population guidance
6. Update directory path references to new 4-directory model

**What stays**: Onboarding workflow (project setup → source configuration → initial architecture sketch → first epic decomposition), interactive guidance.

#### Command 8: `backlog.md` (358 → ~250 lines)

**Changes**:
1. Add `epic-decomposition` skill reference
2. Add scale assessment (Trivial/Standard/Epic) to work item creation
3. Add epic decomposition flow referencing skill
4. Update BACKLOG.md path to `work/BACKLOG.md`
5. Add YAML frontmatter updates via AP-7 scripts
6. Update directory path references

**What stays**: Backlog management workflow (add/prioritize/decompose/close items), user interaction for prioritization.

#### Command 9: `manage-sources.md` (357 → ~250 lines)

**Changes**:
1. Add `source-traceability` skill reference (extract inline source management knowledge)
2. Update SOURCE_INDEX.md path reference to `knowledge/SOURCE_INDEX.md`
3. Update directory path references

**What stays**: Source management workflow (add/validate/update sources in SOURCE_INDEX.md), source validation criteria.

**Exit criteria**:
- [x] All 9 commands refactored with skill references (avg 114 lines, max 135)
- [x] Average command length under 300 lines (actual avg: 114 lines, 79% reduction)
- [x] All commands reference new directory paths (knowledge/, modeling_project/, work/, data/) — zero `modeling_pm/` refs
- [x] AP-7 script invocations added where specified (implement: 3, audit: 2, research: 1, backlog: inline)
- [x] YAML frontmatter generation added to spec-model, plan-model, and design-model
- [x] Structural convention documented — `.project/active/d3.1-command-refactoring/command-convention.md` (Q15 resolved)
- [x] D2.5 extraction mapping verified — all SKILL sections removed, all PARTIAL trimmed, all STAYS retained

---

### D3.2: New Commands (5 commands)

**Type**: Implementation
**Status**: Pending
**Dependencies**: D3.1 partially complete (structural convention established from first 2–3 refactored commands)
**Delta checklist**: § 3A.2 (5 items)

**Objective**: Create 5 new command files in `claude/commands/` following the structural convention established during D3.1.

#### `/quick-model` — Trivial-scale direct changes

| Field | Value |
|-------|-------|
| Job | Make a small change without the full spec → design → plan pipeline |
| Skills | `sysml-conventions`, `model-validation` |
| Key user decision | Change scope — is this truly trivial? |
| Target length | ~150 lines |

**Workflow**: User describes a small change → agent assesses scope → if trivial: make change directly + run validation → if not trivial: redirect to `/spec-model` with scope explanation. No work item directory. PM doesn't track.

**Guard rail**: The command must include a scope assessment step that honestly evaluates whether the change is trivial. If the change touches multiple files, introduces new patterns, or requires design decisions, the agent redirects to `/spec-model`.

#### `/review-model` — Design review before implementation

| Field | Value |
|-------|-------|
| Job | Review a design document against requirements, conventions, and architecture before implementation begins |
| Skills | `sysml-conventions`, `model-validation`, `project-structure`, `requirements-tracking` |
| Key user decision | Which findings to accept, skip, or defer |
| Target length | ~200 lines |

**Workflow**: Read design.md + spec.md → check against REQUIREMENTS.md and ARCHITECTURE.md → check SysML conventions → produce review.md with verdict (pass/concerns/fail in YAML frontmatter) and findings → user curates findings → if changes accepted, feed back to `/design-model`.

**Design note**: review.md is NOT a PM-tracked stage (DD-3 from frontmatter-schemas.md). It is part of the design stage. The PM engine does not look for review.md. The review is advisory — the user can proceed to `/plan-model` without it (AP-5: toolkit, not pipeline).

#### `/analyze-models` — Model analysis reports

| Field | Value |
|-------|-------|
| Job | Produce model state reports — structure, compliance, health indicators |
| Skills | `project-structure`, `model-validation` |
| Key user decision | Analysis scope (which models, which aspects) |
| Target length | ~200 lines |

**Workflow**: Parse model structure (files, definitions, usages, cross-file deps) → check REQUIREMENTS.md compliance → compute health indicators (validation levels, test coverage, debt markers) → write report to `work/analysis/YYYYMMDD-HHMMSS_topic.md`.

**Open question (Q14)**: Should this be a command (agent-driven, interactive) or a script subcommand (deterministic)? The likely answer is hybrid: script for metrics, agent command for interpretation. For this epic, implement as a command. If Epic 4 produces deterministic analysis capabilities, `/analyze-models` becomes a thin wrapper (similar to `/status`).

#### `/status` — Project state dashboard

| Field | Value |
|-------|-------|
| Job | Present project state and recommend next actions |
| Skills | `epic-decomposition`, `requirements-tracking` |
| Key user decision | What to do next |
| Target length | ~150 lines |

**Workflow**: Call `agentic-mbse status` script (Epic 4 PM dashboard) → present dashboard output → add interpretation (what's blocked, what's ready, what needs attention) → offer recommendations → optional modes: `decompose <epic>`, `close <item>`.

**Dependency**: This command is a thin wrapper around the Epic 4 PM dashboard. It should be the **last command written** in this epic, after Epic 4 delivers the dashboard script. If Epic 4 is incomplete, write the command structure with a placeholder for the script call.

#### `/formalize-intent` — Extract goals and questions from intent documents

| Field | Value |
|-------|-------|
| Job | Process documents in `modeling_project/intent/` to extract G-XXX goals and AQ-XXX analysis questions for OVERVIEW.md |
| Skills | `project-structure` |
| Key user decision | Which extracted G-XXX/AQ-XXX to accept, modify, or skip |
| Target length | ~200 lines |

**Workflow**: Read documents from `modeling_project/intent/` → extract candidate goals (G-XXX) and analysis questions (AQ-XXX) → present each to user for approval/modification/skip → call AP-7 script to register approved entries in OVERVIEW.md → suggest follow-up actions (research for AQ-XXX questions, /spec-model for actionable goals).

**Exit criteria**:
- [ ] 5 new command files exist in `claude/commands/`
- [ ] Each follows the structural convention from D3.1
- [ ] Each has correct skill references
- [ ] `/quick-model` has a working scope guard rail
- [ ] `/review-model` produces review.md with YAML frontmatter (Verdict, Created, Related Artifacts)
- [ ] `/status` calls PM dashboard script (or has documented placeholder for Epic 4)

---

### D3.3: Command Registration

**Type**: Implementation
**Status**: Complete
**Dependencies**: D3.1 and D3.2 (commands must exist to register)
**Delta checklist**: § 3A.3 (2 items)

**Objective**: Register all new commands in the installation pipeline so `agentic-mbse init` and `replicate_setup.sh` install them to target projects.

**Changes to `src/agentic_mbse/cli/__init__.py`**:

Update `MBSE_COMMANDS` list to include new commands:
```python
MBSE_COMMANDS = [
    # Existing (refactored)
    "audit-models.md",
    "backlog.md",
    "design-model.md",
    "implement-model.md",
    "manage-sources.md",
    "onboard.md",
    "plan-model.md",
    "research.md",
    "spec-model.md",
    # New
    "analyze-models.md",      # NEW
    "formalize-intent.md",    # NEW
    "quick-model.md",         # NEW
    "review-model.md",        # NEW
    "status.md",              # NEW
]
```

**Changes to `scripts/replicate_setup.sh`**:

Add new commands to the install loop. Must match `MBSE_COMMANDS` exactly.

**Verification**: After registration, run:
1. `uv run agentic-mbse init /tmp/test-project` — verify all 14 commands appear in `.claude/commands/`
2. `uv run agentic-mbse init --dev` on agentic-mbse repo — verify symlinks for all commands
3. Check each command file installs without errors

**Exit criteria**:
- [x] `MBSE_COMMANDS` list updated with all 14 commands
- [x] `replicate_setup.sh` updated with matching command set
- [x] `agentic-mbse init` installs all 14 commands to `.claude/commands/`
- [x] `agentic-mbse init --dev` creates symlinks for all 14 commands
- [x] All existing tests pass — 342 passed, 1 skipped

---

### D3.4: Agent Cleanup

**Type**: Evaluation + Implementation
**Status**: Pending
**Dependencies**: None (can proceed in parallel with D3.1)
**Delta checklist**: § 3A.4 (3 items)

**Objective**: Resolve the `sysmlv2-doc-analyzer` deprecation status and standardize doc path references across all agents.

#### `sysmlv2-doc-analyzer` — EVALUATE

**Current state**: In `claude/agents/deprecated/sysmlv2-doc-analyzer.md`. The architecture (components.md § 3) lists it as an active agent used for "broad SysML questions, pattern recommendations."

**Evaluation questions**:
1. **Is it still useful?** The agent provides cross-cutting SysML v2 specification lookups. Other agents (`sysml-expert`, `kerml-expert`) cover specific aspects but not broad pattern recommendations across the full spec.
2. **Why was it deprecated?** Check git history for deprecation rationale. If it was deprecated due to a temporary issue (e.g., doc path problems), restoring may be appropriate.
3. **Does it duplicate other agents?** Compare its scope with `sysml-expert` and `kerml-expert`. If it's purely additive (broader scope), restore. If it overlaps significantly, confirm deprecation.

**Proposed disposition**: Decide restore or confirm deprecation. If restored, move from `deprecated/` to `agents/` and update `MBSE_AGENTS` in `cli/__init__.py`.

#### Doc path standardization

**Current state**: Agent files use `{SYSML_DOCS_PATH}` and `{SYSIDE_DOCS_PATH}` placeholders that are substituted during `cmd_init()`.

**Changes**:
1. Verify all agent files use consistent placeholder syntax
2. Verify `cmd_init()` substitution logic handles all agents correctly
3. If `sysmlv2-doc-analyzer` is restored, ensure its placeholders match the pattern

**Exit criteria**:
- [ ] `sysmlv2-doc-analyzer` disposition decided with documented rationale
- [ ] If restored: agent moved to `agents/`, added to `MBSE_AGENTS`, placeholders verified
- [ ] If confirmed deprecated: agent removed from architecture description (components.md reference is informational)
- [ ] All agent files use consistent `{SYSML_DOCS_PATH}` and `{SYSIDE_DOCS_PATH}` placeholders
- [ ] `MBSE_AGENTS` list in `cli/__init__.py` reflects final agent set

---

### D3.5: Validation Walkthrough (Quality Gate)

**Type**: Verification (not code changes)
**Status**: Pending
**Dependencies**: D3.1 (refactored commands), D3.2 (new commands), D2.5 (extraction mapping from Epic 2)
**Delta checklist**: § 3A.5 (6 walkthrough items + 1 added cross-command pipeline test)

**Objective**: Walk each refactored command through a real fusion-tea workflow to verify no implicit knowledge was lost during the skill extraction and command refactoring.

**Why this is mandatory**: The primary risk of skill extraction is losing nuanced guidance that was embedded in long command prompts. A command may reference the correct skills but miss context-specific guidance that emerged from the original prompt's structure. The walkthrough catches this before shipping.

**Walkthrough protocol**:

For each command:
1. **Select a real fusion-tea work item** that exercises the command's core workflow
2. **Run the refactored command** against the work item
3. **Cross-reference against D2.5 extraction mapping**: Is every line range accounted for? Does the skill reference + command workflow cover what the original monolithic command covered?
4. **Check for quality regression**: Does the agent produce guidance of comparable quality? Are SysML patterns correct? Are validation steps complete?
5. **Document findings**: Record pass/fail and any knowledge gaps found

**Walkthrough items**:

| # | Command | Fusion-tea scenario | What to verify |
|---|---------|-------------------|----------------|
| 1 | `/spec-model` | Spec a new work item (e.g., new subsystem model) | G-XXX reading, DI-XXX insight access, YAML frontmatter generation, MR-XXX requirements |
| 2 | `/design-model` | Design against an existing spec | Skill references provide equivalent SysML guidance, ARCHITECTURE.md reading, REQUIREMENTS.md compliance |
| 3 | `/implement-model` | Implement a phase of an existing plan | Inline knowledge capture, traceability recording, validation at each phase, backward navigation handling |
| 4 | `/audit-models` | Audit existing fusion-tea models | Decision promotion flow, SV-XXX updates, requirements compliance checking |
| 5 | `/research` | Research a domain question from SOURCE_INDEX.md | Approval workflow, DI-XXX capture, file save to pending/ |
| 6 | Q12 verification | Cross-reference all 9 refactored commands against D2.5 extraction mapping | Every extracted line range is accounted for — either moved to a skill or retained in the command. No implicit knowledge lost. |
| 7 | Cross-command | Full pipeline: spec → design → plan → implement → audit on a single work item | End-to-end data flow between stages, YAML frontmatter consistency, no broken references |

**Handling findings**: If knowledge gaps are found:
- Minor gap (missing nuance): Add the missing content to the relevant skill or back to the command
- Major gap (entire workflow step lost): Investigate D2.5 mapping for the omission, fix the command
- Skill boundary issue (knowledge falls between skills): Add to the most relevant skill, document the decision

**Exit criteria**:
- [ ] All 7 walkthrough items completed (5 command walkthroughs + Q12 cross-reference + cross-command pipeline)
- [ ] No major knowledge gaps found (or all found gaps are fixed)
- [ ] Q12 resolved: every extracted line range accounted for, validation method confirmed as effective
- [ ] Walkthrough results documented

---

## Sequencing

```
D3.4 (agent cleanup) ──────────────────────────────────────────┐
                                                                │
D3.1 (refactor commands, sequential by priority):               │
  design-model ──► implement-model ──► spec-model ──►           │
  plan-model ──► audit-models ──► research ──►                  │
  onboard ──► backlog ──► manage-sources ──────────────────────┤
                                                                │
D3.2 (new commands, after ~3 refactored commands establish      │
      convention):                                              │
  quick-model, review-model, analyze-models, ──────────────────┤
  formalize-intent                                              │
                     (but NOT /status yet)                      │
                                                                ▼
                                                     D3.3 (registration)
                                                                │
                                                                ▼
                                                     D3.5 (validation walkthrough)
                                                                │
                                              D3.2 (/status — after Epic 4 dashboard)
```

- **D3.4** (agent cleanup) has no dependency on D3.1 and can proceed in parallel
- **D3.1** is sequential because each refactored command may reveal patterns that adjust subsequent commands. The first 2–3 commands (design-model, implement-model, spec-model) establish the structural convention.
- **D3.2** (new commands except `/status`) can begin once the convention is established (~3 refactored commands done)
- **D3.3** (registration) depends on all commands being written
- **D3.5** (walkthrough) depends on D3.1 and D3.2 being complete
- **D3.2 `/status`** is last — depends on Epic 4 PM dashboard

---

## Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Command refactoring loses implicit knowledge (Q12) | High | Medium | D2.5 extraction mapping provides cross-reference. D3.5 mandatory walkthrough catches gaps. Process: refactor one command, walkthrough immediately, adjust approach before continuing. |
| Skill references don't provide equivalent agent behavior | Medium | Medium | Skills are loaded into context alongside commands — the agent has the same knowledge, just organized differently. Walkthrough verifies this empirically. |
| Command structural convention is too rigid for diverse commands | Low | Medium | Convention is a guideline, not a template. Commands have different jobs (spec vs audit vs quick-model). Shared structure: frontmatter, skill references, context reading, workflow phases. Divergence is OK where justified. |
| `/status` blocked on Epic 4 PM dashboard | Medium | Medium | Write the command structure with all non-dashboard logic first. Add dashboard integration when Epic 4 delivers. `/status` is explicitly last in sequencing. |
| New commands need design iteration that delays the epic | Medium | Low | New commands are simpler than refactored ones (no legacy content to extract). `/quick-model` is the simplest (~150 lines). `/formalize-intent` is the most novel but well-specified in workflows.md. |
| `replicate_setup.sh` and `cmd_init()` diverge during command additions | Medium | Medium | Update both in the same commit (D3.3). Verify with `agentic-mbse init` on fresh directory and `--dev` mode. |

---

## What This Epic Does NOT Include

Explicitly out of scope (handled in other epics or deferred):

- **PM engine code** (parsers, state derivation, dashboard, operations) — Epic 4. This epic adds AP-7 script *calls* to commands, but the scripts themselves are Epic 4.
- **Skill content changes** — Epic 2. If the walkthrough (D3.5) reveals skill content gaps, the fix goes into the skill file, but this is a minor adjustment, not a re-scoping of Epic 2.
- **YAML frontmatter schema changes** — Epic 1. Schemas are settled. Commands generate frontmatter per the existing schemas.
- **fusion-tea migration** — Epic 1 (complete). fusion-tea's project structure is already migrated. This epic validates commands *against* fusion-tea but doesn't change fusion-tea's structure.
- **Git integration, hooks, cross-project sharing** — Deferred (Q16, Q17, Q18)

---

## Relationship to Epic 1

Epic 1 (Structure) established the target file structure that commands must reference:

- All refactored commands update path references from `modeling_pm/` to the 4-directory model (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- New commands (`/formalize-intent`) read from directories created in Epic 1 (`modeling_project/intent/`)
- YAML frontmatter generation in `spec-model` and `plan-model` follows the schemas defined in Epic 1 (D1.5, frontmatter-schemas.md)
- Command registration (D3.3) extends the same `MBSE_COMMANDS` and `replicate_setup.sh` mechanisms updated in D1.4

---

## Relationship to Epic 2

Epic 2 (Knowledge) is the direct input to this epic:

- Every refactored command replaces inline knowledge with references to skills created in Epic 2
- The extraction mapping (D2.5) is D3.1's primary input — it specifies exactly what to remove from each command
- The context window measurements (D2.4) confirmed skills load upfront — commands reference skills without staging concerns
- D3.5 walkthrough verifies no knowledge was lost by cross-referencing against D2.5

---

## Relationship to Epic 4

Epic 4 (PM Script Engine) runs in parallel with this epic:

- Several refactored commands add AP-7 script calls (`add-insight`, `trace-element`, `promote-requirement`, `approve-research`, `register-decision`, `update-validation`). These calls are correct even if the scripts aren't built yet — they document the intended integration point.
- `/status` is the convergence point: it's a command (Epic 3) that calls the PM dashboard script (Epic 4). It's sequenced last.
- If Epic 4 delivers operations before the corresponding command is refactored, the command can be validated against the real script immediately.

---

**Last Updated**: 2026-02-02
**Next Action**: D3.1, D3.2, D3.3 complete. Begin D3.4 (agent cleanup) and D3.5 (validation walkthrough).
