# Spec: V2 Validation — FORMULA Exemption in `adr002.py`

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-09 20:54:03 UTC
**Complexity:** MEDIUM
**Branch:** adr004-005
**Epic:** EPIC-COMPATTR-001, Item 1

---

## Business Goals

### Why This Matters

The sysml-codegen ATTR-EXPR epic (Phase 2) added support for FORMULA computed attributes — expressions like `attribute area = length * width` that generate synthetic pipeline modules automatically. ADR-002 has been amended to permit these patterns. However, the agentic-mbse V2 validator (`check_static_expressions()` in `adr002.py`) still flags them as `V2_DYNAMIC_EXPRESSION` violations.

This creates a direct contradiction: the codegen pipeline accepts and processes FORMULA patterns, but the validation pyramid rejects them. Modelers who follow the updated ADR-002 guidance get false errors. This is the single highest-priority upstream change identified by the integration research.

### Success Criteria

- [x] `agentic-mbse validate` passes on models containing FORMULA computed attributes with zero false V2 violations
- [x] EXPOSE_COMPUTED and true derived expressions (calc output refs) are still correctly flagged as V2 violations
- [x] Zero regressions in existing V2/V1/V4 test coverage

### Priority

P1 — blocking. Items 2-4 of the epic (docs, commands, templates) describe patterns that the validator rejects until this is fixed.

---

## Problem Statement

### Current State

`check_static_expressions()` in `adr002.py:418-510` implements a 3-path decision:

1. No feature refs after std lib filtering → TRUE STATIC → OK
2. `_is_expose_pattern()` matches → EXPOSE → OK
3. Everything else → `V2_DYNAMIC_EXPRESSION` violation

Path 3 catches FORMULA patterns like `attribute area = length * width` because the expression has feature references (`length`, `width`) that aren't EXPOSE. The function treats all non-EXPOSE feature refs as violations, with no distinction between sibling attribute refs (FORMULA) and calc output refs (true derived expressions).

### Desired Outcome

A 4-path decision:

1. No feature refs → TRUE STATIC → OK
2. EXPOSE pattern → OK
3. **FORMULA pattern (all refs are sibling attributes, no calc output refs) → OK**
4. Everything else → violation

The FORMULA check must be consistent with ADR-005's classification: an expression is FORMULA when ALL feature references resolve to sibling attributes on the same owning part, with no `FeatureChainExpression` nodes (no dotted paths to calc outputs or other parts).

---

## Scope

### In Scope

- New `_is_formula_pattern()` function in `adr002.py`
- Integration into `check_static_expressions()` between the EXPOSE check and the violation
- Update `check_static_expressions()` docstring to reflect the new FORMULA exemption path
- New SysML test fixture (`v2_formula_pattern.sysml`) covering FORMULA, EXPOSE_COMPUTED, and mixed patterns
- New test cases in `tests/test_sysml/test_adr002.py`

### Out of Scope

- Pattern doc updates (`adr002-calculations.md`, `expose-pattern.md`) — Item 2
- Agent command changes (`implement-model.md`, `design-model.md`) — Item 3
- Template changes (`MODELING_GUIDE.md.template`) — Item 4
- Changes to `extract_feature_refs()` or `ExpressionRef` — already sufficient
- Changes to `_is_expose_pattern()` — works correctly as-is
- Qualified name resolution strategy (owner-based vs qualified-name-based sibling detection) — deferred to design stage

### Edge Cases & Considerations

