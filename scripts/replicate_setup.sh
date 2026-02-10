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
# - Creates 4-directory project structure (knowledge/, modeling_project/, work/, data/)
# - Creates knowledge/SOURCE_INDEX.md from template
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
    for cmd in analyze-models.md audit-models.md backlog.md design-model.md \
               formalize-intent.md implement-model.md manage-sources.md onboard.md \
               plan-model.md quick-model.md research.md review-model.md \
               spec-model.md status.md; do
        cp "$REPO_ROOT/claude/commands/$cmd" "$REPO_ROOT/.claude/commands/$cmd"
        log_created ".claude/commands/$cmd"
    done

    # Agents - copy with placeholder substitution
    for agent in python-debugger.md kerml-expert.md sysml-expert.md \
                 syside-expert.md sysmlv2-validator.md; do
        sed -e "s|{SYSML_DOCS_PATH}|$DOCS_PATH/sysmlv2|g" \
            -e "s|{SYSIDE_DOCS_PATH}|$DOCS_PATH/syside|g" \
            "$REPO_ROOT/claude/agents/$agent" > "$REPO_ROOT/.claude/agents/$agent"
        log_created ".claude/agents/$agent (with path substitution)"
    done

    # Skills - recursive copy
    for skill in epic-decomposition model-validation pdf-analysis \
                 project-structure python-debugger record-learning \
                 requirements-tracking source-traceability sysml-conventions \
                 toolkit-awareness; do
        if [[ -d "$REPO_ROOT/claude/skills/$skill" ]]; then
            cp -r "$REPO_ROOT/claude/skills/$skill" "$REPO_ROOT/.claude/skills/"
            log_created ".claude/skills/$skill/"
        fi
    done

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
    # Create 4-directory structure
    mkdir -p "$REPO_ROOT/knowledge/research/pending"
    mkdir -p "$REPO_ROOT/knowledge/research/approved"
    mkdir -p "$REPO_ROOT/knowledge/research/impacts"
    mkdir -p "$REPO_ROOT/knowledge/sources"
    mkdir -p "$REPO_ROOT/modeling_project/intent"
    mkdir -p "$REPO_ROOT/work/backlog"
    mkdir -p "$REPO_ROOT/work/active"
    mkdir -p "$REPO_ROOT/work/completed"
    mkdir -p "$REPO_ROOT/work/analysis"
    mkdir -p "$REPO_ROOT/work/learnings"
    mkdir -p "$REPO_ROOT/data"
    mkdir -p "$REPO_ROOT/models/library"
    mkdir -p "$REPO_ROOT/models/designs"
    mkdir -p "$REPO_ROOT/tests/models"

    log_created "knowledge/{research/{pending,approved,impacts},sources}/"
    log_created "modeling_project/intent/"
    log_created "work/{backlog,active,completed,analysis,learnings}/"
    log_created "data/"
    log_created "models/{library,designs}/"
    log_created "tests/models/"

    # Tool-owned templates
    cp "$REPO_ROOT/project_templates/MODELING_GUIDE.md.template" \
       "$REPO_ROOT/modeling_project/MODELING_GUIDE.md"
    log_created "modeling_project/MODELING_GUIDE.md"

    cp "$REPO_ROOT/project_templates/MODELING_PROCESS.md.template" \
       "$REPO_ROOT/modeling_project/MODELING_PROCESS.md"
    log_created "modeling_project/MODELING_PROCESS.md"

    cp "$REPO_ROOT/project_templates/EPIC_GUIDE.md.template" \
       "$REPO_ROOT/work/EPIC_GUIDE.md"
    log_created "work/EPIC_GUIDE.md"

    cp "$REPO_ROOT/project_templates/epic_template.md.template" \
       "$REPO_ROOT/work/backlog/epic_template.md"
    log_created "work/backlog/epic_template.md"

    # User-owned templates
    cp "$REPO_ROOT/project_templates/OVERVIEW.md.template" \
       "$REPO_ROOT/modeling_project/OVERVIEW.md"
    log_created "modeling_project/OVERVIEW.md"

    cp "$REPO_ROOT/project_templates/BACKLOG.md.template" \
       "$REPO_ROOT/work/BACKLOG.md"
    log_created "work/BACKLOG.md"

    cp "$REPO_ROOT/project_templates/RAW_LEARNINGS.md.template" \
       "$REPO_ROOT/work/learnings/RAW_LEARNINGS.md"
    log_created "work/learnings/RAW_LEARNINGS.md"

    cp "$REPO_ROOT/project_templates/KNOWLEDGE.md.template" \
       "$REPO_ROOT/knowledge/KNOWLEDGE.md"
    log_created "knowledge/KNOWLEDGE.md"

    cp "$REPO_ROOT/project_templates/ARCHITECTURE.md.template" \
       "$REPO_ROOT/modeling_project/ARCHITECTURE.md"
    log_created "modeling_project/ARCHITECTURE.md"

    cp "$REPO_ROOT/project_templates/REQUIREMENTS.md.template" \
       "$REPO_ROOT/modeling_project/REQUIREMENTS.md"
    log_created "modeling_project/REQUIREMENTS.md"

    cp "$REPO_ROOT/project_templates/VALIDATION_MATRIX.md.template" \
       "$REPO_ROOT/modeling_project/VALIDATION_MATRIX.md"
    log_created "modeling_project/VALIDATION_MATRIX.md"

    # Data templates
    cp "$REPO_ROOT/project_templates/data/traceability_matrix.csv" \
       "$REPO_ROOT/data/traceability_matrix.csv"
    log_created "data/traceability_matrix.csv"
}

create_source_index() {
    cp "$REPO_ROOT/SOURCE_INDEX.md.template" "$REPO_ROOT/knowledge/SOURCE_INDEX.md"
    log_created "knowledge/SOURCE_INDEX.md (from template)"
}

print_summary() {
    echo ""
    echo "================================"
    echo "Setup complete!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review modeling_project/OVERVIEW.md for the project template"
    echo "  2. Run /spec-model to start modeling"
    echo "  3. Or run /onboard for interactive configuration"
    echo ""
    echo "To update after code changes, re-run:"
    echo "  ./scripts/replicate_setup.sh"
}

setup_docling_mcp() {
    if [[ "${NO_DOCLING:-false}" == "true" ]]; then
        echo -e "${YELLOW}.${NC} Docling MCP setup skipped (NO_DOCLING=true)"
        return
    fi

    local setup_script="$REPO_ROOT/scripts/setup-docling.sh"
    if [[ ! -f "$setup_script" ]]; then
        echo -e "${YELLOW}Warning:${NC} Docling setup script not found at $setup_script"
        return
    fi

    echo ""
    echo "Setting up Docling MCP server..."

    if bash "$setup_script"; then
        log_created "Docling MCP server (see ~/.docling-mcp-env.md)"
    else
        echo -e "${YELLOW}Warning:${NC} Docling MCP setup failed — pdf-analysis will use Tier 1 + 3 only"
    fi
}

main() {
    cd "$REPO_ROOT"

    echo "Replicating agentic-mbse setup in $REPO_ROOT"
    echo ""

    check_prerequisites
    install_claude_components
    setup_docling_mcp
    create_settings_json
    create_project_structure
    create_source_index
    print_summary
}

main "$@"
