# Design: Replicate Setup Script

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-09 21:36:19 UTC
**Branch:** 1cfe_dev

---

## Overview

A shell script that self-installs the agentic-mbse toolkit within its own repository for dogfooding, wrapping the existing `agentic-mbse init` command and pre-filling context files for the coffee maker test subject.

---

## Related Artifacts

- **Spec:** `.project/active/replicate-setup/spec.md`
- **Implementation Reference:** `src/agentic_mbse/cli/__init__.py:182-432` (cmd_init function)

---

## Research Findings

### Existing `init` Command Behavior

The `cmd_init()` function at `src/agentic_mbse/cli/__init__.py:182-432` provides:

1. **Idempotent operation** - Skips existing files unless `--force` is used (line 211, 276, 307, etc.)
2. **Track created vs skipped** - Lists `created[]` and `skipped[]` at end (lines 206-207, 410-431)
3. **Force flag** - `--force` overwrites all files (line 533-534)
4. **Path detection** - `_get_data_root()` (lines 52-72) already handles source checkout vs pip install

### What `init` Creates

| Item | Source | Destination |
|------|--------|-------------|
| Commands (9) | `claude/commands/*.md` | `.claude/commands/` |
| Agents (2) | `claude/agents/*.md` | `.claude/agents/` (with path substitution) |
| Skills (1) | `claude/skills/python-debugger/` | `.claude/skills/` |
| Hooks (1) | `claude/hooks/ruff-format.sh` | `.claude/hooks/` |
| Settings | Generated | `.claude/settings.json` |
| Templates (5) | `project_templates/` | `project/`, `README.md` |
| Source Index | `SOURCE_INDEX.md.template` | `SOURCE_INDEX.md` |
| Gitignore | Inline content | `.gitignore` |

### Template File Analysis

**`SOURCE_INDEX.md.template`** (56 lines):
- Contains placeholder comments showing example sources
- Has "(No primary sources configured yet)" placeholder text
- Needs pre-filling with self-referential docs path

**`OVERVIEW.md.template`** (172 lines):
- Uses `<!-- placeholder -->` format throughout
- Key placeholders: project name, purpose, status, structure
- Comprehensive template - we only need to fill key fields for dogfooding

### Directory Structure

No `scripts/` directory currently exists - will create it.

---

## Proposed Design

### High-Level Architecture

```
scripts/replicate_setup.sh
├── Check prerequisites (agentic-mbse installed)
├── Run: agentic-mbse init . --force
├── Create: models/library/ directory
├── Overwrite: SOURCE_INDEX.md (pre-filled)
└── Overwrite: project/OVERVIEW.md (pre-filled)
```

### Script: `scripts/replicate_setup.sh`

**Purpose:** Self-install agentic-mbse toolkit for local dogfooding

**Location:** `scripts/replicate_setup.sh`

**Execution:** `./scripts/replicate_setup.sh` from repo root

**Behavior:**

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Verify running from repo root
#    Check for pyproject.toml with "agentic-mbse" name

# 2. Check agentic-mbse is installed
#    Run: command -v agentic-mbse
#    Suggest: pip install -e ".[dev]" if missing

# 3. Check .env for SYSIDE_LICENSE_KEY (warn only)
#    grep SYSIDE_LICENSE_KEY .env 2>/dev/null

# 4. Run init with force
#    agentic-mbse init . --force

# 5. Create models/library/ if missing
#    mkdir -p models/library

# 6. Write pre-filled SOURCE_INDEX.md
#    Heredoc with self-referential content

# 7. Write pre-filled project/OVERVIEW.md
#    Heredoc with coffee maker content

# 8. Print summary
```

### Pre-filled `SOURCE_INDEX.md`

Content pointing to this repo's bundled docs as the domain source:

```markdown
# Source Index

This file tells MBSE commands where to find domain knowledge sources.
Commands read this file to discover what references are available for research and validation.

## Primary Sources

### SysML v2 Specification
- **Type**: documentation
- **Location**: docs/sysmlv2/
- **Use for**: SysML syntax, semantics, and best practices
- **Validation**: N/A (reference only)

### syside Library Documentation
- **Type**: documentation
- **Location**: docs/syside/
- **Use for**: Parser API, CLI usage, integration patterns
- **Validation**: N/A (reference only)

### agentic-mbse Source Code
- **Type**: codebase
- **Location**: src/agentic_mbse/
- **Use for**: Understanding validation logic, CLI behavior, adapter patterns
- **Validation**: Compare model outputs against validation pyramid

## How This File Is Used

MBSE commands (design-model, plan-model, implement-model, audit-models) read this file to:

1. **Discover** what reference sources exist for your domain
2. **Research** by exploring codebase sources and reading documentation
3. **Validate** by comparing model outputs against baseline sources

## Test Subject

This project uses a **Coffee Maker** as the test subject for exercising MBSE workflows.
See `project/OVERVIEW.md` for the system description.
```

### Pre-filled `project/OVERVIEW.md`

Content describing the coffee maker test subject:

```markdown
# Project Overview

**Project**: Coffee Maker Model (Dogfooding Test Subject)
**Purpose**: Exercise agentic-mbse MBSE workflows with a simple, familiar system
**Start Date**: 2026-01-09
**Status**: Active

---

## What We're Building

SysMLv2 models of a **drip coffee maker** that enable:

1. **Structural Modeling** - Component hierarchy (reservoir, heater, pump, brew basket, carafe, controls)
2. **Behavioral Modeling** - Brew cycle state machine and control logic
3. **Physics Integration** - Heat transfer, fluid flow, temperature control
4. **Validation Framework** - Constraint checking for temperature limits, timing, capacity

