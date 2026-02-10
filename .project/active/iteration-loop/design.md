# Design: Iteration Loop — Experimental Orchestration for Claude Code

**Status:** Revised (post-review)
**Owner:** Reid W
**Created:** 2026-02-10 09:43 PST
**Branch:** ralph/doc-ingest
**Commit:** cc99347

---

## Overview

Three shell scripts and four prompt templates that replace the Ralph Wiggum loop with an experimental convergence loop. The human provides qualitative goals; the system iteratively generates quantitative specs (IterationSpecAgent), runs plan→build→eval cycles (inner loop), archives results, and adapts (outer loop).

## Related Artifacts

- **Spec:** `.project/active/iteration-loop/spec.md`
- **Ralph reference:** `~/.claude/scripts/ralph-init.sh` (1216 lines — design, review, refine, specs, AGENTS, plan/build prompts, loop)
- **Spec validator:** `~/.claude/scripts/validate-specs-output.sh` (121 lines — fenced block parser)
- **Current loop.sh:** `loop.sh` (48 lines — simple while loop with `claude -p`)
- **Current PROMPT_plan.md / PROMPT_build.md:** plan and build prompt templates (42 / 48 lines)
- **AGENTS.md:** operational guide for doc-ingest (155 lines — build commands, codebase layout, gotchas)
- **Test corpus:** `tests/corpus/papers.jsonl` (5 papers), `tests/corpus/pdfs/`, `tests/corpus/baseline/`, `tests/test_corpus.py`

---

## Research Findings

### Ralph Loop Patterns Worth Carrying Forward

From `~/.claude/scripts/ralph-init.sh`:

1. **`validate_generation()`** (line 91): Detects when claude produces conversational summaries instead of content. Checks line count minimum, conversational preamble patterns, meta-commentary, tool-use artifacts.

2. **`fixup_generate()`** (line 135): Re-prompts claude when validation fails, explicitly stating the problem and demanding direct content output.

3. **`claude_generate()`** (line 162): Wraps validation + fixup into a single call. This is the core pattern for reliable headless generation.

4. **Spec parsing** (line 826): AWK script that extracts `\`\`\`markdown specs/filename.md` fenced blocks into individual files.

5. **`validate-specs-output.sh`**: Standalone validator for fenced spec blocks. Reports exact failure reasons (prose detected, wrong fence format, empty blocks, unclosed fences). Returns `PASS: N spec blocks found` on success.

6. **Resume pattern** (`step_complete()` at line 61): Checks if step output files exist. Allows re-running after failures without redoing completed steps.

### Current Loop Architecture

`loop.sh` (line 37) runs: `cat "$PROMPT_FILE" | claude -p --dangerously-skip-permissions --output-format=stream-json --model sonnet --verbose`

Key observations:
- `--dangerously-skip-permissions`: agents have full tool access (file read/write, bash execution)
- `--output-format=stream-json`: streams full conversation including tool traces to stdout
- `--output-format=text`: returns only the agent's final text response
- Prompt is piped via stdin — the agent's context is the prompt + whatever it reads via tools

### Test Corpus Infrastructure

`tests/test_corpus.py` provides:
- `load_corpus_papers()` reads `papers.jsonl`
- `extract_paper_with_current_pipeline()` runs extraction and measures time
- `compute_metrics()` produces `ExtractionMetrics` (char_count, heading_count, table_row_count)
- `compare_metrics()` produces percentage changes vs baseline
- Regression test allows per-paper thresholds via `heading_regression_pct` in papers.jsonl
- Tests gated behind `--run-corpus` flag

### Existing Artifacts to Remove (FR-9)

Present in worktree and slated for cleanup:
- `DESIGN.md` (11KB, ralph-generated design doc)
- `PROMPT_plan.md` (42 lines, replaced by iteration-aware version)
- `PROMPT_build.md` (48 lines, replaced with minor updates)
- `loop.sh` (48 lines, replaced by outer-loop.sh + inner-loop.sh)
- `ralph-init.log` (22KB)
- `specs/` contents (4 spec files, replaced by IterationSpecAgent output)
- `IMPLEMENTATION_PLAN.md` (37KB, wiped on first inner loop)

Present in worktree and preserved:
- `src/` (all source code)
- `tests/` (all tests)
- `AGENTS.md` (operational guide — needs manual update to remove status section)
- `pyproject.toml`, `uv.lock`, `.gitignore`

---

## Design Decisions

Resolved during design review:

1. **CONVERGED check moved to Step 4b** (between spec validation and inner loop). If the IterationSpecAgent signals convergence, the inner loop is skipped entirely — running plan→build on a "CONVERGED" spec is nonsensical.

2. **Key Learnings populated from eval-report.md.** The outer loop extracts the "Key observations" section from the eval report and writes it inline into the experiment-log entry. No more placeholder text.

