# Workflows

**Parent**: [main.md](main.md) — Problem, principles, implementation plan
**Concern**: How things move through the system — skills, work items, PM, research

This document defines the behavioral layer: how knowledge is delivered to commands (skills), how work items are classified and routed (scale taxonomy), how project state is tracked (PM engine), and how research and analysis work.

---

## 1. Knowledge Layer (Skills)

### 1.1 Design Pattern: Skill Extraction

**Pattern**: Extract knowledge that is (a) referenced by 2+ commands and (b) would otherwise be duplicated or inconsistent into a named skill with a `SKILL.md` entry point.

**What a skill contains**:
- `SKILL.md`: Overview, when to reference, key principles (loaded into context)
- Optional `references/*.md`: Detailed reference material (loaded on demand)

**What a skill does NOT contain**:
- Workflow logic (that's in commands)
- Project-specific data (that's in the information architecture → [information-architecture.md](information-architecture.md))
- Agent prompts (that's in agent definitions)

### 1.2 Skill Catalog

| Skill | What it contains | Referenced by | Justification |
|-------|-----------------|---------------|---------------|
| **sysml-conventions** | Syntax rules, naming, patterns, pitfalls, code stencils | design-model, implement-model, audit-models, quick-model | Currently duplicated across design-model (600+ lines) and partially in others |
| **model-validation** | Quality pyramid (8 levels), CLI commands, pass/fail criteria, regression patterns | design-model, implement-model, audit-models, plan-model | Currently embedded in design-model and implement-model separately |
| **project-structure** | Library vs designs, file organization, cross-file patterns, EXPOSE pattern | design-model, implement-model, spec-model, onboard | Currently scattered; inconsistent between commands |
| **source-traceability** | SOURCE_INDEX format, citation patterns, doc comment requirements | design-model, spec-model, audit-models, research | Currently partially in design-model, partially in manage-sources |
| **epic-decomposition** | Goldilocks principle (adapted for modeling), work item taxonomy, decomposition process, anti-patterns | backlog, status, onboard | Currently missing entirely (identified as CRITICAL gap) |
| **requirements-tracking** | REQUIREMENTS.md format (project-wide PR-XXX rules), promotion path from per-feature patterns, enforcement methods, compliance checking | design-model, audit-models, review-model, status | Currently missing; project-level rules scattered in research docs |
| **toolkit-awareness** | CLI commands, validation tools, environment | all commands | Already exists; needs updates for new PM commands |

### 1.3 Skill Loading Strategy

**Decision needed**: How many skills can be loaded concurrently without context window pressure?

**Proposed approach** (needs measurement):
- Commands declare their skill dependencies in a header comment
- At command start, load the skills needed for the current stage only
- Skills are designed to be concise (<200 lines for SKILL.md) with optional deep references

**Constraint**: If measurement shows context pressure, skills may need to be more granular (principles only in SKILL.md, examples only on demand). This is an iteration target — the skill boundaries can shift without changing the architecture.

---

## 2. Work Item Model

### 2.1 Scale Taxonomy

Work items are classified by **scale** — how much process overhead is appropriate. This is the single routing dimension (AP-3: the intent dimension was deleted because Fix/Refactor/Integrate do not change downstream behavior in any architectural sense — they are prompt-level variations within `/spec-model`, not distinct control flows).

| Scale | Behavior | Entry point | Architectural difference |
|-------|----------|-------------|------------------------|
| **Trivial** | No spec/design/plan. Direct change + validate. | `/quick-model` | Different command. No work item directory. PM doesn't track. |
| **Standard** | Full pipeline: spec → design → plan → implement → audit. Agent adjusts depth naturally based on the nature of the change. | `/spec-model` | Default pipeline. Work item in `work/active/`. |
| **Epic** | Must decompose into sub-items before entering pipeline. Each sub-item is a Standard work item. | `/backlog decompose` → sub-items | Different control flow. Parent-child tracking in PM. |

**Why three scales, not four**: The earlier "Small" scale (abbreviated spec, no separate design doc) was absorbed into Standard. The agent naturally adjusts depth — a straightforward fix gets a lighter spec and may skip design, while a complex feature gets the full treatment. Formalizing this as a separate scale adds taxonomy overhead without changing any data model or control flow.

**What happened to intent types** (Fix, Refactor, Integrate): These are prompt-level concerns, not architecture. When `/spec-model` starts, it can internally ask "what kind of change is this?" and adjust its questions accordingly — a fix gets "what's wrong / what does fixed look like," a refactor gets "what must be preserved," an integration gets "what interfaces must hold." But this is a command design decision (Phase 3D), not an information architecture or control flow concern. The user can also skip stages manually (AP-5: toolkit, not pipeline).

**Investigation is not a work item type**: The original "Investigate" intent covered two distinct activities that are already separate commands: `/research` (builds domain knowledge, Role 2) and `/analyze-models` (builds model understanding, operational intelligence in `work/analysis/`). Neither produces work items — they produce knowledge artifacts and analysis reports, respectively.

### 2.2 Control Flow: Work Item Routing

When work begins, the system determines scale. This is the **routing decision tree**:

```
User describes what they want to do
        │
        v
┌─────────────────────────────────┐
│ DETERMINE SCALE                 │
│                                 │
│ System assesses from scope:     │
│                                 │
│ Trivial: single attribute,      │
│   doc comment, value change     │
│ Standard: feature work, fixes,  │
│   refactors, integrations       │
│ Epic: multiple concerns, needs  │
│   decomposition into sub-items  │
│                                 │
│ "This looks like a [scale]      │
│  change. Agree?"                │
└───────────────┬─────────────────┘
                │
                v
┌─────────────────────────────────┐
│ ROUTE TO ENTRY POINT            │
│                                 │
│ Trivial  → /quick-model         │
│ Standard → /spec-model           │
│ Epic     → /backlog decompose    │
└─────────────────────────────────┘
```

**UX principle**: The system infers and confirms. The user never fills out a form. For power users, scale can be stated directly: `/quick-model "fix missing redefines in cost_model"`.

### 2.3 Backward Navigation

When implementation reveals a design flaw, the system supports going back:

```
Implementing phase 2 of 3
        │
        │ "The approach from the design doesn't work because..."
        v
┌─────────────────────────────────┐
│ BACKWARD NAVIGATION TRIGGER     │
│                                 │
│ Agent detects or user declares  │
│ that current design is flawed   │
│                                 │
│ Options presented:              │
│ 1. Update design.md, re-validate│
│    prototype, adjust plan,      │
│    resume implementation        │
│ 2. Continue with workaround     │
│    (document deviation)         │
│ 3. Pause this item, work on     │
│    something else               │
└─────────────────────────────────┘
```

**Concrete process for option 1**:
1. Open design.md, identify the flawed section
2. Revise the design with the new understanding
3. Re-run validation on the prototype (Levels 1-3)
4. Update plan.md (adjust remaining phases)
5. Resume implementation from the current phase

**Further design needed**: Exact mechanism for tracking "went back" state. Options include git-based checkpointing (deferred) or explicit state markers in plan.md.

---

## 3. Work Item Lifecycle

This section defines the entity models, state machines, artifact conventions, and lifecycle flows for work items and epics. It consolidates what was previously scattered across the scale taxonomy (§ 2), PM engine (§ 4), and main.md.

### 3.1 Work Item Entity Model

Every Standard work item has a directory in `work/active/{item}/`. The first artifact created is **spec.md**, which carries the authoritative metadata for the work item.

**spec.md YAML frontmatter** (required, parseable by PM script engine):

```yaml
---
Status: active | paused | abandoned | failed | completed
Scale: standard
Epic: [epic name, matching BACKLOG.md section header]
Owner: [who is working on this]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

**spec.md is the state-bearing file**. It is the first artifact created and the last one relevant. The PM script engine reads `work/active/{item}/spec.md` frontmatter as the single source of truth for work item state. Other files (design.md, plan.md) may have their own Status fields for stage-level tracking, but the work item's overall state comes from spec.md. This gives the dashboard a single read point per work item.

**All stage artifacts** (spec.md, design.md, plan.md) share a common header pattern:

```yaml
---
Status: [stage-specific status]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Related Artifacts:
  Spec: ./spec.md          # (in design.md and plan.md)
  Design: ./design.md      # (in plan.md)
---
```

The body structure of each artifact is defined by command prompts (Phase 3C concern). The architecture only constrains the parseable frontmatter header.

### 3.2 Work Item States

| State | Determined by | Mechanism |
|-------|--------------|-----------|
| **backlog** | Entry in `work/BACKLOG.md`, no directory in `work/active/` | BACKLOG.md row |
| **active** | Directory exists in `work/active/{item}/`, spec.md Status = `active` | File system + frontmatter |
| **active:stage** | Which artifact files exist: spec.md only = speccing; +design.md = designing; +plan.md = planning; implementation started = implementing | File system |
| **paused** | spec.md Status = `paused` | Frontmatter field |
| **abandoned** | spec.md Status = `abandoned` | Frontmatter field |
| **failed** | spec.md Status = `failed` (work attempted, approach didn't work) | Frontmatter field |
| **completed** | Directory in `work/completed/YYYYMMDD_{item}/` | File system (post-archive) |

**State derivation logic**: The PM script engine uses a two-step read:
1. Check file system: does `work/active/{item}/` exist? → active. Does `work/completed/YYYYMMDD_{item}/` exist? → completed. Neither? → backlog (if in BACKLOG.md).
2. For active items: read spec.md frontmatter Status field. If `paused`, `abandoned`, or `failed`, that overrides the active state. If `active`, determine sub-stage from which artifact files exist.

### 3.3 Stage Artifacts and Inter-Stage Contract

**Stage completion**: User-approved only. No structural gates. AP-5 (toolkit, not pipeline) says don't add friction. The agent guides quality through command prompts; the user decides when to proceed.

**Inter-stage data flow** (documentation of what commands already do — conventions, not enforcement):

| Stage file | Produces (for downstream) | Consumes (from upstream) |
|-----------|--------------------------|-------------------------|
| spec.md | MR-XXX requirements, success criteria, scope boundaries | G-XXX goals, DI-XXX insights, existing model state |
| design.md | Architecture approach, interface decisions, prototype validation results | MR-XXX from spec.md, AD-XXX from ARCHITECTURE.md, PR-XXX from REQUIREMENTS.md |
| review.md | User-curated design review findings (accepted changes, deferred items) | design.md, prototype, REQUIREMENTS.md, ARCHITECTURE.md |
| plan.md | Phased implementation plan, per-phase scope, risk mitigations | Design decisions from design.md, model dependency analysis |

**review.md** is an optional artifact produced by `/review-model` between design and implementation. It contains a verdict (pass/concerns/fail in YAML frontmatter) and user-curated findings. If changes are accepted, `/design-model` reads review.md and applies them. The review is advisory — the user can proceed without it (AP-5: toolkit, not pipeline).

This table is a reference for skills and commands. Skills can use it to know what context to load at each stage. Commands can be validated against it during Phase 3C. The PM script engine uses the frontmatter headers, not the body content.

### 3.4 Resumability

When a paused work item resumes:

- **Resume = re-read the existing artifact files for the current stage + the plan.** The artifacts contain the full history of decisions made so far.
- The `/status` dashboard shows paused items with their current stage.
- The user picks one, and the relevant command (`/design-model`, `/implement-model`, etc.) reads the existing artifacts to reconstruct context.
- No separate "resume" command is needed — existing commands handle "artifact already exists, continue from where we left off."
- spec.md Status field is updated from `paused` back to `active` (by the PM script or manually).

### 3.5 Work Item Close Flow

When a work item is complete, the close flow has two parts: a deterministic script operation and an agent-driven feedback prompt.

```
/status close <item>
  │
  ├─► Script (AP-7 T1): Close work item
  │     1. Move work/active/{item}/ → work/completed/YYYYMMDD_{item}/
  │     2. Update BACKLOG.md status to completed
  │     3. Return confirmation with archive path
  │
  └─► Agent: Project document review prompt
        "This work item is archived. Before we're done,
         let's check if any project-level documents should be updated."

        Trigger questions (concrete, answerable from recent experience):

        - REQUIREMENTS.md: "Did you discover a modeling pattern that
          should be a project-wide rule?"
        - ARCHITECTURE.md: "Did you make a structural decision that
          future work items need to know about?"
        - VALIDATION_MATRIX.md: "Should any new system-level
          verification criteria be added?"
        - KNOWLEDGE.md: "Did you learn something about the domain
          that isn't captured yet?"

        For each "yes": agent helps draft the update,
        calls the appropriate AP-7 script
        (register-requirement, update-validation, add-insight, etc.).
```

**Why trigger questions matter**: They translate the abstract ("does ARCHITECTURE.md need updating?") into something the user can answer from their recent experience. Without them, the feedback prompt becomes a checklist the user clicks through without thinking.

**Project-level revisions**: When a work item reveals a project-level issue (flawed architecture decision, infeasible goal), the close flow's trigger questions are the structured opportunity to surface it. For discoveries made mid-work-item, the backward navigation flow (§ 2.3) handles the per-item response; project-level impact is surfaced at close time.

**Non-linear development**: Already covered by existing mechanisms:
- Quick fix escalation: `/quick-model` user recognizes complexity → creates standard work item via `/backlog add`
- Cross-item refactoring: New standard work item that references originals; archived artifacts in `work/completed/` remain readable
- Undo: Create a new work item that references and corrects the original; don't reopen
- Concurrent items: Git handles file-level conflicts; not an architectural concern at fusion-tea's scale (~3-5 concurrent items)

### 3.6 Epic Tracking

**Two artifacts, two jobs**:

| Artifact | Location | Job |
|----------|----------|-----|
| BACKLOG.md | `work/BACKLOG.md` | **Tracking** — summary of all epics and standalone items, priority ordering, status at a glance |
| Epic file | `work/backlog/epic-{name}.md` | **Decomposition** — the working document where scope, sequencing, per-item requirements, risks, and dependencies are worked out |

Epics need dedicated files because the decomposition work is substantial. A real epic file (see fusion-tea's `epic-end-to-end-pipeline-derisking.md`, ~650 lines) contains: executive summary, context/prior art, system design, pipeline architecture, success criteria, risks, and detailed per-item breakdowns with scope, deliverables, and dependencies. Trying to fit that into a BACKLOG.md section would make BACKLOG.md unreadable.

**The workflow**:

```
User starts with research or spec → realizes scope is too big
        │
        v
Write epic file in work/backlog/epic-{name}.md
  - Iterate on decomposition, sequencing, dependencies
  - Each item gets high-level requirements and success criteria
        │
        v
Add summary entry to work/BACKLOG.md (name, priority, status, item list)
        │
        v
Move to item-by-item execution
  - /spec-model reads the epic file for baseline requirements
  - Each spec.md starts with a solid foundation, not a blank page
  - BACKLOG.md tracks progress across all items
```

**BACKLOG.md format** — YAML frontmatter for machine state, markdown body for human view:

The PM script engine reads **only the YAML frontmatter**. The markdown body is a rendered dashboard maintained by the agent for human readability. If the body drifts from the frontmatter, the frontmatter wins — it is the source of truth. AP-7 scripts that update BACKLOG.md update the frontmatter; the agent re-renders the body.

```markdown
---
epics:
  - name: "End-to-End Pipeline De-Risking"
    goal: G-001
    priority: P0
    status: active
    file: backlog/epic-end-to-end-pipeline-derisking.md
    items:
      - name: "Solar+Battery SysML Model"
        scale: standard
        status: completed
        completed: 2026-02-05
      - name: "Codegen Chain Spike"
        scale: standard
        status: active
        work_dir: active/codegen-chain-spike
      - name: "Cost Evaluation & Entry Points"
        scale: standard
        status: backlog

standalone:
  - name: "Fix cost_model redefines"
    scale: trivial
    priority: P1
    status: completed
    completed: 2026-01-28
  - name: "Add missing doc comments"
    scale: standard
    priority: P2
    status: backlog
---

# Project Backlog

## Epic: End-to-End Pipeline De-Risking
**Goal**: G-001 (LCOE traceability) | **Priority**: P0 | **Status**: active
**Epic file**: [epic-end-to-end-pipeline-derisking.md](backlog/epic-end-to-end-pipeline-derisking.md)

| Item | Scale | Status | Notes |
|------|-------|--------|-------|
| Solar+Battery SysML Model | standard | completed | 2026-02-05 |
| Codegen Chain Spike | standard | active | |
| Cost Evaluation & Entry Points | standard | backlog | |
...

## Standalone Items

| Item | Scale | Priority | Status | Notes |
|------|-------|----------|--------|-------|
| Fix cost_model redefines | trivial | P1 | completed | 2026-01-28 |
| Add missing doc comments | standard | P2 | backlog | |
```

BACKLOG.md is the single dashboard for both epics and standalone items. Epic files provide the depth; BACKLOG.md provides the breadth.

**Epic file structure** (user-owned, content varies by project):

```yaml
---
Status: draft | active | completed
Priority: P0 | P1 | P2 | P3
Goal: G-XXX
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

The body is free-form — the user structures it as needed for the decomposition. Common sections include: executive summary, context, system design, success criteria, risks, and per-item breakdowns. The `epic-decomposition` skill provides guidance on how to write effective decompositions; the architecture only constrains the frontmatter and file location.

**Epic state is derived**:
- **draft**: Epic file exists but items haven't entered the pipeline yet
- **active**: At least one sub-item is active
- **completed**: All sub-items are completed

No E-XXX ID scheme. No formal state machine beyond these three states. The epic file name (`epic-{name}.md`) is the identifier.

---

## 4. Project Management

### 4.1 The Split: Scripts vs. Agent

**Design pattern**: State queries are deterministic (Python scripts). State changes are agent-guided (commands). Intelligence layers on top.

```
┌──────────────────────────────────────────────────┐
│  CLI Layer: `agentic-mbse status`                │
│  (Python script — deterministic, testable)       │
│                                                  │
│  Reads: work/BACKLOG.md, project/REQUIREMENTS.md,│
│         work/active/, work/completed/,           │
│         project/VALIDATION_MATRIX.md,            │
│         models/, tests/                          │
│                                                  │
│  Produces: Markdown dashboard with:              │
│  - Epic progress (items done/total)              │
│  - Work item states (pending/active/paused/done) │
│  - Requirements coverage (tested/untested)       │
│  - Validation status (passing/failing/pending)   │
│                                                  │
│  Guarantees: Deterministic, no hallucination,    │
│              same input → same output            │
└──────────────────────┬───────────────────────────┘
                       │
                       │ script output fed to
                       v
┌──────────────────────────────────────────────────┐
│  Command Layer: `/status`                        │
│  (Agent command — intelligent, interactive)      │
│                                                  │
│  Reads: Script output + project context          │
│                                                  │
│  Adds:                                           │
│  - Interpretation ("magnet modeling is blocked    │
│    on a design question")                        │
│  - Recommendations ("complete phase 3, then      │
│    start blanket & shield")                      │
│  - Gap analysis ("4 requirements untraced to     │
│    goals — may be orphaned")                     │
│                                                  │
│  Modes:                                          │
│  - default: dashboard + interpretation           │
│  - decompose <epic>: break into work items       │
│  - close [item]: verify + archive                │
└──────────────────────────────────────────────────┘
```

### 4.2 PM Script Engine: Data Model

The script engine needs to parse structured files. This defines **what it expects**.

**Input validation**: The PM engine validates file structure before parsing (AP-7 input validation guarantee). On validation failure, it reports warnings and produces partial results — "3 of 5 work items parsed; BACKLOG.md frontmatter has invalid status at epic[1].items[2]" rather than crashing. Schema definitions for each file are an implementation concern (Phase 3D).

**Convention**: All markdown files the PM engine reads use **YAML frontmatter** for machine-parsed fields. The markdown body is human-readable content that scripts do not parse. This applies to: spec.md, design.md, plan.md, epic files, and BACKLOG.md. Non-markdown files (traceability_matrix.csv) and low-frequency registry files (REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md) use their existing formats.

**Work item state**: See § 3.2 for the authoritative state table. The PM script engine uses the two-step derivation: file system structure for active/completed/backlog, then spec.md YAML frontmatter Status field for paused/abandoned/failed overrides.

**Backlog state**: The PM engine reads BACKLOG.md YAML frontmatter for epic and item tracking. See § 3.6 for the BACKLOG.md format.

**Project requirements compliance** (derived from `project/REQUIREMENTS.md`):

| Metric | Computed by |
|--------|-------------|
| Total project rules | Count rows in `project/REQUIREMENTS.md` |
| With validation method | Count rows where Validation Method column is non-empty |
| Enforceable (machine-checkable) | Count rows where Enforcement = validation rule (vs. design review) |

Note: Per-feature MR-XXX requirements are NOT tracked at the project level. They are ephemeral artifacts of individual work items in `work/active/{item}/spec.md` and are archived with the work item when complete.

**Validation status** (derived from `project/VALIDATION_MATRIX.md`):

| Metric | Computed by |
|--------|-------------|
| Total criteria | Count rows |
| Passing | Count rows where Status = "passing" |
| Failing | Count rows where Status = "failing" |
| Pending | Count rows where Status = "pending" |

### 4.3 PM Script Engine: Output Format

```
## Project: [name]

### Work Items
Epic: Power Core Components                    [3/8 done]
  [x] Foundation types .................. completed 2026-01-15
  [x] Power balance calcs .............. completed 2026-01-22
  [x] Cost pattern fix (fix) ........... completed 2026-01-28
  [ ] Magnet modeling (model) .......... active:implementing (phase 2/3)
  [ ] Blanket & shield (model) ........ backlog
  [ ] Divertor (model) ................ backlog (blocked by: blanket)
  [ ] Turbine plant (model) ........... backlog
  [ ] System integration (integrate) .. backlog (blocked by: all above)

### Project Rules (REQUIREMENTS.md)
Total: 8 | With validation method: 7 | Machine-enforceable: 4

### Validation Status
Total: 12 | Passing: 7 | Failing: 1 | Pending: 4
Failing: SV-006 (LCOE vs PyFECONS: got 48.2, expected 45.1, tolerance ±5%)
```

### 4.4 Visual Representation

The dashboard uses plain markdown that renders in both terminal and IDE preview. No dependencies on external tools. ASCII trees, markdown tables, and inline metrics.

**Further design needed**: Exact CLI flags, output format options (--json for programmatic use?), and what constitutes the minimum viable dashboard.

---

## 5. Research Split

Two distinct functions, each with a clear job:

### 5.1 External Research: `/research`

The research flow is the primary instance of the curation gate (AP-6) mechanized via scripts (AP-7). The full data management flow is defined in → [information-architecture.md#role-2-domain-knowledge--knowledgemd-new--research-directory](information-architecture.md#role-2-domain-knowledge--knowledgemd-new--research-directory).

```
Input:  Research question + knowledge/SOURCE_INDEX.md
        │
        v
   Agent explores authority sources using specialist agents
   (sysmlv2-doc-analyzer, Explore, etc.)
        │
        v
   Agent writes research document content.
   Script saves to: knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md
   (agent does not choose file path — script enforces convention)
        │
        v
   Agent presents findings + suggests DI-XXX insight candidates
        │
        v
   User reviews: approve/revise/reject report; accept/modify/skip insights
        │
        v
   Agent calls: agentic-mbse pm approve-research <file> --insights '...'
   (AP-7, Tier 2 script: moves file, assigns IDs, appends to knowledge/KNOWLEDGE.md)
```

**Key**: The agent's job is content generation and user interaction. The script's job is file operations and registry maintenance. This separation is the core application of AP-7.

### 5.2 Internal Analysis: `/analyze-models`

```
Input:  Model files (models/), test files (tests/),
        project/MODELING_GUIDE.md + project/REQUIREMENTS.md (Role 4 rules)
        │
        v
   Parse model structure: files, definitions, usages, cross-file deps
   Check rules compliance: which Role 4 rules are followed/violated
   Compute health indicators: test coverage, validation levels, debt markers
        │
        v
   Produce model state report
   (feeds into /status for architecture health section)
```

**Further design needed**: Should `/analyze-models` be a command (agent-driven, interactive) or a script subcommand (deterministic, like `agentic-mbse analyze`)? The answer depends on how much interpretation vs. parsing is involved. Likely: script for metrics, agent command for interpretation.

---

## 6. Knowledge Evolution

Domain knowledge evolves. Later research may contradict or supersede earlier insights. This section defines the control flow for knowledge supersession and the impact propagation that follows.

### 6.1 Knowledge Supersession Flow

When new research contradicts or refines an existing domain insight:

```
User runs /research (or discovers contradiction during any command)
        |
        v
Agent identifies conflict with existing DI-XXX
Presents: "DI-003 states [X]. New findings suggest [Y]. Supersede?"
        |
        v
+-------------------------------------------------+
| USER DECISION POINT                             |
|                                                 |
| "Supersede DI-003"  -> proceed                  |
| "Keep both"         -> new DI with no link      |
| "Revise DI-003"     -> update in place (rare)   |
+-------------------------------------------------+
        |
        v
Agent calls: agentic-mbse pm supersede-insight DI-003
  --new-insight '<structured JSON for DI-017>'
  --reason 'New research on HTS vs LTS cost structures'
        |
        v
+-------------------------------------------------+
| SCRIPT EXECUTION (AP-7, Tier 2)                 |
|                                                 |
| 1. Assign DI-017 ID                            |
| 2. Add DI-017 entry with Supersedes: DI-003    |
| 3. Update DI-003: Status = superseded,          |
|    Superseded-by = DI-017                       |
| 4. Query traceability_matrix.csv:               |
|    which elements have Knowledge = DI-003?      |
| 5. Produce IMPACT REPORT:                       |
|    - Affected model elements (with file paths)  |
|    - Affected PR-XXX requirements               |
|    - Affected work items (from work/active/)    |
| 6. Write impact report to                       |
|    knowledge/research/impacts/                   |
|    DI-003_superseded.md                         |
+-------------------------------------------------+
        |
        v
Agent presents impact report to user:
"DI-003 superseded. 3 model elements affected.
 Recommend: create a work item to update
 cost structure assumptions."
        |
        v
+-------------------------------------------------+
| USER DECISION POINT                             |
|                                                 |
| "Create work item" -> /backlog add              |
| "Review later"     -> impact report persists    |
| "No action needed" -> close (user judgment)     |
+-------------------------------------------------+
```

### 6.2 Impact Analysis Primitive

The impact query is a direct lookup — no intermediate hops through ephemeral documents:

```
DI-XXX -> [traceability_matrix.csv Knowledge column] -> model elements
PR-XXX -> [traceability_matrix.csv Requirement column] -> model elements
```

Fully deterministic (AP-4). The PM script engine exposes this as `agentic-mbse pm impact-query <ID>`.

### 6.3 Impact Report Format

Impact reports persist to `knowledge/research/impacts/` as evidence of why work items were created. They enable later review of how knowledge evolution affected the project.

```markdown
# Impact Report: DI-003 Superseded

**Date**: 2026-02-15
**Superseded by**: DI-017
**Reason**: New research on HTS vs LTS cost structures

## Affected Model Elements

| Element | File | Requirement |
|---------|------|-------------|
| MagnetSystemCostCalc | models/library/calculations/magnet_cost.sysml | PR-005 |
| TFCoilCostCalc | models/library/calculations/tf_coil_cost.sysml | PR-005 |
| PFCoilCostCalc | models/library/calculations/pf_coil_cost.sysml | PR-012 |

## Affected Requirements

| ID | Requirement | Impact |
|----|-------------|--------|
| PR-005 | Magnet costing uses unified cost model | May need split into HTS/LTS variants |

## Affected Work Items

- work/active/magnet-system/ (active:implementing, phase 2/3)

## Recommended Action

Create work item to update cost structure assumptions for HTS vs LTS differentiation.
```

### 6.4 Inline Knowledge Capture

Domain insights can be captured inline during any command — not just `/research`. When the agent discovers a domain fact during `/spec-model`, `/design-model`, `/implement-model`, or any other command, it can propose a DI-XXX candidate immediately without entering the full research flow.

**Trigger**: Agent recognizes a domain insight during active work (e.g., "PyFECONS treats all magnets uniformly but CATF data shows 3x cost difference between HTS and LTS at scale").

**Flow**: Agent proposes → user approves/skips → agent calls `agentic-mbse pm add-insight` with pre-formed content → script assigns ID and appends to `knowledge/KNOWLEDGE.md` → agent confirms and resumes current command.

**Key properties**:
- **AP-7 T1 mechanics, T3 invocation**: The agent passes all DI-XXX fields pre-formed. The script does deterministic file ops only — no `claude -p` call.
- **Source convention**: `work-item:{name}/{artifact}` (e.g., `work-item:magnet-system/design.md`). The work item directory name is the stable identifier, resolvable across `work/active/` and `work/completed/*/`.
- **Rationale field**: Inline-captured insights include a `Rationale` field recording why the insight was recognized, compensating for the absence of a full research document as provenance.
- **Add-only**: No supersession. If the agent discovers a contradiction with an existing DI-XXX, it captures the new insight and flags the conflict, but supersession goes through the full flow (§ 6.1).
- **Immediate, not queued**: The insight is proposed when discovered, while context is fresh. The user can decline to stay in flow.

See [backlog.md B-008](backlog.md) for the full control flow diagram and design rationale.

---

## 7. Downstream Pipeline Verification

### 7.1 Writing Verification Tests Through the Work PM Flow

Verification tests (SV-XXX entries in VALIDATION_MATRIX.md with `Mechanism: test`) are written through the normal work PM flow. During `/spec-model`, the agent identifies what must be verified and creates SV-XXX entries. During `/implement-model`, the agent writes the pytest tests that verify those criteria.

Some of these tests exercise the downstream pipeline (sysml-codegen → teax) and cannot pass until that pipeline is operational. These tests should still be **written early** — they document expectations and activate automatically when the infrastructure is ready.

### 7.2 Pytest Skip Convention for Pre-Codegen Tests

Tests that exercise the downstream pipeline use a skip marker based on codegen availability:

```python
# tests/conftest.py — defines the project-level skip condition
import pytest

def _codegen_pipeline_ready() -> bool:
    """Check whether codegen + teax pipeline is operational."""
    # Implementation detail: check for generated code, sentinel file,
    # or importability of generated package. Exact mechanism is a
    # project-level decision, not an architectural one.
    ...

codegen_available = pytest.mark.skipif(
    not _codegen_pipeline_ready(),
    reason="Codegen pipeline not yet operational"
)
```

Usage in verification tests:

```python
from tests.conftest import codegen_available

@codegen_available
def test_capital_cost_range():
    """SV-001: Total capital cost in $3B-$15B range.

    Runs sysml-codegen on the CATF MFE design, executes the generated
    pipeline via teax, and checks the total capital cost output.
    """
    result = run_codegen_and_simulate("designs/catf_mfe/")
    assert 3e9 <= result.total_capital_cost <= 15e9
```

**Why this pattern matters**:

- Tests exist and document expectations before the downstream pipeline works
- When codegen becomes operational, tests automatically activate — no manual intervention
- VALIDATION_MATRIX.md entries transition from `pending` to `passing`/`failing` naturally
- `/status` can report "N verification tests skipped (awaiting codegen)" by inspecting pytest markers
- The pattern is standard pytest — no custom infrastructure required

### 7.3 Level 8 / sysml-codegen Contract

Level 8 validation ("codegen readiness") checks that models meet the structural requirements for successful code generation. These checks are **derived from** sysml-codegen's extraction and analysis stages.

**Contract**: When sysml-codegen's extractor or analyzer rejects a model pattern that Level 8 accepts, Level 8 must be updated to match. Drift between Level 8 and sysml-codegen is a bug in the validation pyramid, not a modeling workflow problem.

This is a development coordination obligation between the agentic-mbse and sysml-codegen repos. It does not require new data models, automation, or feedback mechanisms — just the stated obligation and periodic verification (e.g., running sysml-codegen against the same test fixtures used for Level 8).
