# Epic: Architecture Redesign — Structure (Phase 1A)

**Epic ID**: EPIC-ARCH-001
**Status**: Ready
**Priority**: P0
**Created**: 2026-02-01
**Concept**: `.project/concepts/architecture-redesign/` (main.md, information-architecture.md, workflows.md, delta-checklist.md, implementation-plan.md)
**Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` §§ 1.1–1.9

---

## Executive Summary

Establish the information architecture that the entire redesign depends on: file structure, entity formats, project templates, `cmd_init()` rewiring, YAML frontmatter schemas, and fusion-tea migration. This is the critical path — every subsequent epic (skills, commands, PM engine) references the directory structure and file formats defined here.

**Critical Success Factor**: `agentic-mbse init` on a fresh directory produces the 4-directory structure (`knowledge/`, `modeling_project/`, `work/`, `data/`) with all registry files, and fusion-tea has been migrated with all 42 existing tests passing.

---

## Why This Epic Is First

Every downstream artifact references the file structure:

- **Skills** (Epic 2) reference `knowledge/KNOWLEDGE.md`, `modeling_project/REQUIREMENTS.md`, `work/BACKLOG.md`
- **Commands** (Epic 3) read from and write to the new directory paths
- **PM engine** (Epic 4) parses YAML frontmatter in `work/BACKLOG.md`, `work/active/*/spec.md`, and registries in `modeling_project/`

If the structure changes after any of those are built, everything downstream must be reworked. This epic settles the structure first.

---

## Success Criteria

- [ ] `agentic-mbse init` on a fresh directory creates the 4-directory structure with all registry files
- [ ] `agentic-mbse init --dev` on the agentic-mbse repo creates the correct symlink structure
- [ ] fusion-tea has been migrated and all 42 existing tests pass
- [ ] All YAML frontmatter schemas are documented in a single authoritative reference
- [ ] `replicate_setup.sh` produces the same structure as `cmd_init()`
- [ ] All existing agentic-mbse tests pass after CLI changes (`uv run pytest tests/`)

---

## Deliverables and Backlog Items

Seven deliverables with a dependency structure (see [Sequencing](#sequencing) below).

### D1.3: Template Evaluation Decisions — COMPLETE

**Type**: Design decisions
**Status**: Complete (approved 2026-02-01)
**Dependencies**: None (must come first — affects what templates exist)
**Decision record**: `.project/active/template-evaluation-decisions/spec.md`

**Objective**: Resolve keep/merge/delete for 4 existing templates not explicitly addressed in the architecture.

**Decisions (approved):**

| Template | Disposition | Rationale |
|----------|-------------|-----------|
| `assumption_register.md.template` | **DELETE** | Dead file — never installed by `cmd_init()`. Assumptions belong in spec.md (ephemeral) or PR-XXX in REQUIREMENTS.md (durable). |
| `LOCAL_GUIDE.md.template` | **MERGE into REQUIREMENTS.md, then DELETE** | Purpose identical to REQUIREMENTS.md (project-specific rules). Remove from `USER_OWNED_TEMPLATES`, remove `TestLocalGuide` tests. |
| `RAW_LEARNINGS.md.template` | **KEEP, update path** | Destination: `work/learnings/RAW_LEARNINGS.md` (was `modeling_pm/learnings/`). |
| `traceability_matrix.csv` | **KEEP, update schema, add to `cmd_init()`** | Rename 2 columns, add `Knowledge`/`Requirement`, remove `Status`. Install to `data/` as user-owned. |

Traceability matrix target header:
```
Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified
```

**Exit criteria**:
- [x] All 4 templates have a documented disposition (keep/merge/delete with rationale)
- [x] traceability_matrix.csv schema confirmed or updated

---

### D1.1: New Project Templates (6 templates) — COMPLETE

**Type**: Implementation
**Status**: Complete (audited 2026-02-01)
**Dependencies**: D1.3 (template decisions)

**Objective**: Create 6 new `.template` files in `project_templates/`. Each must be valid in the empty state (AP-1: design for 0, 1, N) with correct entity formats per information-architecture.md § 3.

**Delta checklist**: § 1.1

| Template | Destination | Entity format | Key content |
|----------|-------------|---------------|-------------|
| `KNOWLEDGE.md.template` | `knowledge/KNOWLEDGE.md` | DI-XXX entries | Domain insight registry. Empty-state: header + format example in comment. |
| `ARCHITECTURE.md.template` | `modeling_project/ARCHITECTURE.md` | AD-XXX entries | Domain Decomposition, Package Organization table, Key Decisions. Empty-state: section headers + placeholder text. |
| `REQUIREMENTS.md.template` | `modeling_project/REQUIREMENTS.md` | PR-XXX table | Columns: ID, Requirement, Source, Enforcement, Validation Method. Empty-state: header row only. |
| `VALIDATION_MATRIX.md.template` | `modeling_project/VALIDATION_MATRIX.md` | SV-XXX table | Columns: ID, Description, Type, Mechanism, Expected, Tolerance, Source, Test, Status. Empty-state: header row only. |
| `EPIC_GUIDE.md.template` | `work/EPIC_GUIDE.md` | Prose reference | Decomposition guidance: Goldilocks principle, scale taxonomy, anti-patterns. Tool-owned. |
| `epic_template.md.template` | `work/backlog/epic-{name}.md` | YAML frontmatter | Template for epic files: Status, Priority, Goal, Created, Updated frontmatter + free-form body sections. |

**Design constraints**:
- Each template must work when empty (no entries) — tables with header rows only, registries with format examples in comments
- Entity formats must exactly match information-architecture.md § 3
- EPIC_GUIDE.md content derived from workflows.md § 2.1 (scale taxonomy) and § 3.6 (epic tracking)

**Exit criteria**:
- [x] 6 new template files exist in `project_templates/`
- [x] Each template is valid markdown and works in the empty state
- [x] Entity formats match information-architecture.md § 3

---

### D1.2: Revised Project Templates (5 templates) — COMPLETE

**Type**: Implementation
**Status**: Complete (2026-02-01)
**Dependencies**: D1.3 (template decisions)

**Objective**: Update 5 existing templates to match the architecture.

**Delta checklist**: § 1.2

| Template | Key changes |
|----------|-------------|
| `OVERVIEW.md.template` | Add Goals Registry table (ID, Goal, Priority, Status, Source, Traced Requirements), Analysis Questions table (ID, Question, Implies, Source, Status), Scope section, Success Criteria section. Per information-architecture.md § 3 Role 3. |
| `BACKLOG.md.template` | Add YAML frontmatter structure (epics list with items, standalone list). Body becomes a rendered dashboard. Per workflows.md § 3.6. |
| `MODELING_GUIDE.md.template` | Extract reference/how-to material that will move to skills in Epic 2. What remains: pure rules (definitions vs usages, ADR-002, package structure, naming, documentation standards, validation checklist). |
| `MODELING_PROCESS.md.template` | Update references to new directory structure (`knowledge/`, `modeling_project/`, `work/`), new commands (`/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`), new documents (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md). |
| `README.md.template` | Update directory structure description to match 4-directory model. |

**Exit criteria**:
- [x] All 5 templates updated
- [x] OVERVIEW.md has Goals Registry and Analysis Questions tables
- [x] BACKLOG.md has YAML frontmatter structure matching workflows.md § 3.6
- [x] MODELING_GUIDE.md has reference material flagged or extracted (preparation for skill extraction in Epic 2)

---

### D1.5: YAML Frontmatter Schemas (Design Artifact)

**Type**: Design
**Dependencies**: None (can proceed in parallel with D1.1/D1.2)

**Objective**: Consolidate the exact YAML frontmatter schemas for all files the PM engine will parse. These are the PM engine's input contracts — Phase 3D (Epic 4) references this artifact.

**Delta checklist**: § 1.6

Schemas already sketched in workflows.md § 3.1–3.3 and § 3.6. This deliverable consolidates them into a single authoritative reference.

| File | Key fields | Source |
|------|-----------|--------|
| `spec.md` | Status (active\|paused\|abandoned\|failed\|completed), Scale (standard), Epic, Owner, Created, Updated | workflows.md § 3.1 |
| `design.md` | Status, Created, Updated, Related Artifacts (Spec path) | workflows.md § 3.1 |
| `plan.md` | Status, Created, Updated, Related Artifacts (Spec + Design paths) | workflows.md § 3.1 |
| `review.md` | Verdict (pass\|concerns\|fail), Created, Related Artifacts (Design path) | workflows.md § 3.3 |
| `BACKLOG.md` | epics list (name, goal, priority, status, file, items list), standalone list (name, scale, priority, status, completed) | workflows.md § 3.6 |
| `epic-{name}.md` | Status (draft\|active\|completed), Priority, Goal, Created, Updated | workflows.md § 3.6 |

**Deliverable**: A design document (`.project/concepts/architecture-redesign/frontmatter-schemas.md` or a section added to an existing doc) that Epic 4 can reference as the authoritative contract.

**Exit criteria**:
- [x] All 6 schemas documented with exact field names, types, and allowed values
- [x] Each schema has an example
- [x] Document is referenced from implementation-plan.md

---

### D1.4: `cmd_init()` Rewiring — COMPLETE

**Type**: Implementation
**Status**: Complete (2026-02-01)
**Dependencies**: D1.1 (new templates), D1.2 (revised templates), D1.5 (frontmatter schemas)

**Objective**: Update the Python init logic to create the new directory structure and install templates to their new locations.

**Delta checklist**: § 1.4 (~12 items) + § 1.5 (~6 items for `replicate_setup.sh`)

#### Changes to `src/agentic_mbse/cli/__init__.py`:

**Directory creation** — replace `modeling_pm/{backlog,active,research,learnings}` with:
```
knowledge/
knowledge/research/pending/
knowledge/research/approved/
knowledge/research/impacts/
knowledge/sources/
project/
modeling_project/intent/
work/
work/backlog/
work/active/
work/completed/
work/analysis/
work/learnings/
data/
```

**`USER_OWNED_TEMPLATES`** — update destinations:
- `OVERVIEW.md.template` → `modeling_project/OVERVIEW.md` (was `modeling_pm/OVERVIEW.md`)
- `BACKLOG.md.template` → `work/BACKLOG.md` (was `modeling_pm/backlog/BACKLOG.md`)
- `RAW_LEARNINGS.md.template` → `work/learnings/RAW_LEARNINGS.md` (was `modeling_pm/learnings/RAW_LEARNINGS.md`)
- Add: `KNOWLEDGE.md.template` → `knowledge/KNOWLEDGE.md`
- Add: `ARCHITECTURE.md.template` → `modeling_project/ARCHITECTURE.md`
- Add: `REQUIREMENTS.md.template` → `modeling_project/REQUIREMENTS.md`
- Add: `VALIDATION_MATRIX.md.template` → `modeling_project/VALIDATION_MATRIX.md`
- Remove or update: `LOCAL_GUIDE.md.template` (per D1.3 decision)
- Evaluate: `assumption_register.md.template` (per D1.3 decision)

**`TOOL_OWNED_TEMPLATES`** — update destinations:
- `MODELING_GUIDE.md.template` → `modeling_project/MODELING_GUIDE.md` (was `modeling_pm/MODELING_GUIDE.md`)
- `MODELING_PROCESS.md.template` → `modeling_project/MODELING_PROCESS.md` (was `modeling_pm/MODELING_PROCESS.md`)
- Add: `EPIC_GUIDE.md.template` → `work/EPIC_GUIDE.md`

**`DEV_MODE_GITIGNORE_PATHS`** — update:
- `modeling_pm/MODELING_GUIDE.md` → `modeling_project/MODELING_GUIDE.md`
- `modeling_pm/MODELING_PROCESS.md` → `modeling_project/MODELING_PROCESS.md`
- Add: `work/EPIC_GUIDE.md`

**SOURCE_INDEX.md** — move creation to `knowledge/SOURCE_INDEX.md` (was project root)

**Data templates** — install `data/traceability_matrix.csv` to `data/` directory

**Unchanged templates** — confirm these remain as-is (paths don't change in the new architecture):
- `conftest.py.template` → `tests/conftest.py`
- `test_models_example.py.template` → `tests/models/test_example.py`

#### Changes to `scripts/replicate_setup.sh` (reconcile and update in lockstep):

**Pre-existing divergence to reconcile**: `replicate_setup.sh` and `cmd_init()` currently install different component sets:
- `replicate_setup.sh` installs `sysmlv2-doc-analyzer.md` agent; `MBSE_AGENTS` does not list it
- `replicate_setup.sh` installs only `python-debugger` skill; `MBSE_SKILLS` lists all 3 (`python-debugger`, `record-learning`, `toolkit-awareness`)
- Agent lists differ between the two files

D1.4 must reconcile these divergences — bring both files to the same component set or document the differences as intentional (with a comment in each file explaining why). The new directory structure changes are the forcing function: if we're touching both files anyway, align them.

**Directory and template changes**:
- `create_project_structure()` → new directory structure
- Template copy destinations → new paths
- `create_overview_md()` → `modeling_project/OVERVIEW.md` with Goals Registry and Analysis Questions
- `create_source_index()` → `knowledge/SOURCE_INDEX.md`
- Add creation of new files: `knowledge/KNOWLEDGE.md`, `modeling_project/ARCHITECTURE.md`, `modeling_project/REQUIREMENTS.md`, `modeling_project/VALIDATION_MATRIX.md`, `work/BACKLOG.md`

#### Documentation updates (agentic-mbse repo):

**`CLAUDE.md`** — must update in lockstep with `cmd_init()` since it describes what init produces:
- Directory Clarification table: `modeling_pm/` references → `knowledge/`, `modeling_project/`, `work/`
- Architecture section: update init description, directory descriptions
- `DEV_MODE_GITIGNORE_PATHS` documentation: update paths
- Add descriptions of new files (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md)

**`docs/source-index.md`** — update path references now that SOURCE_INDEX.md moves to `knowledge/SOURCE_INDEX.md`

**Exit criteria**:
- [x] `agentic-mbse init` on a fresh directory creates the full 4-directory structure
- [x] All templates installed to correct new locations
- [x] `agentic-mbse init --dev` creates correct symlinks
- [x] `replicate_setup.sh` produces identical structure (or divergences documented as intentional)
- [x] Pre-existing component divergence between `replicate_setup.sh` and `cmd_init()` reconciled
- [x] SOURCE_INDEX.md created at `knowledge/SOURCE_INDEX.md`
- [x] `data/traceability_matrix.csv` installed with correct schema
- [x] agentic-mbse `CLAUDE.md` updated to reflect new structure
- [x] `docs/source-index.md` updated for new SOURCE_INDEX.md path

---

### D1.7: Test Updates

**Type**: Implementation
**Dependencies**: D1.4 (`cmd_init()` changes)

**Objective**: Update `tests/test_cli.py` to expect the new directory structure.

**Delta checklist**: § 1.9 (4 items)

**Scope**:
1. Update `cmd_init()` tests to expect new directories (`knowledge/`, `modeling_project/`, `work/`, `data/`)
2. Add tests for new template installation (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md)
3. Update path expectations from `modeling_pm/` to new locations
4. Verify `--dev` mode creates correct symlinks to new paths

**Exit criteria**:
- [ ] All 9 tests broken by D1.4 rewiring are fixed (see D1.4 audit M1):
  - `test_creates_source_index` — assert `knowledge/SOURCE_INDEX.md`
  - `test_overwrites_source_index_with_force` — same path fix
  - `test_uses_current_directory_if_no_path` — same path fix
  - `test_dev_creates_symlinks_for_tool_templates` — assert `modeling_project/MODELING_GUIDE.md`
  - `test_dev_updates_gitignore` — check for `modeling_project/` paths in gitignore
  - `test_init_creates_local_guide` — delete or repurpose (LOCAL_GUIDE.md removed)
  - `test_local_guide_skipped_if_exists` — delete or repurpose
  - `test_reinit_with_modification_prompts` — use `modeling_project/MODELING_GUIDE.md`
  - `test_force_flag_skips_prompts` — same path fix
- [ ] New tests for new templates (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md, epic_template.md)
- [ ] New tests for CSV installation to `data/traceability_matrix.csv`
- [ ] New tests for full 16-directory structure creation
- [ ] `uv run pytest tests/test_cli.py` passes (0 failures)

---

### D1.6: fusion-tea Migration

**Type**: Manual migration (on a git branch)
**Dependencies**: D1.4 (`cmd_init()` working correctly)

**Objective**: One-time migration of fusion-tea's project structure to validate the new architecture against a real project.

**Delta checklist**: § 1.7 (~26 items)

#### File moves

| From | To | Notes |
|------|----|-------|
| `modeling_pm/OVERVIEW.md` | `modeling_project/OVERVIEW.md` | |
| `modeling_pm/MODELING_GUIDE.md` | `modeling_project/MODELING_GUIDE.md` | |
| `modeling_pm/MODELING_PROCESS.md` | `modeling_project/MODELING_PROCESS.md` | |
| `modeling_pm/LOCAL_GUIDE.md` | Per D1.3 decision | Merge into `modeling_project/REQUIREMENTS.md` or keep at `modeling_project/LOCAL_GUIDE.md` |
| `modeling_pm/backlog/BACKLOG.md` | `work/BACKLOG.md` | |
| `modeling_pm/active/*` | `work/active/*` | |
| `modeling_pm/research/*` | `knowledge/research/approved/*` | Existing research was user-reviewed |
| `modeling_pm/learnings/*` | `work/learnings/*` | |
| `modeling_pm/docs/COST_MODELING.md` | `knowledge/sources/COST_MODELING.md` | Or remain separate — decide during migration |
| `SOURCE_INDEX.md` | `knowledge/SOURCE_INDEX.md` | |

#### New files to create (populated from existing content)

| File | Source content |
|------|--------------|
| `knowledge/KNOWLEDGE.md` | Extract DI-XXX entries from existing research and modeling knowledge |
| `modeling_project/ARCHITECTURE.md` | Extract AD-XXX from OVERVIEW.md and research (domain decomposition, CAS hierarchy) |
| `modeling_project/REQUIREMENTS.md` | Extract PR-XXX from LOCAL_GUIDE.md and learned patterns (cost patterns, doc comments) |
| `modeling_project/VALIDATION_MATRIX.md` | Populate SV-XXX from existing test assertions in `tests/models/` |
| `data/traceability_matrix.csv` | Verify/update schema (add Knowledge and Requirement columns if missing) |

#### New directories

`knowledge/research/pending/`, `knowledge/research/impacts/`, `knowledge/sources/`, `modeling_project/intent/`, `work/backlog/`, `work/completed/`, `work/analysis/`

#### Format changes

- `work/BACKLOG.md` — add YAML frontmatter with epics/standalone structure
- `work/active/*/spec.md` — add YAML frontmatter (Status, Scale, Epic, Owner, Created, Updated). Work item identity is the directory name, not a frontmatter field — consistent with the architecture's no-E-XXX-ID decision.
- `work/active/*/design.md` — add YAML frontmatter (Status, Created, Updated, Related Artifacts)
- `work/active/*/plan.md` — add YAML frontmatter (Status, Created, Updated, Related Artifacts)

#### Cleanup

- Remove `modeling_pm/` (or rename to `modeling_pm.bak/` temporarily)
- Update `.gitignore`
- Update fusion-tea's `CLAUDE.md` to reference new paths
- Update symlinks (`.claude/` components point to agentic-mbse repo)

#### Risks and mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Migration breaks existing 42 tests | High | Do on a git branch; run all tests before merging |
| Active work items in `modeling_pm/active/` need frontmatter | Medium | Add YAML frontmatter to each spec.md during migration |
| Symlinks in `.claude/` need updating | Low | Update after directory moves are complete |

**Exit criteria**:
- [ ] All files moved to new locations
- [ ] New registry files created and populated
- [ ] YAML frontmatter added to all active work item artifacts
- [ ] BACKLOG.md restructured with YAML frontmatter
- [ ] fusion-tea CLAUDE.md updated
- [ ] All 42 existing tests pass
- [ ] Migration done on a branch for clean revert capability

---

## Sequencing

```
D1.3 (template decisions) ─────► D1.1 (new templates) ──┐
                                  D1.2 (revised templates) ──┤
                                                              ├─► D1.4 (cmd_init) ──► D1.7 (tests)
