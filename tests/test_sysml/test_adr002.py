"""Tests for ADR-002 validation rules.

Tests the V1, V2, V4 checks from agentic_mbse.validation.adr002
using the test fixtures in tests/fixtures/adr002_violations/.
"""
import pytest
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import get_syside

from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.adr002 import (
    check_calc_def_locations,
    check_supported_operators,
    check_static_expressions,
    _is_expose_pattern,
    _build_calc_output_catalog,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def v1_violation_model():
    """Load model with V1 violation (calc def in designs/)."""
    files = list(Path("tests/fixtures/adr002_violations/designs").glob("v1_*.sysml"))
    assert len(files) > 0, "V1 violation fixture not found"
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def v2_violation_model():
    """Load model with V2 violation (references calc output).

    Loads both the library calc def and the design file that references it.
    """
    # Get library calc def and the v2 violation file
    library_files = list(Path("tests/fixtures/adr002_violations/library").glob("*.sysml"))
    design_files = list(Path("tests/fixtures/adr002_violations").glob("v2_*.sysml"))
    files = library_files + design_files
    assert len(files) >= 2, "V2 violation fixtures not found (need library + design)"
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def v4_violation_model():
    """Load model with V4 violation (unsupported operator)."""
    files = list(Path("tests/fixtures/adr002_violations").glob("v4_*.sysml"))
    assert len(files) > 0, "V4 violation fixture not found"
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def valid_model():
    """Load compliant model (no violations)."""
    files = list(Path("tests/fixtures/adr002_violations").glob("valid_*.sysml"))
    assert len(files) > 0, "Valid model fixture not found"
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def expose_pattern_model():
    """Load model with EXPOSE pattern test cases.

    Loads library calc def and the EXPOSE pattern test file.
    Contains:
    - expose_test_part: EXPOSE pattern (exposed_output = my_calc.output_val)
    - multi_ref_test: Non-EXPOSE violation (combined = calc1.output_val + calc2.output_val)
    """
    library_files = list(Path("tests/fixtures/adr002_violations/library").glob("*.sysml"))
    design_files = [Path("tests/fixtures/adr002_violations/v2_expose_pattern.sysml")]
    files = library_files + design_files
    assert len(files) >= 2, "EXPOSE pattern fixtures not found (need library + design)"
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


# ============================================================================
# V1 Tests: Calc Def Location
# ============================================================================


def test_check_calc_def_locations_detects_violation(v1_violation_model):
    """V1: Calc defs in designs/ produce ERROR.

    Input: Model with calc def in designs/
    Output: ValidationIssue with code V1_CALC_DEF_LOCATION
    """
    issues = check_calc_def_locations(v1_violation_model)

    assert len(issues) >= 1, "Expected at least 1 V1 violation"
    assert any(i.code == ValidationCode.V1_CALC_DEF_LOCATION for i in issues)
    assert all(i.severity == Severity.ERROR for i in issues)
    assert any("library/" in (i.suggestion or "") for i in issues)


def test_check_calc_def_locations_passes_valid_model(valid_model):
    """V1: Models with no calc defs in designs/ pass validation.

    Input: Model with no calc defs (or calc defs in library/)
    Output: No V1 issues
    """
    issues = check_calc_def_locations(valid_model)

    v1_issues = [i for i in issues if i.code == ValidationCode.V1_CALC_DEF_LOCATION]
    assert len(v1_issues) == 0, f"Unexpected V1 violations: {v1_issues}"


# ============================================================================
# V4 Tests: Supported Operators
# ============================================================================


def test_check_supported_operators_detects_exponentiation(v4_violation_model):
    """V4: Exponentiation operator produces ERROR.

    Input: Model with ** operator in expression
    Output: ValidationIssue with code V4_UNSUPPORTED_OPERATOR
    """
    issues = check_supported_operators(v4_violation_model)

    assert len(issues) >= 1, "Expected at least 1 V4 violation"
    assert any(i.code == ValidationCode.V4_UNSUPPORTED_OPERATOR for i in issues)
    assert all(i.severity == Severity.ERROR for i in issues)
    # Check the operator is mentioned in message
    assert any("**" in i.message or "^" in i.message for i in issues)


def test_check_supported_operators_allows_basic_arithmetic(valid_model):
    """V4: Basic arithmetic operators pass validation.

    Input: Model using only +, -, *, /
    Output: No V4 issues
    """
    issues = check_supported_operators(valid_model)

    v4_issues = [i for i in issues if i.code == ValidationCode.V4_UNSUPPORTED_OPERATOR]
    assert len(v4_issues) == 0, f"Unexpected V4 violations: {v4_issues}"


# ============================================================================
# V2 Tests: Static Expressions
# ============================================================================


def test_check_static_expressions_detects_calc_output_ref(v2_violation_model):
    """V2: Expressions referencing calc outputs produce ERROR.

    Input: Model with attribute = calc_usage.output * 0.95
    Output: ValidationIssue with code V2_DYNAMIC_EXPRESSION
    """
    issues = check_static_expressions(v2_violation_model)

    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
    assert len(v2_issues) >= 1, "Expected at least 1 V2 violation"
    assert all(i.severity == Severity.ERROR for i in v2_issues)
    assert any("calc" in (i.suggestion or "").lower() for i in v2_issues)
    # Verify the specific output is detected
    assert any("output_val" in i.message for i in v2_issues)


def test_check_static_expressions_allows_literal_refs(valid_model):
    """V2: Expressions referencing only literals/static attrs pass.

    Input: Model with attribute = other_attr * 2.0 (all static)
    Output: No V2 issues
    """
    issues = check_static_expressions(valid_model)

    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
    assert len(v2_issues) == 0, f"Unexpected V2 violations: {v2_issues}"


# ============================================================================
# EXPOSE Pattern Tests (Phase 1: Direct Function Tests)
# ============================================================================


def test_is_expose_pattern_detects_simple_case(expose_pattern_model):
    """_is_expose_pattern returns True for attr = calc.output (EXPOSE pattern).

    The exposed_output attribute in expose_test_part is a pure value propagation
    from my_calc.output_val - this is the EXPOSE pattern.
    """
    # Build calc output catalog (now returns tuple)
    calc_outputs, _ = _build_calc_output_catalog(expose_pattern_model)

    # Find the exposed_output attribute in expose_test_part
    exposed_attr = None
    for attr in expose_pattern_model.elements(get_syside().AttributeUsage):
        if hasattr(attr, "name") and attr.name == "exposed_output":
            exposed_attr = attr
            break

    assert exposed_attr is not None, "Could not find exposed_output attribute in fixture"
    assert hasattr(exposed_attr, "feature_value_expression"), "Attribute has no expression"

    expr = exposed_attr.feature_value_expression

    # Call _is_expose_pattern directly
    result = _is_expose_pattern(exposed_attr, expr, calc_outputs)

    assert result is True, (
        f"Expected _is_expose_pattern to return True for EXPOSE pattern, "
        f"but got {result}. Expression type: {type(expr).__name__}"
    )


def test_is_expose_pattern_rejects_operator_expression(expose_pattern_model):
    """_is_expose_pattern returns False for attr = calc.output * 0.95 (computed).

    The combined attribute in multi_ref_test uses an OperatorExpression
    (calc1.output_val + calc2.output_val) - this is NOT an EXPOSE pattern.
    """
    # Build calc output catalog (now returns tuple)
    calc_outputs, _ = _build_calc_output_catalog(expose_pattern_model)

    # Find the combined attribute in multi_ref_test
    combined_attr = None
    for attr in expose_pattern_model.elements(get_syside().AttributeUsage):
        if hasattr(attr, "name") and attr.name == "combined":
            combined_attr = attr
            break

    assert combined_attr is not None, "Could not find combined attribute in fixture"
    assert hasattr(combined_attr, "feature_value_expression"), "Attribute has no expression"

    expr = combined_attr.feature_value_expression

    # Call _is_expose_pattern directly
    result = _is_expose_pattern(combined_attr, expr, calc_outputs)

    assert result is False, (
        f"Expected _is_expose_pattern to return False for OperatorExpression, "
        f"but got {result}. Expression type: {type(expr).__name__}"
    )


# ============================================================================
# EXPOSE Pattern Tests (Phase 2: Integration Tests)
# ============================================================================


def test_expose_pattern_is_exempt_from_v2(expose_pattern_model):
    """V2: EXPOSE pattern (attr = calc.output) should NOT produce violation.

    The exposed_output attribute uses pure value propagation from my_calc.output_val.
    This is the EXPOSE pattern and should be exempt from V2 check.
    """
    issues = check_static_expressions(expose_pattern_model)
    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]

    # EXPOSE pattern should be exempt - no violation for exposed_output
    exposed_issues = [i for i in v2_issues if "exposed_output" in i.element_name]
    assert len(exposed_issues) == 0, (
        f"EXPOSE pattern should be exempt from V2, but got: {exposed_issues}"
    )


