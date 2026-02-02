# Spec: Revised Project Templates (D1.2)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-01 20:40:05 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** `.project/backlog/epic_architecture-structure.md` (EPIC-ARCH-001, D1.2)

---

## Business Goals

### Why This Matters

The 5 existing project templates reference the old `modeling_pm/` directory structure, lack structured entity tables (G-XXX goals, AQ-XXX analysis questions), and contain content that now has dedicated homes in the new architecture. Until these templates are revised, D1.4 (`cmd_init()` rewiring) would install templates that contradict the 4-directory information architecture, and downstream epics (skills, commands, PM engine) would reference a structure that doesn't match reality.

### Success Criteria

- [x] All 5 templates updated to reflect the new directory structure
- [x] OVERVIEW.md has Goals Registry table (G-XXX) and Analysis Questions table (AQ-XXX) matching information-architecture.md section 3 Role 3
- [x] BACKLOG.md has YAML frontmatter structure matching workflows.md section 3.6
- [x] MODELING_GUIDE.md has all reference/how-to sections marked with skill extraction comments identifying the destination skill
- [x] MODELING_PROCESS.md references new directory paths, new documents, and existing commands only
- [x] README.md describes the 4-directory structure and lists only the 9 existing commands

### Priority

On the critical path. Gates D1.4 (`cmd_init()` rewiring) alongside D1.1 (complete). Can proceed in parallel with D1.5 (frontmatter schemas).

---

## Problem Statement

### Current State

The 5 templates were written for the original `modeling_pm/` directory structure:

- **OVERVIEW.md.template** has no structured entity tables (Goals Registry, Analysis Questions). Content that belongs in ARCHITECTURE.md (Technical Approach, Model Organization) and BACKLOG.md (Project Management status) is mixed in.
- **BACKLOG.md.template** uses a priority-bucket markdown format with no YAML frontmatter. Not machine-parseable by the PM engine (Epic 4).
- **MODELING_GUIDE.md.template** mixes pure rules (definitions vs usages, naming conventions) with reference/how-to material (syntax patterns, import examples, testing methodology) that belongs in skills (Epic 2).
- **MODELING_PROCESS.md.template** references `modeling_pm/` paths and only the original commands. Does not mention new documents (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md).
- **README.md.template** describes the old `modeling_pm/` directory structure.

### Desired Outcome

5 revised templates ready for D1.4 to wire into `cmd_init()`. Each template reflects the 4-directory model, uses the correct entity formats, and is valid in the empty state.

---

## Scope

### In Scope

- Revising 5 existing `.template` files in `project_templates/`
- Adding structured entity tables to OVERVIEW.md (Goals Registry, Analysis Questions)
- Adding YAML frontmatter to BACKLOG.md with the machine-readable state structure
- Marking skill-extractable content in MODELING_GUIDE.md with `<!-- SKILL: moves to {skill-name} -->` comments
- Updating all path references from `modeling_pm/` to the new directory structure
- Updating README.md directory description to match 4-directory model

### Out of Scope

- Wiring templates into `cmd_init()` or `replicate_setup.sh` (D1.4)
- Actually extracting content from MODELING_GUIDE.md into skills (Epic 2)
- Adding new commands that don't exist yet to any template (Epic 3 updates templates when commands ship)
- Building YAML frontmatter parsers (Epic 4)
- Creating new templates (D1.1 — complete)
- Deleting templates per D1.3 decisions (D1.4)

### Edge Cases & Considerations

- MODELING_GUIDE.md MUST remain fully functional after marking — no content removed, only annotations added. Commands that currently rely on this content continue to work.
- BACKLOG.md YAML frontmatter MUST use an empty-state example (empty `epics:` and `standalone:` lists) — not example data that looks real. The body should show what a rendered dashboard looks like with explanatory comments.
- OVERVIEW.md sections removed (Technical Approach, Model Organization, Project Management, Key Contacts, Current Status) have homes in other architecture files — this is content migration, not deletion.
- README.md command table lists only the 9 existing commands. A brief note like "Additional commands are available in later toolkit versions" is acceptable but no command-by-command planned list.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and architecture documents unless marked [INFERRED].

