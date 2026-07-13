# Spec: Executable Profile — Eligibility Gates and Named Diagnostics

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** MEDIUM-HIGH
**Branch:** `constraint-exec-epic`
**Epic:** CONSTRAINT-EXEC, Item 3

---

## Problem

A modeled assertion is either something we can execute or something we can't, and today
agentic-mbse cannot tell the two apart. Two seams paper over the gap:

- **L4 constraint coverage** reports a hardcoded 0% (`level4_constraints.py:56-73` —
  `check_constraint_coverage` never parses a predicate, so every attribute reads as
  unconstrained). The number is a placeholder, not a measurement.
- **L6 executability** fires one blanket WARNING per constraint usage — "not executable and
  is dropped at extraction" (`level6_architecture.py:595-642`) — regardless of whether the
  assertion is a simple `cost <= budget` we can run or a `xor` we genuinely can't.

The epic makes supported assertions execute inside the generated forward model. Before any of
that pays off, the toolkit needs the **decision procedure** that says, per construct, whether
an assertion may run — and when it may not, names the exact unsupported construct and where it
is. Without it, downstream lowering (Item 5) and generation (Item 7) have no gate deciding what
reaches them, and the compiler is not a safety net: S2 proved the predicate compiler
strip-renders unit annotations, so a unit-mismatched comparison that reaches it compiles to a
silent bare-float comparison (concept Appendix B, S2 carry-forward (2)).

The governing principle from the concept: **silence is never an outcome for a modeled limit.**
Every asserted predicate must end in exactly one visible place — admitted to run, cataloged as
present-but-unassessed, or blocked with its construct and location named.

## Success Criteria

- [ ] Every operand shape in S1's golden equality table (`findings.md` §5, 14 rows) receives
  the profile's matrix decision, and the two inequality-unit cases S1 left unpinned are added
  as golden fixtures: `1 [m] <= 100 [cm]` → **block**, `integer <= real` → **admit**.
- [ ] L4 no longer reports the 0% attribute-coverage placeholder; it reports executable-assertion
  eligibility instead (how many asserted constraints are executable vs blocked vs unassessed).
- [ ] L6's blanket per-constraint "dropped at extraction" WARNING is gone; in its place, each
  ineligible asserted construct produces exactly one named diagnostic that states the construct
  and its source location; a satisfy or require/assume constraint is cataloged unassessed, not
  blocked.
- [ ] A model whose assertions use only supported constructs produces **no** eligibility
  diagnostic (silent-on-clean); each blocked construct fires exactly its own named diagnostic
  (loud-on-gap).
- [ ] A codegen preflight hook runs the profile and halts generation — before any compilation —
  when a would-execute assertion is ineligible, emitting the same named diagnostic (construct +
  location + constraint identity). Its contract is specified here; its wiring is a small
  sysml-codegen change this item owns.
- [ ] agentic-mbse suite green; sysml-codegen suite green (both repos).

## Known Requirements

### The profile's input and shape

- **[HARD]** The profile consumes the production `ConstraintFacts` aggregate produced by
  `extract_constraint_facts(model)` (`constraint_extraction.py:113`) — Item 1's schemas and
  Item 2's `ExpressionIR` node algebra, both landed on this branch. It does not re-extract and
  does not invoke the SysIDE evaluator; every fact it needs (operand `category`, enum
  `enumeration`, `UnitFact` unit/dimension, `chain_segments`, `is_negated`, source `form`,
  actuals, `omitted_default_formals`) is already on those types.
- **[INFERRED]** The profile decides per `ConstraintUsageFact`: **admit** (all constructs in
  its effective predicate are supported and all operands resolve) or **block** (carrying one or
  more named diagnostics), and per non-asserted usage: **cataloged-unassessed**. The exact
  return type (a decision object, a diagnostic list) is design detail; the three outcomes are not.
- **[HARD]** For a definition-typed usage the effective predicate lives on the
  `ConstraintDefinitionFact.predicate`, not the usage; for an inline usage it is the usage's own
  `predicate`. The profile walks whichever the source form designates
  (`ConstraintSource.effective_predicate_source`) and evaluates eligibility of the actuals and
  omitted-default formals bound at the usage.

### Which usages are candidates to admit

