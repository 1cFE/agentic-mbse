# Design: Replicate Setup Script

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-09 22:28:18 UTC
**Branch:** 1cfe_dev (4f3591e)

---

## Overview

A shell script (`scripts/replicate_setup.sh`) that enables dogfooding the agentic-mbse toolkit within its own development repository by replicating the Claude component installation from `agentic-mbse init` without CLI dependency or overwriting library-owned files.

## Related Artifacts

- **Spec:** `.project/active/replicate-setup/spec.md`
- **Reference Implementation:** `src/agentic_mbse/cli/__init__.py:182-432` (`cmd_init` function)

---

## Research Findings

### Codebase Analysis

**Key files examined:**
- `src/agentic_mbse/cli/__init__.py:182-432` - `cmd_init()` implementation
- `claude/commands/onboard.md` - `/onboard` command definition
- `claude/agents/sysmlv2-doc-analyzer.md` - Agent with doc path placeholders
- `project_templates/*.template` - 5 templates for project structure
- `SOURCE_INDEX.md.template` - Domain source configuration template
- `docs/` - Contains `sysmlv2/` and `syside/` subdirectories

**Key constants from CLI (`cli/__init__.py:14-48`):**
```python
MBSE_COMMANDS = [
    "design-model.md", "plan-model.md", "implement-model.md",
    "spec-model.md", "research.md", "audit-models.md",
    "onboard.md", "manage-sources.md", "backlog.md",
]
MBSE_AGENTS = ["python-debugger.md", "sysmlv2-doc-analyzer.md"]
MBSE_SKILLS = ["python-debugger"]
MBSE_HOOKS = ["ruff-format.sh"]
PROJECT_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "project/OVERVIEW.md"),
    ("MODELING_GUIDE.md.template", "project/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "project/MODELING_PROCESS.md"),
    ("BACKLOG.md.template", "project/backlog/BACKLOG.md"),
]
```

### Current Agent Path Handling (Problem)

The current design uses `agent_literature/` as a placeholder that looks like a real path:

**Source file** (`claude/agents/sysmlv2-doc-analyzer.md:12-16`):
```markdown
- **SysML Specifications**: `agent_literature/SysML/*/full_document.md`
- **Syside Python API**: `agent_literature/syside-docs/v0.8.1/api/`
```

**`init` substitution** (`cli/__init__.py:327-332`):
```python
content = content.replace("agent_literature/SysML/", f"{docs_path}/sysmlv2/")
content = content.replace("agent_literature/syside-docs/v0.8.1/", f"{docs_path}/syside/")
```

**Problem:** `agent_literature/` looks like a real directory but is actually just a string that gets replaced. This is confusing.

### Proposed Fix: Obvious Placeholders

Change to use placeholders that are obviously placeholders:
- `agent_literature/SysML/` → `{SYSML_DOCS_PATH}/`
- `agent_literature/syside-docs/v0.8.1/` → `{SYSIDE_DOCS_PATH}/`

This makes the substitution pattern explicit and prevents confusion.

### Settings.json Permission Format

From CLAUDE.md and `cli/__init__.py:394-399`:
- `~/path` = relative to $HOME (portable)
- `//path` = absolute filesystem path
- `/path` = relative to settings.json file (NOT absolute!)

### Key Distinction: Docs vs SOURCE_INDEX.md

| Component | Purpose | Contains |
|-----------|---------|----------|
| `docs/` (via placeholders) | SysML v2 **language** documentation | Specs, guides, syside API docs |
| `SOURCE_INDEX.md` | **Domain-specific** knowledge sources | Reference implementations, physics papers, specifications for the thing being modeled |

The `sysmlv2-doc-analyzer` agent reads from `docs/` (after placeholder substitution) to answer SysML syntax/pattern questions. MBSE commands read `SOURCE_INDEX.md` to find domain sources (e.g., fusion physics code, coffee maker thermodynamics).

---

## Init vs Replicate Setup: Step-by-Step Comparison

This table compares what `agentic-mbse init` and `/onboard` do for a typical **external target project** versus what `replicate_setup.sh` should do for **this library's own repo**.

| Step | `init` (External Project) | `/onboard` (After Init) | `replicate_setup.sh` (This Repo) |
|------|---------------------------|-------------------------|----------------------------------|
| **1. .gitignore** | Creates standard Python .gitignore | N/A (assumes exists) | **SKIP** - library has its own |
| **2. SOURCE_INDEX.md** | Copies template with placeholders | Fills in user's domain sources interactively | Copies template (no domain sources for toy example) |
| **3. .claude/commands/** | Copies 9 commands from `claude/commands/` | N/A | Copies same 9 commands (direct file copy) |
| **4. .claude/agents/** | Copies agents, **substitutes placeholders** with absolute path to installed package's `docs/` | N/A | **Same technique**: substitutes placeholders with absolute path to this repo's `docs/` |
| **5. .claude/skills/** | Recursively copies skill directories | N/A | Same recursive copy |
| **6. .claude/hooks/** | Copies hooks, preserves execute bits | N/A | Same copy with permissions |
| **7. .claude/settings.json** | Creates with `Read/Grep/Glob` for absolute `docs/` path + editable deps | May add user source paths | Creates with `Read/Grep/Glob` for absolute `docs/` path |
| **8. README.md** | Copies from template | Fills placeholders with project context | **SKIP** - library has its own |
| **9. project/OVERVIEW.md** | Copies from template | Fills placeholders with system/goals | Creates pre-filled coffee maker test subject |
| **10. project/MODELING_GUIDE.md** | Copies from template | N/A (methodology guide) | Copies from template |
| **11. project/MODELING_PROCESS.md** | Copies from template | N/A (methodology guide) | Copies from template |
| **12. project/backlog/BACKLOG.md** | Copies from template | Fills initial tasks | **SKIP** - library uses `.project/backlog/` |
| **13. project/{backlog,active,research}/** | Creates directories | N/A | Creates directories |
| **14. models/library/** | N/A (init doesn't create) | Creates `models/library/` and `models/designs/` | Creates `models/library/` for test model |
| **15. CLAUDE.md update** | N/A | Creates/updates with system context | Updates with `project/` vs `.project/` explanation |
| **16. .env check** | N/A | N/A | Warns if `SYSIDE_LICENSE_KEY` missing |

### Key Differences Summary

| Aspect | `init` | `replicate_setup.sh` |
|--------|--------|----------------------|
| **Agent path strategy** | Substitutes placeholders → absolute path to installed package's `docs/` | **Same technique**: substitutes placeholders → absolute path to this repo's `docs/` |
| **README.md** | Creates from template | Skips (library owns) |
| **.gitignore** | Creates standard Python | Skips (library owns) |
| **settings.json paths** | Absolute path to installed package's `docs/` | Absolute path to this repo's `docs/` |
| **SOURCE_INDEX.md** | Template placeholder | Template (no domain sources - toy example) |
| **project/OVERVIEW.md** | Template placeholder | Pre-filled with coffee maker |
| **Dependency** | Requires CLI installed | No CLI dependency (direct file ops) |

---

## Proposed Design

### High-Level Architecture

```
scripts/replicate_setup.sh
    │
    ├── Check Prerequisites
    │   ├── Verify running from repo root
    │   └── Warn if .env missing SYSIDE_LICENSE_KEY
    │
    ├── Install Claude Components
    │   ├── .claude/commands/*.md (direct copy)
    │   ├── .claude/agents/*.md (copy with placeholder substitution)
    │   ├── .claude/skills/* (recursive copy)
    │   └── .claude/hooks/* (copy with permissions)
    │
    ├── Create .claude/settings.json
    │   └── Read/Grep/Glob permissions for docs/ (absolute path)
    │
    ├── Create Project Structure
    │   ├── project/{backlog,active,research}/
    │   ├── project/MODELING_GUIDE.md (from template)
    │   ├── project/MODELING_PROCESS.md (from template)
    │   ├── project/OVERVIEW.md (pre-filled coffee maker)
    │   └── models/library/
    │
    ├── Create SOURCE_INDEX.md
    │   └── Copy template (no domain sources)
    │
    └── Print Summary
        └── What was created/updated
```

### Script Structure

```bash
#!/usr/bin/env bash
# scripts/replicate_setup.sh - Replicate agentic-mbse setup for local development

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_PATH="$REPO_ROOT/docs"

# ANSI colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # No Color

log_created() { echo -e "${GREEN}+${NC} $1"; }
log_skipped() { echo -e "${YELLOW}.${NC} $1 (exists)"; }

main() {
    cd "$REPO_ROOT"

    echo "Replicating agentic-mbse setup in $REPO_ROOT"
    echo ""

    check_prerequisites
    install_claude_components
    create_settings_json
    create_project_structure
    create_source_index
    print_summary
}

# ... function implementations ...

main "$@"
```

### Component Details

#### 1. Prerequisites Check

```bash
check_prerequisites() {
    # Verify repo root markers exist
    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]] || [[ ! -d "$REPO_ROOT/claude" ]]; then
        echo "Error: Must run from agentic-mbse repository root" >&2
        exit 1
    fi

    # Warn about missing license key
    if [[ ! -f "$REPO_ROOT/.env" ]] || ! grep -q "SYSIDE_LICENSE_KEY" "$REPO_ROOT/.env" 2>/dev/null; then
        echo -e "${YELLOW}Warning:${NC} SYSIDE_LICENSE_KEY not found in .env"
        echo "  Validation commands will not work until this is configured."
        echo ""
    fi
}
```

#### 2. Install Claude Components

```bash
install_claude_components() {
    mkdir -p "$REPO_ROOT/.claude/commands"
    mkdir -p "$REPO_ROOT/.claude/agents"
    mkdir -p "$REPO_ROOT/.claude/skills"
    mkdir -p "$REPO_ROOT/.claude/hooks"

    # Commands - direct copy
    for cmd in design-model.md plan-model.md implement-model.md spec-model.md \
               research.md audit-models.md onboard.md manage-sources.md backlog.md; do
        cp "$REPO_ROOT/claude/commands/$cmd" "$REPO_ROOT/.claude/commands/$cmd"
        log_created ".claude/commands/$cmd"
    done

    # Agents - copy with placeholder substitution (same as init)
    for agent in python-debugger.md sysmlv2-doc-analyzer.md; do
        # Read source, substitute placeholders, write to destination
        sed -e "s|{SYSML_DOCS_PATH}|$DOCS_PATH/sysmlv2|g" \
            -e "s|{SYSIDE_DOCS_PATH}|$DOCS_PATH/syside|g" \
            "$REPO_ROOT/claude/agents/$agent" > "$REPO_ROOT/.claude/agents/$agent"
        log_created ".claude/agents/$agent (with path substitution)"
    done

    # Skills - recursive copy
    if [[ -d "$REPO_ROOT/claude/skills/python-debugger" ]]; then
        cp -r "$REPO_ROOT/claude/skills/python-debugger" "$REPO_ROOT/.claude/skills/"
        log_created ".claude/skills/python-debugger/"
    fi

    # Hooks - copy with permissions
    for hook in ruff-format.sh; do
        if [[ -f "$REPO_ROOT/claude/hooks/$hook" ]]; then
            cp "$REPO_ROOT/claude/hooks/$hook" "$REPO_ROOT/.claude/hooks/$hook"
            chmod +x "$REPO_ROOT/.claude/hooks/$hook"
            log_created ".claude/hooks/$hook"
        fi
    done
}
```

#### 3. Create .claude/settings.json

```bash
create_settings_json() {
    local settings_file="$REPO_ROOT/.claude/settings.json"

    # Convert absolute path to ~ format for portability
    local docs_permission_path="${DOCS_PATH/#$HOME/\~}"

    # Always overwrite to ensure permissions are current
    cat > "$settings_file" << EOF
{
  "permissions": {
    "allow": [
      "Read($docs_permission_path/**)",
      "Grep($docs_permission_path/**)",
      "Glob($docs_permission_path/**)"
    ]
  }
}
EOF
    log_created ".claude/settings.json (permissions for $docs_permission_path)"
}
```

#### 4. Create Project Structure

```bash
create_project_structure() {
    # Create directories
    mkdir -p "$REPO_ROOT/project/backlog"
    mkdir -p "$REPO_ROOT/project/active"
    mkdir -p "$REPO_ROOT/project/research"
    mkdir -p "$REPO_ROOT/models/library"

    log_created "project/{backlog,active,research}/"
    log_created "models/library/"

    # Copy methodology guides from templates
    cp "$REPO_ROOT/project_templates/MODELING_GUIDE.md.template" \
       "$REPO_ROOT/project/MODELING_GUIDE.md"
    log_created "project/MODELING_GUIDE.md"

    cp "$REPO_ROOT/project_templates/MODELING_PROCESS.md.template" \
       "$REPO_ROOT/project/MODELING_PROCESS.md"
    log_created "project/MODELING_PROCESS.md"

    # Create pre-filled OVERVIEW.md with coffee maker test subject
    create_overview_md
}

create_overview_md() {
    cat > "$REPO_ROOT/project/OVERVIEW.md" << 'EOF'
# Project Overview

**Project**: Coffee Maker Test Model
**Purpose**: Dogfooding agentic-mbse with a simple test subject
**Start Date**: 2026-01-09
**Status**: Active

---

## What We're Building

SysMLv2 models of a simple drip coffee maker that enable:

1. **Formal Integration** - Connect behavior (brewing process), structure (components), and physics (heat transfer, fluid flow)
2. **Validation Framework** - Constraint-based checking against physical laws
3. **Design Exploration** - Parametric studies (capacity, brew time, temperature)
4. **Workflow Testing** - Exercise the full MBSE command workflow

**Reference Implementation**: N/A (test subject for workflow validation)
**Validation Baseline**: Common sense physics constraints

---

## System Description

A simple drip coffee maker with these components:

**Parts:**
- Water reservoir (capacity: configurable)
- Heating element (power: configurable)
- Pump (flow rate: configurable)
- Brew basket (filter holder)
- Carafe (output container)
- Control panel (on/off, brew button)

**Behaviors:**
- Fill reservoir -> Heat water -> Pump to brew basket -> Drip into carafe
- Temperature control (maintain brew temp ~195-205F)
- Auto-shutoff after brewing complete

**Why this subject:**
- Familiar to most people
- 5-7 components (right complexity for testing)
- Clear data flows (water, heat, control signals)
- Natural requirements (brew time, temperature, capacity)

---

## Technical Approach

For MBSE methodology, see [MODELING_PROCESS.md](MODELING_PROCESS.md).
For SysML syntax and patterns, see [MODELING_GUIDE.md](MODELING_GUIDE.md).

---

## Current Status

**Active Work Item**: Initial setup
**Status**: Ready to start modeling
**Next Up**: Run /spec-model to define first feature

---

## Getting Started

1. Run `/spec-model coffee-maker-structure` to define requirements
2. Run `/design-model coffee-maker-structure` to design the model
3. Run `/implement-model coffee-maker-structure` to create SysML files

---

**Last Updated**: 2026-01-09
EOF
    log_created "project/OVERVIEW.md (coffee maker test subject)"
}
```

#### 5. Create SOURCE_INDEX.md

```bash
create_source_index() {
    # Just copy the template as-is - it already says "no sources configured"
    cp "$REPO_ROOT/SOURCE_INDEX.md.template" "$REPO_ROOT/SOURCE_INDEX.md"
    log_created "SOURCE_INDEX.md (from template)"
}
```

#### 6. Print Summary

```bash
print_summary() {
    echo ""
    echo "================================"
    echo "Setup complete!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review project/OVERVIEW.md for the test subject"
    echo "  2. Run /spec-model coffee-maker-structure to start modeling"
    echo "  3. Or run /onboard for interactive configuration"
    echo ""
    echo "To update after code changes, re-run:"
    echo "  ./scripts/replicate_setup.sh"
}
```

---

## Required Code Changes

### 1. Update Agent Source File

**File:** `claude/agents/sysmlv2-doc-analyzer.md`

Change placeholder paths to obvious placeholders:

| Before | After |
|--------|-------|
| `agent_literature/SysML/` | `{SYSML_DOCS_PATH}/` |
| `agent_literature/syside-docs/v0.8.1/` | `{SYSIDE_DOCS_PATH}/` |

**Example changes in file:**
```markdown
## Documentation Structure

You have access to:
- **SysML Specifications**: `{SYSML_DOCS_PATH}/*/full_document.md`
  - Core specs: `SysML_Spec_v2_Part2`, `SysML_Spec_v2_Part3`
  - Guides: `SysML_IntroGuide_v2`, `SysML_HoltPerryConcepts_v20`
  - Examples: `Cheatsheet/`, `SysML_IntegratingReasoning`
- **Syside Python API**: `{SYSIDE_DOCS_PATH}/api/`
```