- **EXPOSE_COMPUTED** (`attribute adj = calc.output * 0.95`): OperatorExpression wrapping a FeatureChainExpression. The ref to `calc.output` must NOT pass the FORMULA check — it has a different owner (the CalcDef) or is identified as a calc output.
- **Mixed** (`attribute x = sibling_a + calc.output`): Some refs are siblings, some are calc outputs. Must NOT be exempted — any calc output ref disqualifies FORMULA.
- **Chain FORMULA** (`attribute cost = area * rate` where `area` is itself computed): MUST be exempted. All refs are siblings on the same part, regardless of whether they are literal or computed. The compiler's chain-blindness is a feature.
- **Literal mixed with ref** (`attribute p_net_kw = p_net_mw * 1000.0`): MUST be exempted. `1000.0` is a `LiteralRational` (not a feature ref), `p_net_mw` is a sibling ref. `extract_feature_refs()` returns only `[p_net_mw]`.
- **Conservative default**: If the function cannot determine whether all refs are siblings, it must return False (don't exempt). This matches `_is_expose_pattern()`'s design.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic item definition and integration research unless marked [INFERRED].

1. **FR-1**: `_is_formula_pattern(attr, expr, calc_outputs)` SHALL return True when ALL feature references in the expression resolve to sibling attributes on the same owning part and NONE are calc output references.

2. **FR-2**: `_is_formula_pattern()` SHALL return False when ANY feature reference is a calc output reference (as determined by existing `_is_calc_output_reference()` or equivalent logic — approach to be evaluated in design).

3. **FR-3**: `_is_formula_pattern()` SHALL return False when the expression is a `FeatureChainExpression` (dotted path). FORMULA patterns use `OperatorExpression` with `FeatureReferenceExpression` operands, not chained references.

4. **FR-4**: `_is_formula_pattern()` SHALL return False (conservative default) when any ref cannot be classified.

5. **FR-5**: `check_static_expressions()` SHALL call `_is_formula_pattern()` after the EXPOSE check and before the violation, adding a `continue` branch for FORMULA patterns.

6. **FR-6**: [INFERRED] The `check_static_expressions()` docstring SHALL be updated to document the FORMULA exemption path, referencing ADR-002 Amendment (2026-02-09) and ADR-005.

7. **FR-7**: A new SysML test fixture SHALL cover the following patterns:
   - Simple FORMULA: `attribute area = length * width` → no V2 violation
   - Chain FORMULA: `attribute cost = area * rate` (where `area` is computed) → no V2 violation
   - FORMULA with literal operand: `attribute p_net_kw = p_net_mw * 1000.0` → no V2 violation
   - EXPOSE_COMPUTED: `attribute adj = calc.output * 0.95` → V2 violation
   - Mixed: `attribute x = sibling_a + calc.output` → V2 violation

8. **FR-8**: All existing V2, V1, and V4 tests SHALL continue to pass with zero regressions.

---

## Acceptance Criteria

### Core Functionality

- [x] `_is_formula_pattern()` correctly identifies FORMULA patterns (sibling-only refs, no FeatureChain, no calc output refs)
- [x] `check_static_expressions()` exempts FORMULA patterns via new `continue` branch
- [x] `check_static_expressions()` docstring updated with FORMULA exemption documentation

### Test Coverage

- [x] Test: `attribute area = length * width` (simple FORMULA) → no V2 violation
- [x] Test: `attribute cost = area * rate` (chain FORMULA) → no V2 violation
- [x] Test: `attribute p_net_kw = p_net_mw * 1000.0` (FORMULA + literal) → no V2 violation
- [x] Test: `attribute adj = calc.output * 0.95` (EXPOSE_COMPUTED) → V2 violation
- [x] Test: `attribute x = sibling_a + calc.output` (mixed refs) → V2 violation
- [x] Test: existing EXPOSE patterns → still pass (no regression)
- [x] Test: existing true static patterns → still pass (no regression)
- [x] Test: existing derived expression violations → still caught (no regression)

### Quality & Integration

- [x] `uv run pytest tests/` — all existing tests pass, zero regressions (886 passed, 1 skipped)
- [x] `uv run mypy src/` — type check passes (pre-existing errors in runner.py only)
- [x] `uv run ruff check src/` — lint passes

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_computed-attribute-integration.md` (EPIC-COMPATTR-001, Item 1)
- **Design:** `.project/active/compattr-v2-formula/design.md` (to be created)
- **Authority Sources:**
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-002-calculation-architecture.md` — Rule 3 amendment, FORMULA conditions
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-005-computed-attribute-classification.md` — 5-way classification, FORMULA definition
  - `~/1cfe/sysml-codegen/.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md` — Integration point inventory, proposed `_is_formula_pattern()` logic
- **Implementation Reference:**
  - `src/agentic_mbse/validation/adr002.py:297-391` — `_is_expose_pattern()` structural model
  - `src/agentic_mbse/validation/adr002.py:229-286` — `_is_calc_output_reference()` existing utility
  - `src/agentic_mbse/validation/adr002.py:418-510` — `check_static_expressions()` integration point
  - `tests/test_sysml/test_adr002.py` — existing test patterns
  - `tests/fixtures/adr002_violations/v2_*.sysml` — existing fixture naming convention

---

**Next Steps:** After approval, proceed to `/_my_design`
