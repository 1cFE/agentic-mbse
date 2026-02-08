# Spec: Template Evaluation Decisions (D1.3)

**Status:** Approved
**Owner:** Reid Westwood
**Created:** 2026-02-01 19:37:52 UTC
**Complexity:** LOW
**Branch:** revamp-architecture
**Epic:** `.project/backlog/epic_architecture-structure.md` (EPIC-ARCH-001, D1.3)

---

## Business Goals

### Why This Matters

Four existing project templates are not explicitly addressed in the architecture redesign. Their disposition — keep, merge, or delete — must be resolved before D1.1 (new templates), D1.2 (revised templates), and D1.4 (`cmd_init()` rewiring) can proceed. This is the first deliverable in Epic 1 because it determines what templates exist.

### Success Criteria

- [ ] Each of the 4 templates has a documented disposition with rationale
- [ ] Traceability matrix CSV schema delta is specified exactly (column adds, removes, renames)
- [ ] Downstream impacts are identified (which files in D1.1/D1.2/D1.4/D1.7 are affected by each decision)

### Priority

Gate for all other Epic 1 deliverables. On the critical path.

---

## Problem Statement

### Current State

Four templates exist in `project_templates/` that the architecture redesign documents do not place:

| Template | Installed by `cmd_init()`? | Used in fusion-tea? | Referenced by commands? |
|----------|---------------------------|---------------------|------------------------|
| `data/assumption_register.md.template` | No (dead file) | No (never created) | Yes — `design-model.md`, `implement-model.md` |
| `LOCAL_GUIDE.md.template` | Yes (user-owned, `modeling_pm/LOCAL_GUIDE.md`) | Template-only (no real content) | No commands; has tests in `test_cli.py` |
| `RAW_LEARNINGS.md.template` | Yes (user-owned, `modeling_pm/learnings/RAW_LEARNINGS.md`) | Template-only (no entries) | No commands directly |
| `data/traceability_matrix.csv` | No (not installed by any code path) | No (`data/` is empty) | Yes — `implement-model.md` references it |

### Desired Outcome

Each template has a clear disposition that the rest of Epic 1 can act on without further discussion.

---

## Scope

### In Scope

- Disposition decision for each of the 4 templates
- Traceability matrix CSV schema specification (exact column delta)
- Identification of downstream impacts on D1.1, D1.2, D1.4, D1.7, and Epic 3

### Out of Scope

- Modifying any template files (D1.1, D1.2)
- Modifying `cmd_init()`, `replicate_setup.sh`, or tests (D1.4, D1.7)
- Modifying commands that reference assumption_register (Epic 3 — commands are refactored there)

---

## Requirements

### FR-1: `assumption_register.md.template` — DELETE

**Disposition:** Delete the template file from `project_templates/data/`.

**Rationale:**
- The template is a dead file — no code path in `cmd_init()` or `replicate_setup.sh` installs it
- fusion-tea never created the file despite commands referencing it
- The architecture provides two better homes for assumption content:
  - **Per-work-item assumptions** belong in `spec.md` (ephemeral, scoped to the work item)
  - **Durable assumptions that become project rules** are promoted to PR-XXX in `project/REQUIREMENTS.md` via the requirement promotion path (information-architecture.md § 3 Role 4)
- The assumption_register's entity format (A001, uncertainty percentages, validation needed) overlaps with but is less structured than REQUIREMENTS.md's PR-XXX format (ID, Requirement, Source, Enforcement, Validation Method)

**Downstream impacts:**
- D1.1/D1.2: None (template is not being created or revised)
- D1.4: Remove the dead file from `project_templates/data/` during the rewiring
- Epic 3: `design-model.md` and `implement-model.md` references to `assumption_register.md` MUST be removed during command refactoring. Commands SHOULD guide assumptions into spec.md (ephemeral) or the promote-requirement flow (durable)

### FR-2: `LOCAL_GUIDE.md.template` — MERGE into REQUIREMENTS.md template, then DELETE

**Disposition:** Merge the concept into the new `REQUIREMENTS.md.template` (D1.1), then delete `LOCAL_GUIDE.md.template`.

**Rationale:**
- LOCAL_GUIDE's purpose is "project-specific patterns, validated findings, and customizations" — this is exactly what `project/REQUIREMENTS.md` is for (PR-XXX entries: project-specific rules)
- LOCAL_GUIDE's three sections map to REQUIREMENTS.md sub-types:
  - "Validated Patterns" → PR-XXX modeling patterns
  - "Project-Specific Guidance" → PR-XXX structural/documentation/domain rules
  - "Lessons Learned" → process knowledge stays in `work/learnings/RAW_LEARNINGS.md`; domain knowledge goes to `knowledge/KNOWLEDGE.md` as DI-XXX
- fusion-tea's LOCAL_GUIDE contains only template boilerplate — no real content to migrate
- Keeping both LOCAL_GUIDE and REQUIREMENTS.md would create ambiguity about where project-specific rules belong

