#!/bin/bash
set -euo pipefail

# =============================================================================
# outer-loop.sh — Outer iteration driver
# =============================================================================
#
# Usage: ./outer-loop.sh [--max N] [--dry-run] [--model <model>]
#
# Runs the IterationSpecAgent → inner-loop → archive → log → push cycle.
#
# =============================================================================

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------

MAX_ITERATIONS=0  # 0 = unlimited
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --max)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --model)
            SPEC_MODEL="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $(basename "$0") [--max N] [--dry-run] [--model <model>]"
            echo ""
            echo "Options:"
            echo "  --max N          Max outer iterations (default: 0 = unlimited)"
            echo "  --dry-run        Show what would happen without executing"
            echo "  --model <model>  Override model for IterationSpecAgent (default: $SPEC_MODEL)"
            exit 0
            ;;
        *)
            log_error "Unknown argument: $1"
            ;;
    esac
done

# Validate workspace
[[ -f GOALS.md ]] || log_error "GOALS.md not found — run experiment-init.sh first"
[[ -f experiment-log.md ]] || log_error "experiment-log.md not found — run experiment-init.sh first"
[[ -f iteration-count ]] || log_error "iteration-count not found — run experiment-init.sh first"
[[ -f PROMPT_iteration_spec.md ]] || log_error "PROMPT_iteration_spec.md not found"
[[ -f PROMPT_eval.md ]] || log_error "PROMPT_eval.md not found"
[[ -f PROMPT_plan.md ]] || log_error "PROMPT_plan.md not found"
[[ -f PROMPT_build.md ]] || log_error "PROMPT_build.md not found"
[[ -f challenge-rules.conf ]] || log_error "challenge-rules.conf not found — run experiment-init.sh first"

CURRENT_BRANCH=$(git branch --show-current)

echo -e "\n${GREEN}Outer Loop — Experimental Convergence${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Max iterations: $( [[ "$MAX_ITERATIONS" -eq 0 ]] && echo "unlimited" || echo "$MAX_ITERATIONS" )"
echo "  Spec model:     $SPEC_MODEL"
echo "  Build model:    $BUILD_MODEL"
echo "  Eval model:     $EVAL_MODEL"
echo "  Branch:         $CURRENT_BRANCH"
[[ "$DRY_RUN" = true ]] && echo "  Mode:           DRY RUN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# -----------------------------------------------------------------------------
# Outer loop
# -----------------------------------------------------------------------------

