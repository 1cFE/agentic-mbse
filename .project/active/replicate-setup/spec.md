# Spec: Replicate Setup Script

**Status:** Draft
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

### Desired Outcome
A `scripts/replicate_setup.sh` script that:
1. Installs Claude commands, agents, skills, hooks locally
2. Pre-fills project context for immediate use
3. Provides a coffee maker test subject for modeling exercises
4. Is idempotent (safe to re-run after updates)

---

## Scope

### In Scope
- Shell script at `scripts/replicate_setup.sh`
- Calls `agentic-mbse init . --force` to install Claude components
- Pre-fills `SOURCE_INDEX.md` with self-referential docs (this repo's `docs/`)
- Pre-fills `project/OVERVIEW.md` with coffee maker test subject
- Creates `models/library/` directory structure for the test model
- Skips interactive commands (`/onboard`, `/manage-sources`) entirely

### Out of Scope
- Creating/managing `.env` file (user responsibility)
- Running `/onboard` or other interactive flows
- Modifying the `init` command itself
- CI/CD integration
- Full coffee maker SysML implementation (just scaffold)

### Edge Cases & Considerations
- Script should work whether or not `.claude/` already exists
- Script should not fail if `models/` already has content
- Should warn (not error) if syside license key is missing

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED]

1. **FR-1**: Script MUST be a shell script located at `scripts/replicate_setup.sh`
2. **FR-2**: Script MUST call `agentic-mbse init . --force` to install Claude components
3. **FR-3**: Script MUST pre-fill `SOURCE_INDEX.md` pointing to this repo's `docs/` as the domain source
4. **FR-4**: Script MUST pre-fill `project/OVERVIEW.md` with coffee maker test subject description
5. **FR-5**: Script MUST create `models/library/` directory for the test model
6. **FR-6**: Script MUST be idempotent (safe to re-run after pulling changes)
7. **FR-7**: [INFERRED] Script SHOULD skip `/onboard` and `/manage-sources` commands (non-interactive)
8. **FR-8**: [INFERRED] Script SHOULD check for `.env` with `SYSIDE_LICENSE_KEY` and warn if missing

### Non-Functional Requirements

- Script should complete in under 5 seconds
- Script should provide clear output indicating what was done

---

## Acceptance Criteria

### Core Functionality
- [ ] Running `./scripts/replicate_setup.sh` installs all Claude components to `.claude/`
- [ ] After running, `/design-model`, `/plan-model`, `/implement-model` commands are available
- [ ] `SOURCE_INDEX.md` references this repo's bundled docs as a source
- [ ] `project/OVERVIEW.md` describes the coffee maker test subject
- [ ] `models/library/` directory exists for the test model
- [ ] Re-running the script updates all components without errors

### Quality & Integration
- [ ] Existing tests continue to pass
- [ ] Script works from repo root directory
- [ ] Script provides meaningful output (what was installed/updated)

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
- **Design:** `.project/active/replicate-setup/design.md` (to be created)
- **Implementation:** `src/agentic_mbse/cli/__init__.py` (existing init command)

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `scripts/replicate_setup.sh` | Create | Main script |
| `SOURCE_INDEX.md` | Overwrite | Pre-filled for dogfooding |
| `project/OVERVIEW.md` | Overwrite | Coffee maker description |
| `models/library/.gitkeep` | Create | Placeholder for test model |

---

**Next Steps:** After approval, proceed to `/_my_design`
