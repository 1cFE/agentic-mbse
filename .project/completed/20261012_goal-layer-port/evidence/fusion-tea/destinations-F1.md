# F1: every ledger destination exists on the fusion-tea branch

Checked by the orchestrator, 2026-10-11, on `goal-layer-mr7` at `32bd4529a` (base `b06585709`, fusion-tea `main` after its PR #122). Ledger rows are those of the Item 2 section of `.project/active/wrap-split-migration-ledger.md`. The ledger's `CLAUDE.md` line numbers are the base's (`b06585709` equals `2b1e9f9d5` for that file); F1's new section moves later lines down by 10.

| Destination | Where on the branch |
|---|---|
| `CLAUDE.md` "Goal layer in this repository" with "Research", "Integration", "Studies", "Decision records", "Launcher" | `CLAUDE.md:7-17` (added by F1) |
| MR-7 "Invariant", "Conductor models", "Depth work" | `modeling_project/REQUIREMENTS.md`, MR-7 (rewritten by F1; heading and authority line byte-identical to the base) |
| `CLAUDE.md` holdout line | `CLAUDE.md:257` (base `:247`, exists) |
| `CLAUDE.md` "Project Management — Two Systems" | `CLAUDE.md:84` (base `:74`, exists) |
| `CLAUDE.md` "Research Artifact Sync (R2)" | `CLAUDE.md:312` (base `:302`, exists) |
| `AGENTS.md:7`, `:11` (Codex test-worktree launcher) | exist, unchanged |
| `.project/adr/`, ADR-0009, run-study runbook, the probe record, the concept file | exist at the base, unchanged |
| `tests/orchestration/test_goal_contract.py` (ADR-register check) | exists, unchanged |
| The shipped rule and rows that MR-7 now cites | agentic-mbse `goal-layer-port`; reach fusion-tea at F2's pin move |

**Anchors.** `### MR-7: Preserve Design Choices; Separate Evaluation from Design Selection` is at `REQUIREMENTS.md:87`; the anchor `mr-7-preserve-design-choices-separate-evaluation-from-design-selection` is linked from `CLAUDE.md` and `.project/completed/20261011_demo-depth-rubric/application-policy.md` (one hit each).

**Bytes (SC7).** `cmp` of `modeling_project/MODELING_PROCESS.md`, `work/orchestration/GOAL_RUNBOOK.md` and the three goal templates against this repo's templates at `64ae4ed` is silent. `learnings.md` already equalled its template, so F1 commits six paths, not seven.

**One wording call beyond design A6.** MR-7's opening says "This project MUST apply agentic-mbse's design-choice pattern, which this entry does not restate", where A6 said "applies … without restating it". A requirement entry keeps its modal force; this is the same present-tense slip M3 fixed in the pattern.
