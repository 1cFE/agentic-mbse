# Spec: Development Mode for Init Command

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-15 19:56:27 UTC
**Complexity:** LOW
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters

When developing agentic-mbse alongside a test domain project (e.g., fusion-tea), the current workflow requires manual synchronization. Changes made to commands, agents, or templates in the agentic-mbse repo must be re-installed via `init`, and changes made directly in the domain project must be manually backported. This creates friction, risks drift between locations, and wastes developer time.

### Success Criteria

- [ ] Developer can edit a command in agentic-mbse and immediately see the change in the domain project
- [ ] Developer can identify at a glance whether a project was initialized in dev mode (via `ls -la` showing symlinks)
- [ ] Re-running `init --dev` updates symlinks cleanly without errors

### Priority

P1 (High) - Directly supports agentic-mbse development velocity. Blocks efficient iteration on commands/agents/templates.

**Related backlog item:** ITEM-DEVMODE-001

---

## Problem Statement

### Current State

`agentic-mbse init` copies all files from the source repo to the target project:
- Commands → `.claude/commands/`
- Agents → `.claude/agents/`
- Skills → `.claude/skills/`
- Hooks → `.claude/hooks/`
- Templates → `project/`

This means:
1. Changes in agentic-mbse require re-running `init` to propagate
2. Changes made in domain project are disconnected from source
3. Backporting requires manual diff/merge work

### Desired Outcome

A `--dev` flag that creates symlinks for tool-owned files instead of copies, enabling bidirectional synchronization:
- Edit in agentic-mbse → change visible in domain project immediately
- Edit in domain project → change visible in agentic-mbse immediately (same file)

---

## Scope

### In Scope

1. **`--dev` CLI flag** for the `init` subcommand
2. **Symlink creation** for all TOOL_OWNED files when `--dev` is specified
3. **Source checkout detection** - error if `--dev` used with pip-installed package
4. **Idempotent symlink handling** - re-running `--dev` removes existing file/symlink and creates fresh symlink
5. **Summary output** indicating symlink vs copy status (format deferred to design)

### Out of Scope

- **Windows support**: `--dev` mode is not supported on Windows due to symlink permission requirements. The command MUST error with a clear message on Windows.
- **`--repo` flag**: Source path auto-detection only; no explicit repo path override.
- **Watch mode**: No auto-reload or file watching for changes.
- **`replicate_setup.sh` changes**: Coordination may be needed but is separate work.

### Edge Cases & Considerations

- **Target file exists as regular file**: Remove and replace with symlink
- **Target file exists as symlink (possibly stale)**: Remove and create new symlink
- **Source file missing**: Skip with warning (existing behavior)
- **Mixed mode (some symlinked, some copied)**: Not supported; `--dev` applies to all tool-owned files
- **Git tracking**: Symlinks use absolute paths (machine-specific), so tool-owned paths must be gitignored to prevent broken symlinks when others clone the repo

---

## Requirements

### Functional Requirements

> Requirements below are from user's research document (ITEM-DEVMODE-001)

1. **FR-1**: The `init` subcommand MUST accept a `--dev` flag
2. **FR-2**: When `--dev` is specified, tool-owned files MUST be created as symlinks pointing to the source repo's absolute paths
3. **FR-3**: When `--dev` is specified, user-owned files MUST still be copied (never symlinked)
4. **FR-4**: When `--dev` is specified on a pip-installed package (no source checkout), the command MUST exit with an error message explaining that dev mode requires a source checkout
5. **FR-5**: When `--dev` is specified on Windows, the command MUST exit with an error message explaining that dev mode is not supported on Windows
6. **FR-6**: Re-running `init --dev` MUST be idempotent - existing files or symlinks at target paths MUST be removed before creating new symlinks
7. **FR-7**: Summary output MUST distinguish between symlinked and copied files
8. **FR-8**: When `--dev` is specified, tool-owned paths MUST be added to `.gitignore` to prevent committing machine-specific symlinks

### File Classification

| Category | Files | Behavior with `--dev` |
|----------|-------|----------------------|
| **TOOL_OWNED** | `MBSE_COMMANDS`, `MBSE_AGENTS`, `MBSE_SKILLS`, `MBSE_HOOKS`, `TOOL_OWNED_TEMPLATES` | Symlink |
| **USER_OWNED** | `.gitignore`, `SOURCE_INDEX.md`, `.claude/settings.json`, `USER_OWNED_TEMPLATES` | Copy (always) |

### Non-Functional Requirements

- **NFR-1**: Symlinks MUST use absolute paths (not relative) for reliability
- **NFR-2**: Error messages MUST be actionable (explain what to do instead)

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse init --dev /path/to/project` creates symlinks for tool-owned files
- [ ] `ls -la .claude/commands/design-model.md` shows symlink pointing to agentic-mbse source
- [ ] Editing `agentic-mbse/claude/commands/design-model.md` is immediately reflected in domain project
- [ ] User-owned files (`.gitignore`, `SOURCE_INDEX.md`, etc.) are copied, not symlinked
- [ ] Running `init --dev` twice in a row completes without error
- [ ] Running `init --dev` from pip-installed package shows error: "Dev mode requires source checkout"
- [ ] Running `init --dev` on Windows shows error: "Dev mode not supported on Windows"
- [ ] Running `init --dev` adds tool-owned paths to `.gitignore` (idempotent - doesn't duplicate if already present)

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] New tests cover: symlink creation, pip-install detection, Windows detection, idempotent behavior
- [ ] `init` without `--dev` behaves exactly as before (no regression)

---

## Related Artifacts

- **Research:** `project/research/20260113-150000_progressive-disclosure-architecture.md` (Part 2)
- **Design:** `.project/active/dev-mode-init/design.md` (to be created)
- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-DEVMODE-001)
- **Implementation:** `src/agentic_mbse/cli/__init__.py`

---

**Next Steps:** After approval, proceed to `/_my_design`