#### FR-1: `OVERVIEW.md.template`

**Destination:** `project/OVERVIEW.md` (user-owned)
**Architecture reference:** information-architecture.md section 3 Role 3

Restructure around the Project Intent role:

**Add (from architecture):**
1. **Goals Registry table** with columns: ID, Goal, Priority, Status, Source, Traced Requirements. Empty-state: header row only, no example data. Format example in HTML comment.
2. **Analysis Questions table** with columns: ID, Question, Implies, Source, Status. Empty-state: header row only. Format example in HTML comment.
3. **Scope** section with sub-sections: In Scope, Out of Scope, Future Phases.
4. **Success Criteria** section — project-level acceptance criteria.

**Keep (non-conflicting, useful for humans):**
5. **Project Summary** — replaces the current freeform intro. Brief prose context (2-3 paragraphs).
6. **Risks** section — project risks and mitigation.
7. **Getting Started** section — guidance for collaborators and agents.

**Remove (content now has dedicated homes):**
8. **Technical Approach** — this is now `project/ARCHITECTURE.md`'s job (Role 5).
9. **Model Organization** — same, ARCHITECTURE.md Package Organization section.
10. **Project Management** — now `work/BACKLOG.md` + `/status` command.
11. **Key Contacts** — operational noise in a template.
12. **Current Status** — operational tracking, not intent.

**Empty-state validity:** Template MUST work for a brand new project with nothing filled in (AP-1).

#### FR-2: `BACKLOG.md.template`

**Destination:** `work/BACKLOG.md` (user-owned)
**Architecture reference:** workflows.md section 3.6

1. **YAML frontmatter** with the machine-readable state structure:
   - `epics:` list (each with: name, goal, priority, status, file, items list)
   - `standalone:` list (each with: id, name, scale, priority, status, completed)
   - Empty-state: both lists empty (`epics: []`, `standalone: []`)
2. **Markdown body** as a rendered dashboard showing what the populated format looks like.
   - Epic sections with item tables (Item, Scale, Status, Notes columns)
   - Standalone items table (Item, Scale, Priority, Status, Notes columns)
   - Body is a deterministic rendering of frontmatter — AP-7 scripts own both
3. **Explanatory comments** in the body indicating the relationship between YAML frontmatter (source of truth) and markdown body (rendered view).

#### FR-3: `MODELING_GUIDE.md.template`

**Destination:** `project/MODELING_GUIDE.md` (tool-owned)

Three-part scope:

1. **Mark skill-extractable sections** with `<!-- SKILL: moves to {skill-name} -->` comments. Each marker identifies the destination skill from the skill catalog (workflows.md section 1.2):

   | Content | Destination skill |
   |---------|------------------|
   | Syntax patterns, imports, conditionals, constraints, semantic operators | `sysml-conventions` |
   | Model regression testing structure, methodology, test patterns | `model-validation` |
   | EXPOSE pattern details, cross-file binding patterns, library vs designs deep dive | `project-structure` |
   | Source citation patterns, doc comment format details | `source-traceability` |
   | Tools and scripts reference | `toolkit-awareness` |

2. **Verify pure-rules content is coherent**: The sections that remain unmarked (definitions vs usages rule, ADR-002 calculation placement, package structure rules, naming conventions, documentation standards, validation checklist) MUST form a logical, readable document even with the marked sections present.

3. **Leave all content in place.** No removal. The markers serve as a work list for Epic 2 — `grep -r "<!-- SKILL:"` yields the extraction manifest.

#### FR-4: `MODELING_PROCESS.md.template`

**Destination:** `project/MODELING_PROCESS.md` (tool-owned)

1. **Update directory references**: All `modeling_pm/` paths become their new equivalents:
   - `modeling_pm/OVERVIEW.md` → `project/OVERVIEW.md`
   - `modeling_pm/MODELING_GUIDE.md` → `project/MODELING_GUIDE.md`
   - `modeling_pm/backlog/` → `work/backlog/`
   - `modeling_pm/active/` → `work/active/`
   - `modeling_pm/research/` → `knowledge/research/`
   - `modeling_pm/learnings/` → `work/learnings/`
   - Any other `modeling_pm/` references → appropriate new path

