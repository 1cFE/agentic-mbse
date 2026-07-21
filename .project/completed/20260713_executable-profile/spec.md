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

- [x] Every operand shape in S1's golden equality table (`findings.md` §5, 14 rows) receives
  the profile's matrix decision, **observable through the diagnostic's reason** — each of the
  golden's seven distinct block reasons is distinguishable in the profile's output, not collapsed
  to a bare "construct blocked." The two inequality-unit cases S1 left unpinned are added as
  golden fixtures: `1 [m] <= 100 [cm]` → **block**, `integer <= real` → **admit**.
- [x] L4 no longer reports the 0% attribute-coverage placeholder; it reports executable-assertion
  eligibility instead (how many asserted constraints are executable vs blocked vs unassessed).
- [x] L6's blanket per-constraint "dropped at extraction" WARNING is gone; in its place, each
  ineligible asserted construct produces exactly one named diagnostic that states the construct
  and its source location; a satisfy or require/assume constraint is cataloged unassessed, not
  blocked.
- [x] A model whose assertions use only supported constructs produces **no** eligibility
  diagnostic (silent-on-clean); each blocked construct fires exactly its own named diagnostic
  (loud-on-gap).
- [ ] A codegen preflight hook runs the profile and halts generation — before any compilation —
  when a would-execute assertion is ineligible, emitting the same named diagnostic (construct +
  location + constraint identity). Its contract is specified here; its wiring is a small
  sysml-codegen change this item owns.
- [ ] agentic-mbse suite green; sysml-codegen suite green (both repos).

## Known Requirements

### The profile's input and shape

- **[HARD]** The profile's input is a `ConstraintFacts` **data value** — Item 1's schemas
  carrying Item 2's `ExpressionIR` node algebra, both landed on this branch — regardless of
  origin. It takes the same aggregate whether live-extracted
  (`extract_constraint_facts(model)`, `constraint_extraction.py:113`) or snapshot-parsed
  (`constraint_facts.parse()`). It never reads the live SysIDE model and never invokes the
  evaluator, so the codegen preflight wiring is mechanical and **license-free** (the snapshot
  path deliberately carries no SysIDE dependency — Item 8). Every fact the profile needs
  (operand `category`, enum `enumeration`, `UnitFact` unit/dimension, `chain_segments`,
  `is_negated`, source `form`, actuals, `omitted_default_formals`) is already on those types.
- **[INFERRED]** The profile decides per `ConstraintUsageFact`: **admit** (all constructs in
  its effective predicate are supported and all operands resolve) or **block** (carrying one or
  more named diagnostics), and per non-asserted usage: **cataloged-unassessed**. The exact
  return type (a decision object, a diagnostic list) is design detail; the three outcomes are not.
- **[HARD]** For a definition-typed usage the effective predicate lives on the
  `ConstraintDefinitionFact.predicate`, not the usage; for an inline usage it is the usage's own
  `predicate`. The profile walks whichever the source form designates
  (`ConstraintSource.effective_predicate_source`).

- **[HARD]** *Predicate body vs actual bindings — two different checks.* The construct block
  list (feature chains, invocation, `xor`/`implies`, unit conversion, `UnsupportedNode`) applies
  only to the **predicate expression body** — the tree the profile walks for node-kind
  eligibility. It does **not** apply to an actual's binding expression. An actual is checked for
  **resolvability**, not for predicate-construct eligibility: whether it resolves to a producer
  channel, a design attribute, or a modeled default is Item 5's strict resolver's job
  (resolvable-or-generation-error, a Non-Goal here); the profile only confirms the operand's
  recovered category (for the equality gate / unit policy at the comparison node it feeds). So an
  actual whose value is a feature chain does **not** trip the feature-chain block. Pinned:
  the `typed_feature_chain_and_literal` golden fixture, which binds an actual
  `sensor.reading` (a chain), is **admitted** at the profile level — the chain resolves
  downstream. The motivating shape is the epic's flagship `affordable` usage, which binds `cost`
  to a calc output (a cross-part reference resolved to a producer channel at lowering) and which
  S4 executed; if feature-chain actuals blocked, the acceptance test could not pass.

### The decision procedure: ordered layers, default-deny

- **[NEED]** A usage flows through the gate in three ordered layers, **first block wins**, so
  every input gets exactly one outcome:
  1. **Form/kind gate.** satisfy and require/assume/plain usages → cataloged unassessed (stop);
     `named_usage_reference` (assert-by-reference) → block (stop); only inline and
     definition-typed asserts proceed — even though a `named_usage_reference` has a walkable
     predicate, it blocks here, before the predicate walk.
  2. **Predicate node-kind walk.** Walk the effective predicate body; apply the block list to
     each node.
  3. **Operand-fact checks at comparison nodes.** Apply the equality gate and the unit policy
     using the recovered operand facts.
