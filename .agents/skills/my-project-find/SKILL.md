---
name: my-project-find
description: Find relevant project management context in .project/. Use when you need to locate specs, plans, designs, or recent research quickly.
---

Generated from `claude-pack/commands/_my_project_find.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.


# Project Find

Quickly locate and display project management context based on what you need.

**Usage**: ``my-project-find` [topic]`

---

## Topics

### ``my-project-find` current` or ``my-project-find` now`

Show what's being worked on right now.

**Read and summarize**:
- `.project/CURRENT_WORK.md`
- Active item's `plan.md` (current phase)

**Output**: Brief summary of active work, current phase, immediate tasks.

---

### ``my-project-find` backlog` or ``my-project-find` next`

Show what's planned and prioritized.

**Read and summarize**:
- `.project/backlog/BACKLOG.md`
- Top 3 priority epics

**Output**: Prioritized list of upcoming work with brief descriptions.

---

### ``my-project-find` epic [name]`

Show details of a specific epic.

**Read and summarize**:
- `.project/backlog/epic_[name].md` or search for matching epic
- Related items in active/completed

**Output**: Epic summary, items, status, dependencies.

---

### ``my-project-find` item [name]`

Show details of a specific work item.

**Search**:
- `.project/active/[name]/`
- `.project/completed/*[name]*/`

**Read and summarize**:
- spec.md, design.md, plan.md

**Output**: Item summary, current phase, remaining work.

---

### ``my-project-find` history` or ``my-project-find` done`

Show completed work.

**Read and summarize**:
- `.project/completed/CHANGELOG.md`
- Recent completed item folders

**Output**: List of completed epics/items with dates and summaries.

---

### ``my-project-find` blockers`

Show any blockers or issues.

**Read and extract**:
- Blockers section from `CURRENT_WORK.md`
- Any "Blocked" status items
- Risk sections from active epics

**Output**: List of blockers with context.

---

### ``my-project-find` context` (default)

General orientation - show everything needed to get started.

**Read and summarize**:
1. `CURRENT_WORK.md` - What's active
2. Active item's `plan.md` - Where we are
3. `backlog/BACKLOG.md` - What's next
4. `.project/product/INDEX.md` - What the product promises (skip if absent)

**Output**: Comprehensive context summary for starting work.

---

## Implementation

1. Parse the topic from user input (default to "context")
2. Read the relevant files
3. Summarize concisely (not full file contents)
4. Highlight actionable information

### Output Format

```markdown
## [Topic] Summary

**As of**: [Date from CURRENT_WORK.md]

[Concise summary of findings]

### Key Points
- [Point 1]
- [Point 2]

### Relevant Files
- `.project/[path]` - [What it contains]

### Suggested Actions
- [What to do next based on findings]
```

---

## Tips

- Use ``my-project-find` current` at the start of each session
- Use ``my-project-find` backlog` when deciding what to work on next
- Use ``my-project-find` context` for full orientation
- Combine with ``my-status`` for deeper analysis

---

**When to use**: Quick orientation, finding specific project info, starting a work session

