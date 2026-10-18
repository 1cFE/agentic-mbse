Implement **Phases 5, 6 and 7** of `.project/active/exec-subset-profile/plan.md` (EXEC-SUBSET-CONTRACT Item 1), in order, then stop and report. Phases 1–4 are done (see their implementation notes).

Read the plan's Settled Inputs, Standing Rules (incl. "Green, defined"), R2 Surfacing Map, Phases 5–7 in full, and the design sections they cite (records, invariants, probe certification, Appendix A data model, Appendix C probe list). R1 is decided; SA-1 is accepted.

Rules:
- Never modify ~/src/sysml-codegen or ~/src/dc3; probes run in isolated temp trees through the Phase 1 harness. Verify both repos' `git status` unchanged at the end.
- Records grow only from probes that certified. A refused/excluded/omitted record entry without a certifying probe must fail at load, and the test proving that must exist.
- **R2 (owner gate):** if a probe shows the generator admitting a (shape, context) a rule expected to refuse, run the codegen oracle to rule out a port bug, then stop that rule: leave its entry `unconfirmed`, record the R2 item (probe ID, observation, rule, context) in the plan and in `.project/active/exec-subset-profile/evidence/r2-open.md`, and continue the rules that don't depend on it. Do not narrow the context or change the fixture to make it pass. If the generator refuses where the rule expected admit, correct the record and note it (M5 direction).
- Engineering bar: the evaluator is a pure function of explicit facts and records; closed validated vocabularies; deterministic output; `unverified` never reads as clean; the derived verdict is `CLEAR` only when complete and clean.
- Untracked `.codex/`, `AGENTS.md`, `.project/TRIAGE_MEMORIES.md` in the working tree are not yours: never add or commit them.
- Tick checkboxes with implementation notes per phase; commit per phase or finer, subject leading with the outcome; end each commit with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Finish with per-phase outcome, probe counts (certified / failed / R2), the record entries by outcome, any R2 items, deviations, and the ARTIFACT line (plan.md).
