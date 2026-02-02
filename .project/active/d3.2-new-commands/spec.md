# Spec: D3.2 New Commands (5 commands)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02 07:41 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-003 (Architecture Redesign — Commands)

---

## Business Goals

### Why This Matters

The architecture redesign identified 5 missing commands required for the behavioral layer to be complete. Today, agentic-mbse forces all modeling work through the Standard spec→design→plan→implement pipeline (P3: rigid pipeline) and has no project-level visibility (P5: PM depends on agent memory). These 5 commands fill distinct gaps:

- **No trivial-change path** — a 1-line attribute fix requires `/spec-model` (P3)
- **No design review** — users jump from design to implementation with no structured review point
- **No model analysis** — understanding current model state requires ad-hoc exploration
- **No project dashboard** — project status lives in agent memory, not a deterministic view (P5)
- **No intent formalization** — raw project documents sit in `modeling_project/intent/` with no structured extraction path to G-XXX goals and AQ-XXX questions

### Success Criteria

- [ ] 5 new command files exist in `claude/commands/`
- [ ] Each follows the D3.1 structural convention (command-convention.md)
- [ ] Each is 100–150 lines (consistent with D3.1 average of 114 lines)
- [ ] Each has correct skill references matching components.md § 1
- [ ] `/quick-model` has a working scope guard rail
- [ ] `/review-model` produces review.md with YAML frontmatter (Verdict, Created, Related Artifacts)
- [ ] `/analyze-models` writes reports to `work/analysis/YYYYMMDD-HHMMSS_topic.md`
- [ ] `/status` calls PM dashboard script (or has documented placeholder for Epic 4)
- [ ] `/formalize-intent` handles both initial and incremental intent extraction
- [ ] All existing agentic-mbse tests pass (`uv run pytest tests/`)

### Priority

P0. Part of Epic 3 critical path. Depends on D3.1 (complete). Blocks D3.3 (registration) and D3.5 (validation walkthrough).

---

## Problem Statement

### Current State

9 commands exist (refactored in D3.1). 5 behavioral gaps remain per the architecture redesign analysis:

| Gap | Impact | Design Reference |
|-----|--------|-----------------|
| No trivial-change command | All work forced through full pipeline (P3) | workflows.md § 2.1 (scale taxonomy), components.md § 1 |
| No design review command | No structured quality gate between design and implementation | workflows.md § 3.3 (review.md artifact), components.md § 1 |
| No model analysis command | Model state understanding is ad-hoc | workflows.md § 5.2 (internal analysis), components.md § 1 |
| No project status command | PM state lives in agent memory (P5) | workflows.md § 4 (PM split), components.md § 1 |
| No intent formalization command | Raw intent docs not processed into G-XXX/AQ-XXX | information-architecture.md § 3 Role 3, components.md § 1 |

### Desired Outcome

5 new commands following the established D3.1 convention (~100-140 lines each), integrating with the information architecture, skill layer, and AP-7 script engine.

---

## Scope

### In Scope

1. Creating 5 new command files in `claude/commands/`
2. Following the D3.1 structural convention exactly (command-convention.md)
3. Declaring correct skill dependencies in YAML frontmatter
4. Adding AP-7 script invocations with exact CLI syntax where applicable
5. Referencing the 4-directory model paths throughout
6. Specifying YAML frontmatter schemas for artifacts produced (review.md)

### Out of Scope

- Command registration in `cmd_init()` and `replicate_setup.sh` (D3.3)
- Building AP-7 PM scripts (Epic 4) — commands include the *calls*
- Modifying existing refactored commands (D3.1 — complete)
- Modifying skill SKILL.md files
- Validation walkthroughs (D3.5)

### Edge Cases & Considerations

- **`/status` depends on Epic 4**: The PM dashboard script doesn't exist yet. The command must be structurally complete with a placeholder for the script call, becoming functional when Epic 4 delivers. Per the epic sequencing, `/status` should be the **last command written** in D3.2.
- **`/analyze-models` hybrid question (Q14)**: The epic resolves this as "implement as a command for now." If Epic 4 produces deterministic analysis capabilities, `/analyze-models` becomes a thin wrapper later.
- **`/formalize-intent` incremental updates**: Must handle both initial extraction (during `/onboard`) and incremental updates (new docs added later). The command reads OVERVIEW.md to see what's already formalized and proposes only new entries.