**Reference Implementation**: Simple drip coffee maker (~10 cup capacity)
**Validation Baseline**: Physical constraints (water boiling point, safe temperatures)

---

## System Description

### Components

| Part | Function | Key Attributes |
|------|----------|----------------|
| Water Reservoir | Store water for brewing | capacity (L), currentLevel (L) |
| Heating Element | Heat water to brew temperature | power (W), maxTemp (°C) |
| Pump | Move water from reservoir to brew basket | flowRate (L/min) |
| Brew Basket | Hold filter and coffee grounds | capacity (g) |
| Carafe | Collect brewed coffee | capacity (L), keepWarmTemp (°C) |
| Control Panel | User interface (on/off, brew) | brewButton, powerSwitch |

### Behaviors

1. **Idle** - System off, waiting for user
2. **Heating** - Water heating to brew temperature (92-96°C)
3. **Brewing** - Pump active, water flowing through grounds
4. **Keep Warm** - Heating element maintains carafe temperature
5. **Auto-Shutoff** - Turn off after timeout (safety feature)

### Data Flows

```
[Reservoir] --water--> [Pump] --water--> [Brew Basket] --coffee--> [Carafe]
                          ^                                            |
[Heater] ----heat--------+--------------------------------------------+
                          ^
[Controls] ---signals----+
```

---

## Why This Test Subject?

- **Familiar** - Everyone knows how a coffee maker works
- **Right complexity** - 5-7 components, clear interfaces
- **Multiple domains** - Thermal, fluid, electrical, control
- **Natural requirements** - Temperature, timing, capacity, safety
- **Exercisable** - Can run through full design/plan/implement cycle

---

## Technology Stack

**Core Tools**:
- **SysIDE** - SysML v2 parsing and validation (via `syside` CLI)
- **Python 3.11+** - Scripting and analysis
- **Git** - Version control
- **agentic-mbse** - MBSE workflow commands and validation

**Model Organization**:
```
models/
├── library/           # Reusable definitions (start here)
│   ├── definitions/   # CoffeeMaker parts
│   ├── calculations/  # Thermal, flow calculations
│   └── materials/     # (if needed)
├── designs/           # Specific configurations
│   └── basic-drip/    # 10-cup drip coffee maker
└── tests/             # Test and validation models
```

---

## Success Criteria

### Must Have (Dogfooding Validation)
- [ ] Can run `/design-model` on coffee maker subject
- [ ] Can run `/plan-model` to create implementation plan
- [ ] Can run `/implement-model` to generate SysML files
- [ ] Can run `/audit-models` to validate against sources
- [ ] `agentic-mbse validate models/` passes level 1-2

### Should Have
- [ ] Physics constraints (temperature limits) defined
- [ ] Behavior state machine modeled
- [ ] At least one design instance created

---

## Current Status

**Active Work Item**: Initial setup via replicate_setup.sh
**Status**: Ready for modeling
**Next Up**: Run `/design-model` to create coffee maker design document

---

## Getting Started

**For dogfooding this library**:
1. Run `./scripts/replicate_setup.sh` to install Claude commands
2. Ensure `.env` has `SYSIDE_LICENSE_KEY`
3. Start with `/design-model` to create the coffee maker design doc
4. Follow the MBSE workflow: design → plan → implement → audit

---

**Last Updated**: 2026-01-09
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| Not in repo root | Exit with error, show expected location |
| `agentic-mbse` not installed | Exit with error, show install command |
| `.env` missing or no license key | Warn but continue |
| `models/` has content | Continue (mkdir -p is safe) |

### Output Messages

```
=== agentic-mbse dogfood setup ===

Checking prerequisites...
  [OK] Running from repo root
  [OK] agentic-mbse installed
  [WARN] .env missing SYSIDE_LICENSE_KEY (validation will fail)

Running: agentic-mbse init . --force
[init output here]

Creating test subject structure...
  + models/library/

Pre-filling context files...
  + SOURCE_INDEX.md (self-referential)
  + project/OVERVIEW.md (coffee maker)

=== Setup complete ===

Next steps:
  1. Add SYSIDE_LICENSE_KEY to .env (if not done)
  2. Run: /design-model to start designing the coffee maker
  3. Follow workflow: design → plan → implement → audit
```

---

## Potential Risks

| Risk | Mitigation |
|------|-----------|
| Script overwrites user customizations | Use `--force` intentionally; document this behavior |
| `agentic-mbse` not on PATH | Check explicitly and provide install command |
| Path issues on different shells | Use `#!/usr/bin/env bash` and `set -euo pipefail` |

---

## Integration Strategy

- Script lives in `scripts/` alongside any future dev scripts
- Does NOT modify `agentic-mbse init` - purely additive
- Can be run repeatedly after pulling changes to update Claude components
- Test subject (`models/library/`) is a scaffold, not a full implementation

---

## Validation Approach

**Manual testing:**
1. Run `./scripts/replicate_setup.sh` from repo root
2. Verify `.claude/commands/` contains all 9 commands
3. Verify `SOURCE_INDEX.md` has self-referential content
4. Verify `project/OVERVIEW.md` has coffee maker content
5. Verify `models/library/` exists
6. Run a Claude command (e.g., `/design-model`) to confirm it works

**Regression:**
- Existing tests in `tests/` should continue to pass (script doesn't modify src/)

---

**Next Step:** After approval → `/_my_implement`