3. **String concatenation, not template placeholders.** The outer loop builds the IterationSpecAgent prompt by concatenating the static template with runtime context via bash heredoc. No `{{PLACEHOLDER}}` substitution — simpler and matches the code.

4. **Eval agent write permissions documented as known trade-off.** `claude -p --dangerously-skip-permissions` is all-or-nothing. The prompt says "READ-ONLY" but enforcement is by convention only. Acceptable because the agent has no incentive to modify code, and git provides a safety net.

5. **Eval reports preserved across retries.** Each retry saves `eval-report-retry-N.md`. The latest is also saved as `eval-report.md` for the outer loop. All copies are archived in `experiment-history/`.

6. **INNER_EXIT used for logging.** The inner loop exit code is captured and logged as a warning if non-zero. The outer loop always proceeds to archive/log/commit regardless (a failed inner loop is still a data point for the next outer iteration).

7. **Targeted git staging.** `git add` lists specific paths instead of `-A` to prevent accidentally committing large PDFs, `.env`, or temp files. `.gitignore` also updated with `*.pdf`, `.env`, `tests/corpus/pool/`.

8. **External dependencies checked at lib.sh source time.** `validate-specs-output.sh` existence and `claude` CLI availability are verified when `lib.sh` is sourced, failing fast instead of mid-execution.

9. **No jq dependency.** Corpus slug listing uses a python3 one-liner instead of `jq` (python3 is already required by the project).

---

## Proposed Design

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ experiment-init.sh                                                  │
│  Creates workspace: GOALS.md, experiment-log.md, iteration-count,  │
│  challenge-rules.conf, experiment-history/                          │
│  Cleans old ralph artifacts                                         │
│  Sources: lib.sh                                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ outer-loop.sh  (one cycle = one "outer iteration")                  │
│                                                                     │
│  1. Increment iteration-count                                       │
│  2. Wipe specs/                                                     │
│  3. Run IterationSpecAgent (PROMPT_iteration_spec.md)               │
│     ├─ Agent: reads GOALS, log, corpus, runs tests                  │
│     ├─ Output: fenced spec blocks → parsed into specs/              │
│     └─ Side-effect: writes iteration-brief.md                       │
│  4. Validate: specs exist, iteration-brief.md exists                │
│  4b. Check for CONVERGED signal → archive, log, commit, break       │
│  5. inner-loop.sh ──────────────────────────────┐                   │
│  6. Archive to experiment-history/iteration-NNN/ │                   │
│  7. Append entry to experiment-log.md            │                   │
│     (extract Key Learnings from eval-report.md)  │                   │
│  8. git add <specific files> && git commit && git push              │
│  Sources: lib.sh                                 │                   │
└──────────────────────────────────────────────────┼──────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ inner-loop.sh  (plan → build → eval, with retry)                    │
│                                                                     │
│  For each retry (max_retries, default 2):                           │
│    1. Wipe IMPLEMENTATION_PLAN.md                                   │
│    2. Plan: claude -p × plan_iterations (default 2)                 │
│       PROMPT_plan.md (reads specs/, produces IMPLEMENTATION_PLAN.md)│
│    3. Build: claude -p × build_iterations (default 8)               │
│       PROMPT_build.md (picks tasks, implements, tests, commits)     │
│    4. Eval: claude -p × 1                                           │
│       PROMPT_eval.md (reads specs, runs tests, produces verdict)    │
│       ├─ Saves eval-report-retry-N.md (+ eval-report.md = latest)  │
│       └─ Parses VERDICT: PASS / RETRY                               │
│    5. If PASS → exit 0                                              │
│    6. If RETRY → continue loop                                      │
│  Exit 1 if max retries exhausted                                    │
│  Sources: lib.sh                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Shared Library: `lib.sh`

All three scripts source a shared helper library to avoid duplication. Extracted from `ralph-init.sh` patterns.

**Location:** `lib.sh` (worktree root, alongside the loop scripts)

**Contents:**

```bash
# Colors and logging
log_step(), log_info(), log_error(), log_timestamp()

# Agent invocation
validate_generation(output, min_lines)    # From ralph-init.sh:91
fixup_generate(raw_output, prompt, model) # From ralph-init.sh:135
claude_generate(prompt, description, min_lines, model)  # Combines above

# Spec parsing
parse_specs_from_output(output)  # AWK parser from ralph-init.sh:826
validate_specs(output)           # Calls validate-specs-output.sh

# Configuration
SPEC_MODEL="${EXPERIMENT_SPEC_MODEL:-opus}"
BUILD_MODEL="${EXPERIMENT_BUILD_MODEL:-sonnet}"
EVAL_MODEL="${EXPERIMENT_EVAL_MODEL:-sonnet}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SPECS="$HOME/.claude/scripts/validate-specs-output.sh"

# Dependency checks (fail fast at source time, not mid-execution)
[[ -f "$VALIDATE_SPECS" ]] || { echo "ERROR: validate-specs-output.sh not found at $VALIDATE_SPECS" >&2; exit 1; }
command -v claude >/dev/null || { echo "ERROR: claude CLI not found" >&2; exit 1; }
```

