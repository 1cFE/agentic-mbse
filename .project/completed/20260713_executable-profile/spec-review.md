# Spec Review: Executable Profile — Eligibility Gates and Named Diagnostics

**Spec:** `.project/active/executable-profile/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/executable-profile/spec-review.md`
**Date:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 3

---

## Reality Check

**Sound.** The spec is about the right work item, its Problem section is accurate to the code
(L4's 0% placeholder at `level4_constraints.py:44-82`; L6's blanket per-constraint WARNING at
`level6_architecture.py:595-642` are both exactly as described), and its inputs are the real
landed types (`constraint_facts.py`, `expression_ir.py`, `expression_facts.py`,
`extract_constraint_facts` at `constraint_extraction.py:113`). I walked all 14 golden equality
rows against the spec's equality gate — every row maps cleanly to the spec's stated decision
(evidence table below). The core is faithful and the equality gate is total over the golden.

The findings below are not about direction. They are about **totality and precision** — the
brief's hardest probe. A profile is a decision procedure that must give exactly one outcome for
every input the landed IR can produce. As written, the procedure is total over the *enumerated*
cases but has no stated behavior for the *un-enumerated* ones, and one collision between two of
its own rules would block the epic's flagship assertion if read literally. Those are must-fixes
because a decision procedure with gaps is not yet a contract.

### Equality-gate evidence (14 golden rows → spec gate)

Every `equality_cases` row in `tests/fixtures/constraint_fact_shapes/golden.json` maps to a
spec decision. Confirmed 1:1:

| Golden row (decision) | Spec gate clause | Maps |
|---|---|---|
| enum_own (`support_enum_same_enumeration`) | same-enumeration admit | ✓ |
| enum_incompatible (`block_incompatible_enumerations`) | different enums block | ✓ |
| integer_real (`block_real_equality_requires_tolerance`) | integer/real promotion block | ✓ |
| integer_integer (`support_integer`) | Integer/Integer admit | ✓ |
| boolean_boolean (`support_boolean`) | Boolean/Boolean admit | ✓ |
| string_string (`support_string`) | String/String admit | ✓ |
| quantity_same_unit (`block_real_equality_requires_tolerance`) | same exact unit, still real-eq, block | ✓ |
| quantity_convertible_unit (`block_unit_conversion_required`) | same dimension diff units block | ✓ |
| quantity_incompatible_dimension (`block_incompatible_dimensions`) | different dimensions block | ✓ |
| unit_bearing_arithmetic (`block_real_equality_requires_tolerance`) | unit-bearing arithmetic operands block | ✓ |
| unitless_dimensioned (`block_unitless_dimensioned`) | unitless-vs-dimensioned block | ✓ |
| quantity_feature_unknown_unit (`block_unknown_exact_unit`) | dimension-known-unit-unknown block | ✓ |
| unresolved_operand (`block_unresolved_operand`) | unresolved operand block | ✓ |
| inherited_alias_type (`block_real_equality_requires_tolerance`) | inherited/aliased real block | ✓ |

The two new inequality pins (`1 [m] <= 100 [cm]` → block; `integer <= real` → admit) are stated
precisely enough, with the correct fact trigger (unit mismatch vs both-dimensionless), and the
reasoning ("promotion poisons only equality, not ordering") is sound.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (credit):** The code-facing claims are true. I checked each: the L4
placeholder (`check_constraint_coverage`, empty `constrained_attrs`), the L6 blanket warning and
its `L6_CONSTRAINT_NON_EXECUTABLE` code, the extraction entrypoint, and every node/field name the
spec cites (`InvocationNode`, `FeatureReferenceNode.chain_segments`, `UnsupportedNode`,
`OperandTypeFact.category`, `UnitFact`, `ConstraintSource.effective_predicate_source`,
`is_negated`, `omitted_default_formals`) all exist as stated. No stale claims.

**L1-2 · Direct claim:** The spec's operand-category vocabulary is incomplete against the landed
type. `OperandTypeFact.category` (`expression_facts.py:56-58`) is one of eight values:
`boolean`, `string`, `integer`, `real`, `enum`, `quantity`, `unresolved`, **`unknown`**. The last
is produced live at `constraint_extraction.py:332` (resolved but no known category matched). The
spec's equality gate and block list name `unresolved` but never name `unknown`. A profile that
enumerates outcomes by category leaves `unknown` with no decision. This is the totality gap in
miniature (see L3-1) and is a faithfulness issue too: the spec describes the input type as if it
had seven categories when the code produces eight.

