# Spec: D3.3 Command Registration

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 15:32 UTC
**Complexity:** LOW
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-003 (Architecture Redesign — Commands)

---

## Business Goals

### Why This Matters

D3.2 created 5 new command files in `claude/commands/`, but they are not yet registered in the installation pipeline. Users who run `agentic-mbse init` on their projects will only get the 9 original commands — the new `/quick-model`, `/review-model`, `/analyze-models`, `/status`, and `/formalize-intent` commands are invisible to the installer. This is the mechanical step that makes all 14 commands available to target repos.

### Success Criteria

- [ ] `MBSE_COMMANDS` list includes all 14 commands
- [ ] `replicate_setup.sh` installs all 14 commands
- [ ] `agentic-mbse init /tmp/test-project` installs all 14 commands to `.claude/commands/`
- [ ] `agentic-mbse init --dev` creates symlinks for all 14 commands
- [ ] `agentic-mbse install-commands --list` shows all 14 commands
- [ ] All existing tests pass (`uv run pytest tests/`)

### Priority

P0. Blocks D3.5 (validation walkthrough). Depends on D3.1 (complete) and D3.2 (complete).

---

## Problem Statement

### Current State

`MBSE_COMMANDS` in `src/agentic_mbse/cli/__init__.py:18-28` lists 9 commands. `replicate_setup.sh` lines 55-58 has a matching 9-command install loop. The 5 new command files exist in `claude/commands/` but are not referenced by either installation pathway.

### Desired Outcome

Both installation pathways register all 14 commands and stay in sync with each other.

---

## Scope

### In Scope

1. Adding 5 entries to `MBSE_COMMANDS` in `cli/__init__.py`
2. Adding 5 entries to the command install loop in `replicate_setup.sh`
3. Verifying all installation pathways (`init`, `init --dev`, `install-commands`, `install-commands --list`)

### Out of Scope

- Modifying command file content (D3.2 — complete)
- Agent registration changes (D3.4)
- Validation walkthroughs (D3.5)
- PM engine or AP-7 scripts (Epic 4)

### Edge Cases & Considerations

- The `MBSE_COMMANDS` list is referenced in 4 code locations: modification checks (line 540), file installation (line 681), `--list` output (line 963), and `install-commands` (line 981). All 4 iterate over the same list, so a single list update covers all pathways.
- `replicate_setup.sh` has a separate hardcoded list that must be updated independently and kept in sync with `MBSE_COMMANDS`.

---

## Requirements

### Functional Requirements

> FR-1: `MBSE_COMMANDS` in `src/agentic_mbse/cli/__init__.py` MUST include all 14 commands: the 9 existing plus `analyze-models.md`, `formalize-intent.md`, `quick-model.md`, `review-model.md`, `status.md`.

Ref: delta-checklist.md § 3A.3 — "Add: quick-model.md, review-model.md, analyze-models.md, status.md, formalize-intent.md"

> FR-2: The command install loop in `scripts/replicate_setup.sh` MUST include the same 14 commands.

Ref: delta-checklist.md § 3A.3 — "replicate_setup.sh — Add new commands to the install loop"
Ref: CLAUDE.md Change Coordination — "Both handle the same set of commands... they must not diverge."

> FR-3: Both lists SHOULD be in alphabetical order for maintainability.

[INFERRED] The current `MBSE_COMMANDS` list is not alphabetical, but the epic's example (§ D3.3) shows alphabetical ordering. Alphabetical order makes it easy to verify the two lists match and to spot missing entries.

> FR-4: Both files MUST be updated in the same commit to prevent divergence.

Ref: implementation-plan.md § 7 Risk Register — "replicate_setup.sh and cmd_init() diverge... Update both in the same commit."

---

## Acceptance Criteria

### Core Functionality

- [ ] `MBSE_COMMANDS` contains exactly 14 entries (9 existing + 5 new)
- [ ] `replicate_setup.sh` install loop contains exactly 14 entries
- [ ] Both lists contain the same set of command filenames
- [ ] `uv run agentic-mbse install-commands --list` prints all 14 commands
- [ ] `uv run agentic-mbse init /tmp/test-d33` creates `.claude/commands/` with all 14 command files
- [ ] `uv run agentic-mbse init --dev` creates symlinks in `.claude/commands/` for all 14 commands (run from agentic-mbse repo root with no target directory argument, or per existing dev-mode convention)

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] No other code changes beyond the two list updates

---

## Related Artifacts

- **Epic**: `.project/backlog/epic_architecture-commands.md` (D3.3)
- **Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` § 3A.3
- **D3.2 Spec**: `.project/active/d3.2-new-commands/spec.md` (the commands being registered)
- **CLI Source**: `src/agentic_mbse/cli/__init__.py` (MBSE_COMMANDS at line 18)
- **Shell Script**: `scripts/replicate_setup.sh` (install loop at line 55)
- **CLAUDE.md**: Change Coordination section (replicate_setup.sh / cmd_init() sync requirement)

---

**Next Steps:** After approval, proceed to `/_my_implement` (no design or plan needed — this is a 2-file mechanical change).