**Rationale:** `ralph-init.sh` has ~90 lines of helper functions that are directly reusable. Putting them in a shared library avoids copy-pasting across 3 scripts and ensures consistent behavior.

### Script 1: `experiment-init.sh`

**Location:** Worktree root
**Usage:** `./experiment-init.sh <project_name> <goals_file> [options]`

**Options:**
- `--challenge-rules <file>`: Path to challenge rules file (default: creates standard rules)
- `--resume`: Skip initialization, validate existing workspace
- `--model <model>`: Override default model for spec agent
- `--help`: Usage information

**Behavior:**

1. Validate arguments (project name, goals file exists)
2. Validate git repository

3. **Clean old ralph artifacts** (FR-9):
   ```bash
   rm -f DESIGN.md DESIGN_v1.md DESIGN_REVIEW.md ralph-init.log loop.sh
   rm -f specs/*.md  # Wipe old specs (will be regenerated by IterationSpecAgent)
   # Keep: src/, tests/, AGENTS.md, IMPLEMENTATION_PLAN.md, pyproject.toml, uv.lock, .gitignore
   ```

4. **Create workspace artifacts:**
   - Copy goals file → `GOALS.md`
   - Create `experiment-log.md` with header + goals copy
   - Create `iteration-count` containing `0`
   - Create `experiment-history/` directory
   - Write `PROMPT_iteration_spec.md` from template (injecting challenge rules)
   - Write `PROMPT_eval.md` from template
   - Write `PROMPT_plan.md` from template (updated for iteration context)
   - Write `PROMPT_build.md` from template (updated for iteration context)

5. **Create `challenge-rules.conf`:**
   - If `--challenge-rules` provided: copy that file
   - Default for doc-ingest:
     ```
     ADD_PDF_PER_ITERATION=1
     INITIAL_CORPUS=tests/corpus/papers.jsonl
     PDF_POOL_DIR=tests/corpus/pool/
     ```

6. **Update `.gitignore`:** Append entries to prevent accidental staging of large or sensitive files:
   ```
   # Experiment artifacts (large/temp)
   *.pdf
   .env
   tests/corpus/pool/
   ```

7. **Update AGENTS.md:** Strip the `## Status` section (everything between `## Status` and the next `##`), keeping only operational content. This is a mechanical sed operation, not AI-generated.

8. **Commit:**
   ```bash
   git add -A && git commit -m "experiment-init: set up iteration loop for <project_name>"
   ```

9. Print next-steps summary.

**Resume behavior (`--resume`):**
- Validate that GOALS.md, experiment-log.md, iteration-count exist
- Do NOT overwrite existing files
- Allow re-running cleanup + prompt regeneration if prompts are missing

### Script 2: `outer-loop.sh`

**Location:** Worktree root
**Usage:** `./outer-loop.sh [--max N] [--dry-run]`

**Options:**
- `--max N`: Maximum outer iterations (default: 0 = unlimited)
- `--dry-run`: Show what would happen without executing
- `--model <model>`: Override model for IterationSpecAgent

**Behavior per iteration:**

**Step 1: Increment iteration counter**
```bash
ITER=$(cat iteration-count)
ITER=$((ITER + 1))
echo "$ITER" > iteration-count
ITER_PADDED=$(printf "%03d" "$ITER")
```

**Step 2: Wipe specs and previous iteration brief**
```bash
rm -f specs/*.md iteration-brief.md
```

**Step 3: Run IterationSpecAgent**

Build the prompt by concatenating `PROMPT_iteration_spec.md` with runtime context:
```bash
PROMPT="$(cat PROMPT_iteration_spec.md)

---

CURRENT ITERATION: $ITER
GOALS:
$(cat GOALS.md)

---

EXPERIMENT LOG:
$(cat experiment-log.md)

---

CHALLENGE RULES:
$(cat challenge-rules.conf)
"
```

Invoke claude:
```bash
OUTPUT=$(echo "$PROMPT" | claude -p \
    --dangerously-skip-permissions \
    --output-format text \
    --model "$SPEC_MODEL")
```

**Step 4: Validate IterationSpecAgent output**

Two paths for spec output:

**Path A — Agent wrote specs directly via tools (preferred):**
The agent has `--dangerously-skip-permissions`, so it can write files. The prompt instructs it to write specs to `specs/` and `iteration-brief.md`. Validation:
```bash
SPEC_COUNT=$(find specs -maxdepth 1 -name '*.md' -size +0c | wc -l)
if [[ "$SPEC_COUNT" -eq 0 ]]; then
    # Fallback: try parsing fenced blocks from stdout
    # (in case agent output specs as text instead of writing files)
    echo "$OUTPUT" | validate-specs-output.sh && parse_specs_from_output "$OUTPUT"
fi
```

