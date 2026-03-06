---
date: 2026-02-13T18:00:00-07:00
researcher: Claude
topic: "BART Loop Process Learnings: What Went Wrong and How to Improve Autonomous Agent Iteration"
tags: [research, process, bart, ralph, agent-orchestration, pdf-extraction]
status: complete
last_updated: 2026-02-13
---

# Research: BART Loop Process Learnings

**Date**: 2026-02-13 18:00 MST
**Researcher**: Claude
**Research Type**: Process / Architecture

## Research Question

The BART loop (Build-Agent Retry Topology) was applied to the PDF extraction problem across multiple worktrees and ~5 outer iterations. The resulting pipeline grew from 57 lines to 797 lines of custom code without meaningfully improving extraction quality on the hardest problems (math, complex tables). Why didn't the autonomous iteration produce better outcomes? What would a better middle ground between RALPH (front-loaded design) and BART (self-guided iteration) look like?

## Summary

- BART's IterationSpecAgent consistently chose heading detection as the problem to solve, spending ~25 commits on promote-then-demote regex patterns while ignoring the harder (and more impactful) problems of equation extraction and table recovery
- The loop has no mechanism for architectural backpressure — nothing prevents the agent from accumulating complexity in one layer when the real fix is at a different level of the stack
- GOALS.md was well-written and explicitly warned against downstream regex fixes, but the spec agent ignored these constraints because the prompt structure rewards "find a failing test, fix it" over "investigate the extraction tools"
- RALPH's front-loaded design works when the solution architecture is known; BART's open-ended iteration works when the problem space needs exploration — PDF extraction needs a hybrid: constrained exploration with human-set architectural guardrails
- The key missing piece is **problem decomposition by a human** — not full architecture design (RALPH) or no design (BART), but a lightweight framing that tells the agents what categories of work exist and what approaches are off-limits

## Detailed Findings

### 1. What BART Actually Did: The Commit Record

The git history across the `ralph/doc-ingest` worktree shows three distinct BART experiment runs (each starting with `experiment-init`), plus a RALPH-driven phase that preceded them:

**RALPH phase** (commits `73a20d5`–`b45cee3`): Built the original extraction pipeline, three-layer architecture (pymupdf → GMFT tables → Claude repair), test corpus infrastructure, quality routing. This was ~20 commits of focused implementation against a clear design. The original `pymupdf_backend.py` was 57 lines — a clean wrapper around `pymupdf4llm.to_markdown()`.

**BART run 1** (`bfeaa12`–`aa35944`): 1 outer iteration. IterationSpecAgent investigated the corpus, found heading detection gaps, produced specs. BuildAgent fixed plain header regex, promoted italic headers, added ligature repair, added energy_amplifier to corpus. Reasonable scope, useful fixes.

**BART run 2** (`7bc8ed1`–`4b95c85`+`2245c7b`–`5340eda`): 2 outer iterations across two experiment-inits. This is where the pattern went wrong. The spec agent found phantom headings (correct observation) and prescribed adding guards and noise rejection patterns (wrong approach). Commits show: implement custom multi-signal header detector → fix Pattern 1 guards → fix Pattern 2 guards → extend noise header rejection → add address rejection → extend bibliographic detection → enhanced bibliographic detection. **12 commits all touching the same two files** (pymupdf_backend.py and postprocess.py), each adding more regex patterns.

**BART run 3** (`0a8798d`–`c778cc6`): 1 outer iteration, current worktree. Switched `table_strategy` to `lines_strict` and extended Guard 2. The `lines_strict` change was genuinely good (upstream parameter fix). The Guard 2 extension was more promote-then-demote logic.

**Net result across all BART runs**: ~25 commits that grew `postprocess.py` from 0 to 560 lines and `pymupdf_backend.py` from 57 to 237 lines. The `_is_noise_header()` function alone is 170 lines of regex matching bib entries, addresses, equations, table rows, TOC lines, report labels, and figure references — each pattern added to patch a false positive created by the heading promotion logic.

### 2. Why the Loop Got Stuck: Structural Analysis