def test_multi_reference_is_not_expose_pattern(expose_pattern_model):
    """V2: Multi-reference (calc1.x + calc2.y) is NOT EXPOSE pattern.

    The combined attribute uses an OperatorExpression with multiple calc outputs.
    This is NOT an EXPOSE pattern and should still be flagged as V2 violation.
    """
    issues = check_static_expressions(expose_pattern_model)
    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]

    # Multi-reference should still be flagged
    combined_issues = [i for i in v2_issues if "combined" in i.element_name]
    assert len(combined_issues) >= 1, (
        f"Multi-reference expression should still be V2 violation, "
        f"but got no violations. All V2 issues: {[i.element_name for i in v2_issues]}"
    )


# ============================================================================
# EXPOSE Pattern Tests (Phase 3: Real Model Validation)
# ============================================================================


@pytest.mark.skip(reason="Requires fusion_modeling CATF models not in this repo")
def test_real_model_expose_patterns_exempt():
    """V2: All 16 EXPOSE patterns in CATF models should be exempt.

    The CATF models have 16 EXPOSE patterns (verified 2025-12-22):
    - blanket.sysml: pump_power
    - heating.sysml: wall_plug_power
    - magnets.sysml: cooling_power
    - physics.sysml: p_alpha_out, p_neutron_out, p_thermal_out, p_electric_gross_out,
                     p_electric_net_out, q_sci_out, q_eng_out, f_recirc_out, eta_plant_out
    - system.sysml: auxiliary_power
    - tritium.sysml: processing_power
    - vacuum.sysml: pump_power, cryo_power

    After the EXPOSE pattern exemption, ALL 16 should be exempt from V2 check.

    Note: Per ADR-002 Amendment (2025-12-22), derived expressions in radial_build.sysml
    ARE expected to be flagged. This test only verifies EXPOSE patterns are exempt.
    """
    from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model

    model_files = discover_sysml_files(Path("models"))
    model, _ = load_sysml_model(model_files)

    issues = check_static_expressions(model)
    v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]

    # Verify known EXPOSE attributes are NOT in any violations
    # (EXPOSE pattern exemption still works)
    known_expose_attrs = [
        "wall_plug_power",    # heating.sysml
        "cooling_power",      # magnets.sysml
        "pump_power",         # blanket.sysml, vacuum.sysml
        "cryo_power",         # vacuum.sysml
        "processing_power",   # tritium.sysml
        "auxiliary_power",    # system.sysml
        "p_alpha_out",        # physics.sysml
        "p_thermal_out",      # physics.sysml
        "q_sci_out",          # physics.sysml
        "eta_plant_out",      # physics.sysml
    ]

    for attr_name in known_expose_attrs:
        flagged = [i for i in v2_issues if attr_name in i.element_name]
        assert len(flagged) == 0, (
            f"EXPOSE attribute '{attr_name}' should be exempt, but got: {flagged}"
        )

    # Per ADR-002 Amendment: derived expressions in radial_build.sysml ARE expected
    # to be flagged. This is correct behavior - they need to be refactored to calc defs.
    # The ~30 violations in radial_build.sysml are expected.