**Path B — Agent produced fenced blocks in text output (fallback):**
Use `validate-specs-output.sh` + AWK parser from ralph-init.sh to extract specs.

Check `iteration-brief.md` exists:
```bash
[[ -s iteration-brief.md ]] || log_error "IterationSpecAgent failed to produce iteration-brief.md"
```

**Step 4b: Check for CONVERGED signal**

If the IterationSpecAgent determines all goals are met, it writes a spec containing `CONVERGED:`. Check for this *before* running the inner loop (which would be nonsensical on a convergence signal):
```bash
if grep -rq '^CONVERGED:' specs/; then
    log_step "CONVERGED — IterationSpecAgent says all goals met"
    # Archive and log the convergence, then break
    ARCHIVE_DIR="experiment-history/iteration-${ITER_PADDED}"
    mkdir -p "$ARCHIVE_DIR/specs"
    cp specs/*.md "$ARCHIVE_DIR/specs/"
    cp iteration-brief.md "$ARCHIVE_DIR/"
    BRIEF=$(head -1 iteration-brief.md)
    cat >> experiment-log.md << EOF

---

## Iteration $ITER — $(date '+%Y-%m-%d')
**Brief:** $BRIEF
**Outcome:** CONVERGED
**Evidence:** $(grep '^CONVERGED:' specs/*.md | head -1)
EOF
    git add specs/ iteration-brief.md experiment-log.md experiment-history/ iteration-count
    git commit -m "iteration $ITER: CONVERGED — $(head -1 iteration-brief.md)"
    git push origin "$(git branch --show-current)" 2>/dev/null || \
        git push -u origin "$(git branch --show-current)"
    break
fi
```

**Step 5: Run inner-loop.sh**
```bash
./inner-loop.sh
INNER_EXIT=$?
if [[ "$INNER_EXIT" -ne 0 ]]; then
    log_info "WARNING: inner loop exited with status $INNER_EXIT (max retries exhausted)"
fi
```

**Step 6: Archive iteration**
```bash
ARCHIVE_DIR="experiment-history/iteration-${ITER_PADDED}"
mkdir -p "$ARCHIVE_DIR/specs"
cp specs/*.md "$ARCHIVE_DIR/specs/"
cp iteration-brief.md "$ARCHIVE_DIR/"
# Archive all eval reports (retries + final)
for f in eval-report*.md; do
    [[ -f "$f" ]] && cp "$f" "$ARCHIVE_DIR/"
done
```

**Step 7: Append to experiment-log.md**

Extract Key Learnings from eval-report.md rather than leaving a placeholder:
```bash
BRIEF=$(head -1 iteration-brief.md)
SPEC_LIST=$(ls specs/*.md | xargs -I{} basename {})
VERDICT="TIMEOUT"
[[ -f eval-report.md ]] && VERDICT=$(grep -oP 'VERDICT:\s*\K\w+' eval-report.md | tail -1)

# Extract Key observations from eval report (the "Key observations:" line and following bullets)
KEY_LEARNINGS=""
if [[ -f eval-report.md ]]; then
    KEY_LEARNINGS=$(sed -n '/Key observations:/,/^$/p' eval-report.md | head -10)
fi
if [[ -z "$KEY_LEARNINGS" ]]; then
    KEY_LEARNINGS="- Inner loop exited with status $INNER_EXIT"
fi

# List corpus slugs without jq (python one-liner as fallback)
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
```

**Step 8: Commit and push**

Stage specific files rather than `git add -A` to avoid accidentally committing large PDFs, temp files, or `.env`:
```bash
git add specs/ experiment-history/ experiment-log.md iteration-brief.md \
    iteration-count eval-report*.md IMPLEMENTATION_PLAN.md \
    src/ tests/ AGENTS.md
git add -u  # Stage modifications to already-tracked files
git commit -m "iteration $ITER: $VERDICT — $(head -1 iteration-brief.md)"
git push origin "$(git branch --show-current)" 2>/dev/null || \
    git push -u origin "$(git branch --show-current)"
```

**Max iterations check** is at the top of the loop.

### Script 3: `inner-loop.sh`

**Location:** Worktree root
**Usage:** `./inner-loop.sh [--max-retries N] [--plan-iters N] [--build-iters N]`

**Options:**
- `--max-retries N`: Maximum eval→retry cycles (default: 2)
- `--plan-iters N`: Number of plan iterations per retry (default: 2)
- `--build-iters N`: Number of build iterations per retry (default: 8)

**Behavior per retry:**

**Step 1: Wipe implementation plan** (not source code)
```bash
rm -f IMPLEMENTATION_PLAN.md
```

