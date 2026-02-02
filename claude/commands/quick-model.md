---
name: quick-model
description: Make a small SysML model change without the full spec-design-plan-implement pipeline
skills: [sysml-conventions, model-validation]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Quick Model Command

**Purpose:** Make a SMALL change — single attribute, doc comment, value fix, or minor correction — without the full pipeline.
**Input:** Description of the change (inline or interactive)
**Output:** Modified model file(s) + validation results

This command is the Trivial-scale entry point. It exists so that a 1-line fix doesn't require `/spec-model` → `/design-model` → `/plan-model` → `/implement-model`. No work item directory is created. PM does not track trivial changes.

When invoked without a description, ask what change the user wants to make.

## Skills Referenced

- **sysml-conventions**: Syntax rules, naming, definition vs usage, pitfalls. Consult when making the change to ensure correctness.
- **model-validation**: Quality pyramid, CLI usage. Consult when validating the change.

## Process

### 1. Understand

Read the user's description. Identify:
- Which file(s) are affected
- What specifically changes (attribute value, doc comment, redefines keyword, etc.)
- Why (fixing a bug, updating a value, adding missing documentation)

Read the affected model file(s) and enough surrounding context to understand the change. Check `models/README.md` if you need orientation on what exists.

If the user didn't specify a file, search `models/` for the relevant element.

### 2. Assess Scope

**This is the guard rail.** Honestly evaluate whether the change is trivial:

**Trivial** (proceed):
- Single attribute, doc comment, or value change
- Does NOT touch multiple files
- Does NOT introduce new patterns or definitions
- Does NOT require design decisions

**Not trivial** (redirect):
- Touches multiple files
- Introduces new part/calc/port definitions
- Requires interface changes or new bindings
- Needs design decisions about where things go or how they relate

Present your assessment: "This looks like a [trivial/non-trivial] change because [reason]."

If **not trivial**, explain why and redirect: "This change is bigger than it looks — [reason]. I recommend `/spec-model` to scope it properly." Stop here. Don't attempt a partial fix.

If **trivial**, confirm with the user and proceed.

**Common misjudgments**: Adding a "simple" attribute to a part def that other designs redefined — this touches multiple files. Changing a calculation formula — this may require updating test baselines and validation criteria. "Just fix the imports" — may reveal circular dependency issues. When in doubt, it's not trivial.

### 3. Make the Change

Propose the specific edit before making it. Show the before/after for the affected lines so the user sees exactly what will change. Wait for user approval, then apply the edit.

Follow the **sysml-conventions** skill for syntax correctness — naming, redefines syntax, doc comment format, units, etc.

If you encounter unexpected complexity while editing (e.g., the fix requires changes in another file, or the element's interface is consumed by other files), stop and reassess scope. This may not be trivial — redirect to `/spec-model` if needed.

### 4. Validate

Run validation per the **model-validation** skill:

```bash
uv run agentic-mbse validate models/
```

At minimum, Levels 1-3 must pass. If validation fails, diagnose and fix. If the fix cascades into multiple files, reassess scope — the change may need `/spec-model`.

Present results to the user: what file was changed, what the change was, and what validation levels passed.

### 5. Wrap Up

Summarize what was done in 2-3 sentences. If the change revealed something worth investigating further (a pattern that should be a project rule, a domain insight, a related fix needed elsewhere), mention it and suggest the appropriate command (`/research`, `/spec-model`, `/audit-models`). If the change turned out to need follow-up work beyond the trivial scope, suggest adding it to the backlog via `/backlog add` so it gets proper scoping.

## Guidelines

- **Scope honesty is the entire point.** Don't stretch "trivial" to avoid the pipeline — the pipeline exists for a reason. Err on the side of redirecting to `/spec-model`.
- No work item directory. No spec.md, design.md, or plan.md. No entry in `work/BACKLOG.md`.
- If the user describes something non-trivial, redirect gracefully — don't make them feel wrong for asking. Frame it as "this deserves proper scoping" not "this is too hard."
- If you discover a domain insight while making the change, mention it to the user and suggest capturing it via inline `agentic-mbse pm add-insight` — but don't derail the quick fix.
- Always validate. A "quick" change that breaks parsing is worse than no change.
- Check `modeling_project/REQUIREMENTS.md` if the change relates to a known project rule (PR-XXX). Trivial changes should not violate project requirements.

---

**Related Commands:** For larger changes → `/spec-model` | To verify models broadly → `/audit-models`
