# Design Review: ExpressionIR — Production Tree, Extraction, Serialization

**Design:** `.project/active/expression-ir/design.md`
**Spec:** `.project/active/expression-ir/spec.md`
**Review File:** `.project/active/expression-ir/design-review.md`
**Date:** 2026-07-12
**Reviewer posture:** skeptical; verified against landed Item 1 code and the S2 probe, not the design's word.

---

## Fundamental Assessment

**Sound.** The design is the right approach, and it is not over-engineered. It adopts an idiom the repo
already ships (`aggregation.py:88-165` — distinct dataclass per node kind joined by a `TypeAlias` union)
and a dispatch S2 already proved (`s2_ir.py:100-162`), inverting only the fallback from "generic operator
node" to "explicit unsupported node." Every new abstraction earns its place: the tagged union exists to
make wrong-kind representation a type error (the whole point of the spec's inversion), the distinct
unit/invocation kinds exist because the spelling-fidelity criterion needs source text and resolved QN as
separate slots, and the single shared `_canonical_json` exists to kill the "silent third representation"
risk. There is no cleverness to cut. Proceed to detailed review.

The design is well-written and does its comprehension job: a reader gets the model (one tree, algebra-is-
the-shape, allowlist-inverts-to-unsupported) before the mechanism.

**But the review found one real defect that will turn the suite red mid-implement**, plus the framing
error that caused it. Both are cheap to fix and neither touches the approach.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design meets every success criterion and carries the spec's provenance faithfully (the `[AGENT]`
namespace override, the `[HARD]` FCE-before-OE ordering, the honest n-ary/invocation bounds all survive).
The allowlist enumeration is complete and correct against the corpus (see Dimension 6).

The one gap is **spec compliance in the literal sense of the spec's own gate**: "agentic-mbse suite green"
makes the migration surface a *defined worklist*. The design's worklist is missing a site (below), so the
gate the spec pins cannot be met by executing the design's list as written.

### 2. Pattern Consistency
**Assessment:** Pass

Follows `aggregation.py`'s node-algebra idiom exactly (distinct dataclasses + union alias), follows Item 1's
`_canonical_json` discipline, follows Item 1's anticipated `expression_ir.py` layout
(`constraint-facts/design.md:199-211`). Import direction stays one-way and acyclic. No new pattern invented
where an existing one fits.

### 3. Abstraction Quality
**Assessment:** Pass

Six nodes, each with a clear single responsibility; the union is the natural join. `UnitAnnotationNode` and
`InvocationNode` as distinct kinds (D3) is the right call — the rejected alternative (operator node with
`operator="["` plus a `UnitFact` on `operand_type`) genuinely overloads `operands[1]` and has no clean home
for the resolved unit. A new developer reads this and understands it.

### 4. Duplication Avoidance
**Assessment:** Pass

D5 (one serialize/parse path exposed bare and embedded, `_canonical_json` defined once in the lower module)
is precisely the anti-duplication decision. `ExpressionFact` is deleted, not left to drift alongside the new
tree (D1). Leaves are reused, not restated.

### 5. Data Structure Clarity
**Assessment:** Concerns

The node schemas are explicit and typed. The concern is the `kind` field's **dual meaning across the
transition**, which the design does not flag and which the migration reasoning gets wrong:

- In the **landed** tree, `ExpressionFact.kind` holds the **SysML metaclass name**
  (`type(expression).__name__` — e.g. `"OperatorExpression"`, `"FeatureReferenceExpression"`,
  `"LiteralRational"`; `constraint_extraction.py:318,345,376`). The production golden bakes these:
  `kind:"FeatureChainExpression"` (4), `kind:"FeatureReferenceExpression"` (52), `kind:"LiteralInteger"`
  (24), `kind:"LiteralRational"` (24), `kind:"OperatorExpression"` (45).
- In the **new** tree, `kind` is the **discriminant** (`"literal"`, `"feature_ref"`, `"operator"`, `"unit"`,
  `"invocation"`, `"unsupported"`).

