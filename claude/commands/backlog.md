---
name: backlog
description: Manage work items — add, decompose epics, and close completed work
skills: [epic-decomposition]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Backlog Command

**Purpose:** Manage WORK ITEMS — add new items with scale assessment, decompose epics, and close completed work.
**Input:** Mode and optional arguments: `/backlog add [source]`, `/backlog decompose <epic>`, `/backlog close [item]`
**Output:** Updated `work/BACKLOG.md`, epic files in `work/backlog/`, archived work in `work/completed/`

When invoked without arguments, ask: "Would you like to add work items, decompose an epic, or close completed work?"

## Skills Referenced

- **epic-decomposition**: Scale taxonomy (Trivial/Standard/Epic), Goldilocks decomposition principles, work item quality indicators, epic file structure. Consult when assessing scale, writing epic decompositions, and evaluating whether work items are well-scoped.

## Process

### 1. Add Work Items (`/backlog add [source]`)

**Gather items.** If a source path is given (e.g., a research doc in `knowledge/research/`), read it and extract recommendations, next steps, and action items. If no source, ask the user to describe what needs to be done.

**Read project context:**
- `work/BACKLOG.md` — existing items (check for duplicates by title similarity)
- `modeling_project/OVERVIEW.md` — G-XXX goals (which goal does each item serve?)
- `work/backlog/` — existing epic files for context

**Assess scale** for each item per the **epic-decomposition** skill:
- **Trivial** — single attribute, doc comment, value change. Route to `/quick-model`. No tracking in BACKLOG.md.
- **Standard** — feature work, fixes, refactors. Route to `/spec-model`. Gets a work item directory in `work/active/`.
- **Epic** — multiple concerns needing decomposition. Route to `/backlog decompose`. Gets an epic file.

Present scale assessment: "This looks like a [scale] change. Agree?" Let the user override.

**Prioritize** each item with the user (P0/P1/P2/P3). Register Standard items with:
```
agentic-mbse pm add-item --name "<name>" --scale standard --priority <P0|P1|P2|P3> --goal <G-XXX>
```
For an Epic, write and approve its epic file as described below, then register it with `pm add-epic`.
The script updates BACKLOG.md YAML frontmatter and re-renders the markdown body. Do not edit BACKLOG.md directly for state transitions.

Confirm additions and suggest next steps: `/spec-model` for P0 Standard items, `/backlog decompose` for Epics.

### 2. Decompose Epic (`/backlog decompose <epic>`)

If the epic is already registered, read its entry in `work/BACKLOG.md`. If an epic file already exists at `work/backlog/epic-{name}.md`, read it and continue refining. Otherwise, create one.

**Read broadly** to inform decomposition:
- `modeling_project/OVERVIEW.md` — which G-XXX goal does this epic serve?
- `modeling_project/ARCHITECTURE.md` — AD-XXX decisions that constrain the scope
- `knowledge/KNOWLEDGE.md` — DI-XXX insights relevant to the domain
- `knowledge/SOURCE_INDEX.md` — available authority sources

**Decompose** per the **epic-decomposition** skill — apply the Goldilocks principle: items should be independently deliverable, testable, and small enough for one focused work session. Each sub-item gets: name, brief scope, key requirements, dependencies on other sub-items, and scale (should be Standard; if one is Epic, decompose further).

**Write the epic file** at `work/backlog/epic-{name}.md`:
```yaml
---
Status: draft
Priority: <P0|P1|P2|P3>
Goal: <G-XXX>
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
---
```

The body is free-form: executive summary, context, per-item breakdowns with scope and dependencies, sequencing rationale, success criteria, risks. Depth matches complexity.

Present the decomposition to the user. Iterate until approved. On approval, register the epic, then
register its sub-items using the epic priority:
```
agentic-mbse pm add-epic --name "<epic-name>" --priority <P0|P1|P2|P3> --file "work/backlog/epic-{name}.md" --goal <G-XXX>
agentic-mbse pm add-item --name "<item>" --scale standard --priority <P0|P1|P2|P3> --epic "<epic-name>"
```

### 3. Close Work (`/backlog close [item]`)

If no item specified, scan `work/active/` for completed items — read each `spec.md` frontmatter for Status. Present candidates.

Read “Durable Handoff and Closure” in `modeling_project/MODELING_PROCESS.md`. Inspect the linked positive independent audit and confirm that it covers the current scoped change and acceptance conditions. If absent, failed, or superseded, route to `/audit-models` before closing. Reuse applicable evidence rather than rerunning checks merely to archive.

Under the owner's existing closure authorization, use `agentic-mbse pm close-item <WI-XXX>`. The operation archives and updates state; it does not validate audit evidence. Carry warranted durable decisions and discoveries through native PM operations, preserving source authority and owner-reserved approvals.

## Guidelines

- **Scripts own BACKLOG.md** — never manually edit BACKLOG.md for state transitions. The YAML frontmatter is the machine-readable source of truth; the markdown body is a rendered view. Both are maintained by AP-7 scripts.
- Work items must be specific and actionable — not "improve everything." See **epic-decomposition** skill for quality indicators.
- Always check for duplicates before adding.
- When items are too large for Standard scale, decompose — don't create oversized work items.
- If BACKLOG.md doesn't exist, create from template (`project_templates/BACKLOG.md.template`).

---

**Related Commands:** After add → `/spec-model` (Standard) or `/quick-model` (Trivial) | Before close → `/audit-models` | For research → `/research` before adding items