**Step 2: Plan phase**
Run `claude -p` with `PROMPT_plan.md` for `plan_iters` iterations:
```bash
for i in $(seq 1 "$PLAN_ITERS"); do
    cat PROMPT_plan.md | claude -p \
        --dangerously-skip-permissions \
        --output-format stream-json \
        --model "$BUILD_MODEL" \
        --verbose
done
```

This is the same pattern as the current `loop.sh` plan mode. The agent reads specs/ and produces/updates `IMPLEMENTATION_PLAN.md`.

**Step 3: Build phase**
Run `claude -p` with `PROMPT_build.md` for `build_iters` iterations:
```bash
for i in $(seq 1 "$BUILD_ITERS"); do
    cat PROMPT_build.md | claude -p \
        --dangerously-skip-permissions \
        --output-format stream-json \
        --model "$BUILD_MODEL" \
        --verbose
    # Build agent commits after each iteration (per PROMPT_build.md instructions)
done
```

Same as current `loop.sh` build mode. Each iteration: pick task, implement, test, commit.

**Step 4: Eval phase**
Run `claude -p` with `PROMPT_eval.md` once:
```bash
EVAL_OUTPUT=$(cat PROMPT_eval.md | claude -p \
    --dangerously-skip-permissions \
    --output-format text \
    --model "$EVAL_MODEL")

# Save retry-specific copy (preserves history across retries)
echo "$EVAL_OUTPUT" > "eval-report-retry-${RETRY}.md"
# Also save as canonical eval-report.md (outer loop reads this)
echo "$EVAL_OUTPUT" > eval-report.md
```

Parse verdict:
```bash
VERDICT=$(echo "$EVAL_OUTPUT" | grep -oP 'VERDICT:\s*\K\w+' | tail -1)
if [[ -z "$VERDICT" ]]; then
    log_info "WARNING: EvalAgent produced no VERDICT line — treating as RETRY"
    VERDICT="RETRY"
fi
```

**Step 5: Act on verdict**
```bash
if [[ "$VERDICT" == "PASS" ]]; then
    log_step "PASS — inner loop complete"
    exit 0
elif [[ "$VERDICT" == "CONVERGED" ]]; then
    log_step "CONVERGED — goals fully met"
    exit 0
fi
log_info "RETRY ($RETRY/$MAX_RETRIES) — eval failed, retrying..."
```

**Exit codes:**
- `0`: PASS or CONVERGED
- `1`: Max retries exhausted (all attempts produced RETRY)

### Prompt 1: `PROMPT_iteration_spec.md`

**Purpose:** Instruct the IterationSpecAgent to evaluate the current state, produce quantitative specs, and optionally expand the test corpus.

**Key sections:**

```markdown
# Iteration Spec Agent — Experimental Convergence

You are the IterationSpecAgent. Your job is to evaluate the current state of the
project against qualitative goals and produce quantitative, testable specifications
for the next implementation cycle.

## Your Process

1. **Read GOALS.md** — understand the high-level qualitative targets
2. **Read experiment-log.md** — what was tried, what worked, what failed
3. **Read the test corpus** — `tests/corpus/papers.jsonl` and inspect current results
4. **Run tests** — `uv run pytest tests/test_corpus.py --run-corpus -v` to see current state
5. **Read eval reports** — if `eval-report.md` exists, understand what failed
6. **Evaluate against goals** — how close are we? What's the biggest gap?
7. **Apply progressive challenge rules** — see CHALLENGE RULES section below

## Output Requirements

### Specs
Write spec files to `specs/` directory. Each spec MUST:
- Have a clear, measurable acceptance criterion
- Be verifiable by the eval agent (via test output, file inspection, or metric comparison)
- Reference specific test corpus papers where relevant
- NOT repeat approaches that already failed (check experiment-log.md)

Write each spec file directly to disk (e.g., `specs/improve-table-extraction.md`).

### Iteration Brief
Write `iteration-brief.md` — a 1-paragraph summary of:
- What this iteration aims to achieve
- Why (which goal gap is being addressed)
- How success will be measured

### Convergence
If ALL goals in GOALS.md are met by the current codebase state, write a spec
containing ONLY: `CONVERGED: All goals met. [1-sentence evidence summary]`

## Rules

- **ANALYSIS AND SPEC-WRITING ONLY** — do NOT modify source code or tests
- Specs must be SPECIFIC and MEASURABLE — no vague "improve quality"
- Reference the experiment log to avoid repeating failed approaches
- Each spec should be achievable in one inner-loop cycle (plan + 8 build iterations)
- Prefer incremental improvement over ambitious rewrites

## Spec Format

Use this format for each spec file:

# [Topic Name]

## Purpose
[One sentence]

## Requirements
[Bullet points — observable outcomes]

## Acceptance Criteria
[Specific, testable conditions — numbers, thresholds, test commands]

## Constraints
[What must NOT change — no regressions, preserve existing tests]
```