---

## Requirements

### Structural Convention (All 5 Commands)

All requirements below apply to every command unless a specific command is named.

> FR-1: Each new command MUST follow the D3.1 structural convention documented in `.project/active/d3.1-command-refactoring/command-convention.md`.

Required sections in order:
1. YAML frontmatter (`name`, `description`, `skills`, `allowed-tools`, `user-invocable`)
2. Title + Purpose/Input/Output
3. Skills Referenced (prose — what each skill provides, when to consult it)
4. Process (lightweight numbered steps: Understand → Core Work → Validate → Approve/Complete)
5. What Good Output Looks Like (when command produces a structured artifact)
6. Sub-Agent Usage (when command uses multiple agents)
7. Guidelines (critical rules and error handling)
8. Related Commands (single line, workflow context)

> FR-2: Each command MUST be 100–150 lines, consistent with the D3.1 average of 114.

Ref: command-convention.md — "Target: 100-140 lines. No command should exceed 200 lines."

> FR-3: Each command MUST declare skill dependencies in YAML frontmatter matching components.md § 1.

> FR-4: Each command MUST use 4-directory model paths (`knowledge/`, `modeling_project/`, `work/`, `data/`, `models/`).

> FR-5: AP-7 script invocations MUST be placed inline within Process steps at the point where the agent should call them, using fenced code blocks with exact CLI syntax.

Ref: command-convention.md — "AP-7 Script Invocations" section.

### `/quick-model` — Trivial-Scale Direct Changes

**Design references:**
- workflows.md § 2.1 (scale taxonomy: Trivial = "single attribute, doc comment, value change")
- workflows.md § 2.2 (routing decision tree: Trivial → `/quick-model`)
- components.md § 1 (Job: "Make a SMALL change", Key decision: "Change scope — is this truly trivial?")
- epic § D3.2 `/quick-model` (workflow, guard rail, target length ~150 lines)

> FR-6: `/quick-model` MUST include a scope assessment step that evaluates whether the change is truly trivial before proceeding.

The scope assessment is the command's key user decision point. Criteria for "trivial" (from workflows.md § 2.1):
- Single attribute, doc comment, or value change
- Does NOT touch multiple files
- Does NOT introduce new patterns
- Does NOT require design decisions

> FR-7: If the scope assessment determines the change exceeds trivial scale, the command MUST redirect to `/spec-model` with a scope explanation.

Ref: workflows.md § 2.2 — "System assesses from scope... 'This looks like a [scale] change. Agree?'"
Ref: epic — "Guard rail: The command must include a scope assessment step that honestly evaluates whether the change is trivial. If the change touches multiple files, introduces new patterns, or requires design decisions, the agent redirects to /spec-model."

> FR-8: `/quick-model` MUST NOT create a work item directory. PM does not track trivial changes.

Ref: workflows.md § 2.1 — "No work item directory. PM doesn't track."

> FR-9: `/quick-model` MUST run validation after making the change.

Ref: epic — "make change directly + run validation"

> FR-10: `/quick-model` skills MUST be `[sysml-conventions, model-validation]`.

Ref: components.md § 1, epic § D3.2.

### `/review-model` — Design Review Before Implementation

**Design references:**
- workflows.md § 3.3 (review.md artifact: "optional artifact produced by /review-model between design and implementation")
- components.md § 1 (Job: "REVIEW design before implementing", Key decision: "Which findings to accept/skip/defer")
- epic § D3.2 `/review-model` (workflow, design note about PM non-tracking)
- information-architecture.md § 3 Role 4 (REQUIREMENTS.md as compliance target)
- information-architecture.md § 3 Role 5 (ARCHITECTURE.md as adherence target)

> FR-11: `/review-model` MUST read design.md + spec.md from the work item directory.

