---
name: my-epic-plan
description: Decompose shaping output into a scoped epic with backlog items. Use when concepts or research are ready to become an implementation plan.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `claude-pack/commands/_my_epic_plan.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Epic Plan

**Purpose:** Bridge shaping to scoping — take concept, concept-design, and research files and produce a scoped epic with backlog items.
**Input:** Shaping-tier files (via `User-provided arguments are supplied when this skill is invoked.` or interactive discovery)
**Output:** `.project/backlog/epic_{name}.md` + updated `BACKLOG.md`

## Before You Start

Read these fully:
- `.project/EPIC_GUIDE.md` — decomposition methodology, sizing rules, item template, quality checks. Follow it. Do not restate it here.
- `.project/epic_template.md` — the output structure. Copy it; do not improvise a format.
- `.project/backlog/BACKLOG.md` — existing epics, so you don't duplicate or collide.

## Finding Input Files

If `User-provided arguments are supplied when this skill is invoked.` names a file path or concept name, use it. If ambiguous or missing, scan `.project/concepts/` and `.project/research/` and ask the user which files are the source material for this epic. When a named concept has a shaping product-design sibling (`.project/concepts/{name}-product-design.md`), include it among the candidates; it is not mandatory source material.

Read every identified source file fully before proceeding.

## Stage 1: Scope

1. Copy `.project/epic_template.md` to `.project/backlog/epic_{name}.md`. Derive the epic name from the primary concept; you'll confirm it with the user below.
2. Fill in these sections from the source material:
   - **Epic ID, Status** (Draft), **Priority**, **Created**, **Estimated Effort** (rough)
   - **Executive Summary** — what this epic delivers and why, in 2-3 sentences
   - **Source Documents** — list every shaping-tier file you read, with type annotations (concept, concept-design, research)
   - **Why This Epic** — current state vs. future state
   - **Success Criteria** — measurable outcomes as checkboxes
3. **Present to the user.** Show the epic name, executive summary, source documents, and success criteria. Ask for confirmation.
4. **Wait for approval.** Adjust as directed. Do not proceed to decomposition until the user approves the scope.

## Stage 2: Decompose

1. Using the EPIC_GUIDE methodology, identify natural backlog item boundaries in the scoped work.
2. **Present the proposed breakdown in-console** — a table or structured list showing each item's name, type, estimated effort, and one-line purpose:

   ```
   | # | Item | Type | Effort | Purpose |
   |---|------|------|--------|---------|
   | 1 | ... | ... | ... | ... |
   ```

   Include a brief note on the critical path and which items can run in parallel.
3. **Offer a mental-model checkpoint.** After presenting the decomposition and before asking for approval, offer one question-led HTML explanation (via ``my-mental-model``) that reconnects the product intent, the proposed slicing, and code reality so the user can judge the breakdown. Skip the offer when your invocation carries the NON-INTERACTIVE orchestration marker — do not stop for it and do not let an orchestrator accept it for the user. Declining changes nothing; the stage proceeds identically.
4. **Wait for approval.** Adjust item boundaries, ordering, or scope as directed. Do not proceed to writing items until the user approves the decomposition.

## Stage 3: Write Items

1. Think through carefully:
   - **Dependencies** between items — what must complete before what?
   - **Required Reading** per item — which source documents carry intent relevant to each specific item? Different items may reference different subsets. Not every item needs Required Reading.
   - **Epic Strategy** — value delivery path, critical path, decomposition rationale.
   - **De-risking** — does any item rest on an unverified bet about how something behaves? If so, consider surfacing a ``my-spike`` (confirm a known assumption with throwaway code) or ``my-learning-test`` (map an unfamiliar surface with kept tests) as an early item or first phase, so the bet is tested before dependents build on it.
2. **Run the product-lens over the decomposition.** The epic is where scope first narrows, so an independent check re-derives the point here. Spawn a fresh-context `default` subagent whose entire instruction set is `../../../.codex/scripts/product-lens.md` (pack source: `claude-pack/scripts/product-lens.md`). SOURCES = the repo's durable product statements (`README`, `docs/`, `.project/adr/`, `.project/product/` index-first) plus any owner-verbatim in the source concept; WORK = the proposed decomposition and each item's one-line purpose. It checks the slicing both directions — does any item narrow or contradict the point, and does the set omit an obligation the point requires? Record its verdict (the product-lens ledger block, format in that spec's §3) in the epic file under a **Product-Lens** heading. An unresolved owner/`[HARD]` contradiction blocks the epic until dispositioned; a lower-authority or can't-find finding needs a visible disposition and may proceed. An unresolved epic finding is not cleared by item creation: `_my_spec` carries it into each affected item's per-item ledger, which is the ledger downstream ship gates read.
3. Write the full backlog items into the epic file, following the item template in `EPIC_GUIDE.md`. Fill in Epic Strategy, the dependency graph, risks, and timeline sections.
4. Add an entry to `.project/backlog/BACKLOG.md` following the existing format (priority, status, estimate, brief description, items list with checkboxes).
5. Present the completed epic to the user.

User-provided arguments are supplied when this skill is invoked.

