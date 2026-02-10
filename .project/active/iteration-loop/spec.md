# Spec: Iteration Loop — Experimental Orchestration for Claude Code

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-10 09:32 PST
**Complexity:** HIGH
**Branch:** ralph/doc-ingest
**Commit:** cc99347

---

## Business Goals

### Why This Matters

The Ralph Wiggum loop works well for problems with a known target shape — you write a design, decompose into specs, and iterate plan/build until complete. But a large class of valuable engineering problems are **exploratory**: you don't know what "good" looks like until you've tried several approaches and measured. PDF extraction quality, performance optimization, and ML pipeline tuning all share this property.

Right now, when facing an exploratory problem, the workflow degenerates into ad-hoc manual sessions — no memory between iterations, no structured evaluation, no progressive challenge. The Iteration Loop provides a disciplined orchestration for these problems: high-level qualitative goals → iterative experiment cycles → convergence on a solution.

### Success Criteria

- [ ] A complete set of scripts that can be run against the doc-ingest worktree to iteratively improve PDF extraction quality
- [ ] Outer loop correctly invokes the IterationSpecAgent, which produces quantitative specs from qualitative goals
- [ ] Inner loop runs plan→build→eval cycles with fresh context per iteration
- [ ] Experiment log accumulates learnings across outer iterations without unbounded growth
- [ ] The system can run unattended for multiple outer iterations (not requiring human intervention between iterations, though human can interrupt/adjust)
- [ ] Progressive challenge mechanism works (e.g., adding 1 PDF per outer iteration)

### Priority

Immediate — this is the vehicle for the next phase of doc-ingest work.

---

## Problem Statement

### Current State

Ralph Wiggum loop assumes you can write a complete design upfront. For experimental problems:
- No structured way to capture "what we learned" between experiment cycles
- No agent that evaluates functional outcomes against goals and adjusts specs
- No progressive challenge mechanism to prevent overfitting to a small test set
- No eval step to decide whether an inner loop achieved its specs or needs retry

### Desired Outcome

A reusable (within this repo, for now) set of deterministic shell scripts and prompt templates that orchestrate an experimental convergence loop. The human provides qualitative goals; the system iteratively makes them quantitative, implements experiments, evaluates results, and adapts.

---

## Scope

### In Scope

- Shell scripts: `experiment-init.sh`, `outer-loop.sh`, `inner-loop.sh`
- Prompt templates: `PROMPT_iteration_spec.md`, `PROMPT_eval.md`, `PROMPT_plan.md`, `PROMPT_build.md`
- Artifact conventions: directory structure, experiment-log format, iteration directory layout
- Integration with the existing doc-ingest worktree as the first target problem
- Cleanup of old ralph artifacts (DESIGN*.md, DESIGN_REVIEW.md, PROMPT_*.md, specs/, AGENTS.md, loop.sh, ralph-init.log) from the worktree

### Out of Scope