The prompt is a static template. At runtime, `outer-loop.sh` appends the dynamic context (iteration number, GOALS.md content, experiment-log.md content, challenge-rules.conf content) via bash string concatenation — see the Step 3 code block in the outer-loop section above.

### Prompt 2: `PROMPT_eval.md`

**Purpose:** Instruct the EvalAgent to evaluate the current codebase against the iteration's specs and produce a machine-parseable verdict.

**Key sections:**

```markdown
# Eval Agent — Specification Verification

You are the EvalAgent. Your job is to evaluate whether the current codebase
meets the specifications for this iteration.

## Your Process

1. **Read all specs** in `specs/` — understand what was required
2. **Run the test suite** — `uv run pytest tests/ -v` (all tests)
3. **Run corpus tests** — `uv run pytest tests/test_corpus.py --run-corpus -v`
4. **For each spec**, evaluate acceptance criteria:
   - Run specific test commands mentioned in the spec
   - Inspect output files, metrics, test results
   - Compare against baseline/threshold values
5. **Produce eval report** with per-spec verdicts

## Output Format

Your entire output is the eval report. Use this structure:

# Eval Report — Iteration [N]

## Per-Spec Results

### [spec-filename.md]
**Verdict:** PASS / FAIL
**Evidence:**
- [Specific test output, file contents, or metric values]
- [Cite exactly what you observed]

### [next-spec.md]
...

## Summary
- Specs passed: N/M
- Critical failures: [list if any]
- Key observations: [what almost worked, what was far off]

## VERDICT: PASS
(or)
## VERDICT: RETRY
**Reason:** [which specs failed and why]

## Rules

- **READ-ONLY** — do NOT modify any code, tests, or configuration
- **EVIDENCE-BASED** — never mark PASS without citing specific evidence
- All tests must pass for overall PASS (no partial credit)
- If a spec is ambiguous, interpret strictly (fail if uncertain)
- The VERDICT line must be the LAST non-empty line of your output
```

**Known trade-off: eval agent has full write permissions.** The eval agent runs with `--dangerously-skip-permissions` because it needs to execute `uv run pytest` (bash tool) and read files (read tool). `claude -p` does not currently support restricting tool access to read-only — `--dangerously-skip-permissions` is all-or-nothing. The prompt's "READ-ONLY" instruction is the only enforcement. This is acceptable because: (a) the eval agent has no incentive to modify code (its job is evaluation), and (b) git history provides a safety net if it does. If a future `claude -p` flag adds tool-level restrictions, the eval agent invocation should be updated.

### Prompt 3: `PROMPT_plan.md` (Updated)

Minor updates from the current version to reference iteration context:

```markdown
You are a PLANNING agent in an iteration loop. No code edits, no commits.

## Process

1. **Study all specs** — read each file in specs/
2. **Read iteration-brief.md** — understand this iteration's focus
3. **Study existing code** — search src/ to understand what's already built
4. **Study IMPLEMENTATION_PLAN.md** if it exists — note completed vs pending tasks
5. **Gap analysis** — compare spec requirements against current codebase
   - Don't assume not implemented — always search first (Glob, Grep, Read)
6. **Produce IMPLEMENTATION_PLAN.md** — create or update with prioritized tasks

## Task Format (markdown bullets)

- **Task name** [spec-NNN]
  - What: concrete deliverable (~5 files max, one iteration)
  - Why: which spec requirement(s) it satisfies
  - Verified by: what backpressure proves it works (test, mypy, ruff)
  - Depends on: prerequisite tasks if any

## Rules

- PLANNING ONLY — no implementation, no file edits, no commits
- Prioritize: critical path first, dependencies before dependents
- Size tasks for ONE iteration (completable in a single agent run)
- IMPLEMENTATION_PLAN.md lives at repository root
```

Changes from current: Added step to read `iteration-brief.md`. Removed Ralph-specific language.

### Prompt 4: `PROMPT_build.md` (Updated)

Minimal changes from the current version:

```markdown
You are a BUILD agent in an iteration loop. Complete exactly ONE task per iteration.

## Workflow

1. **Study** specs/* for requirements and constraints
2. **Read** iteration-brief.md for this iteration's focus
3. **Read** IMPLEMENTATION_PLAN.md — pick the highest-priority incomplete task
4. **Search** the codebase before assuming anything is missing (Glob, Grep, Read)
5. **Implement** the task completely — no TODOs, no placeholders, no stubs
6. **Test** — write tests that validate behavior against spec requirements
7. **Validate**
   - `uv run pytest tests/` — all tests must pass
   - `uv run ruff check src/ tests/ && uv run ruff format src/ tests/`
8. **Update IMPLEMENTATION_PLAN.md** — mark task [DONE], add discoveries/blockers
9. **Commit** — `git add -A && git commit -m "descriptive message"`

## Guardrails (ascending criticality)

[Same as current PROMPT_build.md guardrails]

## Environment

- Python with UV — `uv run pytest`, `uv run ruff check/format`
- Source: src/
- Tests: tests/
- Read AGENTS.md for build commands, codebase layout, and gotchas
```

