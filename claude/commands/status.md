---
name: status
description: Present project state dashboard with intelligent interpretation and recommendations
skills: [epic-decomposition, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Status Command

**Purpose:** Understand PROJECT STATE — what's done, what's active, what's blocked, what to do next.
**Input:** Mode (default, `decompose <epic>`, or `close <item>`)
**Output:** Dashboard with interpretation and recommendations; or epic decomposition; or archived work item

This command layers intelligent interpretation on top of deterministic project state. The script computes facts (items done, validation status, coverage); the agent interprets them (what's blocked, what's ready, what needs attention).

When invoked without arguments, run the default dashboard mode.

## Skills Referenced

- **epic-decomposition**: Goldilocks principle, work item taxonomy, decomposition process. Consult during `decompose` mode when breaking an epic into work items.
- **requirements-tracking**: PR-XXX format, compliance checking. Consult when interpreting requirements coverage and gap analysis.

## Process

This command has three modes. Determine which from the user's invocation.

### Mode: Default Dashboard

#### 1. Get Project State

Call the PM dashboard script for deterministic state:

```bash
uv run agentic-mbse status
```

> **Note**: This script is delivered by Epic 4. If it is not yet available, manually read the project state files: `work/BACKLOG.md` (epic and item status), `work/active/` (in-progress items — read each spec.md frontmatter for Status), `work/completed/` (archived items), `modeling_project/OVERVIEW.md` (G-XXX goals, AQ-XXX questions), `modeling_project/REQUIREMENTS.md` (PR-XXX count), and `modeling_project/VALIDATION_MATRIX.md` (SV-XXX pass/fail/pending). Present a dashboard from what you find.

#### 2. Interpret and Recommend

Layer intelligence on top of the dashboard output:

- **What's blocked** — items waiting on dependencies, paused items, failing validation
- **What's ready** — backlog items with no blockers, next phases of active work
- **What needs attention** — stale items (active but no recent updates), failing SV-XXX entries, requirements with no traced model elements
- **Gap analysis** — PR-XXX requirements without satisfying elements, G-XXX goals with no work items, AQ-XXX questions still open
- **Recommendations** — specific next actions ("complete WI-003 phase 2, then start WI-005", "run `/audit-models` — 3 PR-XXX rules are untested")

Distinguish an epic's PM rollup “all items closed” from independent acceptance of its outcomes and integration; inspect the linked epic audit before claiming the latter. Present the dashboard and interpretation to the user.

### Mode: Decompose Epic

Invoked as `/status decompose <epic-name>`.

#### 1. Read Epic Context

Read the epic file at `work/backlog/epic-{name}.md`. Read `modeling_project/OVERVIEW.md` for the G-XXX goal the epic serves. Read `modeling_project/ARCHITECTURE.md` for structural context.

#### 2. Decompose

Per the **epic-decomposition** skill, break the epic into Standard work items. Each item should have: a name, a scope description, dependencies on other items, and baseline requirements derived from the epic.

Present the decomposition to the user for review. Iterate until approved.

#### 3. Register Items

For each approved work item, call the AP-7 script to register in BACKLOG.md:

```bash
agentic-mbse pm add-item --epic '<epic-name>' --name '<item-name>' --scale standard --priority <P0|P1|P2|P3>
```

### Mode: Close Work Item

Invoked as `/status close <item>`. Read “Durable Handoff and Closure” in `modeling_project/MODELING_PROCESS.md`. Inspect the linked positive independent audit for the current scoped change before calling `agentic-mbse pm close-item <WI-XXX>`. If audit evidence is missing or inadequate, route to `/audit-models` first. Use the owner's existing closure authorization; do not add a repeat confirmation.

The native operation archives the item and updates its records. It does not verify audit evidence. Carry any warranted durable decisions or discoveries through the applicable native PM operations, preserving owner-reserved approvals.

## Guidelines

- The dashboard must be grounded in file-system state, not memory. Read the actual files every time.
- Interpretation adds value only when it's specific. "Things look good" is useless. "WI-003 is active:implementing phase 2/3, no blockers, validation passing" is useful.
- AP-7 scripts own all state mutations. The agent drafts content; scripts handle file operations, ID assignment, and format enforcement.

---

**Related Commands:** Work items → `/backlog` | Next work → `/spec-model` | Model health → `/analyze-models`
