Plan EXEC-SUBSET-CONTRACT Item 3 from `.project/active/l6-subset-profile/design.md` (rev 1, reviewed; Resolutions in `design-review.md`) and `spec.md`. Output: `.project/active/l6-subset-profile/plan.md` with checkbox phases.

Read also `spikes/findings.md` and `briefs/align.md` (owner decisions; gate outcomes; owner boundary: no Item 2, no sysml-codegen writes).

Plan shape:
- **Phase 1:** baseline at `ebb3d467` (pytest/mypy/ruff, plus fusion-tea and dc3 `validate --complete` results and fusion-tea wall time from `git archive` copies), then land the shared extraction session alone, with the with/without equality test for every level and one fusion-tea timing. Stop and report if any level's results differ or fusion-tea gets more than 10% slower.
- Then: the settings module (closed keys, shared with the research holdout guard); the pure severity policy with its table test; the runner crash handling and JSON report; L6 consuming the contract (contract first, String handoff, advisories with the extracted `falls_to_text_fallback` and its unchanged-output test); the exception-site fixes; the legacy-check audit dispositions; `init`; docs and CLAUDE.md L6 description line; the Appendix C safeguard as the last phase, with its stop-and-show condition (any tree going from pass to fail goes to the owner before merge).
- Each phase ends green: no new failures versus the Phase 1 baseline; every new or modified file clean under ruff check, ruff format --check and mypy. Never run repo-wide `ruff format`.
- Test-first where the design gives fixtures. Name files per phase. Trace each phase's done condition to spec criteria.
