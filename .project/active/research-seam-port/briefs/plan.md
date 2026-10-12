# Brief: /_my_plan — research-seam-port (`WRAP-SPLIT` Item 5)

Write the implementation plan for `design.md` to `.project/active/research-seam-port/plan.md`. Do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

## Read first

`design.md` (revised after review; D1–D18, I1–I8, Appendices A–D), `design-review.md` including its Resolutions, `spec.md`, `briefs/align.md` and `evidence/o1-baseline.md`, all beside this brief. The fusion-tea code to port is in the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`, current as of `c42ed1d8a`).

## Shape

- **Six implement phases, P1–P6, as the design's Next-Stage Handoff lists them.** Each phase must fit one implement session. Give each phase its files, the tests it moves or adds (by Appendix B row), the D and I numbers it satisfies, and an exit check.
- **Every phase uses the same exit check.**
  - `uv run pytest tests/` shows no new failures over the baseline: 2,217 passed, 1 skipped, 1 xfailed, 5 deselected at `ac5fb1a` under `uv sync --all-extras`, recorded in `.orchestrate-logs/baseline-pytest.txt`. In addition, `uv run pytest tests/test_research -m ""` passes, so the ported `slow` tests run too.
  - `uv run ruff check src/ tests/` and `uv run mypy src/` add no findings over `.orchestrate-logs/baseline-ruff.txt` (118) and `.orchestrate-logs/baseline-mypy.txt` (88).
  - A phase commits once, with a subject that leads with what changed.
- **Interleave the orchestrator-run steps where they belong, marked "Orchestrator".** Stage subagents cannot do them.
  - O1's `verify` comparison runs right after the phase that lands `verify.py` and the CLI's `verify`. If the CLI lands later than `verify.py`, the plan says how the orchestrator calls it in between, or moves the comparison to after the CLI.
  - The rest of O1 (the fusion-tea branch) runs after P6.
  - O2a and O2b run after P6, from a built wheel.
  - O3 is post-merge and owner-paced. The plan lists it but does not schedule it.
- **Before the first code moves,** P1 lands the I1 golden tests against the snapshot's behaviour. That is the design's de-risking order.

## Constraints

- An implement stage started fresh can commit; a resumed one cannot. If a phase is resumed, it stages its commit under `.orchestrate-logs/commit-steps/` with the verify output, and the orchestrator commits.
- Stage subagents cannot read or write fusion-tea, `~/.claude/`, or anything outside this worktree, and cannot run `claude -p`.
- Do not edit `src/agentic_mbse/cli/installation.py`, because Item 3's branch edits it.

## Keep it tight

Reference the design by D, I and Appendix numbers rather than restating it. Use checkboxes. Leave a short "Implementation Notes" slot under each phase for the implementer to fill.
