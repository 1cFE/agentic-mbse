---
name: narrate-goal
description: >
  Create a concise, evidence-linked narrative snapshot of an orchestration goal for human readers. Use when asked to narrate, summarize, explain, or capture the engineering story of a goal at a milestone. The output is optional presentation material outside the goal contract, never goal state or review.
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Narrate Goal

Create one human-readable account of what a goal's evidence supports at one cutoff. The narrative explains the starting problem, causal changes, measured results, limits, and useful visuals without becoming part of `/run-goal`.

## Authority boundary

The narrative is derived presentation material. It is never evidence, state, authorization, a decision record, a review verdict, or an input cited by an authoritative artifact. If the narrative and a cited source disagree, the source wins.

Read from `work/orchestration/goals/<goal-slug>/`, but write only one new file under `work/narratives/`. Do not edit the goal, its evidence, native workflow records, earlier narratives, or project status files.

## Intake and output

Get the canonical goal slug or goal-directory path from the request. Ask only if the target is missing or ambiguous. Confirm that `goal.md`, `trail.md`, and `learnings.md` exist.

Use the generation time in UTC and name the output `work/narratives/YYYYMMDD-HHMMSSZ-<canonical-goal-slug>.md`. Normal creation must not overwrite an existing file. If that exact path already exists, stop and report the collision.

## Establish the source basis

1. Record the base commit with `git rev-parse HEAD` and the UTC generation time.
2. Read `goal.md`, then `trail.md`, then `learnings.md`. Follow the authoritative native records they cite when those records are needed to support the story.
3. Determine goal-level closure from the authoritative trail. A closed round, an accepted learning, or a review that recommends closure does not close the goal. Treat the goal as closed only when the trail records the owner's close ruling; current goals use a `## Goal close — YYYY-MM-DD` heading. Otherwise report it as open at this cutoff.
4. For a closed goal, take the calendar date and disposition from the close entry. If that entry has no explicit time, find the commit that first introduced its close heading and use the commit time only as a rough proxy. Label it `Git commit-time proxy` and include the short commit id. If the entry is uncommitted or its introducing commit cannot be identified, state that the rough time is unavailable; never infer one from nearby work.
5. Do not use an earlier narrative, `CURRENT_WORK.md`, `SUMMARY.md`, or other orientation prose as evidence. They may help locate a source, but every retained claim must resolve to a goal file or native record.
6. Check the goal files and every cited native record actually used with `git status --short -- <paths>` immediately before writing. If relevant files changed while drafting, reread them before creating the snapshot.
7. Dirty sources are allowed. When any relevant input is dirty, label the cutoff `Provisional`, record the base commit, state that uncommitted source content was included, and say that the exact source state may not be recoverable from Git.

For a clean cutoff, identify the base commit in `Narrative cutoff`. For a provisional cutoff, use this meaning without softening it: `Provisional working tree over <base-commit>; uncommitted source content was included and the exact source state may not be recoverable from Git.`

## Required document shape

Start with `# Narrative: <canonical-goal-slug>`, followed by this authority warning in plain language: the narrative summarizes cited records; it is not evidence, state, or a decision record; if it disagrees with a cited source, the source wins.

Then include these metadata bullets:

- `Goal status` — begin with `Open` or `Closed` so closure state is unmistakable. For an open goal, say that no owner close is recorded at this cutoff. For a closed goal, distinguish an ordinary close from `Closed by redirect` when the owner ruling does.
- `Goal closed` — include only for a closed goal. Give the authoritative close date and either the explicit artifact time or an approximate time, short commit id, and `Git commit-time proxy` label. Cite the trail close entry in this bullet.
- `Narrative cutoff` — the commit or provisional working-tree basis.
- `Review status` — the actual review state of the summarized authoritative records. If source records have mixed review states, enumerate them here or label the affected claims where they appear. Do not imply that the narrative itself was independently reviewed.

Use these H2 sections in this exact order:

1. `At a glance`
2. `Starting point and motivation`
3. `Story in one picture`
4. `Research learnings`
5. `Model changes`
6. `Study results`
7. `Outcome and follow-on issues`
8. `Evidence and visual index`

Keep topic-specific H3 headings free to state the actual conclusions. When a required section has no applicable evidence, state that bounded absence briefly instead of inventing content or dropping the heading.

## Writing and visual quality

- Make the narrative easy to skim. A reader scanning headings, bold-led bullets, visuals, and compact tables or lists must recover the starting problem, important change, measured outcome, and remaining limit.
- Use short sections and no large blocks of text. An ordinary prose paragraph must contain no more than 60 words. Lists, tables, diagrams, and code or equation blocks are excluded from that count.
- Keep the complete Markdown file fewer than 250 source lines, including headings, blank lines, tables, and fenced visual blocks.
- Make `At a glance` a short set of bold-led bullets. Define technical terms in plain language on first use. Prefer H3 headings that state conclusions rather than generic topics.
- Use a diagram, table, plot, or other compact visual wherever it makes a causal chain, sequence, constraint interaction, or repeated-field comparison easier to interpret than prose. `Story in one picture` must contain at least one purposeful visual.
- Every visual must state what relationship it shows, stay within the evidence, and cite its authoritative source. Do not add decoration or repeat the visual line by line in adjacent prose.
- Put each quantitative or decision-bearing citation in the same paragraph, table note, or visual caption as the claim it supports. The final evidence index aids navigation; it does not replace claim-local citations.
- Preserve force and provenance. Keep owner decisions distinct from agent interpretation, label provisional readings where they matter, and state unsupported claims in `Outcome and follow-on issues`.

## Validate and report

Before reporting completion:

1. Confirm the target did not exist before this invocation and that no file outside the one new snapshot changed.
2. Run `uv run pytest tests/orchestration/test_narrative_links.py -q`. Fix failures caused by the new narrative. If an unrelated contract failure remains, stop and report it without editing outside this skill's boundary.
3. Recheck the line count, paragraph ceiling, heading order, purposeful visual, closure metadata, authority warning, and local links.
4. Report the output path, the cutoff and whether it is provisional, and the validation result.
