Plan EXEC-SUBSET-CONTRACT Item 4 from `.project/active/positional-binding-check/design.md` (revision 1, reviewed; Resolutions in `design-review.md`) and `spec.md`. Output: `.project/active/positional-binding-check/plan.md` with checkbox phases.

Read also `learning-findings.md` and `tests/learning/test_syside_input_redefinition.py` (observed SysIDE 0.8.4 behavior the plan builds on), and `briefs/align.md` (gates; R4-1 decided; owner boundary: do not touch Item 2 or sysml-codegen).

Plan shape:
- Phase 1 settles the plan-phase-1 question the design left (does L1 actually reject `out_before_in`, given L1 reads only parser diagnostics?) and other cheap fixture-truth checks, before code.
- Then: the shared fact and extractor (incl. placeholder detection); the pure check; the pin list (strict parsing, root-only discovery, `--positional-pins-root`, stale vs out-of-scope); the L2 integration (only pinned positional warnings exempt from the pass rule); the reproduction (pin list built from the prototype log, fusion-tea runs 0–2, dc3 zero findings, mutation and stale tests, fusion-tea L2 status measured); the hazard register; guidance edits under invariant I8 with codegen's conformance test run read-only as evidence.
- Each phase ends green as this repo defines it: no new failures versus `main` at `ccd57d83` (record that baseline in phase 1), and every new or modified file clean under ruff check, ruff format --check and mypy. Never run repo-wide `ruff format`.
- Test-first where the design gives fixtures. Name files per phase. State each phase's verifiable done condition traced to spec criteria.
- Premise-surprise rule: if the fusion-tea run differs from the 125 prototype identities, or dc3 is not zero, the implementer stops and surfaces it rather than tuning the detector.
- The fusion-tea pin move consequence stays an owner item (R4-3); the plan produces the evidence, not a fusion-tea change.
