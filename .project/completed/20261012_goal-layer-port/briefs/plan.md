# Brief: /_my_plan — goal-layer-port (`WRAP-SPLIT` Item 2)

Write the implementation plan for `.project/active/goal-layer-port/design.md` (approved in round 2 of `design-review.md`) to `.project/active/goal-layer-port/plan.md`. Do not commit; the orchestrator commits. Start no background tasks. End with `ARTIFACT: <path>`.

## Inputs

`spec.md`, `design.md`, `design-review.md` (both rounds and the Resolutions), `briefs/align.md`. The design's exact texts (Appendix A), line-change table (B), ledger rows (C), fusion-tea work (D), reach trace (E) and model (F) are the source; the plan sequences them and does not restate them.

## Carry these into the plan (from round 2, plus one orchestrator call)

- Rule 7's "stays the basis", and Acceptance's "stays explicitly unsupported" and "records compliance", take MR-7's own force when the file is written: "must remain", "must record" (round 2, reviewer's own round-1 miss).
- [AGENT] (orchestrator call) The clause added to the template's `:59` seed sentence must forbid one direction only, as MR-7 does: do not set installed capacity, equipment or inventory from demand. "Do not set one from the other" also forbids setting an operating point from installed capacity, which is often a legitimate operating assumption, and it goes beyond the owner-ratified rule. Use the one-direction wording; the SC6 crosswalk records it.
- Verification step 1 says an identity over supplied values (such as `volume = area * length`) passes.
- A `---` before the closing grade paragraph of `design-choices.md`.
- The dry run (design D3): `mkdir` the target before `init`; set `VIRTUAL_ENV` as well as `PATH` (unverified by the reviewer; the orchestrator checks it at run time).

## Shape the plan this way

- **Phases a stage can run** (agentic-mbse worktree only): P1 is the fixture and its kept test (Appendix F; validate all three trees). Then the rule placement, the goal-layer port, installer registration and tests, the decision record, the contract tests (SC5(f), with one reverted edit shown), and the evidence that lives in this repo (SC12 hunk diff, SC6 crosswalk, SC5(d) trace, ledger section). Each phase ends with the checks it can run (`uv run pytest tests/`, ruff, mypy, the SC2 grep) and one commit. Size each phase so one fresh implement session finishes it; a resumed session cannot commit.
- **Orchestrator-run phases**, marked as such, with exact commands and what to capture into `.project/active/goal-layer-port/evidence/`: the fusion-tea F1 content commit on `goal-layer-mr7` in `/home/reid/1cfe/fusion-tea-goal-layer`; the SC8 rehearsal on a disposable copy of that branch tip; the SC4 dry run from a wheel in a scratch venv outside any repo. Put them after the agentic-mbse phases they depend on (F1 copies the template bytes, so it follows the template phase).
- **Post-merge (not executed in this run):** F2 (pin move, local-skill removal, re-init, the resolver hop in fusion-tea's own environment) as a runbook in evidence, rehearsed by the SC8 run where possible. The owner merges; F2 follows.
- Checkboxes per phase, and a short "Progress notes" slot under each for the implementer.

Keep it tight: steps, files, checks, commit subject. No restated rationale.
