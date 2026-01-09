# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

agentic-mbse is a domain-agnostic Model-Based Systems Engineering (MBSE) toolkit for AI-assisted systems engineering. It provides SysML v2 model validation and Claude Code slash commands/agents for guided modeling workflows.

## Development Commands

```bash
# Install in development mode (creates agentic-mbse CLI)
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_cli.py

# Run a specific test
pytest tests/test_cli.py::test_init_creates_files -v

# Run tests with coverage
pytest --cov=src/agentic_mbse tests/

# Type checking
mypy src/

# Linting and formatting (ruff)
ruff check src/ tests/
ruff format src/ tests/
```

## CLI Usage

```bash
# Validate SysML models (default path: models/)
agentic-mbse validate models/

# Run specific validation level (1-8)
agentic-mbse validate --level=3 models/

# Initialize new MBSE project with templates and commands
agentic-mbse init [path]

# List available MBSE commands
agentic-mbse install-commands --list
```

## Architecture

### Core Modules (`src/agentic_mbse/`)

- **cli/**: CLI entry point (`agentic-mbse` command). Handles `validate`, `init`, and `install-commands` subcommands. The `init` command installs Claude commands, agents, skills, and project templates.

- **validation/**: 8-level quality validation pyramid for SysML models:
  - Level 1: Syntax validation (via syside parser)
  - Level 2: Structural completeness (parts, ports, connections)
  - Level 3: Dataflow integrity (binding consistency)
  - Level 4: Constraint satisfaction (assert/require statements)
  - Level 5: Semantic consistency (unit compatibility, type matching)
  - Level 6: Traceability & documentation (requirements linking)
  - Level 7: Architectural integrity (subsystem boundaries)
  - Level 8: Code generation readiness (completeness for codegen)

- **sysml/**: SysML model analysis utilities:
  - `syside_adapter.py`: Wrapper around syside library for parsing SysML v2
  - `expression.py`: Expression tree traversal and analysis
  - `binding.py`: Port/attribute binding classification
  - `graph.py`: Dependency cycle detection and topological sort
  - `types.py`: ValidationIssue, BindingInfo, and other type definitions

### Claude Integration (`claude/`)

The toolkit includes Claude Code slash commands and agents installed via `agentic-mbse init`:

- **commands/**: MBSE workflow commands (`/design-model`, `/plan-model`, `/implement-model`, `/spec-model`, `/research`, `/audit-models`, `/onboard`, `/manage-sources`, `/backlog`)
- **agents/**: Specialized agents (`python-debugger.md`, `sysmlv2-doc-analyzer.md`)
- **skills/**: Reusable skill definitions
- **hooks/**: Git hooks (e.g., `ruff-format.sh`)

### Project Templates (`project_templates/`)

Templates installed by `init` command to bootstrap new MBSE projects:
- `README.md.template` → `README.md`
- `OVERVIEW.md.template` → `project/OVERVIEW.md`
- `MODELING_GUIDE.md.template` → `project/MODELING_GUIDE.md`
- `MODELING_PROCESS.md.template` → `project/MODELING_PROCESS.md`
- `BACKLOG.md.template` → `project/backlog/BACKLOG.md`

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
