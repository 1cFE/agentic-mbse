# Design Review: Neutral Constraint Facts — Production Schemas and Extraction

**Design:** `.project/active/constraint-facts/design.md`
**Spec:** `.project/active/constraint-facts/spec.md`
**Review File:** `.project/active/constraint-facts/design-review.md`
**Date:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 1
**Reviewer posture:** skeptical; verified against `tests/fixtures/constraint_fact_shapes/{golden.json,source_forms.sysml,type_units.sysml}`, `tests/constraint_fact_learning.py` (the S1 blueprint), and `tests/test_sysml/test_constraint_fact_shapes.py`. Did not take the design's word.

---

## Fundamental Assessment

**Sound.** The core approach is right and I would not rework it. The three-module split
(`expression_facts` → `constraint_facts` → `constraint_extraction`) with one-way imports is the
correct shape, it mirrors the existing `aggregation.py` / `data_models.py` idiom, and the
`@dataclass` choice is confirmed downstream (orchestrator cross-repo evidence: sysml-codegen imports
`agentic_mbse.sysml.data_models` dataclasses today — D1's precedent claim stands, not reviewed
further). Retiring the capture module, keeping the S1 fixtures as the oracle, and the canonical-JSON
byte-stability contract are all the right calls.

The design is not ready to implement against as written. Three structural findings are load-bearing,
and all three are cases where the design **analyzed the wrong axis of a risk it named**:

1. **C1 defends code acyclicity but leaves the *wire version* to churn.** The predicate tree is
   serialized inside the single byte-stable `constraint-facts/v1` section. Item 2 will change the
   tree shape. That forces v2 within the epic — the exact churn the brief flagged. Import direction
   does not solve this.
2. **The dispatch order, read literally, misclassifies `requirement_constraint` as `inline`.** The
   design dropped the `AssertConstraintUsage` type gate that S1's code relies on. Requirement-owned
   constraints own a `result_expression` too, so the "owns a `result_expression` → inline"
   discriminator catches them.
3. **D6's `owning_definition` rule is non-total on the exact case it was invented for.** For
   `direct_owned` (a package-scoped `PartUsage`), there is no enclosing `PartDefinition` — so the
   stated rule returns nothing, and C2's "gives Item 5 the grade in all cases" is false.

None of these is a foundation failure. They are three targeted fixes. Verdict is
**Approved-with-must-fixes**, not Rework.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design carries the spec's provenance faithfully — the four `[HARD]` items (base-`ConstraintUsage`
sweep, owner-filtered formals, `result_expression` discriminator, structural dimension resolution)
all survive as design elements, and the fact/decision split (M1) and the `FeatureDirectionKind`
neutralization (M3) are honored. But two spec requirements are stated without a total mechanism:

- **Structural dimension resolution is asserted, not specified (M-fix-4 below).** The spec makes
  `Unit`-suffix stripping `[HARD]`-banned and requires the dimension resolved "structurally (via
  unit-reference targets and feature typing)." The design's step 5 says only "unit-reference target
  types (m→SI::metre, whose type distinguishes length from mass)." That distinguishes the *category*
  (length vs mass) but does not state the access path that yields the exact dimension QN the golden
  asserts (`"ISQBase::Length"`). The S1 golden contains both `ISQBase::Length` (the dimension, 10×)
  and `ISQBase::LengthUnit` (the unit type, 2×); the banned code produced the former by
  `removesuffix("Unit")` on the latter (`constraint_fact_learning.py:380-381`). The value is
  structurally reachable, but the design must name the path from unit → dimension type, or an
  implementer will re-derive the strip.

- **`owning_definition` totality is claimed but not delivered (see D6 finding).**

### 2. Pattern Consistency
**Assessment:** Pass

The layout, the `@dataclass` algebra, the tagged-union style (`ConstraintSource.form`), and the
`__init__.py` export pattern all match the existing `aggregation.py` / `data_models.py` surface.
Canonical JSON via `json.dumps(sort_keys=True, ...)` over `dataclasses.asdict` is a clean, standard
mechanism. No invented patterns.

### 3. Abstraction Quality
**Assessment:** Concerns

The leaf/predicate/usage layering is the right decomposition. One abstraction claim is overstated:
"**one neutral leaf vocabulary**" and "a **faithful promotion, not a redesign**." S1 actually
produced **two** operand shapes, and the design silently merges them:

- Predicate-node operands in `source_forms` carry `{kind, reference:{resolved, source_name, target,
  target_types}, result_type:<object>, source}` — no `category`, no `enumeration`, no `unit`.
- Equality-case operands in `type_units` carry `{category, enumeration, result_type:<string>,
  source, types:[…], unit:{unit, dimension}}` — no `reference` block, and `result_type` is a flat
  string, not an object.