Changes from current: Added step to read `iteration-brief.md`. Removed `mypy` (not configured in this worktree). Added AGENTS.md reference.

### Artifact Conventions

Matches FR-7 from the spec exactly:

```
GOALS.md                      # Qualitative goals (human-written, stable)
experiment-log.md             # Running log of all outer iterations
iteration-brief.md            # Current iteration's aim (overwritten each outer loop)
iteration-count               # Plain integer, current outer iteration number
challenge-rules.conf          # Progressive challenge configuration
specs/                        # Current iteration's specs (wiped + rewritten each outer loop)
IMPLEMENTATION_PLAN.md        # Current inner loop's plan (wiped on inner retry)
eval-report.md                # Latest eval agent output (canonical)
eval-report-retry-N.md        # Per-retry eval reports (preserved across retries)
AGENTS.md                     # Operational guide (stable, manually maintained)
lib.sh                        # Shared shell utilities
experiment-init.sh            # One-time setup
outer-loop.sh                 # Outer iteration driver
inner-loop.sh                 # Inner plan→build→eval driver
PROMPT_iteration_spec.md      # IterationSpecAgent prompt template
PROMPT_eval.md                # EvalAgent prompt template
PROMPT_plan.md                # Plan agent prompt
PROMPT_build.md               # Build agent prompt
src/                          # Source code (persistent)
tests/                        # Tests (persistent, grow over time)
experiment-history/           # Archive of previous iterations
  iteration-001/
    iteration-brief.md
    specs/
    eval-report.md
  iteration-002/
    ...
```

### Progressive Challenge

**Configuration** (`challenge-rules.conf`):
```
ADD_PDF_PER_ITERATION=1
INITIAL_CORPUS=tests/corpus/papers.jsonl
PDF_POOL_DIR=tests/corpus/pool/
```

**Mechanism:**
- The `IterationSpecAgent` receives the challenge rules and the current iteration number
- The agent reads `papers.jsonl` (current corpus size) and `PDF_POOL_DIR` (available PDFs)
- If `current_corpus_size < initial_size + (iteration * ADD_PDF_PER_ITERATION)`, the agent's specs should include adding the next PDF
- The agent chooses which PDF to add based on which would provide the most diagnostic value (e.g., a paper with complex tables if table extraction is the current gap)
- The build agent executes the addition (copies PDF, creates baseline, updates papers.jsonl)

**PDF Pool:** `tests/corpus/pool/` must be pre-populated with candidate PDFs and their baseline extractions. This is a manual one-time setup step documented in experiment-init.sh output.

**Why the agent chooses (not the script):** The script could mechanically add PDFs in order, but the agent can make intelligent choices (e.g., "table extraction is weak, so add a table-heavy paper next"). The challenge rules just set the pace.

### Model Selection

| Agent | Default Model | Rationale |
|-------|--------------|-----------|
| IterationSpecAgent | opus | Makes the key judgment calls — evaluating progress, choosing specs |
| PlanAgent | sonnet | Straightforward task decomposition |
| BuildAgent | sonnet | Implementation, same as Ralph |
| EvalAgent | sonnet | Structured evaluation with clear criteria |

Configurable via environment variables:
```bash
EXPERIMENT_SPEC_MODEL=opus    # IterationSpecAgent
EXPERIMENT_BUILD_MODEL=sonnet # Plan + Build agents
EXPERIMENT_EVAL_MODEL=sonnet  # EvalAgent
```

---

## Potential Risks

### 1. IterationSpecAgent Produces Unusable Specs
**Risk:** The agent writes vague specs ("improve quality") or specs that the eval agent can't verify.
**Mitigation:** The prompt explicitly requires measurable acceptance criteria with specific numbers/thresholds. Validation step in outer-loop.sh checks that specs are non-empty and contain "Acceptance Criteria" sections. If validation fails, the outer loop can retry the spec generation once before failing.

### 2. EvalAgent Disagrees With Itself
**Risk:** Running the eval agent twice on the same state produces different verdicts.
**Mitigation:** Specs should reference concrete, deterministic tests (`uv run pytest tests/test_corpus.py --run-corpus`). The prompt instructs the agent to cite specific test output, not make subjective judgments. Temperature is 0 by default in `claude -p`.

### 3. Experiment Log Grows Beyond Context Window
**Risk:** After 10+ iterations, experiment-log.md exceeds useful context for the IterationSpecAgent.
**Mitigation:** For now, not addressed. The agent naturally focuses on recent entries. Future: the IterationSpecAgent could be instructed to summarize old entries when the log exceeds a line threshold (e.g., 200 lines). This is explicitly out of scope for v1.

