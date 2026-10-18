Implement **Phases 2, 3 and 4** of `.project/active/exec-subset-profile/plan.md` (EXEC-SUBSET-CONTRACT Item 1), in order, then stop and report. Phase 1 is done (see its implementation notes).

Read the plan's Settled Inputs, Standing Rules — including the new "Green, defined" note — R2 Surfacing Map, and Phases 2–4 in full, plus the design sections and spike F1 material they cite.

Rules:
- Never modify ~/src/sysml-codegen or ~/src/dc3. Oracle captures and codegen test runs happen in isolated temp trees via the Phase 1 harness pattern. Verify both repos' `git status` is unchanged at the end.
- Phase 2: the port is the approved summary port (R1, owner 2026-10-18). Port function by function from the spike; capture every expected.json from codegen's oracle, never hand-write one. If a parity case fails, fix the port to match codegen — do not fix codegen behavior (G1/G2 are mirrored on purpose). If you cannot match a case, stop and report it rather than excluding it.
- Phase 3 edits `reference_use.py`, which codegen consumes. Its observable behavior for codegen must not change: run codegen's test suite in an isolated tree against this agentic-mbse revision before and after the edit, as the plan says, and report both results.
- Engineering bar: pure fact types, closed vocabularies, every abort a named fact failure, deterministic ordering, no duplicated interpretation beyond the approved port. Test-first where the plan gives a stencil.
- Tick each phase's checkboxes in plan.md with implementation notes as you finish it. Commit per phase (or finer), subject leading with the outcome; end each commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Finish with per-phase outcome, parity counts, codegen-suite before/after, any deviation or surprise, and the ARTIFACT line (plan.md).
