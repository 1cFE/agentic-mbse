# Design: V2 Validation — FORMULA Exemption in `adr002.py`

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-09 20:56:52 UTC
**Complexity:** MEDIUM
**Branch:** adr004-005
**Commit:** b9f8dbe

---

## Overview

Add a `_is_formula_pattern()` function to `adr002.py` that exempts FORMULA computed attributes (all feature refs are sibling attributes, no calc output refs, no FeatureChainExpression) from V2 violations. Integrate it into `check_static_expressions()` as a third exemption path between EXPOSE and the violation.

## Related Artifacts

- **Spec:** `.project/active/compattr-v2-formula/spec.md`
- **Epic:** `.project/backlog/epic_computed-attribute-integration.md` (EPIC-COMPATTR-001, Item 1)
- **Authority Sources:**
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-005-computed-attribute-classification.md`
  - `~/1cfe/sysml-codegen/.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md`

## Research Findings

### Codebase Analysis

**`check_static_expressions()` (`adr002.py:418-510`)**: The integration point. Current 3-path decision:
1. No refs after std lib filtering → TRUE STATIC → `continue`
2. `_is_expose_pattern(attr, expr, calc_outputs)` → EXPOSE → `continue`
3. Everything else → `V2_DYNAMIC_EXPRESSION` violation

The new FORMULA path inserts between steps 2 and 3.

**`_is_expose_pattern()` (`adr002.py:297-391`)**: Structural model for the new function. Key patterns reused:
- Wraps all logic in `try/except` with conservative `return False` on exception (`:388-390`)
- Checks expression type via `type(expr).__name__` (`:331-332`)
- Uses `attr.owner` for sibling detection via object identity (`attr_owner is not source_owner`, `:380`)
- Receives `(attr, expr, calc_outputs)` parameters

**`_is_calc_output_reference()` (`adr002.py:229-286`)**: 3-method layered check. Uses `ref.document_path`, `ref.qualified_name`, and `ref.element.owner` type. Returns `True` conservatively if all methods fail. **Important**: This function operates on individual `ExpressionRef` objects, not on the expression itself. The FORMULA check needs to call this for each ref.

**`extract_feature_refs()` (`expression.py:119-222`)**: Returns `list[ExpressionRef]` with std lib refs already filtered. Each `ExpressionRef` has `name`, `qualified_name`, `document_path`, and `element` fields. The `element` field provides the raw AST element for owner-based sibling detection.

**`ExpressionRef` (`types.py:98-123`)**: Pydantic model with `element: Any | None` (excluded from serialization). The `element` field provides access to `element.owner` for sibling detection.

**`is_reference_type()` (`expression.py:308-325`)**: Checks `"FeatureReference" in type_name or "FeatureChain" in type_name`. Useful for the FR-3 FeatureChainExpression check.

### Sibling Detection Strategy

ADR-005 defines FORMULA as "ALL feature references resolve to sibling attributes on the same PartDef/PartUsage." Two strategies exist:

**Strategy A: Owner-based identity comparison** (used by `_is_expose_pattern()`)
- Compare `ref.element.owner is attr.owner` using Python object identity
- Proven pattern in the codebase (`:373-380`)
- Works because syside returns the same Python object for the same SysML element
- Simple, no string parsing needed

**Strategy B: Qualified-name namespace comparison** (used by ADR-005 classification)
- Compare parent namespace of `ref.qualified_name` with owning part's `qualified_name`
- More robust against edge cases with re-exported elements
- Requires string parsing

**Decision**: Use Strategy A (owner-based). It's the proven pattern in this codebase, matches `_is_expose_pattern()` style, and is simpler. The spec deferred this decision to design ("qualified name resolution strategy — deferred to design stage"), and owner identity is the right choice for the validation context where all elements come from the same parse.

### Existing Test Impact Analysis

**Critical finding**: The existing "derived expression" test fixtures ARE FORMULA patterns:
- `v2_derived_single.sysml`: `diameter = radius * 2.0` — `radius` is a sibling attribute → FORMULA
- `v2_derived_multi.sysml`: `volume = ... * major_radius * minor_radius * elongation` — all sibling attributes → FORMULA

After the FORMULA exemption, these will no longer produce V2 violations. This is **correct behavior** — the ADR-002 amendment says FORMULA patterns are valid. But it means:

1. `TestDerivedExpressionProhibition.test_single_reference_violation` → will fail (FORMULA exempted)
2. `TestDerivedExpressionProhibition.test_multi_reference_violation` → will fail (FORMULA exempted)
3. `TestDerivedExpressionProhibition.test_guidance_includes_calc_def_template` → will fail (no violation from derived_single fixture)

**`v2_false_positive_prevention.sysml` impact**: This fixture has `doubled_output = output_val * 2.0` where `output_val` is a local sibling attribute (`:19`, `= 100.0`). After the change, `doubled_output` becomes FORMULA-exempt (correctly — `output_val` is a sibling, not a calc output). This fixture has no dedicated test — it's only loaded as part of the `v2_violation_model` glob (`Path("tests/fixtures/adr002_violations").glob("v2_*.sysml")`). The `test_check_static_expressions_detects_calc_output_ref` test checks `len(v2_issues) >= 1` and `"output_val" in i.message` — both still satisfied by the remaining violation from `v2_dynamic_expression.sysml` (`derived_value = my_calc.output_val * 0.95`, which is EXPOSE_COMPUTED and remains a violation). **No test changes needed for this fixture.**

The spec's "zero regressions" criterion (FR-8) means V1, V4, and non-FORMULA V2 tests pass unchanged. The derived expression tests must be **updated** to reflect the new FORMULA exemption, and new test cases must be added for patterns that remain violations (EXPOSE_COMPUTED, mixed refs).

### Patterns That Must Still Be Flagged

After the FORMULA exemption, these remain V2 violations:
- **EXPOSE_COMPUTED**: `attribute adj = calc.output * 0.95` — contains FeatureChainExpression
- **Mixed refs**: `attribute x = sibling_a + calc.output` — contains a calc output ref
- **Cross-part refs**: (hypothetical) `attribute x = other_part.attr` — FeatureChainExpression

The existing test `test_check_static_expressions_detects_calc_output_ref` (using `v2_dynamic_expression.sysml`) tests EXPOSE_COMPUTED and will continue to pass.

---

## Proposed Design

### High-Level Architecture

```
check_static_expressions(model)
  │
  ├── refs = extract_feature_refs(expr)
  ├── len(refs) == 0 → TRUE STATIC → continue
  ├── _is_expose_pattern(attr, expr, calc_outputs) → EXPOSE → continue
  ├── _is_formula_pattern(attr, expr, refs, calc_def_qnames) → FORMULA → continue  ← NEW
  └── else → V2_DYNAMIC_EXPRESSION violation
