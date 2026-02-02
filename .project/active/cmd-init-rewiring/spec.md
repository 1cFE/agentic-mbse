# Spec: D1.4 — `cmd_init()` Rewiring

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-01
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-001 (Architecture Redesign — Structure)

---

## Business Goals

### Why This Matters

This is the critical-path deliverable that makes the new information architecture real. Every downstream epic — skills (Epic 2), commands (Epic 3), PM engine (Epic 4) — references the directory structure and file locations produced by `cmd_init()`. Until init is rewired, the 11 new and revised templates from D1.1/D1.2 sit unused in `project_templates/`, and users cannot adopt the 4-directory architecture.

### Success Criteria

- [ ] `agentic-mbse init` on a fresh directory creates the full 4-directory structure (`knowledge/`, `project/`, `work/`, `data/`) with all registry files
- [ ] All templates installed to correct new locations
- [ ] `agentic-mbse init --dev` creates correct symlinks to new paths
- [ ] `replicate_setup.sh` produces equivalent structure to `cmd_init()`
- [ ] Component divergence between `replicate_setup.sh` and `cmd_init()` reconciled (both directions)
- [ ] SOURCE_INDEX.md created at `knowledge/SOURCE_INDEX.md`
- [ ] `data/traceability_matrix.csv` installed with D1.3-approved schema
- [ ] `CLAUDE.md` updated to reflect new structure
- [ ] `docs/source-index.md` updated for new SOURCE_INDEX.md path
- [ ] All existing agentic-mbse tests still pass (D1.7 updates them — but nothing should break *more* than existing `modeling_pm/` expectations)

### Priority

P0 — blocks D1.7 (test updates) and D1.6 (fusion-tea migration).

---

## Problem Statement

### Current State

`cmd_init()` creates the old `modeling_pm/{backlog,active,research,learnings}` structure. Templates are installed to `modeling_pm/` paths. `replicate_setup.sh` does roughly the same but with a divergent component set (different agents, different skills) and a hardcoded coffee-maker OVERVIEW.md. The traceability matrix CSV has an outdated schema. `CLAUDE.md` and `docs/source-index.md` describe the old structure.

### Desired Outcome

Both `cmd_init()` and `replicate_setup.sh` produce the new 4-directory structure with all templates at their correct locations, identical component sets, and documentation that matches reality.

---

## Scope

### In Scope

1. `src/agentic_mbse/cli/__init__.py` — all changes listed below
2. `scripts/replicate_setup.sh` — all changes listed below
3. `project_templates/data/traceability_matrix.csv` — schema update per D1.3
4. `CLAUDE.md` — update directory descriptions and path references
5. `docs/source-index.md` — update SOURCE_INDEX.md path reference

### Out of Scope

- **Test updates** — D1.7 (separate deliverable, depends on this one)
- **fusion-tea migration** — D1.6 (separate deliverable, depends on this one)
- **Template content** — D1.1 and D1.2 are complete; no template file bodies change here
- **New commands, skills, or PM engine** — Epics 2, 3, 4
- **Deleting `assumption_register.md.template` or `LOCAL_GUIDE.md.template` from `project_templates/`** — the files can remain on disk; D1.4 just stops installing them. Cleanup is optional and low-priority.

### Edge Cases & Considerations

- **Idempotency**: `cmd_init()` run twice on the same directory MUST produce the same result. New directories use `mkdir(parents=True, exist_ok=True)`. User-owned files are skipped if they exist. Tool-owned files are always updated.
- **Dev mode symlinks**: `--dev` must symlink tool-owned files to their new destination paths, not the old `modeling_pm/` paths.
- **Existing installs**: Users with the old `modeling_pm/` structure who re-run `init` will get the new directories *alongside* the old ones. This is acceptable — migration is the user's responsibility (or D1.6 for fusion-tea). `cmd_init()` does not delete old directories.
- **`.gitignore` dev mode section**: If a user already has the old dev mode section in `.gitignore`, re-running `--dev` will append a second section. This is the existing behavior and is acceptable (the marker check prevents duplication only if the exact marker string matches). The marker string changes because the paths change, so existing installs will get a second block. This is a known minor issue — not worth adding migration logic.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic's D1.4 section and user's answers unless marked [INFERRED].

#### FR-1: Directory Structure (delta checklist § 1.4)

`cmd_init()` MUST create these directories instead of `modeling_pm/{backlog,active,research,learnings}`:

```
knowledge/
knowledge/research/pending/
knowledge/research/approved/
knowledge/research/impacts/
knowledge/sources/
project/
project/intent/
work/
work/backlog/
work/active/
work/completed/
work/analysis/
work/learnings/
data/
```

The `tests/models/` directory creation MUST remain unchanged.