**Observation A: The spec agent optimized for what was measurable, not what was impactful.**

The corpus tests measure heading count (min/max bounds), table row count, and character count. Heading count was the metric that most frequently failed. The spec agent, reading test failures, naturally wrote specs to fix heading counts. But heading count is a proxy metric — what matters is whether the headings are correct, not how many there are. The agent optimized the proxy.

Meanwhile, the truly impactful problems — equations losing fraction structure, tables replaced by image placeholders, superscripts becoming bracket notation — are not measured by any corpus test. They happen inside pymupdf4llm before our code runs. The spec agent never wrote specs for these because no test fails on them.

**Observation B: No architectural guard prevented the promote-then-demote anti-pattern.**

GOALS.md says: "Fixes that add format-specific pattern matching are low-value because each new format needs another pattern." The spec agent prompt says: "Prefer leveraging existing library features over writing new custom code." Both are correct guidance.

But the spec agent's investigation process is: read goals → run tests → inspect output → write specs. When it inspects output and sees "## 30 M shots." (a phantom heading), the fastest path to a measurable improvement is a regex to catch that pattern. The spec prompt asks for a "self-check" but there's no enforcement — the agent checks its own work and finds it acceptable.

The fundamental problem: **the spec agent has no constraint on solution architecture**. It can see that pymupdf4llm has font metadata, and it can see that the heading detector already uses font metadata, but there's nothing stopping it from adding another downstream regex instead of rethinking how the detector works.

**Observation C: Each iteration made the next iteration's problem harder.**

The promote-then-demote architecture means each new heading promoter creates new false positives for the noise filter, and each new noise filter risks demoting real headings. The spec agent in iteration 2 saw more phantom headings than iteration 1 — because iteration 1's changes created new ones. This is the textbook "accumulating maintenance burden" that GOALS.md warned about, but the spec agent couldn't see it because each individual iteration's tests passed.

**Observation D: The build agent had no reason to question the spec.**

The PROMPT_build.md says: "Read specs, pick highest-priority task, implement it." The build agent faithfully implemented every regex pattern the spec agent prescribed. It had no prompt structure for saying "this approach is creating complexity" or "the spec is asking me to patch a symptom." Even when the build agent had to write 170 lines of noise rejection patterns, there was no signal to escalate.

**Observation E: The eval agent couldn't detect architectural decay.**

The PROMPT_eval.md evaluates whether specs' acceptance criteria are met. "Heading count within bounds" — PASS. "No phantom heading X in paper Y" — PASS. The eval agent has no criteria for "did the solution generalize" or "did the codebase get more maintainable." It checks spec compliance, not solution quality.

### 3. RALPH vs BART: Where Each Works

**RALPH** (front-loaded spec → design → plan → implement):
- Works when the solution architecture is known or knowable before implementation
- The comment system implementation (commits `dff30bc`–`f62866f`) was 18 tasks across 9 work packages, all implemented cleanly because the design was clear: Pydantic models → similarity functions → CLI → MCP server → git integration
- Fails when the problem space needs exploration — you can't design a PDF extraction pipeline without experimenting with what the extraction libraries actually produce

**BART** (qualitative goals → autonomous spec → plan → build → eval → iterate):
- Works when the problem space needs exploration and quality is measurable
- The `table_strategy="lines_strict"` discovery was genuine BART value — the spec agent investigated library parameters and found one that solved the problem
- Fails when it lacks architectural constraints — the spec agent gravitates toward the easiest measurable improvement (regex patches) rather than the hardest impactful one (rethinking how the tool is called)

**The gap**: Neither approach handles "explore a problem space but within architectural constraints." RALPH assumes the architecture is known. BART assumes the agent will figure out the architecture. PDF extraction needs the human to set architectural boundaries while the agent explores within them.

### 4. The Dormant Modules Problem

The codebase contains significant infrastructure that BART never activated:

