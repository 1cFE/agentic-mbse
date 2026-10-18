---
name: my-close
description: Archive a completed work item or epic to completed/ and update tracking files (CURRENT_WORK.md, CHANGELOG.md, BACKLOG.md). Use when work is done and ready to be moved out of active development.
---

Generated from `claude-pack/commands/_my_close.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Close Command

**Purpose:** Archive a completed work item or epic to `completed/` and update all tracking files
**Input:** Item name (folder in `active/`) or epic name (file in `backlog/`) via `User-provided arguments are supplied when this skill is invoked.`
**Output:** Archived artifacts in `completed/`, updated CURRENT_WORK.md, CHANGELOG.md, and (for epics) BACKLOG.md

## Overview

You are an archive utility. Your job is to move completed work out of `active/` and `backlog/`, update the project's tracking files, record what shipped, and file the decisions that emerged during implementation before their context is archived. You do not evaluate or certify — that is ``my-audit``. You archive and update the books.

When invoked:
- If `User-provided arguments are supplied when this skill is invoked.` names an item or epic, resolve the scope and start.
- If no argument, ask what to close.

## Step 1: Resolve Scope

Determine whether the argument is a work item or an epic:
- If `.project/active/{arg}/` exists → **item scope**.
- If `.project/backlog/epic_{arg}.md` exists → **epic scope**. Try both `epic_{arg}.md` and `{arg}.md` if the user included the prefix.
- If both match → ask the user which scope they mean.
- If neither → report what you checked and ask for a valid name.

## Step 2: Gather State

**Item scope:**
1. Read `spec.md`, `plan.md`, and `audit.md` from `active/{item}/` (skip any that don't exist).
2. Check audit status: look for the `**Verdict:**` field in `audit.md`. Note whether it says "Certify," "Needs Work," or is absent.
3. Find the parent epic: check the spec's Related Artifacts section for an epic reference. If not found, grep `.project/backlog/epic_*.md` for the item name. If no parent epic, note it as standalone.
4. **Scan for records to file** — one pass, three destinations. Read `plan.md` deviation/implementation notes, `audit.md` findings, and `product-lens.md` if present. For each candidate, ask which of three homes it belongs in:
   - **A decision we made, and the reasoning a future challenge re-derives against** → `.project/adr/`. Apply the density bar in `.project/adr/README.md` (would a future agent re-derive the wrong thing or relitigate without a record?). A `product-lens.md` finding disposed as an **intended contract change** (or a smell-7 change of who owns an invariant) is a decision to record via `adr.sh new`; if it changes a recorded decision, also `adr.sh amend|supersede` the affected active entry and set owner-ratified provenance (not the default `[AGENT]`). The ledger finding must cite the entry id. No other product-lens disposition files an ADR.
   - **A promise the product now makes** → `.project/product/`. Did this item implement (or materially change) a product promise a cold agent could reasonably miss or undo? Bar: the density standard in `.project/product/README.md` (major use case, public surface, or cross-cutting contract — judgment, not inventory). A material change to an already-recorded promise is a `supersede`/`amend` candidate, not a new entry.
   - **How a component, tool, or data format actually behaves, discovered while working** → `.project/execution/ENTRIES.md`. Apply the density bar in `.project/execution/README.md` (would a future agent spend real time rediscovering it?). The fact is the behavior, not the reasoning behind a decision — a decision record may sit nearby, but they are different records.
   When the session that runs close did the implementation, also ask that session directly whether it encountered a behavior worth recording — the artifacts do not always carry this class.
   Most items yield nothing in any of the three categories. That is the common case; close proceeds on "none" — this is never a gate.

**Epic scope:**
1. Read the epic file. Extract child items from the Backlog Items section — use each item's `**Location**:` field to get the folder name.
2. For each child item, check whether it is in `active/` (needs archiving) or already in `completed/` (skip).
3. For each active child, read `audit.md` and note certification status.
4. **Read the epic's own Product-Lens block.** If it records an open `BLOCK` nobody came back to, mention it in the summary. It does not stop the close.

## Step 3: Confirm

Present a summary to the user. Include:

- What will be archived (source → destination paths).
- What tracking files will be updated.
- **Records to file — or none** — the candidate entries from the record scan, grouped by destination (`.project/adr/`, `.project/product/`, `.project/execution/ENTRIES.md`), or "none found." For a decision that is a workaround against another repo's behavior, note the placement: the ruling entry files in the repo that must uphold it, plus a local pointer entry (see `.project/adr/README.md`); if that repo is unreachable, file the pointer and surface the gap.
- **Certification warnings** — if any item has no audit or a "Needs Work" verdict, flag it visibly. Example: `⚠️ {item} has no audit certification.`
- **Open product-lens findings** — if an item's `product-lens.md` records a `BLOCK` that no later block resolves, say so plainly. A missing ledger is worth a mention too. Neither stops the close; the user decides what to do about it.
- For epic scope: a list of child items showing which will be archived and which are already in `completed/`.

**Wait for user confirmation. Do not proceed without it.**

## Step 4: Execute

After confirmation, execute in this order:

### 4a. Read data for CHANGELOG

Before moving anything, read the data you need for the CHANGELOG entry from the item's artifacts (spec Problem section, spec Created date, list of artifacts present). Once `git mv` runs, the source paths are gone.

### 4b. File records

For each approved candidate from the confirm step, file it in its destination:

- **Decision** → `.project/scripts/adr.sh new <slug>`, fill in the body, set provenance and seams.
- **Promise** → `.project/scripts/product.sh new <slug>` (or `supersede`/`amend` for a material change to a recorded promise), fill Promise/Authority/Evidence/Scope, set provenance and surfaces, then stamp `product.sh check <id>` — `new` leaves `checked` null, and filing an audited item is the verification.
- **Execution fact** → append to `.project/execution/ENTRIES.md` using the format in `.project/execution/README.md`. No script, no id — just the tagged heading, **Fact**, and **Evidence**.

In Authority / Evidence, cite the item's artifacts at their post-close `completed/$(date +%Y%m%d)_{item}/` paths, since the archive is about to move them. Do all filing **before** archiving, while the source artifacts still exist at their `active/` paths for reading. If a script is missing (repo not re-initialized), note the gap; don't hand-mint ids.

### 4c. Archive

Use `git mv` for all moves:
- **Item scope:** `git mv .project/active/{item} .project/completed/$(date +%Y%m%d)_{item}`
- **Epic scope:** For each active child item, `git mv` to `completed/`. Then `git mv .project/backlog/epic_{name}.md .project/completed/$(date +%Y%m%d)_epic_{name}.md`.

### 4d. Update tracking files

**CURRENT_WORK.md:**
- Remove the item (or child items) from the Active Work section.

**CHANGELOG.md** (`completed/CHANGELOG.md`):
- Add an entry using the established format, **at the top of the file, above the newest existing entry**. The CHANGELOG is ordered newest-first and session boot reads the first five entries, so an entry appended at the bottom is invisible to it. Auto-populate:
  - **Type**: "Item" or "Epic"
  - **Duration**: computed from the spec's `Created` date to today
  - **Summary**: the first 2-3 sentences of the spec's Problem section, reframed as what was accomplished
  - **Deliverables**: list the artifacts that exist in the item folder (spec.md, design.md, plan.md, audit.md, plus code deliverables from the spec)
- For epic scope, write one entry summarizing the entire epic, not per-child entries.

**Parent epic** (item scope only):
- If the item belongs to an epic, mark the item's success/done-state checkboxes `- [x]` in the epic file. If all success criteria pass, append ✅ to the item heading.
- Check if all epic items are now complete. If so, suggest: "All items in {epic} are now complete. Run ``my-close` {epic}` to archive the epic."

**BACKLOG.md** (epic scope only):
- Update the epic's entry: strikethrough the heading, add ✅, change status to `Complete (YYYY-MM-DD)`, add `Archived to: .project/completed/{path}`.

### 4e. Commit

Stage all changes from steps 4a–4d and commit. Message format:

```
Close {item|epic}: {one-line summary}

Archived to completed/{dest}. [Brief note of any records filed.]
```

### 4f. Report

Show the user what was done: what was archived, what files were updated, and any next steps (e.g., suggesting epic close if all items are done).

---

**Related Commands:**
- Before close: ``my-audit`` to certify
- After close: ``my-pre-pr`` when the item is shippable on its own — otherwise once at the end of the epic
- After close (epic items done): ``my-close` {epic}` to archive the epic
- Session context: ``my-wrap-up`` to persist session state

**Last Updated**: 2026-09-10 — consolidated decision and promise scans into one record scan with three destinations (adr, product, execution); removed the per-item learnings field from CHANGELOG.

User-provided arguments are supplied when this skill is invoked.

