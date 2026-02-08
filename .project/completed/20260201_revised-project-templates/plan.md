# Implementation Plan: Revised Project Templates (D1.2)

**Status:** Complete
**Created:** 2026-02-01 21:04:17 UTC
**Last Updated:** 2026-02-01 21:04:17 UTC

## Source Documents
- **Spec:** `.project/active/revised-project-templates/spec.md`
- **Design:** `.project/active/revised-project-templates/design.md` — See here for section structures, marker tables, path substitution tables, and directory trees

## Implementation Strategy

**Phasing Rationale:**
All 5 changes are template edits — no Python code, no new modules. Phases are ordered by complexity (most complex first) so that the hardest work gets the most attention. BACKLOG.md is a complete rewrite (highest risk of getting the YAML wrong). OVERVIEW.md is a restructure (add/remove sections). MODELING_GUIDE.md is additive (markers only). MODELING_PROCESS.md and README.md are mechanical path updates (grouped together). Final phase validates the complete set.

**Overall Validation Approach:**
- After each phase: visual inspection of the edited template
- After Phase 4: `grep -r "modeling_pm" project_templates/` returns zero matches
- After Phase 5: `uv run pytest tests/` passes, all acceptance criteria checked

---

## Phase 1: BACKLOG.md.template (Complete Rewrite)

### Goal
Replace the priority-bucket markdown format with YAML frontmatter + rendered dashboard body. This is the most structurally different change — the entire file content is replaced.

### Changes Required

**File:** `project_templates/BACKLOG.md.template` (REWRITE)

See `design.md#template-2-backlogmdtemplate` for the exact structure.

- [x] Replace entire file content with YAML frontmatter (`epics: []`, `standalone: []`)
- [x] Add `# Project Backlog` heading
- [x] Add explanatory HTML comment explaining frontmatter/body relationship
- [x] Add empty-state guidance text ("No epics or work items yet...")
- [x] Add rendered dashboard format example in HTML comment (epic section + standalone table)

### Validation

**Automated:**
- [x] Parse YAML frontmatter with Python: `python3 -c "import yaml; print(yaml.safe_load(open('project_templates/BACKLOG.md.template').read().split('---')[1]))"` — should print `{'epics': [], 'standalone': []}`

**Manual:**
- [x] Read the template — does it make sense to someone seeing it for the first time?
- [x] Verify no content that looks like real project data

**What We Know Works After This Phase:**
BACKLOG.md template has valid YAML frontmatter that a parser can read, with a clear empty-state body.

---

## Phase 2: OVERVIEW.md.template (Restructure)

### Goal
Restructure from generic project overview to Role 3 (Project Intent) document with Goals Registry and Analysis Questions tables.

### Changes Required

**File:** `project_templates/OVERVIEW.md.template` (REWRITE)

See `design.md#template-1-overviewmdtemplate` for section structure and removed/kept/added sections.

- [x] Replace `# Project Overview` with `# <!-- PROJECT_NAME -->`
- [x] Replace "What We're Building" + "Why SysMLv2" with `## Project Summary` (consolidated, 2-3 paragraph placeholder)
- [x] Add `## Goals Registry` with table header: `| ID | Goal | Priority | Status | Source | Traced Requirements |` and format example in HTML comment
- [x] Add `## Analysis Questions` with intro text and table header: `| ID | Question | Implies | Source | Status |` and format example in HTML comment
- [x] Add `## Scope` with sub-sections: In Scope, Out of Scope, Future Phases
- [x] Revise `## Success Criteria` — simplify from Must/Should/Nice to single section with user-fillable checkboxes
- [x] Keep `## Project Risks` — table format unchanged
- [x] Keep `## Getting Started` — update path references per design
- [x] Keep `## Resources` — update paths, add new document references
- [x] Remove: Technical Approach section
- [x] Remove: Technology Stack section (Model Organization + Project Management trees)
- [x] Remove: Current Status section
- [x] Remove: Key Contacts section

### Validation

**Manual:**
- [x] Goals Registry table has exactly 6 columns matching information-architecture.md § 3 Role 3
- [x] Analysis Questions table has exactly 5 columns matching architecture spec
- [x] No sections remain for: Technical Approach, Model Organization, Project Management, Key Contacts, Current Status
- [x] Getting Started references use correct paths (sibling files bare, cross-directory with `../` or description)
- [x] Template reads well in empty state — a new user understands what to fill in

**What We Know Works After This Phase:**
OVERVIEW.md template matches the Role 3 (Project Intent) structure with correct entity table schemas.

---

## Phase 3: MODELING_GUIDE.md.template (Skill Markers)

### Goal
Add `<!-- SKILL: moves to {skill-name} -->` markers to all reference/how-to sections. Update LOCAL_GUIDE.md reference to REQUIREMENTS.md. No content removed.

