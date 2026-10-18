# Product-Lens Ledger — POSITIONAL-BINDING-CHECK (EXEC-SUBSET-CONTRACT Item 4)

Append-only.

## spec — 2026-10-18 — rev unknown (branch `positional-binding-check`, base `bb624d32`) + .project/active/positional-binding-check/spec.md (untracked draft)
Epic: EXEC-SUBSET-CONTRACT

Method note: the lens instruction file (`~/.claude/scripts/product-lens.md`) was unreadable in this non-interactive session, so an independent subagent ran the lens inline, read-only, using the ledger format of `.project/completed/20261018_exec-subset-profile/product-lens.md`. It worked out the point from the sources below before reading the spec's framing. `git rev-parse` was denied to it. No tests, detector runs or scripts were run; prototype counts are recorded evidence, not reproduced.

Epic finding references: none. The epic's Product-Lens section reads "Not yet run". Gates resolve `Epic: EXEC-SUBSET-CONTRACT` against the epic's live gate.

Point (re-derived): a target-repo author who writes correctly named calc or constraint inputs in a different order from the definition gets a silent wrong value, and native SysIDE and the generated/TEAx route disagree on it (-7 vs 7). Nothing warns, and the knowledge has sat in sysml-codegen since July without reaching authors. Item 4 must close that gap in four ways:
- An L2 check that finds unintended implicit name/target mismatches from resolved redefinition evidence, accepts deliberate rename and by-name forms, and never passes when inspection fails.
- The owner's severity policy: new mismatches block, explicitly pinned legacy cases warn until migration, and a legacy warning certifies nothing about cross-route semantic parity.
- Retained fixtures and the cross-route counterexample.
- A hazard register entry and corrected guidance that reach authors.

It must not change how either route binds (R4-2), must not edit fusion-tea (R4-3), and must not describe fusion-tea as clean.

[source: epic Owner decision D1, grade: `[OWNER]` as recorded in `briefs/align.md` ("[OWNER] D1 (approved 2026-10-15) ... Settled"); the epic itself says only "approved by the owner" (see spec-F3). Epic Item 4 scope 1–6 and success criteria, overall success criterion 8, Critical Success Factor ("fusion-tea ... must not be described as clean"), design principles 1, 5 and 6, Prototype findings, grade: INHERITED. Align gates R4-1..R4-3, grade: agent/ratified. Prototype `04-README.md`, grade: INHERITED, feasibility only. `.project/product/` 0001 and `.project/adr/` 0001 cover the Item 1 subset contract only. README and `docs/` state no positional-binding promise. `docs/patterns/plant-idiom.md:298` "Order does not matter" is about a redefine placed after a binding, as the spec says.]

Falsifier: any one of these would show the point violated.
- A reversed unprefixed input that is not pinned passes L2, or a deliberate `in local redefines a` or `in :>> b` is flagged.
- An inspection failure, or zero inputs inspected, yields a clean L2.
- A mismatch that is new after adoption becomes a non-blocking warning without an owner-authorized disposition.
- Any output or doc lets a reader take pinned warnings, or an L2 pass with them, as "values correct" or "routes agree".
- The check or its tests import sysml-codegen, or the item edits fusion-tea or sysml-codegen.

Findings:
- spec-F1 [DON'T] The pin mechanism has no notion of "legacy", so a hand-added pin can downgrade a new mismatch. D1 limits warnings to "explicitly pinned **legacy** cases"; epic scope 1 wants intentional use handled by "a narrow, documented disposition rather than an automatic new baseline entry", and R4-1 reserves any such mechanism to the owner. In use, "new mismatches block" would depend on reviewers reading the pin file. Suggested: require pin provenance and show how later additions are caught, or state that legacy is enforced by review and put that limit to the owner under R4-1. — epic D1 (`[OWNER]` per align); epic Item 4 scope 1 and R4-1 (INHERITED / agent-ratified) — disposition: DISPOSE (surface to owner)
  - **Disposed 2026-10-18:** accepted as routing. Added an `[INFERRED]` requirement that the pin list carries a recorded-against revision and date header, with its limit stated (hand additions are caught only by review), and a malformed-header criterion. The question "is review enough, or should the toolkit verify a digest of the pinned set?" is recorded under R4-1 in Open Questions with a recommendation. Not decided here (R4-1 is reserved).
- spec-F2 [DO] D1's third sentence ("Legacy warning acceptance does not certify cross-route semantic parity") has no criterion. fusion-tea's L2 passes with 125 WARNINGs and nothing a target-repo user sees says those are unverified for value and route parity. — epic D1 (`[OWNER]` per align); Critical Success Factor and Item 4 scope 5 (INHERITED) — disposition: DISPOSE
  - **Disposed 2026-10-18:** accepted. Added a Policy criterion: the pinned-WARNING message and the register entry say a pin certifies neither native values nor route agreement, and the L2 summary reports pinned findings as a separate count; a test asserts both.
- spec-F3 [DON'T] D1 is graded `[OWNER]`, while Item 1 regraded D2 from the same 2026-10-15 discussion to ratified (Item 1 `product-lens.md` spec-F2). The two items should agree. — `.claude/rules/capture-fidelity.md` §1; Item 1 product-lens spec-F2 (agent/ratified) — disposition: DISPOSE
  - **Disposed 2026-10-18:** kept `[OWNER]` as the align record and spec brief state it, and added a note in the D1 requirement pointing at the Item 1 grading for spec review to confirm. The spec does not challenge D1, so the grade does not change any requirement.
- spec-F4 [DO] The inspected-input comparison leaves out fusion-tea (5,573 matching in the prototype), so a scope regression could still reproduce exactly 125 identities. — epic Item 4 scope 2 and principle 5 (INHERITED); `04-README.md` (INHERITED) — disposition: DISPOSE
  - **Disposed 2026-10-18:** accepted. The reproduction criterion now compares fusion-tea's inspected counts (5,573 matching plus 125 mismatches) too.
- spec-F5 [DO] The register ships to target repos, but its citations pointed at this repo's `tests/` and `.project/active/` paths, which do not exist there and move at close. — epic Item 4 scope 4 and Root causes row "Known hazards lacked a reliable route into author guidance"; Item 5 scope 4 (INHERITED) — disposition: DISPOSE
  - **Disposed 2026-10-18:** accepted. Register citations name repository and pinned revision and use post-close `.project/completed/` paths; the shipped-text test checks that form.
- spec-F6 [can't-find] Epic scope 3 asks to record the upstream discrepancy "and its disposition", but no one is named to file the draft or track its disposition. — epic Item 4 scope 3 (INHERITED) — disposition: DISPOSE
  - **Disposed 2026-10-18:** accepted. Filing is the owner's call (or Item 2's); the register says "unfiled" until then, and close lists it as an open item in `CURRENT_WORK.md`.

Smells: smell 1 (a consumer compensating for a producer guarantee) did not fire; the in-repo fusion-tea baseline exists because R4-3 forbids fusion-tea edits, and the spec records the adoption consequence. Smell 7 (ownership change without saying so) did not fire; the spec changes L2's "any issue fails" rule only for pinned `L2_POSITIONAL_BINDING` warnings and says so, citing `level2_structure.py:450` against `types.py:30-38`.

Gate: DISPOSED (spec-F1 routed to owner under R4-1; spec-F2–F6 accepted). No owner/`[HARD]` contradiction, so not BLOCKED. spec-F1 becomes a BLOCK if design adopts a pin mechanism that lets new mismatches warn without an owner R4-1 decision.