### 4. Inner Loop Exhausts Retries Without Progress
**Risk:** Build agent makes changes that break tests, eval says RETRY, but the same thing happens again.
**Mitigation:** The hard cap (default 2 retries) prevents infinite loops. The experiment log captures the failure, and the next outer iteration's IterationSpecAgent sees it and can adjust the approach.

### 5. EvalAgent Modifies Code Despite Read-Only Intent
**Risk:** The eval agent has full tool permissions and could edit files, breaking the codebase.
**Mitigation:** Prompt-level enforcement ("READ-ONLY — do NOT modify any code"). The agent has no incentive to modify code. Git history provides rollback. If a future `claude -p` flag supports tool-level restrictions, update the eval invocation.

### 6. Progressive Challenge Adds PDFs Without Available Pool
**Risk:** `PDF_POOL_DIR` is empty or has fewer PDFs than iterations expected.
**Mitigation:** The IterationSpecAgent is smart enough to skip the "add PDF" rule when no pool PDFs are available. The outer loop logs a warning if the pool is exhausted.

---

## Integration Strategy

### Deployment to Worktree

These scripts are placed directly in the doc-ingest worktree root. They are NOT part of the agentic-mbse Python package — they are experiment-specific orchestration scripts.

### Relationship to Ralph

The iteration loop **replaces** the Ralph loop for experimental problems. It is not an alternative — once `experiment-init.sh` runs, the old Ralph artifacts are gone. The inner loop IS a Ralph-style plan→build cycle, just wrapped in outer iteration context.

### AGENTS.md Continuity

The existing AGENTS.md contains valuable operational knowledge (build commands, codebase layout, known gotchas). The `## Status` section at the top is stripped by `experiment-init.sh` because it contains stale progress tracking. Everything else is preserved.

### Existing Test Infrastructure

The corpus test suite (`test_corpus.py`, `metrics.py`, `compare.py`) is reused without modification. The IterationSpecAgent and EvalAgent run these tests as their primary evaluation mechanism. The progressive challenge mechanism extends the corpus by adding papers to `papers.jsonl`.

---

## Validation Approach

### Manual Verification

1. Run `experiment-init.sh` and verify:
   - GOALS.md, experiment-log.md, iteration-count, challenge-rules.conf created
   - Old ralph artifacts removed
   - AGENTS.md status section stripped, operational content preserved

2. Run `outer-loop.sh --max 1` and verify:
   - IterationSpecAgent produces specs and iteration-brief.md
   - Inner loop runs plan→build→eval
   - Eval report has VERDICT line
   - Experiment history archived
   - Experiment log updated
   - Git commit and push succeed

3. Run `outer-loop.sh --max 3` and verify:
   - Multiple iterations complete
   - Each iteration has distinct specs (not copy-pasted)
   - Experiment log grows correctly
   - Progressive challenge expands corpus (if pool available)

### Automated Checks

- `validate-specs-output.sh` validates spec format after each IterationSpecAgent run
- Inner loop validates test suite passes after each build iteration
- Outer loop validates iteration-brief.md and spec files exist before proceeding

### Success Criteria (from spec)

- [ ] experiment-init.sh creates full directory structure
- [ ] outer-loop.sh runs 3+ iterations unattended
- [ ] inner-loop.sh runs plan→build→eval and interprets PASS/RETRY correctly
- [ ] IterationSpecAgent produces parseable spec files
- [ ] EvalAgent produces machine-parseable verdict with evidence
- [ ] Experiment history archives correctly
- [ ] Progressive challenge works across iterations
- [ ] Max iteration/retry safety valves work

---

## Implementation Notes

### File Count
- **New files (7):** `experiment-init.sh`, `outer-loop.sh`, `inner-loop.sh`, `lib.sh`, `PROMPT_iteration_spec.md`, `PROMPT_eval.md`, `GOALS.md` (user-written)
- **Updated files (2):** `PROMPT_plan.md`, `PROMPT_build.md` (minor iteration-context additions)
- **Modified files (1):** `AGENTS.md` (status section stripped)
- **Deleted files (5+):** `DESIGN.md`, `loop.sh`, `ralph-init.log`, `specs/*.md` (old), `IMPLEMENTATION_PLAN.md` (wiped on first run)

### Implementation Order
1. `lib.sh` (shared utilities — foundation for everything else)
2. `PROMPT_iteration_spec.md` and `PROMPT_eval.md` (prompt templates)
3. `PROMPT_plan.md` and `PROMPT_build.md` (minor updates)
4. `experiment-init.sh` (workspace setup + cleanup)
5. `inner-loop.sh` (plan→build→eval cycle)
6. `outer-loop.sh` (outer iteration driver)
7. Manual: write GOALS.md for the doc-ingest problem
8. Test: run end-to-end

---

Next Step: After approval → `/_my_implement` (scripts are self-contained and can be implemented directly from this design)
