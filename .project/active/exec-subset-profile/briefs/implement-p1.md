Implement **Phase 1 only** of `.project/active/exec-subset-profile/plan.md` (EXEC-SUBSET-CONTRACT Item 1): the probe harness smoke test. Then stop and report.

Read the plan's Settled Inputs, Standing Rules, R2 Surfacing Map and Phase 1 in full, plus the design sections they cite. R1 is decided (design § R1 Decision line).

Rules:
- Never modify ~/src/sysml-codegen or ~/src/dc3. Probes run in isolated temp trees exported with `git archive`. Verify both repos' `git status` is unchanged at the end.
- SysIDE license key is in `.env`.
- Hold the engineering bar: the judge is pure and small; the harness fails loudly on isolation breaches; no silent fallbacks.
- R2: if any smoke probe shows the generator admitting what the rule expected to refuse, stop and report it — do not change the fixture or context to make it pass.
- The plan's Phase 1 risk: if codegen's error lines carry no usable source location, do not weaken the location check — report it.
- Tick Phase 1's checkboxes in plan.md and add implementation notes (deviations, surprises). Commit your work on the current branch with a message whose subject leads with the outcome; end commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Finish with: phase outcome, the four probes' certification results with exact versions, any deviation, and the ARTIFACT line (plan.md).
