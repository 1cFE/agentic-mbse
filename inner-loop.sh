#!/bin/bash
set -euo pipefail

# =============================================================================
# inner-loop.sh — Plan → Build → Eval cycle with retry
# =============================================================================
#
# Usage: ./inner-loop.sh [--max-retries N] [--plan-iters N] [--build-iters N]
#
# Exit codes:
#   0 — PASS or CONVERGED (specs met)
#   1 — Max retries exhausted (all attempts produced RETRY)
#
# =============================================================================

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------

MAX_RETRIES=2
PLAN_ITERS=2
BUILD_ITERS=8

while [[ $# -gt 0 ]]; do
    case $1 in
        --max-retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        --plan-iters)
            PLAN_ITERS="$2"
            shift 2
            ;;
        --build-iters)
            BUILD_ITERS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $(basename "$0") [--max-retries N] [--plan-iters N] [--build-iters N]"
            echo ""
            echo "Options:"
            echo "  --max-retries N   Max eval→retry cycles (default: 2)"
            echo "  --plan-iters N    Plan iterations per retry (default: 2)"
            echo "  --build-iters N   Build iterations per retry (default: 8)"
            exit 0
            ;;
        *)
            log_error "Unknown argument: $1"
            ;;
    esac
done

CURRENT_BRANCH=$(git branch --show-current)

echo -e "\n${GREEN}Inner Loop — Plan → Build → Eval${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Max retries:    $MAX_RETRIES"
echo "  Plan iters:     $PLAN_ITERS"
echo "  Build iters:    $BUILD_ITERS"
echo "  Build model:    $BUILD_MODEL"
echo "  Eval model:     $EVAL_MODEL"
echo "  Branch:         $CURRENT_BRANCH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# -----------------------------------------------------------------------------
# Retry loop
# -----------------------------------------------------------------------------

for RETRY in $(seq 1 "$MAX_RETRIES"); do
    log_step "Retry $RETRY/$MAX_RETRIES"
    log_timestamp "START inner-loop retry $RETRY"

    # Step 1: Wipe implementation plan and build-done sentinel (not source code)
    rm -f IMPLEMENTATION_PLAN.md .build-done
    log_info "Wiped IMPLEMENTATION_PLAN.md and .build-done"

    # Step 2: Plan phase
    log_step "Plan phase ($PLAN_ITERS iterations)"
    for i in $(seq 1 "$PLAN_ITERS"); do
        log_info "Plan iteration $i/$PLAN_ITERS"
        log_timestamp "START plan iteration $i"
        cat PROMPT_plan.md | claude -p \
            --dangerously-skip-permissions \
            --output-format stream-json \
            --model "$BUILD_MODEL" \
            --verbose
        log_timestamp "END   plan iteration $i"
    done

    # Step 3: Build phase
    log_step "Build phase ($BUILD_ITERS iterations)"
    for i in $(seq 1 "$BUILD_ITERS"); do
        log_info "Build iteration $i/$BUILD_ITERS"
        log_timestamp "START build iteration $i"
        cat PROMPT_build.md | claude -p \
            --dangerously-skip-permissions \
            --output-format stream-json \
            --model "$BUILD_MODEL" \
            --verbose
        log_timestamp "END   build iteration $i"

        if [[ -f .build-done ]]; then
            log_info "Build agent signaled completion — skipping remaining iterations"
            break
        fi
    done

    # Step 4: Eval phase
    log_step "Eval phase"
    log_timestamp "START eval"

    EVAL_OUTPUT=$(cat PROMPT_eval.md | claude -p \
        --dangerously-skip-permissions \
        --output-format text \
        --model "$EVAL_MODEL")

    # Save per-retry eval report (preserves history across retries)
    echo "$EVAL_OUTPUT" > "eval-report-retry-${RETRY}.md"
    # Also save as canonical eval-report.md (outer loop reads this)
    echo "$EVAL_OUTPUT" > eval-report.md
    log_info "Saved eval-report.md and eval-report-retry-${RETRY}.md"

    log_timestamp "END   eval"

    # Step 5: Parse verdict
    VERDICT=$(echo "$EVAL_OUTPUT" | grep -oP 'VERDICT:\s*\K\w+' | tail -1 || true)

    if [[ -z "$VERDICT" ]]; then
        log_info "WARNING: EvalAgent produced no VERDICT line — treating as RETRY"
        VERDICT="RETRY"
    fi

    log_info "Verdict: $VERDICT"

    # Step 6: Act on verdict
    if [[ "$VERDICT" == "PASS" ]]; then
        log_step "PASS — inner loop complete (retry $RETRY/$MAX_RETRIES)"
        log_timestamp "END   inner-loop: PASS"
        exit 0
    elif [[ "$VERDICT" == "CONVERGED" ]]; then
        log_step "CONVERGED — goals fully met (retry $RETRY/$MAX_RETRIES)"
        log_timestamp "END   inner-loop: CONVERGED"
        exit 0
    fi

    if [[ "$RETRY" -lt "$MAX_RETRIES" ]]; then
        log_info "RETRY ($RETRY/$MAX_RETRIES) — eval failed, retrying..."
    else
        log_info "Max retries exhausted ($MAX_RETRIES) — inner loop failed"
    fi

    log_timestamp "END   inner-loop retry $RETRY: $VERDICT"
done

# All retries exhausted
log_step "FAILED — max retries exhausted ($MAX_RETRIES attempts, all RETRY)"
log_timestamp "END   inner-loop: FAILED (max retries)"
exit 1