The design's re-anchor test compares the *production predicate leaves* against S1's *`type_units`
operand facts* (design: "operand category + enumeration + unit/dimension match S1's `type_units`
evidence"). That only works if the production predicate leaf carries `category`/`enumeration`/`unit`
— i.e. the merge is mandatory and central, not incidental. That is fine as a design, but it is a
**schema unification, not a faithful copy**, and the design should own it explicitly and show the
merged leaf carries every field from *both* S1 shapes. See Dimension 5 for the concrete homeless
fields.

### 4. Duplication Avoidance
**Assessment:** Pass

Retiring `tests/constraint_fact_learning.py` (D7) removes the duplicated extraction logic and the two
banned heuristics in one move. Only one importer exists
(`tests/test_sysml/test_constraint_fact_shapes.py:7`), so deletion is clean provided the rewrite is
atomic (that test currently imports `FIXTURE_DIR` and `capture_all_facts` from the deleted module).
The design does not remove the existing type-level `is_droppable_constraint` path, correctly — that
still serves L4/L6.

### 5. Data Structure Clarity
**Assessment:** Concerns

The schema sketch is labelled "representative, not exhaustive," which is acceptable for a design, but
two fields the golden asserts have **no visible home**, and for a contract three repos read as ground
truth that is worth pinning now:

- **Unit/category for a literal-with-unit operand.** `1 [m]` is a literal, so its leaf is a
  `LiteralFact` — but the sketch's `LiteralFact = (kind, value, result_type)` carries no
  `OperandTypeFact`/`UnitFact`. Yet the golden requires that operand to carry `category:"quantity"`
  and `unit:{"SI::metre","ISQBase::Length"}` (`type_units.equality_cases`). The design says "each
  leaf carries its type category… unit/dimension," but the sketch does not show where. State whether
  `OperandTypeFact` hangs off every `ExpressionFact` node (the vague "leaf payload") or only off
  references.
- **`asserted_constraint`.** The golden carries it as a distinct field on every usage
  (`identity`-shaped). The `ConstraintSource` sketch lists `effective_predicate_source`,
  `constraint_definition`, `referenced_feature_target` — but not `asserted_constraint`. It may be
  intentionally derivable/redundant, but say so; otherwise it is a dropped golden field.

The `unit`-as-`{unit, dimension}` two-slot shape with `null` for "dimension known, exact unit
unknown" is well-designed and matches the golden exactly.

### 6. Route Safety
**Assessment:** Fail

This is the classification dispatch, and it is where the design's most load-bearing bet (B1) breaks
as written. See **Must-fix 2**. The `owning_definition` resolver (**Must-fix 3**) is the second
route with an unhandled case. Both are total-function problems: a dispatch/resolution that silently
falls through on real fixture inputs.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are genuine claims with honest "if false" clauses. B1 (structural replacements reproduce
S1's classifications) is the right central bet and the re-anchor test is the right proof. But the
design contains a **hidden bet it does not state**: *that freezing the provisional predicate tree in
`constraint-facts/v1` will not force a version bump when Item 2 lands.* That is the load-bearing
belief under D4 + C1, and it is very likely false (see Must-fix 1). The C1 section argues import
direction — a different, already-safe axis — and never states or defends the wire-stability bet.

D6 is presented as a decision that resolves C2 "in all cases"; it does not (Must-fix 3), so the
decision's stated justification is wrong on its own target case.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept section gives a genuine mental model (one leaf, predicate = tree of operators over
leaves, usage = predicate-in-context tagged with one of six forms) before the mechanism. A tired
engineer can follow it. The one comprehension risk is that "faithful promotion, not a redesign"
(Dimension 3) actively *under-sells* the merge, which could lull the plan stage into treating the
two-shape reconciliation as trivial.

---

## Issues by Severity

### Critical (Must address before implementation)

- **Must-fix 1 — C1 freezes the provisional predicate tree into the byte-stable `v1` wire; Item 2
  forces `v2` within the epic.** [Dim 7, spec Open Question / C1]
- **Must-fix 2 — Dispatch order misclassifies `requirement_constraint` as `inline`; the
  `AssertConstraintUsage` gate is missing.** [Dim 6, B1]
- **Must-fix 3 — D6 `owning_definition` is non-total; it returns nothing for `direct_owned`, the
  case it exists to solve.** [Dim 6, C2]

### Major (Should address)

- **Must-fix 4 — Structural dimension resolution is asserted, not specified; name the unit → dimension
  access path that yields `"ISQBase::Length"` without the banned strip.** [Dim 1]
- **The "one leaf vocabulary" merge is a schema unification, not a faithful copy; own it and show the
  merged leaf carries every field from both S1 operand shapes.** [Dim 3]

### Minor (Consider addressing)

- Homeless golden fields: literal-with-unit operand's `category`/`unit`, and `asserted_constraint`
  on the usage. [Dim 5]
- `allow_nan=False` turns a non-finite operand into a raw `ValueError` inside `serialize()`, not a
  structured extraction diagnostic. The spec wants "reject loudly"; a serialize-time crash is loud
  but unstructured. Prefer detecting non-finite at extraction and emitting a diagnostic.
- Clarify that S1's `golden.json` is preserved as the read-only semantic oracle and the *production*
  golden is a **distinct** artifact byte-compared against itself — the design says both "keep
  golden.json" and "regenerate the production golden," which reads as an overwrite that would destroy
  the oracle.
- The current test file's decision-asserting functions (`test_equality_gate_is_decided_from_static_operand_facts`,
  `test_loader_diagnostics_are_golden_but_not_the_equality_gate`) assert Item 3's `decision` verdicts;
  the rewrite must drop/relocate them, not just re-point the extractor.