```

### Component 1: `_is_formula_pattern()` function

**Location**: `src/agentic_mbse/validation/adr002.py`, after `_is_expose_pattern()` (~line 392)

**Signature**:
```python
def _is_formula_pattern(
    attr: Any,
    expr: Any,
    refs: list[ExpressionRef],
    calc_def_qualified_names: set[str],
) -> bool:
```

**Parameters**:
- `attr`: The `AttributeUsage` being analyzed (provides `attr.owner` for sibling detection)
- `expr`: The attribute's `feature_value_expression` (used only for the top-level type check)
- `refs`: Pre-computed list of `ExpressionRef` from `extract_feature_refs()` — passed by the caller, which already computed them. Avoids a redundant `extract_feature_refs()` call. Unlike `_is_expose_pattern()` (which doesn't use refs), this function iterates over each ref, so accepting them as a parameter is the natural interface.
- `calc_def_qualified_names`: Set of calc def qualified names from `_build_calc_output_catalog()` (for calc output reference detection)

**Algorithm**:

```
try:
    1. Check expression type:
       - type_name = type(expr).__name__
       - If "FeatureChain" in type_name → return False (FR-3: dotted paths are not FORMULA)
       - FORMULA uses OperatorExpression with FeatureReferenceExpression operands
       NOTE: This only catches the case where the ENTIRE expression is a
       FeatureChainExpression (e.g., `attr = calc.output`). When a
       FeatureChainExpression is an OPERAND inside an OperatorExpression
       (e.g., `attr = sibling + calc.output`), the top-level type is
       OperatorExpression, so step 1 does NOT reject it. This is correct —
       the ref-level checks in step 3 handle it:
       - extract_feature_refs() resolves the chain target (e.g., `output_val`
         from `calc.output`), producing an ExpressionRef whose element.owner
         is a CalculationDefinition
       - Step 3a: _is_calc_output_reference() returns True for that ref
         (document_path has "library/", or owner is CalculationDefinition)
       - Step 3b: Even if 3a didn't catch it, the owner identity check
         would reject it (calc def owner ≠ attr owner)

    2. Guard: If len(refs) == 0 → return False
       (no refs = true static, not FORMULA; handled upstream)

    3. Get attr owner and check each ref:
       - attr_owner = attr.owner if hasattr(attr, "owner") else None
       - If attr_owner is None → return False (conservative)
       - For each ref in refs:
         a. Check calc output exclusion (FR-2):
            - If _is_calc_output_reference(ref, calc_def_qualified_names) → return False
         b. Check sibling relationship (FR-1):
            - ref_element = ref.element
            - If ref_element is None → return False (FR-4: conservative)
            - ref_owner = ref_element.owner if hasattr(ref_element, "owner") else None
            - If ref_owner is None → return False (FR-4: conservative)
            - If ref_owner is not attr_owner → return False (not a sibling)

    4. All refs passed → return True (FORMULA pattern)