- **[HARD]** *Default-deny — totality is by construction, not by enumeration.* Any construct or
  operand category **not** in the admit set blocks with a named diagnostic. The admit matrix is
  a whitelist; there is no un-handled fall-through. Two inputs the landed IR can produce that
  this clause explicitly covers, which the enumerated admit/block lists alone would leave
  undefined:
  - an `OperatorNode` whose `operator` is none of the admitted set and not `xor`/`implies` (a
    future or unexpected SysIDE operator — conditional, range, collection op) → **block**;
  - an operand of category **`unknown`** (`OperandTypeFact.category`, produced live at
    `constraint_extraction.py:332` when the result type resolved but matched no known category)
    → **block**. The spec's category vocabulary is the full eight the landed type produces:
    `boolean`, `string`, `integer`, `real`, `enum`, `quantity`, `unresolved`, `unknown`.
  - Any IR node kind with no more specific rule (e.g. a bare-Boolean `FeatureReferenceNode` or
    `LiteralNode` as the whole predicate, or a `UnitAnnotationNode` reached outside a handled
    operand position) falls under default-deny unless design gives it an explicit admit rule.
    `UnitAnnotationNode` in operand position is handled by the unit policy via its
    `operand_type` `UnitFact`; a design that wants to admit a bare-Boolean-reference predicate
    must add it to the admit set explicitly, or it blocks.

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

- **[INHERITED: concept "executable profile" + S1 §5]** In any unit-sensitive operation
  (comparison, inequality, or arithmetic), operands must be **dimensionless** or carry
  **identical, structurally-proven exact units**. Anything requiring a conversion — including
  same-dimension different units — blocks with a named diagnostic, because generated runtime
  values are bare floats and units never convert silently. (The golden pins the dimension-only
  case for equality only; the generalization to inequality/arithmetic is `[INHERITED]` because
  S1 §5 states it in prose — "any unit-sensitive operation" — not `[INFERRED]`. A conscious grade
  call, per the review's L1-3.)
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
- **[HARD]** *Reason-grade diagnostics.* The construct alone is not enough to distinguish the
  block reasons the golden pins, because one construct maps to several reasons with **different
  authoring fixes**: a `==` comparison blocks as `block_real_equality_requires_tolerance` (fix:
  write a two-inequality band) or as `block_unit_conversion_required` (fix: make the units
  match) or as `block_incompatible_dimensions` (fix: correct the model) — same construct, three
  fixes. So each block diagnostic must carry a **reason** distinguishing at least the golden's
  seven block categories: `block_real_equality_requires_tolerance`,
  `block_unit_conversion_required`, `block_incompatible_dimensions`, `block_unitless_dimensioned`,
  `block_unknown_exact_unit`, `block_unresolved_operand`, `block_incompatible_enumerations`. The
  exact codes and wording are design detail; the **distinctions** are not, because Success
  Criterion 1 requires the matrix decision to be observable in the output.

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
- **[HARD]** *Same-IR guarantee, not just ordering.* The gate and the compiler must consume the
  **identical `ExpressionIR`** — the same instance or the same serialized facts — so no
  re-derivation or transformation can slip a predicate past the gate that the compiler then
  lowers differently. "Precedes" is a structural property asserted at the seam (gate and compiler
  read one IR), not merely a call-ordering convention. This closes the drift hole: without it, a
  unit-mismatched comparison could pass a gate reading one IR and reach a compiler reading
  another, then strip-render to a silent bare-float comparison.
- **[HARD]** The profile module and its diagnostic types are owned by **agentic-mbse** (this
  item). sysml-codegen imports and calls them in a small preflight-wiring change this item also
  owns — the cross-repo seam. Per the epic's coordinated-pair discipline, the consumer pins the
  agentic-mbse version. Note for design: `CONSTRAINT_FACTS_SCHEMA_VERSION` versions the fact
  *data*, but the profile's *decisions* are code, not data — a future item relaxing the
  dimension-only block changes behavior without changing the fact-schema version. Design should
  decide whether the pin is the package version or a separate profile-semantic version so a
  behavior change is visible to the consumer.

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

## Decisions (recorded)

These were parked for the owner in the draft; the orchestrator ratified them (agent-grade,
2026-07-12). Recorded here so design treats them as settled, not open.

- **L4/L6 severity → loud, non-failing WARNING.** At codegen preflight the outcome is
  unambiguous — a blocked would-execute assertion **halts generation**. At the L4/L6
  advisory-validation seam the eligibility diagnostics are WARNING severity (loud, with
  construct + location + reason), not level failures. Rationale: advisory validation stays
  advisory; the epic's success criteria need diagnostics to **fire**, not builds to **fail**;
  and ERROR would newly fail existing target-repo models carrying blocked or
  as-yet-unexecutable assertions — and several shipped in-repo fixtures carry `assert constraint`
  (e.g. `tests/fixtures/expression_ir/operator_fidelity.sysml`, `tests/fixtures/item4_subtype/`),
  so WARNING keeps the suite green. Lossless to flip: WARNING→ERROR is a one-field severity
  change on the same construct+location+identity+reason payload, not a redesign. The only
  residual — should target repos opt into ERROR later? — is a future severity toggle, not a
  blocker for this item.

## Open Questions / Deferred to design

- **L4's coverage denominator (design).** Eligibility coverage is naturally
  executable-asserts / total-asserts. Whether L4 also surfaces the unassessed (satisfy,
  require/assume) count as a separate line, and the exact metric labels, is design detail.
- **Diagnostic taxonomy shape (design).** The set of *named* constructs and the seven block
  *reasons* that must be distinguishable are pinned above (reason-grade requirement). Left to
  design: the exact diagnostic codes, `ValidationCode` entries, and message wording — constrained
  only by "names construct + location + identity + a reason distinguishing the golden's seven
  categories."
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
