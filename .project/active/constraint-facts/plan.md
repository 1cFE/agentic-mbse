# Implementation Plan: Neutral Constraint Facts — Production Schemas and Extraction

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 1
**Branch:** `constraint-exec-epic`

## Source Documents
- **Spec:** `.project/active/constraint-facts/spec.md`
- **Design:** `.project/active/constraint-facts/design.md` ← component details, dispatch order, decisions, invariants live here. This plan references it and does not restate it.
- **Design review:** `.project/active/constraint-facts/design-review.md` (Approved-with-must-fixes; the four MFs are discharged in design rev 2)
- **Extraction blueprint (to retire):** `tests/constraint_fact_learning.py` — the S1 capture module. Production keeps its access paths, replaces the two banned heuristics (`:172` namespace-prefix, `:380-381`/`:431` suffix-strip) with the design's structural discriminators.
- **Fixtures / semantic oracle:** `tests/fixtures/constraint_fact_shapes/{source_forms.sysml, type_units.sysml, golden.json}` (committed).

## Implementation Strategy

**Phasing rationale.** Imports point one way — leaves → usage facts → extractor — so the modules must be built in that order. `expression_facts.py` and `constraint_facts.py` are pure (no syside), so they land first and prove the byte-stable serialization contract (B4) with fast, offline unit tests. The extractor (`constraint_extraction.py`) is the only syside-touching module and carries the single biggest risk (B1: do the structural discriminators reproduce S1's six classifications and the dimension values?). It comes next, proven against the fixtures. The re-anchor test formalizes that proof. Retiring the capture module and re-pointing its kept tests is isolated to its own phase behind a suite-green gate. Final gates close out exports, lint, and the banned-heuristic guard.

**Critical path.** `expression_facts.py` → `constraint_facts.py` (+ `serialize`/`parse` + version constants) → `constraint_extraction.py` (dispatch order + MF4 dimension path) → re-anchor test → retire capture module → gates.

**First proof point (fast, offline).** Phase 1's byte-stable round-trip on hand-built facts at the pinned `(constraint-facts/v1, predicate-tree/v0)` pair. If `@dataclass` + `json.dumps(sort_keys=True, …)` does not round-trip byte-identically, the wire contract (B4) is wrong and everything downstream shifts — so prove it before touching syside.

**Central proof point (the B1 de-risk).** Phase 2's extraction over both fixtures: the six source forms come out distinct and each fact field matches the S1 golden's semantic value (decision fields excluded), with the dimension resolved to the real measurement-unit-def QN (`ISQBase::LengthUnit`) via the `mRef` traversal — no suffix strip. Run this before anything cosmetic. If a discriminator diverges, stop and revisit the discriminator, not the golden (design "De-risk first").

**Environment.** Live-SysIDE tests run in this repo's env via `uv run pytest …` — the license loads through `tests/conftest.py` (`load_dotenv()`), so pytest/script runs work; bare `python -c` does not. See CLAUDE.md.

**Overall validation.** Each phase starts with tests. Each phase has an automated gate. Phases are resumable from the checkboxes below.

---

## Phase 1: Leaf vocabulary + usage/def schemas + canonical JSON

### Goal
Land the two pure schema modules and the serializer. No syside. Proves the byte-stable wire contract (B4) offline, before any extraction risk.

### Assumption Under Test
`@dataclass` + `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=True, allow_nan=False)` over `dataclasses.asdict` round-trips byte-identically at a pinned version pair (design [D2](../constraint-facts/design.md#key-decisions), [B4](../constraint-facts/design.md#key-bets)).

### Test Stencil (Write This First)
`tests/test_sysml/test_constraint_facts_serialize.py` (NEW):
```python
def test_round_trip_is_byte_identical():
    facts = _hand_built_facts()          # minimal ConstraintFacts aggregate, all six-form-agnostic
    once = serialize(facts)              # canonical JSON str
    assert serialize(parse(once)) == once            # serialize(parse(serialize(f))) == serialize(f)

def test_every_field_present_absence_is_explicit_null():
    doc = json.loads(serialize(_hand_built_facts()))
    assert "membership_kind" in doc[...]  # present as null, never omitted (D3)

def test_schema_versions_are_pinned():
    doc = json.loads(serialize(_hand_built_facts()))
    assert doc["schema_version"] == "constraint-facts/v1"
    assert _some_predicate(doc)["predicate_schema_version"] == "predicate-tree/v0"

def test_non_finite_serialize_backstop():
    # allow_nan=False raises on a NaN/Inf literal that slipped past extraction (D2a backstop)
    with pytest.raises(ValueError):
        serialize(_facts_with_non_finite_literal())
```

### Changes Required
**See `design.md` for:** [Component Overview](../constraint-facts/design.md#component-overview) (field lists), [Key Decisions D1–D4, D9](../constraint-facts/design.md#key-decisions), [Required Invariants](../constraint-facts/design.md#required-invariants).

- [x] **`src/agentic_mbse/sysml/expression_facts.py`** (NEW) — leaf + predicate-tree node algebra, `@dataclass`, no syside/constraint imports:
  - [x] `FeatureReferenceFact` (source_name, target identity, target_types, chain segments — **no role tag**), `LiteralFact`, `UnitFact` (`unit: str|None`, `dimension: str|None`), `OperandTypeFact` (category, enumeration, `UnitFact`).
  - [x] `ExpressionFact` (predicate_schema_version, kind, operator|None, operands, `operand_type: OperandTypeFact|None`). `operand_type` hangs off **every leaf-bearing node — both feature-reference and literal** (N2), so `1 [m]` carries `category="quantity"` + `UnitFact`; non-leaf operator nodes carry `operand_type=None`.
  - [x] `PREDICATE_TREE_SCHEMA_VERSION = "predicate-tree/v0"` constant.
- [x] **`src/agentic_mbse/sysml/constraint_facts.py`** (NEW) — `@dataclass`, imports `expression_facts` only:
  - [x] `ConstraintDefinitionFact`, `ConstraintUsageFact`, `ConstraintSource` (tagged union: `form` + `effective_predicate_source`/`constraint_definition`/`referenced_feature_target`/`asserted_constraint`, N2), `OwnerFact` with `OwningDefinitionFact` (kind ∈ {part_def, calc_def, requirement_def, package} + qualified_name — D6), `ContextFact`, `ConstraintFacts` aggregate, `IdentityFact` (defined in `expression_facts.py` to keep the one-way import direction; re-exported from `constraint_facts.py` and `__init__.py`).
  - [x] `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"` constant.
  - [x] `serialize(facts) -> str` — canonical JSON per D2 over `dataclasses.asdict`; every field present, absence is explicit `null` (D3).
  - [x] `parse(text) -> ConstraintFacts` — reconstruct the aggregate so the round-trip goes through the typed layer.
- [x] Export the public schema types + `CONSTRAINT_FACTS_SCHEMA_VERSION` from `src/agentic_mbse/sysml/__init__.py` alongside the aggregation/data_models exports ([`__init__.py:6-22,90-115`](../../../src/agentic_mbse/sysml/__init__.py)).

### Validation
**Automated:**
- [x] `uv run pytest tests/test_sysml/test_constraint_facts_serialize.py` → all pass.
- [x] `uv run pytest tests/` → no regressions (1300 passed, 1 skipped, 33 deselected).
- [x] `uv run ruff check src/ tests/ && uv run mypy src/` → clean on the two new modules (pre-existing unrelated errors elsewhere in the repo, unchanged by this phase).

**What We Know Works After This Phase:** the wire contract round-trips byte-identically at the pinned version pair; every field is present (null when absent); the serialize-time non-finite backstop fires. The schema surface downstream imports exists and is exported.

---

## Phase 2: Production extractor — dispatch, dimension, neutralization (B1 core)

### Goal
Land `constraint_extraction.py`: sweep base `ConstraintUsage`, classify into the six forms with S1's type/membership-gated order (MF2), recover formals/actuals/inheritance, resolve operand leaf facts including the structural dimension path (MF4), and neutralize library enums. This collapses the central B1 risk.

### Assumption Under Test
The two banned heuristics have structural replacements that produce the **same** classifications and the **same** operand facts on the fixtures — with the dimension resolving to the real `ISQBase::LengthUnit` QN, not the fabricated `ISQBase::Length` strip artifact ([B1](../constraint-facts/design.md#key-bets); [structural dimension MF4](../constraint-facts/design.md#structural-dimension-resolution-mf4)).

### Test Stencil (Write This First)
Assert against the extractor directly (the full re-anchor is Phase 3). `tests/test_sysml/test_constraint_extraction.py` (NEW, or drive from the Phase 3 test skeleton):
```python
def test_six_forms_extract_and_are_distinct():
    facts = extract_constraint_facts(_load(SOURCE_FORMS))
    forms = {u.source.form for u in facts.usages}
    assert {"inline","definition_typed","named_usage_reference",
            "satisfy","requirement_constraint","plain_usage"} <= forms

def test_requirement_constraint_not_misclassified_as_inline():   # MF2 regression
    facts = extract_constraint_facts(_load(SOURCE_FORMS))
    assert _by_name(facts, "positive_limit").source.form == "requirement_constraint"
    assert _by_name(facts, "below_limit").source.form == "requirement_constraint"

def test_dimension_is_real_measurement_unit_def_qn():            # MF4
    facts = extract_constraint_facts(_load(TYPE_UNITS))
    op = _left_operand(facts, "quantity_convertible_unit")
    assert op.operand_type.unit.dimension == "ISQBase::LengthUnit"  # not ISQBase::Length
    assert op.operand_type.unit.unit == "SI::metre"

def test_direction_is_neutral_token():                           # M3 / no str(enum)
    facts = extract_constraint_facts(_load(SOURCE_FORMS))
    assert _some_actual(facts).direction in {"in","out","inout"}

def test_non_finite_literal_yields_extraction_diagnostic():      # D2a
    facts = extract_constraint_facts(_model_with_non_finite_literal())
    assert any(d.names_the_operand_and_location() for d in facts.diagnostics)
```

### Changes Required
**See `design.md` for:** [Architecture — extraction order and dispatch, steps 1–6](../constraint-facts/design.md#architecture) (authoritative pseudocode), [structural dimension MF4](../constraint-facts/design.md#structural-dimension-resolution-mf4) + [MF4 live-confirmation addendum](../constraint-facts/design.md#addendum-mf4-live-confirmation-orchestrator-2026-07-12), [Required Invariants](../constraint-facts/design.md#required-invariants). The S1 access paths to port live in `tests/constraint_fact_learning.py` (keep the paths, drop the two banned heuristics).

- [ ] **`src/agentic_mbse/sysml/constraint_extraction.py`** (NEW) — `extract_constraint_facts(model) -> ConstraintFacts` + private classify/recover helpers. Only module touching syside.
  - [ ] **Sweep** `elements_of_type(ConstraintUsage, include_subtypes=True)` (`syside_adapter.py:270`). NOT an `AssertConstraintUsage`-rooted sweep (misses `satisfy` — `[HARD]`).
  - [ ] **Classify (MF2 — restore S1's gate order, `constraint_fact_learning.py:164-177`):** membership gate (`RequirementConstraintMembership` → `requirement_constraint`, kind from `.kind`) → assert gate (`isinstance(AssertConstraintUsage)`; inside: `asserted_constraint is not self` → `named_usage_reference`; else no owned `result_expression` → `definition_typed`; else → `inline`) → satisfy gate (`isinstance(SatisfyRequirementUsage)` → `satisfy`) → fallback `plain_usage`. The `result_expression`-ownership test is the **within-assert** `[HARD]` replacement for the banned namespace-prefix test — **not** a whole-population classifier.
  - [ ] **Membership kind** from the owning `RequirementConstraintMembership.kind`, neutralized (`.name.lower()`), never the usage subtype (`[HARD]`).
  - [ ] **Formals** by owner-filtered `AttributeUsage` sweep (`owner is definition`); default = owned `FeatureValue` with `is_default=true`. NOT `ConstraintDefinition.parameters` (`[HARD]`).
  - [ ] **`owning_definition` (D6/MF3, tagged + total):** walk `owner` up to the first enclosing `PartDefinition`/`CalculationDefinition`/`RequirementDefinition`/`Package`; a `Package` always terminates → `kind=package` (e.g. `direct_owned`). Never falls through.
  - [ ] **Operand leaf facts:** category by type conformance; enumeration by owning `EnumerationDefinition`; **dimension via the structural path (MF4)** — unit-annotation operand: the `[` operator's unit operand `referent` → its typing chain's unit-def QN (select the type specializing `MeasurementUnit`/`SimpleUnit`, not positional `[0]`); quantity-feature operand: follow the value type's `mRef` to its most-specific unit-definition type (the addendum's confirmed traversal), `unit=null`, `dimension`=that QN. **No `removesuffix("Unit")`/`removesuffix("Value")`.**
  - [ ] **Neutralize library values:** `FeatureDirectionKind` → `in`/`out`/`inout`; enum-likes via `.name.lower()`. NOT `str(enum)` (`[HARD]` M3).
  - [ ] **Non-finite literal → structured extraction diagnostic** naming the operand + source location (D2a); not a serialize crash.
- [ ] Export `extract_constraint_facts` from `src/agentic_mbse/sysml/__init__.py`.

### Validation
**Automated:**
- [ ] `uv run pytest tests/test_sysml/test_constraint_extraction.py` → all pass; six forms distinct; `requirement_constraint` not misclassified; dimension is `ISQBase::LengthUnit`; direction is a neutral token; non-finite yields a diagnostic.
- [ ] `uv run pytest tests/` → no regressions.
- [ ] `uv run ruff check src/ tests/ && uv run mypy src/` → clean.

**What We Know Works After This Phase:** the production extractor reproduces S1's six classifications and operand facts from live SysIDE 0.8.4, with the structural dimension path and no banned heuristic. B1 is de-risked.

---

## Phase 3: Re-anchor the golden against the production extractor

### Goal
Rewrite `tests/test_sysml/test_constraint_fact_shapes.py` to run the **production** extractor over the two S1 fixtures, self-compare a regenerated production golden, and assert **fact fields only** against the S1 golden as semantic oracle. This rewrite removes the import of the capture module, leaving it orphaned for Phase 4.

### Assumption Under Test
Every S1 golden **fact** field (excluding `decision`) maps to a production field with equal semantic value, and the production format self-round-trips byte-identically over **real extracted facts** (not just hand-built ones).

### Test Stencil (Write This First)
Three ordered sub-steps per the brief — production extractor → production golden (self-comparing) → semantic-oracle comparison:
```python
def test_production_golden_self_compares():        # step 2: byte-compare regenerated vs stored
    facts = extract_constraint_facts(_load_both_fixtures())
    produced = serialize(facts)
    assert produced == (FIXTURE_DIR / "production_facts.json").read_text()

def test_round_trip_over_real_facts():             # byte-stable at pinned version pair
    facts = extract_constraint_facts(_load_both_fixtures())
    assert serialize(parse(serialize(facts))) == serialize(facts)

def test_fact_fields_match_s1_oracle():            # step 3: semantic-oracle, decision EXCLUDED
    facts = extract_constraint_facts(_load_both_fixtures())
    oracle = json.loads((FIXTURE_DIR / "golden.json").read_text())
    # membership/polarity/ownership/actuals/defaults/inheritance/operand facts
    # dimension asserted against ISQBase::LengthUnit (MF4), NOT the golden's ISQBase::Length strip
    assert _map_and_compare_fact_fields(facts, oracle)   # excludes type_units.equality_cases[].decision
```

### Changes Required
**See `design.md` for:** [Validation Approach](../constraint-facts/design.md#validation-approach), [Integration Strategy — oracle vs production golden, two distinct files (N4)](../constraint-facts/design.md#integration-strategy), [Potential Risks](../constraint-facts/design.md#potential-risks) (dimension change, non-atomic rewrite).

- [ ] **Generate `tests/fixtures/constraint_fact_shapes/production_facts.json`** from the production extractor (a distinct new artifact; **never overwrite `golden.json`**, which stays the read-only semantic oracle — N4).
- [ ] **Rewrite `tests/test_sysml/test_constraint_fact_shapes.py`** to import from `agentic_mbse.sysml` (production), **not** from `tests.constraint_fact_learning`:
  - [ ] Keep and re-point the fact-field tests (six forms distinct; membership/polarity/ownership/actuals/omitted-defaults/inheritance; compound Boolean tree; anonymous assertion by location; `owning_definition` present + tagged on every usage; no `str(enum)` in any value).
  - [ ] Map each S1 golden fact field → production field and assert value equality; assert the `dimension` value against the real `ISQBase::LengthUnit` QN (MF4), documenting inline that the S1 golden's `ISQBase::Length` is the retired strip artifact.
  - [ ] **Drop** the two decision-asserting functions (`test_equality_gate_is_decided_from_static_operand_facts`, `test_loader_diagnostics_are_golden_but_not_the_equality_gate`) — they assert Item 3's verdicts (review minor).

### Validation
**Automated:**
- [ ] `uv run pytest tests/test_sysml/test_constraint_fact_shapes.py` → all pass; production golden self-compares; real-fact round-trip byte-identical; every asserted fact field matches the oracle.
- [ ] `grep -rn "constraint_fact_learning" tests/` → **no hit in `test_constraint_fact_shapes.py`** (import removed; the module is now orphaned).
- [ ] `uv run pytest tests/` → no regressions.

**What We Know Works After This Phase:** the re-anchored golden passes against production; the S1 golden survives read-only as the oracle; the capture module has zero importers.

---

## Phase 4: Retire the capture module (its own phase + suite-green gate)

### Goal
Delete the now-orphaned S1 capture module and confirm the suite is green with no banned code left in the tree.

### Assumption Under Test
Nothing imports `tests/constraint_fact_learning.py` after Phase 3, so deletion is clean (design risk: the rewrite made the deletion atomic by removing the import first).

### Changes Required
**See `design.md` for:** [D7 (retire the capture module)](../constraint-facts/design.md#key-decisions), [Integration Strategy](../constraint-facts/design.md#integration-strategy).

- [ ] `grep -rn "constraint_fact_learning" tests/ src/` → confirm **zero** importers remain.
- [ ] Delete `tests/constraint_fact_learning.py` (D7 — it embeds the two banned heuristics at `:172` and `:380-381`/`:431`; keeping it alive keeps banned code and duplicate extraction logic in the tree).

### Validation
**Automated (suite-green gate):**
- [ ] `uv run pytest tests/` → full suite green after deletion.
- [ ] `uv run ruff check src/ tests/` → clean (no unused imports left by the deletion).

**What We Know Works After This Phase:** the retired capture path is gone; the suite is green without it.

---

## Phase 5: Final gates — round-trip, banned-heuristic guard, lint

### Goal
Close out the spec's success criteria: full suite green, ruff clean, byte-stable round-trip test present and green, and an explicit guard that neither banned heuristic reappears in production code.

### Assumption Under Test
No structural discriminator silently fell back to a banned heuristic, and the exported surface is complete for downstream import.

### Changes Required
**See `design.md` for:** [Validation Approach — banned-heuristic guard](../constraint-facts/design.md#validation-approach), [Required Invariants](../constraint-facts/design.md#required-invariants).

- [ ] **Banned-heuristic guard** — add a test (or codified review gate) asserting production source under `src/agentic_mbse/sysml/{expression_facts,constraint_facts,constraint_extraction}.py` contains:
  - [ ] no namespace-prefix classification of inline vs definition-typed (no `startswith("ConstraintFactShapeProbe::")`-style discriminator driving the `inline`/`definition_typed` branch),
  - [ ] no `removesuffix("Unit")` and no `removesuffix("Value")` dimension/quantity strip.
- [ ] Confirm the byte-stable round-trip test at the pinned `(constraint-facts/v1, predicate-tree/v0)` pair is present and green (Phase 1 hand-built + Phase 3 real-fact).
- [ ] Confirm `src/agentic_mbse/sysml/__init__.py` exports the public schema types, `extract_constraint_facts`, `serialize`, and both version constants.

### Validation
**Automated (final gates — spec success criteria):**
- [ ] `uv run pytest tests/` → full suite green.
- [ ] `uv run pytest tests/ -m ""` → slow/corpus tests also green (no regression).
- [ ] `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/` → clean.
- [ ] Banned-heuristic guard → green.

**What We Know Works After This Phase:** all spec success criteria met; the wire contract is byte-stable and version-pinned; no banned heuristic in production; the shared surface is exported for downstream repos.

---

## Environment Setup
See CLAUDE.md. Live-SysIDE tests run via `uv run pytest …` (license loads through `tests/conftest.py`); bare `python -c` will not have the license. Do not `git commit` — the orchestrator commits.

## Risk Management
**See [`design.md#potential-risks`](../constraint-facts/design.md#potential-risks) for the full analysis.**

- **B1 discriminator divergence** (Phase 2): the re-anchor fails loudly on any divergence; run extraction assertions before anything cosmetic; if it diverges, fix the discriminator, not the golden.
- **Dimension value change (MF4)** (Phase 2/3): production `dimension` is `ISQBase::LengthUnit`, not the S1 golden's fabricated `ISQBase::Length`; the re-anchor asserts against the real QN and documents the change as a decision preservation.
- **Non-atomic test rewrite** (Phase 3→4): the Phase 3 rewrite removes the capture-module import before Phase 4 deletes the file, so the suite is green at both boundaries.
- **`cached_result_type` absent on a leaf** (Phase 2): category must be an explicit `unknown`/`unresolved` state, never a crash or omission (`unresolved_operand` fixture case covers it).
- **Float byte-stability** (Phase 1): rests on Python's round-trip `repr`; fixtures are finite decimals; non-finite is rejected at extraction (D2a) with `allow_nan=False` as the backstop.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
**Completed:** 2026-07-12
**Actual Changes:**
- Created `src/agentic_mbse/sysml/expression_facts.py`: `IdentityFact`, `UnitFact`, `OperandTypeFact`, `FeatureReferenceFact`, `LiteralFact`, `ExpressionFact`, `PREDICATE_TREE_SCHEMA_VERSION`.
- Created `src/agentic_mbse/sysml/constraint_facts.py`: `LocationFact`, `OwningDefinitionFact`, `OwnerFact`, `ConstraintSource`, `FormalFact`, `ActualFact`, `ConstraintDefinitionFact`, `ConstraintUsageFact`, `RedefinitionFact`, `ContextFact`, `ExtractionDiagnosticFact`, `ConstraintFacts`, `CONSTRAINT_FACTS_SCHEMA_VERSION`, `serialize()`, `parse()`.
- Exported both modules' public surface from `src/agentic_mbse/sysml/__init__.py`.
- Added `tests/test_sysml/test_constraint_facts_serialize.py` (5 tests, hand-built facts — no syside).

**Issues:**
- None.

**Deviations:**
- `IdentityFact` lives in `expression_facts.py`, not `constraint_facts.py` as the plan's bullet list literally groups it. `FeatureReferenceFact.target` (in `expression_facts.py`) needs an identity fact too, and the design's one-way import rule (`expression_facts` imports nothing from `constraint_facts`) means the shared identity type has to live at the leaf-module level. `constraint_facts.py` imports and reuses it; `__init__.py` exports it from both. No field or shape change — purely a module-placement call.
- Added `_identity_from_dict_required`/`_expression_from_dict_required` parse helpers (not in the plan/design) to satisfy mypy: several fields (`ConstraintDefinitionFact.identity`, `ConstraintUsageFact.identity`/`.scope`, `ContextFact.identity`, and every `ExpressionFact` inside an `operands` list) are non-Optional per the dataclass definitions, so `parse()` needs non-Optional reconstruction paths alongside the Optional ones used for genuinely-nullable fields (e.g. `ConstraintSource.constraint_definition`).

### Phase 2 Completion

### Phase 3 Completion

### Phase 4 Completion

### Phase 5 Completion

---

**Status:** Draft → In Progress → Complete
</content>
</invoke>
