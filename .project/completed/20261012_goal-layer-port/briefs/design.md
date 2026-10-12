# Brief: /_my_design — goal-layer-port (`WRAP-SPLIT` Item 2)

Write the design for `.project/active/goal-layer-port/spec.md` to `.project/active/goal-layer-port/design.md`. Do not commit; the orchestrator commits. Start no background tasks. End with `ARTIFACT: <path>`.

## Read first

- `spec.md` (revised after review), `spec-review.md` including its "Resolutions" section, `briefs/align.md`, and `product-lens.md`, all beside this brief.
- fusion-tea files: the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea commit `2b1e9f9d5`). You cannot read `/home/reid/1cfe/fusion-tea`.

## What matters most

The owner's central direction is [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". The placement of the design-choice rule is the part of this design the owner will judge. Make it read like a rule that was always part of agentic-mbse's pattern set, not a fusion-tea requirement with the number filed off. Hold the same bar for the goal-layer port: clean, general text in the voice of the surrounding shipped files, with the runbook's method unchanged.

## Orchestrator leans (all [AGENT]; overrule them with reasons if the code says otherwise)

1. **Rule home and shape.** A new detailed reference in `docs/patterns/` carries the one full statement, with a plain name. Equality intent stays where it is, unrewritten, and the two name each other. The "Process Selection" row, the point-of-use row and the "Architecture & Design" seed bullet stay one-liners that point at it. This follows the owner's word "patterns" and the table's existing convention. A target reaches the reference through the `get_docs_dir()` resolver, as it reaches every other pattern. If you choose a `MODELING_PROCESS.md` section instead, say what that buys over the resolver route.
2. **Decision record.** Choose its home by how the runbook actually uses it: the runbook cites the records for "why", and an agent reads them rarely. The resolver route (`docs/goal-layer-decisions.md`) matches the patterns. A file inside a skill bundle is installed into the target but has runtime-specific paths, and `tests/test_shipped_text.py` rejects `.claude/` paths in runtime-neutral text. Use the epic's authority stance unless you find a reason against it: a dated snapshot, cited by fusion-tea path and commit, is the authority for installed targets; fusion-tea's live ADRs govern fusion-tea only.
3. **fusion-tea side.** Design it as orchestrator-run work, with exact file changes. The orchestrator has a fusion-tea worktree at `/home/reid/1cfe/fusion-tea-goal-layer` on branch `goal-layer-mr7`, cut from `2b1e9f9d5`; the owner pushes and merges it. Facts the orchestrator holds about fusion-tea's pin (from earlier runs, 2026-10-11):
   - fusion-tea pins agentic-mbse in `pyproject.toml` `[tool.uv.sources]` by full GitHub SHA (`adbef75` today), mirrored in `uv.lock`. A pin can point only at a commit pushed to the remote, and pushing agentic-mbse is the owner's. So the pin move is a post-merge step, as in Item 1's runbook (`.project/completed/20261009_native-skill-distribution/evidence/fusion-tea-runbook.md`).
   - Moving it means editing the `rev`, replacing the SHA in `uv.lock` by hand (re-locking fails under uv 0.10), `uv sync --frozen --extra e2e`, reinstalling `syside-license==0.3.6`, and updating the hard-coded SHA in fusion-tea `tests/test_dependency_provenance.py`. Then `uv run --no-sync agentic-mbse init . < /dev/null`.
   - So the branch can carry the content changes now (MR-7 rewrite, `AGENTS.md` lines, `MODELING_PROCESS.md` equal to the shipped template, and whatever else you decide), and the runbook carries the pin move and re-init after the agentic-mbse merge. Decide whether the branch also removes the local `run-goal`/`narrate-goal` and their `.gitignore` whitelist lines, under the spec's merge-order requirement.
   - Rehearsal (SC8) need not touch fusion-tea's virtualenv: run `init` from this worktree's environment into a disposable copy of the fusion-tea branch tip (a detached fusion-tea worktree in the orchestrator's scratch space). Say what the rehearsal runs and what it captures into this repo's `evidence/`.
4. **Fresh-target dry run (SC4).** Orchestrator-run, in a scratch target outside any git repo, so no repo-level `CLAUDE.md` or `.project/` reaches the agent. The brief states the operator's answers in advance. Name the seed fixture and a goal small enough to ground in one sitting.
5. **Contract test.** Pick a path that cannot collide with fusion-tea's `tests/orchestration/test_goal_contract.py`, and an ownership class, with reasons.

## Execution constraints the plan will inherit

- Stage subagents cannot read or write fusion-tea, `~/.claude/`, or anything outside this worktree. Mark every step that needs fusion-tea, a scratch target outside the repo, or a live `claude -p` run as orchestrator-run.
- An implement stage started fresh can commit; a resumed one cannot. Size phases so each fits one implement session.

## Keep it tight

Re-estimate the effort honestly against the two-day ceiling and record any overrun with its cause, per the Resolutions (do not split the item). The design should be as short as its decisions allow: decisions with their rejected alternatives in one line each, the exact text where wording is the decision (the rule itself, the table rows, the trigger-table row, the MR-7 rewrite), and file-level changes. Do not restate the spec.
