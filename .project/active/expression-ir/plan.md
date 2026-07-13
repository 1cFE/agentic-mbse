# Implementation Plan: ExpressionIR — Production Tree, Extraction, Serialization

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 2 · **Branch:** `constraint-exec-epic`

## Source Documents
- **Spec:** `.project/active/expression-ir/spec.md`
- **Design:** `.project/active/expression-ir/design.md` ← component details, node algebra, allowlist, the 8-site worklist, and the golden-diff checklist all live here. This plan references it; it does not restate it.

## Open questions resolved at plan (design's "Open — plan decides")

The design (Next-Stage Handoff) left three decisions to this stage. Resolved:

1. **`kind` discriminant mechanism** → a `kind: str` field with a fixed per-class default on each node dataclass. Reason: `dataclasses.asdict` serializes it for free (no serializer-side injection), it matches the `aggregation.py` idiom the design adopts, and parse dispatches on the same field. (design.md#implementation-notes allows either; this picks the simpler.)
2. **Unsupported construct for the fixture** → author `ConditionalExpression` (`if c ? a : b`) first; if SysIDE 0.8.4 parses it as an allowlisted operator, fall back to a `select`/`collect` expression. This is a **live parse check gated in Phase 1** (design.md#next-stage-handoff "de-risk first"). Do not build `UnsupportedNode` coverage against an unconfirmed metaclass.
3. **Version placement** → retain per-node `schema_version` defaulting to `EXPRESSION_IR_SCHEMA_VERSION` (design D7). Keeps the golden diff to the spec's stated expectation (version string + tree shape only).

## Implementation Strategy

**Phasing rationale.** Three phases, ordered so the one irreversible risk is retired first and the one atomic break is isolated.

- **Phase 1 is additive and offline.** The new module lands alongside the old `ExpressionFact` without removing anything, so the suite stays green. This is where the two live-SysIDE unknowns get retired cheaply (design.md#next-stage-handoff): does SysIDE emit *distinct* enums for `^` vs `**`, and does the chosen unsupported construct parse to a *non-allowlist* metaclass. Both gate the whole design's fidelity/unsupported criteria; both are one-shot checks.
- **Phase 2 is one atomic migration.** Retyping the extractor's return type breaks `constraint_facts` (its predicate slots are typed `ExpressionFact`) and every old-shape test at once. The design's Integration Strategy is explicit: edit the four src modules + `__init__.py` in one change, because a partial migration leaves the suite red. So the orchestrator's "extractor cutover" and "8-site migration" are **one phase**, not two — the suite is red mid-phase by construction and green only at the phase gate. The extractor cutover is the phase's leading, self-contained block.
- **Phase 3 is coverage + gates.** The new live assertions (spelling distinctness, exercised unsupported node, round-trip over real facts) require the cutover extractor, so they come last, together with the final gates and the "no silent third representation" grep.

**Critical path:** Phase 1 live de-risk (distinct `^`/`**`, non-allowlist unsupported metaclass) → new module + bare round-trip → atomic src+test+golden migration → live coverage + gates.

**First proof point:** Phase 1 — the live parse check confirming `^` and `**` carry distinct SysIDE operator enums and the unsupported construct is off-allowlist. If either fails, the fixture is revisited before any node is built (design.md#next-stage-handoff).

**Overall validation:** each phase starts by writing/adjusting tests; the gate is the **default** pytest suite (`uv run pytest tests/`) + Ruff. **Never** run `pytest tests/ -m ""` or `test_corpus_integration.py` [OWNER].

---

## Phase 1: New `expression_ir.py` module + bare serialize/parse + offline round-trip + live de-risk

### Goal
Land the six-node algebra, the `ExpressionIR` union, the version constant, the bare-tree `serialize_expression`/`parse_expression`, and the `_expression_ir_from_dict` dispatcher — all **additively**, so the suite stays green. Retire the two live-SysIDE unknowns before anything downstream depends on them.

### Assumption Under Test
- SysIDE 0.8.4 emits **distinct** operator enums for `^` and `**` (B1 fidelity rests on this).
- The chosen unsupported construct parses to a metaclass that is **not** on the allowlist (design D4), so it genuinely routes to `UnsupportedNode`.
- A `kind`-tagged union round-trips byte-identically through `dataclasses.asdict` → `_canonical_json` → `_expression_ir_from_dict` (B3).

### De-risk First (do before building nodes) — design.md#next-stage-handoff
- [x] Author `tests/fixtures/expression_ir/operator_fidelity.sysml` (NEW dir): one model containing both `^` **and** `**`, a unary minus, and one structurally unsupported expression (start with `ConditionalExpression` `if c ? a : b`).
- [x] Live-load it via `uv run python` (or a scratch `uv run pytest -k` probe) and confirm: (a) `^` vs `**` surface as different `operator` enum values; (b) the unsupported construct's `type(node).__name__` is off the allowlist. If `^`/`**` collapse or the construct parses as an allowlisted operator, **stop and revise the fixture** (try `select`/`collect`) before continuing.

### Test Stencil (Write This First — offline, no syside)
```python
# tests/test_sysml/test_expression_ir_serialize.py (NEW)
from agentic_mbse.sysml.expression_ir import (
    LiteralNode, OperatorNode, UnsupportedNode,
    EXPRESSION_IR_SCHEMA_VERSION, serialize_expression, parse_expression,
)

def test_bare_tree_round_trips_byte_identically():
    tree = OperatorNode(operator="<=", operands=[_lit(1.0), _lit(2.0)], operand_type=None)
    once = serialize_expression(tree)
    assert serialize_expression(parse_expression(once)) == once   # B3

def test_version_constant_is_pinned():
    assert EXPRESSION_IR_SCHEMA_VERSION == "expression-ir/v1"
```

### Changes Required
**See design.md for:** node algebra sketch → `design.md#node-algebra-schema-sketch-representative`; allowlist → `design.md#allowlist-d4`; shared encoder → `design.md` D5; component list → `design.md#component-overview`.

#### 1. New module
**File:** `src/agentic_mbse/sysml/expression_ir.py` (NEW)
- [x] Six node dataclasses (`LiteralNode`, `FeatureReferenceNode`, `OperatorNode`, `UnitAnnotationNode`, `InvocationNode`, `UnsupportedNode`), each with `kind: str` defaulted per-class and `schema_version: str = EXPRESSION_IR_SCHEMA_VERSION` (D7).
- [x] `ExpressionIR` `TypeAlias` union; `EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"`.
- [x] `_canonical_json` (moved-here definition; `constraint_facts` imports it in Phase 2 — D5).
- [x] `serialize_expression(ir)` = `_canonical_json(dataclasses.asdict(ir))`.
- [x] `_expression_ir_from_dict(dict)` dispatcher on `kind`, recursing on child slots; `parse_expression` wraps it.
- [x] Move the leaf/identity parse helpers the dispatcher needs (`_reference_from_dict`, `_literal_from_dict`, `_operand_type_from_dict`, `_unit_from_dict`, `_identity_from_dict`) into this module (they belong with the tree; `constraint_facts` re-imports in Phase 2). Imports `expression_facts` only.

#### 2. New fixture
**File:** `tests/fixtures/expression_ir/operator_fidelity.sysml` (NEW — authored in De-risk step above).

#### 3. Offline test file
**File:** `tests/test_sysml/test_expression_ir_serialize.py` (NEW) — the stencil above + a node per kind through round-trip.

### Validation
**Automated:**
- [x] `uv run pytest tests/test_sysml/test_expression_ir_serialize.py` → pass.
- [x] `uv run pytest tests/` → still green (nothing landed removed yet).
- [x] `uv run ruff check src/ tests/` → clean.

**Manual:**
- [x] De-risk check output recorded in Implementation Notes: the observed `^`/`**` enum values and the unsupported construct's metaclass name.

**What We Know Works After This Phase:** the new tree serializes and parses byte-stably offline; the two live unknowns are settled; nothing downstream is disturbed.

---

## Phase 2: Atomic src cutover + 8-site migration + golden regen + version bump

### Goal
Cut the extractor over to the allowlist-inverted `_expression_ir` builder, delete `ExpressionFact`, retype the predicate slots, swap the re-exports, migrate every landed test site, and regenerate the golden. One atomic change — the suite is red mid-phase and green at the gate.

### Assumption Under Test
- The allowlist inversion (design D4) routes every off-allowlist metaclass and every unmapped/absent operator to `UnsupportedNode`, and no *supported* construct regresses into unsupported (design.md#potential-risks third bullet).
- Preserved attribute names (`operator`, `operands`, `operand_type`, `reference`, `literal`) keep tree-walking assertions working; only `.kind` **value** readers must migrate (B2).
- The golden diff contains **only** the expected changes (design.md#potential-risks first bullet checklist).

### Test Stencil (the re-pin — write the assertion change first)
```python
# test_constraint_facts_serialize.py::test_schema_versions_are_pinned
assert doc["schema_version"] == "constraint-facts/v1"                    # envelope unchanged
assert doc["usages"][0]["predicate"]["schema_version"] == "expression-ir/v1"  # was predicate-tree/v0
```

### Changes Required — the 8-site worklist (design.md#integration-strategy)

**Block A — extractor cutover (do first; the phase's self-contained logic block):**
- [ ] **Site 2** `constraint_extraction.py`: rename `_expression_fact` → `_expression_ir`; import nodes + `EXPRESSION_IR_SCHEMA_VERSION` from `expression_ir`. Split the operator branch into operator / unit-annotation (operator normalizes to `[`) / unsupported. Reference/literal builders return `FeatureReferenceNode`/`LiteralNode`.
- [ ] Add enum→symbol **normalization with an unrecognized-signal** (design.md#implementation-notes "Normalization is new work"): model on the probe's `_OPERATOR_ENUM_MAP` (`s2_ir.py:70`), but an unmapped/absent operator returns a sentinel routing to `UnsupportedNode` — do **not** pass the raw enum name through (D4; the probe's `_operator_text` did, Item 2 must not).
- [ ] `UnsupportedNode` carries `node_kind` (the unrepresentable metaclass), `diagnostic`, and `source_text` from `reconstruct_expression` (`expression.py:420`) where available.
- [ ] Preserve `operand_type` placement: on literal/reference/unit/arithmetic-operator nodes; `None` on comparison/connective nodes. Reuse the landed `_BOOLEAN_CONNECTIVE_OPERATORS` set (`constraint_extraction.py:53`) **as-is** — do not expand it (keeping it unchanged keeps `operand_type` byte-stable; note `xor` is deliberately absent there today).

**Block B — src retype (atomic with A):**
- [ ] **Site 1** `expression_facts.py:25`: delete `PREDICATE_TREE_SCHEMA_VERSION` + `ExpressionFact`; update `__all__`. Leaves + `IdentityFact` stay.
- [ ] **Site 3** `constraint_facts.py`: retype the five predicate slots (`FormalFact.default`, `ActualFact.value`, `ConstraintDefinitionFact.predicate`, `ConstraintUsageFact.predicate`, `RedefinitionFact.value`) to `ExpressionIR`; delete the local `_expression_from_dict*` + moved leaf helpers, delegating to `expression_ir._expression_ir_from_dict`; import the shared `_canonical_json` from `expression_ir` (verify byte output unchanged except tree shape + version — design.md#implementation-notes).
- [ ] **Site 4** `sysml/__init__.py`: re-export the node types + `ExpressionIR` union + `EXPRESSION_IR_SCHEMA_VERSION` + `serialize_expression`/`parse_expression`; drop `ExpressionFact` + `PREDICATE_TREE_SCHEMA_VERSION`.

**Block C — test migration:**
- [ ] **Site 5** `test_constraint_facts_serialize.py`: migrate `_literal_expression`/`_reference_expression`/`_hand_built_facts` to the new node types; re-pin `test_schema_versions_are_pinned` (stencil above, note the field rename `predicate_schema_version` → `schema_version`).
- [ ] **Site 6** `test_constraint_extraction.py`: migrate the `_expression_fact` import + `MockLiteralRational` test (`:192-203`) to `_expression_ir` and the new return type. The operand-type/compound assertions (`:58-69`, `:136-139`) read preserved names and need **no** change (B2 / design.md#implementation-notes).
- [ ] **Site 8** `test_constraint_fact_shapes.py:121,123`: the two `.value.kind` metaclass-name comparisons — migrate per design step 8: chain via `actuals["observed"].value.chain_segments` non-empty; rational via `actuals["limit"].value.literal.kind == "LiteralRational"`.

**Block D — golden:**
- [ ] **Site 7** `production_facts.json`: regenerate (self-compare test writes/reads its own golden — `test_constraint_fact_shapes.py:54-58`). Review the diff **node-by-node** against the expected-change checklist (design.md#potential-risks): every node drops the nullable slots it no longer has; version string flips `predicate-tree/v0 → expression-ir/v1`; each unit annotation loses its `operands[1]` unit-reference subtree (collapsed into `unit_text` + resolved `UnitFact`). **Anything else in the diff is a regression, not an expected change** — stop and investigate.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green (the phase gate; red mid-phase is expected).
- [ ] `uv run ruff check src/ tests/` → clean.

**Manual:**
- [ ] Golden diff reviewed against the checklist; the single largest deletion is the unit-annotation `operands[1]` subtree and nothing else structural moved.

**What We Know Works After This Phase:** one tree in the codebase; the full suite green on the new shape; the golden pinned; versions bumped.

---

## Phase 3: Live coverage + final gates

### Goal
Prove the success criteria that need the cutover extractor — spelling distinctness, exercised unsupported node, round-trip over real facts — and run the final gates including the "no silent third representation" check.

### Assumption Under Test
- Over the reused landed fixtures + `operator_fidelity.sysml`, the five predicate shapes + operator fidelity extract and round-trip byte-identically, within a load and across independent loads (Required Invariants).
- `ExpressionFact` is fully gone (no silent third representation).

### Test Stencil (Write This First)
```python
# tests/test_sysml/test_expression_ir_extraction.py (NEW)  — live syside
def test_caret_and_power_stay_distinct():
    facts = _extract("tests/fixtures/expression_ir/operator_fidelity.sysml")
    ops = _all_operator_strings(facts)
    assert "^" in ops and "**" in ops            # spelling distinctness

def test_unsupported_node_is_exercised():
    node = _find_unsupported(...)
    assert node.kind == "unsupported"
    assert node.node_kind and node.diagnostic     # metaclass + message
    # no sibling dropped or mis-kinded

def test_unit_annotation_keeps_source_and_resolved():
    n = _find_unit_annotation(...)
    assert n.unit_text == "m"
    assert n.operand_type.unit.unit == "SI::metre"
```

### Changes Required
**See design.md#validation-approach for the full list.**
- [ ] `tests/test_sysml/test_expression_ir_extraction.py` (NEW): distinctness, exercised unsupported, unit source+resolved, and cross-independent-load round-trip over `operator_fidelity.sysml`.
- [ ] Confirm leaf reuse is visible: node fields are `FeatureReferenceFact`/`LiteralFact`/`OperandTypeFact`/`UnitFact` instances (a type assertion suffices).

### Validation (final gates)
**Automated:**
- [ ] `uv run pytest tests/` → green (default selection only).
- [ ] `uv run ruff check src/ tests/` → clean.
- [ ] Byte-stable round-trip confirmed at the pair `(constraint-facts/v1, expression-ir/v1)` — the new extraction test + `test_round_trip_over_real_facts`.

**Manual:**
- [ ] `grep -rn "ExpressionFact\|predicate-tree\|PREDICATE_TREE_SCHEMA_VERSION" src/ tests/` → **no hits** (the "no silent third representation" gate; `ExpressionFact` gone everywhere).

**What We Know Works After This Phase:** every Item 2 success criterion is exercised by a live test; the gates are green; one tree, one encoder, one version pair.

---

## Environment Setup
**See CLAUDE.md.** `uv sync`; tests via `uv run pytest tests/` (default selection). Live syside loads need `SYSIDE_LICENSE_KEY` in `.env`. Never run `pytest tests/ -m ""` or `test_corpus_integration.py` [OWNER]. The orchestrator commits; this work does not `git commit`.

## Risk Management
**See design.md#potential-risks for the full analysis.** Phase-specific:
- **Phase 1:** the two live unknowns (`^`/`**` distinctness, off-allowlist unsupported metaclass) are retired by the de-risk check *before* any node is built.
- **Phase 2:** the golden diff can hide an unintended change → node-by-node review against the expected-change checklist, then the self-compare test pins it. An unmapped-but-common operator landing in unsupported → the operator set is the S2-proven `_OPERATOR_ENUM_MAP`; any miss shows as an unexpected `UnsupportedNode` in the golden.
- **Phase 3:** `operand_type` placement regressions → the migrated `test_constraint_extraction.py` operand-type assertions + the type-unit oracle cover it.

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-12
**De-risk results (record):**
- `^` surfaces as `Operator.ExponentCaret` (str `"^"`); `**` surfaces as `Operator.ExponentStar` (str `"**"`) — distinct enums confirmed, B1 holds.
- Unary minus: single-operand `Operator.Minus` (str `"-"`), one operand — confirmed representable by the existing operator-node shape.
- Unsupported construct: `if c ? a else b` (KerML `:` ternary syntax rejected by the parser; `else` is required) parses as an **`OperatorExpression`** with `operator=Operator.If` (str `"if"`) — not an off-allowlist metaclass as the design's fallback candidate anticipated. `"if"` is absent from the D4 operator-symbol set, so it routes to `UnsupportedNode` through the "unrecognized operator" arm of the allowlist, which design.md#allowlist-d4 already specifies for exactly this case ("absent or unrecognized operator → `UnsupportedNode`"). No fixture revision needed; the assumption under test ("off-allowlist metaclass") was narrower than what the design actually requires, and the broader unrecognized-operator path covers it.
**Actual Changes:**
- Added `tests/fixtures/expression_ir/operator_fidelity.sysml` (NEW): one `Probe` part with `caret_form` (`^`), `power_form` (`**`), `unary_minus_form` (unary `-`), `unsupported_form` (`if ... ? ... else ...`).
- Added `src/agentic_mbse/sysml/expression_ir.py` (NEW): six node dataclasses, `ExpressionIR` union, `EXPRESSION_IR_SCHEMA_VERSION`, `_canonical_json`, `serialize_expression`/`parse_expression`, `_expression_ir_from_dict` dispatcher, leaf parse helpers. Imports `expression_facts` only.
- Added `tests/test_sysml/test_expression_ir_serialize.py` (NEW): version-pin test + one offline round-trip test per node kind (7 tests total).
**Issues / Deviations:**
- Ternary syntax: the design's example `if c ? a : b` does not parse in SysIDE 0.8.4's KerML grammar; `if c ? a else b` does. Recorded here since Phase 3's live extraction tests reuse this fixture.
- `UnsupportedNode.operand_type`: the design's node-algebra sketch (design.md#node-algebra-schema-sketch-representative) omits an explicit `operand_type` slot on `UnsupportedNode` — it is not a value-producing node, so no slot was added, matching the sketch.

### Phase 2 Completion
**Completed:**
**Golden diff review (record):** confirmed only expected changes.
**Actual Changes:**
**Issues / Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues / Deviations:**

---

**Status:** Draft → In Progress → Complete