- `docling_backend.py` (136 lines) — alternative extraction backend with ML-based layout analysis
- `table_extraction.py` — GMFT-based table detection, already benchmarked at 83% accuracy
- `quality_gates.py` — problem detection between extraction layers
- `claude_structure.py` — Claude-powered structure repair
- `ai_repair.py` — per-region AI repair with cross-validation

These were built during the RALPH phase but never wired into the active pipeline during BART iterations. The spec agent's prompt tells it to investigate these modules, but investigation costs tokens and the reward signal (test pass/fail) doesn't distinguish between "used an existing module" and "wrote a new regex."

### 5. What the 8-Paper Quality Audit Revealed

Our parallel agent review of all 8 papers produced grades from B to C:

| Grade | Papers | Common Issues |
|-------|--------|---------------|
| B | hsu_2020, delene_2001, helios_design | Minor heading issues, good text/table fidelity |
| B- | sparc_overview | Phantom headings in references, degraded equations |
| C+ | woodruff_2026 | 7 phantom + 3 missing headings (12% error rate) |
| C | hawker_2020, aries_cost_account, energy_amplifier | Equations fragmented, tables missing, chart misdetection |

The pattern: **text extraction is consistently solid across all papers** (body text is complete, readable, accurate). The failures are all in structured content — equations, tables, and heading detection. The 797 lines of custom code addresses only heading detection, and even there the results are mixed (B on simple papers, C+ on the paper specifically added to test headings).

## Architecture Insights

### The Promote-then-Demote Anti-Pattern

The current pipeline has two independent heading detection paths:
1. **Upstream** (AcademicHeaderDetector, 150 lines): runs per-span during extraction with font metadata. Promotes numbered patterns to headings.
2. **Downstream** (postprocess.py promoters, ~100 lines): promotes bold headers, plain headers, all-caps headers from markdown text. No font metadata.
3. **Downstream** (postprocess.py noise filter, ~170 lines): demotes headers that look like bib entries, addresses, table rows, equations.

Paths 2 and 3 fight each other. Every new promoter creates new false positives for the filter. This is visible in the commit history — almost every "add promoter" commit is followed by "extend noise filter" commits.

### What Generalization Looks Like

The GOALS.md framing is correct: generalization means leveraging tool capabilities (library parameters, ML models, backend selection), not adding format-specific patterns. The single best change across all BART iterations was `table_strategy="lines_strict"` — a one-line parameter change that eliminated 252 false-positive table artifacts with zero regressions. This is what tool-level fixes look like.

The worst changes were the 170 lines of `_is_noise_header()` patterns — each one fixes a specific paper's false positive but creates implicit dependencies on the formatting conventions of that paper's publisher.

## Recommendations: Hybrid Approach

### The Missing Middle Ground

Between RALPH ("here's the full architecture, implement it") and BART ("here are qualitative goals, figure it out"), there's a useful middle ground: **constrained exploration**.

The human provides:
1. **Problem decomposition** — not a full design, but a breakdown of the problem into independent streams (e.g., "heading detection," "table recovery," "equation extraction")
2. **Approach constraints** — what kinds of solutions are acceptable per stream (e.g., "heading detection: only tool-parameter and backend-selection changes, no downstream regex")
3. **Priority ordering** — which streams to work on first, based on impact
4. **Escape valve** — explicit instructions for what to do when stuck ("if you can't improve equations with the current tools, document what you tried and stop")

The agent provides:
1. **Investigation** — what do the tools produce? what parameters exist? what's underutilized?
2. **Experimentation** — learning tests, parameter sweeps, backend comparisons
3. **Implementation** — within the constraints set by the human
4. **Reporting** — what worked, what didn't, what the human should rethink

### Concrete Framing for PDF Extraction (If Restarted)

If the BART loop were restarted with better guidance, the human should provide something like:

**Stream 1: Backend Selection (highest priority)**
- Compare pymupdf4llm vs Docling on each corpus paper for heading, table, and equation quality
- The winner becomes the default backend; the loser becomes the fallback
- Constraint: no custom postprocessing in this stream — only tool parameters and backend selection
- Deliverable: a comparison matrix and a justified default backend choice

