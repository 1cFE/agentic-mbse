#!/usr/bin/env bash
# post-commit-reconcile.sh - Reconcile comments after each commit (REQ-4, AC-3)
#
# Installation:
#   ln -s ../../claude/hooks/post-commit-reconcile.sh .git/hooks/post-commit
#
# Configuration (optional):
#   git config comment-system.orphan-threshold 5  # Warn if > 5 orphans (default: 0)
#   git config comment-system.fail-on-orphans true  # Fail commit if orphans (default: false)
#
# This hook:
#   1. Runs reconciliation after every commit
#   2. Reports orphaned comment count (AC-3)
#   3. Optionally fails if orphan count exceeds threshold (REQ-4)

set -euo pipefail

# CON-4: Must not break if git binary is missing (checked via command existence)
if ! command -v git &> /dev/null; then
    echo "Warning: git not found, skipping comment reconciliation" >&2
    exit 0
fi

# Check if comment CLI is available
if ! command -v comment &> /dev/null; then
    # Silently skip if comment system not installed
    exit 0
fi

# Read configuration
ORPHAN_THRESHOLD=$(git config --get comment-system.orphan-threshold || echo "0")
FAIL_ON_ORPHANS=$(git config --get comment-system.fail-on-orphans || echo "false")

# Run reconciliation (quiet mode to reduce noise)
echo "Reconciling comments..." >&2
RECONCILE_OUTPUT=$(comment reconcile --all --json 2>&1) || {
    echo "Warning: Comment reconciliation failed, continuing anyway" >&2
    exit 0
}

# Parse orphaned count from JSON output
ORPHANED_COUNT=0
for file_report in $(echo "$RECONCILE_OUTPUT" | jq -c '.[]' 2>/dev/null || echo "[]"); do
    FILE_ORPHANED=$(echo "$file_report" | jq -r '.orphaned // 0')
    ORPHANED_COUNT=$((ORPHANED_COUNT + FILE_ORPHANED))
done

# Report orphaned count (AC-3)
if [ "$ORPHANED_COUNT" -gt 0 ]; then
    echo "⚠ Warning: $ORPHANED_COUNT orphaned comment(s) detected after commit" >&2

    # Show which files have orphaned comments
    echo "Files with orphaned comments:" >&2
    for file_report in $(echo "$RECONCILE_OUTPUT" | jq -c '.[]' 2>/dev/null || echo "[]"); do
        FILE_ORPHANED=$(echo "$file_report" | jq -r '.orphaned // 0')
        if [ "$FILE_ORPHANED" -gt 0 ]; then
            FILE_PATH=$(echo "$file_report" | jq -r '.file')
            echo "  - $FILE_PATH: $FILE_ORPHANED orphaned" >&2
        fi
    done

    # Check threshold (REQ-4)
    if [ "$ORPHANED_COUNT" -gt "$ORPHAN_THRESHOLD" ]; then
        echo "⚠ Orphaned count ($ORPHANED_COUNT) exceeds threshold ($ORPHAN_THRESHOLD)" >&2

        if [ "$FAIL_ON_ORPHANS" = "true" ]; then
            echo "Error: Commit rejected due to orphaned comments (set comment-system.fail-on-orphans=false to allow)" >&2
            exit 1
        fi
    fi
else
    echo "✓ No orphaned comments" >&2
fi

exit 0