# ============================================================================
# Derived Expression Prohibition Tests (ADR-002 Amendment)
# ============================================================================


@pytest.fixture
def derived_single_model():
    """Load model with single design attribute reference (derived expression).

    Contains TestPart with:
    - radius = 5.0 (true static)
    - diameter = radius * 2.0 (VIOLATION - derived expression)
    """
    files = [Path("tests/fixtures/adr002_violations/v2_derived_single.sysml")]
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def derived_multi_model():
    """Load model with multiple design attribute references (derived expression).

    Contains TestPart with:
    - major_radius, minor_radius, elongation (true static)
    - volume = expression with 3 refs (VIOLATION - derived expression)
    """
    files = [Path("tests/fixtures/adr002_violations/v2_derived_multi.sysml")]
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def true_static_model():
    """Load model with pure literal expressions (true static).

    Contains TestPart with:
    - pi_value = 3.14159
    - pi_squared = 3.14159 * 3.14159
    - etc. (all true static, no refs)
    """
    files = [Path("tests/fixtures/adr002_violations/v2_true_static.sysml")]
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


@pytest.fixture
def true_static_units_model():
    """Load model with unit annotations (true static with std lib refs).

    Contains TestPart with:
    - length = 3.0 [m]
    - mass = 1000.0 [kg]
    - etc. (all true static, SI:: refs filtered)
    """
    files = [Path("tests/fixtures/adr002_violations/v2_true_static_with_units.sysml")]
    model, _ = get_syside().try_load_model([str(f) for f in files])
    return model