while true; do
    # Step 1: Increment iteration counter
    ITER=$(cat iteration-count)
    ITER=$((ITER + 1))

    # Max iterations check
    if [[ "$MAX_ITERATIONS" -gt 0 ]] && [[ "$ITER" -gt "$MAX_ITERATIONS" ]]; then
        log_step "Max iterations reached ($MAX_ITERATIONS) — stopping"
        break
    fi

    echo "$ITER" > iteration-count
    ITER_PADDED=$(printf "%03d" "$ITER")

    log_step "Outer Iteration $ITER"
    log_timestamp "START outer iteration $ITER"

    # Dry-run mode
    if [[ "$DRY_RUN" = true ]]; then
        echo "  [DRY RUN] Would:"
        echo "    1. Wipe specs/ and iteration-brief.md"
        echo "    2. Run IterationSpecAgent (model: $SPEC_MODEL)"
        echo "    3. Validate specs output"
        echo "    4. Check for CONVERGED signal"
        echo "    5. Run inner-loop.sh"
        echo "    6. Archive to experiment-history/iteration-${ITER_PADDED}/"
        echo "    7. Append to experiment-log.md"
        echo "    8. Git commit and push"
        echo ""
        # Reset counter since we didn't actually do anything
        echo "$((ITER - 1))" > iteration-count
        break
    fi

    # Step 2: Wipe specs and previous iteration brief
    rm -f specs/*.md iteration-brief.md
    mkdir -p specs
    log_info "Wiped specs/ and iteration-brief.md"

    # Step 3: Build IterationSpecAgent prompt via string concatenation
    PROMPT="$(cat PROMPT_iteration_spec.md)

---

CURRENT ITERATION: $ITER

---

GOALS:
$(cat GOALS.md)

---

EXPERIMENT LOG:
$(cat experiment-log.md)

---

CHALLENGE RULES:
$(cat challenge-rules.conf)"

    log_info "Running IterationSpecAgent (model: $SPEC_MODEL)"
    log_timestamp "START IterationSpecAgent"

    OUTPUT=$(claude_generate "$PROMPT" "IterationSpecAgent" 5 "$SPEC_MODEL")

    log_timestamp "END   IterationSpecAgent"

    # Step 4: Validate IterationSpecAgent output
    log_info "Validating spec output..."

    # Path A: Agent wrote specs directly via tools (preferred)
    SPEC_COUNT=$(find specs -maxdepth 1 -name '*.md' -size +0c 2>/dev/null | wc -l)

    if [[ "$SPEC_COUNT" -eq 0 ]]; then
        # Path B: Try parsing fenced blocks from stdout
        log_info "No spec files found — trying fenced block parsing from output"
        SPEC_VALIDATION=$(validate_specs "$OUTPUT" 2>&1) || true
        if [[ "$SPEC_VALIDATION" == PASS:* ]]; then
            log_info "Spec validation: $SPEC_VALIDATION"
            parse_specs_from_output "$OUTPUT"
            SPEC_COUNT=$(find specs -maxdepth 1 -name '*.md' -size +0c 2>/dev/null | wc -l)
        else
            log_info "Spec validation failed: $SPEC_VALIDATION"
            # Save raw output for debugging
            echo "$OUTPUT" > specs/_raw_output.md
            log_error "IterationSpecAgent failed to produce valid specs. Raw output saved to specs/_raw_output.md"
        fi
    fi

    log_info "Specs found: $SPEC_COUNT"

    # Validate iteration-brief.md exists
    if [[ ! -s iteration-brief.md ]]; then
        log_info "WARNING: IterationSpecAgent did not produce iteration-brief.md"
        echo "Iteration $ITER — specs generated but no brief provided" > iteration-brief.md
    fi

    # Step 4b: Check for CONVERGED signal (design review fix #1)
    if grep -rq '^CONVERGED:' specs/ 2>/dev/null; then
        log_step "CONVERGED — IterationSpecAgent says all goals met"
        log_timestamp "CONVERGED at iteration $ITER"

        # Archive
        ARCHIVE_DIR="experiment-history/iteration-${ITER_PADDED}"
        mkdir -p "$ARCHIVE_DIR/specs"
        cp specs/*.md "$ARCHIVE_DIR/specs/"
        cp iteration-brief.md "$ARCHIVE_DIR/"

        # Log
        BRIEF=$(head -1 iteration-brief.md)
        EVIDENCE=$(grep '^CONVERGED:' specs/*.md | head -1)
        cat >> experiment-log.md << EOF

---

## Iteration $ITER — $(date '+%Y-%m-%d')
**Brief:** $BRIEF
**Outcome:** CONVERGED
**Evidence:** $EVIDENCE
EOF

        # Commit and push
        git add specs/ iteration-brief.md experiment-log.md experiment-history/ iteration-count
        if ! git diff --cached --quiet 2>/dev/null; then
            git commit -m "iteration $ITER: CONVERGED — $(head -1 iteration-brief.md)"
            log_info "Committed convergence at iteration $ITER"
        else
            log_info "No changes to commit"
        fi
        git push origin "$CURRENT_BRANCH" 2>/dev/null || \
            git push -u origin "$CURRENT_BRANCH"

        log_step "Experiment complete — CONVERGED at iteration $ITER"
        break
    fi

    # Step 5: Run inner loop
    log_step "Running inner loop"
    log_timestamp "START inner-loop"

    INNER_EXIT=0
    ./inner-loop.sh || INNER_EXIT=$?

    if [[ "$INNER_EXIT" -ne 0 ]]; then
        log_info "WARNING: inner loop exited with status $INNER_EXIT (max retries exhausted)"
    fi

    log_timestamp "END   inner-loop (exit: $INNER_EXIT)"

    # Step 6: Archive iteration
    ARCHIVE_DIR="experiment-history/iteration-${ITER_PADDED}"
    mkdir -p "$ARCHIVE_DIR/specs"
    cp specs/*.md "$ARCHIVE_DIR/specs/"
    cp iteration-brief.md "$ARCHIVE_DIR/"
    # Archive all eval reports (retries + final)
    for f in eval-report*.md; do
        [[ -f "$f" ]] && cp "$f" "$ARCHIVE_DIR/"
    done
    log_info "Archived to $ARCHIVE_DIR/"

    # Step 7: Append to experiment-log.md
    BRIEF=$(head -1 iteration-brief.md)
    SPEC_LIST=$(ls specs/*.md 2>/dev/null | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')

    # Determine verdict (design review fix #6: use INNER_EXIT as fallback)
    VERDICT="TIMEOUT"
    if [[ -f eval-report.md ]]; then
        VERDICT=$(grep -oP 'VERDICT:\s*\K\w+' eval-report.md | tail -1 || true)
    fi
    if [[ -z "$VERDICT" ]]; then
        if [[ "$INNER_EXIT" -ne 0 ]]; then
            VERDICT="TIMEOUT"
        else
            VERDICT="PASS"
        fi
    fi

    # Extract Key Learnings from eval report (design review fix #2)
    KEY_LEARNINGS=""
    if [[ -f eval-report.md ]]; then
        KEY_LEARNINGS=$(sed -n '/Key observations:/,/^$/p' eval-report.md | head -10)
    fi
    if [[ -z "$KEY_LEARNINGS" ]]; then
        if [[ "$INNER_EXIT" -ne 0 ]]; then
            KEY_LEARNINGS="- Inner loop exited with status $INNER_EXIT (max retries exhausted)"
        else
            KEY_LEARNINGS="- Inner loop completed successfully"
        fi
    fi

    # List corpus slugs (python3, no jq dependency — design decision #9)
    CORPUS_SLUGS=$(python3 -c "
import json, sys
for line in open('tests/corpus/papers.jsonl'):
    line = line.strip()
    if line: print(json.loads(line)['slug'], end=', ')
" 2>/dev/null || echo "(could not read corpus)")

    cat >> experiment-log.md << EOF

---

## Iteration $ITER — $(date '+%Y-%m-%d')
**Brief:** $BRIEF
**Specs:** $SPEC_LIST
**Outcome:** $VERDICT
**Key Learnings:**
$KEY_LEARNINGS
**Corpus:** $CORPUS_SLUGS
EOF

    log_info "Updated experiment-log.md"

    # Step 8: Commit and push
    log_step "Committing and pushing"

    # Stage specific files (design review fix #7: targeted staging)
    git add specs/ experiment-history/ experiment-log.md iteration-brief.md \
        iteration-count IMPLEMENTATION_PLAN.md \
        src/ tests/ AGENTS.md 2>/dev/null || true
    # Also stage eval reports and any modified tracked files
    for f in eval-report*.md; do
        [[ -f "$f" ]] && git add "$f"
    done
    git add -u  # Stage modifications to already-tracked files

    if ! git diff --cached --quiet 2>/dev/null; then
        git commit -m "iteration $ITER: $VERDICT — $(head -1 iteration-brief.md)"
        log_info "Committed iteration $ITER"
    else
        log_info "No changes to commit"
    fi

    git push origin "$CURRENT_BRANCH" 2>/dev/null || \
        git push -u origin "$CURRENT_BRANCH"
    log_info "Pushed to $CURRENT_BRANCH"

    # Step 9: Check for CONVERGED verdict from inner loop
    if [[ "$VERDICT" == "CONVERGED" ]]; then
        log_step "CONVERGED — experiment complete at iteration $ITER"
        break
    fi

    log_timestamp "END   outer iteration $ITER: $VERDICT"
    echo ""
done

log_step "Outer loop finished"
log_timestamp "END   outer-loop"
