A fresh reviewer produced `.project/active/positional-binding-check/spec-review.md` (verdict: Revise). Read it in full and revise the spec. Record resolutions in the review's Resolutions section with the grade shown.

**Must-fix — accept all three:**
- L1-1 [AGENT]: an input is exempt only when its *own* declaration carries an explicit redefinition accounting for its positional target (as the prototype did). Another input's explicit redefinition never exempts it. Add the mixed-spelling fixture `in b = 3; in :>> a = 10;` (flagged) and a reversed deliberate-rename fixture (not flagged), and state the expected outcomes.
- L2-1 [AGENT]: exclude requirement/case `subject`, `actor` and `stakeholder` parameters (keyword-declared special parameters whose positional redefinition of library parameters is intended). Add one fixture per kind proving no finding. State it as a scoped exclusion with its reason, not a blanket rule for all `in` parameters of those definitions. If an ordinary `in` parameter of a requirement or case def is positionally swapped, it is still in scope.
- L3-1 [AGENT]: the fusion-tea reproduction compares the production check's finding identities against the 125 identities in the prototype's recorded log, not against a pin list built from the check's own output. Itemize any difference; a difference is a premise surprise to surface, not something to tune away.

**Owner questions — the orchestrator decides these as execution of D1, [AGENT]:**
- L2-2: a pinned positional warning does not by itself make L2 fail; that is what D1's "warn" means. Every other L2 code keeps its current pass/fail behavior (the existing `level2_structure.py:450` rule). Remove or correct any claim that the pin move by itself changes fusion-tea's L2 outcome beyond what is verified; say plainly what is unverified (fusion-tea's current L2 status) and that design must measure it.
- L2-3: when only part of a tree is validated, a pin is judged stale only if its owner lies within the validated scope; pins outside scope are counted and reported as out-of-scope, never as stale.

**Should-fix — accept all:** L1-2 grade D1 `[AGENT] (ratified by owner, 2026-10-15)` matching Item 1's D2 grading. L3-2 cite evidence at `.project/active/positional-binding-check/...` paths (close rewrites them). L3-3 the guidance-example criterion asserts no positional finding (and the specific expected findings), not a full L2 pass. L3-4 the unverifiable result must come from a real evidence failure (a fact that cannot be resolved), never from the prototype heuristic; add the valid model on which the prototype misfired as a must-pass fixture.

R4-1 is decided: [AGENT] (ratified by owner 2026-10-18, "A is fine") pin-list integrity rests on review of the pin file; no digest. Record it.

Keep it proportionate and readable. End with a short change list and the ARTIFACT line.
