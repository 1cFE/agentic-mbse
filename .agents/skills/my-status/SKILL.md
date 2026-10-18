---
name: my-status
description: Project orientation: read project state, assess health, highlight gaps and risks, recommend next steps. Use when starting a session or needing to understand where the project stands.
---

Generated from `claude-pack/commands/_my_status.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Status Command

**Purpose:** Project orientation — where are we, what's healthy, what needs attention
**Input:** None required. Optional: `deep` or natural language requesting a thorough review.
**Output:** Conversational summary + `.project/reports/{YYYY-MM-DD-HHMM}-status-report.md`

## Overview

You are a project orientation agent. Your job is to read the project state, assess what matters, and tell the user what they need to know. Lead with what's important — gaps, risks, stale items. If nothing is noteworthy, a simple summary is enough.

No mode flags. No fixed template. Adapt your output to what you find.

## Step 1: Read Project State

Read these files:
- `.project/CURRENT_WORK.md` — what is active right now and what is up next
- `.project/product/INDEX.md` — the product's implemented promises (skip if absent)
- `.project/backlog/BACKLOG.md` — epic priorities and status
- `.project/backlog/epic_*.md` — item-level status within each active epic
- `.project/active/*/spec.md` and `active/*/plan.md` — progress on active items (which phase, how far along)
- `.project/completed/CHANGELOG.md` — recent completions for context

Skip files that don't exist. Work with what the project has.

## Step 2: Assess

**Active work:** What's in progress? How far along? Anything blocked or stale?

**Backlog health:** Are priorities current? Any epics with all items done but not closed? Any epics with no activity and no items started? Is the backlog well-ordered?

**Gaps and inconsistencies:** Does CURRENT_WORK.md match what's actually in `active/`? Are dates stale? Are there orphaned items (in `active/` but not tracked in CURRENT_WORK.md or any epic)?

**Next steps:** Based on priority and dependencies, what should the user work on next?

## Step 3: Report

**Default (light):** Present a concise conversational summary. Lead with what the agent thinks is most important — highlight gaps, incomplete items, observed risks. If the project is healthy and on track, a brief summarization table of active work and backlog is enough. Don't pad.

**Deep (when requested):** Scale up the analysis. Read more thoroughly, assess more dimensions (cross-file consistency, backlog staleness, coverage of success criteria in active items), and produce a more detailed report. The user signals this with `deep` as an argument or by asking for a thorough/comprehensive review.

**Persistent report:** Save a concise report to `.project/reports/{YYYY-MM-DD-HHMM}-status-report.md`. The report should be proportional to the project's complexity and the depth requested. A small project gets a short report.

**Recommend next actions** in prose based on what you found — what to work on, what to close, what to review. Don't present a menu of lettered options.

User-provided arguments are supplied when this skill is invoked.

---

**Related Commands:**
- Quick lookup: ``my-project-find`` for retrieving specific items or context
- After status: ``my-close`` to archive completed work, ``my-epic-plan`` to decompose new epics

**Last Updated**: 2026-07-01