class TestDerivedExpressionProhibition:
    """V2 check must reject expressions with feature references (except EXPOSE and std lib).

    Per ADR-002 Amendment (2025-12-22):
    - Expressions referencing design attributes are DERIVED EXPRESSIONS
    - Derived expressions are prohibited in design files
    - Only TRUE STATIC expressions (literals + std lib refs) are allowed
    - EXPOSE pattern (single ref to sibling calc output) is exempt
    """

    def test_true_static_allowed(self, true_static_model):
        """Expressions with ONLY literals are allowed.

        Input: Model with pure literal arithmetic (3.14159 * 3.14159)
        Output: No V2 issues
        """
        issues = check_static_expressions(true_static_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) == 0, f"True static expressions should pass, got: {v2_issues}"

    def test_unit_annotations_allowed(self, true_static_units_model):
        """Unit annotations [m], [kg] are allowed - std lib refs filtered.

        Input: Model with unit-annotated literals (3.0 [m])
        Output: No V2 issues (SI::metre filtered by extract_feature_refs)
        """
        issues = check_static_expressions(true_static_units_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) == 0, f"Unit annotations should pass, got: {v2_issues}"

    def test_single_reference_violation(self, derived_single_model):
        """Even one reference to a design attribute is a violation.

        Input: Model with diameter = radius * 2.0
        Output: V2 issue for diameter (references design attr 'radius')
        """
        issues = check_static_expressions(derived_single_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) >= 1, "Expected at least 1 V2 violation for derived expression"
        # Check the violating attribute is diameter
        assert any("diameter" in i.element_name for i in v2_issues), (
            f"Expected 'diameter' in violations, got: {[i.element_name for i in v2_issues]}"
        )

    def test_multi_reference_violation(self, derived_multi_model):
        """Multiple references are still a single violation per attribute.

        Input: Model with volume = ... * major_radius * minor_radius * elongation
        Output: V2 issue for volume (references 3 design attrs)
        """
        issues = check_static_expressions(derived_multi_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) >= 1, "Expected at least 1 V2 violation"
        # Check the violating attribute is volume
        assert any("volume" in i.element_name for i in v2_issues), (
            f"Expected 'volume' in violations, got: {[i.element_name for i in v2_issues]}"
        )

    def test_expose_pattern_still_allowed(self, expose_pattern_model):
        """EXPOSE pattern (single ref to sibling calc output) is still allowed.

        Input: Model with exposed_output = my_calc.output_val
        Output: No V2 issue for exposed_output (EXPOSE exempt)
        """
        issues = check_static_expressions(expose_pattern_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        exposed_issues = [i for i in v2_issues if "exposed_output" in i.element_name]
        assert len(exposed_issues) == 0, f"EXPOSE pattern should be exempt, got: {exposed_issues}"

    def test_computation_on_calc_output_still_violation(self, v2_violation_model):
        """Computation on calc outputs (not pure EXPOSE) is still violation.

        Input: Model with attr = calc.output * 0.95
        Output: V2 issue (computation on calc output, not pure EXPOSE)
        """
        issues = check_static_expressions(v2_violation_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) >= 1, "Computation on calc output should be V2 violation"

    def test_guidance_includes_calc_def_template(self, derived_single_model):
        """Violation guidance should suggest creating a calc def.

        Input: Model with derived expression
        Output: V2 issue suggestion mentions calc def
        """
        issues = check_static_expressions(derived_single_model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
        assert len(v2_issues) >= 1
        # Check suggestion mentions calc def
        assert any("calc" in (i.suggestion or "").lower() for i in v2_issues), (
            f"Suggestion should mention calc def, got: {[i.suggestion for i in v2_issues]}"
        )
