#!/bin/bash
# =============================================================================
# lib.sh — Shared utilities for the experiment iteration loop
# =============================================================================
#
# Sourced by: experiment-init.sh, outer-loop.sh, inner-loop.sh
# Ported from: ~/.claude/scripts/ralph-init.sh (validate_generation, fixup, etc.)
#
# =============================================================================

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

SPEC_MODEL="${EXPERIMENT_SPEC_MODEL:-opus}"
PLAN_MODEL="${EXPERIMENT_PLAN_MODEL:-sonnet}"
BUILD_MODEL="${EXPERIMENT_BUILD_MODEL:-sonnet}"
EVAL_MODEL="${EXPERIMENT_EVAL_MODEL:-sonnet}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SPECS="$HOME/.claude/scripts/validate-specs-output.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# -----------------------------------------------------------------------------
# Dependency checks (fail fast at source time)
# -----------------------------------------------------------------------------

require_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || {
        echo -e "${RED}ERROR: '$cmd' not found in PATH${NC}" >&2
        exit 1
    }
}

require_command claude

[[ -f "$VALIDATE_SPECS" ]] || {
    echo -e "${RED}ERROR: validate-specs-output.sh not found at $VALIDATE_SPECS${NC}" >&2
    exit 1
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_info() {
    echo -e "${YELLOW}  → $1${NC}"
}

log_error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
    exit 1
}

log_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# -----------------------------------------------------------------------------
# Agent output validation
# -----------------------------------------------------------------------------

# Validate that generation output is actual content, not a conversational summary
# Args: $1=output, $2=min_lines (default 20)
# Returns: 0 (valid) or 1 (summary detected)
validate_generation() {
    local output="$1"
    local min_lines="${2:-20}"

    local line_count
    line_count=$(echo "$output" | wc -l)

    if [[ "$line_count" -lt "$min_lines" ]]; then
        log_info "Validation FAIL: output too short ($line_count lines, minimum $min_lines)" >&2
        return 1
    fi

    # Check if first non-empty line looks like conversational preamble
    local first_line
    first_line=$(echo "$output" | sed '/^[[:space:]]*$/d' | head -1)

    if [[ "$first_line" =~ ^(I\'ve\ |I\ have\ |Here\'s\ |Here\ are|Here\ is|Below\ |The\ following\ |Sure|Let\ me|Certainly|Of\ course) ]]; then
        log_info "Validation FAIL: conversational preamble detected: '${first_line:0:60}...'" >&2
        return 1
    fi

    # Catch "The <noun> is ready/complete/done" — meta-commentary about content
    if [[ "$first_line" =~ ^The\ .+\ (is\ ready|is\ complete|is\ done|has\ been) ]]; then
        log_info "Validation FAIL: meta-commentary detected: '${first_line:0:60}...'" >&2
        return 1
    fi

    # Catch "Summary of" at start
    if [[ "$first_line" =~ ^Summary\ (of|:) ]]; then
        log_info "Validation FAIL: summary header detected: '${first_line:0:60}...'" >&2
        return 1
    fi

    # Check for tool-use artifacts (Claude asking for permissions)
    if echo "$output" | grep -qiE '(please approve|file write permission|approve the|permission to write|ready to write)'; then
        log_info "Validation FAIL: tool-use artifact detected (Claude asked for permissions instead of producing content)" >&2
        return 1
    fi

    return 0
}

# Re-generate when output was a summary instead of actual content
# Args: $1=raw_output, $2=original_prompt, $3=model
fixup_generate() {
    local raw_output="$1"
    local original_prompt="$2"
    local model="$3"

    local line_count
    line_count=$(echo "$raw_output" | wc -l)
    local first_line
    first_line=$(echo "$raw_output" | sed '/^[[:space:]]*$/d' | head -1)

    local fixup_prompt
    fixup_prompt="Your previous response was a conversational summary (${line_count} lines starting with: '${first_line:0:80}'). That is NOT what was requested. Output the COMPLETE content as specified in the original prompt. Start DIRECTLY with the content — no introductory text, no explanations, no preamble.

---

ORIGINAL PROMPT:

${original_prompt}"

    log_info "Fix-up: re-generating with explicit content instruction" >&2
    local output
    output=$(echo "$fixup_prompt" | claude -p --dangerously-skip-permissions --model "$model" --output-format text)
    echo "$output"
}

# Run claude headless and capture output, with validation + fix-up
# Args: $1=prompt, $2=description, $3=min_lines (default 20), $4=model (default $SPEC_MODEL)
claude_generate() {
    local prompt="$1"
    local description="$2"
    local min_lines="${3:-20}"
    local model="${4:-$SPEC_MODEL}"

    log_info "Generating: $description (model: $model)" >&2
    local output
    output=$(echo "$prompt" | claude -p --dangerously-skip-permissions --model "$model" --output-format text)

    if [[ -z "$output" ]]; then
        log_error "Generation failed (empty output): $description"
    fi

    if ! validate_generation "$output" "$min_lines"; then
        log_info "Attempting fix-up for: $description" >&2
        output=$(fixup_generate "$output" "$prompt" "$model")

        if [[ -z "$output" ]]; then
            log_error "Fix-up generation failed (empty output): $description"
        fi

        if ! validate_generation "$output" "$min_lines"; then
            log_info "Warning: fix-up output still looks like a summary, proceeding anyway" >&2
        fi
    fi

    echo "$output"
}

# -----------------------------------------------------------------------------
# Build-done detection
# -----------------------------------------------------------------------------

# Check if all tasks in IMPLEMENTATION_PLAN.md are marked [DONE].
# If so, write .build-done sentinel and return 0; otherwise return 1.
check_build_done() {
    [[ -f IMPLEMENTATION_PLAN.md ]] || return 1

    local total done remaining
    total=$(grep -cE '^\*\*Task [0-9]+' IMPLEMENTATION_PLAN.md 2>/dev/null || echo 0)
    [[ "$total" -gt 0 ]] || return 1

    done=$(grep -cE '^\*\*Task [0-9]+.*\[DONE\]' IMPLEMENTATION_PLAN.md 2>/dev/null || echo 0)
    remaining=$((total - done))

    if [[ "$remaining" -eq 0 ]]; then
        echo "ALL_TASKS_COMPLETE" > .build-done
        log_info "check_build_done: all $total tasks complete — wrote .build-done"
        return 0
    fi
    return 1
}

# -----------------------------------------------------------------------------
# Spec parsing
# -----------------------------------------------------------------------------

# Parse fenced ```markdown specs/filename.md blocks from agent output into files
# Args: $1=output text
parse_specs_from_output() {
    local output="$1"

    echo "$output" | awk '
    { gsub(/\r$/, "") }
    /^```markdown specs\/[^`]+\.md[[:space:]]*$/ {
        match($0, /specs\/[^`]+\.md/)
        filename = substr($0, RSTART, RLENGTH)
        getline
        content = ""
        while (getline > 0 && !/^```[[:space:]]*$/) {
            content = content $0 "\n"
        }
        print content > filename
        close(filename)
    }
    '
}

# Validate spec output using validate-specs-output.sh
# Args: $1=output text
# Returns: 0 on PASS, 1 on FAIL (prints validation message)
validate_specs() {
    local output="$1"
    local result
    result=$(echo "$output" | "$VALIDATE_SPECS" 2>&1) || true

    echo "$result"
    [[ "$result" == PASS:* ]]
}
