#!/usr/bin/env bash
# pre-commit-check-comments.sh - Block commits with unresolved comments (REQ-4, AC-5)
#
# Installation:
#   ln -s ../../claude/hooks/pre-commit-check-comments.sh .git/hooks/pre-commit
#
# Configuration:
#   git config comment-system.block-on-unresolved true   # Block commits (default: false)
#   git config comment-system.block-on-unresolved false  # Disable blocking
#
# This hook:
#   1. Checks for unresolved comments on staged files
#   2. Blocks commit if unresolved comments found and blocking enabled (AC-5)
#   3. Shows list of files with unresolved comments

set -euo pipefail

# CON-4: Must not break if git binary is missing
if ! command -v git &> /dev/null; then
    echo "Warning: git not found, skipping comment check" >&2
    exit 0
fi

# Check if comment CLI is available
if ! command -v comment &> /dev/null; then
    # Silently skip if comment system not installed
    exit 0
fi

# Read configuration (default: false to not block existing workflows)
BLOCK_ON_UNRESOLVED=$(git config --get comment-system.block-on-unresolved || echo "false")

if [ "$BLOCK_ON_UNRESOLVED" != "true" ]; then
    # Blocking disabled, exit early
    exit 0
fi

# Get list of staged files (both modified and added)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=AM)

if [ -z "$STAGED_FILES" ]; then
    # No staged files, nothing to check
    exit 0
fi

# Check each staged file for unresolved comments
UNRESOLVED_FILES=()
while IFS= read -r file; do
    # Skip if file doesn't exist (deleted files)
    if [ ! -f "$file" ]; then
        continue
    fi

    # Check for open comments on this file
    OPEN_COUNT=$(comment list --json --status=open "$file" 2>/dev/null | jq 'length' || echo "0")

    if [ "$OPEN_COUNT" -gt 0 ]; then
        UNRESOLVED_FILES+=("$file ($OPEN_COUNT open)")
    fi
done <<< "$STAGED_FILES"

# Block commit if unresolved comments found (AC-5)
if [ ${#UNRESOLVED_FILES[@]} -gt 0 ]; then
    echo "❌ Error: Commit blocked due to unresolved comments on staged files:" >&2
    for file_info in "${UNRESOLVED_FILES[@]}"; do
        echo "  - $file_info" >&2
    done
    echo >&2
    echo "Options:" >&2
    echo "  1. Resolve comments: comment resolve THREAD_ID --decision=\"...\"" >&2
    echo "  2. Disable blocking: git config comment-system.block-on-unresolved false" >&2
    echo "  3. Skip hook once: git commit --no-verify" >&2
    exit 1
fi

# All clear
exit 0
