# Spec: Replicate Setup Script

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-09 21:30:50 UTC
**Complexity:** LOW
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters
As the library author, you need to dogfood the agentic-mbse toolkit within its own development repository. Currently there's no streamlined way to test Claude commands and modeling workflows locally after making changes. This creates friction in the development loop: change code → manually set up → test → repeat.

### Success Criteria
- [ ] Can run a single script to install/update all Claude components locally
- [ ] Can immediately use `/design-model`, `/plan-model`, etc. after running the script
- [ ] Re-running the script after pulling changes updates everything
- [ ] A test subject model exists to exercise the full workflow

### Priority
Development enablement - directly supports faster iteration on the core product.

---

## Problem Statement

### Current State
- `agentic-mbse init` exists for external users but targets new projects
- No quick way to self-install the toolkit in this repo for testing
- After code changes, manual steps needed to test updated commands/agents
- No example model exists for exercising the modeling workflow

### Why NOT use `agentic-mbse init`
The `init` command is designed for external user projects, not for dogfooding the library itself:

1. **Overwrites README.md** - The library has its own README; `init` would clobber it with a template
2. **Overwrites .gitignore** - The library has its own .gitignore; `init` would replace it
3. **Circular dependency** - Requires CLI to be installed before dev environment is set up

The script should replicate what `init` does for Claude components, but skip library-owned files.

### Desired Outcome
A `scripts/replicate_setup.sh` script that:
1. Installs Claude commands, agents, skills, hooks locally (directly, without calling CLI)
2. Pre-fills project context for immediate use
3. Provides a coffee maker test subject for modeling exercises
4. Is idempotent (safe to re-run after updates)
5. Does NOT overwrite library-owned files (README.md, .gitignore)

---

## Scope

### In Scope
- Shell script at `scripts/replicate_setup.sh`
- Directly copies Claude components (no CLI dependency):
  - `claude/commands/*.md` → `.claude/commands/`
  - `claude/agents/*.md` → `.claude/agents/` (no modification needed)
  - `claude/skills/*` → `.claude/skills/`
  - `claude/hooks/*` → `.claude/hooks/`
- Creates `agent_literature/` with symlinks to `docs/` (so agent paths work as-is)
- Generates `.claude/settings.json` with agent_literature permissions
- Copies essential templates:
  - `project_templates/MODELING_GUIDE.md.template` → `project/MODELING_GUIDE.md`
  - `project_templates/MODELING_PROCESS.md.template` → `project/MODELING_PROCESS.md`
- Pre-fills `SOURCE_INDEX.md` referencing `agent_literature/` as the domain source
- Pre-fills `project/OVERVIEW.md` with coffee maker test subject
- Creates `models/library/` directory structure for the test model
- Updates `CLAUDE.md` to document related concepts

### Out of Scope
- Creating/managing `.env` file (user responsibility)
- Running `/onboard` or other interactive flows
- CI/CD integration
- Full coffee maker SysML implementation (just scaffold)
- Modifying README.md or .gitignore (library owns these)

### Edge Cases & Considerations
- Script should work whether or not `.claude/` already exists
- Script should not fail if `models/` already has content
- Should warn (not error) if syside license key is missing

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED]

**Script Requirements:**
1. **FR-1**: Script MUST be a shell script located at `scripts/replicate_setup.sh`
2. **FR-2**: Script MUST NOT call `agentic-mbse` CLI (no circular dependency)
3. **FR-3**: Script MUST be idempotent (safe to re-run after pulling changes)
4. **FR-4**: [INFERRED] Script SHOULD check for `.env` with `SYSIDE_LICENSE_KEY` and warn if missing

**Claude Component Installation:**
5. **FR-5**: Script MUST copy `claude/commands/*.md` to `.claude/commands/`
6. **FR-6**: Script MUST copy `claude/agents/*.md` to `.claude/agents/` (no modification)
7. **FR-7**: Script MUST copy `claude/skills/*` to `.claude/skills/` (recursive)
8. **FR-8**: Script MUST copy `claude/hooks/*` to `.claude/hooks/` (preserve executable permissions)
9. **FR-9**: Script MUST generate `.claude/settings.json` with Read/Grep/Glob permissions for `agent_literature/`

**Agent Literature Setup:**
10. **FR-10**: Script MUST create `agent_literature/` directory structure matching agent expectations:
    - `agent_literature/SysML/` → symlink or copy from `docs/sysmlv2/`
    - `agent_literature/syside-docs/v0.8.1/` → symlink or copy from `docs/syside/`

**Project Structure:**
11. **FR-11**: Script MUST copy `project_templates/MODELING_GUIDE.md.template` → `project/MODELING_GUIDE.md`
12. **FR-12**: Script MUST copy `project_templates/MODELING_PROCESS.md.template` → `project/MODELING_PROCESS.md`
13. **FR-13**: Script MUST create `project/backlog/`, `project/active/`, `project/research/` directories
14. **FR-14**: Script MUST pre-fill `SOURCE_INDEX.md` pointing to `agent_literature/` as the domain source
15. **FR-15**: Script MUST pre-fill `project/OVERVIEW.md` with coffee maker test subject description
16. **FR-16**: Script MUST create `models/library/` directory for the test model

