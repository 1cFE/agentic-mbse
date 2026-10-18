"""`invocation_uses` is total and agrees with the reference walk's allowlist refusal."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml import reference_use
from agentic_mbse.sysml.reference_use import inspect_reference_uses, invocation_uses
from agentic_mbse.sysml.syside_adapter import SysideAdapter

#: (attribute type, authored value, expected [(callable, supported)]).
CASES = [
    ("Real", "product(xs)", [("NumericalFunctions::product", False)]),
    ("Real", "sum(xs)", [("NumericalFunctions::sum", True)]),
    ("Real", "a * b", []),  # an operator, not an invocation
    (
        "ISQ::PowerValue",
        "max(a, b) [SI::W]",
        [("NumericalFunctions::max", False)],
    ),  # through a unit
    ("Real", "SequenceFunctions::size(xs)", [("SequenceFunctions::size", False)]),
    (
        "Real",
        "sum(xs) + product(xs)",
        [("NumericalFunctions::sum", True), ("NumericalFunctions::product", False)],
    ),
    (
        "Real",
        "sum(xs) * max(a, product(xs))",
        [
            ("NumericalFunctions::sum", True),
            ("NumericalFunctions::max", False),
            ("NumericalFunctions::product", False),
        ],
    ),
    ("Real", "if a < b ? a else b", []),  # a conditional is an operator expression
]

#: Every case except the conditional, which the reference walk refuses on its branch targets.
INVOCATION_CASES = [(i, c) for i, c in enumerate(CASES) if not c[1].startswith("if ")]


@pytest.fixture(scope="module")
def expressions(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    body = "\n".join(
        f"        attribute v{i} : {kind} = {source};" for i, (kind, source, _) in enumerate(CASES)
    )
    path = tmp_path_factory.mktemp("invocations") / "model.sysml"
    path.write_text(
        "package inv {\n"
        "    private import ScalarValues::*;\n"
        "    private import SI::*;\n"
        "    private import NumericalFunctions::*;\n"
        "    part def P {\n"
        "        attribute xs : Real[3];\n"
        "        attribute a : Real;\n"
        "        attribute b : Real;\n"
        f"{body}\n"
        "    }\n"
        "}\n"
    )
    model, diagnostics = SysideAdapter.load_model([path])
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return {
        str(u.name): u.feature_value_expression
        for u in SysideAdapter.elements_of_type(model, "AttributeUsage")
        if str(u.name).startswith("v")
    }


@pytest.mark.parametrize(("index", "case"), list(enumerate(CASES)), ids=[c[1] for c in CASES])
def test_invocation_uses_is_total_and_matches_allowlist(
    expressions: dict[str, Any], index: int, case: tuple[str, str, list[tuple[str, bool]]]
) -> None:
    uses = invocation_uses(expressions[f"v{index}"])
    assert [(u.callable_name, u.supported) for u in uses] == case[2]
    assert all(u.location is not None and u.authored_text for u in uses)


@pytest.mark.parametrize(
    ("index", "case"), INVOCATION_CASES, ids=[c[1] for _i, c in INVOCATION_CASES]
)
def test_the_reference_walk_refuses_exactly_when_an_unsupported_call_is_reported(
    expressions: dict[str, Any], index: int, case: tuple[str, str, list[tuple[str, bool]]]
) -> None:
    """The grandfathered raise and the total walk read one predicate, so they cannot disagree.

    The conditional is left out: it refuses for a different reason (an unresolved branch target,
    ES-006), which this test is not about.
    """
    expression = expressions[f"v{index}"]
    unsupported = [u for u in invocation_uses(expression) if not u.supported]
    if unsupported:
        with pytest.raises(SemanticEvidenceError) as raised:
            inspect_reference_uses(expression)
        assert raised.value.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED
        assert unsupported[0].callable_name in raised.value.detail
    else:
        inspect_reference_uses(expression)


def test_a_walk_that_cannot_finish_raises_its_named_code(
    expressions: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(reference_use, "MAX_EXPRESSION_DEPTH", 1)
    with pytest.raises(SemanticEvidenceError) as raised:
        invocation_uses(expressions["v5"])
    assert raised.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED
    assert raised.value.operation == "invocation_uses"