Same field name, completely different value semantics. Any reader that reads `.kind` for a metaclass name
breaks silently (still an attribute, wrong value). This is the root of the missed migration site below.

### 6. Duplication / Allowlist Completeness (Route Safety)
**Assessment:** Pass

Independently verified the allowlist against the golden. Every operator string the landed extractor actually
emits over the corpus is in the design's operator set:

```
golden operators:  +  <=  ==  >  >=  [  and  not  or
design set:        < <= > >= == != and or not xor implies + - * / ** ^ [
```

All covered; no corpus predicate falls to `UnsupportedNode` unexpectedly. Every metaclass in the corpus
(FeatureChain / FeatureReference / Literal{Integer,Rational} / Operator) routes to a productive node. The
uncovered symbols (`< != * / ** ^ xor implies` and unary minus) are the exact gaps D6's new
`operator_fidelity.sysml` is authored to exercise. The `[`-routes-to-unit and the FCE-before-OE ordering are
both explicit. Fallback (everything else → unsupported) is safe and total. This dimension is genuinely clean.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B1 (compat fields survive)** — verified true against `s2_ir.py`'s compat renderer (`_compile_numeric`/
  `_compile_boolean`, lines 204-249). Every field it consumed survives: operator spelling on `OperatorNode`
  (`^`≠`**` kept distinct), unary-minus arity via `len(operands)==1`, literal `value`/`result_type` on the
  reused `LiteralFact` (int-vs-float repr fidelity is already frozen in the leaf, unchanged), the unit value
  subtree on `UnitAnnotationNode.value`, `unit_text`. Honest bet, holds. *(Note: S2 read `n.value`,
  `operands[0]`; the new tree exposes `literal.value`, `value`. Information survives; Item 13's renderer
  reads different field paths — a code-adaptation for Item 13, not a byte-identity risk. Worth one line so
  Item 13 isn't surprised.)*
- **B2 (attribute names stable → assertions survive)** — **partly false as stated, and this is the defect.**
  `operator`/`operands`/`operand_type`/`reference`/`literal` are preserved in both name *and* value, so
  assertions reading them do survive. But B2 lists `kind` in the same breath, and `kind`'s value is
  repurposed (metaclass name → discriminant). Every `.kind`-reading assertion breaks. The design's own
  Implementation Notes (`:275`) repeat this by listing `kind` among "preserved read-side attribute names so
  existing tree-walking assertions survive." That framing is what let the migration list miss a site.
- **B3 (kind discriminant → total parse)** — sound. `dataclasses.asdict` + dispatch on `kind` in
  `_expression_ir_from_dict` round-trips; `sort_keys=True` makes field order irrelevant to bytes.
- **Hidden bet, correctly surfaced:** the Handoff's "de-risk first" (confirm live SysIDE emits distinct
  enums for `^` vs `**`, and a non-allowlist metaclass for the chosen unsupported construct) is the real
  load-bearing bet, and the design flags it honestly rather than burying it. Good.

### 8. Reader Comprehension
**Assessment:** Pass

Core Concept states the model plainly before mechanism. The one comprehension miss is substantive, not
stylistic: because `kind`'s semantic change is never called out, a reader (and the implementer) is led to
believe `.kind`-reading assertions are safe. Fixing the B2 framing fixes the comprehension gap too.

---

## Issues by Severity

