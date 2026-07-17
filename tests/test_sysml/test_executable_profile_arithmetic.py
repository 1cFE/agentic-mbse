"""Value-operation gating and totality: the F1/F3 remediation (plan.md Phase 1).

Pins the D-R1 arithmetic unit policy (derived, not declared — D-R2) and the D-R3 rule that
malformed snapshot facts become `block_malformed_operand_fact`, never an `assert`. Every IR
here is built the way a snapshot could carry it; the headline mixed-unit case round-trips
through `serialize_expression`/`parse_expression` to prove it is snapshot-valid.
"""

from __future__ import annotations

import json

import pytest

from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.constraint_facts import (
    parse as parse_constraint_facts,
)
from agentic_mbse.sysml.constraint_facts import (
    serialize as serialize_constraint_facts,
)
from agentic_mbse.sysml.executable_profile import (
    PROFILE_SEMANTIC_VERSION,
    REASON_CODES,
    Eligibility,
    UsageDecision,
    evaluate_profile,
)
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    parse_expression,
    serialize_expression,
)

_OWNER = OwnerFact(
    owner=None, owning_definition=OwningDefinitionFact(kind="package", qualified_name="Synthetic")
)

_METRE = UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit")
_CENTIMETRE = UnitFact(unit="SI::centimetre", dimension="ISQBase::LengthUnit")
_SECOND = UnitFact(unit="SI::second", dimension="ISQBase::DurationUnit")


def _quantity(unit: UnitFact | None) -> OperandTypeFact:
    return OperandTypeFact(category="quantity", enumeration=None, unit=unit)


def _leaf(
    category: str,
    *,
    unit: UnitFact | None = None,
    enumeration: str | None = None,
    chain_segments: list[str] | None = None,
):
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode

    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="x", target=None, target_types=[], chain_segments=chain_segments or []
        ),
        operand_type=OperandTypeFact(category=category, enumeration=enumeration, unit=unit),
    )


def _annotated_literal(value: int, unit: UnitFact, unit_text: str) -> UnitAnnotationNode:
    """`<value> [<unit_text>]` the way live extraction emits it: an integer literal wrapped in
    a unit annotation whose own fact carries the exact unit."""
    inner = LiteralNode(
        literal=LiteralFact(
            kind="LiteralInteger", value=value, result_type="ScalarValues::Positive"
        ),
        operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
    )
    return UnitAnnotationNode(value=inner, unit_text=unit_text, operand_type=_quantity(unit))


def _int_literal(value: int) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(
            kind="LiteralInteger", value=value, result_type="ScalarValues::Integer"
        ),
        operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
    )


