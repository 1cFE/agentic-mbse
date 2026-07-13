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
- [ ] For every extracted usage fact, these facts match S1's golden values: membership kind,
      polarity, ownership/scope, actuals (with formal targets), omitted defaulted formals, and
      inheritance/retyping facts.
- [ ] `ConstraintDefinitionFact` carries the reusable predicate, its formals with defaults,
      and source identity; each usage fact carries **exactly one** `ConstraintSource` naming
      its form.
- [ ] Neither fixture-coupled heuristic appears in production code: no namespace-prefix
      discrimination of inline vs definition-typed, and no `Unit`-suffix stripping for quantity
      dimension.
- [ ] The facts serialize to a **versioned** JSON section that round-trips **byte-stably**.
- [ ] Golden tests are re-anchored from S1's fixtures against the production extractor; S1's
      test-only capture module is retired or clearly demoted to fixture tooling.
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
- **[INHERITED]** Exact unit is a **conditional** fact, not a universally recoverable field. A
  feature typed only as a dimension (e.g. `LengthValue`) proves the dimension, not one runtime
  unit. The schema must represent "dimension known, exact unit unknown" as a first-class state,
  not silently omit it. *(S1 `[AGENT]` verdict — `findings.md` §5; concept: silence is never an
  outcome. Note: the *eligibility decision* that consumes this state is Item 3, not here.)*

### Serialization

- **[NEED]** The facts serialize to a JSON section that carries an explicit **schema version**
  and round-trips **byte-stably** (serialize → parse → serialize is identical). *(Epic Item 1
  success criteria; concept: the facts are the downstream contract.)*
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
- **[NEED]** S1's test-only capture module (`tests/constraint_fact_learning.py`) is retired, or
  clearly demoted to fixture-generation tooling with no production role. *(Epic Item 1 scope
  §3; S1 explicitly marked it non-production — `findings.md` §4.)*

## Non-Goals

- **Eligibility / executable-profile decisions.** Which facts a runtime may execute — the
  equality/unit gate, what blocks — is Item 3. This item captures the *facts*, including
  "dimension known, exact unit unknown"; it does not decide what to do with them.
- **Expression tree internals / `ExpressionIR`.** Item 2 owns the canonical expression
  representation. This item owns the fact vocabulary that Item 2 adopts (see Open Questions for
  the boundary). It does not define the full expression IR.
- **Any sysml-codegen consumption.** Downstream lowering and snapshot v3 wiring are out of
  scope; this item ships the producer side only.
- **Re-deciding S1's semantic verdicts.** The equality/unit gate table and the exact-unit
  restriction are settled S1 evidence, carried forward, not relitigated here.

## Open Questions / Deferred to design

- **Predicate representation — the Item 1 / Item 2 boundary.** Both the definition fact and the
  inline/requirement usage facts carry a `predicate`, and actuals/defaults carry expression
  values. S1's golden captures full predicate trees (operators, operands, feature-reference and
  literal leaves with resolved targets and types). But Item 2 owns `ExpressionIR`. Design must
  settle **how much of the predicate representation this item freezes** versus defers: the
  guidance is that this item owns the leaf fact vocabulary (feature-ref and literal field
  shapes) that Item 2's `ExpressionIR` adopts, while Item 2 owns the tree structure. This is a
  real cross-item coordination point — surface it to Item 2's design, do not resolve it
  silently in either repo.
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
- **Concept (binding, but see note):** `~/1cfe/sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  — "Neutral Constraint Facts — agentic-mbse" section, Appendix B (S1), and Next-Stage
  Handoff S1 `[AGENT]` blocks. **Note:** this file sits outside the session's allowed working
  directory and was not directly readable during spec authoring (harness path guard). Its
  binding content for this item was taken from two sources that transmit it: the S1 findings
  (which record the Appendix B S1 result and carry-forwards) and the orchestrator brief (which
  transmits the settled Design Principles and the epic item text). Design should re-read the
  concept directly if access allows, and surface any contradiction loudly.
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
