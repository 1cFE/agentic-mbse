# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

agentic-mbse is a domain-agnostic Model-Based Systems Engineering (MBSE) toolkit for AI-assisted systems engineering. It provides SysML v2 model validation and Claude Code slash commands/agents for guided modeling workflows.

## Critical: Two Contexts

This repo serves TWO distinct purposes, and confusing them will lead to incorrect work. Read this carefully.

### Context A: Developing agentic-mbse (THIS repo)

When working on the agentic-mbse codebase itself:
- **What you're doing**: Writing Python code, CLI logic, validation algorithms
- **Project management**: `.project/` directory (specs, designs, backlog)
- **Workflow commands**: Developer's personal commands (e.g., `/_my_spec`, `/_my_plan`) - these are NOT part of agentic-mbse
- **Tests**: `tests/` directory - pytest tests for the Python library

### Context B: Target repos (SysML modeling projects)

When discussing what agentic-mbse provides to its users:
- **Target repo**: Any SysML modeling project that runs `agentic-mbse init`
- **What users do**: Build SysML v2 models using guided workflows
- **Project management**: `knowledge/`, `modeling_project/`, `work/`, `data/` directories
- **Workflow commands**: The MBSE commands we ship in `claude/commands/`:
  - `/spec-model` - requirements and success criteria for models
  - `/design-model` - model architecture decisions
  - `/plan-model` - implementation planning with phases
  - `/implement-model` - executing the plan, writing SysML
- **Tests**: (future) `tests/models/` - pytest tests that validate SysML models

### Terminology

| Term | Meaning |
|------|---------|
| **"commands"** | The MBSE commands in `claude/commands/` that we ship, unless explicitly stated otherwise |
| **"target repo"** | A SysML modeling project that installs agentic-mbse and inherits `claude/` and `project_templates/` |
| **"spec", "plan", "implement"** | In modeling context, these refer to `/spec-model`, `/plan-model`, `/implement-model` - NOT personal dev workflow commands |

### Why This Matters

When a work item says "the spec should include evaluatable success criteria" or "the plan should add test phases":
- **CORRECT**: Modify `claude/commands/spec-model.md` or `claude/commands/plan-model.md`
- **WRONG**: Assume it means personal dev commands like `/_my_spec` or `/_my_plan`

The personal dev workflow commands are used to develop THIS repo but are not shipped to users.

## Development Commands

This project uses **uv** for dependency management. All commands should be run via `uv run`.

```bash
# Install dependencies and set up development environment
uv sync

# Run tests (skips slow corpus tests by default)
uv run pytest tests/

# Run ALL tests including slow corpus integration tests
uv run pytest tests/ -m ""

# Run only the slow corpus tests
uv run pytest tests/ -m slow

# Run a single test file
uv run pytest tests/test_cli.py

# Run a specific test
uv run pytest tests/test_cli.py::test_init_creates_files -v

# Run tests with coverage
uv run pytest --cov=src/agentic_mbse tests/

# Type checking
uv run mypy src/

# Linting and formatting (ruff)
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## CLI Usage

```bash
# Validate SysML models (default path: models/)
uv run agentic-mbse validate models/

# Run specific validation level (1-6)
uv run agentic-mbse validate --level=3 models/

# Initialize new MBSE project with templates and commands
uv run agentic-mbse init [path]

