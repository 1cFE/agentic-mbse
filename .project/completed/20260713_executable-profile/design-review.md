# Design Review: Executable Profile — Eligibility Gates and Named Diagnostics

**Design:** `.project/active/executable-profile/design.md`
**Spec:** `.project/active/executable-profile/spec.md`
**Review File:** `.project/active/executable-profile/design-review.md`
**Date:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 3

---

## Fundamental Assessment

**Sound.** The approach is right and not over-built. The profile is a pure decision procedure
over `ConstraintFacts` that returns one of three outcomes per usage, with totality by default-deny
rather than enumeration. That is exactly what the spec asks for, and the design adds no parallel
mechanism: it reuses the landed `OperandTypeFact`/`UnitFact` for all type reasoning, iterates the
landed `facts.usages`, and hands decisions to two existing seams plus one new preflight. Every new
abstraction earns its place — the decision/diagnostic dataclasses (D2) keep the library
license-free, the shared `unit_compatibility` helper (D4) is proven necessary by the golden, and
the module placement (D1) follows the facts, not a consumer.

I verified the design's central claim independently rather than taking its word:

- **The 14-row reproduction is correct.** I re-derived every `equality_cases` row in
  `tests/fixtures/constraint_fact_shapes/golden.json` through the design's equality precedence
  (Implementation Notes) and each returns the golden's `decision`. The tricky rows hold:
  - `quantity_feature_unknown_unit` (dimension known, unit `None`) reaches
    `block_unknown_exact_unit` because both operands are `quantity`, so the "exactly one
    dimensioned quantity" guard is skipped and the "both quantity, any `unit.unit is None`" guard
    fires. Correct.
  - `quantity_same_unit` and `unit_bearing_arithmetic` pass `unit_compatibility` (`ok`) then block
    at step 4 as `block_real_equality_requires_tolerance`. Correct.
  - `integer_real` blocks for equality (step 4, "any is real") but the same operands admit for
    ordering (`unit_compatibility` → `ok`), so promotion poisons equality only. Correct.
  - `enum_incompatible` reaches `block_incompatible_enumerations` at step 5. Correct.

The findings below are precision and totality gaps, not redirection. The design is a trustworthy
contract once the two must-fixes are closed.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design carries the spec's `[HARD]`/`[NEED]`/`[INHERITED]` points faithfully, including the two
that the spec-review escalated to must-fixes: the actuals/feature-chain boundary (Non-Goals + the
`typed_feature_chain_and_literal` admit pin) and default-deny totality. The reason-grade diagnostic
requirement (spec `[HARD]`) maps to I3 and the eleven codes.

The concern is the two `[HARD]` guarantees the design under-covers — the same-IR seam for the
serialized codegen path, and totality over a *missing* predicate — see must-fixes MF1 and MF2.

### 2. Pattern Consistency
**Assessment:** Pass

Reuses `expression_facts`, iterates `facts.usages`, and mirrors the one-way import direction the
landed modules already hold (`executable_profile` reads facts, imports no syside, imports no
validation layer). The L6 replacement preserves the existing `check_*(model) -> list[ValidationIssue]`
shape. No new pattern where an existing one would serve.

### 3. Abstraction Quality
**Assessment:** Pass

Three ordered layers with first-match-wins is the clearest possible framing of a single-outcome
procedure. The `unit_compatibility`/`classify_equality` split is the right seam — the golden proves
`==` and the inequalities share operand facts, so one helper is correct and two would drift.
`PROFILE_SEMANTIC_VERSION` (D8) is a small, justified addition: decisions are code, the fact-schema
version wouldn't move on a behavior change, so a separate pin is what lets the consumer see the change.

### 4. Duplication Avoidance
**Assessment:** Concerns

L4 and L6 will each call `extract_constraint_facts(model)` independently, so a single validation run
extracts constraint facts twice. Not a correctness problem — extraction is deterministic — but worth
a note in the plan (a shared per-run fact cache, or accept the cost as small). Minor.

### 5. Data Structure Clarity
**Assessment:** Pass

`UsageDecision` / `EligibilityDiagnostic` / `ProfileResult` are explicit dataclasses with stated
fields. `PreflightResult` (`ok`, `blocking`, `admitted`, `unassessed`) is a clean codegen surface.
The eleven golden codes plus construct/default-deny codes are named as `REASON_CODES`.

### 6. Route Safety
**Assessment:** Concerns

Default-deny is the right routing posture and the design applies it at the *node* level correctly.
The gap is that two inputs are not "a node with an unadmitted role" — a **None** effective predicate
and a **failed definition lookup** — so the node-level catch-all does not obviously cover them
(MF2). A total procedure must route those explicitly.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1 (eight-value category + `UnitFact` is a sufficient basis) is well-supported — I confirmed all 14
rows resolve from `(category, enumeration, unit)` with no evaluator call. B3 (no true n-ary node) is
honestly graded as latent, not special-cased, and correctly noted as "untested, not broken" if wrong.