def _real_literal(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(
            kind="LiteralRational", value=value, result_type="ScalarValues::Rational"
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _inline_usage(name: str, predicate) -> ConstraintUsageFact:
    identity = IdentityFact(
        kind="AssertConstraintUsage", name=name, qualified_name=f"Synthetic::{name}"
    )
    return ConstraintUsageFact(
        identity=identity,
        location=LocationFact(file="synthetic.sysml", line=1, column=1),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=_OWNER,
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _decide(predicate: ExpressionIR | None) -> UsageDecision:
    facts = ConstraintFacts(
        definitions=[],
        usages=[_inline_usage("case", predicate)],
        contexts=[],
        diagnostics=[],
    )
    return evaluate_profile(facts).decisions[0]


def _reasons(decision: UsageDecision) -> set[str]:
    return {diagnostic.reason for diagnostic in decision.diagnostics}


# === F1: mixed-unit arithmetic must hit the unit gate ===


def test_mixed_unit_addition_blocks_unit_conversion_required() -> None:
    """`(1 [m] + 1 [cm]) <= 3 [m]` — the F1 hole: on v1 the declared quantity/metre fact on
    the `+` node bypassed the unit gate and this admitted silently. Round-tripped through the
    snapshot codec to prove the IR is snapshot-valid."""
    plus = OperatorNode(
        operator="+",
        operands=[_annotated_literal(1, _METRE, "m"), _annotated_literal(1, _CENTIMETRE, "cm")],
        operand_type=_quantity(_METRE),  # the stale declared fact D-R2 must ignore
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(3, _METRE, "m")], operand_type=None
    )
    round_tripped = parse_expression(serialize_expression(predicate))
    decision = _decide(round_tripped)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unit_conversion_required"}


def test_mixed_unit_addition_blocks_with_correct_reason_not_coincidental_one() -> None:
    """Same predicate, but the `+` node declares dimension-known/unit-unknown (what live
    extraction's all-children-equal rule stamps for mixed units). v1 blocked coincidentally
    with `block_unknown_exact_unit`; the derived fact names the actual gap."""
    plus = OperatorNode(
        operator="+",
        operands=[_annotated_literal(1, _METRE, "m"), _annotated_literal(1, _CENTIMETRE, "cm")],
        operand_type=_quantity(UnitFact(unit=None, dimension="ISQBase::LengthUnit")),
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(3, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unit_conversion_required"}


def test_declared_interior_fact_never_consulted_when_operands_are_clean() -> None:
    """D-R2 in the admitting direction: a garbage declared fact on the `+` node must not
    block `(1 [m] + 1 [m]) <= 2 [m]` — the derived fact decides."""
    plus = OperatorNode(
        operator="+",
        operands=[_annotated_literal(1, _METRE, "m"), _annotated_literal(1, _METRE, "m")],
        operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(2, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


def test_nested_arithmetic_recurses_to_the_inner_violation() -> None:
    """`(1 [m] + (1 [m] + 1 [cm])) <= 3 [m]` — the mixed-unit pair sits one arithmetic level
    down; the derivation must recurse, not stop at the outer `+`."""
    inner = OperatorNode(
        operator="+",
        operands=[_annotated_literal(1, _METRE, "m"), _annotated_literal(1, _CENTIMETRE, "cm")],
        operand_type=None,
    )
    outer = OperatorNode(
        operator="+", operands=[_annotated_literal(1, _METRE, "m"), inner], operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[outer, _annotated_literal(3, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unit_conversion_required"}


# === F3/D-R3: malformed snapshot facts block, never crash ===


def test_quantity_fact_without_unitfact_blocks_malformed_not_assert() -> None:
    """`a <= b`, both quantity with `OperandTypeFact.unit=None` — snapshot-parseable (the
    codec accepts a null unit), so it must be a named BLOCK, not an AssertionError."""
    predicate = OperatorNode(
        operator="<=",
        operands=[_leaf("quantity", unit=None), _leaf("quantity", unit=None)],
        operand_type=None,
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_malformed_operand_fact"}


def test_leaf_with_none_operand_type_in_arithmetic_blocks_malformed() -> None:
    """A value leaf carrying no operand fact at all inside `+` — D-R3's other malformed shape.
    On v1 this crossed the walk silently and crashed the comparison's assert."""
    bare = LiteralNode(
        literal=LiteralFact(kind="LiteralInteger", value=1, result_type=None),
        operand_type=None,  # deliberately malformed — D-R3 probe
    )
    plus = OperatorNode(
        operator="+", operands=[bare, _annotated_literal(1, _METRE, "m")], operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(2, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_malformed_operand_fact"}


@pytest.mark.parametrize("leaf_kind", ["literal", "feature_ref", "unit"])
@pytest.mark.parametrize("wire_shape", ["null", "missing"])
def test_malformed_leaf_from_facts_wire_reaches_named_profile_block(
    leaf_kind: str, wire_shape: str
) -> None:
    """The public facts codec stays shape-only for D-R3's malformed leaf fact, so both JSON
    representations reach the profile and produce its named semantic BLOCK."""
    if leaf_kind == "literal":
        bare: ExpressionIR = LiteralNode(
            literal=LiteralFact(kind="LiteralInteger", value=1, result_type=None),
            operand_type=None,
        )
    elif leaf_kind == "feature_ref":
        bare = _leaf("integer")
        bare.operand_type = None
    else:
        bare = UnitAnnotationNode(value=_int_literal(1), unit_text="m", operand_type=None)
    predicate = OperatorNode(operator="<=", operands=[bare, _int_literal(2)], operand_type=None)
    facts = ConstraintFacts(
        definitions=[],
        usages=[_inline_usage("wire_case", predicate)],
        contexts=[],
        diagnostics=[],
    )
    document = json.loads(serialize_constraint_facts(facts))
    malformed_leaf = document["usages"][0]["predicate"]["operands"][0]
    if wire_shape == "missing":
        del malformed_leaf["operand_type"]

    parsed = parse_constraint_facts(json.dumps(document))
    decision = evaluate_profile(parsed).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_malformed_operand_fact"}


def test_arithmetic_with_null_declared_fact_over_clean_operands_admits() -> None:
    """`(1 [m] + 1 [m]) <= 2 [m]` with the `+` node's declared fact null (the snapshot schema
    allows it) — v1 crashed on the comparison assert; the derived fact admits it."""
    plus = OperatorNode(
        operator="+",
        operands=[_annotated_literal(1, _METRE, "m"), _annotated_literal(1, _METRE, "m")],
        operand_type=None,
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(2, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


# === D-R1: multiplication ===


def test_quantity_times_quantity_blocks_derived_unit_unsupported() -> None:
    """`(a [m] * b [m]) <= 1 [m]` — m·m is not representable without a dimensional algebra,
    even when the declared interior fact claims a plain metre (the v1 admit path)."""
    times = OperatorNode(
        operator="*",
        operands=[_leaf("quantity", unit=_METRE), _leaf("quantity", unit=_METRE)],
        operand_type=_quantity(_METRE),
    )
    predicate = OperatorNode(
        operator="<=", operands=[times, _annotated_literal(1, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_derived_unit_unsupported"}


@pytest.mark.parametrize("order", ["scalar_first", "quantity_first"])
def test_scalar_times_quantity_admits(order: str) -> None:
    """`(2 * mass) <= 3 [m]` (either operand order) — scalar scaling keeps the quantity's
    unit, so the outer comparison gate decides (and here admits)."""
    scalar = _int_literal(2)
    quantity = _leaf("quantity", unit=_METRE)
    operands = [scalar, quantity] if order == "scalar_first" else [quantity, scalar]
    times = OperatorNode(operator="*", operands=operands, operand_type=None)
    predicate = OperatorNode(
        operator="<=", operands=[times, _annotated_literal(3, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


def test_dimensionless_product_merges_numeric_categories() -> None:
    """`(2 * 3) == 6` stays integer (support_integer admits); any real operand makes the
    product real, and real equality then blocks on tolerance."""
    integer_product = OperatorNode(
        operator="*", operands=[_int_literal(2), _int_literal(3)], operand_type=None
    )
    admitted = _decide(
        OperatorNode(operator="==", operands=[integer_product, _int_literal(6)], operand_type=None)
    )
    assert admitted.eligibility is Eligibility.ADMIT

    real_product = OperatorNode(
        operator="*", operands=[_int_literal(2), _real_literal(3.0)], operand_type=None
    )
    blocked = _decide(
        OperatorNode(operator="==", operands=[real_product, _int_literal(6)], operand_type=None)
    )
    assert blocked.eligibility is Eligibility.BLOCK
    assert _reasons(blocked) == {"block_real_equality_requires_tolerance"}


# === D-R1: division ===


def test_quantity_ratio_identical_unit_is_dimensionless() -> None:
    """`(a [m] / b [m]) <= 2` — a pure ratio needs no conversion; the derived real fact must
    feed the outer gate and pair cleanly with the dimensionless bound."""
    ratio = OperatorNode(
        operator="/",
        operands=[_leaf("quantity", unit=_METRE), _leaf("quantity", unit=_METRE)],
        operand_type=None,
    )
    predicate = OperatorNode(operator="<=", operands=[ratio, _int_literal(2)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


def test_quantity_over_dimensionless_keeps_the_unit() -> None:
    """`(a [m] / 2) <= 3 [m]` — halving a length is still a length."""
    ratio = OperatorNode(
        operator="/", operands=[_leaf("quantity", unit=_METRE), _int_literal(2)], operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[ratio, _annotated_literal(3, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


@pytest.mark.parametrize(
    ("left_unit", "right_unit", "reason"),
    [
        (_METRE, _CENTIMETRE, "block_unit_conversion_required"),  # same dimension, differing unit
        (_METRE, _SECOND, "block_derived_unit_unsupported"),  # differing dimensions (m/s)
    ],
)
def test_quantity_ratio_of_differing_units_blocks(
    left_unit: UnitFact, right_unit: UnitFact, reason: str
) -> None:
    ratio = OperatorNode(
        operator="/",
        operands=[_leaf("quantity", unit=left_unit), _leaf("quantity", unit=right_unit)],
        operand_type=None,
    )
    predicate = OperatorNode(operator="<=", operands=[ratio, _int_literal(2)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {reason}


def test_dimensionless_over_quantity_blocks_derived_unit_unsupported() -> None:
    """`(2 / a [m]) <= 3` — an inverse unit (1/m) is not representable."""
    ratio = OperatorNode(
        operator="/", operands=[_int_literal(2), _leaf("quantity", unit=_METRE)], operand_type=None
    )
    predicate = OperatorNode(operator="<=", operands=[ratio, _int_literal(3)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_derived_unit_unsupported"}


# === D-R1: exponentiation ===


@pytest.mark.parametrize("operator", ["**", "^"])
def test_power_of_dimensionless_operands_is_real(operator: str) -> None:
    power = OperatorNode(
        operator=operator, operands=[_int_literal(2), _int_literal(3)], operand_type=None
    )
    predicate = OperatorNode(operator="<=", operands=[power, _real_literal(9.0)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


def test_power_with_quantity_operand_blocks_derived_unit_unsupported() -> None:
    power = OperatorNode(
        operator="**", operands=[_leaf("quantity", unit=_METRE), _int_literal(2)], operand_type=None
    )
    predicate = OperatorNode(operator="<=", operands=[power, _int_literal(9)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_derived_unit_unsupported"}


# === D-R1: unary sign and arity ===


def test_unary_minus_preserves_the_operand_fact() -> None:
    """`(-a [m]) <= 0 [m]` — negation preserves units, so both sides gate as metres."""
    negated = OperatorNode(
        operator="-", operands=[_leaf("quantity", unit=_METRE)], operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[negated, _annotated_literal(0, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


@pytest.mark.parametrize(
    ("operator", "operand_count"),
    [("+", 0), ("+", 3), ("*", 1), ("*", 3)],
)
def test_unsupported_arithmetic_arity_blocks(operator: str, operand_count: int) -> None:
    arithmetic = OperatorNode(
        operator=operator, operands=[_int_literal(1)] * operand_count, operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[arithmetic, _int_literal(1)], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unsupported_node"}
    assert f"{operand_count} operands" in decision.diagnostics[0].message


# === D-R1: category and precedence guards ===


@pytest.mark.parametrize(
    "leaf",
    [
        pytest.param(_leaf("boolean"), id="boolean"),
        pytest.param(_leaf("string"), id="string"),
        pytest.param(_leaf("enum", enumeration="Synthetic::Color"), id="enum"),
    ],
)
def test_non_numeric_category_in_arithmetic_blocks(leaf) -> None:
    plus = OperatorNode(operator="+", operands=[leaf, _int_literal(1)], operand_type=None)
    predicate = OperatorNode(operator="<=", operands=[plus, _int_literal(2)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unsupported_operand_category"}


@pytest.mark.parametrize(
    ("category", "reason"),
    [("unresolved", "block_unresolved_operand"), ("unknown", "block_unsupported_operand_category")],
)
def test_unresolved_and_unknown_precedence_matches_unit_compatibility(
    category: str, reason: str
) -> None:
    plus = OperatorNode(
        operator="*", operands=[_leaf(category), _leaf("quantity", unit=_METRE)], operand_type=None
    )
    predicate = OperatorNode(
        operator="<=", operands=[plus, _annotated_literal(1, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {reason}


def test_arithmetic_reports_every_operand_violation_not_first_only() -> None:
    """A chain on one side and an invocation on the other — both named, matching the
    comparison walk's both-sides behavior."""
    plus = OperatorNode(
        operator="+",
        operands=[
            _leaf("real", chain_segments=["sensor", "reading"]),
            InvocationNode(
                function_qn=["Calc", "size"],
                arguments=[],
                operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    predicate = OperatorNode(operator="<=", operands=[plus, _int_literal(1)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_feature_chain", "block_invocation"}


def test_unit_annotation_over_chained_reference_still_blocks() -> None:
    """The annotation's declared fact supersedes the inner value's fact, but the inner value
    is still walked — a chained reference under `[...]` keeps blocking as before."""
    annotated = UnitAnnotationNode(
        value=_leaf("real", chain_segments=["sensor", "reading"]),
        unit_text="m",
        operand_type=_quantity(_METRE),
    )
    predicate = OperatorNode(
        operator="<=", operands=[annotated, _annotated_literal(1, _METRE, "m")], operand_type=None
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_feature_chain"}


def test_proposition_as_arithmetic_operand_blocks_non_predicate_root() -> None:
    """`((a <= b) + 1) <= 2` — a comparison sitting in a value position (D6, both directions)."""
    comparison = OperatorNode(
        operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
    )
    plus = OperatorNode(operator="+", operands=[comparison, _int_literal(1)], operand_type=None)
    predicate = OperatorNode(operator="<=", operands=[plus, _int_literal(2)], operand_type=None)
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_non_predicate_root"}


# === D-R4: version and reason-code vocabulary ===


def test_profile_semantic_version_is_v2() -> None:
    assert PROFILE_SEMANTIC_VERSION == "executable-profile/v2"


def test_new_reason_codes_are_registered() -> None:
    assert "block_derived_unit_unsupported" in REASON_CODES
    assert "block_malformed_operand_fact" in REASON_CODES


# === Connective arity (v2): a vacuous connective must not admit ===


def _boolean_comparison() -> OperatorNode:
    return OperatorNode(operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None)


@pytest.mark.parametrize(
    ("operator", "operand_count"),
    [("and", 0), ("and", 1), ("or", 0), ("or", 1), ("not", 0), ("not", 2)],
)
def test_connective_arity_blocks_instead_of_vacuous_admit(
    operator: str, operand_count: int
) -> None:
    """The audit's zero-operand `and` probe: walking no operands proved nothing, yet v1
    admitted. `not` is unary; `and`/`or` need at least two propositions."""
    predicate = OperatorNode(
        operator=operator,
        operands=[_boolean_comparison() for _ in range(operand_count)],
        operand_type=None,
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert _reasons(decision) == {"block_unsupported_node"}
    assert f"{operand_count} operands" in decision.diagnostics[0].message


@pytest.mark.parametrize(("operator", "operand_count"), [("and", 2), ("or", 3), ("not", 1)])
def test_connective_admitted_arities_still_admit(operator: str, operand_count: int) -> None:
    predicate = OperatorNode(
        operator=operator,
        operands=[_boolean_comparison() for _ in range(operand_count)],
        operand_type=None,
    )
    decision = _decide(predicate)
    assert decision.eligibility is Eligibility.ADMIT