- **[INHERITED: concept "executable profile"]** Only `AssertConstraintUsage` in the **inline**
  and **definition-typed** source forms are candidates to admit. Everything else is not an
  execution:
  - **assert-by-reference** (`form = named_usage_reference`) → **block** with a named diagnostic.
  - **satisfy** (`form = satisfy`) → **cataloged unassessed** (never blocked, never coverage).
  - **require/assume** and plain non-asserted usages (`form = requirement_constraint` /
    `plain_usage`, read from membership kind) → **cataloged unassessed**.
- **[INHERITED: concept]** An unused `ConstraintDefinition` is authoring inventory — it never
  appears as unassessed coverage and is not a profile subject.

### Admit matrix (operator matrix v1)

- **[INHERITED: concept Appendix B, S2 result]** Admitted constructs, in the effective predicate
  of an inline or definition-typed static scalar assertion:
  - comparisons (`<`, `<=`, `>`, `>=`, and equality subject to the equality gate below);
  - Boolean connectives `and`, `or`, `not`;
  - arithmetic in operand position, including unary minus and `^`;
  - negated assertion polarity (`is_negated = true`);
  - operands that are owner-scope references (plain feature references, `chain_segments` empty),
    literals, explicit actuals, or omitted formals carrying a modeled default.

### Equality gate (S1 evidence)

- **[INHERITED: S1 findings §5 golden table]** Equality (`==`) is admitted **only** by proven
  type compatibility, never by guess. Admitted: Boolean/Boolean, String/String,
  Integer/Integer, same-enumeration/same-enumeration. Blocked, each with its named diagnostic:
  different enums; integer/real promotion (real-valued equality); same exact quantity unit
  (still real-valued equality); same dimension different units; different dimensions;
  unit-bearing arithmetic operands; unitless-vs-dimensioned; quantity feature with dimension but
  no exact unit; unresolved operand; inherited/aliased real type.
- **[INHERITED: concept Non-Goals]** Real-valued equality stays blocked because admitting it
  would require inventing a floating-point tolerance, which the concept's Non-Goals forbid. The
  authoring fix is an explicit two-inequality band; the profile only blocks, it does not rewrite.

### Unit policy (applies to inequalities and arithmetic, not only equality)

- **[INHERITED: concept "executable profile" + S1]** In any unit-sensitive operation
  (comparison, inequality, or arithmetic), operands must be **dimensionless** or carry
  **identical, structurally-proven exact units**. Anything requiring a conversion — including
  same-dimension different units — blocks with a named diagnostic, because generated runtime
  values are bare floats and units never convert silently.
- **[INHERITED: S1]** A feature typed only by a quantity kind (e.g. `LengthValue`) proves its
  dimension but not one exact runtime unit (`UnitFact.unit = None, dimension = <set>`). It blocks
  in any unit-sensitive operation until an authoritative structural fact supplies the exact unit.
- **[HARD]** The two S1-unpinned inequality-unit cases become golden fixtures with these
  decisions: `1 [m] <= 100 [cm]` → **block** (conversion required); `integer <= real` → **admit**
  (integer/real promotion poisons only *equality*, not ordering comparisons).

### Block list (named diagnostics)

- **[INHERITED: concept Appendix B, S2 matrix]** These constructs, when they appear in a
  would-execute assertion, block generation with a construct-named diagnostic: assert-by-reference,
  `xor`, `implies`, invocation (`InvocationNode`), feature chains (a `FeatureReferenceNode` with
  non-empty `chain_segments`), and unit conversion. An `UnsupportedNode` in the effective
  predicate blocks, surfacing its carried structural diagnostic.
- **[NEED]** Every block diagnostic names three things: the unsupported **construct**, the
  **source location** (`LocationFact` — the only identity an anonymous assertion has), and the
  **constraint identity**. "Silence is never an outcome" (concept Design Principle 5).

### Enforcement seams

- **[NEED]** L4 (`analyze_constraints`, `level4_constraints.py:85`) reports eligibility-based
  coverage over asserted constraints — replacing the `check_constraint_coverage` 0% placeholder.
- **[NEED]** L6's blanket `check_constraint_executability` WARNING
  (`level6_architecture.py:595`) is replaced by per-construct eligibility diagnostics.
