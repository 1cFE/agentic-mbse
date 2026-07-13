# Spec: Neutral Constraint Facts — Production Schemas and Extraction

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** `constraint-exec-epic`
**Epic:** CONSTRAINT-EXEC, Item 1

---

## Problem

agentic-mbse owns the neutral SysML semantics that every downstream repo consumes (the
PUSH-DOWN pattern). Today its constraint handling is type-level only: it sweeps
`ConstraintUsage` and decides *droppability* (`is_droppable_constraint` in
`src/agentic_mbse/sysml/syside_adapter.py:410`), but it collapses every membership kind to
"plain" and drops the predicate entirely. It cannot tell an `assert` from a `satisfy`, a
`require` from an `assume`, or a definition-typed usage from an inline one, and it carries
no formals, actuals, defaults, or inheritance facts.

That gap blocks the rest of the CONSTRAINT-EXEC epic. Downstream consumers — sysml-codegen
lowering, snapshot v3, and the executable profile (Item 3) — need a **frozen, neutral fact
vocabulary** to build on. Whatever this item ships becomes the contract they read as ground
truth.

The S1 spike (`.project/active/spike-constraint-fact-shapes/findings.md`) already proved,
against live SysIDE 0.8.4, that every needed fact is recoverable structurally without an
evaluator, and it froze the exact fact shapes as a committed fixture + golden JSON + kept
tests. But S1 shipped that as **test-only capture code**, explicitly *not* a production IR or
schema commitment (findings.md §4). This item promotes S1's frozen shapes into production
schemas with production extraction.

## Success Criteria

- [ ] All **six** source-form classes from S1's golden matrix extract via production code:
      `inline`, `definition_typed`, `named_usage_reference`, `satisfy`,
      `requirement_constraint` (requirement-owned require/assume), and `plain_usage`
      (non-asserted usage as a reference target).
- [ ] For every extracted usage fact, these facts **semantically match** S1's golden values:
      membership kind, polarity, ownership/scope, actuals (with formal targets), omitted
      defaulted formals, and inheritance/retyping facts. "Match" means value equality of the
      facts, not byte-identity with S1's `golden.json` (see the serialization criterion).
- [ ] Operand **leaf facts** extract and match the S1 type/unit evidence: each operand's type
      category (Boolean / String / Integer / Real), enumeration identity where the operand is an
      enum, and unit/dimension state resolved structurally — including the "dimension known,
      exact unit unknown" state. The Item-3 equality-gate *decision* over these facts is **not**
      asserted here.
- [ ] Every feature reference keeps its source name, qualified target, and feature-chain
      segments, and carries **no** channel/parameter/intermediate role tag.
- [ ] No serialized fact contains a SysIDE Python type name or an `str(enum)` repr; library
      enums (e.g. parameter direction) map to a neutral vocabulary at extraction.
- [ ] `ConstraintDefinitionFact` carries the reusable predicate, its formals with defaults,
      and source identity; each usage fact carries **exactly one** `ConstraintSource` naming
      its form.
- [ ] Neither fixture-coupled heuristic appears in production code: no namespace-prefix
      discrimination of inline vs definition-typed, and no `Unit`-suffix stripping for quantity
      dimension.
- [ ] The facts serialize to a **versioned** JSON section whose **own** serialization
      round-trips **byte-identically** (serialize → parse → serialize is stable). This is a
      property of Item 1's production format — not a claim that S1's `golden.json` is reproduced
      byte-for-byte.
- [ ] Golden tests are re-anchored from S1's fixtures against the production extractor, covering
      **fact fields only**; the `type_units.equality_cases[].decision` verdicts are Item 3's and
      are excluded from Item 1's assertions. S1's test-only capture module is retired or clearly
      demoted to fixture tooling.
- [ ] agentic-mbse suite green; Ruff clean.

## Known Requirements

### The fact vocabulary (schemas)

- **[INHERITED]** Three production, serializable schemas: `ConstraintDefinitionFact`,
  `ConstraintUsageFact`, and `ConstraintSource`. *(Epic Item 1 objective; S1 froze the field
  shapes — `findings.md` §2, `tests/fixtures/constraint_fact_shapes/golden.json`.)*
- **[INHERITED]** `ConstraintDefinitionFact` carries: source identity (kind, name,
  qualified_name); the reusable predicate; and an ordered list of formals, each with name,
  qualified_name, types, `has_default`, and the default value when present. *(S1 golden
  `definitions[].formals`.)*
