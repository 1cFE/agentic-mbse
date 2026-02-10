# Implementation Plan: Iteration Loop

**Status:** Complete
**Created:** 2026-02-10
**Last Updated:** 2026-02-10

## Source Documents
- **Spec:** `.project/active/iteration-loop/spec.md`
- **Design:** `.project/active/iteration-loop/design.md` — See here for component details, architecture, prompt contents, artifact conventions
- **Design Review:** Design review identified 2 critical + 4 major issues, all incorporated below

## Implementation Strategy

**Phasing Rationale:**
Bottom-up build order — shared library first, then prompts (highest-judgment work), then scripts in dependency order (init → inner → outer). Prompts are front-loaded because getting agent instructions right is the riskiest part and allows iteration before wiring into scripts. Design review fixes are distributed across their natural phases rather than treated as a separate pass.

**Overall Validation Approach:**
- Each phase has a manual smoke test (run the script, inspect output)
- No pytest tests for shell scripts — validation is behavioral (run + verify artifacts)
- End-to-end validation in Phase 5 with `--max 1` then `--max 3`

---

## Phase 1: Shared Library (`lib.sh`)

### Goal
Build the foundation all three scripts source — logging, agent invocation with validation/fixup, spec parsing. This is the riskiest code (agent output validation) and everything depends on it.

### Test Stencil (Manual Verification)
```bash
# Source lib.sh and verify functions exist
source lib.sh
type validate_generation  # should print "validate_generation is a function"
type fixup_generate
type claude_generate
type parse_specs_from_output
type log_step

# Test validate_generation with known-bad output
echo "Sure! Here's what I think about that..." | validate_generation /dev/stdin 5
echo $?  # should be non-zero (conversational preamble detected)

# Test validate_generation with known-good output
printf '%s\n' "# Spec Title" "" "## Purpose" "Extract tables" "" "## Requirements" | validate_generation /dev/stdin 3
echo $?  # should be 0
```

### Changes Required

**See `design.md#shared-library-libsh` for:** function list, model defaults, external dependency paths