### 2. Update CLI Init Function

**File:** `src/agentic_mbse/cli/__init__.py:327-332`

Update string replacement to use new placeholders:

```python
# Before:
content = content.replace("agent_literature/SysML/", f"{docs_path}/sysmlv2/")
content = content.replace("agent_literature/syside-docs/v0.8.1/", f"{docs_path}/syside/")

# After:
content = content.replace("{SYSML_DOCS_PATH}", f"{docs_path}/sysmlv2")
content = content.replace("{SYSIDE_DOCS_PATH}", f"{docs_path}/syside")
```

### 3. Update Test Assertions

**File:** `tests/test_cli.py:168-169`

Update to check for new placeholders:

```python
# Before:
assert "agent_literature/SysML/" not in agent_content
assert "agent_literature/syside-docs/" not in agent_content

# After:
assert "{SYSML_DOCS_PATH}" not in agent_content
assert "{SYSIDE_DOCS_PATH}" not in agent_content
```

---

## CLAUDE.md Updates

The following section should be added to `CLAUDE.md` after the "Testing Structure" section:

```markdown
## Directory Clarification

This repo has two similar-looking directories:

| Directory | Purpose | Committed to Git |
|-----------|---------|------------------|
| `.project/` | Internal development project management (specs, designs, backlog for agentic-mbse itself) | Yes |
| `project/` | Dogfooding test subject (OVERVIEW.md, MODELING_GUIDE.md for coffee maker test model) | Created by `replicate_setup.sh` |

## Change Coordination

When modifying `scripts/replicate_setup.sh` or `cmd_init()` in `src/agentic_mbse/cli/__init__.py`:

1. Review if the same change is needed in the other
2. Both handle the same set of commands, agents, skills, and hooks (see `MBSE_COMMANDS`, `MBSE_AGENTS`, `MBSE_SKILLS`, `MBSE_HOOKS` in `cli/__init__.py`)
3. Both use the same placeholder substitution technique for agent paths

| File | Substitutes placeholders with |
|------|-------------------------------|
| `cmd_init()` | Absolute path to installed package's `docs/` |
| `replicate_setup.sh` | Absolute path to this repo's `docs/` |
```

