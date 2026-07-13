# Design: Neutral Constraint Facts — Production Schemas and Extraction

**Status:** Draft
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

The design is a faithful promotion, not a redesign. S1 already proved every fact is structurally
recoverable and froze the shapes. Item 1's job is to (1) move those shapes from a test module into
`@dataclass` schemas in `agentic_mbse.sysml`, (2) replace two fixture-coupled heuristics with the
principled structural discriminators the spec makes `[HARD]`, (3) neutralize one library-enum leak
at extraction, and (4) serialize to a versioned, self-consistent byte-stable JSON section. The leaf
vocabulary lives in its own module so Item 2's `ExpressionIR` imports it without a cycle.

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
- **B3.** The nearest enclosing *definition* of a constraint usage is structurally walkable from
  `owner`, giving Item 5 an `owning_part_def_qn`-grade fact in the direct-usage case where
  `owner.qualified_name` is a `PartUsage`, not a definition. *If false → Item 5 cannot key
  multiplicity expansion by owning-definition + feature for directly-owned assertions.*
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
  whitespace/encoding drift; `allow_nan=False` turns a non-finite operand into an extraction error
  rather than emitting non-standard `NaN`. Float round-trips via Python's round-trip `repr`.
  *Rejected: pretty-printed indent like S1's golden (whitespace is a byte-instability surface and
  the spec explicitly does not require reproducing S1's byte layout).*
- **D3. Every field always present; absence is explicit `null`.** No optional-field omission. Makes
  the round-trip total and the schema a fixed shape. Matches the golden's explicit `null`s
  (`membership_kind: null`, `referenced_feature_target: null`). *Rejected: omit-when-None (two byte
  forms for one fact; a moving contract).*
- **D4. Version = single module constant `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"`,
  emitted as the top-level `schema_version` field of the serialized section.** One source of truth;
  bumped on any breaking field change; the string downstream's version hard-gate keys on (concept
  Required Invariant `:143`). *Rejected: S1's `constraint-fact-learning-test/v1` tag (test-only,
  and names the retired capture path). Rejected: an integer with no namespace (collides with
  snapshot v3's own version; the `constraint-facts/` prefix keeps them distinct).*
- **D5. Six-form discriminant carried as one `ConstraintSource` on each usage fact.** The spec
  requires "exactly one `ConstraintSource`." It holds `form` (one of the six) plus the
  form-specific pointers (effective-predicate-source identity, `constraint_definition`,
  `referenced_feature_target`). *Rejected: flat sibling fields as in S1's golden (the spec makes the
  single-discriminant explicit, and grouping prevents an illegal combination — e.g. a `satisfy`
  carrying an inline predicate).*
