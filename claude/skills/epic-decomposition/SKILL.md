---
name: epic-decomposition
description: >
  Use when asking about "epic", "decompose", "too large", "too small", "scale",
  "work item size", "backlog", "how to break down", "Goldilocks", "standard vs epic",
  "trivial vs standard", "work item taxonomy", "scope sizing",
  or when deciding whether work needs decomposition or determining work item scale.
  Provides the scale taxonomy, Goldilocks indicators, and decomposition process.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# Epic Decomposition

Scale taxonomy, work item sizing, and decomposition process for modeling work.

## Core Principle

Decompose by **domain concern**, not by workflow phase or validation level. Each work item should model one domain subsystem end-to-end, be independently validatable, and produce clear deliverables. The overhead of the workflow (spec/design/plan/implement) must be proportionate to the work.

## When to Reference

- `/backlog` — when adding work items or decomposing epics
- `/spec-model` — when scoping a work item (is this the right size?)
- `/onboard` — when planning initial project work

## Scale Taxonomy

| Scale | Behavior | Entry Point | Tracking |
|-------|----------|-------------|----------|
| **Trivial** | Direct change + validate. No spec/design/plan. | `/quick-model` | No work item directory. Not tracked in PM. |
| **Standard** | Full pipeline: spec → design → plan → implement. Agent adjusts depth naturally. | `/spec-model` | `work/active/WI-XXX_{name}/` directory |
| **Epic** | Must decompose into standard sub-items before execution. | `/backlog decompose` | Epic file in `work/backlog/epic-{name}.md` |

**Routing**: The system infers scale from scope description and confirms with the user. Power users can state scale directly.

**Examples**:
- Trivial: Fix a naming convention violation; update a constant from a source revision
- Standard: Model a costing subsystem; integrate power balance with a plant subsystem
- Epic: End-to-end costing pipeline across all subsystems; full system model with multiple configurations

## Goldilocks Indicators

### Too Large (needs decomposition into epic)

- Spans multiple domain subsystems that could be modeled independently
- Depends on 4+ authority sources
- Would produce 25+ new definitions (part defs, calc defs, constraint defs)
- Success criteria mix structural, validation, and codegen concerns
- Cannot describe scope without referencing multiple architectural decisions (AD-XXX)

### Too Small (doesn't need the full workflow)

- Single definition change or addition
- No new interfaces or cross-file dependencies
- Success criteria are a single validation check
- Spec/design/plan overhead would exceed the work itself

### Just Right (standard work item)

- Models one domain subsystem or concern end-to-end
- Depends on 1-3 authority sources
- Produces 5-20 new definitions
- Can be validated independently through applicable validation levels
- A change to a domain insight (DI-XXX) affecting this item would be localized, not cascading

## Decomposition Process

### Step 1: Review Epic Scope

What domain concern does this epic address? Which project goals (G-XXX) does it serve? What architectural decisions (AD-XXX) constrain it? Read `modeling_project/OVERVIEW.md` and `modeling_project/ARCHITECTURE.md`.

### Step 2: Identify Authority Source Dependencies

List sources from `knowledge/SOURCE_INDEX.md` that constrain the work. Flag unstable sources that need `/research` before items can proceed. Authority sources shape the model from the start — discovering a source conflict mid-implementation causes rework.

### Step 3: Sketch Sub-Items by Domain Concern

Decompose by domain subsystem or model package — NOT by workflow phase (spec/design/plan) and NOT by validation level. Each item produces a complete, independently-validatable piece of the model. Align with architectural decisions (AD-XXX): items should respect package boundaries.

### Step 4: Check Each Item's Independence

For each candidate item, verify:
- Can it be spec'd, designed, and implemented without waiting for other items?
- Does it produce clear deliverables (model files, tests)?
- Is the scope right-sized per the Goldilocks indicators?

### Step 5: Define Success Criteria and Sequencing

Each item gets high-level success criteria — MR-XXX candidates that `/spec-model` will refine. Map dependencies between items. Identify the critical path.

For PR-XXX format used in success criteria, see the **requirements-tracking** skill.

## Epic File Structure

Location: `work/backlog/epic-{name}.md`

```yaml
---
Status: draft | active | completed
Priority: P0 | P1 | P2 | P3
Goal: G-XXX
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

**Body sections**: Executive Summary, Context (G-XXX, DI-XXX, AD-XXX links), Authority Source Dependencies, Success Criteria, Items (per-item breakdowns with dependencies), Sequencing (dependency map, critical path), Risks.

**Relationship to BACKLOG.md**: BACKLOG.md is the dashboard (summary of all epics with status). Epic files hold the decomposition detail. When a sub-item moves to execution, it gets a `work/active/WI-XXX_{name}/` directory.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|-------------|---------------|
| **Phase-as-item** ("Item 1: Design. Item 2: Implement.") | Each item should go through its own full workflow cycle |
| **Validation-level decomposition** ("Item 1: L1-3. Item 2: L4-6.") | Levels are quality gates, not separable units of work |
| **Separating authority sources** ("Item 1: Structure. Item 2: Data.") | Sources constrain models from the start; integrate together |
| **Ignoring AD-XXX boundaries** | Items should respect package boundaries from ARCHITECTURE.md |
| **Vague success criteria** ("Models are complete") | Reference specific domain constraints, SV-XXX entries |
| **No goal traceability** | Every epic must link to G-XXX goals in OVERVIEW.md |

## Related Skills

- For PR-XXX format used in success criteria, see the **requirements-tracking** skill.
- For project file organization, see the **project-structure** skill.