### Critical
- **Missed migration site: `tests/test_sysml/test_constraint_fact_shapes.py:121,123`** — Dimensions 1/5/7.
  These assert `actuals["observed"].value.kind == "FeatureChainExpression"` and
  `actuals["limit"].value.kind == "LiteralRational"` — expression-node `.kind` as a metaclass name. Under the
  new discriminant, `.kind` becomes `"feature_ref"` / `"literal"`, so both assertions fail. This file is the
  one containing `test_production_golden_self_compares`; the design's migration list (Integration Strategy,
  `:311-319`) names only its golden JSON (site 7), not these code assertions. Result: the suite goes red at a
  site the "seven-site" worklist does not cover — the exact failure the design's own probe #1 claims to have
  closed by finding the "+1" (`test_constraint_extraction.py`). The list is itself one short.

  *Fix (mechanical, no information lost):* add `test_constraint_fact_shapes.py` to the migration list and
  rewrite the two assertions against the new shape. The information survives cleanly:
  - chain check → `value.kind == "feature_ref"` **and** `value.reference.chain_segments != []` (chain vs
    plain is carried by `chain_segments`, per the design's own note at `:203`).
  - rational check → `value.kind == "literal"` **and** `value.literal.kind == "LiteralRational"` (the literal
    metaclass moves to `LiteralFact.kind`, per `:202`).

### Major
- **B2 / Implementation-Notes framing of `kind` as a "preserved" name** — Dimensions 5/7/8. `kind` must be
  split out from `operator/operands/operand_type/reference/literal`. Those five are preserved in name and
  value; `kind` is preserved in name only, value repurposed. State explicitly that **every `.kind`-reading
  assertion migrates**. This is the correction that prevents the Critical from recurring (and there may be
  future `.kind` readers; the rule, not the enumeration, is what protects them). Verified today there are
  exactly two such readers repo-wide, both at the site above.

### Minor
- **`_operator_text` is an S2-probe function, not landed code** — Implementation Notes (`:286`) says
  "refactor `_operator_text` so an unmapped enum returns a sentinel." The landed extractor has no
  `_operator_text`; it uses bare `str(operator)` inline (`constraint_extraction.py:366`), which already
  yields clean symbols including `[` (the golden shows `operator:"["`). The plan should treat this as
  *building* the normalize-and-allowlist check, not refactoring an existing function, and decide whether
  normalization goes through an enum map (S2's approach, for operators `str()` may not clean — `xor`,
  `implies`, `^`, `**` were never verified to `str()`-clean in `findings.md`) or stays bare `str()` with a
  membership test. Ties into the de-risk check the design already flags.
- **Unit-node shape churn is expected but should be called out for golden review** — the landed `[` node
  carries `operands=[value, unit_ref]` (verified: `operands[1]` is a `FeatureReferenceExpression` node). The
  new `UnitAnnotationNode` drops `operands[1]` into `unit_text` + resolved `UnitFact`. No test walks
  `unit-node.operands[1]`, so it's safe, but the Potential-Risks "review the diff node-by-node" step should
  name this specific structural drop so the reviewer doesn't read it as an accidental loss.

---

## Recommendations

1. **Add `test_constraint_fact_shapes.py` to the migration surface as an eighth site**, with the two
   `.value.kind` assertions rewritten as above. Update the design's "seven-site" language to eight.
2. **Fix the B2 / Implementation-Notes framing:** separate `kind` (name preserved, value repurposed → all
   `.kind` readers migrate) from the five truly-stable names. Make it a rule, not a count.
3. **Clarify the normalization mechanism** at plan stage (enum-map vs bare `str()`), noting `_operator_text`
   is probe code and folding this into the existing `^`/`**` de-risk live check.
4. **Name the unit-node `operands[1]` drop** in the golden-diff review step.

None of these change the design's approach, abstractions, or decisions. They correct the migration worklist
and the reasoning that undercounted it.

---

## Resolutions

*(To be filled in with the owner. The reviewer does not edit the design.)*

---

**Overall:** Approved-with-must-fixes

Must-fix before implement: (1) add `test_constraint_fact_shapes.py` (2 assertions) to the migration list;
(2) correct the B2/`kind` framing so `.kind` readers are known to migrate. Nice-to-haves: (3) normalization
mechanism clarification; (4) name the unit-node structural drop in the diff review.

**Next Steps:** Once resolutions are recorded, re-run `/_my_design` (or return to the design-agent session)
and point it at this review to incorporate. The reviewer does not edit the design.
