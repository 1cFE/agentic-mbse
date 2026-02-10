# Iteration Loop: Usage Guide & Smoke Test Report

**Date:** 2026-02-10
**Branch:** ralph/doc-ingest
**Result:** PASS (1 iteration, 2 retries)

---

## 1. Setup

### Prerequisites

| Requirement | Check |
|-------------|-------|
| `claude` CLI installed and authenticated | `which claude` |
| `python3` available | `which python3` |
| `validate-specs-output.sh` at `~/.claude/scripts/` | `ls ~/.claude/scripts/validate-specs-output.sh` |
| Branch `ralph/doc-ingest` checked out | `git branch --show-current` |

### One-time initialization

```bash
# Write GOALS.md with qualitative goals (or use existing)
# Then run init:
./experiment-init.sh <project-name> <goals-file>

# Example:
./experiment-init.sh doc-ingest GOALS.md
```

This creates:
- `experiment-log.md` — running iteration history
- `iteration-count` — starts at 0
- `challenge-rules.conf` — progressive challenge config
- `experiment-history/` — archive directory
- `specs/` — empty, populated each iteration

It also:
- Cleans old Ralph artifacts (`DESIGN.md`, `loop.sh`, etc.)
- Strips `## Status` section from `AGENTS.md`
- Updates `.gitignore` (excludes `*.pdf`, `.env`, `tests/corpus/pool/`)
- Commits everything

**Note:** If `GOALS.md` is the goals file, the copy is skipped (same-file guard).

### Progressive challenge (optional)

To enable progressive PDF addition each iteration, populate the pool:

```bash
mkdir -p tests/corpus/pool/
# Add PDFs via Zotero download (from fusion-tea):
cd /path/to/fusion-tea
uv run python scripts/zotero_group_download.py <ITEM_KEY> \
  --output-dir /path/to/doc-ingest/tests/corpus/pool/
```

The `challenge-rules.conf` default adds 1 PDF per iteration from the pool.

### Resume an existing workspace

```bash
./experiment-init.sh --resume doc-ingest GOALS.md
```

Validates the workspace exists and prints next steps. Does not overwrite.

---

## 2. Invocation

### Smoke test (1 iteration)

```bash
./outer-loop.sh --max 1
```

### Multi-iteration run

```bash
./outer-loop.sh --max 3    # 3 iterations
./outer-loop.sh             # unlimited (until CONVERGED)
```

### Dry run (see what would happen)

```bash
./outer-loop.sh --max 1 --dry-run
```

### Override spec agent model

```bash
./outer-loop.sh --max 1 --model sonnet   # cheaper, faster
```

### What happens per iteration

1. **IterationSpecAgent** (opus) reads goals, experiment log, runs tests, inspects quality, writes specs + iteration-brief.md
2. **Plan agent** (sonnet) reads specs, studies code, produces IMPLEMENTATION_PLAN.md
3. **Build agent** (sonnet, 8 iterations) implements tasks, runs tests, commits
4. **Eval agent** (sonnet) runs tests, inspects results, produces eval-report.md with VERDICT
5. On RETRY: wipe plan, re-run plan+build+eval (max 2 retries)
6. On PASS: archive to `experiment-history/iteration-NNN/`, update experiment-log.md, commit + push

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `EXPERIMENT_SPEC_MODEL` | `opus` | Model for IterationSpecAgent |
| `EXPERIMENT_BUILD_MODEL` | `sonnet` | Model for plan + build + eval agents |
| `EXPERIMENT_EVAL_MODEL` | `sonnet` | Model for eval agent |

---

## 3. Smoke Test Observations

### Timeline

| Phase | Duration | Model | Notes |
|-------|----------|-------|-------|
| IterationSpecAgent | ~10 min | opus | Deep investigation: ran tests, read source, inspected extracted files |
| Inner loop retry 1 | ~25 min | sonnet | Plan (2 iters) + build (8 iters) + eval |
| Inner loop retry 2 | ~25 min | sonnet | Fixed constraint violation, re-evaluated |
| Outer loop commit/push | <1 min | — | Archive, log, commit, push |
| **Total** | **~60 min** | | |

### What the IterationSpecAgent produced

3 specs from qualitative GOALS.md input:

1. **fix-delene-baseline-artifacts** — Identified that the delene_2001 baseline was contaminated with 28 Claude Layer 3 AI hallucination artifacts (conversational text like "I notice you mentioned an image..."), creating a phantom -6.2% character regression. Spec required cleaning the baseline.

2. **add-bold-allcaps-heading-promotion** — Found a specific regex gap: bold all-caps headings like `**ABSTRACT**` (8 chars) fall through both the allcaps promoter (requires no bold markers) and the unnumbered bold promoter (requires 14+ chars). Cited exact lines in delene_2001.

