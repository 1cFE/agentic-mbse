# SC4 dry run: checks

Run 2026-10-11 by the orchestrator. One run; no re-run was needed. Pass or fail per line of plan O3.

| Check | Result | Basis |
|---|---|---|
| `goal.md` reads `grounded`, all five field classes filled, grounding evidence cites the fixture | PASS | `goal.md:7-9` (status and the five classes named), § Invariants `:25`, § Grounding evidence `:39` cites `station.sysml` and `drainage.sysml` at `e24e41c`, § Limits `:48`, § Reserved gates `:59` |
| `trail.md` holds `## Round 1`, `### Strategy revision`, `### T-001 scope`, `### T-001 start` | PASS | `trail.md:9,11,21,32` |
| `goal.md` § Invariants names installed pump capacity as a supplied choice the goal preserves | PASS | `goal.md:33`: `pump.installed_flow_capacity` "chosen — installed capacity, supplied by the design"; the agent's summary: it "must never be sized from demand" |
| `read-files.txt` includes `design-choices.md` (B1) | PASS | `read-files.txt:6`, read from the packaged docs before writing any goal file; the brief named neither design choices nor the pattern |
| Docs resolve to the scratch venv's packaged docs (R2-A2) | PASS | the agent's own resolver call (`read-files.txt:5`) and the orchestrator's both printed the packaged path (`install.md`); the agent read the pattern at that path (`:6`) |
| No read path points into the agentic-mbse worktree or at fusion-tea | PASS | `grep -c "agentic-mbse-goal-layer\|fusion" read-files.txt` → 0; same grep over `goal.md` and `trail.md` → no output |

**Also observed.** The agent judged T-001 (add a one-sided fit check) routine under "Process Selection", because it changes no equation, interface or variable role, and recorded that reasoning in the trail. That is the trigger firing narrowly, as MR-7's scope intends. It also left out the learnings template's sample entry so it would not read as an accepted learning. It stopped at `### T-001 start` without a handoff stop.
