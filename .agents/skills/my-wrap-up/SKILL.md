---
name: my-wrap-up
description: Update project state at session end and propose cheap records for confirmation. Use when closing a session and refreshing .project/CURRENT_WORK.md, the completion changelog, or the execution register.
---

Generated from `claude-pack/commands/_my_wrap_up.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Wrap Up

**Purpose:** End-of-session command that writes cheap records: current state, a completion no work item captured, and a fact learned by doing. Each has a tracked home that already exists.

## Usage

```
`my-wrap-up`                   # review the session, update state, propose records
`my-wrap-up` --quick           # just update CURRENT_WORK.md status
```

## Why This Exists

Sessions die and take their context with them. Three things are worth keeping, and each has a home:

- **What is active right now** → `.project/CURRENT_WORK.md`. The first file the next session reads.
- **Important work that shipped without becoming a tracked item** → `.project/completed/CHANGELOG.md`. Work that goes through ``my-close`` lands there already. Work that never became a work item reaches the next session only if this command catches it.
- **A fact about how this codebase or environment actually behaves, learned by doing** → `.project/execution/ENTRIES.md`.

All three are records. A record is cheap and survives a mediocre entry. This command writes records and nothing else — curated documentation changes through the work-item lifecycle, not from a session summary.

## Instructions

### Step 1. Review What Changed

1. **Review the conversation** to identify what was worked on, decisions made, and problems solved this session. The conversation is the source of truth for what *this* session did.
2. **Cross-check with git** — run `git diff --stat` and `git log --oneline -5` to validate. If the git log contains commits that don't match your conversation (e.g., from another concurrent session), ignore them — only summarize your own work.
3. Read `.project/CURRENT_WORK.md` to understand the current state.
4. Briefly summarize to the user: "Here's what happened this session: [summary]"

### Step 2. Update CURRENT_WORK.md

`.project/CURRENT_WORK.md` holds Active Work and Up Next. Update it to reflect the session:

- **Update active items** with current status, blockers, next steps. Append a bullet; don't rewrite what an earlier session left.
- **Add new items** if work was started but not finished.
- **Update "Up Next"** if priorities shifted.
- Keep entries concise — the next session reads this to get oriented.

Completed items are removed from Active Work by ``my-close``, which files the completion in the CHANGELOG. This file carries no history of its own.

**If `--quick` was passed, skip Steps 3 and 4 and go straight to Step 5.**

### Step 3. Propose Records — and Wait

Two candidates. Either, both, or neither may apply. **Write nothing in this step.**

**A light CHANGELOG entry** — an important change this session made that no work item captured. Work that went through ``my-close`` is already in the CHANGELOG; this catches what never became a tracked item. Judge it against that guidance: *important changes not captured by work items*. Routine edits, in-progress work, and anything still on the branch unfinished are not candidates.

**An execution-register entry** — a fact about how this codebase or environment behaves that you learned by doing, this session. You hold the session, so find candidates by asking yourself what cost real time and would cost the next agent the same. `.project/execution/README.md` carries the density bar and the boundary against the other homes; read it before proposing. If ``my-close`` already filed a fact this session, don't propose it again — both beats write to the same register.

Show the user each candidate in the shape it would be written, and **stop and wait for confirmation.** Do not proceed to Step 4 until the user has answered.

"Nothing to record" is a normal outcome and the common one. Say so and move to Step 5. Do not pad either register to have something to show.

### Step 4. Write What Was Confirmed

Write only what the user confirmed.

**The light CHANGELOG entry** goes at the **top** of `.project/completed/CHANGELOG.md`, above the newest existing entry. The file is ordered newest-first and session boot reads the first five entries; an entry appended at the bottom is invisible to it. Three fields, which is what the boot read takes:

```markdown
## [2026-09-11] - explicit-skill-scopes

**Type**: Change

### Summary
Made the workflow shortcut skills explicit-only so they stop firing on unrelated prompts.
```

`Type: Change` is what distinguishes these from ``my-close``'s entries, which are `Item` or `Epic` and carry `Duration` and `Deliverables` as well.

**The execution note** is appended to the **end** of `.project/execution/ENTRIES.md`, using the format in `.project/execution/README.md`. No script, no id — just the tagged heading, **Fact**, and **Evidence**. Never rewrite an existing entry.

### Step 5. Stage, Show, Confirm

1. **Stage all of the session's changes**, not just the files this command wrote — `git add -A`. The session ends with its work staged, records and code together.
2. Show what is staged: `git status --short` and `git diff --cached --stat`.
3. Summarize:

```
Wrap-up complete:
- CURRENT_WORK.md: [what changed]
- CHANGELOG: [the light entry, or "none"]
- Execution register: [the fact, or "none"]
- Staged: [N files]
```

4. **Ask whether to commit, and wait.** Propose a commit message describing the session's work, following the project's CLAUDE.md conventions for message format and attribution. Commit only if the user says yes; otherwise leave everything staged and stop.

Never commit without asking.

---

**When to use this:**
- End of a work session before closing Claude
- After completing a significant piece of work
- After discovering something that burned time (so it doesn't burn time again)
- When the user says "wrap up", "save context", or similar

**Related Commands:**
- ``my-handoff`` — write a handoff doc so a fresh agent can continue mid-task
- ``my-close`` — archive a completed work item or epic before wrapping up

User-provided arguments are supplied when this skill is invoked.