#### FR-2: USER_OWNED_TEMPLATES Updates

Update the `USER_OWNED_TEMPLATES` list:

| Action | Template | Old Destination | New Destination |
|--------|----------|----------------|-----------------|
| **Change path** | `OVERVIEW.md.template` | `modeling_pm/OVERVIEW.md` | `project/OVERVIEW.md` |
| **Change path** | `BACKLOG.md.template` | `modeling_pm/backlog/BACKLOG.md` | `work/BACKLOG.md` |
| **Change path** | `RAW_LEARNINGS.md.template` | `modeling_pm/learnings/RAW_LEARNINGS.md` | `work/learnings/RAW_LEARNINGS.md` |
| **Add** | `KNOWLEDGE.md.template` | — | `knowledge/KNOWLEDGE.md` |
| **Add** | `ARCHITECTURE.md.template` | — | `project/ARCHITECTURE.md` |
| **Add** | `REQUIREMENTS.md.template` | — | `project/REQUIREMENTS.md` |
| **Add** | `VALIDATION_MATRIX.md.template` | — | `project/VALIDATION_MATRIX.md` |
| **Remove** | `LOCAL_GUIDE.md.template` | `modeling_pm/LOCAL_GUIDE.md` | *(not installed)* |

`conftest.py.template` and `test_models_example.py.template` destinations are unchanged.
`README.md.template` destination is unchanged.

#### FR-3: TOOL_OWNED_TEMPLATES Updates

Update the `TOOL_OWNED_TEMPLATES` list:

| Action | Template | Old Destination | New Destination |
|--------|----------|----------------|-----------------|
| **Change path** | `MODELING_GUIDE.md.template` | `modeling_pm/MODELING_GUIDE.md` | `project/MODELING_GUIDE.md` |
| **Change path** | `MODELING_PROCESS.md.template` | `modeling_pm/MODELING_PROCESS.md` | `project/MODELING_PROCESS.md` |
| **Add** | `EPIC_GUIDE.md.template` | — | `work/EPIC_GUIDE.md` |

#### FR-4: SOURCE_INDEX.md Location Change

`cmd_init()` MUST create SOURCE_INDEX.md at `knowledge/SOURCE_INDEX.md` instead of the project root. The `get_template_path()` helper and `source_index_path` variable in `cmd_init()` must update accordingly.

#### FR-5: Traceability Matrix CSV

`cmd_init()` MUST install `project_templates/data/traceability_matrix.csv` to `data/traceability_matrix.csv` as a user-owned file (skip if exists, overwrite with `--force`).

The CSV template MUST be updated to the D1.3-approved schema:

```
Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified
```

(Replaces: `Element,Type,Source_Type,Source_Document,Source_Location,Implementation_Location,Status,Confidence,Assumptions,Date_Created`)

#### FR-6: DEV_MODE_GITIGNORE_PATHS

Update the `DEV_MODE_GITIGNORE_PATHS` list:

| Action | Old Path | New Path |
|--------|----------|----------|
| **Change** | `modeling_pm/MODELING_GUIDE.md` | `project/MODELING_GUIDE.md` |
| **Change** | `modeling_pm/MODELING_PROCESS.md` | `project/MODELING_PROCESS.md` |
| **Add** | — | `work/EPIC_GUIDE.md` |

#### FR-7: Component Reconciliation

**`MBSE_AGENTS` in `cli/__init__.py`**: No change. The 5 non-deprecated agents remain as-is. `sysmlv2-doc-analyzer.md` is NOT added — the agent lives in `claude/agents/deprecated/` with an explicit deprecation banner, and its functionality is covered by the 4 specialized replacements (`kerml-expert`, `sysml-expert`, `syside-expert`, `sysmlv2-validator`). Epic 3A (delta checklist § 3A.4) evaluates its final disposition. (See design DD-1.)

**`replicate_setup.sh` agent loop**: Replace the current 2-agent list with the `MBSE_AGENTS` list (removing the deprecated agent):
- `python-debugger.md`
- `kerml-expert.md`
- `sysml-expert.md`
- `syside-expert.md`
- `sysmlv2-validator.md`

**`replicate_setup.sh` skill loop**: Replace the current 1-skill install with the full `MBSE_SKILLS` list:
- `python-debugger`
- `record-learning`
- `toolkit-awareness`

`MBSE_AGENTS`/`MBSE_SKILLS` in `cli/__init__.py` is the source of truth. `replicate_setup.sh` mirrors it.

#### FR-8: `replicate_setup.sh` Structure Changes