---

## Potential Risks

| Risk | Mitigation |
|------|------------|
| Placeholder format changes | Document the placeholders in agent files and coordinate changes |
| Forgetting to update one when other changes | Add CLAUDE.md section documenting coordination |
| Script accidentally run in wrong directory | Check for `pyproject.toml` and `claude/` markers |

---

## Integration Strategy

- **Complements**: `agentic-mbse init` for external users
- **Replaces**: Manual setup steps for library development
- **Workflow**: After pulling changes, run `./scripts/replicate_setup.sh` to update Claude components

---

## Validation Approach

**Testing strategy:**
1. Run `./scripts/replicate_setup.sh` from repo root
2. Verify all files created as expected
3. Start Claude Code and verify `/design-model` command is available
4. Verify `sysmlv2-doc-analyzer` agent can access docs (paths substituted correctly)
5. Run existing tests to ensure no regressions

**Success criteria:**
- [ ] Script completes without errors
- [ ] All Claude components installed to `.claude/`
- [ ] Agent files have absolute paths (no placeholders remaining)
- [ ] `.claude/settings.json` has correct permissions for `docs/`
- [ ] `/design-model`, `/plan-model`, `/implement-model` commands available
- [ ] `project/OVERVIEW.md` describes coffee maker test subject
- [ ] Re-running script updates components without errors
- [ ] README.md and .gitignore NOT modified

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `scripts/replicate_setup.sh` | Create | Main script (~120 lines) |
| `claude/agents/sysmlv2-doc-analyzer.md` | Modify | Change `agent_literature/` to `{SYSML_DOCS_PATH}` and `{SYSIDE_DOCS_PATH}` placeholders |
| `src/agentic_mbse/cli/__init__.py` | Modify | Update placeholder strings in substitution logic |
| `tests/test_cli.py` | Modify | Update assertions for new placeholder format |
| `CLAUDE.md` | Modify | Add directory clarification and change coordination sections |
| `.gitignore` (library's) | Modify | Add `project/`, `models/library/` |

---

**Next Step:** After approval, proceed to `/_my_implement`
