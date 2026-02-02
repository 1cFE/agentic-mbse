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

Present the dashboard and interpretation to the user.

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
agentic-mbse pm add-item --epic '<epic-name>' --name '<item-name>' --scale standard
```

### Mode: Close Work Item

Invoked as `/status close <item>`. This is a two-part flow: deterministic archive, then agent-driven project feedback.

#### Part 1: Archive

Call the AP-7 script to archive the work item:

```bash
agentic-mbse pm close-item <WI-XXX>
```

The script moves `work/active/{WI-XXX}_{name}/` to `work/completed/YYYYMMDD_{WI-XXX}_{name}/`, updates `work/BACKLOG.md` status to completed, and returns confirmation with the archive path.

> **Note**: If the close-item script is not yet available (Epic 4), perform the archive manually: move the directory and update BACKLOG.md frontmatter.

#### Part 2: Project Document Review

After archiving, prompt the user with four trigger questions. These surface project-level learnings from the completed work:

**REQUIREMENTS.md**: "Did you discover a modeling pattern during this work item that should be a project-wide rule? (e.g., 'all power calculations must account for recirculating power fraction')"
- If yes: help the user identify which DI-XXX insight or G-XXX goal the requirement derives from, draft the requirement text, then call:
  ```bash
  agentic-mbse pm promote-requirement --requirement "<drafted requirement text>" --source <DI-XXX or G-XXX>
  ```

**ARCHITECTURE.md**: "Did you make a structural decision that future work items need to know about? (e.g., 'HTS and LTS magnets need separate library packages due to 3x cost difference')"
- If yes: help draft an AD-XXX entry, then call:
  ```bash
  agentic-mbse pm register-decision --title "<title>" --decision "<decision text>" --rationale "<rationale>"
  ```

**VALIDATION_MATRIX.md**: "Should any new system-level verification criteria be added? (e.g., 'total capital cost must be in $3B-$15B range')"
- If yes: help draft an SV-XXX entry, then call:
  ```bash
  agentic-mbse pm add-validation --description "<description>" --type <reasonableness|baseline|physical|relationship|rollup> --mechanism <model|test|manual> --expected "<expected value>" --tolerance "<tolerance>"
  ```

**KNOWLEDGE.md**: "Did you learn something about the domain that isn't captured yet? (e.g., 'PyFECONS treats all magnets uniformly but real costs diverge at scale')"
- If yes: help draft a DI-XXX entry, then call:
  ```bash
  agentic-mbse pm add-insight --title "<title>" --source "work-item:<WI-XXX>/<artifact>" --context "<context>" --model-implications "<implications>" --analysis-implications "<implications>" --rationale "<why captured>"
  ```

For each "no", move on. The user doesn't need to justify skipping — these are prompts, not gates.

## Guidelines

- The dashboard must be grounded in file-system state, not memory. Read the actual files every time.
- Interpretation adds value only when it's specific. "Things look good" is useless. "WI-003 is active:implementing phase 2/3, no blockers, validation passing" is useful.
- The close flow trigger questions must be concrete and answerable from recent experience. Don't ask abstract questions — ask about specific patterns, decisions, and discoveries from the work just completed.
- All four trigger questions are optional. The user may answer "no" to all of them. That's fine.
- AP-7 scripts own all state mutations. The agent drafts content; scripts handle file operations, ID assignment, and format enforcement.

---

**Related Commands:** Work items → `/backlog` | Next work → `/spec-model` | Model health → `/analyze-models`