# List available MBSE commands
uv run agentic-mbse install-commands --list
```

## Architecture

### Core Modules (`src/agentic_mbse/`)

- **cli/**: CLI entry point (`agentic-mbse` command). Handles `validate`, `init`, and `install-commands` subcommands. The `init` command installs Claude commands, agents, skills, and project templates.

- **validation/**: 6-level quality validation pyramid for SysML models:
  - Level 1: Syntax validation (via syside parser)
  - Level 2: Structural completeness (unused defs, unbound inputs)
  - Level 3: Dependency integrity (circular package imports)
  - Level 4: Constraint coverage (constraint counts, coverage metrics)
  - Level 5: Traceability & documentation (doc comment presence)
  - Level 6: Architecture & pipeline readiness (ADR-002, manifests, codegen)

- **sysml/**: SysML model analysis utilities:
  - `syside_adapter.py`: Wrapper around syside library for parsing SysML v2
  - `expression.py`: Expression tree traversal and analysis
  - `binding.py`: Port/attribute binding classification
  - `graph.py`: Dependency cycle detection and topological sort
  - `types.py`: ValidationIssue, BindingInfo, and other type definitions

### Claude Integration (`claude/`)

The toolkit includes Claude Code slash commands and agents installed via `agentic-mbse init`:

- **commands/**: MBSE workflow commands (`/design-model`, `/plan-model`, `/implement-model`, `/spec-model`, `/research`, `/audit-models`, `/onboard`, `/manage-sources`, `/backlog`)
- **agents/**: Specialized agents (`python-debugger.md`, `kerml-expert.md`, `sysml-expert.md`, `syside-expert.md`, `sysmlv2-validator.md`)
- **skills/**: Reusable skill definitions
- **hooks/**: Git hooks (e.g., `ruff-format.sh`)

### Project Templates (`project_templates/`)

Templates installed by `init` command to bootstrap new MBSE projects:

**User-owned** (created once, preserved on re-init):
- `README.md.template` → `README.md`
- `OVERVIEW.md.template` → `modeling_project/OVERVIEW.md`
- `BACKLOG.md.template` → `work/BACKLOG.md`
- `KNOWLEDGE.md.template` → `knowledge/KNOWLEDGE.md`
- `ARCHITECTURE.md.template` → `modeling_project/ARCHITECTURE.md`
- `REQUIREMENTS.md.template` → `modeling_project/REQUIREMENTS.md`
- `VALIDATION_MATRIX.md.template` → `modeling_project/VALIDATION_MATRIX.md`
- `RAW_LEARNINGS.md.template` → `work/learnings/RAW_LEARNINGS.md`

**Tool-owned** (updated on every re-init):
- `MODELING_GUIDE.md.template` → `modeling_project/MODELING_GUIDE.md`
- `MODELING_PROCESS.md.template` → `modeling_project/MODELING_PROCESS.md`
- `EPIC_GUIDE.md.template` → `work/EPIC_GUIDE.md`
- `epic_template.md.template` → `work/backlog/epic_template.md`

**Data templates** (user-owned):
- `data/traceability_matrix.csv` → `data/traceability_matrix.csv`

### Documentation (`docs/`)

- **sysmlv2/**: SysML v2 specifications and reference documentation
- **syside/**: syside library documentation
- **source-index.md**: Guide for configuring domain knowledge sources (`SOURCE_INDEX.md`)

## Key Dependencies

- **syside**: SysML v2 parser (installed from GitLab PyPI, requires `SYSIDE_LICENSE_KEY` in `.env`)
- **pydantic**: Data validation for model structures
- **pyyaml**: YAML parsing for configuration

## Claude Code Permission Paths

When generating `.claude/settings.json` permissions, path format matters:

| Format | Meaning |
|--------|---------|
| `~/path` | Relative to $HOME (recommended for portability) |
| `//path` | Absolute filesystem path |
| `/path` | Relative to settings.json file (NOT absolute!) |

Use `_to_claude_permission_path()` in `cli/__init__.py` to convert absolute paths correctly. It converts `/home/user/foo` → `~/foo` when under $HOME.

## Testing Structure

Tests mirror the source structure:
- `tests/test_cli.py`: CLI command tests
- `tests/test_sysml_quality_checks.py`: Validation level tests
- `tests/test_adapter.py`: syside adapter tests
- `tests/fixtures/`: Sample SysML models for testing

## Directory Clarification

See [Critical: Two Contexts](#critical-two-contexts) for the full distinction. Quick reference:

| Directory | Context | Purpose | Committed to Git |
|-----------|---------|---------|------------------|
| `.project/` | A (developing agentic-mbse) | Specs, designs, backlog for the Python library | Yes |
| `knowledge/` | B (target repo) | Domain insights, research, source index | No (created by init) |
| `modeling_project/` | B (target repo) | Architecture, requirements, overview, guides | No (created by init) |
| `work/` | B (target repo) | Backlog, active/completed work items, learnings | No (created by init) |
| `data/` | B (target repo) | Traceability matrix and structured data | No (created by init) |
| `claude/commands/` | B (shipped to target repos) | MBSE workflow commands users run | Yes |
| `tests/` | A (developing agentic-mbse) | pytest tests for Python code | Yes |

## Change Coordination

When modifying `scripts/replicate_setup.sh` or `cmd_init()` in `src/agentic_mbse/cli/__init__.py`:

1. Review if the same change is needed in the other
2. Both handle the same set of commands, agents, skills, and hooks (see `MBSE_COMMANDS`, `MBSE_AGENTS`, `MBSE_SKILLS`, `MBSE_HOOKS` in `cli/__init__.py`)
3. Both use the same placeholder substitution technique for agent paths

| File | Substitutes placeholders with |
|------|-------------------------------|
| `cmd_init()` | Absolute path to installed package's `docs/` |
| `replicate_setup.sh` | Absolute path to this repo's `docs/` |

## Init File Ownership

When adding new files to `cmd_init()`, categorize them as user-owned or tool-owned:

| Category | Behavior | Examples |
|----------|----------|----------|
| **User-owned** | Create once, skip on re-init (preserve customizations) | `knowledge/SOURCE_INDEX.md`, `modeling_project/OVERVIEW.md`, `work/BACKLOG.md`, `README.md`, `.gitignore`, `.claude/settings.json` |
| **Tool-owned** | Always update on re-init (get latest versions) | Commands, agents, skills, hooks, `modeling_project/MODELING_GUIDE.md`, `modeling_project/MODELING_PROCESS.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md` |

Use `--force` to overwrite user-owned files.

In code, use:
- `USER_OWNED_TEMPLATES` list for user-owned project templates
- `TOOL_OWNED_TEMPLATES` list for tool-owned project templates
- For non-template files, add existence check with `args.force` for user-owned, or always-update logic for tool-owned
