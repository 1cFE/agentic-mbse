#!/usr/bin/env bash
# check_open_comments.sh - Query open comments for agent workflows
#
# Usage: ./scripts/check_open_comments.sh [FILE]
#
# Examples:
#   # Check all open comments in project
#   ./scripts/check_open_comments.sh
#
#   # Check open comments on specific file
#   ./scripts/check_open_comments.sh src/foo.py
#
# Exit codes:
#   0 - Success (comments found or none)
#   1 - Usage error
#   2 - System error (no git repo, comment CLI not available)

set -euo pipefail

# Check if comment CLI is available
if ! command -v comment &> /dev/null; then
    echo "Error: 'comment' CLI not found. Install agentic-mbse comment system." >&2
    exit 2
fi

# Parse arguments
FILE="${1:-}"

# Query comments
if [ -z "$FILE" ]; then
    # Project-wide query
    COMMENTS=$(comment list --json --status=open --all)
else
    # File-specific query
    if [ ! -f "$FILE" ]; then
        echo "Error: File not found: $FILE" >&2
        exit 1
    fi
    COMMENTS=$(comment list --json --status=open "$FILE")
fi

# Verify JSON is valid (AC-1)
if ! echo "$COMMENTS" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON output from comment CLI" >&2
    exit 2
fi

# Output results
echo "$COMMENTS"

# Count open comments
COUNT=$(echo "$COMMENTS" | jq 'length')
if [ "$COUNT" -gt 0 ]; then
    echo "Found $COUNT open comment(s)" >&2
else
    echo "No open comments" >&2
fi

exit 0
