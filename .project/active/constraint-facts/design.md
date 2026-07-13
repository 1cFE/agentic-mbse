# Design: Neutral Constraint Facts — Production Schemas and Extraction

**Status:** Draft (revised to incorporate design-review must-fixes)
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** `constraint-exec-epic`
**Epic:** CONSTRAINT-EXEC, Item 1
**Commit at design start:** `ad4e6e2`

---

## Overview

Promote S1's frozen, test-only constraint fact shapes into production schemas and a production
extractor that lives with the neutral SysML semantics in `agentic_mbse.sysml`. The output is a
versioned, byte-stable JSON fact vocabulary that three downstream repos read as ground truth.

## Review Incorporation

This revision discharges the four must-fixes and named minors from
`.project/active/constraint-facts/design-review.md` (verdict: Approved-with-must-fixes). Where the
review left options, the orchestrator chose; those choices are agent-grade and recorded as
`[AGENT] (orchestrator, 2026-07-12)`:

- **MF1 — predicate wire-shape churn.** `[AGENT]` The predicate serializes as a **separately
  versioned sub-document** (`predicate-tree/v0`, provisional) inside the stable `constraint-facts/v1`
  envelope. Item 2 replaces the tree and bumps **only** the sub-version. See D4, D9, C1.
- **MF2 — dispatch order.** Restore S1's proven type/membership-gated ordering; the
  `result_expression` test is confined to the assert branch. See Architecture step 2.
- **MF3 — `owning_definition` totality.** `[AGENT]` Make it a **tagged** owner fact, total over all
  six forms. See D6, C2.