**L1-3 · Question to the user:** The `[INHERITED]` tags on the equality gate and unit policy cite
"S1 findings §5" and "concept." Those citations are accurate. But the spec's generalization of
the dimension-only block "in every unit-sensitive position (equality AND inequality AND
arithmetic)" is an `[INHERITED: S1]`-tagged claim, while the golden only pins the dimension-only
case (`quantity_feature_unknown_unit`) for **equality**. The generalization to inequality and
arithmetic is a defensible reading of S1's prose note, but it is an *inference*, not a pinned
golden decision. Tag honesty: is the inequality/arithmetic generalization `[INHERITED]` (S1 said
it) or `[INFERRED]` (the spec is extending S1's equality evidence)? S1's §5 note does say "any
unit-sensitive operation," so `[INHERITED]` is arguably fair — flagging only so the grade is a
conscious call, not a default.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (structural ordering):** Success Criterion 5 and the `[HARD]`
enforcement-seam requirement say the preflight "strictly precedes any compilation." This is the
whole point of S2 carry-forward (2): the compiler strip-renders units, so a unit-mismatched
comparison that reaches it compiles to a silent bare-float comparison. The spec states the
*ordering* but not the *structural guarantee that the gate and the compiler see the same
predicate*. The risk is drift between them: if codegen re-derives or transforms facts between
preflight and compile, the gate can pass a predicate the compiler then lowers differently. This
is fine **if** design makes the profile run over the exact `ExpressionIR` that compilation will
consume, in one pass — but a real hole **if** "precedes" is only a call-ordering convention. The
spec should state the guarantee as a property (gate and compiler consume the same IR instance /
same serialized facts), not just an ordering.

**L2-2 · Question to the user (severity):** The Open Question on L4/L6 severity is the highest-
stakes *owner* call in the spec, and it is parked correctly with a recommendation
(loud-but-non-failing WARNING) and a stated blast radius. Two things to confirm before it's
settled: (a) the recommendation is genuinely lossless to flip — because both severities carry the
same construct+location+identity payload, WARNING→ERROR later is a one-field change, which the
spec asserts and I agree with; (b) the blast-radius note says ERROR "would newly fail existing
target-repo models." agentic-mbse cannot see target repos, so that claim is a prediction, not a
verified fact — but it is the right prediction (any model carrying a blocked or not-yet-executable
assertion would newly fail). Within *this* repo, several shipped test fixtures carry `assert
constraint` (`tests/fixtures/expression_ir/operator_fidelity.sysml`,
`tests/fixtures/item4_subtype/`), so the WARNING-keeps-suite-green path is the safe default. This
is a clean deferral; the owner just needs to ratify WARNING vs ERROR-for-target-repos.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix — totality):** The decision procedure is not provably total. The
admit matrix is a whitelist and the block list is a named blacklist, but there is no stated
default for a construct in neither set. Two concrete inputs the landed IR can produce fall through:
- An `OperatorNode` whose `operator` string is none of {comparisons, `and`/`or`/`not`,
  arithmetic, `^`, unary minus, `xor`, `implies`} — e.g. a conditional, a range, a collection op.
  SysIDE can emit these as `OperatorExpression`; the spec's block list names only `xor`/`implies`.
- An operand of category `unknown` (per L1-2).

The spec leans on "silence is never an outcome" as the *principle*, but the *procedure* needs the
matching rule: **any construct/category not in the admit set blocks with a named diagnostic
(default-deny), so totality is by construction, not by enumeration.** Without that clause, a
future SysIDE operator or an `unknown` operand has undefined behavior — exactly the silent gap the
epic exists to kill. State the catch-all explicitly.

**L3-2 · Direct claim (must-fix — the actuals/feature-chain collision):** Two of the spec's own
rules collide on a shape S1 built a fixture for, and the literal reading blocks the epic's
flagship assertion. The `[HARD]` requirement (spec lines 73-74) says the profile "evaluates
eligibility of the actuals and omitted-default formals bound at the usage." The block list (line
128-132) says "feature chains (a `FeatureReferenceNode` with non-empty `chain_segments`)" block.
The golden fixture `typed_feature_chain_and_literal` binds an actual whose value is `sensor.reading`
— a feature chain (golden.json lines 440-500). Read literally: the profile evaluates the actual,
sees a feature chain, and **blocks**.