- **[INHERITED]** Each `ConstraintUsageFact` carries exactly one `ConstraintSource` discriminant
  identifying one of the six forms above. The four **asserted** forms are inline,
  definition-typed, named-usage-reference, and satisfy. The two **non-asserted catalog** forms
  must both be pinned so neither falls between "assertion" and "authoring inventory":
  requirement-owned require/assume constraints (`requirement_constraint`), and plain
  non-asserted usages that serve as reference targets (`plain_usage`). *(Epic Item 1 scope §1;
  S1 golden distinct `source_form` values.)*
- **[INHERITED]** Per-usage facts: identity; `membership_kind` read from the **owning
  membership** (`RequirementConstraintMembership.kind` → `requirement` / `assumption` / `None`),
  *not* from the owned usage subtype; polarity (`is_negated` for asserts, absent/null for
  non-asserted forms); owner and scope (owning type distinguishes `PartDefinition`,
  `CalculationDefinition`, `PartUsage`, `Package`, `RequirementDefinition`); the typing
  `constraint_definition`; `asserted_constraint`; `referenced_feature_target` (for
  named-usage-reference); actuals with their formal targets and direction; omitted defaulted
  formals; inheritance/retyping facts (`inherited_into`); and source location. *(S1 golden
  `source_forms.constraints[]` fields; `findings.md` §2.)*
- **[HARD]** Anonymous assertions have neither `name` nor `qualified_name`, so their identity
  is their **source location** (file, line, column). The schema must carry source location as a
  first-class identity fact, not an optional annotation. *(S1: `findings.md` §2; forced by
  SysIDE — anonymous `AssertConstraintUsage` has no qualified name.)*
- **[INHERITED]** Inheritance/retyping facts at the owning-context level: general types,
  inherited constraints, and redefinitions (each: the redefining feature, the redefined
  feature, and the redefining value). *(S1 golden `source_forms.contexts[]`.)*

### Extraction (production)

- **[HARD]** Extraction sweeps the **base `ConstraintUsage`** with subtype inclusion and
  classifies afterward. An `AssertConstraintUsage`-rooted sweep does **not** return `satisfy`
  in SysIDE 0.8.4. The adapter already supports this shape
  (`elements_of_type(..., include_subtypes=True)`, `syside_adapter.py:269`). *(S1 verified —
  `findings.md` §2; forced by SysIDE 0.8.4 subtype semantics.)*
- **[HARD]** Constraint-definition formals are recovered by an owner-filtered `AttributeUsage`
  model sweep (`owner is definition`), because `ConstraintDefinition.parameters` and
  `owned_members` omit the user-declared input attributes in SysIDE 0.8.4. The default is an
  owned `FeatureValue` with `is_default = true`. *(S1 verified — `findings.md` §2; forced by
  SysIDE 0.8.4.)*
- **[HARD]** Inline vs definition-typed is discriminated by whether the usage **owns a
  `result_expression`** (inline owns one; definition-typed does not — its
  `constraint_definition` owns the predicate). This is the principled structural
  discriminator. **Namespace-prefix discrimination is banned.** *(S1 carry-forward (1); Epic
  Item 1 scope §2; concept Design Principle — no fixture-coupled heuristics.)*
- **[HARD]** Quantity dimensions are resolved **structurally** (via unit-reference targets and
  feature typing — e.g. `m`/`cm`/`kg` → `SI::metre`/`SI::centimetre`/`SI::kilogram`, whose
  types distinguish length from mass). **`Unit`-suffix stripping is banned.** *(S1
  carry-forward (1); Epic Item 1 scope §2; `findings.md` §3.)*

### Operand leaf facts (the leaf vocabulary downstream gates consume)

This item **owns** the operand leaf facts as extracted, serialized facts. Item 3's equality/unit
gate and Item 5's resolver read them; the *decisions* over them stay downstream. The concept
assigns this leaf vocabulary to the neutral facts: equality is admitted only "when both operand
types are recovered from the neutral facts and their compatibility is proven" (concept
`.project/reference/constraint-execution-concept.md:91`), and references "keep source name,
qualified target, and feature-chain segments; they do not pre-classify a value as channel,
parameter, or intermediate — that is codegen's job" (concept `:87`).

- **[INHERITED]** Every operand carries its **type category** (Boolean / String / Integer /
  Real) and, where it is an enum, its **enumeration identity**, as recovered facts. These are
  what let a downstream gate prove operand compatibility without guessing. *(Concept `:91`; S1
  `type_units.equality_cases` evidence — `findings.md` §3.)*
- **[INHERITED]** Every operand carries its **unit/dimension** fact, resolved structurally (per
  the banned-heuristic requirement above). *(Concept `:91`; `findings.md` §3.)*
- **[INHERITED]** Exact unit is a **conditional** fact, not a universally recoverable field. A
  feature typed only by a quantity kind (e.g. `LengthValue`) proves the dimension, not one
  runtime unit. The schema must represent "dimension known, exact unit unknown" as a first-class
  state, not silently omit it. *(Concept `:91` `[AGENT]` sharpening; S1 verdict — `findings.md`
  §5; concept Design Principle 5: silence is never an outcome. The eligibility decision that
  consumes this state is Item 3.)*