---

## Must-Fixes (each with why)

### Must-fix 1 — Isolate the predicate from the byte-stable `v1` version, or accept `v2`-on-Item-2 explicitly

**What the design does.** The predicate is a first-class `ExpressionFact` tree serialized inside the
top-level section under one `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"` (D3: every
field always present; D4: single version; byte-stability invariant covers "any produced fact
section"). The predicate mirrors SysIDE's raw AST: `OperatorExpression`, `FeatureChainExpression`
with operator `"."` and a `target_feature` block, `reference.resolved`, full `target_types` supertype
chains (verified in `golden.json` — `typed_feature_chain_and_literal.actuals[].value` and
`.predicate`).

**Why it's load-bearing.** Item 2 owns `ExpressionIR`, whose node algebra (concept `:87`: literal,
feature reference, operator, invocation, **unit annotation**, **explicit-unsupported**) is richer than
the provisional `(kind, operator, operands)` node and is a *canonical* algebra — by definition not
SysIDE's raw AST. When Item 2 lands, the serialized tree shape changes, which bumps
`constraint-facts/v1 → v2`. If nothing has consumed v1 yet (snapshot v3 is out of scope here), v1 was
a throwaway version, and Item 8's snapshot section — which the concept says embeds these facts — is
invalidated within the same epic. The design's C1 defense is entirely about **import direction /
code acyclicity**, which is already safe and is not the risk. It never addresses **wire-shape
churn**, and "What overturns it" discusses relocating leaf *types* (code), not canonicalizing the
tree *shape* (wire). The design analyzed the wrong axis.

**What to do (pick one, state it):**
- **(a) Version the predicate separately / mark it unstable.** Give the predicate sub-document its
  own `predicate_schema_version`, or explicitly carve the predicate out of the `v1` byte-stability
  guarantee, so the leaf + usage contract Item 3/Item 5 actually consume is stable independent of the
  tree shape Item 2 will canonicalize. Then Item 2 bumps only the predicate sub-version.
- **(b) Serialize leaves-only in `v1`.** The leaf facts (type category, enumeration, unit/dimension,
  reference identity) are what Item 3/5 read and are stable; defer serializing the *tree structure*
  until Item 2 fixes it. Item 1 still builds the in-memory tree for the re-anchor test.
- **(c) Accept and document `v2`-on-Item-2.** State that `v1`'s predicate is provisional, no consumer
  freezes against it, and the first snapshot-consumed version is post-Item-2. Then Item 8 targets that
  version, not `v1`.

Whichever — the design must make the call, because as written it presents `v1` as the stable
cross-repo contract while quietly baking in a shape three items will migrate.

### Must-fix 2 — Restore the `AssertConstraintUsage` type gate in the dispatch order

**What the design says (Architecture step 2).** A flat dispatch: `satisfy` →
`named_usage_reference` (asserted_constraint is not self) → `inline` vs `definition_typed`
(**owns a `result_expression`?**) → `requirement_constraint` (owning membership is
`RequirementConstraintMembership`) → `plain_usage`.

**Why it's wrong.** Read as a linear order, the `result_expression`-ownership test is reached before
the `requirement_constraint` test. But requirement-owned constraints own a `result_expression` too:
`assume constraint positive_limit { checked.limit > 0.0 }` and
`require constraint below_limit { … }` (`source_forms.sysml:11-18`) are inline predicates. So they
match "owns a `result_expression` → inline" and never reach the `requirement_constraint` branch —
yet the golden classifies them as `requirement_constraint`, not `inline`
(`golden.json`: `positive_limit`/`below_limit` → `"source_form":"requirement_constraint"`).