- The PDF extraction problem itself (that's the workload, not the orchestration)
- Generic framework / multi-repo support (if it works, future extraction to `agentic-project-init`)
- GUI, web dashboard, or visualization
- Multi-machine / distributed execution
- Worktree management (operates in-place on a branch)

### Edge Cases & Considerations

- **Context window pressure**: The IterationSpecAgent needs enough context to evaluate the codebase but can't read everything. It needs a focused evaluation strategy.
- **Experiment log growth**: After many outer iterations, the log could exceed useful context size. Need a compaction strategy.
- **Flaky eval**: The EvalAgent might disagree with itself across runs. Specs need to be testable enough that eval is deterministic-ish.
- **Stuck inner loops**: Need a max-iteration safety valve on both inner and outer loops.

---

## Requirements

### FR-1: Experiment Initialization (`experiment-init.sh`)

The script MUST:
- Accept a project name and a goals file (freeform markdown) as arguments
- Accept an optional `--resume` flag to continue from a previous run
- Create the experiment directory structure (see FR-7)
- Copy the goals file into the experiment workspace as `GOALS.md`
- Initialize `experiment-log.md` with a header and the original goals
- Initialize `iteration-count` at 0
- NOT create worktrees (operates in-place)
- NOT generate design documents (no upfront design — that's the whole point)

### FR-2: Outer Loop (`outer-loop.sh`)

The script MUST:
- Accept `max_iterations` as an argument (default: unlimited, `0`)
- Read the current `iteration-count` and increment it
- Invoke the IterationSpecAgent (claude headless) with `PROMPT_iteration_spec.md`
- Validate that the agent produced spec files (non-empty, in expected location)
- Invoke `inner-loop.sh` for the current iteration
- After inner loop completes, append a summary entry to `experiment-log.md`
- Loop until max_iterations reached or a "CONVERGED" signal is found
- Push to remote after each outer iteration

The script SHOULD:
- Log timestamps for each phase
- Support `--dry-run` to show what would happen without executing

### FR-3: Inner Loop (`inner-loop.sh`)

The script MUST:
- Wipe artifacts from the previous inner loop (implementation plan, not source code)
- Run `plan` mode (claude headless with `PROMPT_plan.md`) for N iterations (default: 2)
- Run `build` mode (claude headless with `PROMPT_build.md`) for M iterations (default: 8)
- Run `eval` mode (claude headless with `PROMPT_eval.md`) once after build completes
- Parse the eval output for a verdict: `PASS` (specs met) or `RETRY` (not met)
- On `RETRY`: clear the implementation plan and re-run inner loop (up to max retries, default: 2)
- On `PASS`: exit with success
- Commit after each build iteration (the build agent does this, same as Ralph)

The script MUST NOT:
- Delete source code or test files between retries (only wipe the plan)
- Run indefinitely (hard cap on total inner iterations)

### FR-4: IterationSpecAgent (`PROMPT_iteration_spec.md`)

The prompt MUST instruct the agent to:

1. **Read `GOALS.md`** — the qualitative high-level goals
2. **Read `experiment-log.md`** — what was tried, what worked, what didn't
3. **Read the current test corpus** — understand what PDFs/documents are being tested
4. **Evaluate the codebase functionally** — run tests, inspect outputs, measure against goals
5. **Produce quantitative specs** from qualitative goals — turn "tables should extract well" into specific, testable acceptance criteria for this iteration
6. **Apply progressive challenge rules** — e.g., add 1 new PDF to the test corpus per outer iteration
7. **Write specs** to `specs/` directory using the standard Ralph format (```markdown specs/filename.md fenced blocks)
8. **Write an iteration brief** — a 1-paragraph summary of what this iteration aims to achieve and why, saved to `iteration-brief.md`

The prompt MUST include:
- The progressive challenge rules (parameterized — the init script writes them into the prompt)
- Instructions to be SPECIFIC and MEASURABLE in specs (no vague "improve quality")
- Instructions to reference the experiment log to avoid repeating failed approaches
- A format specification for the iteration brief

The prompt MUST NOT:
- Allow the agent to write code or make file changes (analysis and spec-writing only)
- Allow specs that can't be verified by the eval agent

### FR-5: EvalAgent (`PROMPT_eval.md`)

The prompt MUST instruct the agent to:

1. **Read the current iteration's specs** from `specs/`
2. **Run tests** (`uv run pytest`) and inspect results
3. **Evaluate each spec's acceptance criteria** against the actual codebase state
4. **Produce an eval report** with per-spec verdicts (PASS / FAIL with evidence)
5. **Produce a final verdict**: `PASS` (all critical specs met) or `RETRY` (with specific failures listed)

The prompt MUST include:
- A machine-parseable verdict format (e.g., last line: `VERDICT: PASS` or `VERDICT: RETRY`)
- Instructions to be EVIDENCE-BASED (cite test output, file contents, specific measurements)

The prompt MUST NOT:
- Allow the agent to modify code (read-only evaluation)
- Mark specs as PASS without verifiable evidence

### FR-6: Plan and Build Prompts (`PROMPT_plan.md`, `PROMPT_build.md`)

These are adapted from Ralph's prompts with minimal changes:

- `PROMPT_plan.md` MUST reference `specs/` for the current iteration's specs (same as Ralph)
- `PROMPT_build.md` MUST reference `specs/` and include the standard Ralph guardrails
- Both MUST reference `AGENTS.md` for operational guidance (build commands, conventions)
- The `AGENTS.md` file MUST exist and contain operational guidance (not auto-generated — carried forward from the existing worktree or hand-written)

### FR-7: Artifact Conventions

Directory structure within the experiment workspace (the worktree root):

```
GOALS.md                      # High-level qualitative goals (human-written, stable)
experiment-log.md             # Running memory of all outer iterations
iteration-brief.md            # Current iteration's aim (overwritten each outer loop)
iteration-count               # Plain integer file, current outer iteration number
specs/                        # Current iteration's specs (wiped + rewritten each outer loop)
IMPLEMENTATION_PLAN.md        # Current inner loop's plan (wiped on inner retry)
AGENTS.md                     # Operational guide (stable, not auto-generated)
src/                          # Source code (persistent across all iterations)
tests/                        # Tests (persistent, grow over time)
experiment-history/           # Archive of previous iterations
  iteration-001/
    iteration-brief.md        # Copy of that iteration's brief
    specs/                    # Copy of that iteration's specs
    eval-report.md            # Copy of that iteration's eval output
  iteration-002/
    ...
```

The experiment-log.md format MUST be:

```markdown
# Experiment Log

## Goals
[Copy of original GOALS.md content]

---

## Iteration 1 — [date]
**Brief:** [1-line from iteration-brief.md]
**Specs:** [list of spec filenames]
**Outcome:** [PASS/RETRY/TIMEOUT]
**Key Learnings:**
- [Tight bullet points — what worked, what didn't, what surprised us]
**Corpus:** [list of test PDFs for this iteration]

---

## Iteration 2 — [date]
...
```

### FR-8: Progressive Challenge Configuration

The `experiment-init.sh` script MUST accept a `--challenge-rules` file (or inline flag) that specifies iteration-over-iteration escalation rules. For the doc-ingest case:

```
ADD_PDF_PER_ITERATION=1
INITIAL_CORPUS=tests/corpus/papers.jsonl
```

These rules MUST be:
- Written into `challenge-rules.conf` in the workspace
- Injected into the IterationSpecAgent prompt so it knows how to escalate
- Readable by the outer loop script for any mechanical escalation (e.g., actually adding the PDF)

### FR-9: Cleanup of Old Ralph Artifacts

Before the first experiment run, the following MUST be removed from the doc-ingest worktree:
- `DESIGN.md`, `DESIGN_v1.md`, `DESIGN_REVIEW.md`
- `PROMPT_plan.md`, `PROMPT_build.md` (will be replaced by new versions)
- `specs/` directory contents (will be replaced by IterationSpecAgent output)
- `loop.sh` (replaced by outer-loop.sh + inner-loop.sh)
- `ralph-init.log`

The following MUST be preserved:
- `src/` — all implemented code
- `tests/` — all tests
- `AGENTS.md` — operational guide (may need manual update)
- `IMPLEMENTATION_PLAN.md` — can be wiped on first inner loop, but don't delete preemptively
- `pyproject.toml`, `uv.lock`, `.gitignore` — project config
- `CONCEPT.md` — original concept if it exists

---

## Acceptance Criteria

### Core Functionality

- [ ] `experiment-init.sh` creates the full directory structure from a goals file
- [ ] `outer-loop.sh` runs at least 3 iterations unattended, producing experiment-log entries
- [ ] `inner-loop.sh` runs plan→build→eval cycle and correctly interprets PASS/RETRY
- [ ] IterationSpecAgent produces parseable spec files from qualitative goals
- [ ] EvalAgent produces a machine-parseable verdict with evidence
- [ ] Experiment history archives previous iterations correctly
- [ ] Progressive challenge (add 1 PDF) works across outer iterations

### Robustness

- [ ] Inner loop respects max retries and doesn't loop forever
- [ ] Outer loop respects max iterations
- [ ] Empty or malformed agent output is detected and handled (with logged error, not silent failure)
- [ ] `--resume` on experiment-init.sh works (doesn't clobber existing experiment state)

### Integration with doc-ingest

- [ ] Old ralph artifacts are cleaned up
- [ ] New scripts work against the existing doc-ingest codebase
- [ ] AGENTS.md is preserved and usable by plan/build agents

---

## Related Artifacts

- **Ralph loop reference:** `~/.claude/scripts/ralph-init.sh`
- **Spec validation:** `~/.claude/scripts/validate-specs-output.sh` (reusable for spec parsing)
- **Concept:** `.project/concepts/resilient-document-ingestion.md`
- **Research:** `.project/research/html-trace.md`
- **Doc-ingest worktree:** `/home/reid/1cfe/agentic-mbse_doc-ingest/`

---

## Implementation Notes

These are observations, not requirements — defer decisions to design phase.

- The outer-loop and inner-loop scripts should use `claude -p --model sonnet --output-format text` for headless execution, same as Ralph
- The IterationSpecAgent might benefit from a stronger model (opus) since it makes the key judgment calls — consider `--design-model` flag like Ralph has
- The `validate-specs-output.sh` script from Ralph can be reused verbatim for parsing IterationSpecAgent output
- The `validate_generation()` and `fixup_generate()` patterns from ralph-init.sh are worth carrying forward for all agent invocations
- The experiment-log compaction problem can likely be solved by having the IterationSpecAgent summarize old entries when the log exceeds a threshold

---

**Next Steps:** After approval, proceed to `/_my_design` (or go straight to implementation given the scripts are self-contained and the ralph-init.sh serves as a strong reference)
