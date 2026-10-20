Implement **Phases 6 through 11** of `.project/active/l6-subset-profile/plan.md` (EXEC-SUBSET-CONTRACT Item 3), in order, then stop and report. Phases 1–5 are done; read their notes.

Same rules as before (owner boundary: no Item 2, no writes to ~/src/sysml-codegen — export `b5663c07` with `git archive` if Phase 8 needs codegen source; read-only siblings via `git archive`; explicit-path staging only, never the six unrelated working-tree edits; no repo-wide `ruff format`; tick and annotate; outcome-led commits ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).

Specifics:
- Phase 6: commit the recorded `reconstruct_expression` outputs before refactoring; the unchanged-output test must pass after (Item 2's agent depends on this function).
- Phase 8: only the four rows the design lists are lowered under `native`, each in the same commit as its audit row and fixture; everything else keeps today's severity.
- Phase 9: if uv mishandles a `pyproject.toml` with no `[project]` table, stop for an owner decision as the plan says.
- Phase 10: the CLAUDE.md change is the one L6 description line only.
- **Phase 11 stop-and-show:** if any tree (dc3 `808464d`, dc3 `60b44d5`, fusion-tea `f96ad312`) goes from pass to fail between base `ebb3d467` and the branch, stop and report it with the evidence; do not change anything to make it pass. Record expected new String warnings (131 fusion-tea, 30 dc3 `60b44d5`) separately from unexpected changes.

Finish with per-phase outcome, the Phase 11 before/after table (exit, per-level pass/fail, issue counts, wall time, resolved project root), final repository checks against the Phase 1 baseline, any surprise, and the ARTIFACT line (plan.md).