> FR-12: `/review-model` MUST check the design against:
> - `modeling_project/REQUIREMENTS.md` (PR-XXX compliance)
> - `modeling_project/ARCHITECTURE.md` (AD-XXX adherence)
> - SysML conventions (via **sysml-conventions** skill)
> - Model validation standards (via **model-validation** skill)

Ref: epic — "Read design.md + spec.md → check against REQUIREMENTS.md and ARCHITECTURE.md → check SysML conventions → produce review.md"

> FR-13: `/review-model` MUST produce `review.md` in the work item directory with YAML frontmatter:

```yaml
---
Verdict: pass | concerns | fail
Created: <YYYY-MM-DD>
Related Artifacts:
  Design: ./design.md
---
```

Ref: workflows.md § 3.3, epic exit criteria, frontmatter-schemas.md (DD-3: "review.md is advisory, not a PM-tracked stage").

> FR-14: `/review-model` MUST present findings to the user for curation: accept, skip, or defer each finding.

Ref: components.md § 1 — "Key user decision: Which findings to accept/skip/defer"

> FR-15: review.md is NOT a PM-tracked stage. The PM engine does not look for review.md. The review is advisory.

Ref: workflows.md § 3.3 — "review.md is NOT a PM-tracked stage... The review is advisory — the user can proceed to /plan-model without it (AP-5: toolkit, not pipeline)."
Ref: epic design note — "review.md is NOT a PM-tracked stage (DD-3 from frontmatter-schemas.md)."

> FR-16: `/review-model` skills MUST be `[sysml-conventions, model-validation, project-structure, requirements-tracking]`.

Ref: components.md § 1, epic § D3.2.

### `/analyze-models` — Model Analysis Reports

**Design references:**
- workflows.md § 5.2 (internal analysis: parse model structure, check rules, compute health)
- components.md § 1 (Job: "UNDERSTAND current model state", Key decision: "Analysis scope")
- epic § D3.2 `/analyze-models` (workflow, Q14 resolution: implement as command)

> FR-17: `/analyze-models` MUST parse model structure: files, definitions, usages, cross-file dependencies.

Ref: workflows.md § 5.2, epic — "Parse model structure (files, definitions, usages, cross-file deps)"

> FR-18: `/analyze-models` MUST check compliance against `modeling_project/REQUIREMENTS.md` (PR-XXX rules).

Ref: workflows.md § 5.2 — "Check rules compliance: which Role 4 rules are followed/violated"
Ref: epic — "check REQUIREMENTS.md compliance"

> FR-19: `/analyze-models` MUST compute health indicators: validation levels, test coverage, debt markers.

Ref: workflows.md § 5.2, epic — "compute health indicators (validation levels, test coverage, debt markers)"

> FR-20: `/analyze-models` MUST write reports to `work/analysis/YYYYMMDD-HHMMSS_topic.md`.

Ref: information-architecture.md § 2 (file structure: `work/analysis/`), epic — "write report to work/analysis/YYYYMMDD-HHMMSS_topic.md"

> FR-21: `/analyze-models` MUST accept a user-specified analysis scope (which models, which aspects).

Ref: components.md § 1 — "Key user decision: Analysis scope (which models, which aspects)"

> FR-22: `/analyze-models` skills MUST be `[project-structure, model-validation]`.

Ref: components.md § 1, epic § D3.2.

### `/status` — Project State Dashboard

**Design references:**
- workflows.md § 4.1 (the PM split: scripts for state queries, agent commands for interpretation)
- workflows.md § 4.2–4.4 (PM data model, output format, visual representation)
- workflows.md § 3.5 (work item close flow — `/status close <item>`)
- components.md § 1 (Job: "Understand PROJECT STATE", Key decision: "What to do next")
- epic § D3.2 `/status` (workflow, dependency on Epic 4)

> FR-23: `/status` MUST call `agentic-mbse status` script to get deterministic dashboard output.

Ref: workflows.md § 4.1 — "State queries are deterministic (Python scripts). State changes are agent-guided (commands). Intelligence layers on top."
Ref: epic — "Call agentic-mbse status script (Epic 4 PM dashboard)"

