# Spec: YAML Frontmatter Schemas (D1.5)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-01
**Complexity:** LOW
**Branch:** revamp-architecture

---

## Business Goals

### Why This Matters

The YAML frontmatter schemas are the PM engine's input contracts. Epic 4 (PM Engine) must parse structured files deterministically — it needs an authoritative reference for what fields to expect, what values are valid, and what types they are. Without this, the PM engine implementation would need to reverse-engineer schemas from scattered references across workflows.md, information-architecture.md, and existing templates.

D1.5 is also a dependency for D1.4 (`cmd_init()` rewiring), which installs templates that carry these schemas.

### Success Criteria

- [ ] All 6 schemas documented with exact field names, types, and allowed values
- [ ] Each schema has a concrete example
- [ ] Document is referenced from implementation-plan.md
- [ ] Three design decisions resolved and documented (ID-in-frontmatter, BACKLOG.md as ID registry, Name field disposition)

### Priority

P0 — on the critical path. Blocks D1.4 and Epic 4.

---

## Problem Statement

### Current State

Frontmatter schemas are sketched in workflows.md § 3.1–3.3 and § 3.6, but:
- They are examples, not contracts — field types and allowed values are implied, not stated
- There is at least one inconsistency: § 3.1 includes `ID: WI-XXX` and `Name` in spec.md frontmatter, but the epic's curated field list (line 146) and the "no-ID-in-frontmatter" decision (D1.6 line 322) exclude them
- No single document consolidates all 6 schemas in one place
- The existing templates (BACKLOG.md.template, epic_template.md.template) have frontmatter that should be verified against the schemas

### Desired Outcome

A single authoritative reference document (`.project/concepts/architecture-redesign/frontmatter-schemas.md`) that:
1. Defines each schema precisely enough for a developer to write a parser
2. Resolves inconsistencies in the source material
3. Serves as the contract between file producers (commands) and consumers (PM engine)

---

## Scope

### In Scope

- Consolidate and formalize all 6 YAML frontmatter schemas from workflows.md
- Resolve the `ID`/`Name` field question for spec.md (resolved: remove both — directory name is identity)
- Document BACKLOG.md's dual role as dashboard and WI-XXX ID registry
- Verify existing templates (BACKLOG.md.template, epic_template.md.template) match the schemas
- Add a cross-reference from implementation-plan.md to the new document

### Out of Scope

- PM engine implementation (Epic 4)
- Modifying existing templates (D1.1/D1.2 already complete — if discrepancies are found, document them for D1.4 to resolve)
- Command prompt design (Epic 3 — commands produce frontmatter, but their prompts are a separate concern)
- Schema validation code (Epic 4)

### Edge Cases & Considerations

- **Optional vs required fields**: Some fields (e.g., `Epic` in spec.md) may be empty for standalone items. The schema must distinguish required-always vs required-when-applicable.
- **Related Artifacts paths**: design.md and plan.md use relative paths (`./spec.md`, `./design.md`). The schema should specify the path convention.
- **BACKLOG.md item `completed` field**: Only present when status = completed. The schema must mark this as conditional.
- **review.md is not a tracked PM stage**: The schema must note this — the PM engine reads review.md for verdict but does not use it for stage detection.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and source documents unless marked [INFERRED].

1. **FR-1**: Define spec.md frontmatter schema with fields: Status, Scale, Epic, Owner, Created, Updated. Allowed Status values: active, paused, abandoned, failed, completed. (Source: epic line 146, workflows.md § 3.1, with ID/Name removed per design decision)
2. **FR-2**: Define design.md frontmatter schema with fields: Status (draft|complete), Created, Updated, Related Artifacts (Spec path). (Source: workflows.md § 3.1)
3. **FR-3**: Define plan.md frontmatter schema with fields: Status (draft|complete), Created, Updated, Related Artifacts (Spec + Design paths). (Source: workflows.md § 3.1)
4. **FR-4**: Define review.md frontmatter schema with fields: Verdict (pass|concerns|fail), Created, Related Artifacts (Design path). (Source: workflows.md § 3.3)
5. **FR-5**: Define BACKLOG.md frontmatter schema with epics list (name, goal, priority, status, file, items list) and standalone list. (Source: workflows.md § 3.6)
6. **FR-6**: Define epic file frontmatter schema with fields: Status (draft|active|completed), Priority, Goal, Created, Updated. (Source: workflows.md § 3.6)
7. **FR-7**: Each schema MUST include a concrete YAML example. (Source: epic exit criteria)
8. **FR-8**: Document that BACKLOG.md is the WI-XXX ID registry — IDs are assigned there by AP-7 scripts, and work item identity is derived from directory name, not frontmatter. (Source: design decisions from scoping)
9. **FR-9**: [INFERRED] Document field type conventions (date format, string conventions, enum values) once at the top, then reference from individual schemas.
10. **FR-10**: [INFERRED] Verify BACKLOG.md.template and epic_template.md.template frontmatter matches the defined schemas; document any discrepancies.

---

## Acceptance Criteria

### Core Functionality

- [ ] All 6 schemas documented in `.project/concepts/architecture-redesign/frontmatter-schemas.md`
- [ ] Each schema specifies: field name, type, required/optional, allowed values, and description
- [ ] Each schema has a concrete YAML example
- [ ] Design decisions documented: no ID/Name in spec.md frontmatter; BACKLOG.md as ID registry; directory-name-as-identity convention
- [ ] BACKLOG.md.template and epic_template.md.template verified against schemas
- [ ] implementation-plan.md updated with reference to frontmatter-schemas.md

### Quality & Integration

- [ ] Existing tests continue to pass (no code changes in this deliverable)
- [ ] Schemas are consistent with workflows.md § 3.1–3.3, § 3.6 (with documented deviations where design decisions override sketches)
- [ ] Field types and allowed values are precise enough to write a YAML parser/validator against

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.5)
- **Source (workflows):** `.project/concepts/architecture-redesign/workflows.md` § 3.1–3.3, § 3.6
- **Source (info arch):** `.project/concepts/architecture-redesign/information-architecture.md` § 2
- **Delta checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 1.6
- **Implementation plan:** `.project/concepts/architecture-redesign/implementation-plan.md`
- **Existing templates:** `project_templates/BACKLOG.md.template`, `project_templates/epic_template.md.template`
- **Design:** `.project/active/frontmatter-schemas/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (though given LOW complexity and the design-artifact nature of this deliverable, design and implementation may merge — the deliverable IS a design document).
