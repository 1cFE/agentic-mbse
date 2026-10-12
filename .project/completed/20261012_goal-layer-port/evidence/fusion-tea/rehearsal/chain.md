# SC8: MR-7 enforcement chain on the re-initialized copy

Walked by the orchestrator, 2026-10-12, on a detached copy of fusion-tea `goal-layer-mr7` at `32bd4529a` with F2's step 3 applied and `init` run from this worktree. Every link resolves. None rests on a kept edit to a tool-owned file: `MODELING_PROCESS.md` and the goal files were deleted before `init` and written fresh, and the manifest matches them (`manifest.txt`).

| Link | Resolves to |
|---|---|
| `CLAUDE.md:5` → MR-7 | the anchor `#mr-7-preserve-design-choices-separate-evaluation-from-design-selection`; heading at `modeling_project/REQUIREMENTS.md:87` |
| MR-7 → the pattern | `REQUIREMENTS.md:91` "MUST apply agentic-mbse's design-choice pattern … `design-choices.md` in the installed toolkit's pattern directory" |
| the resolver → `design-choices.md` | `get_docs_dir() / "patterns"` printed `/home/reid/1cfe/agentic-mbse-goal-layer/docs/patterns`, and the file exists. This ran in this worktree's environment: fusion-tea's pin `adbef75` has no `docs/patterns/design-choices.md`, so this shows the chain's shape, and F2 step 5's in-environment check is the real proof |
| MR-7 / the pattern → the review trigger | `modeling_project/MODELING_PROCESS.md:24` ("Process Selection" row), with the clause at `:60` and the point-of-use row at `:76` |
| installed goal template → pattern and requirements | `work/orchestration/goal-templates/goal.md:29` |
| installed runbook → pattern and requirements | `work/orchestration/GOAL_RUNBOOK.md:85` (§ Grounding a goal) |
| installed `run-goal` → pattern and requirements | `.agents/skills/run-goal/SKILL.md:58` |

**Listed, not edited.** fusion-tea `.project/completed/20261011_modeling-intent-enforcement/repair-goal-prompt.md:18` still says `MODELING_PROCESS.md` holds "MR-7 evidence and independent review obligations"; a reader following it lands on the design-choice trigger and rows. It is a completed record (design § Potential Risks).
