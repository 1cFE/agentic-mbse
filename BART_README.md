# BART — Build-Agent Retry Topology

BART is a shell-based iteration loop that drives autonomous code improvement using Claude as the execution engine. It runs four specialized agents in a structured cycle: **Spec** (what to improve), **Plan** (how to implement it), **Build** (do the work), and **Eval** (verify it worked). The loop repeats until goals converge or a budget is exhausted.

BART was designed for problems where quality is measurable but ground truth doesn't exist — you know what "better" looks like, but can't write a deterministic solution. The canonical use case is PDF-to-markdown extraction, where the pipeline must be iteratively improved against a growing test corpus.

## Architecture

```
run.sh
 └─ experiment-init.sh          (one-time workspace setup)
 └─ outer-loop.sh               (iteration driver)
      │
      │  for each iteration:
      │
      ├─ IterationSpecAgent      (reads GOALS.md + experiment-log.md → writes specs/)
      │
      └─ inner-loop.sh           (plan → build → eval, with retry)
           │
           │  for each retry:
           │
           ├─ PlanAgent           (reads specs/ → writes IMPLEMENTATION_PLAN.md)
           ├─ BuildAgent ×N       (picks tasks, implements, tests, commits)
           └─ EvalAgent           (verifies specs → PASS / RETRY / CONVERGED)
```

### Outer loop

Each outer iteration:

1. **IterationSpecAgent** reads the qualitative goals (`GOALS.md`) and the experiment history (`experiment-log.md`), investigates the current codebase state, and produces quantitative specs (`specs/*.md`) with measurable acceptance criteria.
2. **Inner loop** executes the specs (see below).
3. Results are archived to `experiment-history/iteration-NNN/`, appended to `experiment-log.md`, committed, and pushed.

The outer loop runs until `--max` iterations are exhausted or the IterationSpecAgent signals `CONVERGED` (all qualitative goals met).

### Inner loop

Each inner-loop retry:

1. **Plan phase** — The PlanAgent reads specs and produces `IMPLEMENTATION_PLAN.md` with prioritized tasks. Runs for `--plan-iters` iterations (default: 2).
2. **Build phase** — The BuildAgent picks the highest-priority incomplete task, implements it, runs tests, commits. Runs for `--build-iters` iterations (default: 8). Exits early if it writes a `.build-done` sentinel (all tasks complete).
3. **Eval phase** — The EvalAgent verifies each spec's acceptance criteria against actual test output and codebase state. Produces a verdict: **PASS** (all specs met), **RETRY** (some failed), or **CONVERGED** (all specs met and all high-level goals met).

On RETRY, the inner loop wipes the implementation plan and starts over (up to `--max-retries`, default: 2). On PASS or CONVERGED, it exits successfully.

## Usage

```bash
# First run — initializes workspace, then runs
./run.sh doc-ingest GOALS.md --max 3

# Subsequent runs — detects existing workspace, resumes
./run.sh --max 5

# Dry run — shows what would happen
./run.sh --dry-run
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--max N` | Max outer iterations | unlimited |
| `--build-iters N` | Build agent iterations per retry | 8 |
| `--plan-iters N` | Plan agent iterations per retry | 2 |
| `--model <model>` | Override spec agent model | opus |
| `--plan-model <model>` | Override plan agent model | sonnet |
| `--build-model <model>` | Override build agent model | sonnet |
| `--dry-run` | Show what would happen without executing | — |

Models can also be set via environment variables: `EXPERIMENT_SPEC_MODEL`, `EXPERIMENT_PLAN_MODEL`, `EXPERIMENT_BUILD_MODEL`, `EXPERIMENT_EVAL_MODEL`.

## Workspace Layout

`experiment-init.sh` creates these artifacts:

| File | Purpose |
|------|---------|
| `GOALS.md` | Qualitative goals the loop optimizes toward |
| `experiment-log.md` | Append-only history of iterations, outcomes, and learnings |
| `iteration-count` | Current iteration number |
| `challenge-rules.conf` | Progressive challenge config (e.g., add 1 PDF per iteration) |
| `experiment-history/` | Per-iteration archives (specs, eval reports, briefs) |
| `specs/` | Current iteration's spec files (wiped each iteration) |

## Agent Prompts

Each agent has a prompt file at the repo root:

| File | Agent | Mode |
|------|-------|------|
| `PROMPT_iteration_spec.md` | IterationSpecAgent | Read-only. Investigates codebase, writes specs. |
| `PROMPT_plan.md` | PlanAgent | Read-only. Reads specs, writes implementation plan. |
| `PROMPT_build.md` | BuildAgent | Read-write. Implements tasks, runs tests, commits. |
| `PROMPT_eval.md` | EvalAgent | Read-only. Verifies specs against actual results. |

Only the BuildAgent modifies code. All other agents are read-only.

## Key Design Decisions

**Qualitative goals, quantitative specs.** GOALS.md describes what good looks like in human terms. The IterationSpecAgent's job is to investigate the corpus, find specific gaps, and turn them into measurable acceptance criteria. This separation means the human sets direction while the agent does the measurement work.

**Retry inside, iterate outside.** The inner loop retries on the same specs (eval said RETRY — try again). The outer loop advances to new specs (what should we work on next?). This mirrors how a human would work: attempt a task a few times, then step back and reassess.

**Early exit.** The BuildAgent writes `.build-done` when all implementation plan tasks are complete and tests pass. This avoids burning remaining build iterations when work is done. If the agent never writes the sentinel, all iterations run — safe fallback.

**Progressive challenge.** `challenge-rules.conf` can specify adding new test PDFs each iteration, forcing the pipeline to generalize rather than overfit to a fixed corpus.

**Experiment log as memory.** The experiment log is the primary mechanism for cross-iteration learning. The IterationSpecAgent reads it to avoid repeating failed approaches and to build on what worked.

## Shared Utilities

`lib.sh` provides:

- Model configuration and environment variable overrides
- Logging functions (`log_step`, `log_info`, `log_error`, `log_timestamp`)
- `claude_generate()` — runs Claude headless with output validation and automatic fix-up (detects and retries when the model produces conversational summaries instead of content)
- `validate_generation()` / `fixup_generate()` — catches preamble, meta-commentary, and tool-use artifacts
- `parse_specs_from_output()` — fallback parser for specs embedded in agent stdout
- Dependency checks (fails fast if `claude` CLI is not installed)
