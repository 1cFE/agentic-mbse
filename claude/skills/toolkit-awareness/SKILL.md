---
name: toolkit-awareness
description: >
  This skill should be used when the user asks about "validation", "validate models",
  "run checks", "quality checks", "codegen readiness", "TEA pipeline", "how to validate",
  "run the pipeline", "toolkit", "available commands", "what tools do we have",
  or when answering questions about project workflow, build steps, or CI processes.
  Ensures Claude uses the actual installed toolchain instead of guessing commands.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# Toolkit Awareness

Ensure accurate knowledge of the project's installed tools before answering questions about validation, workflow, pipeline steps, or available commands.

## Core Principle

Never guess or fabricate CLI commands, validation steps, or workflow processes. Always ground answers in the project's actual `README.md` and installed toolchain.

## When This Skill Triggers

- Questions about validation, quality checks, or model correctness
- Questions about the project pipeline or workflow stages
- Questions about available CLI commands or slash commands
- Any time a shell command would be suggested to the user
- Planning or describing build/CI/pipeline processes

## Required Actions

### Before Answering Tooling Questions

1. **Read `README.md`** at the project root. This is the authoritative source for:
   - CLI commands and their flags
   - The 8-level validation framework
   - Slash commands available in Claude Code
   - Project setup and environment requirements

2. **Read `CLAUDE.md`** at the project root. This documents:
   - Python environment rules (`uv` requirement)
   - MBSE workflow steps
   - Domain sources and how to reference them

3. **Do not invent commands.** If a tool or command is not documented in README.md or CLAUDE.md, do not suggest it exists.

### Validation Framework

The project uses `agentic-mbse validate` with 8 quality levels. For complete details including level descriptions and blocking status, read the "Validation Framework" section of `README.md`.

Invocation patterns:
```bash
# All levels, fail-fast (default)
uv run agentic-mbse validate models/

# All levels, continue past failures
uv run agentic-mbse validate --complete models/

# Specific level only
uv run agentic-mbse validate --level=N models/

# Verbose diagnostics
uv run agentic-mbse validate --verbose models/
```

Do not suggest `uv run syside check` as a standalone validation step. Level 1 of `agentic-mbse validate` already runs syntax validation via syside. The 8-level framework is the correct entry point.

### CLI Tools

The primary CLI tool is `agentic-mbse`. Always invoke via `uv run`:
```bash
uv run agentic-mbse validate models/    # Validation
uv run agentic-mbse --help              # Discover commands
```

Never use bare `python`, `pip`, `python3`, or `syside` without `uv run` prefix.

### Slash Commands

Consult the "Slash Commands" table in `README.md` for the current list. Key workflow commands:
- `/spec-model`, `/design-model`, `/plan-model`, `/implement-model` — MBSE workflow
- `/audit-models` — Validate against domain sources
- `/research` — Deep-dive into domain knowledge
- `/manage-sources` — Add/remove domain sources
- `/backlog` — Work item management

### Python Environment

All Python commands require `uv run` prefix. This is a hard rule documented in `CLAUDE.md`. See `references/python-environment.md` for details.

## Anti-Patterns to Avoid

| Instead of | Use |
|------------|-----|
| `syside check models/` | `uv run agentic-mbse validate models/` |
| `python script.py` | `uv run python script.py` |
| `pip install X` | `uv add X` |
| Inventing validation commands | Reading README.md first |
| Describing tools from memory | Reading README.md to confirm |

## Reference Files

For additional context when answering tooling questions:
- **`references/python-environment.md`** — `uv` usage rules and rationale