**Documentation Updates:**
17. **FR-17**: MUST update `CLAUDE.md` to explain `project/` vs `.project/` directories
18. **FR-18**: MUST update `CLAUDE.md` to document change coordination between `replicate_setup.sh` and `init`

### Non-Functional Requirements

- Script should complete in under 5 seconds
- Script should provide clear output indicating what was done

### Change Coordination

When modifying either `replicate_setup.sh` or `cmd_init()` in `src/agentic_mbse/cli/__init__.py`:
- Review if the same change is needed in the other
- The script replicates `init` logic for Claude components but skips library-owned files
- Both must handle the same set of commands, agents, skills, and hooks
- `init` does path substitution in agents; `replicate_setup.sh` creates `agent_literature/` symlinks instead

---

## Acceptance Criteria

### Core Functionality
- [ ] Running `./scripts/replicate_setup.sh` installs all Claude components to `.claude/`
- [ ] Script does NOT require `agentic-mbse` CLI to be installed
- [ ] After running, `/design-model`, `/plan-model`, `/implement-model` commands are available
- [ ] `agent_literature/SysML/` exists and contains SysML docs (symlink to `docs/sysmlv2/`)
- [ ] `agent_literature/syside-docs/v0.8.1/` exists and contains syside docs (symlink to `docs/syside/`)
- [ ] `.claude/settings.json` has Read/Grep/Glob permissions for `agent_literature/`
- [ ] `SOURCE_INDEX.md` references `agent_literature/` as a source
- [ ] `project/OVERVIEW.md` describes the coffee maker test subject
- [ ] `project/MODELING_GUIDE.md` and `project/MODELING_PROCESS.md` exist
- [ ] `models/library/` directory exists for the test model
- [ ] Re-running the script updates all components without errors

### Quality & Integration
- [ ] Existing tests continue to pass
- [ ] Script works from repo root directory
- [ ] Script provides meaningful output (what was installed/updated)
- [ ] README.md and .gitignore are NOT modified

### Documentation
- [ ] `CLAUDE.md` explains `project/` vs `.project/` directories
- [ ] `CLAUDE.md` documents change coordination between `replicate_setup.sh` and `init`

---

## Test Subject: Coffee Maker

A simple drip coffee maker with these components for modeling exercises:

**Parts:**
- Water reservoir
- Heating element
- Pump
- Brew basket (filter holder)
- Carafe
- Control panel (on/off, brew button)

**Behaviors:**
- Fill reservoir → Heat water → Pump to brew basket → Drip into carafe
- Temperature control (maintain brew temp)
- Auto-shutoff after brewing complete

**Why this subject:**
- Familiar to most people
- 5-7 components (right complexity)
- Clear data flows (water, heat, control signals)
- Natural requirements (brew time, temperature, capacity)

---

## Related Artifacts

- **Research:** N/A (codebase investigation done inline)
- **Design:** `.project/active/replicate-setup/design.md`
- **Reference Implementation:** `src/agentic_mbse/cli/__init__.py:182-432` (`cmd_init` function)

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `scripts/replicate_setup.sh` | Create | Main script (no CLI dependency) |
| `CLAUDE.md` | Modify | Add `project/` vs `.project/` explanation; add change coordination note |
| `agent_literature/SysML/` | Create | Symlink to `docs/sysmlv2/` |
| `agent_literature/syside-docs/v0.8.1/` | Create | Symlink to `docs/syside/` |
| `SOURCE_INDEX.md` | Create | Pre-filled, references `agent_literature/` |
| `project/OVERVIEW.md` | Create | Coffee maker description |
| `project/MODELING_GUIDE.md` | Create | Copy from template |
| `project/MODELING_PROCESS.md` | Create | Copy from template |
| `project/backlog/` | Create | Directory structure |
| `project/active/` | Create | Directory structure |
| `project/research/` | Create | Directory structure |
| `.claude/commands/*.md` | Create | Copy from `claude/commands/` |
| `.claude/agents/*.md` | Create | Copy from `claude/agents/` (no modification) |
| `.claude/skills/*` | Create | Copy from `claude/skills/` |
| `.claude/hooks/*` | Create | Copy from `claude/hooks/` |
| `.claude/settings.json` | Create | Generated with `agent_literature/` permissions |
| `models/library/` | Create | Directory for test model |

---

## Directory Clarification

This repo has two similar-looking directories that serve different purposes:

| Directory | Purpose | Committed to Git |
|-----------|---------|------------------|
| `.project/` | Internal development project management (specs, designs, backlog) | Yes |
| `project/` | Dogfooding test subject documentation (OVERVIEW.md, MODELING_GUIDE.md) | Created by script |

---

**Next Steps:** After approval, proceed to `/_my_design`
