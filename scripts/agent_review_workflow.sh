#!/usr/bin/env bash
# agent_review_workflow.sh - Demonstrate agent-agent review pattern (AC-2)
#
# Usage: ./scripts/agent_review_workflow.sh <FILE> <AGENT1_OUTPUT> <AGENT2_REVIEW_PROMPT>
#
# Example:
#   ./scripts/agent_review_workflow.sh PLAN.md plan_v1.md "Review for completeness"
#
# This script demonstrates REQ-2 (Agent-Agent Review):
#   1. Agent 1 writes artifact (already completed, passed as AGENT1_OUTPUT)
#   2. Agent 2 reviews using comment_add tool (simulated here with CLI)
#   3. Human can then review Agent 2's comments and filter/prioritize
#   4. Agent 1 addresses comments (out of scope for this script)
#
# Exit codes:
#   0 - Success
#   1 - Usage error
#   2 - System error

set -euo pipefail

# Check if comment CLI is available
if ! command -v comment &> /dev/null; then
    echo "Error: 'comment' CLI not found. Install agentic-mbse comment system." >&2
    exit 2
fi

# Parse arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <FILE> <AGENT1_OUTPUT> <AGENT2_REVIEW_PROMPT>" >&2
    exit 1
fi

FILE="$1"
AGENT1_OUTPUT="$2"
AGENT2_REVIEW_PROMPT="$3"

# Verify file exists
if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE" >&2
    exit 1
fi

# Verify agent 1 output exists (artifact already generated)
if [ ! -f "$AGENT1_OUTPUT" ]; then
    echo "Error: Agent 1 output not found: $AGENT1_OUTPUT" >&2
    exit 1
fi

echo "=== Agent-Agent Review Workflow ===" >&2
echo "File to review: $FILE" >&2
echo "Agent 1 output: $AGENT1_OUTPUT" >&2
echo "Agent 2 review prompt: $AGENT2_REVIEW_PROMPT" >&2
echo >&2

# Step 1: Verify source file is unchanged (AC-2 requirement)
SOURCE_HASH_BEFORE=$(sha256sum "$FILE" | awk '{print $1}')
echo "Source file hash before review: $SOURCE_HASH_BEFORE" >&2

# Step 2: Agent 2 adds review comments
# (Simulated: in real workflow, Agent 2 would use comment_add tool via MCP)
# For demo, we add a sample comment
echo "Agent 2 adding review comment..." >&2
THREAD_ID=$(comment add "$FILE" -L 1:1 "$AGENT2_REVIEW_PROMPT" | grep "Thread ID:" | awk '{print $3}')
echo "Created thread: $THREAD_ID" >&2

# Step 3: Verify source file is still unchanged (AC-2)
SOURCE_HASH_AFTER=$(sha256sum "$FILE" | awk '{print $1}')
if [ "$SOURCE_HASH_BEFORE" != "$SOURCE_HASH_AFTER" ]; then
    echo "Error: Source file was modified during review (AC-2 violation)" >&2
    exit 2
fi
echo "✓ Source file unchanged (AC-2 verified)" >&2

# Step 4: Show sidecar contains review thread (AC-2)
SIDECAR_PATH=$(comment show "$THREAD_ID" | grep "Sidecar:" | awk '{print $2}')
if [ ! -f "$SIDECAR_PATH" ]; then
    echo "Error: Sidecar not created" >&2
    exit 2
fi
echo "✓ Sidecar exists at: $SIDECAR_PATH" >&2

# Step 5: List all review comments for human filtering
echo >&2
echo "Review comments (for human filtering/prioritization):" >&2
comment list "$FILE" --status=open

echo >&2
echo "=== Workflow Complete ===" >&2
echo "Next steps:" >&2
echo "  1. Human reviews Agent 2's comments above" >&2
echo "  2. Human filters/prioritizes comments" >&2
echo "  3. Agent 1 addresses remaining comments via 'comment reply' and 'comment resolve'" >&2

exit 0
