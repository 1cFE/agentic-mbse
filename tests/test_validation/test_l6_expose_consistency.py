"""L6 EXPOSE validation consistency (L6-EXPOSE-CONSISTENCY).

Contract: .project/active/l6-expose-consistency/spec.md. Fixtures and expected
results: design.md Appendix A and Appendix B.

A design attribute bound directly to a sibling calc or part output
(`attribute x : Real = my_calc.scaled;`) is an EXPOSE binding. The static-expression
check (V2) already accepts it; the supported-operator check (V4) and the
design-attribute completeness check must accept it too. Every non-EXPOSE
expression keeps exactly the diagnostics it had before.
"""

import shutil
from collections import Counter
from pathlib import Path

import pytest

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation.adr002 import (
    check_static_expressions,
    check_supported_operators,
    is_expose_binding,
)
from agentic_mbse.validation.common import (
    discover_sysml_files,
    get_qualified_name,
    load_sysml_model,
)
from agentic_mbse.validation.level6_architecture import (
    check_design_attr_completeness,
    validate_architecture,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"
SHAPES = FIXTURES / "l6_expose_consistency" / "shapes"
CONTROLS = FIXTURES / "l6_expose_consistency" / "controls"
REFERENT = FIXTURES / "adr002_violations" / "v2_expose_pattern.sysml"
REFERENT_LIB = FIXTURES / "adr002_violations" / "library" / "simple_calc.sysml"

V2 = ValidationCode.V2_DYNAMIC_EXPRESSION
V4 = ValidationCode.V4_UNSUPPORTED_OPERATOR
UNX = ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE
INC = ValidationCode.L6_DESIGN_ATTR_INCOMPLETE

# Design Appendix B: 13 (code, element) pairs, each exactly once, before and after.
D = "ExposeControlsDesign::"
EXPECTED_CONTROLS = Counter(
    [(code, D + "remote_reader::remote") for code in (V2, V4, UNX)]
    + [(code, D + "item_head_reader::payload_mass") for code in (V2, V4, UNX)]
    + [(code, D + "derived_part::derated") for code in (V2, V4, UNX)]
    + [(V4, D + "controls::powered"), (UNX, D + "controls::powered")]
    + [(INC, D + "controls::missing"), (UNX, D + "controls::divzero")]
)

EXPOSED = "ExposePatternTest::expose_test_part::exposed_output"
COMBINED = "ExposePatternTest::multi_ref_test::combined"
# `combined = calc1.output_val + calc2.output_val`: two V4 '.', one per chain operand.
EXPECTED_COMBINED = Counter({V2: 1, V4: 2, UNX: 1})


def _assert_referent(issues):
    """The EXPOSE binding is clean; the arithmetic over calc outputs is not."""
    assert [i for i in issues if i.element_name == EXPOSED] == []
    assert Counter(i.code for i in issues if i.element_name == COMBINED) == EXPECTED_COMBINED


# ============================================================================
# Spec criterion 1: the retained referent produces neither false positive,
# through the individual checks and the combined L6 route.
# ============================================================================


def test_referent_individual_checks():
    model, _ = load_sysml_model([REFERENT_LIB, REFERENT])
    issues = (
        check_static_expressions(model)
        + check_supported_operators(model)
        + check_design_attr_completeness(model, design_path_filter=None)[0]
    )
    _assert_referent(issues)


def test_referent_combined_route(tmp_path):
    # Copy into a designs/ + library/ layout so the default design filter checks it.
    (tmp_path / "designs").mkdir()
    (tmp_path / "library").mkdir()
    shutil.copy(REFERENT, tmp_path / "designs")
    shutil.copy(REFERENT_LIB, tmp_path / "library")
    result = validate_architecture(str(tmp_path))
    _assert_referent(result.structured_issues)


# ============================================================================
# Spec criterion 2: pure EXPOSE bindings on part definitions and part usages
# stay accepted (including the part-headed sibling relay, design D6).
# Arithmetic over a calc output staying rejected is pinned by `derated` below.
# ============================================================================


def test_shapes_pass_combined_route():
    result = validate_architecture(str(SHAPES))
    assert result.issues == [], result.issues
    assert result.success is True
    assert result.metrics["Design attrs checked"] == 3


# ============================================================================
# Spec criterion 3: unsupported operators, absent values, unextractable static
# defaults, and invalid reference targets keep their diagnostics.
# ============================================================================


def test_controls_keep_every_diagnostic():
    result = validate_architecture(str(CONTROLS))
    pairs = Counter((i.code, i.element_name) for i in result.structured_issues)
    assert pairs == EXPECTED_CONTROLS
    assert len(result.issues) == 13  # also catches unstructured manifest strings
    assert result.metrics["Design attrs checked"] == 6
    powered_v4 = [
        i
        for i in result.structured_issues
        if i.code == V4 and i.element_name == D + "controls::powered"
    ]
    assert len(powered_v4) == 1
    assert "'^'" in powered_v4[0].message


# The predicate boundary behind criteria 2 and 3 (design Invariant 3): a top-level
# feature chain whose head is a sibling calc or part usage. A non-sibling head, an
# item head, and arithmetic over a chain are not EXPOSE.

_MODELS: dict[Path, object] = {}


def _attr(root: Path, qualified_name: str):
    if root not in _MODELS:
        _MODELS[root], _ = load_sysml_model(discover_sysml_files(str(root)))
    for attr in SysideAdapter.elements_of_type(_MODELS[root], "AttributeUsage"):
        if get_qualified_name(attr) == qualified_name:
            return attr
    raise AssertionError(f"{qualified_name} not found under {root}")


@pytest.mark.parametrize(
    ("root", "qualified_name", "expected"),
    [
        (SHAPES, "ExposeShapesDesign::ExposingModule::module_result", True),
        (SHAPES, "ExposeShapesDesign::expose_test_part::exposed_output", True),
        (SHAPES, "ExposeShapesDesign::relay_part::relayed", True),  # part head, D6
        (CONTROLS, D + "remote_reader::remote", False),  # head is not a sibling
        (CONTROLS, D + "item_head_reader::payload_mass", False),  # item head
        (CONTROLS, D + "derived_part::derated", False),  # arithmetic
    ],
)
def test_is_expose_binding_boundary(root, qualified_name, expected):
    attr = _attr(root, qualified_name)
    assert is_expose_binding(attr, attr.feature_value_expression) is expected
