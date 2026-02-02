---
name: spec-model
description: Define modeling requirements and success criteria for SysMLv2 model enhancements
skills: [project-structure, source-traceability, model-validation, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Spec Model Command

**Purpose:** Define WHAT to model — scope, requirements, and success criteria for a modeling work item.
**Input:** Model enhancement ideas, modeling scope, optional research reference
**Output:** `work/active/{WI-XXX}_{name}/spec.md`

The spec is the **first artifact** for a Standard work item and the **state-bearing file** — its YAML frontmatter is the single source of truth for work item state. Everything downstream (design, plan, implementation) consumes the spec's requirements and scope boundaries.

When invoked without a description, ask what model enhancement the user wants to specify.

## Skills Referenced

- **project-structure**: Library vs designs separation, file organization. Consult when specifying where model elements belong.
- **source-traceability**: Citation patterns, SOURCE_INDEX format. Consult when specifying traceability requirements.
- **model-validation**: Quality pyramid, regression testing patterns. Consult when defining success criteria and verification methods.
- **requirements-tracking**: MR-XXX/PR-XXX format, EARS syntax. Consult when writing requirements. Flag durable requirements for later promotion to PR-XXX.

## Process

### 1. Understand the Landscape

The spec is the first to survey what matters for this work item. Read broadly.

**Project context:**
- `modeling_project/OVERVIEW.md` — project goals (G-XXX) and analysis questions (AQ-XXX). Which ones does this work item serve?
- `knowledge/KNOWLEDGE.md` — domain insights (DI-XXX). Are there captured insights relevant to this scope? Surface them — they should inform requirements.
- `work/BACKLOG.md` — which epic does this belong to?
- `knowledge/SOURCE_INDEX.md` — what domain sources are available for traceability?

**Epic context** (when the work item belongs to an epic): Read the epic file at `work/backlog/epic-{name}.md`. Epics contain baseline requirements, scope boundaries, dependencies, and per-item breakdowns. **The spec should start from this foundation, not a blank page.** Identify which epic-level requirements apply to this specific work item.

**Existing models:**
- `models/README.md` — what's already in the library? Does this model already exist?
- Search `models/library/` and `models/designs/` for related definitions
- If enhancing or refactoring, read the relevant model files

**Prior work:**
- `knowledge/research/` — has research been done on this topic?
- Related completed work items in `work/completed/` (if referenced)

Ask focused questions to fill gaps: scope type (new/enhance/refactor), location (library/designs), current limitations, validation targets.

### 2. Scope and Confirm

Present your understanding back to the user: what's being modeled, current state, what needs to change, why it matters, which G-XXX goals and AQ-XXX questions it addresses, what epic it belongs to.

Define clear boundaries — what's in scope and what's not. If scope is too large (>5 model files or multiple independent concerns), suggest decomposition via `/backlog`.

**Wait for user confirmation before writing requirements.**

### 3. Define Requirements and Success Criteria

Write requirements in MR-XXX format per the **requirements-tracking** skill (EARS syntax: "The model SHALL..."). Categorize as Functional, Quality, Constraint, or Traceability.

**Trace requirements to their sources.** Each MR-XXX should reference the G-XXX goal, AQ-XXX question, DI-XXX insight, or PR-XXX project requirement it derives from. This establishes the upstream traceability chain.

**Define success criteria that are both human-readable AND machine-checkable** where possible. The **model-validation** skill has regression testing patterns. For library modifications, identify which existing designs depend on the library and what interfaces must remain stable.

**Flag requirements for promotion.** Some MR-XXX will be durable enough to become project-wide PR-XXX rules (e.g., "all power calculations must account for recirculating power"). Flag these explicitly — `/implement-model` will handle the actual promotion.

**Create SV-XXX entries.** When a success criterion maps to a verifiable system-level check, create an entry in `modeling_project/VALIDATION_MATRIX.md` with status `pending`. These become the verification contract for `/audit-models`.

Present requirements to the user. Iterate until approved.

### 4. Write the Spec

Create the work item directory and write the spec:

```bash
mkdir -p work/active/{WI-XXX}_{name}
```

The spec.md must start with YAML frontmatter (this is the work item's authoritative state):
```yaml
---
Status: active
Scale: standard
Epic: <epic name from work/BACKLOG.md>
Owner: <user>
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
---
```

## What Good Output Looks Like

A spec.md should contain:

- **YAML Frontmatter** — Status, Scale, Epic, Owner, Created, Updated (state-bearing, read by PM scripts)
- **Overview** — what's being created/enhanced and why (1-2 sentences)
- **Goals & Context** — which G-XXX goals and AQ-XXX questions this serves, relevant DI-XXX insights surfaced from KNOWLEDGE.md, epic-level context if applicable
- **Current State** — existing model files and elements (with paths and line numbers), known issues. "None — creating new" if greenfield.
- **Modeling Requirements** — MR-XXX numbered per **requirements-tracking** skill. Each has: type, EARS-format description, priority, rationale, validation method, and source (G-XXX, AQ-XXX, DI-XXX, or PR-XXX it derives from). Flag any that should be promoted to PR-XXX.
- **Scope Boundaries** — in scope (specific model elements with file paths) and out of scope
- **Success Criteria** — functional (elements exist, calculations work), quality (validation levels pass), verification (baseline comparison targets, constraint satisfaction). Reference SV-XXX entries created in VALIDATION_MATRIX.md.
- **Assumptions & Risks** — numbered, with confidence/likelihood and impact
- **Traceability** — source requirements (codebase files with lines, literature), downstream impacts (other models/designs affected), applicable PR-XXX project requirements
- **Related Artifacts** — links to epic file, research, design (to be created), plan (to be created)

The depth should match the complexity. A simple library addition needs less than a multi-subsystem enhancement.

## Guidelines

- Survey broadly — the spec's job is to establish context that downstream commands read selectively
- Start from the epic file when one exists — don't reinvent baseline requirements
- Trace every requirement to its source (G-XXX, DI-XXX, PR-XXX, or domain knowledge)
- Always check `models/README.md` — don't spec something that already exists
- Requirements must be specific and measurable — never "model works well"
- Specify where elements go (library/ vs designs/) per **project-structure** skill
- Specify traceability sources (file:line references) per **source-traceability** skill
- If scope is vague, stop and ask. If sources aren't specified, stop and ask.

---

**Related Commands:** Before → `/research` | After → `/design-model`
