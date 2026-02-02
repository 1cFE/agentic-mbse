# Spec: Status Field Semantics Clarification

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02 16:57:17 UTC
**Complexity:** LOW
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (PM Script Engine)

---

## Business Goals

### Why This Matters

During the D4.2 (state derivation) spec process, an ambiguity surfaced in the architecture concept docs: the `Status` field in design.md and plan.md reads as "document readiness" (is the draft finalized?) but should mean "has the work described in this artifact been completed?" This ambiguity caused an agent to incorrectly conclude the design was underspecified, wasting investigation time. If left uncorrected, it will confuse future implementors of D4.4 (operations) — specifically `close-item`, which is the first operation in the build order and needs to know it touches all three artifact Status fields.

### Success Criteria

- [ ] A reader of frontmatter-schemas.md understands that design.md `Status: complete` means "the design has been implemented," not "the design document is finalized"
- [ ] The `close-item` operation description in the epic explicitly states it sets Status on spec.md, design.md, and plan.md
- [ ] `/audit-models` offers to close a work item when a work-item audit passes — no direct frontmatter editing by any command

### Priority

Should be completed before D4.4 implementation begins (close-item is operation #1 in the build order).

---

## Problem Statement

### Current State

The architecture concept docs contain an ambiguity about what `Status` means in stage artifacts:

- **frontmatter-schemas.md § 3.2** (design.md): Description says "Stage-level status (not the work item status — that's in spec.md)." This implies document readiness.
- **frontmatter-schemas.md § 3.3** (plan.md): Description says "Stage-level status." Same implication.
- **workflows.md § 3.1**: "Stage-level Status values: design.md and plan.md use `draft | complete`. These are simpler than spec.md's work-item-level states because stage artifacts don't independently pause or fail." Again reads as document readiness — "is this draft done?"
- **workflows.md § 3.5** (close flow): Does not mention updating design.md or plan.md Status. Only describes directory move + BACKLOG.md update.
- **PM engine epic D4.4** (close-item): Describes moving the directory and updating BACKLOG.md, but does not mention setting Status fields on any artifact.
- **No command sets any Status field post-creation**: spec.md is created with `Status: active` and never updated. design.md and plan.md are created with `Status: draft` and never updated.
- **`/audit-models`**: Can confirm a work item is complete but has no mechanism to trigger archival.

### Desired Outcome

Consistent semantics: `Status` in all artifacts tracks whether the **work described in the artifact** has been completed, not whether the document text is finalized. All Status mutations go through the `close-item` AP-7 script (preserving AP-7: scripts handle state mutations). `/audit-models` offers to trigger close when a work-item audit passes.

---

## Scope

### In Scope

Six files need targeted edits:

| File | Change |
|------|--------|
| `.project/concepts/architecture-redesign/frontmatter-schemas.md` | Clarify Status descriptions for design.md and plan.md; add DD-4 |
| `.project/concepts/architecture-redesign/workflows.md` § 3.1 | Update "Stage-level Status values" paragraph |
| `.project/concepts/architecture-redesign/workflows.md` § 3.5 | Add Status field updates to close flow description |
| `.project/backlog/epic_architecture-pm-engine.md` D4.4 | Update close-item operation to include all 3 Status updates |
| `claude/commands/audit-models.md` | Add AskUserQuestion → close-item offer after successful work-item audit |
| `claude/commands/backlog.md` | Clarify that close-item script handles Status updates |

### Out of Scope

- Changing the allowed Status enum values (`draft | complete` stays for design.md/plan.md; the full set stays for spec.md)
- Adding new stages or changing stage detection logic (settled in D4.2 spec)
- Having `/implement-model` set plan.md Status mid-implementation (checkboxes track progress)
- Changes to the D4.2 state derivation spec (already correct — it checks spec.md Status for override, uses file existence for stages)
- Having `/status close` independently set Status fields (it calls `close-item`, which handles it)

---

## Requirements

### Concept Doc Updates

#### FR-1: frontmatter-schemas.md — Clarify Status Descriptions

The Description column for `Status` in design.md (§ 3.2) and plan.md (§ 3.3) MUST be updated to clarify that `complete` means the work described in the artifact has been completed, not that the document is finalized.

Current (design.md § 3.2):
> Stage-level status (not the work item status — that's in spec.md).

Updated:
> Whether the work described in this artifact has been completed — not whether the document text is finalized. `draft` = work in progress; `complete` = work done (design implemented, or plan executed). Set to `complete` by the `close-item` AP-7 operation or by `/audit-models` confirmation. Not independently set by commands that create these artifacts.

The same pattern SHOULD apply to plan.md (§ 3.3).

A new design decision DD-4 MUST be added to § 2:

> **DD-4: Status Tracks Work Completion, Not Document Readiness**
>
> **Decision**: The `Status` field in design.md and plan.md tracks whether the work described in the artifact has been completed, not whether the document text is finalized as a draft. `draft` means work is in progress; `complete` means the work is done.
>
> **Rationale**: design.md Status = `complete` means the design has been implemented and verified, not that the design document was approved. plan.md Status = `complete` means the plan has been fully executed, not that the plan text was finalized. This aligns all three artifacts on a consistent semantic: Status tracks work state. The richer enum on spec.md (`paused`, `abandoned`, `failed`) remains because those are work-item-level states that affect the whole item — stage artifacts don't independently pause or fail.
>
> **Who sets it**: The `close-item` AP-7 operation sets all three artifacts' Status fields atomically as part of the archive operation. No command edits these fields directly — AP-7 scripts handle state mutations.

#### FR-2: workflows.md § 3.1 — Clarify Stage-Level Status Paragraph

The paragraph beginning "Stage-level Status values" MUST be updated to replace the document-readiness framing.

Current:
> Stage-level Status values: design.md and plan.md use `draft | complete`. These are simpler than spec.md's work-item-level states because stage artifacts don't independently pause or fail — the work item does (via spec.md). A completed design that needs revision during backward navigation (§ 2.3) returns to `draft`; the revision history lives in git.

Updated:
> Stage-level Status values: design.md and plan.md use `draft | complete`. These track whether the work described in the artifact has been completed — `draft` means work is in progress, `complete` means the work is done (design implemented, plan executed). They are simpler than spec.md's work-item-level states because stage artifacts don't independently pause or fail — the work item does (via spec.md). Status fields are set to `complete` by the `close-item` AP-7 operation as part of the archive flow; commands that create these artifacts set them to `draft`. A completed design that needs revision during backward navigation (§ 2.3) returns to `draft`; the revision history lives in git.

#### FR-3: workflows.md § 3.5 — Add Status Updates to Close Flow

The close flow description MUST be updated to include Status field updates as part of the `close-item` script execution. The script description currently lists:

1. Move `work/active/{WI-XXX}_{name}/` → `work/completed/YYYYMMDD_{WI-XXX}_{name}/`
2. Update BACKLOG.md status to completed

It MUST be extended to:

1. Set spec.md `Status: completed`
2. Set design.md `Status: complete` (if file exists)
3. Set plan.md `Status: complete` (if file exists)
4. Set spec.md `Updated:` to today's date
5. Move `work/active/{WI-XXX}_{name}/` → `work/completed/YYYYMMDD_{WI-XXX}_{name}/`
6. Update BACKLOG.md status to completed, re-render body

Status updates MUST happen before the directory move so the archived artifacts contain their final state.

### Epic Updates

#### FR-4: Update close-item Operation in PM Engine Epic

The close-item entry in the epic's D4.4 operation inventory MUST be updated to reflect the expanded scope. Specifically, the "What it does" column should include setting Status on all three artifacts before the directory move. The atomicity guarantee still holds — all writes happen or none do.

### Command Updates

#### FR-5: `/audit-models` — Offer Close on Successful Work-Item Audit

When performing a **work item audit** (not a project audit), if the audit verdict is positive (all MR-XXX requirements satisfied, all spec acceptance criteria met, Levels 1-3 passing), the command MUST use `AskUserQuestion` to ask whether the user wants to close the work item.

If the user confirms, the command MUST call:
```
agentic-mbse pm close-item <WI-XXX>
```

Then proceed to the project document review trigger questions (same as `/backlog close` and `/status close`).

If the user declines, the command proceeds normally (report saved, no state change).

This MUST NOT fire for project audits or for work-item audits that find failures.

#### FR-6: `/backlog close` — Clarify Script Handles Status

The `/backlog close` process description SHOULD add a note clarifying that the `close-item` script handles setting Status fields on all artifacts. The command does not need to set them independently — the script does it atomically.

Current description of close-item (line 93):
> The script moves `work/active/{WI-XXX}_{name}/` to `work/completed/YYYYMMDD_{WI-XXX}_{name}/` and updates BACKLOG.md status.

Updated:
> The script sets all artifact Status fields to their completion values (spec.md → `completed`, design.md → `complete`, plan.md → `complete`), moves the directory to `work/completed/YYYYMMDD_{WI-XXX}_{name}/`, and updates BACKLOG.md status. All mutations are atomic.

---

## Acceptance Criteria

### Documentation
- [ ] frontmatter-schemas.md § 3.2 and § 3.3 Status descriptions updated
- [ ] frontmatter-schemas.md DD-4 added
- [ ] workflows.md § 3.1 "Stage-level Status values" paragraph updated
- [ ] workflows.md § 3.5 close flow includes Status updates on all 3 artifacts
- [ ] PM engine epic D4.4 close-item description includes all 3 Status updates

### Commands
- [ ] `/audit-models` includes AskUserQuestion → close-item offer after successful work-item audit
- [ ] `/audit-models` does NOT offer close for project audits or failed work-item audits
- [ ] `/backlog close` description clarifies close-item handles Status fields
- [ ] `/status close` description is consistent (already calls close-item; verify wording)

### Consistency
- [ ] No command directly edits spec.md, design.md, or plan.md Status fields for state transitions — all go through AP-7 scripts
- [ ] The word "draft" in design.md/plan.md context is never described as "document readiness" in any concept doc
- [ ] All references to close-item's behavior are consistent across workflows.md, the epic, and the commands

---

## Related Artifacts

- **D4.2 spec:** `.project/active/d4.2-state-derivation/spec.md` (no changes needed — already correct)
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.4 section needs update)
- **Concept docs:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`, `workflows.md`
- **Commands:** `claude/commands/audit-models.md`, `claude/commands/backlog.md`, `claude/commands/status.md`