- **[HARD]** The codegen preflight hook runs the profile and **strictly precedes any
  compilation** of a predicate to Python (S2 carry-forward (2): the compiler is not a unit
  safety net). A would-execute assertion carrying any blocked construct halts generation with
  its named diagnostic; generation emits nothing partial. Non-assert kinds pass preflight as
  cataloged-unassessed.
- **[HARD]** The profile module and its diagnostic types are owned by **agentic-mbse** (this
  item). sysml-codegen imports and calls them in a small preflight-wiring change this item also
  owns — the cross-repo seam. Per the epic's coordinated-pair discipline, the consumer pins the
  agentic-mbse schema/profile version.

## Non-Goals

- The predicate compiler itself and Kleene/margin semantics (Item 7).
- Catalog persistence and the two-level `ConstraintCatalog` (Items 5, 7). The profile decides
  eligibility; it does not write the catalog.
- Concrete lowering, actual resolution against the output registry, or ID minting (Item 5). The
  profile reasons over extracted facts, not over resolved channels.
- Resolving where an exact-unit contract for a quantity-typed feature could come from. This item
  **blocks** the dimension-only case; a future item may relax it (see Open Questions).
- Rewriting a blocked predicate (e.g. real-equality → two inequalities). The profile blocks and
  names the fix in the diagnostic; the author rewrites.

## Open Questions / Deferred to design

- **Severity at the agentic-mbse validation seam (design, with an owner check).** At codegen
  preflight the outcome is unambiguous — a blocked would-execute assertion **halts generation**.
  At the L4/L6 advisory-validation seam the failing-vs-non-failing choice is open. Today L6 is
  deliberately WARNING severity so it does not fail the level, and agentic-mbse validation
  describes itself as reporting metrics, not gating. **Recommendation:** keep the L4/L6
  eligibility diagnostics loud-but-non-failing (WARNING with construct + location), so advisory
  validation stays advisory and the *hard* gate is codegen preflight. This satisfies every
  success criterion above, which require a diagnostic to *fire*, not a level to *fail*. The
  residual owner decision — should a blocked construct also fail L4/L6 for target repos? — is
  parked here; flipping it later is a severity change, not a redesign. Note the blast radius:
  making it ERROR would newly fail existing target-repo models that carry blocked or
  as-yet-unexecutable assertions.
- **L4's coverage denominator (design).** Eligibility coverage is naturally
  executable-asserts / total-asserts. Whether L4 also surfaces the unassessed (satisfy,
  require/assume) count as a separate line, and the exact metric labels, is design detail.
- **Diagnostic taxonomy shape (design).** The set of *named* constructs is pinned by the block
  list above; the exact diagnostic codes, `ValidationCode` entries, and message wording are
  design detail, constrained only by "names construct + location + identity."
- **Exact-unit contract source (out of scope; future item).** Where an authoritative exact-unit
  fact could come from for a dimension-only quantity feature is recorded as a decision, not
  scoped here: this item blocks that case. It bites ordinary quantity-typed attributes, though
  not the first-scope models (which use bare Reals).
- **n-ary operator eligibility (design note).** S2 carry-forward (4): live SysIDE emits nested
  binary for infix `and`/`or`/arithmetic, so the IR's n-ary capacity is latent and unexercised.
  The profile should treat an `OperatorNode` uniformly by operator and operand count; no special
  case is needed while true n-ary nodes cannot arise.

---

## Related Artifacts

- **Epic:** `.project/reference/epic_constraint_execution.md` (Item 3)
- **Required Reading:** concept "executable profile" paragraph + Non-Goals + S1/S2 results and
  carry-forwards (`.project/reference/constraint-execution-concept.md`); S2 operator matrix table
  (concept Appendix B); S1 golden equality table
  (`.project/active/spike-constraint-fact-shapes/findings.md` §5).
- **Landed inputs (this branch):** `src/agentic_mbse/sysml/constraint_facts.py` (Item 1),
  `expression_ir.py` + `expression_facts.py` (Item 2), `constraint_extraction.py`
  (`extract_constraint_facts`).
- **Seams to replace:** `src/agentic_mbse/validation/level4_constraints.py` (L4 placeholder),
  `src/agentic_mbse/validation/level6_architecture.py:595` (L6 blanket warning).
- **Design:** `.project/active/executable-profile/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
