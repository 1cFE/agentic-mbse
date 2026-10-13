# Brief: /_my_implement — research-seam-port (`WRAP-SPLIT` Item 5)

This brief is shared by every implement phase. Each run's message names the phase, and you implement only that phase of `.project/active/research-seam-port/plan.md`. Start no background tasks. End with `ARTIFACT: .project/active/research-seam-port/plan.md`.

## Read first

`plan.md` (your phase, plus "Conventions for every phase"), `design.md` (the D, I and Appendix numbers your phase cites), and the snapshot code you port, in `.orchestrate-logs/fusion-tea-snapshot/` (read-only; fusion-tea `0a833b9f7`, current as of `c42ed1d8a`). Read the Implementation Notes of earlier phases in `plan.md` before you start.

## The bar

- **Behaviour first.** Port the ladder order, messages, outcomes and on-disk shapes exactly, except where the design's Behaviour Changes table says otherwise. When the snapshot and the design disagree on something the table doesn't list, follow the snapshot. Record the disagreement in your phase's Implementation Notes.
- **Code that reads like agentic-mbse.** Small modules with one job each, typed signatures, frozen dataclasses for results, and docstrings that say what a function guarantees. Model it on `src/agentic_mbse/pm/` and `cli/pm_cli.py`. Leave out consumer citations, design-record ids (`seam D7`, `R-*`, `audit F*`, `WI-*`) and dead code. A comment explains a reason the code can't show. Tests check behaviour, not implementation trivia.
- **No shortcuts past the exit check.** Don't skip a moved test to get green. Don't loosen a golden value. Don't add a `# type: ignore` or `noqa` without a one-line reason. If a moved test cannot pass without a behaviour change the design doesn't list, stop. Say so in your final message, and don't improvise.

## Environment facts ([AGENT], verified by the orchestrator 2026-10-12)

- The venv is synced with `uv sync --all-extras`. Baselines are in `.orchestrate-logs/baseline-{pytest,ruff,mypy}.txt`.
- The snapshot's `zotero_lib.py` imports `pyzotero` at module level, and `pyzotero` is not installed (`dotenv` is). When P1's scratch script under `.orchestrate-logs/golden/` imports snapshot modules to derive golden values, it puts a stub `pyzotero` package on `sys.path` inside `.orchestrate-logs/golden/`. Never add `pyzotero` to agentic-mbse's dependencies or venv.
- The worktree root has its own `knowledge/` directory. Tests must never write there.
- Do not edit `src/agentic_mbse/cli/installation.py`.
- You cannot read or write fusion-tea, `~/.claude/`, or anything outside this worktree, and you cannot run `claude -p`.

## Finish

- Run the phase's exit check. Fill your phase's Implementation Notes in `plan.md` with what changed, any deviation and why, and anything the next phase must know. Check off the phase's boxes.
- Commit once, staging only this phase's paths, with a subject that leads with what changed. End the message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. If you cannot commit, stage the commit under `.orchestrate-logs/commit-steps/P<n>.md` (paths, message, exit-check output), and say so.
- Your final message reports the exit-check numbers (passed, skipped, failed; ruff and mypy counts) and any deviation.