- `create_project_structure()`: Create the new 13-directory structure (same as FR-1) instead of `modeling_pm/{backlog,active,research}`
- Template copy destinations: Use new paths (same as FR-2 and FR-3)
- Delete `create_overview_md()` function — use `OVERVIEW.md.template` instead (copy from `project_templates/OVERVIEW.md.template` to `project/OVERVIEW.md`)
- `create_source_index()`: Copy to `knowledge/SOURCE_INDEX.md` instead of root `SOURCE_INDEX.md`
- Add creation of new user-owned files from templates: `knowledge/KNOWLEDGE.md`, `project/ARCHITECTURE.md`, `project/REQUIREMENTS.md`, `project/VALIDATION_MATRIX.md`, `work/BACKLOG.md`
- Install `data/traceability_matrix.csv` from `project_templates/data/`
- Install `work/EPIC_GUIDE.md` from template

#### FR-9: CLAUDE.md Updates

Update `CLAUDE.md` in the agentic-mbse repo to reflect the new structure:

- **Directory Clarification table**: Replace `modeling_pm/` references with `knowledge/`, `project/`, `work/`, `data/`
- **Architecture section**: Update init description and directory descriptions
- **`DEV_MODE_GITIGNORE_PATHS` documentation**: Update paths
- **Add descriptions** of new files: KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md
- **Update the `cmd_init()` docstring** in the Architecture section to describe the new structure
- **Update `MBSE_AGENTS` mention** if any (list unchanged; `sysmlv2-doc-analyzer.md` remains deprecated per DD-1)

#### FR-10: `docs/source-index.md` Update

Update path references: SOURCE_INDEX.md is now at `knowledge/SOURCE_INDEX.md`, not the project root.

#### [INFERRED] FR-11: `replicate_setup.sh` Print Summary

Update `print_summary()` to reference the new paths (e.g., `project/OVERVIEW.md` instead of `modeling_pm/OVERVIEW.md`).

#### [INFERRED] FR-12: epic_template.md.template

Add `epic_template.md.template` to `TOOL_OWNED_TEMPLATES` with destination `work/backlog/epic_template.md`. This is a tool-owned reference file (same category as `EPIC_GUIDE.md`) — users may create epics manually (AP-5: toolkit, not pipeline), and having the structural template visible in the project is self-documenting. The PM engine won't parse it (it globs for `epic-*.md`, not `epic_template.md`). Also add `work/backlog/epic_template.md` to `DEV_MODE_GITIGNORE_PATHS`. (See design DD-2.)

---

## Acceptance Criteria

### Core Functionality

- [ ] `cmd_init()` on a fresh `tmp_path` creates all 13 new directories
- [ ] `cmd_init()` does NOT create `modeling_pm/` or any of its subdirectories
- [ ] All `USER_OWNED_TEMPLATES` install to correct new paths
- [ ] All `TOOL_OWNED_TEMPLATES` install to correct new paths
- [ ] SOURCE_INDEX.md created at `knowledge/SOURCE_INDEX.md`
- [ ] `data/traceability_matrix.csv` installed with correct D1.3 schema header
- [ ] `data/traceability_matrix.csv` is user-owned (skipped on re-init without `--force`)
- [ ] `--dev` mode symlinks point to correct new paths
- [ ] `--dev` mode `.gitignore` entries use new paths
- [ ] `MBSE_AGENTS` unchanged (5 non-deprecated agents; `sysmlv2-doc-analyzer.md` not added per DD-1)
- [ ] `replicate_setup.sh` installs the same 5 agents as `MBSE_AGENTS` (deprecated agent removed)
- [ ] `replicate_setup.sh` installs all 3 skills from `MBSE_SKILLS` list
- [ ] `replicate_setup.sh` creates the same directory structure as `cmd_init()`
- [ ] `replicate_setup.sh` uses `OVERVIEW.md.template` (no hardcoded coffee-maker content)
- [ ] `replicate_setup.sh` installs SOURCE_INDEX.md to `knowledge/`

### Documentation

- [ ] `CLAUDE.md` directory table reflects `knowledge/`, `project/`, `work/`, `data/`
- [ ] `docs/source-index.md` references `knowledge/SOURCE_INDEX.md`

### Quality & Integration

- [ ] Existing tests pass (they will need updates in D1.7 — but the code change itself should not introduce import errors, syntax errors, or crashes)
- [ ] `cmd_init()` remains idempotent (running twice produces same result)
- [ ] `--force` flag still works correctly with new paths
- [ ] Hash tracking works correctly with new file paths

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-structure.md`
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` (§§ 1.4, 1.5)
- **Frontmatter Schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`
- **Template Decisions:** `.project/active/template-evaluation-decisions/spec.md` (D1.3)
- **Information Architecture:** `.project/concepts/architecture-redesign/information-architecture.md`
- **Design:** `.project/active/cmd-init-rewiring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
