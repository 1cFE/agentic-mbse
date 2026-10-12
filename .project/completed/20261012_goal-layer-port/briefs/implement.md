# Brief: /_my_implement — goal-layer-port (`WRAP-SPLIT` Item 2)

Shared brief for every implement session of this item. The orchestrator names the phases for each session in its arguments.

## What to do

- Read `.project/active/goal-layer-port/plan.md` (the phases you were given, plus "Carried into this plan" and "Shared checks"), and the design sections those phases cite. The design's Appendix A holds exact texts; use them as written, with the plan's carried changes applied.
- Work only in this worktree (`/home/reid/1cfe/agentic-mbse-goal-layer`). You cannot reach fusion-tea; its files are in the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea commit `2b1e9f9d5`). Do not run the orchestrator-run phases (O0–O3) or F2.
- Write each phase's tests first, then the change, then the shared checks. Make exactly one commit per phase, with a subject that leads with what the phase decided or delivered, and end the message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Commit with explicit paths; never `git add -A`. Do not push.
- Tick the phase's checkboxes in `plan.md` and fill its "Progress notes": what changed, anything that deviated from the plan and why, and anything the next phase or the auditor should know. Include `plan.md` in the phase commit.
- Start no background tasks.

## The bar

- **Engineering quality, not "it runs".** Code reads like the surrounding code: its naming, its comment density, its idioms. Tests check behaviour that matters and would fail if the behaviour broke; no tests that only restate the implementation.
- **Shipped text reads as agentic-mbse's own.** New docs, skills and templates match the voice and shape of their neighbours (other `docs/patterns/` files, other skills, the existing templates). General rules, labelled examples, no fusion-tea pointer as authority. In new markdown files, keep each paragraph and list item on one line; in existing files, match what is there.
- **The port is a port.** Change only what the design's line-change table and the plan's steps name. If you find you need to change the runbook's method, or a design text looks wrong, stop and say so in your final message instead of improvising.
- **Report faithfully.** If a check fails or a step is skipped, say so with the output.

End your final message with the commit hash(es), the check results, and anything the orchestrator must decide.