But the concept's flagship `affordable` usage binds `cost` to a calc output — also a cross-part
reference, resolved to a producer channel at lowering — and S4 *executed* it. If feature-chain
actuals block, the flagship assertion blocks and the epic's acceptance test cannot pass. The
resolution is almost certainly: actual-binding expressions are resolved at lowering (Item 5, a
Non-Goal here) and are **not** subject to the predicate node-kind block list; the profile checks
actuals for resolvability/category, not for predicate-construct eligibility. The spec must say
this outright and pin the `typed_feature_chain_and_literal` decision (admit, with the chain
resolved downstream). As written, "evaluates eligibility of the actuals" + "feature chains block"
is a contradiction two engineers would resolve opposite ways.

**L3-3 · Direct claim (must-fix — diagnostic granularity vs the golden decisions):** Success
Criterion 1 requires every golden row to "receive the profile's matrix decision," and the golden
distinguishes seven block *reasons* (`block_real_equality_requires_tolerance`,
`block_unit_conversion_required`, `block_incompatible_dimensions`, `block_unitless_dimensioned`,
`block_unknown_exact_unit`, `block_unresolved_operand`, `block_incompatible_enumerations`). But the
`[NEED]` on diagnostics (line 133-135) requires only that a diagnostic name the **construct** +
location + identity, and the Open Question parks the diagnostic taxonomy as design detail. The gap:
a real-equality block and a unit-conversion block are both "the `==`/comparison construct" but have
**different authoring fixes** (write a two-inequality band vs make the units match). If the
diagnostic only names the construct, the golden's decision categories are not observable in the
output, and Success Criterion 1 is unverifiable. The spec should require the diagnostic to carry
enough to distinguish the golden's decision categories (at least: real-equality vs
conversion-required vs incompatible-dimension vs unresolved), since these are the outcomes the
success criterion pins — the exact *codes/wording* can stay design detail, but the *distinctions*
cannot.

**L3-4 · Rewrite request (procedure layering):** The decision procedure operates at three levels
that the spec describes separately but never orders: (1) a usage-form/kind gate (satisfy →
unassessed; `named_usage_reference` → block; only inline/definition-typed proceed), (2) a
predicate node-kind walk (block list), (3) operand-fact checks at comparison nodes (equality gate,
unit policy). "Exactly one outcome" depends on the precedence among these — e.g. a
`named_usage_reference` blocks at level 1 even though it has a walkable predicate (golden shows it
resolves one). Ask the spec to state the procedure as ordered layers so the single-outcome
guarantee is legible. This is close to L3-1/L3-2; a short "the procedure runs in this order, first
match wins" paragraph would discharge all three.

**L3-5 · Question to the user (node-kind coverage):** Two IR node kinds have no explicit
treatment. `UnitAnnotationNode` (the `[` node, e.g. `0 [m]`) appears in operand position — is it
handled purely via its operand's `UnitFact` under the unit policy (likely yes), or does it need
its own rule? And a predicate whose root is a bare `FeatureReferenceNode` or `LiteralNode` of
Boolean category (`assert constraint { flag }`) — the admit matrix assumes a comparison/connective
root and never addresses a bare-Boolean-reference predicate. Both are edge cases, but a total
procedure should name them. (Folds into L3-1's default-deny if that clause is written to cover
"any node kind not otherwise handled.")

**L3-6 · If-then tradeoff (cross-repo seam precision):** The preflight-hook contract is specified
well enough on outputs (halts generation, emits nothing partial, non-assert kinds pass as
unassessed) but is imprecise on **input provenance**. The `[HARD]` says the profile "consumes the
production `ConstraintFacts` aggregate produced by `extract_constraint_facts(model)`." At codegen
preflight, though, facts may come from a **snapshot** (Item 8 serializes the fact section;
`constraint_facts.parse()`), not from live extraction — and that path is deliberately license-free
(no SysIDE). This is fine **if** the profile's input type is "a `ConstraintFacts` value" regardless
of origin (which the code supports — `parse()` returns the same aggregate), but the spec ties the
input to the live `extract_constraint_facts(model)` call, which reads as live-only. State that the
profile takes `ConstraintFacts` data (live-extracted or snapshot-parsed), so the codegen wiring is
mechanical and license-free. Also clarify what "pins the agentic-mbse schema/profile version"
means: the fact schema carries `CONSTRAINT_FACTS_SCHEMA_VERSION`, but the *profile's decisions* are
code, not data — is the pin the package version, or a separate profile-semantic version? A future
item relaxing the dimension-only block changes behavior without changing the fact-schema version.