except Exception:
    return False  (conservative default, FR-4)
```

**Key design decisions**:
- Checks `FeatureChainExpression` FIRST (step 1) — cheap type check eliminates pure EXPOSE/cross-part refs. Nested chains inside OperatorExpressions are caught by ref-level checks (step 3a/3b).
- Reuses existing `_is_calc_output_reference()` for calc output detection — no duplication
- Uses owner identity (`is`) for sibling detection — proven pattern from `_is_expose_pattern()`
- Accepts `refs` as a parameter — the caller already computed them; avoids redundant `extract_feature_refs()` call
- No new imports needed in `adr002.py` — `ExpressionRef` is already imported at `:16`

### Component 2: Integration into `check_static_expressions()`

**Location**: `src/agentic_mbse/validation/adr002.py:486-487` (between EXPOSE check and violation)

**Change**: Add 2 lines after the EXPOSE pattern check:

```python
# EXPOSE PATTERN: Single ref to sibling calc output is exempt
if _is_expose_pattern(attr, expr, calc_outputs):
    continue  # OK - EXPOSE pattern exempt

# FORMULA PATTERN: All refs are sibling attributes (no calc output refs)
if _is_formula_pattern(attr, expr, refs, calc_def_qnames):
    continue  # OK - FORMULA pattern exempt per ADR-002 Amendment

# DERIVED EXPRESSION VIOLATION: Has feature refs that aren't EXPOSE or FORMULA
```

This requires `calc_def_qnames` to be available. Currently `_build_calc_output_catalog()` returns `(calc_outputs, calc_def_qualified_names)` but only `calc_outputs` is used. The second return value is already available:

```python
# Current (line 449):
calc_outputs, _ = _build_calc_output_catalog(model)

# Updated:
calc_outputs, calc_def_qnames = _build_calc_output_catalog(model)
```

### Component 3: Docstring update for `check_static_expressions()`

**Location**: `adr002.py:418-444`

Update to document the 4-path decision:

```python
"""
V2: Validate that design attribute expressions are either:
- True static (no feature references except standard library), OR
- EXPOSE pattern (single reference to sibling calc output), OR
- FORMULA pattern (all references are sibling attributes, no calc outputs)

Per ADR-002 Rule 3 Amendment (2026-02-09) and ADR-005:
- FORMULA expressions (arithmetic on sibling attributes) are exempt
- EXPOSE expressions (value propagation from calc outputs) are exempt
- Only expressions referencing calc outputs or cross-part elements are violations

Algorithm:
1. For each AttributeUsage in designs/ with expression:
   - Skip if inside a calc usage (bindings are allowed)
   - Extract all feature references (std lib filtered by default)
   - If no refs → TRUE STATIC → OK
   - If EXPOSE pattern → OK
   - If FORMULA pattern → OK (per ADR-002 Amendment)
   - Otherwise → DERIVED EXPRESSION VIOLATION
"""
```

### Component 4: Test fixture — `v2_formula_pattern.sysml`

**Location**: `tests/fixtures/adr002_violations/v2_formula_pattern.sysml`

Contains the FORMULA-exempt patterns (no library deps needed):

```sysml
package V2FormulaPatternTest {
    public import ScalarValues::*;

    part def FormulaTestPart {
        // Inputs (true static)
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute rate : Real = 12.0;

        // Simple FORMULA: sibling refs only → NO violation
        attribute area : Real = length * width;

        // Chain FORMULA: refs another computed attr → NO violation
        attribute cost : Real = area * rate;

        // FORMULA + literal: sibling ref mixed with literal → NO violation
        attribute p_net_kw : Real = length * 1000.0;
    }
}
```

### Component 4b: Mixed-ref test case in `v2_expose_pattern.sysml`

**Location**: `tests/fixtures/adr002_violations/v2_expose_pattern.sysml` — add a new part to the existing fixture.

The EXPOSE_COMPUTED test case already exists in `v2_dynamic_expression.sysml` (`derived_value = my_calc.output_val * 0.95`). Only the mixed-ref pattern (sibling + calc output in one expression) is new. Add it to `v2_expose_pattern.sysml`, which already imports `V2TestLibrary::*` and loads with library files via the `expose_pattern_model` fixture:

```sysml
    part mixed_ref_test {
        calc my_calc : SimpleCalc { in input_val = 5.0; }

        // Sibling attribute (true static)
        attribute sibling_a : Real = 10.0;

        // MIXED: sibling ref + calc output ref → SHOULD be V2 violation
        // _is_formula_pattern rejects because my_calc.output_val is a calc output ref
        attribute mixed : Real = sibling_a + my_calc.output_val;
    }