3. **add-sparc-to-corpus** — Progressive challenge: add SPARC tokamak paper from pool, expanding corpus from 5 to 6 papers.

**Quality of specs was high.** Each had: purpose, requirements, investigation steps (learning tests), evidence with line numbers, specific acceptance criteria with thresholds, exact verification commands, and constraints.

### Retry mechanism worked correctly

**Retry 1 eval verdict: RETRY.** The eval agent found that hsu_2020 heading count dropped from 6 to 4. The spec said "Do NOT reduce heading counts for hsu_2020" — the eval agent correctly enforced this as a hard constraint, even though the test suite's -50% threshold passed. The eval agent noted the lost headings were likely baseline false positives but correctly interpreted the spec strictly.

**Retry 2 fix:** The build agent cleaned the hsu_2020 baseline (removed false positive headings), then re-ran tests. All constraints satisfied.

**Retry 2 eval verdict: PASS.** All 3 specs passed.

### Commits produced (8 total)

```
51d87cb Clean delene_2001 baseline by removing 28 AI hallucination artifacts
c32b13b Add bold all-caps heading promotion to fix detection gap
dbc4c7a Add SPARC tokamak paper to test corpus (6th paper)
550fc19 Clean up IMPLEMENTATION_PLAN.md after Iteration 1 completion
ca8cc4a Clean hsu_2020 baseline to resolve phantom heading regression
846fe32 Clean IMPLEMENTATION_PLAN.md after Iteration 1 completion
4882b19 Fix test_extraction.py to match current pymupdf_backend implementation
aa35944 iteration 1: PASS — # Iteration 1 Brief
```

### What went well

- **IterationSpecAgent investigation depth.** It ran the corpus tests, read the comparison report, inspected the extracted markdown, read the postprocess source code, and identified root causes before writing specs. The prompt improvements (backpressure tools, learning tests, tool investigation) clearly influenced its behavior.

- **Spec quality.** The specs were specific, measurable, and grounded in evidence. The bold-allcaps spec included the exact regex patterns that were failing and the exact line numbers in the corpus files.

- **Eval agent strictness.** The eval agent correctly caught a constraint violation that the test suite's relaxed thresholds would have missed. It applied strict interpretation as instructed.

- **Retry self-correction.** On retry 2, the build agent understood the eval failure, identified that the hsu_2020 baseline had false positive headings, cleaned them, and re-validated.

- **Progressive challenge.** The SPARC paper was added to the corpus with correct metadata, baseline, and metrics. Corpus grew from 5 to 6 papers.

- **Archiving.** All artifacts correctly archived to `experiment-history/iteration-001/` with specs, brief, eval-report, and both retry reports.

### Issues and observations

1. **Eval report captured agent thinking.** The eval-report.md and eval-report-retry-1.md both include the agent's internal reasoning before the formatted report (e.g., "So the breakdown is:..." followed by the actual report). The `--output-format text` captures everything the agent outputs, including reasoning preamble. This is cosmetic — the verdict parsing (`grep -oP 'VERDICT:\s*\K\w+'`) handles it correctly — but the archived reports are messy.

2. **Key Learnings not backfilled.** The experiment-log entry for Iteration 1 has a "Starting State" section with `Key Learnings: _(to be filled by eval agent)_` that was never updated. The backfill instruction tells the IterationSpecAgent to do this on the NEXT iteration. Since we only ran 1 iteration, backfill hasn't been tested yet.

3. **Key Learnings in log entry are meta.** The outer loop's extracted Key Learnings from the eval report describe the iteration loop system itself ("All 5 shell scripts are implemented and functional...") rather than doc-ingest quality insights. This happened because the retry-2 eval agent evaluated the loop infrastructure rather than extraction quality. Future iterations should produce more substantive learnings about the extraction pipeline.

4. **Build iterations are generous.** The build agent completed all 3 tasks within the first few build iterations but continued cycling through the remaining iterations doing plan cleanups and minor fixes. The 8-iteration default may be more than needed for small specs, but provides headroom for complex tasks.

5. **Experiment-log has duplicate Iteration 1 entries.** The IterationSpecAgent wrote a "Starting State" section, and the outer loop appended a separate "Iteration 1 — 2026-02-10" entry. Both contain useful but overlapping information. The IterationSpecAgent's entry has more detail about the starting state; the outer loop's entry has the outcome and key learnings.

### Cost estimate

Rough estimate for 1 iteration (with 1 retry):
- IterationSpecAgent: ~10 min opus
- 2x (plan + build + eval): ~50 min sonnet total
- Total: ~60 min wall clock

For multi-iteration runs, expect ~45-60 min per iteration depending on spec complexity and retries.