- **D6. Add a resolved `owning_definition` fact to the owner block** (kind + qualified_name: the
  nearest enclosing `PartDefinition`/`CalculationDefinition`). Answers spec N2 — see
  [Cross-Item Coordination](#cross-item-coordination). *Rejected: leave Item 5 to derive it from
  `owner.qualified_name` (fails for the direct-`PartUsage`-owned case, where the QN is the usage's,
  not the definition's).*
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
2. **Classify (dispatch order):** `satisfy` (`SatisfyRequirementUsage`) → `named_usage_reference`
   (`asserted_constraint is not self`) → `inline` vs `definition_typed` (**owns a
   `result_expression`?** inline yes, definition-typed no — `[HARD]`) → `requirement_constraint`
   (owning membership is `RequirementConstraintMembership`) → `plain_usage` (fallback). *Rejected
   for inline/def-typed: namespace-prefix test (`constraint_fact_learning.py:172`) — banned,
   fixture-coupled.*
3. **Membership kind** from the owning `RequirementConstraintMembership.kind`, neutralized to
   `requirement`/`assumption`/`null` — read from the membership, never the usage subtype (`[HARD]`).
4. **Formals** by owner-filtered `AttributeUsage` sweep (`owner is definition`); default is an owned
   `FeatureValue` with `is_default = true`. *Rejected: `ConstraintDefinition.parameters` — omits
   user inputs in 0.8.4 (`[HARD]`; findings §2).*
5. **Operand leaf facts** per leaf: category by type conformance; enumeration by the owning
   `EnumerationDefinition`; unit/dimension by **unit-reference target types** (`m`→`SI::metre`,
   whose type distinguishes length from mass). *Rejected: `Unit`-suffix stripping
   (`constraint_fact_learning.py:380-381`) — banned (`[HARD]`).*
6. **Neutralize library values at extraction:** parameter direction maps
   `syside.FeatureDirectionKind` → `in`/`out`/`inout` token; enum-like values map via `.name.lower()`
   to neutral strings. *Rejected: `str(enum)` — leaks `"FeatureDirectionKind.In"` into the wire
   contract (`[HARD]` M3; golden `direction` is the one such leak).*

## Required Invariants

- **Serialize → parse → serialize is byte-identical** for any produced fact section (self-referential;
  not a claim about S1's `golden.json`).
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
  dimension|None), `ExpressionFact` (kind, operator|None, operands, leaf payload). No syside import,
  no constraint import — so Item 2 can adopt it freely.
- **`constraint_facts.py`** — `ConstraintDefinitionFact` (identity, formals, predicate),
  `ConstraintUsageFact` (identity, location, `ConstraintSource`, owner+`owning_definition`, scope,
  membership_kind, is_negated, actuals, omitted_default_formals, predicate, inherited_into),
  `ConstraintSource`, `ContextFact` (inheritance/retyping), the `ConstraintFacts` aggregate, the
  `CONSTRAINT_FACTS_SCHEMA_VERSION` constant, and `serialize()`.
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
    dimension: str | None     # ISQBase::Length | ... | None

@dataclass
class ConstraintSource:
    form: str                 # inline|definition_typed|named_usage_reference|satisfy|
                              # requirement_constraint|plain_usage
    effective_predicate_source: IdentityFact | None
    constraint_definition: IdentityFact | None
    referenced_feature_target: IdentityFact | None
```

## Non-Goals

- **Item 3's eligibility verdicts.** No equality/unit gate, no `decision` labels. Item 1 ships the
  facts those decisions read.
- **Item 2's `ExpressionIR` canonical algebra.** Item 1 ships the leaf vocabulary and a provisional
  predicate tree; Item 2 owns the canonical tree (see coordination).
- **Any sysml-codegen consumption / snapshot v3 host document.** Producer side only.
- **A CLI artifact or manifest emitter.** Facts are in-memory dataclasses + a serializer; no host
  document exists to plug into yet.
- **Re-deciding S1's semantic verdicts.** Carried forward, not relitigated.

## Cross-Item Coordination

Two premise-level seams. The owner (Reid) is not reachable from this non-interactive stage, so per
the capture-fidelity surfacing law these are surfaced **loudly here** with the decision I took and
what would overturn it — not resolved silently in either repo.

- **C1 — Item 1 / Item 2 predicate-tree seam (spec Open Question).** Item 1 needs a predicate tree
  now (the golden's `predicate`, asserted by the re-anchor test); Item 2 owns `ExpressionIR` and does
  not exist yet, so Item 1 cannot import it. **Decision:** Item 1 freezes the **leaf vocabulary**
  (`FeatureReferenceFact`, `LiteralFact`, `OperandTypeFact`, `UnitFact`) in `expression_facts.py` and
  carries the predicate as a **provisional `ExpressionFact` tree** built from those leaves plus a
  minimal operator node. Item 2's `ExpressionIR` **adopts the leaf vocabulary** (imports
  `expression_facts`) and canonicalizes the operator/tree layer; `expression_facts` never imports
  Item 2. Import direction is one-way toward the leaves, so no cycle. **What overturns it:** if Item
  2's design wants the leaf types to physically live in `expression_ir.py`, that is a mechanical
  relocation under Item 2's ownership — `constraint_facts` then imports from `expression_ir`, still
  acyclic because the leaves have no constraint dependency. **Action:** carry C1 into Item 2's design
  brief as the adopted-vocabulary contract.

- **C2 — Item 5's `owning_part_def_qn` grade (spec N2).** `owner` + `inherited_into` suffice for the
  `PartDefinition`-owned, `CalculationDefinition`-owned, and inherited cases (golden:
  `inline_owner_reference`→PartDefinition; `calc_owned`→CalculationDefinition; `inherited_limit`→
  `inherited_into` lists the target part defs). They do **not** suffice for the direct-`PartUsage`-owned
  case (`direct_owned`→owner is a `PartUsage`; its QN is not a definition QN). **Decision (D6):** add a
  resolved `owning_definition` fact (nearest enclosing definition, structurally walked from `owner`).
  This gives Item 5 the `owning_part_def_qn` grade directly in all cases and matches the S3
  carry-forward that "the extracted fact already carries `owning_part_def_qn`." **What overturns it:**
  evidence that Item 5 keys expansion only by the `PartUsage` identity (then `owning_definition` is
  redundant) — not the case per S3/S4.

## Potential Risks

- **A structural discriminator disagrees with S1's classification on some fixture form** (B1). The
  `result_expression`-ownership test for inline vs definition-typed is `[HARD]` and S1-verified, but
  the re-anchor is the proof. *Mitigation:* the re-anchor test fails loudly on any divergence; run it
  first.
- **Operand-fact extraction on a leaf where `cached_result_type` is absent** produces a `category` of
  `unknown`/`unresolved` — must be an explicit state, never a crash or omission. *Mitigation:* the
  "never omitted" invariant + a test on the `unresolved_operand` fixture case.
- **Float byte-stability** rests on Python's round-trip `repr`. Fixtures use finite decimals;
  `allow_nan=False` guards the pathological case. *Mitigation:* the self-round-trip test covers it.
- **Restructuring golden fields into `ConstraintSource`/`owning_definition`** means the re-anchor test
  is rewritten, not copied. *Mitigation:* the re-anchor maps golden field → production field and
  asserts value equality; the production golden is regenerated (spec: S1 golden is the semantic
  oracle, a new production golden byte-compares against itself).

## Integration Strategy

- Add the three modules; export the public schema types + `extract_constraint_facts` +
  `serialize` from `agentic_mbse/sysml/__init__.py` alongside the existing aggregation/data_models
  exports (`__init__.py:6-22,90-115`).
- The existing type-level path (`is_droppable_constraint`, `syside_adapter.py:410`) is **not**
  removed here — it still serves the current L4/L6 validators. Item 1 adds the richer facts beside
  it; retiring the drop path is downstream (concept `:103`).
- Retire `tests/constraint_fact_learning.py`; keep `golden.json` + `.sysml` fixtures.

## Validation Approach

- **Re-anchored golden test** (fact fields only): six source forms extract and are distinct;
  membership/polarity/ownership/actuals/defaults/inheritance match S1 values; operand category +
  enumeration + unit/dimension match S1's `type_units` evidence (**excluding** `decision`); compound
  Boolean tree survives; anonymous assertion identified by location; no `str(enum)` in any value.
- **Byte-stable round-trip test:** `serialize(parse(serialize(facts))) == serialize(facts)`.
- **Banned-heuristic guard:** production code contains no namespace-prefix discrimination and no
  `Unit`-suffix strip (grep-level assertion or review gate).
- **Full suite green + Ruff clean** (spec success criteria).

## Next-Stage Handoff

- **Fixed:** the three-module layout and one-way import direction (D8/C1); `@dataclass` + canonical
  JSON contract (D1–D4); the six-form dispatch order and its structural discriminators; retire the
  capture module (D7); add `owning_definition` (D6/C2).
- **Open (owned downstream, surfaced):** C1 — Item 2 formalizes the operator/tree layer and may
  relocate the leaf types; C2 — confirm `owning_definition` against Item 5's resolver when Item 5 is
  designed.
- **De-risk first:** run the re-anchored golden against the production extractor before anything
  else — it is the single proof that B1 holds and the two structural discriminators reproduce S1's
  classifications. If it diverges, stop and revisit the discriminator, not the golden.

---

**Next Step:** After approval → `/_my_plan`.
