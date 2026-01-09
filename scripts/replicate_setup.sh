#!/usr/bin/env bash
# scripts/replicate_setup.sh - Replicate agentic-mbse setup for local development
#
# This script enables dogfooding the agentic-mbse toolkit within its own
# development repository by installing Claude components directly (no CLI dependency).
#
# Usage: ./scripts/replicate_setup.sh
#
# What it does:
# - Installs .claude/commands/, agents/, skills/, hooks/
# - Creates .claude/settings.json with docs/ permissions
# - Creates project/ structure with coffee maker test subject
# - Creates SOURCE_INDEX.md from template
#
# What it does NOT do (library owns these):
# - Modify README.md
# - Modify .gitignore

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

    # Agents - copy with placeholder substitution (same technique as init)
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

create_source_index() {
    # Copy the template as-is
    cp "$REPO_ROOT/SOURCE_INDEX.md.template" "$REPO_ROOT/SOURCE_INDEX.md"
    log_created "SOURCE_INDEX.md (from template)"
}

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

main "$@"
