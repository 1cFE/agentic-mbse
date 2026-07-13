# Brief: CONSTRAINT-EXEC Item 14 Appendix A — agentic-mbse docs (ready-to-apply)

Process: work synchronously; you MAY commit in this repo (sole writer); NEVER run pytest tests/ -m '' or test_corpus_integration.py [OWNER]. Gate = default suite + ruff. End commits with: Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

- **Design (rev 2, committed):** `.project/active/constraint-migration-acceptance/design.md` ← **all component details, file:line targets, bets, decisions, invariants live here. Do not restate; link.** Key anchors: five-workstream architecture (`design.md#architecture`), the dual carrier surfaces (`design.md#key-decisions` D1), the gain-fix tier (D2), within-v3 removal (D3), the epsilon boundary rule (`design.md#implementation-notes`), retirement grep targets (Appendix B), per-repo doc set (Appendix A).
- **Design review:** `design-review.md` — Approved-with-must-fixes; all three MF and five NTH incorporated into design rev 2 (verified this session).
- **Reference (fusion-tea harness):** `.project/reference/fusion-tea-ife-sweep/FACTS.md` — deletion target `sweep_ife.py:82`, outputs dir, `>`-vs-`>=` boundary hazard. Carries the paths for Appendix C.
- **Memory:** `item3-fusiontea-acceptance-facts` (per-consumer gain key, abs-path parity), `byte-identity-captured-at-churn` (timestamp-only diff gate), `plant-idiom-fixtures`, `verification-matrix-drift-modes`, `syside-license-key-explicit-env-needed`.

---

## Implementation Strategy

### The shape: four repos, one closing item

The design splits into five workstreams across four repos (`design.md#architecture`). This plan groups them into **one in-repo implement session** (sysml-codegen) plus **three cross-repo sessions** the orchestrator sequences. The cross-repo sessions are written as ready-to-apply briefs in Appendices A–C (the Item 3 pattern — those repos are outside this session's sandbox).

**Cross-repo sequencing (the orchestrator's map):**

| Session | Repo | Workstreams | Runs | Depends on |
|---|---|---|---|---|
| **S-CODEGEN** (this plan, Phases 1–5) | sysml-codegen | W1 gain fix, W2 retirement + mapping test, W3a docs, W5a seam | first | Item 13 not mid-commit (write-order only) |
| **S-MBSE** (Appendix A) | agentic-mbse | W3b facts/profile docs | parallel to S-CODEGEN | none |
| **S-TEAX** (Appendix B) | teax | W3c docs, W5b loader seal wiring, W5c tracking-key note | parallel to S-CODEGEN | Items 10–12 landed |
Flip this repo's authoring guidance from "constraints are not executable" to teaching the executable profile + block list; add architecture coverage for the new phases; add verification-matrix rows under the register discipline (`design.md` Appendix A).

### Assumption Under Test
The doc surfaces in Appendix A are the complete in-repo set (verified surfaces), and the register-discipline recount (anchor the STATUS column, don't substring-match) reconciles the matrix against `grep -o 'REQ-[A-Z]*-[0-9]*'` over the reference docs.

### Changes Required
**See `design.md` Appendix A (sysml-codegen verified surfaces) and spec Docs requirements.**
- [ ] Flip `docs/architecture/modeling-assumptions.md:400` §8 → teach the executable profile + block list (invocation, conditional, temporal, unit conversion, real-valued equality) and the real-equality → **explicit two-inequality-band** idiom.
- [ ] Update cross-refs: `reference/01-extraction.md:20`, `reference/02-orchestration.md:40`, `verification-matrix.md:228`.
- [ ] Add/extend architecture reference docs: lowering phase, catalog, contracts, evaluator, study layer.
- [ ] `verification-matrix.md`: add rows for the new REQ families (constraint lowering, generation, catalog, contracts, study); **recount index family counts + STATUS from actual table rows** (memory `verification-matrix-drift-modes` — the index counts and missing REQ families are the real drift, not the summary block).

### Validation
- [ ] `grep -rn "not executable" docs/` → only historical/decision-record mentions remain; no authoring guidance still teaches the retired behavior.
- [ ] `grep -o 'REQ-[A-Z]*-[0-9]*' docs/architecture/reference/*.md | sort -u` cross-checks the matrix; every new REQ family has a row.
- [ ] Index family counts + STATUS recounted and consistent (not just the summary block).

**What We Know Works After This Phase:**
This repo's docs teach the built system. (agentic-mbse and teax docs land in S-MBSE / S-TEAX — Appendices A/B.)

---

## Phase 5: W5a — GENERATOR_MISMATCH seam disposition

### Goal
Dispose of the reserved-but-unreachable `GENERATOR_MISMATCH` diagnostic (`contracts/verify.py:24`): either wire a `generator_version` axis so a generator-version mismatch is detectable, or document it as an intentional reserved seam and remove the dead reachability expectation. Record the disposition either way (spec Small Seams).

### Changes Required
**See spec Known Requirements → Small recorded seams (GENERATOR_MISMATCH).**
- [ ] Inspect `contracts/verify.py:24` and its reachability expectation. Decide wire-vs-document.
- [ ] If document-and-remove: remove the dead expectation, add a one-line reserved-seam note (decision-record phrasing, not an instruction to future agents — capture-fidelity Law 3).
- [ ] Record the disposition in the run report.

### Validation
- [ ] The chosen disposition is recorded; if wired, a test exercises the new axis; if documented, the dead expectation is gone and no test asserts unreachable reachability.

**What We Know Works After This Phase:**
The in-repo seam (W5a) is swept. The teax seams (W5b loader seal, W5c tracking-key note) land in S-TEAX (Appendix B).
## Appendix A — S-MBSE brief: agentic-mbse docs (W3b)

**Repo:** `~/1cfe/agentic-mbse` · **Runs:** parallel to S-CODEGEN · **License:** not needed (docs only).

**Task:** Flip the facts/profile authoring-surface docs and add any L4/L6 verification-matrix rows so no agentic-mbse doc still describes the retired "constraints are not executable" behavior.

**Scope (design-best-guess — confirm the exact file set with repo access; `design.md` Appendix A marks these pending access):**
- [ ] The `constraint_extraction` / `constraint_facts` / executable-profile doc(s) — the neutral-facts + profile authoring surface (source of truth mirrored in-repo at `.project/reference/agentic-mbse-landed/`).
- [ ] Any L4/L6 verification-matrix rows for the neutral-facts and profile REQ families, under the register discipline (recount index counts + STATUS from table rows; memory `verification-matrix-drift-modes`).
- [ ] Teach the executable profile + block list (invocation, conditional, temporal, unit conversion, real equality → two-inequality band) where the authoring surface lives.

**Validation:** `grep -rn "not executable" <docs>` → only historical/decision-record mentions; new REQ families cross-check against the matrix.

**Report back:** the exact files touched + matrix deltas, for the Phase-6 reconcile.

---

## Appendix B — S-TEAX brief: teax docs + loader seal wiring + tracking-key note (W3c/W5b/W5c)