B2 is the load-bearing bet and it is real ("the compiler can be made to lower the exact IR the gate
walked"). But the design states B2/D7/I5 in terms of **Python object identity** ("the identical
object... not a copy"), and there is a **hidden bet** underneath it: that preflight and the compiler
run in one process over one `ConstraintFacts` value. Across a serialize/parse boundary — which is
exactly the Item 8 license-free codegen path the spec names — object identity is not just unverifiable,
it is false by construction (two parses = two object graphs). That unstated precondition is MF1.

### 8. Reader Comprehension
**Assessment:** Pass

A tired engineer can read the Core Concept and the three-layer flow once and know what the system
is. The "compiler strip-renders units, so the gate is the only safety net" framing lands the *why*
before the mechanism. Bets carry their "if false" clauses. No coined term blocks the model.

---

## Issues by Severity

### Critical (must address before implementation)

- **MF1 — the same-IR seam rests on in-process object identity without stating the precondition,
  and does not cover the serialized codegen path.** [Dim 3/7, probe 3]
- **MF2 — totality gap: a None effective predicate and a failed definition lookup have no named
  outcome.** [Dim 6, probe 2]

### Major (should address)

- **L4 deletion surface is named imprecisely.** [Dim 1/4, probe 4]
- **Preserve the L6 "extraction failure must be loud" discipline through the replacement.** [probe 4]

### Minor (consider addressing)

- Duplicate extraction across L4 and L6 (Dim 4).
- The inventory/unassessed boundary holds by construction but is unstated (probe 6).
- D9 fixture reuse should be pinned as a byte-copy of certified operand facts, not a re-authoring
  (probe 5).
- The layer-2 "comparisons admitted" line should carve out `!=` explicitly (probe 2).

---

## Must-Fix Detail

### MF1 — same-IR seam: object identity needs a stated precondition, and the serialized path needs the serialization-equality contract

**Why this matters.** The spec's `[HARD]` same-IR guarantee (spec lines 211–217) says gate and
compiler must consume the identical `ExpressionIR` — "**the same instance or the same serialized
facts**." The design picked the same-instance arm (D7, I5: "the identical object reachable from
`facts`, not a copy") and explicitly rejected the serialization route as unnecessary.

Object identity is well-defined only under a precondition the design never states: **preflight and
the compiler run in one process, over one `ConstraintFacts` value, and the compiler lowers the exact
objects preflight returned.** The design's mechanism actually enforces that in-process — telling the
compiler to lower `admitted[].effective_predicate` (the objects preflight handed back) does exclude
a second parse for the compiler. So the mechanism is sound *when the precondition holds*.

The hole is the path the spec explicitly names: Item 8's **license-free, snapshot-parsed** codegen
input (`constraint_facts.parse()`). If codegen's architecture is "serialize facts → ship → parse,"
then whether object identity holds depends entirely on *where the parse boundary sits* relative to
preflight. If preflight runs on the codegen side of a single parse, identity holds. If facts are
ever parsed twice (once for preflight, once for compile) or re-serialized between the two calls,
identity is false by construction and the design's I5 assertion becomes vacuous — the exact "gate
reads one IR, compiler reads another" drift the guarantee exists to kill.

**What to change.**
1. State the precondition as a property of the seam: one `ConstraintFacts` value (live-extracted or
   parsed **once**) feeds both preflight and compilation; the compiler lowers the objects preflight
   returned, never a re-derived or re-parsed graph.
2. Name serialization-equality as the contract for the snapshot path, per the spec's own "or the
   same serialized facts." `serialize_expression(effective_predicate)` equality is the check that
   survives a parse boundary; object identity is not. The design already has `serialize_expression`
   in `expression_ir.py` — this is the verifiable form of the guarantee for the license-free path.
3. Keep the `/_my_spike` de-risking (Next-Stage Handoff already calls for it), but point it at the
   right question: not just "does the pre-compile seam exist," but "does one parsed `ConstraintFacts`
   reach both the gate and the compiler, or is there a second parse between them."

This is the brief's hardest probe, and the brief's warning was explicit: the contract "must not rest
on Python object identity across a serialization boundary." As written, I5 does exactly that.

### MF2 — totality: a None effective predicate and a failed definition lookup have no named outcome

**Why this matters.** I1 claims "every `ConstraintUsageFact` receives exactly one eligibility... No
fall-through." Default-deny is stated at the node level: "any construct / operand-category / form /
node-role not on an admit list blocks with a named reason." Two inputs the landed types can produce
are not "a node with an unadmitted role," so the node-level catch-all does not cover them:

1. **A None effective predicate on a form that passed the form gate.** `ConstraintDefinitionFact.predicate`
   is `ExpressionIR | None` (`constraint_facts.py:120`) and `ConstraintUsageFact.predicate` is
   `ExpressionIR | None` (`constraint_facts.py:136`). A `definition_typed` usage typed by a bodyless
   `constraint def Foo;`, or a degenerate inline assert, reaches layer 2 with nothing to walk. The
   form gate does not stop it — it only stops satisfy/require/plain (→ unassessed) and
   `named_usage_reference` (→ block). So `inline`/`definition_typed` with a None body falls through
   the walk.
2. **A `definition_typed` usage whose `constraint_definition.qualified_name` is absent from
   `facts.definitions`.** The design resolves the effective predicate by looking the qn up in a
   `{qn: ConstraintDefinitionFact}` index. A usage typed by an imported or library constraint def
   whose definition was not swept into `facts.definitions` is an index miss. The design does not
   state the miss behavior (KeyError? silent skip? block?).

Both are edge cases, but a "provably total" procedure with an explicit I1 no-fall-through claim must
name them. The fix is small: route both under default-deny with named reasons (e.g.
`block_missing_predicate`, `block_unresolved_definition`), and state that layer-2 entry with a None
predicate or a missing definition is a block, not a walk. Add a unit test for each (neither is in the
golden, matching how `unknown` is covered by a unit test rather than a golden pin).

---

## Nice-to-Haves

- **L4 deletion surface (major-ish precision).** The Component Overview says only
  "`check_constraint_coverage` deleted." The deletion actually spans the caller too: in
  `analyze_constraints` (`level4_constraints.py:131–138`), the `unconstrained, coverage_metrics = ...`
  call and the `unconstrained`→warnings loop go with it. State whether the existing counts
  (`Total constraints`, `ConstraintUsage`, `ConstraintDefinition`, `level4_constraints.py:141–146`)
  survive or are replaced — L4 tests likely assert them.
- **L6 loudness discipline (probe 4).** The current `check_constraint_executability`
  (`level6_architecture.py:608–620`) deliberately removed an `except: constraints = []` swallow so an
  extraction failure is loud, not silently collapsed to zero constraints. The replacement now calls
  `extract_constraint_facts(model)`; keep that failure loud rather than swallowing to "no
  diagnostics." Note it in the plan so the discipline is not lost in the rewrite.
- **Inventory boundary (probe 6).** The concept rule — an unused `ConstraintDefinition` never appears
  as unassessed — is enforced by construction: the profile decisions over `facts.usages` and uses
  `facts.definitions` only as the predicate lookup index, so a def with no usage never becomes a
  `UsageDecision`. Correct, but unstated. One line in I1/Architecture ("definitions are the lookup
  index, never a subject") makes the invariant legible.
- **D9 provenance (probe 5).** Reusing the certified metre/centimetre and integer/real operand facts
  for `inequality_cases` is sound — the operator does not change the operand facts, and the decision
  codes were always a hand-authored answer key (Item 1 excluded `decision` from production facts). To
  keep provenance clean, pin that the reuse is a byte-copy of the certified `equality_cases` operand
  objects, not a hand re-authoring that could drift from what live extraction produces.
- **`!=` carve-out (probe 2).** `!=` is in `_OPERATOR_SYMBOLS` (`constraint_extraction.py:76`), so it
  arrives as a comparison `OperatorNode`, not an `UnsupportedNode`. D5 correctly blocks it as
  `block_unsupported_operator`, but the layer-2 "comparisons are admitted" line reads as if all
  comparisons pass. Add one clause: `!=` is the comparison operator that blocks under default-deny.

---

## Recommendations

1. **Close MF1** — state the single-process/single-parse precondition for the object-identity frame,
   and add serialization-equality as the contract for the Item 8 snapshot path. Point the spike at
   "one parsed facts value reaches both consumers."
2. **Close MF2** — route None-predicate and missing-definition inputs under default-deny with named
   reasons and a unit test each.
3. **Tighten the L4 deletion surface and the L6 loudness note** in the design/plan.
4. Fold the four minors in where cheap; they are one line each.

---

## Resolutions

*Filled in during Stage 4, keyed by finding, when the owner engages. The reviewer records
resolutions here; the design agent incorporates them. The reviewer does not edit the design.*

---

**Overall:** **Approved-with-must-fixes.**

The foundation is correct and I verified it independently: the 14-row reproduction holds for every
row including the tricky ones, default-deny is the right totality frame, the L6 replacement is a
clean whole-body swap, D9 is sound, and the inventory boundary holds by construction. MF1 and MF2
are precision and totality gaps in two `[HARD]` guarantees — the serialized same-IR contract and
no-fall-through — not changes of direction. Close them and this is a trustworthy design contract.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) pointed at this review to incorporate. The reviewer does not edit the design.
