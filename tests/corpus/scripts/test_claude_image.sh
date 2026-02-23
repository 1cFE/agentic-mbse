#!/bin/bash
# =============================================================================
# test_claude_image.sh — Verify claude -p can process images via Read tool
# =============================================================================
#
# Tests whether `claude -p` can read and describe a PNG page image.
# This is the riskiest step in Phase 0 — if this doesn't work, the
# experiment architecture changes.
#
# Usage:
#   ./test_claude_image.sh [image_path]
#
# Default image: /tmp/test_page_hsu.png (rendered by render_pages.sh)
# =============================================================================

set -euo pipefail

IMAGE="${1:-/tmp/test_page_hsu.png}"

if [[ ! -f "$IMAGE" ]]; then
    echo "ERROR: Image not found: $IMAGE" >&2
    echo "Run render_pages.sh first, or pass an image path." >&2
    exit 1
fi

ABS_IMAGE="$(realpath "$IMAGE")"
echo "Testing claude -p with image: $ABS_IMAGE"
echo "Image size: $(du -h "$ABS_IMAGE" | cut -f1)"
echo ""

PROMPT="Read the image file at ${ABS_IMAGE} and describe what you see in 2-3 sentences. Focus on whether this is a scientific document page, and mention any tables, equations, or figures you observe."

echo "--- Prompt ---"
echo "$PROMPT"
echo "--------------"
echo ""
echo "Invoking claude -p (text output)..."
START=$(date +%s)

OUTPUT=$(echo "$PROMPT" | env -u CLAUDECODE claude -p \
    --dangerously-skip-permissions \
    --model sonnet \
    --output-format text \
    --allowedTools "Read" \
    --no-session-persistence 2>&1)

END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "--- Output ($ELAPSED seconds) ---"
echo "$OUTPUT"
echo "--- End ---"
echo ""

# Quick sanity check
if [[ -z "$OUTPUT" ]]; then
    echo "FAIL: Empty output"
    exit 1
elif echo "$OUTPUT" | grep -qi "error\|cannot\|unable"; then
    echo "WARN: Output may contain errors (check above)"
else
    echo "OK: Got non-empty output in ${ELAPSED}s"
fi

echo ""
echo "Now testing with JSON output for token usage..."
JSON_OUTPUT=$(echo "$PROMPT" | env -u CLAUDECODE claude -p \
    --dangerously-skip-permissions \
    --model sonnet \
    --output-format json \
    --allowedTools "Read" \
    --no-session-persistence 2>&1)

echo "--- JSON Output ---"
echo "$JSON_OUTPUT" | python3 -m json.tool 2>/dev/null || echo "$JSON_OUTPUT"
echo "--- End ---"
