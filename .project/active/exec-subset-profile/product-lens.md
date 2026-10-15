# Product-Lens Ledger — EXEC-SUBSET-PROFILE (EXEC-SUBSET-CONTRACT Item 1)

Append-only.

## spec — 2026-10-15 — rev c28df85c + .project/active/exec-subset-profile/spec.md (untracked draft)
Epic: EXEC-SUBSET-CONTRACT

Epic finding references: none. The epic's Product-Lens section reads "Not yet run", so there is no epic finding to reference yet. Gates resolve `Epic: EXEC-SUBSET-CONTRACT` against the epic's live gate.

Point (re-derived): Item 1 must create one declared, versioned, evidence-backed contract stating which model shapes the pinned generator admits, refuses, excludes, omits or has not confirmed. The generator, L6 and guidance will all consume that one contract. The constraints on it:
- It lives as neutral agentic-mbse facts and decisions, with no codegen import, and extends `executable_profile` and its `REASON_CODES`.
- It never broadens a current generator refusal without owner review (R2).
- It never turns a detector or scope failure into a clean result.
- It accounts for all 500 candidate sites (D2) and leaves no deferred case without an owner and a stated coverage limit.

[source: `.project/active/exec-subset-profile/briefs/align.md` (Reading, R1–R3, gap handling) and epic Item 1 objective, scope and success criteria plus D2, grade: agent/ratified. Owner "go" ratified the agent reading. D1–D3 are recorded as owner-approved. Nothing shows the owner originated them, so they stay ratified rather than owner-originated. Supporting: `docs/constraint-facts-and-expression-ir.md` (the neutral fact seam between agentic-mbse and sysml-codegen), grade: INHERITED. README and `docs/` state no generator-compatibility promise. `.project/product/` has no INDEX and no entries. `.project/adr/` holds only a README.]

Falsifier: any one of these would show the point violated.
- A shared rule reports `refused` for a shape the pinned generator (`b5663c07`) admits, and no owner R2 decision covers it.
- A rule with a failed extraction or unknown roots yields an empty or clean assessment.
- A candidate site or matrix row exists with no disposition or owner.
- An `agentic_mbse` module imports `sysml_codegen`, or the reason vocabulary contains `ElaborationCode` names.

Findings:
- spec-F1 [DO] Item 1 itself does not show that its new rules leave the generator's existing passing corpus admitted. The guard against broadening refusals (R2) is checked only three ways: a cited generator observation for each refused fixture, the prototype's admitted neighbors, and the one dc3 repaired tree. No criterion runs the evaluator, read-only, over sysml-codegen's existing successfully generating fixtures at `b5663c07`. The epic requires "Existing generating fixtures remain admitted" and "independently accepted near-neighbors remain accepted". ES-012's admitted neighbor has no generator evidence at all. Suggested disposition: add a recorded read-only script run of the evaluator over the codegen generating corpus at `b5663c07`, asserting zero `refused`. — epic Item 1 objective and success criteria, epic overall success criteria, align R2 (agent/ratified) — disposition: DISPOSE
  - **Disposed 2026-10-15:** accepted. Added the success criterion "The generator's passing corpus stays admitted" (zero `refused` over codegen's generating fixtures at `b5663c07`, any exception cited or stopped at R2; it also supplies ES-012's neighbor evidence).