D1.5 (frontmatter schemas) ──────────────────────────────────┘        │
                                                                       ▼
                                                              D1.6 (fusion-tea migration)
```

- **D1.3** must come first — template disposition decisions affect what D1.1 and D1.2 produce
- **D1.1**, **D1.2**, and **D1.5** can proceed in parallel once D1.3 is resolved
- **D1.4** depends on templates being final (it wires them into the CLI)
- **D1.7** depends on D1.4 (tests verify the new CLI behavior)
- **D1.6** depends on D1.4 working correctly (or can follow the same structure manually)

---

## Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| fusion-tea migration breaks existing tests | High | Low | Do on git branch; run all 42 tests before merging |
| YAML frontmatter format needs to change after this epic | High | Low | D1.5 consolidates schemas into explicit design artifact before code depends on them |
| `replicate_setup.sh` and `cmd_init()` diverge | Medium | Medium | Update both in the same commit; add a smoke test comparing their output |
| Template decisions (D1.3) have unexpected consequences | Low | Low | Resolve D1.3 before writing any templates; decisions are small and reversible |
| New directory structure confuses existing users | Low | Medium | MODELING_PROCESS.md template updated with new paths; README.md template updated |

---

## What This Epic Does NOT Include

Explicitly out of scope (handled in later epics):

- **Skill creation** — Epic 2 extracts shared knowledge from commands into skills
- **Command refactoring** — Epic 3 refactors commands to use skills and new paths
- **PM engine code** — Epic 4 builds the Python parsers, state derivation, and CLI subcommands
- **New commands** (`/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`) — Epic 3

This epic produces the **structure** those epics build on. It creates templates and wires them into init, but does not build the software that parses or operates on the structured files.

---

## Relationship to Previous Epic

This epic supersedes `EPIC-CMDREV-001` (MBSE Command System Revision). That epic planned a command-focused revision without the information architecture redesign. The architecture redesign (this epic + Epics 2-4) addresses the same problems at a deeper level:

- CMDREV Stage 1 (command harmonization) → absorbed into Epic 3 with skill-based extraction
- CMDREV Stage 2 (PM enhancement) → absorbed into Epic 4 (script-backed PM engine)
- CMDREV Stage 3 (design refactor) → absorbed into Epic 3 (design-model refactored with skills)
- CMDREV Stage 4 (quick-model, templates) → absorbed into Epic 3 (new commands)

EPIC-CMDREV-001 should be marked as superseded.

---

**Last Updated**: 2026-02-01
**Next Action**: D1.7 (test updates) then D1.6 (fusion-tea migration)