#### 1. `lib.sh` (NEW)
- [x] Create file at worktree root
- [x] Implement logging functions: `log_step()`, `log_info()`, `log_error()`, `log_timestamp()`
- [x] Implement `validate_generation()` — port from ralph-init.sh:91 (line count check, conversational preamble patterns, meta-commentary, tool-use artifacts)
- [x] Implement `fixup_generate()` — port from ralph-init.sh:135 (re-prompt with explicit failure description)
- [x] Implement `claude_generate()` — combines validate + fixup into single call (ralph-init.sh:162 pattern)
- [x] Implement `parse_specs_from_output()` — AWK parser from ralph-init.sh:826 (extract fenced `\`\`\`markdown specs/filename.md` blocks)
- [x] Implement `validate_specs()` — wrapper around `$HOME/.claude/scripts/validate-specs-output.sh`
- [x] Add model defaults: `SPEC_MODEL`, `BUILD_MODEL`, `EVAL_MODEL` from env vars
- [x] Add `SCRIPT_DIR` and `VALIDATE_SPECS` path constants
- [x] Add startup check: verify `validate-specs-output.sh` exists (design review fix #8 — fail early, not mid-execution)
- [x] Add `require_command()` helper to check for `claude` at source time (design review fix #9)

### Validation

**Manual:**
- [x] `source lib.sh` succeeds without errors
- [x] All function names resolve (`type <func>`)
- [x] `validate_generation` rejects conversational output (test with crafted input)
- [x] `validate_generation` accepts well-formed spec output
- [x] `parse_specs_from_output` extracts fenced blocks into `specs/` directory (test with crafted input containing 2 fenced blocks)
- [x] Model defaults read from env vars when set, fall back to defaults when unset
- [x] Missing `validate-specs-output.sh` produces clear error at source time

**What We Know Works After This Phase:**
Agent output validation and spec parsing — the core reliability mechanisms that prevent garbage propagation through the loop.

---

## Phase 2: Prompt Templates

### Goal
Write all 4 prompt templates. This is the highest-judgment work — the prompts define agent behavior and are the primary lever for loop quality. Front-loading lets us review and iterate before wiring into scripts.

Incorporates design review fixes:
- **Critical #2:** IterationSpecAgent prompt includes instruction to summarize previous iteration's learnings in experiment-log.md
- **Major #3:** No `{{PLACEHOLDER}}` syntax — prompts are self-contained documents; runtime context is appended by outer-loop.sh via string concatenation

### Changes Required

**See `design.md#prompt-1-prompt_iteration_specmd` through `#prompt-4-prompt_buildmd` for:** full prompt contents, section structure, rules

#### 1. `PROMPT_iteration_spec.md` (NEW)
- [x] Write prompt with sections: role, process (7 steps from design), output requirements (specs + iteration brief + convergence), rules, spec format
- [x] Include instruction to backfill previous iteration's Key Learnings in experiment-log.md from eval-report.md (design review critical #2)
- [x] Include convergence detection instructions: if all goals met, write `CONVERGED:` spec
- [x] Omit `{{PLACEHOLDER}}` references — runtime context (iteration number, GOALS, experiment-log, challenge rules) will be appended by outer-loop.sh
- [x] Include progressive challenge instructions (reference challenge-rules.conf format)
- [x] Enforce: analysis and spec-writing only, no code changes, specific + measurable criteria

#### 2. `PROMPT_eval.md` (NEW)
- [x] Write prompt with sections: role, process (5 steps), output format (per-spec verdicts + summary + VERDICT line), rules
- [x] Enforce: read-only, evidence-based, strict interpretation
- [x] Specify VERDICT must be last non-empty line
- [x] Include instruction to extract "Key observations" into a summary section (feeds into experiment-log Key Learnings)

#### 3. `PROMPT_plan.md` (UPDATE existing)
- [x] Add step to read `iteration-brief.md` for iteration context
- [x] Remove Ralph-specific language
- [x] Keep existing structure (read specs → study code → gap analysis → produce IMPLEMENTATION_PLAN.md)
- [x] Add AGENTS.md reference

#### 4. `PROMPT_build.md` (UPDATE existing)
- [x] Add step to read `iteration-brief.md`
- [x] Remove `mypy` reference (not configured in this worktree)
- [x] Add AGENTS.md reference
- [x] Keep existing guardrails and commit instructions

### Validation

**Manual:**
- [x] Each prompt is self-contained and readable without design.md context
- [x] IterationSpecAgent prompt: includes Key Learnings backfill instruction, convergence detection, progressive challenge rules, no `{{PLACEHOLDER}}` syntax
- [x] Eval prompt: VERDICT format specified, read-only enforced, evidence-based requirement clear
- [x] Plan prompt: references `iteration-brief.md`, `specs/`, `AGENTS.md`
- [x] Build prompt: references `iteration-brief.md`, `specs/`, `AGENTS.md`, no `mypy`

**What We Know Works After This Phase:**
All agent instructions are defined and reviewed. No code runs yet, but the prompts are the primary quality lever.

---

## Phase 3: `experiment-init.sh` (Setup + Cleanup)

### Goal
One-time workspace initialization — clean old Ralph artifacts (FR-9), create directory structure (FR-7), deploy prompt templates, write challenge rules (FR-8), draft GOALS.md for doc-ingest.

### Test Stencil (Manual Verification)
```bash
# Run init on the doc-ingest worktree
./experiment-init.sh doc-ingest GOALS.md

# Verify cleanup (FR-9)
[[ ! -f DESIGN.md ]] && echo "PASS: DESIGN.md removed"
[[ ! -f loop.sh ]] && echo "PASS: loop.sh removed"
[[ ! -f ralph-init.log ]] && echo "PASS: ralph-init.log removed"
[[ -d src/ ]] && echo "PASS: src/ preserved"
[[ -d tests/ ]] && echo "PASS: tests/ preserved"

# Verify creation
[[ -f GOALS.md ]] && echo "PASS: GOALS.md exists"
[[ -f experiment-log.md ]] && echo "PASS: experiment-log.md exists"
[[ -f iteration-count ]] && echo "PASS: iteration-count exists"
[[ "$(cat iteration-count)" == "0" ]] && echo "PASS: iteration-count is 0"
[[ -d experiment-history/ ]] && echo "PASS: experiment-history/ exists"
[[ -f challenge-rules.conf ]] && echo "PASS: challenge-rules.conf exists"

# Verify AGENTS.md status section stripped
grep -c "## Status" AGENTS.md  # should be 0
```

### Changes Required

**See `design.md#script-1-experiment-initsh` for:** full behavior, options, resume behavior, cleanup list

#### 1. `experiment-init.sh` (NEW)
- [x] Source `lib.sh`
- [x] Parse arguments: `<project_name>`, `<goals_file>`, `--challenge-rules`, `--resume`, `--model`, `--help`
- [x] Validate: goals file exists, current directory is git repo
- [x] Clean old Ralph artifacts (FR-9): `DESIGN.md`, `DESIGN_v1.md`, `DESIGN_REVIEW.md`, `ralph-init.log`, `loop.sh`, `specs/*.md`
- [x] Preserve: `src/`, `tests/`, `AGENTS.md`, `IMPLEMENTATION_PLAN.md`, `pyproject.toml`, `uv.lock`, `.gitignore`
- [x] Copy goals file → `GOALS.md`
- [x] Create `experiment-log.md` with header + goals copy (see `design.md#artifact-conventions` for format)
- [x] Create `iteration-count` containing `0`
- [x] Create `experiment-history/` directory
- [x] Write `challenge-rules.conf` (from `--challenge-rules` file or default for doc-ingest)
- [x] Strip `## Status` section from `AGENTS.md` (defensive — check section exists before stripping)
- [x] Implement `--resume`: validate existing workspace, don't overwrite, allow prompt regeneration
- [x] Commit: `git add -A && git commit -m "experiment-init: ..."`
- [x] Print next-steps summary

#### 2. `GOALS.md` (NEW — manual draft)
- [x] Write qualitative goals for the doc-ingest problem (table extraction, heading detection, multi-format support, etc.)
- [x] Keep high-level and qualitative — the IterationSpecAgent makes them quantitative

### Validation

**Manual:**
- [x] Run `./experiment-init.sh doc-ingest GOALS.md` — completes without error
- [x] Old artifacts removed, source preserved (test stencil checks above)
- [x] `experiment-log.md` contains goals copy and correct header format
- [x] `AGENTS.md` has operational content but no `## Status` section
- [x] `challenge-rules.conf` contains `ADD_PDF_PER_ITERATION`, `INITIAL_CORPUS`, `PDF_POOL_DIR`
- [x] Git commit created with correct message
- [x] Run `./experiment-init.sh --resume doc-ingest GOALS.md` — does not overwrite existing files

**What We Know Works After This Phase:**
Workspace is correctly initialized. Old artifacts cleaned. All configuration files in place. Ready for the loops.

---

## Phase 4: `inner-loop.sh` (Plan→Build→Eval)

### Goal
Implement the core plan→build→eval cycle with retry logic (FR-3). This is the workhorse — it runs the agents that actually implement and evaluate changes.

Incorporates design review fix:
- **Major #5:** Save `eval-report-retry-N.md` per retry so previous attempts aren't lost

### Test Stencil (Manual Verification)
```bash
# Requires: lib.sh, prompt templates, specs/ with at least one spec, AGENTS.md

# Test argument parsing
./inner-loop.sh --max-retries 1 --plan-iters 1 --build-iters 1
# Should run 1 plan, 1 build, 1 eval, then exit (PASS or RETRY)

# Test max retries safety valve
./inner-loop.sh --max-retries 0
# Should exit immediately with error (0 retries = no work)

# Verify eval report saved
[[ -f eval-report.md ]] && echo "PASS: eval-report.md created"
grep "VERDICT:" eval-report.md && echo "PASS: verdict found"
```

### Changes Required

**See `design.md#script-3-inner-loopsh` for:** full behavior, steps, exit codes, verdict parsing

#### 1. `inner-loop.sh` (NEW)
- [x] Source `lib.sh`
- [x] Parse arguments: `--max-retries N`, `--plan-iters N`, `--build-iters N`
- [x] Implement retry loop (default max 2 retries)
- [x] Step 1: Wipe `IMPLEMENTATION_PLAN.md` (not source code — FR-3 constraint)
- [x] Step 2: Plan phase — run `claude -p` with `PROMPT_plan.md` for N iterations, `--output-format stream-json`
- [x] Step 3: Build phase — run `claude -p` with `PROMPT_build.md` for M iterations, `--output-format stream-json`
- [x] Step 4: Eval phase — run `claude -p` with `PROMPT_eval.md` once, `--output-format text`, save to `eval-report.md`
- [x] Save per-retry eval reports: copy `eval-report.md` → `eval-report-retry-${RETRY}.md` before next retry (design review fix #5)
- [x] Parse `VERDICT: PASS|RETRY|CONVERGED` from eval output (last match)
- [x] Handle missing VERDICT: treat as RETRY with logged warning
- [x] Exit 0 on PASS or CONVERGED, exit 1 on max retries exhausted

### Validation

**Manual (with minimal iterations to save time/cost):**
- [x] `./inner-loop.sh --max-retries 1 --plan-iters 1 --build-iters 1` — runs all three phases
- [x] Plan agent produces/updates `IMPLEMENTATION_PLAN.md`
- [x] Build agent commits changes
- [x] Eval agent produces `eval-report.md` with VERDICT line
- [x] On RETRY: `eval-report-retry-1.md` preserved, plan wiped, second attempt starts
- [x] On max retries exhausted: exits with code 1
- [x] On PASS: exits with code 0

**What We Know Works After This Phase:**
The core agent cycle — plan, build, eval, retry — runs correctly with proper verdict handling and retry bookkeeping.

---

## Phase 5: `outer-loop.sh` + End-to-End

### Goal
Implement the outer iteration driver (FR-2) with archiving, experiment logging, progressive challenge, and git push. Then validate the full system end-to-end.

Incorporates design review fixes:
- **Critical #1:** CONVERGED short-circuit between spec validation (Step 4) and inner loop (Step 5) — don't run inner loop on a CONVERGED spec
- **Critical #2:** Extract Key Learnings summary from eval-report.md into experiment-log entry (instead of placeholder text)
- **Major #6:** Use `INNER_EXIT` for logging and VERDICT fallback

### Changes Required

**See `design.md#script-2-outer-loopsh` for:** full behavior, steps 1-9, archive format, log entry format

#### 1. `outer-loop.sh` (NEW)
- [x] Source `lib.sh`
- [x] Parse arguments: `--max N`, `--dry-run`, `--model`
- [x] Implement outer loop with max iteration check at top
- [x] Step 1: Increment `iteration-count`, compute zero-padded `ITER_PADDED`
- [x] Step 2: Wipe `specs/*.md` and `iteration-brief.md`
- [x] Step 3: Build IterationSpecAgent prompt via string concatenation (append iteration number, GOALS.md, experiment-log.md, challenge-rules.conf to `PROMPT_iteration_spec.md`)
- [x] Run `claude_generate()` with spec model
- [x] Step 4: Validate spec output — Path A (agent wrote files directly) with Path B fallback (fenced block parsing)
- [x] Validate `iteration-brief.md` exists
- [x] **Step 4.5 (design review fix #1):** Check spec files for `^CONVERGED:` marker. If found: write convergence entry to experiment-log, archive, commit, push, exit 0. Skip inner loop entirely.
- [x] Step 5: Run `./inner-loop.sh`, capture exit code
- [x] Step 6: Archive to `experiment-history/iteration-${ITER_PADDED}/` (specs, brief, eval-report, retry eval-reports)
- [x] Step 7: Append to experiment-log.md — extract Key Learnings from eval-report.md "Key observations" section instead of placeholder (design review fix #2). Use `INNER_EXIT` to set VERDICT=TIMEOUT if inner loop failed and no eval-report exists (design review fix #6).
- [x] Step 8: `git add -A && git commit && git push` (note: design review minor #7 suggests targeted staging — assess whether `.gitignore` is sufficient)
- [x] Step 9: Check VERDICT for CONVERGED → break
- [x] Implement `--dry-run`: print what each step would do without executing agents

### Validation

**End-to-End Test 1: Single iteration**
- [x] Run `./outer-loop.sh --max 1`
- [x] IterationSpecAgent produces specs and iteration-brief.md
- [x] Inner loop runs plan→build→eval
- [x] `experiment-history/iteration-001/` contains archived specs, brief, eval-report
- [x] `experiment-log.md` has Iteration 1 entry with populated Key Learnings (not placeholder)
- [x] Git commit and push succeed

**End-to-End Test 2: Multiple iterations**
- [x] Run `./outer-loop.sh --max 3`
- [x] Each iteration has distinct specs (not copy-pasted from previous)
- [x] Experiment log grows with per-iteration entries
- [x] Archives accumulate correctly (`iteration-001/`, `iteration-002/`, `iteration-003/`)
- [x] Progressive challenge: corpus size increases if pool PDFs available

**End-to-End Test 3: Convergence**
- [x] (May not trigger naturally — verify CONVERGED check logic by code inspection)
- [x] If IterationSpecAgent writes CONVERGED spec: inner loop is NOT invoked, log entry written, clean exit

**What We Know Works After This Phase:**
The complete system — init, iterate, evaluate, archive, log, push — runs unattended for multiple iterations with correct convergence detection and experiment memory.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

**Prerequisites:**
- `claude` CLI installed and authenticated
- `jq` installed (for corpus listing in experiment-log entries)
- `$HOME/.claude/scripts/validate-specs-output.sh` exists (from Ralph setup)
- `tests/corpus/pool/` pre-populated with candidate PDFs (for progressive challenge)
- Branch `ralph/doc-ingest` checked out

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1:** `validate_generation()` is the most critical function — port carefully from ralph-init.sh, test with crafted good/bad inputs before moving on
- **Phase 2:** Prompts are the primary quality lever — review each prompt for ambiguity and missing constraints before moving to scripts
- **Phase 3:** Cleanup is destructive — verify old artifacts list against actual worktree contents before running `rm`
- **Phase 4:** Inner loop can be expensive (agent API calls) — test with `--plan-iters 1 --build-iters 1` first
- **Phase 5:** Outer loop compounds costs — always test with `--max 1` before `--max 3`

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `lib.sh` (186 lines) with all shared utilities
- Ported from ralph-init.sh: `validate_generation()`, `fixup_generate()`, `claude_generate()`, `parse_specs_from_output()`
- Added `validate_specs()` wrapper around `validate-specs-output.sh`
- Added `require_command()` helper for dependency checks
- Dependency checks run at source time: claude CLI, validate-specs-output.sh
- Model defaults: SPEC_MODEL (opus), BUILD_MODEL (sonnet), EVAL_MODEL (sonnet)

**Issues:** None
**Deviations:**
- `claude_generate()` accepts model as 4th argument (not hardcoded) — matches design intent but different from ralph-init.sh which used separate `claude_generate_design()`

### Phase 2 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `PROMPT_iteration_spec.md` (66 lines) — includes Key Learnings backfill instruction, convergence detection, progressive challenge, no `{{PLACEHOLDER}}` syntax
- Created `PROMPT_eval.md` (52 lines) — VERDICT format specified, read-only enforced, evidence-based, Key observations extraction
- Updated `PROMPT_plan.md` (32 lines) — added iteration-brief.md step, AGENTS.md reference, removed Ralph-specific language
- Updated `PROMPT_build.md` (52 lines) — added iteration-brief.md step, AGENTS.md reference, removed mypy

**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `experiment-init.sh` (229 lines) with full argument parsing, cleanup, workspace creation, .gitignore update, AGENTS.md status stripping, commit
- Created `GOALS.md` (29 lines) — qualitative goals for doc-ingest covering table extraction, heading detection, multi-format, character fidelity, regression safety
- Resume mode validates workspace and exits early

**Issues:** None
**Deviations:**
- Resume mode exits after validation rather than falling through to prompt deployment — simpler and safer; prompts are already on disk from initial run

### Phase 4 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `inner-loop.sh` (132 lines) with plan→build→eval cycle, retry logic, per-retry eval report preservation, verdict parsing

**Issues:** None
**Deviations:** None

### Phase 5 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `outer-loop.sh` (238 lines) with full outer iteration loop: IterationSpecAgent invocation, spec validation (Path A + B fallback), CONVERGED short-circuit, inner loop invocation, archiving, experiment-log extraction, targeted git staging, commit/push
- All design review fixes incorporated: #1 (CONVERGED before inner loop), #2 (Key Learnings extraction), #5 (per-retry eval reports), #6 (INNER_EXIT fallback), #7 (targeted staging), #9 (python3 not jq)

**Issues:** None
**Deviations:** None

---

**Status**: Complete