**Downstream impacts:**
- D1.1: `REQUIREMENTS.md.template` SHOULD include a brief note that it replaces the former LOCAL_GUIDE.md (helps existing users)
- D1.4: Remove `LOCAL_GUIDE.md.template` from `USER_OWNED_TEMPLATES`; delete the template file
- D1.7: Remove `TestLocalGuide` class from `test_cli.py` (tests creation at `modeling_pm/LOCAL_GUIDE.md` and skip-on-re-init behavior — both obsolete)
- D1.6 (fusion-tea): Delete the empty `modeling_pm/LOCAL_GUIDE.md` during migration (no content to transfer)

### FR-3: `RAW_LEARNINGS.md.template` — KEEP, update destination path

**Disposition:** Keep the template. Update its installation destination from `modeling_pm/learnings/RAW_LEARNINGS.md` to `work/learnings/RAW_LEARNINGS.md`.

**Rationale:**
- The architecture explicitly places learnings under `work/` (information-architecture.md § 2 file structure)
- RAW_LEARNINGS.md serves a distinct purpose (append-only process knowledge log) that is not subsumed by any new artifact
- The template content is adequate — no revision needed beyond what D1.2 might do for path references

**Downstream impacts:**
- D1.2: Update internal path references in the template if any point to `modeling_pm/` (current template references `docs/patterns/` and `MODELING_GUIDE.md` — these MAY need updating to `project/MODELING_GUIDE.md` depending on D1.2's scope)
- D1.4: Update `USER_OWNED_TEMPLATES` entry: `("RAW_LEARNINGS.md.template", "work/learnings/RAW_LEARNINGS.md")`

### FR-4: `data/traceability_matrix.csv` — KEEP, update schema, ADD to `cmd_init()` installation

**Disposition:** Keep the template. Update its column schema to match information-architecture.md § 5.3. Add a code path in `cmd_init()` to install it to `data/traceability_matrix.csv`.

**Rationale:**
- The architecture requires this file at `data/traceability_matrix.csv` (information-architecture.md § 5.3)
- The current template exists but is never installed — a gap that D1.4 must close
- The schema must change to support the Knowledge and Requirement columns that the PM engine (Epic 4) and traceability model depend on

**Schema delta:**

| Action | Column | Notes |
|--------|--------|-------|
| Keep | `Element` | Unchanged |
| **Rename** | `Implementation_Location` → `File` | Architecture uses `File` |
| Keep | `Type` | Unchanged |
| **Add** | `Knowledge` | DI-XXX IDs (new — enables direct impact queries) |
| **Add** | `Requirement` | PR-XXX IDs (new — enables requirement coverage checking) |
| Keep | `Source_Type` | Unchanged |
| Keep | `Source_Document` | Unchanged |
| Keep | `Source_Location` | Unchanged |
| **Remove** | `Status` | Not in architecture schema |
| Keep | `Confidence` | Unchanged |
| Keep | `Assumptions` | Unchanged |
| **Rename** | `Date_Created` → `Last_Verified` | Architecture uses `Last_Verified` |

**Resulting header row:**
```
Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified
```

**Downstream impacts:**
- D1.4: Add installation of `data/traceability_matrix.csv` to `data/` directory (user-owned — create once, skip on re-init). Add to `USER_OWNED_TEMPLATES` or handle as a special case since it's CSV not markdown.
- D1.4 (`replicate_setup.sh`): Add equivalent installation
- Epic 4: PM engine parsers (`parser.py`) will parse this exact schema. The `trace-element` operation validates PR-XXX and DI-XXX IDs against REQUIREMENTS.md and KNOWLEDGE.md respectively.

---

## Acceptance Criteria

### Core Decisions
- [ ] `assumption_register.md.template`: disposition is DELETE, rationale documented
- [ ] `LOCAL_GUIDE.md.template`: disposition is MERGE into REQUIREMENTS.md then DELETE, rationale documented
- [ ] `RAW_LEARNINGS.md.template`: disposition is KEEP with path update, new path specified
- [ ] `traceability_matrix.csv`: disposition is KEEP with schema update, exact column delta specified

### Downstream Traceability
- [ ] Each decision identifies impacts on D1.1, D1.2, D1.4, D1.7, and Epic 3
- [ ] The traceability matrix target header row is specified exactly (copy-pasteable into the template)

### Quality & Integration
- [ ] Decisions are consistent with information-architecture.md § 3 (Role 4, Role 6) and § 5.3
- [ ] No orphaned references — every command/test that references a deleted/merged template is identified for later cleanup

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.3)
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 1.3
- **Architecture:** `.project/concepts/architecture-redesign/information-architecture.md` § 3 (Role 4), § 5.3
- **Unblocks:** D1.1 (new templates), D1.2 (revised templates), D1.4 (`cmd_init()` rewiring)

---

**Next Steps:** After approval, proceed to `/_my_design` — though given LOW complexity and the design-decision nature of this deliverable, the spec itself may serve as the decision record. The implementation is carried out by D1.1, D1.2, and D1.4.