```

This part goes inside the existing `ExposePatternTest` package. The `expose_pattern_model` fixture already loads `library/*.sysml` + `v2_expose_pattern.sysml`, so no fixture change needed.

**Existing test compatibility verified**: All 5 tests using `expose_pattern_model` filter by element name before asserting counts — none assert an exact total violation count. Specifically:
- `test_is_expose_pattern_detects_simple_case` — direct function call on `exposed_output` attr, no V2 count
- `test_is_expose_pattern_rejects_operator_expression` — direct function call on `combined` attr, no V2 count
- `test_expose_pattern_is_exempt_from_v2` — filters `"exposed_output" in i.element_name`, asserts `== 0`
- `test_multi_reference_is_not_expose_pattern` — filters `"combined" in i.element_name`, asserts `>= 1`
- `TestDerivedExpressionProhibition.test_expose_pattern_still_allowed` — filters `"exposed_output" in i.element_name`, asserts `== 0`

Adding `mixed_ref_test` with a new `mixed` attribute introduces one additional V2 violation but no existing assertion will break.

**Why this works**: `sibling_a + my_calc.output_val` is an OperatorExpression. `extract_feature_refs()` returns two refs: `sibling_a` (FeatureReferenceExpression, owner = `mixed_ref_test`) and `output_val` (from FeatureChainExpression target, owner = `SimpleCalc` CalculationDefinition). In `_is_formula_pattern()`, step 3a calls `_is_calc_output_reference()` for the `output_val` ref — `ref.document_path` contains "library/" → returns True → function returns False (not FORMULA). The expression correctly remains a V2 violation.

### Component 5: Test cases in `test_adr002.py`

**New fixture**:
```python
@pytest.fixture
def formula_pattern_model():
    """Load model with FORMULA pattern test cases."""
    files = [Path("tests/fixtures/adr002_violations/v2_formula_pattern.sysml")]
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model
```

**New test class** (after `TestDerivedExpressionProhibition`):

```python
class TestFormulaPatternExemption:
    """V2 check must exempt FORMULA patterns (sibling-only refs).

    Per ADR-002 Amendment (2026-02-09) and ADR-005:
    FORMULA expressions where ALL feature refs resolve to sibling
    attributes are exempt from V2 check.
    """

    def test_simple_formula_exempt(self, formula_pattern_model):
        """attribute area = length * width → no V2 violation."""
        # Assert: no V2 issues with "area" in element_name

    def test_chain_formula_exempt(self, formula_pattern_model):
        """attribute cost = area * rate (area is computed) → no V2 violation."""
        # Assert: no V2 issues with "cost" in element_name

    def test_formula_with_literal_exempt(self, formula_pattern_model):
        """attribute p_net_kw = length * 1000.0 → no V2 violation."""
        # Assert: no V2 issues with "p_net_kw" in element_name

    def test_expose_computed_still_violation(self, v2_violation_model):
        """attribute derived_value = my_calc.output_val * 0.95 → V2 violation."""
        # Uses v2_violation_model which loads v2_dynamic_expression.sysml
        # Assert: V2 issue with "derived_value" in element_name

    def test_mixed_refs_still_violation(self, expose_pattern_model):
        """attribute mixed = sibling_a + my_calc.output_val → V2 violation."""
        # Uses expose_pattern_model which loads v2_expose_pattern.sysml (with new mixed_ref_test part)
        # Assert: V2 issue with "mixed" in element_name
```

**Updated existing tests**: The `TestDerivedExpressionProhibition` tests for `v2_derived_single.sysml` and `v2_derived_multi.sysml` need updating. These fixtures contain FORMULA patterns that will now be exempted. Two options:

1. **Update tests to expect no violation** — since `diameter = radius * 2.0` is now a valid FORMULA
2. **Update fixtures to contain actual violations** — e.g., change to `diameter = calc.output * 2.0`

**Decision**: Option 1 (update tests). The fixtures demonstrate real-world patterns. Changing the test expectations documents the behavior change clearly. The tests become "derived expressions that are FORMULA are now allowed."

Specifically:
- `test_single_reference_violation` → rename to `test_single_reference_formula_exempt` and assert 0 V2 violations for `diameter` (was 1, now 0 — FORMULA exempted)
- `test_multi_reference_violation` → rename to `test_multi_reference_formula_exempt` and assert 0 V2 violations for `volume` (was 1, now 0 — FORMULA exempted)
- `test_guidance_includes_calc_def_template` → **repoint to `v2_violation_model`** and check that EXPOSE_COMPUTED violations still include calc def guidance. The `v2_violation_model` still produces violations from `v2_dynamic_expression.sysml` (`derived_value = my_calc.output_val * 0.95`), so guidance testing remains valid. Rename to `test_violation_guidance_includes_calc_def_template` for clarity.

### Component 6: Test imports

No new imports needed in `test_adr002.py`. All new tests are integration tests calling `check_static_expressions()` (already imported). Direct unit tests of `_is_formula_pattern()` are not planned — the function's behavior is fully exercised through the integration tests (FORMULA-exempt, EXPOSE_COMPUTED-violation, mixed-violation). This matches the existing pattern: `_is_expose_pattern` is imported for direct tests because its detection logic is subtle and worth unit-testing independently, but `_is_formula_pattern`'s logic is straightforward (iterate refs, check owner) and doesn't warrant separate unit tests beyond what integration tests cover.

---

## Potential Risks

1. **Owner identity assumption**: `ref.element.owner is attr.owner` relies on syside returning the same Python object for the same SysML owner element. This is the same assumption `_is_expose_pattern()` makes and has been validated in production. Low risk.

2. **Top-level FeatureChainExpression check scope**: The step 1 type check only catches expressions where the ENTIRE expression is a FeatureChainExpression (e.g., `attr = calc.output`). When a FeatureChainExpression is nested as an operand inside an OperatorExpression (e.g., `attr = sibling + calc.output`), step 1 does not reject it. This is by design — the ref-level checks in step 3a/3b handle these cases. See the NOTE in the algorithm for the full analysis.

3. **Test migration**: Changing expectations for `test_single_reference_violation` and `test_multi_reference_violation` may obscure the original intent of those tests. Mitigation: clear renaming and docstring updates explaining the behavior change per ADR-002 amendment.

## Integration Strategy

- The change is entirely within `adr002.py` (one new function, ~30 lines; one integration point, ~4 lines changed)
- No changes needed to `expression.py`, `types.py`, or any other module
- Test changes are additive (new class) plus updates to existing expectations
- The existing `_build_calc_output_catalog()` already returns `calc_def_qualified_names` — just need to capture the second return value

## Validation Approach

### Automated Testing
- `uv run pytest tests/test_sysml/test_adr002.py -v` — all tests pass
- `uv run pytest tests/` — full suite, zero regressions
- `uv run mypy src/` — type check passes
- `uv run ruff check src/ tests/` — lint passes

### Manual Verification
- Inspect V2 output on a model containing FORMULA patterns (e.g., the new fixture)
- Verify EXPOSE_COMPUTED patterns still produce violations
- Verify existing EXPOSE patterns still pass

### Success Criteria from Spec
- [ ] `agentic-mbse validate` passes on FORMULA models with zero false V2 violations
- [ ] EXPOSE_COMPUTED and calc output refs still flagged as V2 violations
- [ ] Zero regressions in V1/V4 test coverage
- [ ] V2 tests updated to reflect FORMULA exemption

---

Next Step: After approval → `/_my_implement`
