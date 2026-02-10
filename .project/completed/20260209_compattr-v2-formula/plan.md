# Implementation Plan: V2 Validation — FORMULA Exemption

**Status:** Complete
**Created:** 2026-02-09
**Last Updated:** 2026-02-09

## Source Documents
- **Spec:** `.project/active/compattr-v2-formula/spec.md`
- **Design:** `.project/active/compattr-v2-formula/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 writes all tests and fixtures first (test-first). Phase 2 implements the core function and integration — the new tests guide and validate implementation. Phase 3 migrates existing tests whose expectations change due to the FORMULA exemption. This sequence de-risks by proving the fixture parsing and test structure before writing production code, then validates the implementation before touching existing tests.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions

---

## Phase 1: Test Infrastructure — Fixtures + New Test Class

### Goal
Create the SysML test fixture for FORMULA patterns, add the mixed-ref test case to the existing EXPOSE fixture, and write the `TestFormulaPatternExemption` test class. Tests will fail until Phase 2 — this proves they're testing the right thing.

### Test Stencil (Write This First)
```python
# Test stencil for Phase 1 — write these tests before implementing _is_formula_pattern()

class TestFormulaPatternExemption:
    def test_simple_formula_exempt(self, formula_pattern_model):
        issues = check_static_expressions(formula_pattern_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        area_issues = [i for i in v2_issues if "area" in i.element_name]
        assert len(area_issues) == 0  # FORMULA exempt

    def test_mixed_refs_still_violation(self, expose_pattern_model):
        issues = check_static_expressions(expose_pattern_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        mixed_issues = [i for i in v2_issues if "mixed" in i.element_name]
        assert len(mixed_issues) >= 1  # NOT exempt — has calc output ref
```

### Changes Required

**See `design.md` for:**
- Fixture SysML content → `design.md#component-4-test-fixture--v2_formula_patternsysml`
- Mixed-ref test case → `design.md#component-4b-mixed-ref-test-case`
- Test class structure → `design.md#component-5-test-cases-in-test_adr002py`

**Specific file changes:**

#### 1. New SysML Fixture
**File:** `tests/fixtures/adr002_violations/v2_formula_pattern.sysml` (NEW)
- [x] Create fixture with `FormulaTestPart` containing:
  - `length`, `width`, `rate` (true static inputs)
  - `area = length * width` (simple FORMULA)
  - `cost = area * rate` (chain FORMULA)
  - `p_net_kw = length * 1000.0` (FORMULA + literal)

#### 2. Add Mixed-Ref Test Case to EXPOSE Fixture
**File:** `tests/fixtures/adr002_violations/v2_expose_pattern.sysml`
- [x] Add `mixed_ref_test` part inside `ExposePatternTest` package
  - `sibling_a : Real = 10.0` (true static)
  - `mixed : Real = sibling_a + my_calc.output_val` (mixed refs → still violation)
  - Needs `calc my_calc : SimpleCalc { ... }` for the calc output ref
- [x] Verify: existing test compatibility (all 5 tests using `expose_pattern_model` filter by element name, none assert total count)

#### 3. New Test Fixture + Test Class
**File:** `tests/test_sysml/test_adr002.py`
- [x] Add `formula_pattern_model` fixture (loads `v2_formula_pattern.sysml` only — no library files needed)
- [x] Add `TestFormulaPatternExemption` class with 5 tests:
  - `test_simple_formula_exempt` — `area` → no V2 violation
  - `test_chain_formula_exempt` — `cost` → no V2 violation
  - `test_formula_with_literal_exempt` — `p_net_kw` → no V2 violation
  - `test_expose_computed_still_violation` — `derived_value` (uses `v2_violation_model`) → V2 violation
  - `test_mixed_refs_still_violation` — `mixed` (uses `expose_pattern_model`) → V2 violation

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_sysml/test_adr002.py -v` — fixture loads, new FORMULA tests FAIL (expected — no exemption yet), EXPOSE_COMPUTED and mixed-ref tests PASS (violations still detected)
- [x] `uv run ruff check tests/` — lint passes

**Manual:**
- [x] Verify fixture parses: `uv run python -c "from agentic_mbse.sysml.syside_adapter import get_syside; m,_=get_syside().try_load_model(['tests/fixtures/adr002_violations/v2_formula_pattern.sysml']); print('OK')"` → prints "OK"

**What We Know Works After This Phase:**
- Fixtures parse correctly in syside
- Test structure is sound and test assertions target the right element names
- The 3 FORMULA exemption tests fail (proving they detect the current violation behavior)
- The 2 violation-retention tests pass (EXPOSE_COMPUTED and mixed-ref remain violations)

---

## Phase 2: Core Implementation — `_is_formula_pattern()` + Integration

### Goal
Implement the `_is_formula_pattern()` function in `adr002.py`, integrate it into `check_static_expressions()` as the third exemption path, update the docstring, and capture `calc_def_qnames` from `_build_calc_output_catalog()`.

### Test Stencil (Write This First)
```python
# No new tests in this phase — Phase 1 tests drive implementation.
# The 3 FORMULA exemption tests should now PASS.
# The 2 violation-retention tests should still PASS.
```

### Changes Required

**See `design.md` for:**
- Function signature and algorithm → `design.md#component-1-_is_formula_pattern-function`
- Integration point → `design.md#component-2-integration-into-check_static_expressions`
- Docstring update → `design.md#component-3-docstring-update-for-check_static_expressions`

**Specific file changes:**

#### 1. New Function: `_is_formula_pattern()`
**File:** `src/agentic_mbse/validation/adr002.py` (~line 392, after `_is_expose_pattern()`)
- [x] Add `_is_formula_pattern(attr, expr, refs, calc_def_qualified_names)` function (~30 lines)
- [x] Implement 4-step algorithm per `design.md#component-1`:
  1. Top-level FeatureChainExpression type check → return False
  2. Guard: `len(refs) == 0` → return False
  3. For each ref: calc output check via `_is_calc_output_reference()`, then owner identity check
  4. All refs pass → return True
- [x] Wrap in `try/except` with conservative `return False`

#### 2. Integration into `check_static_expressions()`
**File:** `src/agentic_mbse/validation/adr002.py:449,486-487`
- [x] Change `calc_outputs, _ = _build_calc_output_catalog(model)` to `calc_outputs, calc_def_qnames = _build_calc_output_catalog(model)` (line 449)
- [x] Add FORMULA check between EXPOSE check and violation (after line 486):
  ```python
  if _is_formula_pattern(attr, expr, refs, calc_def_qnames):
      continue  # OK - FORMULA pattern exempt per ADR-002 Amendment
  ```

#### 3. Docstring Update
**File:** `src/agentic_mbse/validation/adr002.py:418-444`
- [x] Update `check_static_expressions()` docstring to document 4-path decision per `design.md#component-3`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_sysml/test_adr002.py::TestFormulaPatternExemption -v` → all 5 tests PASS
- [x] `uv run pytest tests/test_sysml/test_adr002.py -v` → most tests pass, EXCEPT 3 `TestDerivedExpressionProhibition` tests (expected — they still expect violations from FORMULA patterns)
- [x] `uv run mypy src/` — type check passes (pre-existing errors in runner.py only)
- [x] `uv run ruff check src/` — lint passes

**Manual:**
- [x] Inspect that `_is_formula_pattern()` follows the structural pattern of `_is_expose_pattern()` (try/except, conservative return False)

**What We Know Works After This Phase:**
- `_is_formula_pattern()` correctly exempts simple, chain, and literal-mixed FORMULA patterns
- EXPOSE_COMPUTED and mixed-ref patterns still produce V2 violations
- The integration point is wired correctly (new function called between EXPOSE check and violation)
- Only the 3 derived expression tests remain to be updated (Phase 3)

---

## Phase 3: Test Migration — Update Derived Expression Tests

### Goal
Update the 3 `TestDerivedExpressionProhibition` tests whose expectations changed due to the FORMULA exemption. The `v2_derived_single.sysml` and `v2_derived_multi.sysml` fixtures contain FORMULA patterns that are now correctly exempted.

### Test Stencil (Write This First)
```python
# Updated expectations for derived expression tests

def test_single_reference_formula_exempt(self, derived_single_model):
    """diameter = radius * 2.0 is now FORMULA-exempt per ADR-002 Amendment."""
    issues = check_static_expressions(derived_single_model)
    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
    diameter_issues = [i for i in v2_issues if "diameter" in i.element_name]
    assert len(diameter_issues) == 0  # Now FORMULA exempt

def test_violation_guidance_includes_calc_def_template(self, v2_violation_model):
    """Repoint to v2_violation_model which still produces violations."""
    issues = check_static_expressions(v2_violation_model)
    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
    assert len(v2_issues) >= 1
    assert any("calc" in (i.suggestion or "").lower() for i in v2_issues)
```

### Changes Required

**See `design.md` for:**
- Test update rationale → `design.md#component-5-test-cases-in-test_adr002py` (bottom section on updated existing tests)

**Specific file changes:**

#### 1. Update TestDerivedExpressionProhibition
**File:** `tests/test_sysml/test_adr002.py`
- [x] `test_single_reference_violation` → rename to `test_single_reference_formula_exempt`:
  - Change assertion: `diameter` should have 0 V2 violations (was ≥1)
  - Update docstring: "Per ADR-002 Amendment, `diameter = radius * 2.0` is FORMULA-exempt"
- [x] `test_multi_reference_violation` → rename to `test_multi_reference_formula_exempt`:
  - Change assertion: `volume` should have 0 V2 violations (was ≥1)
  - Update docstring: "Per ADR-002 Amendment, all-sibling-ref expressions are FORMULA-exempt"
- [x] `test_guidance_includes_calc_def_template` → rename to `test_violation_guidance_includes_calc_def_template`:
  - Change fixture from `derived_single_model` to `v2_violation_model`
  - The `v2_violation_model` still produces violations from `v2_dynamic_expression.sysml` (`derived_value = my_calc.output_val * 0.95`)
  - Assertion stays the same (checks `"calc"` in suggestion)
- [x] Update class docstring to mention FORMULA exemption alongside EXPOSE

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_sysml/test_adr002.py -v` → ALL tests pass (22 passed, 1 skipped)
- [x] `uv run pytest tests/` → full suite, zero regressions (886 passed, 1 skipped)
- [x] `uv run mypy src/` — type check passes (pre-existing errors in runner.py only)
- [x] `uv run ruff check src/ tests/` — lint passes (pre-existing issues in other files only)

**Manual:**
- [x] Review renamed tests — docstrings clearly explain the ADR-002 amendment behavior change
- [x] Verify test count: total test count in `test_adr002.py` should increase by 5 (new class) with 0 removed

**What We Know Works After This Phase:**
- Full test suite passes with zero regressions
- FORMULA patterns are exempt (3 new positive tests + 2 updated existing tests)
- EXPOSE_COMPUTED and mixed-ref patterns still flagged (2 new negative tests + existing tests)
- All V1 and V4 tests unchanged and passing
- Type checking and linting clean

---

## Environment Setup

**See CLAUDE.md for full environment rules**

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If fixtures don't parse, check SysML syntax. The `v2_formula_pattern.sysml` uses only `ScalarValues::*` (no library), so parsing should be straightforward.
- **Phase 2**: If owner identity check doesn't work for formula refs, fall back to qualified name comparison (Strategy B from design). But this is unlikely — Strategy A is proven in `_is_expose_pattern()`.
- **Phase 3**: If repointing `test_guidance_includes_calc_def_template` to `v2_violation_model` causes issues (e.g., the violation from `v2_dynamic_expression.sysml` doesn't include calc def guidance), check that `_generate_calc_def_guidance()` is called for all V2 violations regardless of pattern.

## Implementation Notes

All 3 phases completed successfully on 2026-02-09. Zero deviations from plan.

### Phase 1 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/fixtures/adr002_violations/v2_formula_pattern.sysml` with FormulaTestPart (area, cost, p_net_kw patterns)
- Modified `tests/fixtures/adr002_violations/v2_expose_pattern.sysml` — added `mixed_ref_test` part with `mixed = sibling_a + my_calc.output_val`
- Modified `tests/test_sysml/test_adr002.py` — added `formula_pattern_model` fixture and `TestFormulaPatternExemption` class (5 tests)
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Added `_is_formula_pattern()` function (~55 lines with docstring) in `adr002.py` after `_is_expose_pattern()`
- Changed `calc_outputs, _ = ...` to `calc_outputs, calc_def_qnames = ...` in `check_static_expressions()`
- Added FORMULA check (2 lines + comment) between EXPOSE check and violation
- Updated `check_static_expressions()` docstring to document 4-path decision
**Issues:** None — mypy has pre-existing errors in runner.py (unrelated), no new errors
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Renamed `test_single_reference_violation` → `test_single_reference_formula_exempt` (asserts 0 violations for `diameter`)
- Renamed `test_multi_reference_violation` → `test_multi_reference_formula_exempt` (asserts 0 violations for `volume`)
- Renamed `test_guidance_includes_calc_def_template` → `test_violation_guidance_includes_calc_def_template` (repointed from `derived_single_model` to `v2_violation_model`)
- Updated `TestDerivedExpressionProhibition` class docstring to mention FORMULA exemption
**Issues:** None
**Deviations:** None

---

**Status**: Draft → In Progress → Complete
