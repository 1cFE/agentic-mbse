Review `.project/active/exec-subset-profile/design.md` — design for EXEC-SUBSET-CONTRACT Item 1 — against its spec `.project/active/exec-subset-profile/spec.md` (and `spec-review.md` Resolutions), the align record `briefs/align.md` (owner gates R1–R3), and the epic `.project/backlog/epic_executable-subset-contract.md`. Read-only access to ~/src/sysml-codegen (b5663c07, incl. `.project/adr/0007-*.md`) and ~/src/dc3.

Intent [AGENT, ratified by owner 2026-10-15]: one declared contract of which (shape, context) pairs the generator admits, refuses, excludes or omits, with evidence, consumed later by generator, L6 and guidance; Item 1 builds contract, facts, evaluator, inventory and evidence, not consumer wiring.

The design's R1 section will go to the owner for a decision after your review. Review it as the owner's advisor:
- Is Option A (agentic-mbse owns the decision layer, plus a ~500-line port of codegen's occurrence logic into a shared fact, with codegen moving onto it in Item 2) sound? The epic's principle is "no duplicated model interpretation"; the port creates a temporary second copy guarded by a parity check. Is that honest and bounded, or should the boundary be different? Are the rejected alternatives represented fairly, with real costs?
- Does the proposed occurrence port quietly expand Item 1 into Item 2 territory, or touch codegen-observable behavior?
- R2 safety of the record-table/probe mechanism, including the three gaps the design raised (redefined-everywhere calc usages, constructs nested under refused multiplicity, multiplicity attribute).
- Engineering quality: module boundaries, data model, vocabularies, determinism, unverified-result handling, test strategy, probe harness isolation.
- Whether every spec criterion is traceable to a design element.

Do not edit the design. Produce the review artifact with verdict and must-fix / should-fix items. A separate spike (F1, occurrence-port parity) is running in parallel; don't duplicate it.