S1's code does **not** have this bug because the whole assert-related discrimination is gated behind
`isinstance(constraint, syside.AssertConstraintUsage)` (`constraint_fact_learning.py:164-177`):
`assume`/`require constraint` are **not** `AssertConstraintUsage` (no `assert` keyword) — they are
`ConstraintUsage`s held by a `RequirementConstraintMembership` — so they fall through the assert
block to the `requirement_constraint` check by *type*, never by `result_expression` ownership.

**What to do.** State explicitly that the `inline`/`definition_typed` discrimination is confined to
the `AssertConstraintUsage`-with-`asserted_constraint is self` branch; non-assert usages fall through
to `requirement_constraint` / `plain_usage` by type. The `result_expression`-ownership discriminator
is the *within-assert* replacement for the banned namespace-prefix test — it is not a
whole-population classifier. Without this, B1's re-anchor fails on two of the six forms.

### Must-fix 3 — Make `owning_definition` total; define it for the package-scoped and non-part owners

**What D6/C2 say.** Add `owning_definition` = "the nearest enclosing
`PartDefinition`/`CalculationDefinition`," and C2: this "gives Item 5 the `owning_part_def_qn` grade
directly **in all cases**," specifically fixing the `direct_owned` case where `owner` is a
`PartUsage`.

**Why it fails on its own target case.** `direct_owned`'s owner is `direct_usage`, and
`direct_usage` is a **package-scoped** `part` (`source_forms.sysml:64` — declared directly in
`package ConstraintFactShapeProbe`, not inside any definition). Walking up from the `PartUsage` owner
reaches the `Package` — there is **no** enclosing `PartDefinition`. So the stated rule returns
nothing for the exact case D6 was invented to resolve. The same gap hits:
- `satisfied_limit` (owner kind `Package`) — no enclosing definition.
- `positive_limit` / `below_limit` (owner kind `RequirementDefinition`) — a `RequirementDefinition`
  is neither a `PartDefinition` nor a `CalculationDefinition`, so the rule as literally worded skips
  it too.

**What to do.** Define `owning_definition` as a total function over all six forms. Decide and state
the answer for a package-scoped root usage: most likely the `PartUsage` itself is the addressable
expansion root, so `owning_definition` = the usage's own identity (kind `PartUsage`), *or* an explicit
`null` with a documented meaning that Item 5 keys on the usage identity directly. Either is
defensible; silence is not. Also state the intended value for `RequirementDefinition`-owned and
`Package`-owned (satisfy) forms — even if the answer is "not applicable / null," it must be explicit,
because D6 adds the field to *every* usage's owner block.

### Must-fix 4 — Specify the structural dimension access path

State the exact path from a unit reference to its dimension QN (e.g. `metre` → its measurement
reference / quantity-kind → `ISQBase::Length`), such that it yields the golden's `dimension` value
**without** any `Unit`-suffix string manipulation. The QN is structurally present in the model
(`ISQBase::Length` appears in the golden independently of `ISQBase::LengthUnit`), so this is
specifiable; leaving it at "distinguishes length from mass" invites the banned strip back in and
leaves B1's dimension-value match unproven at design time.

---

## Nice-to-haves

- **N1 — Own the two-shape merge.** Replace "faithful promotion, not a redesign" with an honest note
  that Item 1 unifies S1's two operand shapes (predicate-node vs equality-case operand) into one leaf,
  and enumerate the merged leaf's fields so the plan stage treats the reconciliation as real work.
- **N2 — Home the two golden fields** (`asserted_constraint`; literal-with-unit `category`/`unit`) in
  the schema, even in a "representative" sketch, since this is a frozen cross-repo contract.
- **N3 — Non-finite handling as a diagnostic, not a `serialize()` crash.** Detect at extraction and
  emit a structured diagnostic; keep `allow_nan=False` as the backstop.
- **N4 — Clarify oracle vs production golden** are two distinct files (S1 `golden.json` preserved
  read-only; production golden regenerated and self-compared).

---

## Resolutions

*(To be filled in as the owner resolves findings; keyed by Must-fix / N number. The design agent
reads this section to incorporate the review — the reviewer does not edit `design.md`.)*

---

**Overall:** Approved-with-must-fixes. The foundation (three-module split, `@dataclass`, canonical
JSON, capture-module retirement, fact/decision split) is right and confirmed. Three structural
must-fixes (predicate wire-versioning, dispatch type-gate, `owning_definition` totality) plus one
under-specified discriminator (dimension path) stand between this design and a safe implementation.
None is a rework; each is a targeted correction on a risk the design named but analyzed on the wrong
axis.

**Next Steps:** Record resolutions above, then return to the design-agent session (or re-run
`/_my_design`) pointed at this review to incorporate. The reviewer does not edit the design. Carry
Must-fix 1's resolution into Item 2's design brief as the adopted predicate-versioning contract, and
Must-fix 3's `owning_definition` totality rule into Item 5's brief.
