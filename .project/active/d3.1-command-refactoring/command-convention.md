# Command Structural Convention (Q15 Resolution)

**Status:** Confirmed across all 9 refactored commands
**Date:** 2026-02-02
**Purpose:** Reference for D3.2 (new commands) and future command maintenance

---

## Design Philosophy

Commands are **guidance documents, not operations manuals**. Skills carry domain knowledge; the spec defines what to build; the process describes the shape of the work without micromanaging the agent. This produces commands averaging ~114 lines that are more effective than the 400-1300 line originals because the agent can hold the entire command in context alongside the skills.

---

## Required Structure

Every command follows this structure. Sections may be omitted when they don't apply (noted below), but the ordering is fixed.

### 1. YAML Frontmatter

```yaml
---
name: <command-name>
description: <one-line job description — what the command DOES, not how>
skills: [<skill-1>, <skill-2>, ...]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---
```

**Fields:**
- `name`: Kebab-case, matches filename without `.md`
- `description`: From components.md § 1 job description. Active voice, present tense.
- `skills`: Array of skill names this command depends on. Must match directory names in `.claude/skills/`. Skills are loaded at command invocation.
- `allowed-tools`: Tools the agent may use. Include `WebSearch` and `WebFetch` only when the command needs external web access (e.g., research). Include `Task` when the command spawns sub-agents.
- `user-invocable`: Always `true` for shipped commands.

### 2. Title + Purpose/Input/Output

```markdown
# <Command Name> Command

**Purpose:** <VERB> — <what the command does in one sentence>.
**Input:** <what the user provides or what files the command reads>
**Output:** <what artifacts the command produces, with paths>
```

The Purpose line starts with a capitalized verb that matches components.md § 1 "Job" column (e.g., "Define WHAT to model", "VERIFY models", "Manage WORK ITEMS").

Follow with 1-3 lines of essential framing — what makes this command distinct, how it fits in the workflow. End with the "when invoked without arguments" behavior.

### 3. Skills Referenced

```markdown
## Skills Referenced

- **<skill-name>**: <What it contains>. <When to consult it during this command's workflow>.
```

This is behavioral guidance, not just a list. Each entry tells the agent:
1. What knowledge the skill provides (1 clause)
2. When in the workflow to consult it (1 clause)

Example from design-model:
> **sysml-conventions**: Syntax rules, naming, definition vs usage, pitfalls, doc comments. Consult when writing SysML stencils or reviewing prototype code.

### 4. Process

```markdown
## Process

### 1. <Phase Name>
...
### 2. <Phase Name>
...
```

The core algorithm. Lightweight numbered steps following the pattern: **Understand → Core Work → Validate → Approve/Complete**. The depth adapts to command complexity — a simple command might have 3 steps, a complex one might have 5.

**Key conventions:**
- Context reading is integrated into the process steps (typically step 1), not a separate section. The spec command reads broadly in step 1; downstream commands read selectively through what the spec references.
- AP-7 script invocations are placed **inline** at the workflow point where the agent should call them, not in a separate section. Use code blocks for exact CLI syntax.
- Present user decision points clearly: what options, what happens for each.
- Reference skills by name in bold when the agent should consult them: "per the **model-validation** skill."

### 5. What Good Output Looks Like (when applicable)

```markdown
## What Good Output Looks Like

A <artifact> should contain:

- **Section** — what goes here
- **Section** — what goes here
```

Describes the **artifact structure** the command produces, not the steps to produce it. Include only when the command generates a structured document (spec, design, plan, audit report, research doc, epic file). Omit for commands whose output is primarily state transitions (onboard, manage-sources, backlog close).

### 6. Sub-Agent Usage (when applicable)

```markdown
## Sub-Agent Usage

| Question Type | Agent |
|--------------|-------|
| ... | `agent-name` |
```

Compact table mapping question types to specialist agents. Include only when the command uses multiple agents (design-model, research). Omit when agent usage is simple or not applicable.

### 7. Guidelines

```markdown
## Guidelines

- <critical rule 1>
- <critical rule 2>
```

Concise rules and error handling. These are the "must not violate" constraints — things that would cause the command to produce wrong output. Combine what were previously separate "Guidelines" and "Error Handling" sections.

### 8. Related Commands

```markdown
---

**Related Commands:** Before → `/<command>` | After → `/<command>`
```

Single line showing workflow context: what typically comes before and after this command. Separated by a horizontal rule.

---

## Conventions Across All Commands

### Line Budget

Target: **100-140 lines**. The established average is 114 lines. No command should exceed 200 lines. If a command is growing beyond this, knowledge is probably being embedded that should be in a skill.

### Skill vs Command Boundary

| In the command | In a skill |
|----------------|------------|
| Workflow steps (what to do, in what order) | Domain knowledge (rules, formats, patterns) |
| User decision points | Reference material (stencils, schemas) |
| AP-7 script invocations (exact CLI) | Quality criteria and thresholds |
| Artifact structure ("What Good Output Looks Like") | Naming conventions, syntax rules |
| Command-specific error handling | Cross-command standards |

### AP-7 Script Invocations

- Place inline in the Process section at the point where the agent should call them
- Use fenced code blocks with exact CLI syntax and argument placeholders
- Scripts own structured state — the agent never directly edits BACKLOG.md, KNOWLEDGE.md, REQUIREMENTS.md, ARCHITECTURE.md, VALIDATION_MATRIX.md, or traceability_matrix.csv for state transitions
- The agent generates content and calls the script; the script handles file operations

### Path Conventions

All paths use the 4-directory model:
- `knowledge/` — SOURCE_INDEX.md, KNOWLEDGE.md, research/, sources/
- `modeling_project/` — OVERVIEW.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, MODELING_GUIDE.md, MODELING_PROCESS.md, intent/
- `work/` — BACKLOG.md, backlog/, active/, completed/, analysis/, learnings/
- `models/` — library/, designs/
- `data/` — traceability_matrix.csv

### YAML Frontmatter in Artifacts

Commands that produce work item artifacts (spec.md, design.md, plan.md) must instruct the agent to generate YAML frontmatter. The frontmatter schema for each artifact type is defined in `.project/concepts/architecture-redesign/frontmatter-schemas.md`. spec.md is the state-bearing file for work items.

---

## Deviation Log

Deviations from the original FR-1 proposal in the spec (all improvements):

1. **No separate "Context Reading" section.** Context reading is integrated into Process step 1. This improves coherence — the agent reads what it needs as part of understanding, not as a separate checklist.

2. **No separate "AP-7 Script Invocations" section.** Invocations are inline per FR-11. The agent sees the call at the point in the workflow where it's relevant.

3. **"What Good Output Looks Like" replaces rigid templates.** Describes the artifact structure in prose rather than providing a fill-in-the-blank template. This gives the agent flexibility to adapt depth to complexity.

4. **Line targets significantly exceeded.** Spec targeted ~250 lines; actual average is ~114. The aggressive workflow tightening went further than anticipated — a positive deviation.
