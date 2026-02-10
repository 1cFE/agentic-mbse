#!/bin/bash
set -euo pipefail

# =============================================================================
# run.sh — Single entry point: init (if needed) + run outer loop
# =============================================================================
#
# Usage:
#   ./run.sh <project> <goals_file> [options]   # First run (init + run)
#   ./run.sh [options]                           # Subsequent runs (resume)
#
# Options (passed through to outer-loop.sh):
#   --max N          Max outer iterations
#   --dry-run        Show what would happen without executing
#   --model <model>  Override spec model
#
# Examples:
#   ./run.sh doc-ingest GOALS.md --max 3   # Init + 3 iterations
#   ./run.sh --max 5                       # Resume, 5 more iterations
#   ./run.sh --dry-run                     # Resume, dry-run
#
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors (for pre-lib.sh messages)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# -----------------------------------------------------------------------------
# Separate positional args from flags
# -----------------------------------------------------------------------------

PROJECT_NAME=""
GOALS_FILE=""
OUTER_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --max|--model)
            OUTER_ARGS+=("$1" "$2")
            shift 2
            ;;
        --dry-run)
            OUTER_ARGS+=("$1")
            shift
            ;;
        --help|-h)
            cat << 'EOF'
Usage:
  ./run.sh <project> <goals_file> [options]   # First run (init + run)
  ./run.sh [options]                           # Subsequent runs (resume)

Options (passed through to outer-loop.sh):
  --max N          Max outer iterations (default: unlimited)
  --dry-run        Show what would happen without executing
  --model <model>  Override spec model

Examples:
  ./run.sh doc-ingest GOALS.md --max 3
  ./run.sh --max 5
  ./run.sh --dry-run
EOF
            exit 0
            ;;
        -*)
            echo -e "${YELLOW}Warning: Unknown flag '$1' — passing through to outer-loop.sh${NC}"
            OUTER_ARGS+=("$1")
            shift
            ;;
        *)
            if [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            elif [[ -z "$GOALS_FILE" ]]; then
                GOALS_FILE="$1"
            else
                echo "Error: Too many positional arguments" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# -----------------------------------------------------------------------------
# Decide: init or resume
# -----------------------------------------------------------------------------

if [[ -f experiment-log.md ]] && [[ -z "$PROJECT_NAME" ]]; then
    # Existing workspace, no project arg → resume
    echo -e "${GREEN}Resuming existing workspace${NC} (experiment-log.md found)"
    echo ""
elif [[ -n "$PROJECT_NAME" ]] && [[ -n "$GOALS_FILE" ]]; then
    # Project + goals provided → init (or re-init)
    if [[ -f experiment-log.md ]]; then
        echo -e "${YELLOW}Workspace already exists — re-initializing${NC}"
    fi
    "$SCRIPT_DIR/experiment-init.sh" "$PROJECT_NAME" "$GOALS_FILE"
else
    echo "Error: No existing workspace found." >&2
    echo "Usage: ./run.sh <project> <goals_file> [--max N] [--dry-run]" >&2
    exit 1
fi

# -----------------------------------------------------------------------------
# Run outer loop
# -----------------------------------------------------------------------------

exec "$SCRIPT_DIR/outer-loop.sh" "${OUTER_ARGS[@]}"
