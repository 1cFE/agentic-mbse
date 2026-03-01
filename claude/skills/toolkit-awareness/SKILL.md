---
name: toolkit-awareness
description: >
  This skill should be used when the user asks about "validation", "validate models",
  "run checks", "quality checks", "codegen readiness", "TEA pipeline", "how to validate",
  "run the pipeline", "toolkit", "available commands", "what tools do we have",
  "PM operations", "project management", "agentic-mbse pm", "agentic-mbse status",
  "project files", "directory structure",
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
   - The 6-level validation framework
   - Slash commands available in Claude Code
   - Project setup and environment requirements

2. **Read `CLAUDE.md`** at the project root. This documents:
   - Python environment rules (`uv` requirement)
   - MBSE workflow steps
   - Domain sources and how to reference them

3. **Check the 4-directory architecture** — see the Project Files section below for key files in `knowledge/`, `modeling_project/`, `work/`, and `data/`.

4. **Do not invent commands.** If a tool or command is not documented in README.md or CLAUDE.md, do not suggest it exists.

### Validation Framework

The project uses `agentic-mbse validate` with 6 quality levels. For complete details including level descriptions and blocking status, read the "Validation Framework" section of `README.md`.

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

Do not suggest `uv run syside check` as a standalone validation step. Level 1 of `agentic-mbse validate` already runs syntax validation via syside. The 6-level framework is the correct entry point.

### CLI Tools

The primary CLI tool is `agentic-mbse`. Always invoke via `uv run`:
```bash
uv run agentic-mbse validate models/    # Validation
uv run agentic-mbse status              # Project status dashboard
uv run agentic-mbse pm <operation>      # Project management operations
uv run agentic-mbse --help              # Discover commands
```

Never use bare `python`, `pip`, `python3`, or `syside` without `uv run` prefix.

### PM Operations

All PM operations are atomic (mutations succeed fully or not at all) or tolerant (queries return partial results with warnings). Invoke via `uv run agentic-mbse pm <operation> [args]`.

| Operation | Description |
|-----------|-------------|
| `close-item <name>` | Archive completed work item from active to completed |
| `approve-research <file> --insights '<json>'` | Approve pending research and register domain insights |
| `trace-element --element <name> --file <path> ...` | Record model element traceability to matrix |
| `promote-requirement --requirement <text> --source <ID>` | Promote per-item requirement to project-wide PR-XXX |
| `register-decision --title <text> --decision <text> --rationale <text>` | Record architectural decision as AD-XXX |
| `update-validation <SV-XXX> --status <status>` | Update verification criterion status |
| `add-insight --title <text> --source <source> ...` | Capture domain insight as DI-XXX during work |
| `impact-query <ID>` | Find model elements affected by DI-XXX or PR-XXX change |
| `supersede-insight <DI-XXX> --new-insight '<json>' --reason '<text>'` | Replace domain insight and report impact |

### Slash Commands

Consult `README.md` for full details. Complete command list grouped by function:

**Modeling Workflow:**

| Command | Purpose |
|---------|---------|
| `/spec-model` | Define requirements and success criteria for models |
| `/design-model` | Make model architecture decisions |
| `/plan-model` | Create implementation plan with phases |
| `/implement-model` | Execute plan, write SysML |
| `/quick-model` | Rapid single-file model creation |
| `/review-model` | Review model quality and correctness |
| `/formalize-intent` | Convert informal intent to formal SysML |

**Project Management:**

| Command | Purpose |
|---------|---------|
| `/audit-models` | Validate models against domain sources |
| `/analyze-models` | Analyze model structure and dependencies |
| `/status` | Project status dashboard |
| `/backlog` | Work item management |
| `/onboard` | Initialize new MBSE project |

**Knowledge Management:**

| Command | Purpose |
|---------|---------|
| `/research` | Deep-dive into domain knowledge |
| `/manage-sources` | Add/remove domain sources |

### Project Files

Key project files in the 4-directory architecture:

| File | Directory | Role |
|------|-----------|------|
| `SOURCE_INDEX.md` | `knowledge/` | Registry of domain knowledge sources |
| `KNOWLEDGE.md` | `knowledge/` | Domain insights (DI-XXX) and research findings |
| `OVERVIEW.md` | `modeling_project/` | Project scope and high-level description |
| `ARCHITECTURE.md` | `modeling_project/` | Model architecture decisions |
| `REQUIREMENTS.md` | `modeling_project/` | Project-wide requirements (PR-XXX) |
| `VALIDATION_MATRIX.md` | `modeling_project/` | Verification criteria (SV-XXX) and status |
| `BACKLOG.md` | `work/` | Work items, epics, and priorities |
| `traceability_matrix.csv` | `data/` | Element-to-requirement traceability records |

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