2. **Add references to new documents** where contextually appropriate:
   - `knowledge/KNOWLEDGE.md` (domain insights)
   - `knowledge/SOURCE_INDEX.md` (authority sources — was at project root)
   - `project/ARCHITECTURE.md` (structural decisions)
   - `project/REQUIREMENTS.md` (project-specific rules)
   - `project/VALIDATION_MATRIX.md` (verification criteria)

3. **Do NOT add references to commands that don't exist yet** (`/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`). Keep references to only the 9 existing commands. Epic 3 updates this template when new commands ship.

4. [INFERRED] **Update the phase descriptions** where they reference reading from or writing to old locations. The workflow phases should describe reading from `knowledge/` and `project/` rather than `modeling_pm/`.

#### FR-5: `README.md.template`

**Destination:** project root `README.md` (user-owned)

1. **Update directory structure** to match the 4-directory model:
   - Replace `modeling_pm/` section with `knowledge/`, `project/`, `work/`, `data/` descriptions
   - Keep `models/` and `tests/` descriptions
   - Brief description of what each directory answers (from information-architecture.md section 2)

2. **Keep the command table showing only the 9 existing commands.** Do not add planned commands.

3. [INFERRED] **Add a brief note** that additional commands may be available in later toolkit versions. No command-by-command planned list.

4. **Update document purpose table** to include new documents (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md) and remove references to deleted/merged files (LOCAL_GUIDE.md per D1.3).

---

## Acceptance Criteria

### Core Functionality

- [x] OVERVIEW.md.template has Goals Registry and Analysis Questions tables with correct column schemas
- [x] OVERVIEW.md.template has Scope and Success Criteria sections
- [x] OVERVIEW.md.template does NOT have Technical Approach, Model Organization, Project Management, Key Contacts, or Current Status sections
- [x] BACKLOG.md.template has YAML frontmatter with `epics:` and `standalone:` structure
- [x] BACKLOG.md.template YAML is valid YAML with empty lists in default state
- [x] BACKLOG.md.template body shows rendered dashboard format
- [x] MODELING_GUIDE.md.template has `<!-- SKILL: moves to {skill-name} -->` markers on all reference/how-to sections
- [x] MODELING_GUIDE.md.template retains ALL existing content (no removals)
- [x] MODELING_GUIDE.md.template pure-rules sections form a coherent standalone narrative
- [x] MODELING_PROCESS.md.template has zero references to `modeling_pm/`
- [x] MODELING_PROCESS.md.template references new documents in appropriate contexts
- [x] MODELING_PROCESS.md.template does NOT reference commands that don't exist yet
- [x] README.md.template describes the 4-directory structure
- [x] README.md.template command table lists only 9 existing commands
- [x] README.md.template document table includes new documents, excludes deleted ones

### Empty-State Validity

- [x] Each template is valid markdown when installed with no user edits
- [x] No placeholder data that could be mistaken for real project content
- [x] Format examples use HTML comments, not table rows

### Quality & Integration

- [x] Existing agentic-mbse tests continue to pass (`uv run pytest tests/`)
- [x] All 5 templates are ready for D1.4 to wire into `cmd_init()` without further changes

---

## Related Artifacts

- **Architecture:** `.project/concepts/architecture-redesign/information-architecture.md` (section 3 Role 3 for OVERVIEW.md)
- **Architecture:** `.project/concepts/architecture-redesign/workflows.md` (section 3.6 for BACKLOG.md)
- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.2)
- **Predecessor:** `.project/active/template-evaluation-decisions/spec.md` (D1.3 — template dispositions)
- **Predecessor:** `.project/active/new-project-templates/spec.md` (D1.1 — new templates)
- **Successor:** D1.4 (`cmd_init()` rewiring) — consumes these revised templates
- **Successor:** Epic 2 (skill extraction) — reads `<!-- SKILL: -->` markers from MODELING_GUIDE.md

---

**Next Steps:** After approval, proceed to `/_my_design`
