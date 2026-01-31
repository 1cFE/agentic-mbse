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

### 2.1 The Two Dimensions

Every work item has an **intent** (what kind of work) and a **scale** (how much process). These are not metadata — they change downstream behavior (AP-3).

### 2.2 Intent Dimension

Each intent changes: (a) which pipeline stages run, (b) what the spec asks for, and (c) what validation emphasizes.

| Intent | Pipeline path | Spec behavior | Validation emphasis |
|--------|--------------|---------------|---------------------|
| **Model** | spec → design → plan → implement → audit | Full: scope, requirements, success criteria | Correctness against sources |
| **Fix** | spec → implement | Lightweight: what's wrong, what "fixed" looks like | Regression (don't break other things) |
| **Investigate** | research → (optional: spec) | Deferred: research must complete before requirements can be written | N/A (may not produce implementation) |
| **Refactor** | spec → plan → implement | Structural: what changes, what must be preserved | Regression (behavior unchanged) |
| **Integrate** | spec → design → implement | Interface-focused: what connects, what contracts must hold | Cross-file consistency |

**Behavioral differences that justify each intent**:

- **Model vs Fix**: Fix skips design (user knows the structure) and has a lightweight spec (no requirements registry — just "before/after"). Model needs full design because structural decisions haven't been made.
- **Investigate vs Model**: Investigate may terminate after research without producing implementation. The system shouldn't pressure the user into spec→design→plan when they're still learning.
- **Refactor vs Model**: Refactor skips design (no new structure is being invented) but needs a plan (regression safety requires careful ordering). The spec focuses on preservation criteria, not business requirements.
- **Integrate vs Model**: Integrate focuses on interfaces between existing components. Design is about contracts, not component internals.

### 2.3 Scale Dimension

Each scale changes: how much artifact overhead is appropriate.

| Scale | Artifact behavior | Entry point |
|-------|------------------|-------------|
| **Trivial** | No spec/design/plan. Direct: understand → execute → validate | `/quick-model` |
| **Small** | Abbreviated spec (inline in backlog or 1-page). No separate design doc for Fix/Refactor | `/spec-model` (abbreviated mode) |
| **Standard** | Full artifacts per intent's pipeline path | `/spec-model` (full mode) |
| **Epic** | Must decompose into sub-items first, then each sub-item enters pipeline | `/backlog decompose` → sub-items |

### 2.4 Control Flow: Work Item Routing

When work begins, the system determines intent and scale. This is the **routing decision tree**:

```
User describes what they want to do
        │
        v
┌─────────────────────────────────┐
│ DETERMINE INTENT                │
│                                 │
│ System infers from description, │
│ presents to user for            │
│ confirmation:                   │
│                                 │
│ "It sounds like you want to     │
│  [fix/build/investigate/        │
│   refactor/integrate].          │
│  Is that right?"                │
└───────────────┬─────────────────┘
                │
                v
┌─────────────────────────────────┐
│ DETERMINE SCALE                 │
│                                 │
│ System assesses from scope:     │
│                                 │
│ Trivial: single attribute,      │
│   doc comment, value change     │
│ Small: single file, clear scope │
│ Standard: multi-file feature    │
│ Epic: > 3 days, multiple        │
│   concerns, needs decomposition │
│                                 │
│ "This looks like a [scale]      │
│  change. Agree?"                │
└───────────────┬─────────────────┘
                │
                v
┌─────────────────────────────────┐
│ ROUTE TO PIPELINE PATH          │
│                                 │
│ Intent × Scale → entry point    │
│ (see matrix in 2.2/2.3)        │
└─────────────────────────────────┘
```

**UX principle**: The system infers and confirms. The user never fills out a form. For power users, tags can shortcut: `/spec-model --intent=fix "missing redefines in cost_model"`.

### 2.5 Backward Navigation

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

## 3. Project Management

### 3.1 The Split: Scripts vs. Agent

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

### 3.2 PM Script Engine: Data Model

The script engine needs to parse structured files. This defines **what it expects**:

**Work item state** (derived from file system):

| State | Determined by |
|-------|-------------- |
| **backlog** | Entry in `work/BACKLOG.md`, no directory in `work/active/` |
| **active** | Directory exists in `work/active/{item}/` |
| **active:stage** | Which artifact files exist: spec.md only = speccing; design.md = designing; plan.md = planning; implementation started = implementing |
| **paused** | Explicit marker in `work/BACKLOG.md` or `work/active/{item}/STATUS` |
| **completed** | Directory in `work/completed/` |

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

### 3.3 PM Script Engine: Output Format

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

### 3.4 Visual Representation

The dashboard uses plain markdown that renders in both terminal and IDE preview. No dependencies on external tools. ASCII trees, markdown tables, and inline metrics.

**Further design needed**: Exact CLI flags, output format options (--json for programmatic use?), and what constitutes the minimum viable dashboard.

---

## 4. Research Split

Two distinct functions, each with a clear job:

### 4.1 External Research: `/research`

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

### 4.2 Internal Analysis: `/analyze-models`

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
