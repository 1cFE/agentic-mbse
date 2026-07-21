# Design Review: Constraint-Wave Profile Semantics

**Design:** `.project/active/constraint-wave-profile-semantics/design.md`
**Spec:** `.project/active/constraint-wave-profile-semantics/spec.md`
**Review File:** `.project/active/constraint-wave-profile-semantics/design-review.md`
**Date:** 2026-07-19

---

## Fundamental Assessment

**Sound.** The amended design uses the right architecture for both defects. The executable profile
classifies ordering categories and assertion polarity once. The decision carries the positive
predicate and the complementary polarity pair. Codegen verifies provenance, compiles one
polarity-neutral body per true predicate source, and applies each usage's meaning in one shared
finalizer (`design.md:114-128,146-206,292-371`).

This is a necessary correction to the existing flow, not a parallel semantic system. Effective
predicate-source identity already exists in the neutral facts
(`src/agentic_mbse/sysml/constraint_facts.py:83-100`;
`src/agentic_mbse/sysml/constraint_extraction.py:620-638`). The current codegen instead groups by
usage qualified name and compiles the first entry's polarity into the shared function
(`../sysml-codegen/src/sysml_codegen/generation/constraint_catalog.py:46-54`;
`../sysml-codegen/src/sysml_codegen/generation/modules.py:131-173`). D7-D8 correct those two defects
without changing the already-approved profile → lowering → catalog → compiler architecture.

The three findings from the preceding review are resolved. The spec now names candidate-pair
evidence and defers release readiness to Epic Item 8. Resolver evidence now isolates the intended
version conflict with a complete hashed closure and a same-wheelhouse positive control. Candidate
overlays now seal every admitted untracked entry before and after import.

**Stage 0 verdict:** The approach is sound. Proceed with the detailed review.

---

## Prior Review Verification

| Prior issue | Fresh verification | Status |
|---|---|---|
| M1 — candidate evidence weakened the released-pair criterion | The amended spec now requires a hashed, versioned corrected candidate pair and assigns release-readiness certification to Epic Item 8 (`spec.md:133-139,186-192`). D9 uses the same boundary and does not call the unpublished artifacts releases (`design.md:192-197`). | Resolved |
| M2 — sparse wheelhouse could prove the wrong resolver failure | The compatibility seam requires one immutable wheelhouse with the complete direct and transitive closure, normalized identities and hashes for every selectable wheel, no indexes or editable sources, and pinned hashed inputs (`design.md:632-638`). The negative test asserts the exact `agentic-mbse>=0.1.2` versus `==0.1.1` conflict and no other missing or unsatisfied package; changing only the companion request to `==0.1.2` must resolve and install from the same wheelhouse (`design.md:642-652`). | Resolved |
| m1 — untracked overlay content was not reproducibly sealed | Every admitted untracked entry is now recorded by normalized relative path, regular-content or symlink-target SHA-256, file type, full mode, and executable mask. Unsafe and special entries are rejected. Source and overlay entries are verified against the same hashed manifest without following symlinks (`design.md:512-525`). | Resolved |

The earlier C1/C2 and M1-M6 architecture findings also remain closed. The amendments do not reopen
mixed-polarity grouping, mutation ordering, decision-state totality, diagnostic cardinality, true
source identity, dirty-tree isolation, or native arithmetic behavior (`design.md:38-60`).

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Pass

- The design implements the full eight-category ordering product and preserves existing numerical
  and exact-unit checks only for the five whitelisted pairs (`design.md:148-156,210-235`;
  `spec.md:79-92`).
- Bool-only polarity is classified before predicate selection. Every executable decision carries
  complementary Boolean values, while the positive source IR stays unchanged
  (`design.md:157-175,237-272`; `spec.md:93-110`).
- The source-to-compiler byte ladder, paired exact-once execution oracle, diagnostic cardinalities,
  consumer inventory, unchanged snapshot shape, and candidate compatibility matrix all have concrete
  design and validation seams (`design.md:274-290,292-428,584-658`; `spec.md:111-147`).
- Capture fidelity is preserved. The design identifies ordering and polarity as owner-ratified agent
  recommendations, and the amended candidate scope remains an `[INFERRED]` correction rather than an
  owner-originated settled requirement (`design.md:33-36`; `spec.md:151-158,186-192`).

