# Spec: New Project Templates (D1.1)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-01 19:53:02 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** `.project/backlog/epic_architecture-structure.md` (EPIC-ARCH-001, D1.1)

---

## Business Goals

### Why This Matters

The architecture redesign introduces 4 new structured registries (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md) and 2 new work management files (EPIC_GUIDE.md, epic_template.md) that do not exist today. These files are the structured homes for information roles 2-6 defined in the information architecture. Without templates for them, `cmd_init()` cannot create them (D1.4), commands cannot read/write them (Epic 3), and the PM engine cannot parse them (Epic 4).

### Success Criteria

- [ ] 6 new template files exist in `project_templates/`
- [ ] Each template is valid markdown and works in the empty state (no entries, no placeholder data that looks like real content)
- [ ] Entity formats exactly match information-architecture.md section 3
- [ ] EPIC_GUIDE.md content covers the required topics from workflows.md sections 2.1 and 3.6

### Priority

On the critical path. Gates D1.4 (`cmd_init()` rewiring). Can proceed in parallel with D1.2 (revised templates) and D1.5 (frontmatter schemas).

---

## Problem Statement

### Current State

The architecture defines 6 new files that target projects need but no templates exist for them. The `project_templates/` directory has 11 files, none of which cover these new artifacts. The entity formats (DI-XXX, AD-XXX, PR-XXX, SV-XXX) are fully specified in information-architecture.md section 3 but have no concrete template implementation.

### Desired Outcome

6 template files in `project_templates/` ready for D1.4 to wire into `cmd_init()`. Each template produces a valid, useful empty-state document when installed.

---

## Scope

### In Scope

- Creating 6 new `.template` files in `project_templates/`
- Defining the exact markdown structure for each template
- Ensuring empty-state validity (AP-1: design for 0, 1, N)
- Matching entity formats to information-architecture.md section 3

### Out of Scope

- Wiring templates into `cmd_init()` or `replicate_setup.sh` (D1.4)
- Revising existing templates (D1.2)
- Deleting templates per D1.3 decisions (D1.4)
- Updating `data/traceability_matrix.csv` schema (D1.4 — existing file, not a new template)
- Building parsers or the PM engine (Epic 4)
- Writing the full prose content of EPIC_GUIDE.md (implementation concern)

### Edge Cases & Considerations

- Templates MUST NOT contain example data that could be mistaken for real entries. Use HTML comments or clearly marked format examples instead.
- The `epic_template.md.template` is treated like other templates — it is a file in `project_templates/` and D1.4 decides how `cmd_init()` installs/exposes it.
- REQUIREMENTS.md.template SHOULD include a brief note that it replaces the former LOCAL_GUIDE.md (per D1.3 FR-2 downstream impact).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and architecture documents unless marked [INFERRED].

#### FR-1: `KNOWLEDGE.md.template`

**Destination:** `knowledge/KNOWLEDGE.md` (user-owned)
**Entity format:** DI-XXX entries per information-architecture.md section 3 Role 2.

Required entity fields:
- **Source**: approved research doc, user note, authority source, or `work-item:{WI-XXX}/{artifact}`
- **Rationale**: (optional — present only for inline-captured insights)
- **Context**: 1-3 sentences
- **Model implications**: what models must capture
- **Analysis implications**: what analyses this enables or requires
- **Status**: captured | addressed | superseded
- **Superseded-by**: (only when status = superseded)
- **Supersedes**: (when this insight replaces an earlier one)

Empty-state: Document header, purpose description, entity format example in an HTML comment (not a real entry), no data rows.

#### FR-2: `ARCHITECTURE.md.template`

**Destination:** `project/ARCHITECTURE.md` (user-owned)
**Entity format:** AD-XXX entries per information-architecture.md section 3 Role 5.

Required sections:
- **Domain Decomposition** — prose section describing how the system is decomposed into model packages
- **Package Organization** — table with columns: Package, Purpose, Domain Scope, Dependencies
- **Key Decisions** — AD-XXX entries, each with: Decision, Rationale, Date, Status (active | revised | superseded)

Empty-state: Section headers with brief placeholder text explaining what goes in each section. Package Organization table with header row only. Key Decisions section with format example in an HTML comment.

#### FR-3: `REQUIREMENTS.md.template`

**Destination:** `project/REQUIREMENTS.md` (user-owned)
**Entity format:** PR-XXX table per information-architecture.md section 3 Role 4.

Required table columns: ID, Requirement, Source, Enforcement, Validation Method.

The template MUST include:
- A brief introductory note explaining this file extends MODELING_GUIDE.md with project-specific rules
- A note that this file replaces the former LOCAL_GUIDE.md (per D1.3 FR-2)
- The Requirements table with header row only (no example rows)

Empty-state: Header, introductory text, table with header row and separator only.

#### FR-4: `VALIDATION_MATRIX.md.template`