- **[HARD]** A feature reference keeps its **source name**, **qualified target**, and
  **feature-chain segments**, and is **never** pre-classified as channel, parameter, or
  intermediate — that classification is codegen's job (Item 5). Item 5's strict resolver depends
  on the reference arriving un-roled. The S1 golden already obeys this
  (`FeatureReferenceExpression` carries `source_name` / `target` / `target_types`, no role tag).
  *(Concept `:87`; concept Required Invariant — Semantics and Identity.)*

### Wire-format neutrality

- **[HARD]** No serialized fact value may be a library-specific string: no Python `str(enum)` /
  `repr()` form, and no SysIDE-object identity rendered as text. Library-coupled values are
  mapped to a stable neutral vocabulary **at extraction**. This is a general rule — the facts are
  the contract three repos consume, and byte-stable serialization freezes whatever leaks in.
  (SysML v2 **metaclass names** used as `kind` discriminants — e.g. `"AssertConstraintUsage"`,
  `"ConstraintDefinition"` — are *not* leaks: they are spec-standardized and tool-independent, so
  they are legitimate neutral values. The rule targets library formatting, like a Python enum's
  `__str__`, not the SysML type identity itself.) *(Concept Design Principle 3: structure
  survives, reconstructed text does not; Epic Item 1 intent — neutral vocabulary.)*
- **[HARD]** Concretely: parameter **direction** serializes as a neutral token
  (`in` / `out` / `inout`), mapped from `syside.FeatureDirectionKind` at extraction. The S1
  capture module leaked `str(syside.FeatureDirectionKind.In)` → `"FeatureDirectionKind.In"` into
  the golden `direction` field; production must not. *(Audit of S1 golden: `direction` is the one
  such leak; no other `…Kind.X` repr appears.)*

### Serialization

- **[NEED]** The facts serialize to a JSON section that carries an explicit **schema version**
  and whose **own** serialization round-trips byte-identically (serialize → parse → serialize is
  stable). Byte-stability is a property of Item 1's production format — it is **not** a
  requirement to reproduce S1's `golden.json` byte-for-byte. S1's golden is the **semantic
  oracle** for the fact values; a new production golden is generated and byte-compared against
  itself. *(Epic Item 1 success criteria; concept: the facts are the downstream contract.)*
- **[HARD]** These schemas are shared types read by a downstream package (sysml-codegen
  snapshot v3). They belong with the existing shared-type surface
  (`src/agentic_mbse/sysml/data_models.py` / `types.py`, both already documented as
  "imported by downstream packages (sysml-codegen)"). Changes are a cross-repo contract.
  *(Epic Item 1 intent; `data_models.py:1-5`.)*

### Tests

- **[INHERITED]** Golden tests are re-anchored from S1's committed fixtures
  (`tests/fixtures/constraint_fact_shapes/source_forms.sysml`, `type_units.sysml`,
  `golden.json`) and run against the **production** extractor, at
  `tests/test_sysml/test_constraint_fact_shapes.py`. *(Epic Item 1 scope §3.)*
- **[NEED]** The re-anchor asserts **fact fields only**. The S1 golden's
  `type_units.equality_cases[].decision` fields (e.g. `block_real_equality_requires_tolerance`,
  `support_enum_same_enumeration`) are Item 3's equality-gate verdicts, not Item 1 facts — they
  are excluded from Item 1's golden assertions and from its byte-stable claim. Item 1 asserts the
  operand *facts* those decisions were derived from (type category, enumeration identity,
  unit/dimension state), never the verdicts. *(Splits this item's Non-Goal from its tests;
  concept: eligibility is Item 3, `:91`.)*
- **[NEED]** S1's test-only capture module (`tests/constraint_fact_learning.py`) is retired, or
  clearly demoted to fixture-generation tooling with no production role. *(Epic Item 1 scope
  §3; S1 explicitly marked it non-production — `findings.md` §4.)*

## Non-Goals

- **Eligibility / executable-profile decisions.** Which facts a runtime may execute — the
  equality/unit gate, what blocks — is Item 3. This item captures the operand *facts* (type
  category, enumeration identity, unit/dimension state, "dimension known, exact unit unknown");
  it does not decide what to do with them. The equality-gate *verdicts* in S1's golden
  `decision` fields are Item 3's, not Item 1's.
- **Expression tree internals / `ExpressionIR`.** Item 2 owns the canonical expression
  representation and its tree structure. This item owns the operand **leaf** facts Item 2's
  leaves adopt (type category, enumeration identity, unit/dimension, source-name/qualified-target,
  un-pre-classified references) — now enumerated in Known Requirements, not a deferred phrase. It
  does not define the full expression IR.