### 2. Pattern Consistency

**Assessment:** Pass

The design extends existing public facts, profile decisions, Pydantic constraint/catalog models,
lowering guards, and pre-output validation. It reuses the effective-source identity already captured
by extraction and preserves the existing complementary-pair validation pattern. No competing
semantic route or novel service layer is introduced (`design.md:64-112,274-350`).

### 3. Abstraction Quality

**Assessment:** Pass

Each added abstraction has one load-bearing job. `predicate_source_key` owns reusable positive-body
identity. `constraint_id` owns usage wiring. The neutral body evaluates modeled evidence. The shared
finalizer applies one usage's polarity. `ConstraintGenerationPlan` moves semantic validation before
destructive output setup and prevents emission from regrouping or recompiling (`design.md:309-371`).

### 4. Duplication Avoidance

**Assessment:** Pass

One source-keyed body serves all usages of the same predicate source. One finalizer owns status,
margin sign, zero normalization, and indeterminate handling. Repeated IR at fact, decision, concrete,
catalog, and plan seams is retained only for explicit continuity checks, not as competing execution
logic (`design.md:326-350,441-450`).

### 5. Data Structure Clarity

**Assessment:** Pass

The seven-row `UsageDecision` table defines eligibility, predicate presence, polarity, diagnostics,
and unassessed state exhaustively. Five named constructors and `ValueError`-based validation keep
invalid combinations unrepresentable under normal and optimized Python. The source-key table
separates group-equal body data from per-entry polarity and wiring (`design.md:237-329`).

### 6. Route Safety

**Assessment:** Pass

Fact/decision contradictions fail during lowering before graph extension. Catalog, source-group,
name, input, parse, and compile contradictions fail while building an in-memory plan before output
clear or setup. The design accurately permits earlier extraction and context-building work and does
not overclaim protection from ordinary later filesystem failures (`design.md:292-307,352-371`).

### 7. Bets & Decisions Integrity

**Assessment:** Pass

B1-B4 are claims about the existing facts and pipeline, and each states what fails if false. D1-D11
name concrete rejected alternatives. The riskiest evidence bet is now explicit and testable: every
non-companion requirement must be available from the same hashed wheelhouse, the resolver must name
only the intended companion conflict, and the same pins must succeed when the companion request is
changed to `0.1.2` (`design.md:130-206,546-551,630-656`). No hidden compatibility bet remains.

### 8. Reader Comprehension

**Assessment:** Pass

The overview and core concept state the mental model before the mechanisms. The decision-state,
source-key, precedence, and compatibility tables let a reader distinguish semantic authority,
provenance, reusable body ownership, per-usage interpretation, and evidence scope without inferring
unstated behavior.

---

## Issues by Severity

### Critical

None.

### Major

None.

### Minor

None.

---

## Recommendations

1. Preserve D1-D11 and the existing source-keyed neutral-body architecture unchanged in planning.
2. Carry the complete hashed-wheelhouse negative and positive controls into the plan as one
   inseparable compatibility phase.
3. Carry the sealed untracked-entry manifest into the dirty-worktree setup before importing either
   candidate overlay.

---

## Resolutions

- **M1 — candidate versus release scope.** Resolved by the amended spec and D9. Item 1 proves the
  hashed candidate pair; Epic Item 8 owns release-readiness certification.
- **M2 — resolver-failure causality.** Resolved by the complete immutable wheelhouse, exact conflict
  assertion, no-other-unsatisfied-package check, and same-wheelhouse `0.1.2` positive control.
- **m1 — untracked overlay sealing.** Resolved by the path/hash/type/mode manifest, unsafe-entry
  rejection, before-and-after verification, non-following import, and retained manifest hash.
- **Previously approved semantic architecture.** Remains intact. No finding reopens the total
  ordering classifier, separate decision-carried polarity, positive-IR continuity, source-keyed
  neutral body, per-usage finalizer, diagnostic ordering, or read-only pre-output plan.

---

**Overall:** Approve
**Next Steps:** Proceed to `my-plan` for the coordinated two-repository implementation. Treat D1-D11,
the decision-state and diagnostic tables, the source-keyed neutral-body split, the candidate
compatibility seam, and the sealed-overlay process as the approved design contract. The reviewer did
not edit `design.md` or implement code.