**Stream 2: Table Recovery (high priority)**
- For papers where `lines_strict` drops real tables (aries_cost_account), investigate GMFT integration (already built, needs wiring)
- Constraint: GMFT is already benchmarked at 83% — wire it, don't rewrite it
- Deliverable: tables that `lines_strict` misses are recovered by GMFT fallback

**Stream 3: Heading Detection (medium priority, constrained)**
- The only acceptable heading changes are: adjusting pymupdf4llm parameters, adjusting font pre-scan logic, or switching to Docling's heading detection
- Constraint: NO new regex patterns in postprocess.py — if the detector can't be fixed at the tool level, document the limitation and move on
- Deliverable: heading accuracy improves or stays flat, but postprocess.py does not grow

**Stream 4: Equation Extraction (exploratory, bounded)**
- Investigate what Docling, Nougat, or marker produce for equations
- Time-box: 1 iteration of investigation only
- Deliverable: a comparison report, not implementation

### Process-Level Fixes for BART

If BART is used again, these structural changes would help:

1. **Human-written constraints per iteration** — not just GOALS.md, but a "this iteration, you may only change X" directive. The spec agent should have boundaries, not just aspirations.

2. **Complexity budget** — "postprocess.py may not exceed N lines" or "no more than K regex patterns in noise rejection." This forces the agent to find tool-level solutions when the complexity budget is exhausted.

3. **Architectural review checkpoint** — between the spec agent and the build agent, a human (or a separate review agent) evaluates whether the proposed specs are upstream fixes or downstream patches. Veto power on approach, not just on acceptance criteria.

4. **Metric coverage for the real problems** — add corpus metrics for equation quality, table completeness, and structured content fidelity. If the only failing test is heading count, that's all the agent will work on.

5. **Mandatory tool investigation before spec writing** — require the spec agent to produce a "tool investigation report" showing what parameters, backends, and existing modules it explored and ruled out before proposing custom code.

6. **Escape-hatch protocol** — if the spec agent can't find a tool-level fix, it should be allowed to say "this problem cannot be solved at this layer of the stack" and move to the next priority, rather than being forced to produce a spec (which will inevitably be a regex patch).

## Open Questions

1. **Is BART worth continuing vs. starting fresh with constrained exploration?** The loop machinery (shell scripts, agent prompts, experiment history) is well-built. The problem is the guidance, not the infrastructure.

2. **Should the quality audit results feed into the next iteration?** The 8-paper assessment we just completed is the most thorough quality analysis done on this pipeline. It could serve as the "investigation phase" for a human-guided restart.

3. **How much of the dormant infrastructure (GMFT, Docling, quality gates) actually works?** The RALPH phase built it, the BART phase ignored it. A quick "wire it up and see what happens" experiment might be more valuable than any amount of regex tuning.

4. **What's the right granularity for human intervention?** Per-iteration review is probably too frequent (blocks autonomous progress). Per-stream constraints set once and reviewed at stream completion might be the sweet spot.

## Code References

- `src/agentic_mbse/extraction/pymupdf_backend.py:1-237` — The full extraction backend including AcademicHeaderDetector (grew from 57 lines)
- `src/agentic_mbse/extraction/postprocess.py:1-560` — All postprocessing (did not exist before BART)
- `src/agentic_mbse/extraction/postprocess.py:309-497` — `_is_noise_header()`, the 170-line regex gauntlet
- `src/agentic_mbse/extraction/docling_backend.py` — Dormant alternative backend
- `src/agentic_mbse/extraction/table_extraction.py` — Dormant GMFT integration
- `src/agentic_mbse/extraction/quality_gates.py` — Dormant quality gate infrastructure
- `PROMPT_iteration_spec.md` — Spec agent prompt (well-written constraints that weren't enforced)
- `PROMPT_build.md` — Build agent prompt (no mechanism to question approach)
- `PROMPT_eval.md` — Eval agent prompt (checks spec compliance, not solution quality)
- `GOALS.md` — Qualitative goals (correct priorities, ignored by the loop)
- `BART_README.md` — Loop architecture documentation
