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

## implementation — 2026-10-18 — rev 8b2b3a76 (implementation revision 9b123cf3), `src/agentic_mbse/sysml/subset_*`, `occurrence_*`, `invocation_allowlist.py`, `fact_refs.py`, `reference_use.py` diff 23d9ef32..044e32c1, `evidence/acceptance.md`
Epic: EXEC-SUBSET-CONTRACT

Method note: the lens instruction file (`~/.claude/scripts/product-lens.md`) was again unreadable in this non-interactive session, and Bash was denied. The lens ran inline from file reads only. No tests or scripts were run; the acceptance numbers below are the recorded evidence, not reproduced.

Epic finding references: none (the epic's Product-Lens section still reads "Not yet run").

Point (re-derived): a target-repo author, and the tools that speak to them (L6, guidance, later codegen `check`), needs one versioned answer to "will the pinned generator take this model shape, and how sure are we?" The answer is only useful if each of its three states is honest:
- "refused" means a probe saw the generator refuse it.
- "unknown" (unconfirmed or unverified) is never presented as fine.
- "clean" means clean only over what the contract actually checks, and says so.

[source: epic Item 1 objective and success criteria ("detector failures and incomplete scope cannot produce a clean assessment"; "every deferred case has an owner and coverage limitation"), and design principles 4-6, grade: INHERITED / agent-ratified. ADR 0001, grade `[AGENT] (ratified by owner, 2026-10-18)`: ownership, Option A with end condition (ii), invariants 1-6. README, `docs/` and `.project/product/` still state no generator-compatibility promise; `.project/product/INDEX.md` does not exist.]

Falsifier: the spec entry's four, plus: a consumer that reads only the result object can take `CLEAR` to mean "the generator accepts this model".

What holds in the code:
- Records decide; rules only recognize. The loader refuses any non-`unconfirmed` outcome without probe evidence, and any refused shape without an admitted-context probe or an SA-1 statement (`subset_profile.py:395-473`).
- Missing fact kinds, element failures and narrowed roots all force `INCOMPLETE` (`subset_profile.py:1194-1248`).
- The vocabulary is closed. `SI_*` codes appear only in evidence fields (`subset_profile.py:247`, `:373-376`). The evaluator imports nothing from codegen (`subset_profile.py:26-70`, `occurrence_extraction.py:44-70`).
- No R2: zero `refused` on the 14 snapshot fixtures and on dc3 repaired. Occurrence parity is 73/73 at `9b123cf3` (`evidence/acceptance.md`).
- D2: 502 sites, 0 unaccounted (`evidence/site-reconciliation.md`).

Findings:
- impl-F1 [DO] `CLEAR` does not carry its own coverage limit. The verdict docstring reads "Complete … The only clean verdict" (`subset_profile.py:154-155`), and ADR 0001 invariant 2 repeats "only verdict `CLEAR` is clean". But `ScopeReport` (`subset_profile.py:692-705`) reports only roots and fact kinds. It does not say which matrix rows have no rule: ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, DEEP-QUALIFIED-WIRING, and the 82 explicit follow-up sites. The recorded counterexample is `deep_cross_scope_probe`: the evaluator says `CLEAR` and the generator refuses it (`evidence/acceptance.md`, corpus section). Today the limit lives only in prose for the owner. Item 3 (L6) and Item 5 (guidance) would have to rebuild it from the matrix. That is a consumer compensating for a missing producer guarantee (smell 1, latent: no consumer exists yet). Suggested disposition: have the result name the contract's coverage. Either put the uncovered matrix rows, or a pointer to them pinned by `SUBSET_PROFILE_VERSION`, in `ScopeReport`, or reword the `CLEAR` docstring and ADR 0001's wording to "clean over the implemented rules". Then make Item 3 render that limit next to the verdict. — epic Item 1 success criteria and principle 4 (INHERITED); ADR 0001 invariant 2 (agent/ratified) — disposition: DISPOSE
- impl-F2 [DO] `INCOMPLETE` outranks `REFUSED` in the single verdict (`subset_profile.py:1241-1245`). dc3 baseline has 236 probe-backed refusals, and its headline is "incomplete". Nothing is lost: the findings are all present, and INCOMPLETE is never clean. But a consumer that renders only the verdict softens a certain "the generator will refuse this" into "we couldn't finish". This is the case that matters most to an author with `execution-target = generated`. Suggested disposition: report completeness and the worst outcome as two fields, or let `REFUSED` dominate with completeness alongside. Recording it as an Item 3 rendering obligation is also acceptable. — epic Item 3 scope 3 ("confirmed unsupported capabilities are errors") (INHERITED) — disposition: DISPOSE
- impl-F3 [DO] The ownership change is now stated in agentic-mbse but not yet in the repo that must uphold it. sysml-codegen ADR 0012 still says slot construction and multiplicity reads have "narrow codegen ownership". Its amendment is only a draft (`evidence/adr-0012-amendment-draft.md`), deferred to Item 2. Meanwhile agentic-mbse ships the second reader on this branch, and the CI parity guard does not exist yet. ADR 0001 invariant 6 names the manual parity run as the interim check. A codegen agent changing those reads before Item 2 would still be told by its own ADR that it owns them alone. Suggested disposition: file the 0012 amendment, through the owner or Item 2's first step, at or before this branch merges, not at Item 2's end. Under the ADR README's cross-seam rule, the decision belongs where it is upheld. — `.project/adr/README.md` § Cross-seam placement; ADR 0001 invariant 6 (agent/ratified) — disposition: DISPOSE

Earlier open items, checked against the code:
- design-F1 (ESCALATED via smell 7, ADR 0012 ownership): resolved as an escalation. The owner chose Option A (ii), and ADR 0001 states the ownership change. The residual gap is the unfiled codegen amendment, carried as impl-F3. It is not a BLOCK.
- design-F2 (unbounded second occurrence derivation): resolved. End condition (ii) bounds it with a permanent parity test, and the port's docstring holds itself to the parity seed (`occurrence_extraction.py:1-7`). That test lands in Item 2; until then the recorded run (73/73) is the check.
- design-F3 (authority after Item 2): resolved. ADR 0001 invariant 5 names Item 2's screen-bypassed corpus as ground truth.
- No earlier entry is BLOCKED, so no open BLOCK remains.

Already surfaced, not re-raised: dc3 baseline INCOMPLETE, with B8 reported only as `unconfirmed`; the B3 count (15 here vs T-001's "(20)"), not reconciled; the R3 proposal. All three are open owner items in `CURRENT_WORK.md`.

Smells: smell 1 (consumer compensating for a producer guarantee) fired, latent: impl-F1. Smell 7 (ownership change without saying so): the earlier firing is answered in agentic-mbse; the upholding-repo half is impl-F3.

Gate: OPEN, with impl-F1, impl-F2 and impl-F3 awaiting disposition. No owner or `[HARD]` contradiction, so not BLOCKED. None stops audit. impl-F1 should be disposed before Item 3 consumes the verdict.