### Changes Required

**File:** `project_templates/MODELING_GUIDE.md.template` (EDIT)

See `design.md#template-3-modeling_guidemdtemplate` for the section-by-section marker table.

- [x] Add `<!-- SKILL: moves to project-structure -->` before `## The EXPOSE Pattern`
- [x] Add `<!-- SKILL: moves to sysml-conventions -->` before `## Standard Imports`
- [x] Add `<!-- SKILL: moves to sysml-conventions -->` before `## Key Syntax Patterns`
- [x] Add `<!-- SKILL: moves to model-validation -->` before `## Model Regression Testing`
- [x] Add `<!-- SKILL: moves to toolkit-awareness -->` before `## Tools and Scripts`
- [x] Add `<!-- SKILL: moves to sysml-conventions -->` before `## Pattern Documentation Index`
- [x] Update opening note: `[LOCAL_GUIDE.md](LOCAL_GUIDE.md)` → `[REQUIREMENTS.md](REQUIREMENTS.md)`

### Validation

**Automated:**
- [x] `grep -c "<!-- SKILL:" project_templates/MODELING_GUIDE.md.template` returns `6`
- [x] `grep "<!-- SKILL:" project_templates/MODELING_GUIDE.md.template` shows exactly: 1x `project-structure`, 3x `sysml-conventions`, 1x `model-validation`, 1x `toolkit-awareness`
- [x] `grep "LOCAL_GUIDE" project_templates/MODELING_GUIDE.md.template` returns zero matches

**Manual:**
- [x] Read the unmarked sections in order (Definitions vs Usages → ADR-002 → Package Structure → Naming → Documentation Standards → Validation Checklist) — do they form a coherent rules document?
- [x] All existing content is present — no lines deleted

**What We Know Works After This Phase:**
MODELING_GUIDE.md has a complete skill extraction manifest. Epic 2 can `grep "<!-- SKILL:"` and get its work list. The guide remains fully functional.

---

## Phase 4: MODELING_PROCESS.md + README.md (Path Updates)

### Goal
Update all `modeling_pm/` references in both templates. Add new document references to MODELING_PROCESS.md. Update README directory tree and document table.

### Changes Required

**File 1:** `project_templates/MODELING_PROCESS.md.template` (EDIT)

See `design.md#template-4-modeling_processmdtemplate` for path substitution table and new document reference locations.

- [x] Replace all `modeling_pm/` path references per design substitution table
- [x] Replace root-level `SOURCE_INDEX.md` references with `knowledge/SOURCE_INDEX.md`
- [x] Add `knowledge/KNOWLEDGE.md` reference in Phase 1.1 reading list
- [x] Add `project/ARCHITECTURE.md` reference in Phase 2 intro
- [x] Add `project/REQUIREMENTS.md` reference in Phase 2.2 and Phase 3
- [x] Add `project/VALIDATION_MATRIX.md` reference in Phase 3.4
- [x] Update References section at bottom with new paths

**File 2:** `project_templates/README.md.template` (EDIT)

See `design.md#template-5-readmemdtemplate` for document table, directory tree, and path updates.

- [x] Replace document purpose table with expanded 12-row version from design
- [x] Update "What You Edit" section paths per design
- [x] Update "Commands manage for you" section paths
- [x] Update "Static" section paths
- [x] Replace `modeling_pm/` Project Management tree with 4-directory tree from design
- [x] Add brief note after command table: "Additional commands may be available in later toolkit versions."
- [x] Update Resources section links to new paths

### Validation