- **Any sysml-codegen consumption.** Downstream lowering and snapshot v3 wiring are out of
  scope; this item ships the producer side only.
- **Re-deciding S1's semantic verdicts.** The equality/unit gate table and the exact-unit
  restriction are settled S1 evidence, carried forward, not relitigated here.

## Open Questions / Deferred to design

- **Predicate tree structure — the Item 1 / Item 2 seam.** The operand **leaf** facts this item
  freezes are now Known Requirements (type category, enumeration identity, unit/dimension,
  source-name/qualified-target, un-pre-classified references). What remains open is the *tree
  structure* that holds them: the definition fact and inline/requirement usage facts carry a
  `predicate`, and S1's golden captures full trees (operators, ordered operands). Item 2 owns
  `ExpressionIR` (its node algebra — literal, feature reference, operator, invocation, unit
  annotation, explicit-unsupported — is fixed in the concept, `:87`). Design must settle where
  Item 1's fact schema holds the predicate versus references Item 2's tree. A real cross-item
  coordination point — surface it to Item 2's design; do not resolve it silently in either repo.
- **Owner/scope grade for Item 5's `owning_part_def_qn` need.** This item carries `owner`
  (kind/name/qualified_name) and `scope`, plus `inherited_into` for inherited assertions. But
  `owner` is sometimes a `PartUsage` or `CalculationDefinition`, not a part-definition QN (S1
  golden: `direct_owned` → a `PartUsage`; `calc_owned` → a `CalculationDefinition`). Item 4/5 key
  multiplicity expansion by owning-definition + feature and expect an `owning_part_def_qn` grade
  (S3 carry-forward). Design must confirm whether `owner.qualified_name` + `inherited_into`
  suffice for Item 5 to derive the owning-part-definition identity in the inherited and
  direct-usage cases, or whether the schema needs an explicit resolved owning-part-def field.
  Stated as a coordination point, not resolved here.
- **Schema carrier: dataclass vs pydantic.** The existing shared surface mixes both
  (`data_models.py` uses `@dataclass`; `types.py` uses pydantic `BaseModel`). Which to use, and
  the byte-stable serialization mechanism (key ordering, float formatting, `None`/omitted-field
  policy), are design choices.
- **Version identifier scheme.** S1's fixture used the tag `constraint-fact-learning-test/v1`
  (test-only). The production version string, and how versioning interacts with the downstream
  snapshot v3 contract, are for design.
- **Where the JSON section lives.** The facts are a "section" that sysml-codegen snapshot v3
  consumes; there is no existing snapshot/manifest emitter in agentic-mbse to plug into today.
  Whether this item emits a standalone artifact, a CLI-surfaced section, or an in-memory
  structure only, is a design question. (The host document is downstream and out of scope.)

---

## Related Artifacts

- **Epic:** CONSTRAINT-EXEC, Item 1 — transmitted via the orchestrator brief at
  `.project/active/constraint-facts/briefs/spec.md`.
- **Concept (binding):** `.project/reference/constraint-execution-concept.md` — "Neutral
  Constraint Facts — agentic-mbse" (`:85`–`:91`), Required Invariants (`:136`–`:154`), and
  Appendix B / Next-Stage Handoff S1 `[AGENT]` blocks. Now readable in-repo and read directly for
  this revision; no contradiction with the spec's requirements was found. (During original
  authoring the concept was outside the allowed working directory and its content was transmitted
  via the S1 findings + brief; the one leaf-vocabulary rule that indirect transmission dropped —
  references are never pre-classified — is now carried forward as a requirement from `:87`.)
- **S1 spike (verified agent-grade evidence):**
  `.project/active/spike-constraint-fact-shapes/findings.md` — §2 (fact shapes / access
  quirks), §3 (type/unit evidence), §5 (equality gate and exact-unit restriction).
- **S1 committed artifacts:** `tests/fixtures/constraint_fact_shapes/{source_forms.sysml,
  type_units.sysml,golden.json}`, `tests/test_sysml/test_constraint_fact_shapes.py`,
  `tests/constraint_fact_learning.py` (capture module to retire/demote).
- **Existing extraction surface:** `src/agentic_mbse/sysml/syside_adapter.py` (subtype sweep +
  droppability); `src/agentic_mbse/sysml/data_models.py` and `types.py` (shared downstream
  types).
- **Design:** `.project/active/constraint-facts/design.md` (to be created).

---

**Next Steps:** After approval, proceed to `/_my_design`. Design must resolve the Item 1 / Item 2
predicate-representation boundary in coordination with Item 2's `ExpressionIR` design.
