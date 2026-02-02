#!/usr/bin/env bash
# Ralph Loop Integration Script
#
# This script demonstrates how Ralph (an automated AI coding loop) can integrate
# with the comment system to address open comments before proceeding with tasks.
#
# Usage:
#   ./scripts/ralph_loop_integration.sh [FILE_TO_MODIFY]
#
# Requirements:
#   - comment CLI must be in PATH or installed via `uv run comment`
#   - Git repository must be initialized
#   - jq must be installed for JSON parsing
#
# Exit codes:
#   0 - Success, no open comments (Ralph can proceed)
#   1 - Open comments found (Ralph should address them first)
#   2 - System error (missing dependencies, no git repo, etc.)
#
# This is an EXAMPLE script for demonstration purposes. Production Ralph loops
# should customize this logic to fit their specific workflow.

set -euo pipefail

# Configuration
COMMENT_CMD="${COMMENT_CMD:-comment}"  # Allow overriding command (e.g., "uv run comment")
MIN_THRESHOLD="${RALPH_COMMENT_THRESHOLD:-0.6}"  # Reconciliation similarity threshold

# Colors for output (respects NO_COLOR)
if [ -z "${NO_COLOR:-}" ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'  # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Helper functions
log_info() {
    echo -e "${BLUE}[Ralph]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[Ralph]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[Ralph]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[Ralph]${NC} $*" >&2
}

# Check dependencies
check_dependencies() {
    local missing_deps=()

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi

    # Check if comment command works
    if ! $COMMENT_CMD --version &> /dev/null; then
        log_error "Comment CLI not found or not working: $COMMENT_CMD"
        log_error "Try setting COMMENT_CMD environment variable or install the CLI"
        exit 2
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Install with: apt install ${missing_deps[*]} (or equivalent for your OS)"
        exit 2
    fi
}

# Main workflow
main() {
    local file_to_modify="${1:-}"

    check_dependencies

    log_info "=== Ralph Loop Integration Demo ==="
    log_info ""

    # Step 1: Ralph reads specs and picks task (simulated)
    log_info "Step 1: Ralph would read specs and pick a task"
    log_info "For this demo, we'll simulate modifying: ${file_to_modify:-all files}"
    log_info ""

    # Step 2: Before implementing, reconcile anchors to ensure comments are current
    log_info "Step 2: Reconciling anchors to ensure comments are up-to-date..."
    if [ -n "$file_to_modify" ] && [ -f "$file_to_modify" ]; then
        $COMMENT_CMD reconcile "$file_to_modify" --threshold="$MIN_THRESHOLD" > /dev/null 2>&1 || true
    else
        $COMMENT_CMD reconcile --all --threshold="$MIN_THRESHOLD" > /dev/null 2>&1 || true
    fi
    log_success "Reconciliation complete"
    log_info ""

    # Step 3: Check for open comments on files Ralph will modify
    log_info "Step 3: Checking for open comments that need to be addressed..."

    local comments_json
    if [ -n "$file_to_modify" ]; then
        log_info "Checking for open comments on: $file_to_modify"
        comments_json=$($COMMENT_CMD list "$file_to_modify" --json --status=open 2>/dev/null || echo "[]")
    else
        log_info "Checking for open comments across all files"
        comments_json=$($COMMENT_CMD list --all --json --status=open 2>/dev/null || echo "[]")
    fi

    # Display summary
    local comment_count
    comment_count=$(echo "$comments_json" | jq 'length')

    if [ "$comment_count" -eq 0 ]; then
        log_success "No open comments found"
    else
        log_warning "Found $comment_count open comment thread(s):"
        echo "$comments_json" | jq -r '.[] | "  - Thread \(.id): \(.source_file):\(.anchor.line_start)"' >&2
    fi
    log_info ""

    # Step 4: If open comments exist, Ralph should address them first
    if [ "$comment_count" -gt 0 ]; then
        log_warning "Ralph should address these $comment_count comment(s) before proceeding with task implementation"
        log_warning ""
        log_warning "Typical Ralph workflow would:"
        log_warning "  1. Read each comment thread"
        log_warning "  2. Address the feedback (modify code, add documentation, etc.)"
        log_warning "  3. Reply to comments explaining changes"
        log_warning "  4. Resolve comments with decision summaries"
        log_warning "  5. Include comment resolutions in commit message"
        log_info ""

        # Output the comments as JSON for programmatic access
        echo "$comments_json"
        exit 1  # Exit code 1 indicates comments need addressing
    else
        log_success "No open comments to address - Ralph can proceed with task implementation"
        log_info ""

        # Step 5: Ralph would implement the task (simulated)
        log_info "Step 5: Ralph would now implement the task..."
        log_info "  (In real workflow, this is where code changes happen)"
        log_info ""

        # Step 6: Ralph would commit changes (simulated)
        log_info "Step 6: Ralph would commit with message including any resolved comments"
        log_info "  Example: 'Task X: Implement feature Y"
        log_info "  "
        log_info "  Resolved comments:"
        log_info "  - THREAD_ID: [decision summary]'"
        log_info ""

        echo "[]"
        exit 0  # Exit code 0 indicates success
    fi
}

# Run main
main "$@"