**Automated:**
- [x] `grep -rc "modeling_pm" project_templates/MODELING_PROCESS.md.template` returns `0`
- [x] `grep -rc "modeling_pm" project_templates/README.md.template` returns `0`
- [x] `grep -rc "modeling_pm" project_templates/OVERVIEW.md.template project_templates/BACKLOG.md.template project_templates/MODELING_GUIDE.md.template` returns `0` for each (confirm earlier phases didn't miss any)

**Manual:**
- [x] MODELING_PROCESS.md references to new documents appear in contextually appropriate locations
- [x] README.md command table still lists only 9 commands + 2 backlog sub-commands
- [x] README.md directory tree matches design's 4-directory structure

**What We Know Works After This Phase:**
All 5 templates have zero `modeling_pm/` references. New documents are referenced where appropriate. README accurately describes the new structure.

---

## Phase 5: Cross-Template Validation

### Goal
Verify all acceptance criteria from the spec across the complete set of revised templates.

### Validation

**Automated:**
- [x] `grep -r "modeling_pm" project_templates/{OVERVIEW,BACKLOG,MODELING_GUIDE,MODELING_PROCESS,README}.md.template` — zero matches
- [x] `grep -c "<!-- SKILL:" project_templates/MODELING_GUIDE.md.template` — returns 6
- [x] `grep "LOCAL_GUIDE" project_templates/MODELING_GUIDE.md.template` — zero matches
- [x] YAML frontmatter parse on BACKLOG.md.template succeeds
- [x] `uv run pytest tests/` — all existing tests pass

**Manual — Spec Acceptance Criteria Checklist:**
- [x] OVERVIEW.md has Goals Registry and Analysis Questions tables with correct column schemas
- [x] OVERVIEW.md has Scope and Success Criteria sections
- [x] OVERVIEW.md does NOT have Technical Approach, Model Organization, Project Management, Key Contacts, or Current Status
- [x] BACKLOG.md has YAML frontmatter with `epics:` and `standalone:` structure
- [x] BACKLOG.md YAML is valid with empty lists in default state
- [x] BACKLOG.md body shows rendered dashboard format in comment
- [x] MODELING_GUIDE.md has markers on all reference/how-to sections
- [x] MODELING_GUIDE.md retains ALL existing content
- [x] MODELING_GUIDE.md pure-rules sections form coherent standalone narrative
- [x] MODELING_PROCESS.md has zero `modeling_pm/` references
- [x] MODELING_PROCESS.md references new documents in appropriate contexts
- [x] MODELING_PROCESS.md does NOT reference commands that don't exist yet
- [x] README.md describes 4-directory structure
- [x] README.md command table lists only 9 existing commands
- [x] README.md document table includes new documents, excludes deleted ones
- [x] Each template is valid markdown in empty state
- [x] No placeholder data that looks like real content
- [x] Format examples use HTML comments, not table rows

---

## Environment Setup

See CLAUDE.md for full environment rules. Key commands:
- `uv run pytest tests/` — run all tests
- `uv run ruff check src/ tests/` — linting
- `uv run ruff format src/ tests/` — formatting

---

## Risk Management

See `design.md#potential-risks` for detailed risk analysis.

**Phase-Specific Mitigations:**
- **Phase 1**: YAML validity checked immediately with Python parser
- **Phase 3**: Marker count verified with grep — exactly 6 markers, no more, no less
- **Phase 4**: `grep -r "modeling_pm"` sweep catches any missed references across all templates

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Rewrote `project_templates/BACKLOG.md.template` with YAML frontmatter (`epics: []`, `standalone: []`), explanatory HTML comment, empty-state guidance, and rendered dashboard format example in comment
**Issues:** None

### Phase 2 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Rewrote `project_templates/OVERVIEW.md.template` with Role 3 structure: Project Summary, Goals Registry (6-column table), Analysis Questions (5-column table), Scope (In/Out/Future), Success Criteria (checkboxes), Project Risks, Getting Started, Resources
- Removed: Technical Approach, Technology Stack (Model Org + PM trees), Current Status, Key Contacts, Why SysMLv2 (standalone section)
- Updated Getting Started paths to `../work/BACKLOG.md`, `../work/active/`
- Added ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, knowledge/SOURCE_INDEX.md to Resources
**Issues:** None

### Phase 3 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Added 6 `<!-- SKILL: moves to {name} -->` markers: 1x project-structure, 3x sysml-conventions, 1x model-validation, 1x toolkit-awareness
- Updated `LOCAL_GUIDE.md` reference to `REQUIREMENTS.md`
- All existing content preserved (287 lines vs original 282 = +6 markers -1 blank line)
**Issues:** None

### Phase 4 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- `MODELING_PROCESS.md.template`: Updated References section (modeling_pm/MODELING_GUIDE.md → MODELING_GUIDE.md, modeling_pm/OVERVIEW.md → OVERVIEW.md, SOURCE_INDEX.md → knowledge/SOURCE_INDEX.md). Added new doc references: knowledge/KNOWLEDGE.md (Phase 1.1), ARCHITECTURE.md (Phase 2 intro), REQUIREMENTS.md (Phase 2.2 + Phase 3), VALIDATION_MATRIX.md (Phase 3.4). Added ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, knowledge/KNOWLEDGE.md to References section.
- `README.md.template`: Replaced 8-row document table with 12-row version. Updated "What You Edit" and "Commands manage" paths. Updated "Static" paths. Replaced modeling_pm/ tree with 4-directory tree (knowledge/, project/, work/, data/). Added "Additional commands may be available" note. Updated Resources section links.
**Issues:** None

### Phase 5 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- All automated checks pass: zero `modeling_pm/` across 5 templates, 6 SKILL markers, zero LOCAL_GUIDE, valid YAML frontmatter
- 324 pytest tests pass, 1 skipped
**Issues:** None

---

**Status**: Complete