### Lens 4 — Hygiene

None material. The spec is well-structured, tags are mostly honest (one grade to confirm in
L1-3), Non-Goals are crisp, and the Related Artifacts cite real paths.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (minor):** The three-level procedure (L3-4) is the one place a tired
reader has to assemble the decision logic from four separated sections (candidates, admit matrix,
equality gate, unit policy, block list). A single "how a usage flows through the gate" paragraph —
form gate, then predicate walk, then operand checks, first block wins — would let the reader hold
the whole procedure at once. Everything needed is already in the spec; it just isn't in one place.

---

## Engagement Summary

**Overall take:** This is a strong, well-grounded spec — faithful to the concept, accurate to the
code, and total over the 14 golden equality rows I walked. It is not yet a complete decision
procedure: it enumerates outcomes for the cases it lists but states no default for the cases it
doesn't, and one collision between "evaluate the actuals" and "feature chains block" would, read
literally, block the epic's own flagship assertion. Fix the totality clause, the actuals
boundary, and the diagnostic granularity, and I would trust it as the design contract.

**Here's what I need you to weigh in on:**

1. **[L3-2]** The actuals/feature-chain collision — does the eligibility walk descend into
   actual-binding expressions and apply the block list there? Literally, that blocks
   `typed_feature_chain_and_literal` and the flagship `affordable` (chain actual resolved at
   lowering). Confirm actuals are resolvability-checked, not construct-checked, and pin the
   fixture's decision. **Highest stakes — this one touches the acceptance test.**
2. **[L3-1, L1-2]** Totality — add the explicit default-deny clause (any construct/category not in
   the admit set blocks with a named diagnostic), covering un-enumerated `OperatorNode` operators
   and the `unknown` operand category the landed type produces.
3. **[L3-3]** Diagnostic granularity — require the diagnostic to distinguish the golden's block
   *reasons* (real-equality vs conversion vs incompatible-dimension vs unresolved), or Success
   Criterion 1's "matrix decision" is not observable in the output.
4. **[L2-2]** Severity — ratify the parked recommendation (WARNING at L4/L6, hard gate only at
   codegen preflight). It is lossless to flip later; the only open call is whether target repos
   should get ERROR now, at the cost of newly failing existing models.
5. **[L2-1, L3-6]** The two seam questions — (a) a structural guarantee that the gate and compiler
   see the same IR, not just call ordering; (b) the profile input is `ConstraintFacts` data
   (snapshot-parsed too, license-free), not the live model, so the codegen wiring is mechanical.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID, when the owner engages. The reviewer does not edit
the spec; the spec agent incorporates these.*

---

## Must-Fix List (brief format)

1. **L3-2 — actuals/feature-chain collision.** *Why:* literal reading blocks the flagship
   assertion and contradicts S4/acceptance.
2. **L3-1 / L1-2 — totality/default-deny.** *Why:* un-enumerated operators and the `unknown`
   category have no defined outcome; violates "silence is never an outcome" at the procedure level.
3. **L3-3 — diagnostic granularity vs golden decisions.** *Why:* Success Criterion 1 is
   unverifiable if the diagnostic can't distinguish block reasons with different authoring fixes.

## Nice-to-Haves

- **L2-1 / L3-6** — state the gate↔compiler same-IR guarantee and the `ConstraintFacts`-data input
  contract (snapshot-parsed, license-free); clarify what the version pin covers.
- **L3-4 / L5-1** — state the procedure as ordered layers (form gate → predicate walk → operand
  checks, first block wins) in one place.
- **L3-5** — name the treatment of `UnitAnnotationNode` and bare-reference/bare-literal predicates
  (or fold into the default-deny clause).
- **L1-3** — confirm the `[INHERITED]` grade on the inequality/arithmetic generalization of the
  dimension-only block.

---

**Verdict:** **Approved-with-must-fixes** (Revise). The work item is sound and the spec is
faithful; the three must-fixes are precision gaps in the decision procedure, not redirection. Once
L3-1, L3-2, and L3-3 are pinned, this is a trustworthy design contract.

**Next Steps:** Record resolutions in the Resolutions section, then re-run `/_my_spec` (or return
to the spec-agent session) pointed at this review to incorporate. The reviewer does not edit the
spec.