> FR-24: `/status` MUST add intelligent interpretation on top of the script output: what's blocked, what's ready, what needs attention.

Ref: workflows.md § 4.1 — agent command adds "Interpretation, Recommendations, Gap analysis"
Ref: epic — "add interpretation (what's blocked, what's ready, what needs attention) → offer recommendations"

> FR-25: `/status` MUST support three modes:
> - **default**: dashboard + interpretation + recommendations
> - **decompose `<epic>`**: break an epic into work items (invokes `epic-decomposition` skill)
> - **close `<item>`**: verify + archive via close flow

Ref: workflows.md § 4.1 — "Modes: default, decompose <epic>, close [item]"
Ref: epic — "optional modes: decompose <epic>, close <item>"

> FR-26: The `close` mode MUST implement the two-part close flow from workflows.md § 3.5:
> 1. Call `agentic-mbse pm close-item <name>` (AP-7 T1: archive + BACKLOG.md update)
> 2. Agent prompts trigger questions for project document review:
>    - REQUIREMENTS.md: "Did you discover a modeling pattern that should be a project-wide rule?"
>    - ARCHITECTURE.md: "Did you make a structural decision that future work items need to know about?"
>    - VALIDATION_MATRIX.md: "Should any new system-level verification criteria be added?"
>    - KNOWLEDGE.md: "Did you learn something about the domain that isn't captured yet?"
> 3. For each "yes": agent helps draft update, calls appropriate AP-7 script

Ref: workflows.md § 3.5 (full close flow with trigger questions), main.md AP-7 operations table (close-item: T1).

> FR-27: If Epic 4 PM dashboard script is not yet built, `/status` MUST include a documented placeholder for the script call with a note that it becomes functional when Epic 4 delivers.

Ref: epic — "If Epic 4 is incomplete, write the command structure with a placeholder for the script call."

> FR-28: `/status` skills MUST be `[epic-decomposition, requirements-tracking]`.

Ref: components.md § 1, epic § D3.2.

### `/formalize-intent` — Extract Goals and Questions from Intent Documents

**Design references:**
- information-architecture.md § 3 Role 3 (intent formalization flow: raw docs → G-XXX, AQ-XXX)
- workflows.md § 2.2 (routing: formalization can be triggered during `/onboard` or standalone)
- components.md § 1 (Job: "EXTRACT goals and questions from intent docs", Key decision: "Which G-XXX/AQ-XXX to accept, modify, or skip")
- epic § D3.2 `/formalize-intent` (workflow, target length ~200 lines)
- main.md § 5 Q5a resolution ("Dedicated /formalize-intent command (AP-7 T2)")

> FR-29: `/formalize-intent` MUST read documents from `modeling_project/intent/` directory.

Ref: information-architecture.md § 3 Role 3 — "User uploads/writes documents in modeling_project/intent/"

> FR-30: `/formalize-intent` MUST extract candidate G-XXX goals and AQ-XXX analysis questions from the intent documents.

Ref: information-architecture.md § 3 Role 3 — "an agent-driven process reads the documents, proposes structured G-XXX goals and AQ-XXX analysis questions"

> FR-31: `/formalize-intent` MUST present each extracted G-XXX/AQ-XXX to the user for approval, modification, or skip (AP-6 curation gate).

Ref: components.md § 1 — "Key user decision: Which G-XXX/AQ-XXX to accept, modify, or skip"
Ref: main.md AP-6 — "Explicit curation — information passes from raw sources to actionable knowledge through user-approved gates, not automatically"

> FR-32: `/formalize-intent` MUST call an AP-7 script to register approved entries in `modeling_project/OVERVIEW.md`.

Ref: information-architecture.md § 3 Role 3 — "A script registers approved entries in OVERVIEW.md (correct IDs, format, source traceability)"
Ref: main.md Q5a — "AP-7 T2"

> FR-33: `/formalize-intent` MUST handle incremental updates — when new intent documents are added after initial setup, it reads OVERVIEW.md to see what's already formalized and proposes only new entries.