- spec-F2 [DON'T] The spec lists D2 as `[NEED]` under "Settled decisions". Under capture-fidelity, an owner-approved agent recommendation stays `[AGENT] (ratified by owner, 2026-10-15)`. Only owner-originated items are settled. — `.claude/rules/capture-fidelity.md` §1 (agent/ratified) — disposition: DISPOSE
  - **Disposed 2026-10-15:** accepted. D2 regraded to `[INFERRED] (ratified by owner 2026-10-15)`, section renamed "Ratified decisions", with a note that the orchestration brief records D1–D3 as owner decisions. The decision still binds Item 1.
- spec-F3 [can't-find] No durable product statement says the toolkit promises generator compatibility, a contract shared by the generator, L6 and guidance, or the boundary between L6 and codegen. The point exists only in the agent-authored epic and the ratified align record. ADR 0007 is also absent. Suggested disposition: record the capability-policy ownership decision as an ADR at R1; capture the promise as a first `.project/product/` entry at close. — none — disposition: DISPOSE
  - **Disposed 2026-10-15:** accepted as routing. The spec's R1 open question now says the approved decision lands as an ADR and the implemented promise as a `.project/product/` entry at close. No owner/`[HARD]` contradiction; the spec proceeds.

Smells: no smell fired. The matrix-versus-records sync risk (smell 1) is covered by the spec's cross-check test. The spec routes the ownership change (smell 7) explicitly to owner gate R1.

Gate: DISPOSED (spec-F1, spec-F2, spec-F3)

## design_review — 2026-10-15 — rev 9d8a3a3e, `.project/active/exec-subset-profile/design.md`
Epic: EXEC-SUBSET-CONTRACT

Method note: the lens instruction file (`~/.claude/scripts/product-lens.md`) was not readable in this non-interactive session, so the design reviewer ran the lens inline. It re-derived the point from the sources below without using the design's framing.

Epic finding references: none (the epic's Product-Lens section still reads "Not yet run").

Point (re-derived): unchanged from the spec entry above. One versioned, evidence-backed contract of which (shape, context) pairs the pinned generator refuses, admits, excludes, omits or has not confirmed. It lives as neutral agentic-mbse facts and decisions with no codegen import. It never broadens a generator refusal without owner review (R2), never turns a failure into a clean result, and does not duplicate model interpretation. [source: `briefs/align.md` and epic Item 1 objective, grade: agent/ratified. sysml-codegen ADR 0007, grade `[AGENT] (ratified by owner, 2026-07-10)`: model facts in agentic-mbse, and duplicated fact derivation is rejected. ADR 0004, grade `[OWNER]`: occurrences derive from exact evidence; no resolution path forks. ADR 0012, grade `[INHERITED]`: slot construction and multiplicity raw reads keep narrow codegen ownership.]

Falsifier: as in the spec entry, plus: the occurrence structure has two live derivations with no bound on how long both exist or what holds them together.

Findings:
- design-F1 [DON'T] Option A ports codegen's slot construction (`FeatureSlotIndex`) and multiplicity reads into agentic-mbse. sysml-codegen ADR 0012 assigns exactly those to codegen. The design cites only ADR 0007 and does not say it amends 0012. ADR 0004 (owner) is not contradicted, because the port uses exact evidence. — ADR 0012 (INHERITED) — disposition: ESCALATED via smell 7 → design-review M1
- design-F2 [DON'T] The port creates a second occurrence derivation whose end is unbounded ("Item 2 migrates codegen onto it or records why not"). Its summary shape is not what codegen's `OccurrenceIndex` users need, so a migration is not a swap. This works against the epic's "no duplicated model interpretation". — epic Item 1 objective (INHERITED); ADR 0007 rejected alternatives (agent/ratified) — disposition: design-review M2
- design-F3 [DO] Say what the authority is after Item 2. "The generator is ground truth" becomes circular once the generator refuses through the contract. The epic's design principle 3 (screen-bypassed elaboration) is the answer and should be stated. — epic design principle 3 (INHERITED) — disposition: design-review M2(c)

Smells: smell 7 (changes who owns an invariant without saying so) FIRED: design-F1. Escalated into the design review's Fundamental Assessment. The R1 recommendation is held back from the owner until revised. Smell 1 (consumer compensating for a producer guarantee) did not fire: the contract describes the generator's behavior with probe evidence, and Item 2 is scheduled to make the producer consume it.

Gate: ESCALATED (design-F1 via smell 7). No owner/`[HARD]` contradiction, so not BLOCKED. R1 presentation waits on design-review M1 and M2.
