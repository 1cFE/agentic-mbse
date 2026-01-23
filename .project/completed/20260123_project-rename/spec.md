# Spec: Rename `project/` to `modeling_pm/`

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-16 18:34 UTC
**Complexity:** LOW
**Branch:** 1cfe_dev
**Backlog Item:** ITEM-RENAME-001

---

## Business Goals

### Why This Matters

The current naming creates cognitive overhead and potential confusion. Developers must remember the subtle difference between `.project/` (hidden, for tool development) and `project/` (visible, for modeling work). The semantic distinction isn't clear from names alone.

Clear, self-documenting directory names improve onboarding and reduce mistakes when navigating the codebase or working across both tool development and modeling workflows.

### Success Criteria

- [ ] A user reading the directory structure immediately understands what each folder is for
- [ ] `.project/` = developing THIS tool (Python code, CLI, validation logic)
- [ ] `modeling_pm/` = using THIS tool to build SysML models

### Priority

P1 (High) - This is a naming/clarity improvement that affects daily workflow comprehension.

---

## Problem Statement

### Current State

Two directories with similar names serve different purposes:
- `.project/` - Tool/code development (specs, designs, backlog for the agentic-mbse library)
- `project/` - SysML modeling project management (OVERVIEW.md, MODELING_GUIDE.md, etc.)

The distinction requires reading documentation or prior knowledge to understand.

### Desired Outcome

Rename `project/` to `modeling_pm/` (modeling project management) so the purpose is self-evident from the name.

---

## Scope

### In Scope

1. Rename `project/` → `modeling_pm/` in CLI `cmd_init()` output paths
2. Update `scripts/replicate_setup.sh` directory creation and file placement
3. Update `project_templates/` internal references to `project/`
4. Update `CLAUDE.md` documentation of directory structure
5. Update `claude/commands/*.md` commands referencing `project/` paths
6. Update `claude/agents/*.md` agents referencing `project/` paths
7. Rename existing `project/` directory in this repo to `modeling_pm/`
8. Keep same subdirectory structure (`backlog/`, `research/`, `active/`)

### Out of Scope

- Automated migration tooling (only fusion-tea uses this; will be migrated manually)
- Changes to `.project/` directory (that naming is fine)
- Any changes to subdirectory names within the renamed directory

### Edge Cases & Considerations

- Grep/search for `project/` may have false positives (e.g., "project" as a word, `.project/` references) - must be careful during implementation
- Template files may have `project/` in content that should become `modeling_pm/`

---

## Requirements

### Functional Requirements

> Requirements below are from user's request (backlog item ITEM-RENAME-001)

1. **FR-1**: CLI `cmd_init()` MUST create `modeling_pm/` directory instead of `project/`
2. **FR-2**: `replicate_setup.sh` MUST create `modeling_pm/` directory instead of `project/`
3. **FR-3**: All template files MUST reference `modeling_pm/` instead of `project/`
4. **FR-4**: `CLAUDE.md` MUST document the new directory name and its purpose
5. **FR-5**: All Claude commands referencing `project/` paths MUST be updated to `modeling_pm/`
6. **FR-6**: All Claude agents referencing `project/` paths MUST be updated to `modeling_pm/`
7. **FR-7**: Existing `project/` directory in repo MUST be renamed to `modeling_pm/`

---

## Acceptance Criteria

### Core Functionality

- [ ] `uv run agentic-mbse init` creates `modeling_pm/` (not `project/`)
- [ ] `modeling_pm/` contains same structure: `OVERVIEW.md`, `MODELING_GUIDE.md`, `MODELING_PROCESS.md`, `backlog/`, etc.
- [ ] `scripts/replicate_setup.sh` works correctly with new directory name
- [ ] All grep for `project/OVERVIEW` or similar in commands/agents returns no hits (replaced with `modeling_pm/`)

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] `CLAUDE.md` directory clarification table reflects new naming
- [ ] No broken references to old `project/` path remain

---

## Files to Update

From backlog analysis:

| File | Change |
|------|--------|
| `src/agentic_mbse/cli/__init__.py` | Update `cmd_init()` output paths |
| `scripts/replicate_setup.sh` | Update directory creation and file placement |
| `project_templates/*.template` | Update any internal `project/` references |
| `CLAUDE.md` | Update directory structure documentation |
| `claude/commands/*.md` | Update path references |
| `claude/agents/*.md` | Update path references |
| `project/` → `modeling_pm/` | Rename directory |

---

## Related Artifacts

- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-RENAME-001)
- **Design:** `.project/active/project-rename/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