Ref: information-architecture.md § 3 Role 3 — "Incremental updates (new docs added after initial setup) use the same command — the agent reads OVERVIEW.md to see what's already formalized and proposes only new entries."

> FR-34: `/formalize-intent` MUST suggest follow-up actions after extraction: `/research` for AQ-XXX questions, `/spec-model` for actionable goals.

Ref: epic — "suggest follow-up actions (research for AQ-XXX questions, /spec-model for actionable goals)"

> FR-35: `/formalize-intent` skills MUST be `[project-structure]`.

Ref: components.md § 1, epic § D3.2.

### Processing Order

> FR-36: Commands SHOULD be written in this order: `quick-model` → `review-model` → `analyze-models` → `formalize-intent` → `status`.

Rationale: `/quick-model` is the simplest (~150 lines in the epic estimate, likely ~100-120 with the established convention). `/status` is last because it depends on Epic 4 PM dashboard. The middle three can proceed in any order but the listed order moves from simpler to more complex.

Ref: epic sequencing — "/status is last — depends on Epic 4 PM dashboard"

---

## Acceptance Criteria

### Core Functionality

- [ ] 5 new command files exist in `claude/commands/`
- [ ] Each follows D3.1 structural convention (command-convention.md)
- [ ] Each is 100–150 lines
- [ ] YAML frontmatter has correct `name`, `description`, `skills`, `allowed-tools`, `user-invocable` fields
- [ ] Skills Referenced prose section present in all 5 commands
- [ ] `/quick-model` scope guard rail redirects non-trivial work to `/spec-model`
- [ ] `/quick-model` runs validation after change
- [ ] `/review-model` produces review.md with Verdict/Created/Related Artifacts frontmatter
- [ ] `/review-model` checks against REQUIREMENTS.md, ARCHITECTURE.md, and skills
- [ ] `/analyze-models` writes to `work/analysis/YYYYMMDD-HHMMSS_topic.md`
- [ ] `/analyze-models` covers structure, compliance, and health indicators
- [ ] `/status` calls PM dashboard script (or documented placeholder)
- [ ] `/status` supports default, decompose, and close modes
- [ ] `/status close` implements the two-part close flow with trigger questions
- [ ] `/formalize-intent` reads from `modeling_project/intent/`, extracts G-XXX/AQ-XXX
- [ ] `/formalize-intent` handles incremental updates (reads existing OVERVIEW.md)
- [ ] `/formalize-intent` calls AP-7 script to register entries

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] All paths use 4-directory model (zero `modeling_pm/` references)
- [ ] AP-7 invocations use fenced code blocks with exact CLI syntax
- [ ] Commands are readable as Claude Code slash commands (valid frontmatter)

---

## Related Artifacts

- **D3.1 Convention**: `.project/active/d3.1-command-refactoring/command-convention.md` (structural pattern to follow)
- **D3.1 Spec**: `.project/active/d3.1-command-refactoring/spec.md` (prior art — how refactored commands were specified)
- **Architecture — Components**: `.project/concepts/architecture-redesign/components.md` § 1 (command catalog with jobs, skills, decisions)
- **Architecture — Workflows**: `.project/concepts/architecture-redesign/workflows.md` (scale taxonomy § 2, work item lifecycle § 3, PM split § 4, research split § 5)
- **Architecture — Information**: `.project/concepts/architecture-redesign/information-architecture.md` (Role 3 intent formalization, file structure § 2)
- **Architecture — Main**: `.project/concepts/architecture-redesign/main.md` (principles AP-1 through AP-7, Q5a resolution)
- **Architecture — Backlog**: `.project/concepts/architecture-redesign/backlog.md` (B-001 close flow, B-006 decision promotion, B-007 review/audit boundary)
- **Frontmatter Schemas**: `.project/concepts/architecture-redesign/frontmatter-schemas.md` (review.md schema DD-3)
- **Epic**: `.project/backlog/epic_architecture-commands.md` (D3.2)
- **Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` § 3A.2

---

**Next Steps:** After approval, proceed to `/_my_design`