**Destination:** `project/VALIDATION_MATRIX.md` (user-owned)
**Entity format:** SV-XXX table per information-architecture.md section 3 Role 6.

Required table columns: ID, Description, Type, Mechanism, Expected, Tolerance, Source, Test, Status.

The template SHOULD include brief definitions of:
- **Verification types**: reasonableness, baseline, physical, relationship, rollup
- **Verification mechanisms**: model, test, manual

Empty-state: Header, type/mechanism reference, table with header row and separator only.

#### FR-5: `EPIC_GUIDE.md.template`

**Destination:** `work/EPIC_GUIDE.md` (tool-owned)
**Content type:** Prose reference document (no entity format — this is guidance, not a registry).

Required topics (derived from workflows.md sections 2.1 and 3.6):
- **Scale taxonomy**: Trivial, Standard, Epic — definitions, when to use each, routing behavior
- **Goldilocks principle**: Right-sizing work items — not too big (epic), not too small (trivial), just right (standard)
- **Epic decomposition process**: How to break down large scope into standard work items with clear boundaries
- **Epic file structure**: What goes in `work/backlog/epic-{name}.md` — frontmatter fields, recommended body sections (executive summary, context, per-item breakdowns, sequencing, risks)
- **Anti-patterns**: Common decomposition mistakes (items too coupled, items too granular, missing sequencing, etc.)
- **Relationship to BACKLOG.md**: BACKLOG.md tracks summary status; epic files hold decomposition detail

Deliverables: The template MUST cover all 6 topics above. The implementation decides exact prose, length, and organization.

#### FR-6: `epic_template.md.template`

**Destination:** `work/backlog/epic-{name}.md` (user-owned)
**Entity format:** YAML frontmatter per workflows.md section 3.6.

Required YAML frontmatter fields:
```yaml
---
Status: draft | active | completed
Priority: P0 | P1 | P2 | P3
Goal: G-XXX
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

Required body sections (headers only, with brief placeholder guidance):
- Executive Summary
- Context
- Success Criteria
- Risks
- Items (per-item breakdowns)
- Sequencing

Empty-state: Frontmatter with placeholder values, section headers with brief guidance text explaining what each section should contain.

### Non-Functional Requirements

- **NFR-1**: [INFERRED] Templates MUST follow the naming convention `{NAME}.md.template` consistent with existing templates in `project_templates/`.
- **NFR-2**: [INFERRED] Templates MUST be pure markdown (with YAML frontmatter where specified). No template variable substitution syntax — these are copied as-is by `cmd_init()`.

---

## Acceptance Criteria

### Core Functionality
- [ ] 6 files exist in `project_templates/`: `KNOWLEDGE.md.template`, `ARCHITECTURE.md.template`, `REQUIREMENTS.md.template`, `VALIDATION_MATRIX.md.template`, `EPIC_GUIDE.md.template`, `epic_template.md.template`
- [ ] KNOWLEDGE.md.template contains the full DI-XXX entity format specification with all 8 fields
- [ ] ARCHITECTURE.md.template contains Domain Decomposition, Package Organization, and Key Decisions sections with AD-XXX format
- [ ] REQUIREMENTS.md.template contains PR-XXX table with all 5 columns and LOCAL_GUIDE.md replacement note
- [ ] VALIDATION_MATRIX.md.template contains SV-XXX table with all 9 columns and type/mechanism definitions
- [ ] EPIC_GUIDE.md.template covers all 6 required topics (scale taxonomy, Goldilocks principle, decomposition process, epic file structure, anti-patterns, BACKLOG.md relationship)
- [ ] epic_template.md.template has correct YAML frontmatter schema and all 6 body sections

### Empty-State Validity
- [ ] No template contains example data that could be mistaken for real entries
- [ ] All tables have header rows but no data rows
- [ ] Format examples use HTML comments or clearly demarcated reference blocks
- [ ] Each template is immediately usable when installed (no broken markdown, no incomplete sections)

### Quality & Integration
- [ ] Entity formats match information-architecture.md section 3 exactly (field names, allowed values, field descriptions)
- [ ] YAML frontmatter in epic_template.md matches workflows.md section 3.6 exactly (field names, allowed values)
- [ ] Existing tests continue to pass (`uv run pytest tests/`)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.1)
- **Dependency:** `.project/active/template-evaluation-decisions/spec.md` (D1.3 — approved)
- **Architecture:** `.project/concepts/architecture-redesign/information-architecture.md` section 3 (entity formats)
- **Workflows:** `.project/concepts/architecture-redesign/workflows.md` sections 2.1, 3.6 (EPIC_GUIDE content, epic frontmatter)
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` section 1.1
- **Unblocks:** D1.4 (`cmd_init()` rewiring)

---

**Next Steps:** Given MEDIUM complexity (6 files, each with specific format requirements drawn from architecture docs), proceed to `/_my_design` to settle the exact template content before implementation.