- **MF4 — dimension path.** Specify the structural unit→dimension traversal, with a surfaced finding
  that the golden's `ISQBase::Length` value is a strip artifact, not a real element. See
  Architecture step 5 and the [surfaced premise conflict](#surfaced-mf4-isqbaselength-is-not-a-real-element).
- Minors N1–N4 and the test-rewrite hygiene note are folded into Core Concept, Component Overview,
  Required Invariants, and Validation.

## Related Artifacts

- **Spec (accepted):** `.project/active/constraint-facts/spec.md`
- **Spec review:** `.project/active/constraint-facts/spec-review.md`
- **Concept (binding):** `.project/reference/constraint-execution-concept.md` — "Neutral Constraint
  Facts" (`:85`–`:91`), Required Invariants (`:136`–`:154`).
- **S1 findings:** `.project/active/spike-constraint-fact-shapes/findings.md`
- **S1 artifacts:** `tests/fixtures/constraint_fact_shapes/{source_forms.sysml,type_units.sysml,golden.json}`,
  `tests/test_sysml/test_constraint_fact_shapes.py`, `tests/constraint_fact_learning.py` (to retire).
- **Idiom to mirror:** `src/agentic_mbse/sysml/aggregation.py` (neutral node algebra + extractor),
  `src/agentic_mbse/sysml/data_models.py` (shared `@dataclass` types).

---

## Research Findings

- **The repo already has the exact idiom.** `aggregation.py` is a PUSH-DOWN shared module: a
  `@dataclass` node algebra (`FeatureReferenceNode`, `LiteralNode`, `OperatorNode`,
  `InvocationNode`, `UnsupportedNode`, `NullNode` — `aggregation.py:96-165`), a tagged union
  `AggregationNode` (`:156`), and one extractor `decompose_aggregation_expression`. The concept's
  `ExpressionIR` node algebra (`:87`: literal, feature reference, operator, invocation, unit
  annotation, unsupported) is a near-superset of these nodes. Item 1's leaf vocabulary is the same
  shape with type/unit facts added.
- **Shared neutral-fact types are `@dataclass`, not pydantic.** `data_models.py` (`AttributeInfo`,
  `MultiplicityData`, `RedefinitionData`, `SumTerm`) is `@dataclass` and documents itself as "the
  primary shared type between agentic-mbse and sysml-codegen" (`data_models.py:1-5,30-33`).
  `types.py` uses pydantic, but for validation-result and binding-info types, not the neutral fact
  surface. The precedent for *this* work is `@dataclass`.
- **The S1 capture module is the extraction blueprint minus two banned heuristics.**
  `tests/constraint_fact_learning.py` recovers every fact the golden holds. Its `_source_form`
  (`:164-177`) uses the **banned** namespace-prefix test (`:172`), and `_unit_fact` uses the
  **banned** `Unit`-suffix strip (`:380-381`). Production keeps the access paths, replaces the two
  heuristics with the spec's structural discriminators.
- **Downstream consumes in-memory Python objects today; JSON is the future snapshot v3 wire.** No
  snapshot/manifest emitter exists in agentic-mbse now (spec Open Question). So Item 1 ships typed
  facts plus a serializer; it does not build a host artifact.
- **Cross-repo read limit:** this session cannot read `sysml-codegen`. The schema-tech decision
  rests on in-repo precedent (above) and the spec's statement that both `data_models.py` and
  `types.py` are "imported by downstream packages."

## Core Concept

There is **one neutral leaf vocabulary** and the whole design turns on it. An operand — a feature
reference or a literal — is the same thing whether you call it "the thing Item 3's equality gate
types," "the thing Item 5 resolves to a channel," or "a leaf of Item 2's `ExpressionIR`." So Item 1
freezes that leaf once: each leaf carries its **type category** (Boolean/String/Integer/Real/enum/
quantity), its **enumeration identity** when it is an enum, its **unit/dimension** fact (with
"dimension known, exact unit unknown" as a first-class state), and — for a reference — its
**source name, qualified target, and feature-chain segments, with no role tag**. Everything else is
built on that leaf: a predicate is a tree of operators over leaves; a `ConstraintUsageFact` is one
predicate in a context, tagged with exactly one of six `ConstraintSource` forms.

This is a promotion **with one real unification**, not a pure copy. S1 proved every fact is
structurally recoverable, but it emitted operands in **two different shapes** (N1): predicate-tree
operands in `source_forms` carry `{kind, reference:{resolved, source_name, target, target_types},
result_type:<object>, source}` with no type/unit facts, while equality-case operands in `type_units`
carry `{category, enumeration, result_type:<string>, types, unit:{unit, dimension}}` with no
reference block. Item 1 **merges these into one leaf** that carries every field from both shapes —
this is a schema unification and the central real work, not an incidental rename. Beyond that, Item
1's job is to (1) move the shapes from a test module into `@dataclass` schemas in
`agentic_mbse.sysml`, (2) replace two fixture-coupled heuristics (namespace-prefix classification,
`Unit`-suffix dimension strip) with the principled structural discriminators the spec makes
`[HARD]`, (3) neutralize one library-enum leak at extraction, and (4) serialize to a versioned,
self-consistent byte-stable JSON section. The leaf vocabulary lives in its own module so Item 2's
`ExpressionIR` imports it without a cycle.

## Key Bets

- **B1.** Every fact the golden holds is recoverable by the S1 access paths run as production code —
  the two banned heuristics have structural replacements that produce the *same* classifications on
  the fixtures. *If false → the re-anchored golden diverges from S1's semantic values and the
  "production extraction matches S1" success criterion cannot be met without reintroducing a
  fixture-coupled heuristic.*
- **B2.** The operand leaf facts (type category, enumeration, unit/dimension) are sufficient, as
  *facts*, for Item 3's gate and Item 5's resolver to decide downstream — Item 1 need not compute
  any verdict. *If false → Item 3/5 push decision logic back into Item 1, collapsing the
  fact/decision boundary the spec's Non-Goal draws.*
- **B3.** Walking `owner` up the ownership chain always reaches a definition-or-`Package` scope, so a
  **tagged** `owning_definition` (`kind ∈ {part_def, calc_def, requirement_def, package}`) is total
  over all six forms and gives Item 5 the dispatch grade — including the package-scoped `direct_owned`
  case (`kind=package`, key on the `owner` `PartUsage`). *If false → Item 5 cannot key multiplicity
  expansion for some owner shape and `owning_definition` falls through, the exact non-totality MF3
  fixed.*
- **B4.** `@dataclass` + `json.dumps(sort_keys=True)` gives a byte-stable round-trip and a shape
  downstream can consume, matching the existing shared-type surface. *If false → the wire contract
  needs a different carrier (pydantic/attrs) and downstream deserialization must change.*

## Key Decisions

- **D1. Schema technology: `@dataclass`.** Mirrors `data_models.py`/`aggregation.py`, the neutral
  shared-fact precedent. *Rejected: pydantic `BaseModel` (used in `types.py` for validation results,
  not the neutral fact surface; adds a validation/serialization layer the byte-stable contract
  would then have to pin against pydantic's own JSON quirks). Rejected: a hand-rolled TypedDict/dict
  (loses the typed surface downstream imports today).*
- **D2. Canonical JSON = `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
  allow_nan=False)` over `dataclasses.asdict`.** `sort_keys` makes byte layout independent of
  dataclass field order (survives refactors); compact separators and `ensure_ascii` remove
  whitespace/encoding drift. Float round-trips via Python's round-trip `repr`. *Rejected:
  pretty-printed indent like S1's golden (whitespace is a byte-instability surface and the spec
  explicitly does not require reproducing S1's byte layout).*
- **D2a. Non-finite literals: reject loudly at extraction with a structured diagnostic (N3).**
  Standard JSON has no `NaN`/`Infinity`; carrying a non-finite value losslessly would need a
  non-standard encoding that breaks byte-stability and every downstream parser. Static literal facts
  are authored constants and finite by construction (SysML has no infinity literal), so this is a
  guard, not a common path: if the extractor ever produces a non-finite literal it emits a structured
  extraction diagnostic naming the operand and its source location (concept Principle 5 — block with a
  named diagnostic, never silence). `allow_nan=False` stays as the serialize-time backstop.
  *Rejected: carry non-finite losslessly (no standard-JSON encoding, breaks the wire contract).
  Rejected: rely on the bare `allow_nan=False` `ValueError` alone (loud but unstructured — the review's
  minor).*
- **D3. Every field always present; absence is explicit `null`.** No optional-field omission. Makes
  the round-trip total and the schema a fixed shape. Matches the golden's explicit `null`s
  (`membership_kind: null`, `referenced_feature_target: null`). *Rejected: omit-when-None (two byte
  forms for one fact; a moving contract).*
- **D4. Two-level version scheme: a stable envelope version and a provisional predicate sub-version.**
  `[AGENT] (orchestrator, 2026-07-12)`. The serialized section carries `schema_version =
  CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"` (the envelope: leaf facts, usage facts,
  owner/actual/context facts — the surface Item 3 and Item 5 consume). Each predicate tree carries its
  own `predicate_schema_version = PREDICATE_TREE_SCHEMA_VERSION = "predicate-tree/v0"` (the
  provisional tree shape). Both are single module constants. The envelope bumps on a breaking change
  to a leaf/usage/owner field; the predicate sub-version bumps independently when Item 2 lands its
  canonical `ExpressionIR`. This keeps the cross-repo contract Item 3/5 read stable at `v1` through
  the epic while being honest that the tree shape finalizes in Item 2. *Rejected: one flat version
  covering the predicate too (freezes a provisional tree into the stable wire; forces `v1→v2` within
  the epic — MF1). Rejected: S1's `constraint-fact-learning-test/v1` tag (test-only, names the retired
  capture path). Rejected: an integer with no namespace (collides with snapshot v3's own version).*
- **D9. Byte-stability is defined per version pair (envelope, predicate sub-version).**
  `[AGENT] (orchestrator, 2026-07-12)`. Round-trip byte-identity is guaranteed at a **pinned**
  `(constraint-facts/v1, predicate-tree/v0)` pair. Cross-sub-version byte-compat (comparing a
  `predicate-tree/v0` section to a future `v1`) is an **explicit non-goal**: Item 2's tree bump is
  allowed to change bytes. Downstream note carried to handoff: **Item 8 pins BOTH versions** when it
  embeds these facts in snapshot v3. *Rejected: a single global byte-stability claim spanning tree
  versions (would forbid Item 2's canonicalization).*
- **D5. Six-form discriminant carried as one `ConstraintSource` on each usage fact.** The spec
  requires "exactly one `ConstraintSource`." It holds `form` (one of the six) plus the
  form-specific pointers (effective-predicate-source identity, `constraint_definition`,
  `referenced_feature_target`). *Rejected: flat sibling fields as in S1's golden (the spec makes the
  single-discriminant explicit, and grouping prevents an illegal combination — e.g. a `satisfy`
  carrying an inline predicate).*
- **D6. Add a resolved, TAGGED `owning_definition` fact to the owner block — total over all six
  forms.** `[AGENT] (orchestrator, 2026-07-12)`. It carries `kind ∈ {part_def, calc_def,
  requirement_def, package}` plus `qualified_name`, resolved by walking the ownership chain from the
  constraint's `owner` to the first enclosing `PartDefinition` / `CalculationDefinition` /
  `RequirementDefinition` / `Package`. A `Package` always terminates the chain, so the function is
  total — it never falls through. A package-scoped direct usage resolves to `kind=package`. Answers
  spec N2 and MF3 — see [Cross-Item Coordination](#cross-item-coordination). *Rejected: "nearest
  enclosing `PartDefinition`/`CalculationDefinition`" (non-total — returns nothing for the
  package-scoped `direct_owned` usage, the `RequirementDefinition`-owned require/assume forms, and the
  `Package`-scoped satisfy, i.e. it fails on the exact cases D6 exists to cover — MF3). Rejected:
  leave Item 5 to derive it from `owner.qualified_name` (a `PartUsage` QN is not a definition QN).*
- **D7. Retire (delete) `tests/constraint_fact_learning.py`; keep the S1 fixtures as the semantic
  oracle; regenerate the production golden from the production extractor.** *Rejected: demote to
  fixture tooling (it embeds the two banned heuristics at `:172` and `:380-381` — keeping it alive
  keeps banned code in the tree and duplicates extraction logic).*
- **D8. Leaf vocabulary in its own module `expression_facts.py`; `constraint_facts.py` imports it;
  Item 2's `ExpressionIR` imports it too.** Import direction is one-way, toward the leaves. See
  [Cross-Item Coordination](#cross-item-coordination).

## Architecture

Three new modules in `src/agentic_mbse/sysml/`, layered so imports point one way:

```
expression_facts.py   leaf + predicate-tree node algebra (no syside, no constraint deps)
        ▲   ▲
        │   └────────────── (Item 2) expression_ir.py  — adopts the leaf vocabulary
        │
constraint_facts.py   ConstraintDefinitionFact / ConstraintUsageFact / ConstraintSource /
        ▲             context + owner + actual + formal facts + serialize(schema_version)
        │
constraint_extraction.py   production extractor: base-ConstraintUsage sweep → classify →
                           facts. Imports syside_adapter + the two schema modules above.
```

**Data flow.** `constraint_extraction.extract_constraint_facts(model)` sweeps the base
`ConstraintUsage` with subtypes (`syside_adapter.py:270`, `include_subtypes=True`), classifies each
into one of six forms, recovers formals/actuals/operand-facts/inheritance, and returns a typed
`ConstraintFacts` aggregate. `constraint_facts.serialize(facts)` renders the canonical JSON section
with `schema_version`. Downstream imports the dataclasses directly (today) or reads the JSON section
(snapshot v3, future/out-of-scope).

**Extraction order and dispatch** (each step's rejected alternative is the banned or SysIDE-broken
path):

1. **Sweep** `elements_of_type(ConstraintUsage, include_subtypes=True)`. *Rejected: an
   `AssertConstraintUsage`-rooted sweep — misses `satisfy` in SysIDE 0.8.4 (`[HARD]`; findings §2).*
2. **Classify — restore S1's type/membership-gated ordering (MF2), re-anchored on
   `constraint_fact_learning.py:164-177`.** The `result_expression`-ownership test is a
   *within-assert* discriminator, **not** a whole-population classifier: `require`/`assume
   constraint` own a `result_expression` too, so a flat "owns `result_expression` → inline" test
   misclassifies them (they are `requirement_constraint` in the golden). The gates keep the branches
   type-disjoint, so the requirement forms are peeled off by membership/type before any
   `result_expression` test is reached:
   1. **Membership gate first:** owning membership is `RequirementConstraintMembership` →
      `requirement_constraint`; kind from `.kind` → `requirement` / `assumption`. (These are
      `ConstraintUsage`s, **not** `AssertConstraintUsage`, held by a requirement membership — S1
      `:175-177`.)
   2. **Assert gate:** `isinstance(AssertConstraintUsage)` (the type gate the flat draft dropped —
      S1 `:167`). Inside it: `asserted_constraint is not self` → `named_usage_reference` (`:169-170`);
      else if the usage owns **no** `result_expression` (its predicate lives on
      `constraint_definition`) → `definition_typed`; else (owns a `result_expression`) → `inline`.
      *Rejected: namespace-prefix test (`:172`) — banned, fixture-coupled; the `result_expression`
      ownership test is its principled `[HARD]` replacement.*
   3. **Satisfy gate:** `isinstance(SatisfyRequirementUsage)` → `satisfy` (`:165`). Position is safe:
      `satisfy` is type-disjoint from the membership and assert gates (not a
      `RequirementConstraintMembership`-held usage, not an `AssertConstraintUsage`), so it reaches this
      gate unclassified — S1 checked it first only out of multiple-inheritance caution, and the
      classification is identical either way.
   4. **Fallback:** `plain_usage` (a non-asserted `ConstraintUsage` serving as a reference target —
      `:177`).
3. **Membership kind** from the owning `RequirementConstraintMembership.kind`, neutralized to
   `requirement`/`assumption`/`null` — read from the membership, never the usage subtype (`[HARD]`).
4. **Formals** by owner-filtered `AttributeUsage` sweep (`owner is definition`); default is an owned
   `FeatureValue` with `is_default = true`. *Rejected: `ConstraintDefinition.parameters` — omits
   user inputs in 0.8.4 (`[HARD]`; findings §2).*
5. **Operand leaf facts** per leaf: category by type conformance; enumeration by the owning
   `EnumerationDefinition`; unit and dimension resolved structurally (MF4, detailed below).
6. **Neutralize library values at extraction:** parameter direction maps
   `syside.FeatureDirectionKind` → `in`/`out`/`inout` token; enum-like values map via `.name.lower()`
   to neutral strings. *Rejected: `str(enum)` — leaks `"FeatureDirectionKind.In"` into the wire
   contract (`[HARD]` M3; golden `direction` is the one such leak).*

### Structural dimension resolution (MF4)

The dimension fact must be a **real, structurally reachable QN with no suffix string manipulation**.
The two banned strips in the S1 capture module both fabricate a QN: `_unit_fact`
(`constraint_fact_learning.py:380-381`) does `removesuffix("Unit")` on the unit type, and
`_operand_fact` (`:431`) does `removesuffix("Value")` on the quantity feature type.

The **dimension identity is the measurement-unit definition QN** — a real element — reached two ways
that converge on the same anchor:

- **Unit-annotation operand** (`1 [m]`): the `[` operator's unit operand `referent` is `SI::metre`;
  its typing chain contains the unit definition `ISQBase::LengthUnit` (`ISQBase.sysml:35`,
  `LengthUnit :> SimpleUnit`). That QN is the dimension identity. (In the golden it is already present
  as the reference's `target_types[0]`; the extractor selects the type that specializes
  `MeasurementUnit`/`SimpleUnit`, not a positional `[0]`.)
- **Quantity-feature operand, exact unit unknown** (`length_value : LengthValue`): the value type is
  `ISQBase::LengthValue` (`ISQBase.sysml:16`, a `ScalarQuantityValue`); its measurement-reference
  feature `mRef` is redefined to `LengthUnit[1]` (`ISQBase.sysml:30`). Following `mRef`'s type yields
  the same `ISQBase::LengthUnit` anchor. `unit` stays `null` (exact unit unknown); `dimension` is the
  unit-def QN.

Both `SI::metre` and `SI::centimetre` are typed `LengthUnit` (`SI.sysml:316`), so same-dimension /
different-unit is detected exactly (`LengthUnit == LengthUnit`, `SI::metre != SI::centimetre`); mass
is `MassUnit`, so incompatible-dimension is detected exactly. Every S1 equality-gate decision is
preserved. *Rejected: `Unit`/`Value`-suffix stripping (`:380-381`, `:431`) — banned `[HARD]`, and it
fabricates a non-existent QN (see surfaced finding below).*

#### Surfaced (MF4): `ISQBase::Length` is not a real element

The review asked for the path that yields the golden's `dimension` value `"ISQBase::Length"`, stating
that QN "appears in the golden independently of `ISQBase::LengthUnit`." **That premise is wrong, and
per the surfacing law I am flagging it rather than silently coding to it.** `ISQBase::Length` appears
in `golden.json` **only** as the `dimension` field value (10×), every occurrence produced by the
strip; there is **no** `attribute def Length` in the ISQ library (`ISQBase.sysml` defines
`LengthValue` at `:16` and `LengthUnit` at `:35`, and a base quantity `isq.L` referenced from
`LengthUnit`'s `quantityDimension` at `:36`, but nothing named `Length`). So the strip fabricates a
QN that names nothing.

**Consequence, stated plainly:** the production golden's `dimension` value changes from the fabricated
`ISQBase::Length` to the real `ISQBase::LengthUnit`. This is allowed — the production golden is a
regenerated artifact byte-compared against itself (the S1 golden is the semantic oracle, not a
byte-match target), and every equality-gate decision is unchanged. A single canonical base-dimension
QN (via the deeper `quantityDimension → quantityPowerFactors → quantity` walk to `isq.L`) is available
if a future item wants dimension identity decoupled from the unit family; it is **not** needed for
Item 1's decisions and is left to Item 3/Item 5 if they need it. *(The live `mRef`-typing traversal
could not be re-run in this sandboxed session — the offline SysIDE invocation hit an approval gate; it
is a cheap, deterministic plan-stage confirmation against `type_units.sysml`.)*

## Required Invariants

- **Serialize → parse → serialize is byte-identical** for any produced fact section at a pinned
  version pair `(constraint-facts/v1, predicate-tree/v0)` (self-referential; not a claim about S1's
  `golden.json`, and not a cross-sub-version claim — D9).
- **The predicate is a self-describing sub-document** carrying its own `predicate_schema_version`;
  the envelope's `schema_version` and the leaf/usage/owner facts are stable independent of the tree
  shape Item 2 will canonicalize.
- **Non-finite literals never serialize** — they are rejected at extraction with a structured
  diagnostic (D2a); `allow_nan=False` is the backstop.
- **No serialized value is a library-coupled string** — no `str(enum)`/`repr()`, no SysIDE object
  rendered as text. SysML v2 metaclass names used as `kind` (`"AssertConstraintUsage"`) are neutral
  and allowed; a Python enum's `__str__` is not.
- **Every operand leaf carries a `category` and a `unit` fact — never omitted.** "Unknown",
  "unresolved", and "dimension known / exact unit unknown" (`unit=null, dimension=set`) are explicit
  states. Silence is never an outcome (concept Principle 5).
- **A feature reference carries no channel/parameter/intermediate role tag** (`[HARD]` M4; concept
  `:87`). The schema has no field for one.
- **Every usage fact carries exactly one `ConstraintSource`** whose `form` is one of the six.
- **Anonymous assertions are identified by `location` (file, line, column)** as a first-class fact,
  not an optional annotation (`[HARD]`; SysIDE gives them no qualified name).
- **`membership_kind` is read from the owning membership**, not the usage subtype.

## Component Overview

- **`expression_facts.py`** — the frozen leaf vocabulary and predicate-tree nodes. `FeatureReferenceFact`
  (source_name, target identity, target_types, chain segments — no role), `LiteralFact` (kind, value,
  result_type), `OperandTypeFact` (category, enumeration, `UnitFact`), `UnitFact` (unit|None,
  dimension|None), `ExpressionFact` (predicate_schema_version, kind, operator|None, operands, and an
  `operand_type: OperandTypeFact | None`). **`operand_type` hangs off every leaf-bearing
  `ExpressionFact` node — both `FeatureReferenceExpression` and literal nodes (N2)** — so `1 [m]` (a
  literal-with-unit) carries `category="quantity"` and its `UnitFact`, resolving the review's homeless
  literal-unit field. Non-leaf operator nodes carry `operand_type = None`. This node is the **merged
  leaf** that unifies S1's two operand shapes (Core Concept, N1): it carries the `source_forms`
  reference block **and** the `type_units` category/enumeration/unit fields on one object. No syside
  import, no constraint import — so Item 2 can adopt it freely.
- **`constraint_facts.py`** — `ConstraintDefinitionFact` (identity, formals, predicate),
  `ConstraintUsageFact` (identity, location, `ConstraintSource`, `OwnerFact` with the tagged
  `owning_definition`, scope, membership_kind, is_negated, actuals, omitted_default_formals, predicate,
  inherited_into), `ConstraintSource`, `ContextFact` (inheritance/retyping), the `ConstraintFacts`
  aggregate, the `CONSTRAINT_FACTS_SCHEMA_VERSION` and `PREDICATE_TREE_SCHEMA_VERSION` constants, and
  `serialize()`.
- **`constraint_extraction.py`** — `extract_constraint_facts(model)` and the private classify/recover
  helpers. The only module that touches syside.
- **Re-anchored test** at `tests/test_sysml/test_constraint_fact_shapes.py` — runs the production
  extractor over S1's two fixtures, asserts **fact fields only** (drops `type_units.equality_cases[].decision`),
  and byte-compares a regenerated production golden against itself.

Schema sketch (representative, not exhaustive):

```python
@dataclass
class UnitFact:
    unit: str | None          # SI::metre | ... | None  (None + dimension set = "exact unit unknown")
    dimension: str | None     # ISQBase::LengthUnit | ... | None  (the measurement-unit def QN, MF4)

@dataclass
class OwningDefinitionFact:            # tagged + total over all six forms (D6/MF3)
    kind: str                 # part_def | calc_def | requirement_def | package
    qualified_name: str

@dataclass
class ConstraintSource:
    form: str                 # inline|definition_typed|named_usage_reference|satisfy|
                              # requirement_constraint|plain_usage
    effective_predicate_source: IdentityFact | None
    constraint_definition: IdentityFact | None
    referenced_feature_target: IdentityFact | None
    asserted_constraint: IdentityFact | None   # golden field homed here (N2)
```

## Non-Goals

- **Item 3's eligibility verdicts.** No equality/unit gate, no `decision` labels. Item 1 ships the
  facts those decisions read.
- **Item 2's `ExpressionIR` canonical algebra.** Item 1 ships the leaf vocabulary and a provisional
  predicate tree; Item 2 owns the canonical tree (see coordination).
- **Any sysml-codegen consumption / snapshot v3 host document.** Producer side only.
- **A CLI artifact or manifest emitter.** Facts are in-memory dataclasses + a serializer; no host
  document exists to plug into yet.
- **Cross-sub-version predicate byte-compat (D9).** A `predicate-tree/v0` section is not required to
  byte-match a future canonical `predicate-tree/v1`; Item 2's tree bump is allowed to change bytes.
- **Re-deciding S1's semantic verdicts.** Carried forward, not relitigated.

## Cross-Item Coordination

Two premise-level seams. The owner (Reid) is not reachable from this non-interactive stage, so per
the capture-fidelity surfacing law these are surfaced **loudly here** with the decision I took and
what would overturn it — not resolved silently in either repo.

- **C1 — Item 1 / Item 2 predicate-tree seam (spec Open Question, MF1).** Two axes, both must be
  handled: *code acyclicity* (which module imports which) and *wire-shape stability* (whether the
  serialized tree forces a version bump). The original design solved only the first; the review
  flagged the second.
  - *Code axis:* Item 1 freezes the **leaf vocabulary** (`FeatureReferenceFact`, `LiteralFact`,
    `OperandTypeFact`, `UnitFact`) in `expression_facts.py` and carries the predicate as a provisional
    `ExpressionFact` tree of those leaves plus a minimal operator node. Item 2's `ExpressionIR`
    **imports** `expression_facts`; `expression_facts` never imports Item 2. One-way, no cycle.
  - *Wire axis (MF1 decision, `[AGENT]`):* the predicate serializes as a **separately versioned
    sub-document** — `predicate_schema_version = "predicate-tree/v0"` — inside the stable
    `constraint-facts/v1` envelope. The leaf/usage/owner facts Item 3 and Item 5 actually consume live
    in the envelope and are stable at `v1`. When Item 2 lands its canonical `ExpressionIR`, it changes
    the tree shape and bumps **only** `predicate-tree/v0 → v1`; the envelope stays `constraint-facts/v1`.
    The `v1` envelope is therefore a real contract through the epic, not a throwaway.
  - **What overturns it:** Item 2 relocating the leaf *types* into `expression_ir.py` (a mechanical
    move — `constraint_facts` then imports `expression_ir`, still acyclic); or a leaf *field* change
    (that bumps the envelope, which is the honest signal). **Action:** carry the predicate
    sub-versioning contract into Item 2's design brief, and note **Item 8 pins BOTH versions**
    (`constraint-facts/v1` + the then-current `predicate-tree/vN`) when it embeds these facts in
    snapshot v3.

- **C2 — Item 5's `owning_part_def_qn` grade (spec N2, MF3).** `owner` + `inherited_into` suffice for
  the `PartDefinition`-owned, `CalculationDefinition`-owned, and inherited cases, but **not** for the
  package-scoped or non-part owners — `direct_owned`'s owner is a package-scoped `PartUsage` with no
  enclosing definition, and `positive_limit`/`below_limit` are owned by a `RequirementDefinition`.
  **Decision (D6, `[AGENT]`):** `owning_definition` is a **tagged, total** fact — `kind ∈ {part_def,
  calc_def, requirement_def, package}` + `qualified_name`, resolved by walking `owner` up to the first
  enclosing definition-or-package (a `Package` always terminates the chain). **Consumer semantics for
  Item 5, stated explicitly:**
  - `part_def` → expand once per concrete part instance (multiplicity + inheritance).
  - `calc_def` → expand once per concrete calculation usage.
  - `package` (a root `PartUsage` like `direct_owned`, or a package-scoped satisfy) → the usage is
    already concrete; expand **once**, keyed on the `owner` `PartUsage` identity.
  - `requirement_def` (require/assume) and `package`-scoped satisfy → cataloged, unassessed in the
    first executable scope (concept `:91`).

  This gives Item 5 the dispatch it needs from `(owning_definition.kind, owner)` in every case, and
  matches the S3 carry-forward that "the extracted fact already carries `owning_part_def_qn`."
  **Action:** carry the `owning_definition` totality rule and these consumer semantics into Item 5's
  design brief.

## Potential Risks

- **A structural discriminator disagrees with S1's classification on some fixture form** (B1). The
  `result_expression`-ownership test for inline vs definition-typed is `[HARD]` and S1-verified, but
  the re-anchor is the proof. *Mitigation:* the re-anchor test fails loudly on any divergence; run it
  first.
- **Operand-fact extraction on a leaf where `cached_result_type` is absent** produces a `category` of
  `unknown`/`unresolved` — must be an explicit state, never a crash or omission. *Mitigation:* the
  "never omitted" invariant + a test on the `unresolved_operand` fixture case.
- **Float byte-stability** rests on Python's round-trip `repr`. Fixtures use finite decimals; a
  non-finite literal is rejected at extraction with a structured diagnostic (D2a) and `allow_nan=False`
  is the backstop. *Mitigation:* the self-round-trip test + a non-finite-literal diagnostic test.
- **Restructuring golden fields into `ConstraintSource`/`owning_definition` + the changed `dimension`
  value (MF4)** means the re-anchor test is rewritten, not copied, and the S1 golden's `dimension`
  strings (`ISQBase::Length`) will not appear in production output. *Mitigation:* the re-anchor maps
  each S1 golden field → production field and asserts semantic value equality; the production golden is
  a distinct regenerated artifact byte-compared against itself (S1 golden stays the read-only semantic
  oracle). The dimension change is a decision preservation, verified case-by-case in the re-anchor.
- **Test rewrite is not atomic.** The current test imports `FIXTURE_DIR` and `capture_all_facts` from
  the module D7 deletes (`test_constraint_fact_shapes.py:7`). *Mitigation:* delete the capture module
  and rewrite the test against the production extractor in one change; the plan sequences this.

## Integration Strategy

- Add the three modules; export the public schema types + `extract_constraint_facts` +
  `serialize` from `agentic_mbse/sysml/__init__.py` alongside the existing aggregation/data_models
  exports (`__init__.py:6-22,90-115`).
- The existing type-level path (`is_droppable_constraint`, `syside_adapter.py:410`) is **not**
  removed here — it still serves the current L4/L6 validators. Item 1 adds the richer facts beside
  it; retiring the drop path is downstream (concept `:103`).
- Retire `tests/constraint_fact_learning.py`; keep the S1 fixtures.

**Oracle vs production golden — two distinct files (N4):** the S1 `tests/fixtures/constraint_fact_shapes/golden.json`
is preserved **read-only as the semantic oracle**. The production extractor writes a **separate**
production golden (e.g. `tests/fixtures/constraint_fact_shapes/production_facts.json`) that is
regenerated and byte-compared **against itself**. The re-anchor never overwrites `golden.json`, so
the oracle survives.

## Validation Approach

- **Re-anchored golden test** (fact fields only): six source forms extract and are distinct;
  membership/polarity/ownership/actuals/defaults/inheritance match S1 oracle values; operand category
  + enumeration + unit/dimension match S1's `type_units` evidence (**excluding** `decision`; the
  `dimension` value is asserted against the real measurement-unit-def QN per MF4, not the strip
  artifact); compound Boolean tree survives; anonymous assertion identified by location; no `str(enum)`
  in any value; `owning_definition` present and tagged on every usage.
- **Drop/relocate the decision-asserting tests (review minor).** The current
  `test_equality_gate_is_decided_from_static_operand_facts` and
  `test_loader_diagnostics_are_golden_but_not_the_equality_gate` assert Item 3's `decision` verdicts;
  the rewrite removes them from Item 1's suite (they are Item 3's to own), keeping only the operand
  *fact* assertions.
- **Byte-stable round-trip test** at the pinned `(constraint-facts/v1, predicate-tree/v0)` pair:
  `serialize(parse(serialize(facts))) == serialize(facts)`.
- **Non-finite-literal diagnostic test:** a non-finite literal yields a structured extraction
  diagnostic, not a serialize crash (D2a).
- **Banned-heuristic guard:** production code contains no namespace-prefix discrimination and no
  `Unit`/`Value`-suffix strip (grep-level assertion or review gate).
- **Full suite green + Ruff clean** (spec success criteria).

## Next-Stage Handoff

- **Fixed:** the three-module layout and one-way import direction (D8/C1); `@dataclass` + canonical
  JSON contract (D1–D3); the two-level version scheme with a separately-versioned predicate
  sub-document (D4/D9, MF1); the type/membership-gated dispatch and its structural discriminators
  (MF2); the structural dimension path (MF4); retire the capture module (D7); the tagged, total
  `owning_definition` (D6/C2, MF3); non-finite rejected at extraction (D2a).
- **Carry to downstream briefs (surfaced):** **Item 2** — adopt the leaf vocabulary and own the
  canonical tree, bumping only `predicate-tree/vN` (C1/MF1). **Item 5** — the `owning_definition`
  totality rule and its consumer semantics (C2/MF3). **Item 8** — pin BOTH versions
  (`constraint-facts/v1` + the then-current `predicate-tree/vN`) when embedding in snapshot v3 (D9).
- **Open (owned downstream):** the single canonical base-dimension QN (`isq.L`) is available via a
  deeper walk if Item 3/5 need dimension identity decoupled from the unit family; not needed for Item
  1. The live `mRef`-typing traversal (MF4) is a cheap plan-stage confirmation against
  `type_units.sysml` (could not run live here — sandbox approval gate).
- **De-risk first:** run the re-anchored golden against the production extractor before anything
  else — it is the single proof that B1 holds and the type/membership-gated discriminators reproduce
  S1's classifications. If it diverges, stop and revisit the discriminator, not the golden.

---

**Next Step:** After approval → `/_my_plan`.

---

## Addendum: MF4 live confirmation (orchestrator, 2026-07-12)

The one unexecuted check — that a dimension-only quantity feature's value type reaches
the measurement-unit definition structurally — was run live by the orchestrator
(`probe_mref_dimension.py`, this directory; licensed-env invocation as in S1):

- `dim_only : LengthValue` → walking `ISQBase::LengthValue.members` finds `mRef` whose
  types include `ISQBase::LengthUnit` (alongside the generic
  `MeasurementReferences::*MeasurementReference` supertypes). The traversal must select
  the most-specific unit-definition type (the `ISQBase::LengthUnit` entry), not the
  generic measurement-reference supertypes.
- Confirms D-MF4's structural path; no design unknown remains. The plan-stage check the
  revision requested is discharged.
