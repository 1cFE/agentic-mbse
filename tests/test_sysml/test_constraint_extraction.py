"""Production constraint extractor tests — the B1 de-risk (live SysIDE, S1 fixtures)."""

from __future__ import annotations

import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.constraint_extraction import (
    _is_standard_library_element,
    extract_expression_ir,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "constraint_fact_shapes"
SOURCE_FORMS = FIXTURE_DIR / "source_forms.sysml"
TYPE_UNITS = FIXTURE_DIR / "type_units.sysml"


def _load(path: Path) -> Any:
    model, diagnostics = syside.try_load_model([str(path)])
    all_diagnostics = list(diagnostics.all)
    assert not all_diagnostics or path == TYPE_UNITS, all_diagnostics
    return model


def _neutral_facts(model: object) -> ConstraintFacts:
    """The neutral payload of one exact extraction.

    `extract_identified_constraint_facts` is the extractor; `.facts` is the neutral record it
    carries, which is what these tests are about. There is no second sweep.
    """
    return extract_identified_constraint_facts(model).facts


def _by_name(facts: ConstraintFacts, name: str):
    return next(usage for usage in facts.usages if usage.identity.name == name)


def _left_operand(facts: ConstraintFacts, case_name: str):
    usage = _by_name(facts, case_name)
    assert usage.predicate is not None
    return usage.predicate.operands[0]


def test_six_forms_extract_and_are_distinct() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    forms = {usage.source.form for usage in facts.usages}
    assert {
        "inline",
        "definition_typed",
        "named_usage_reference",
        "satisfy",
        "requirement_constraint",
        "plain_usage",
    } <= forms


def test_requirement_constraint_not_misclassified_as_inline() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    assert _by_name(facts, "positive_limit").source.form == "requirement_constraint"
    assert _by_name(facts, "below_limit").source.form == "requirement_constraint"


def test_dimension_is_real_measurement_unit_def_qn() -> None:
    facts = _neutral_facts(_load(TYPE_UNITS))
    operand = _left_operand(facts, "quantity_convertible_unit")
    assert operand.operand_type is not None
    assert operand.operand_type.unit is not None
    assert operand.operand_type.unit.dimension == "ISQBase::LengthUnit"
    assert operand.operand_type.unit.unit == "SI::metre"


def test_quantity_feature_unknown_unit_is_dimension_known_unit_unknown() -> None:
    facts = _neutral_facts(_load(TYPE_UNITS))
    operand = _left_operand(facts, "quantity_feature_unknown_unit")
    assert operand.operand_type is not None
    assert operand.operand_type.unit == type(operand.operand_type.unit)(
        unit=None, dimension="ISQBase::LengthUnit"
    )


def test_direction_is_neutral_token() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    typed = _by_name(facts, "typed_feature_chain_and_literal")
    directions = {actual.direction for actual in typed.actuals}
    assert directions <= {"in", "out", "inout"}
    assert directions


def test_membership_polarity_ownership_survive() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    assert _by_name(facts, "positive_limit").membership_kind == "assumption"
    assert _by_name(facts, "below_limit").membership_kind == "requirement"
    assert _by_name(facts, "negated_inline").is_negated is True

    assert _by_name(facts, "inline_owner_reference").owner.owning_definition.kind == "part_def"
    assert _by_name(facts, "calc_owned").owner.owning_definition.kind == "calc_def"
    assert _by_name(facts, "direct_owned").owner.owning_definition.kind == "package"
    assert _by_name(facts, "positive_limit").owner.owning_definition.kind == "requirement_def"
    assert _by_name(facts, "satisfied_limit").owner.owning_definition.kind == "package"


def test_omitted_default_formals_and_actuals_survive() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    defaulted = _by_name(facts, "typed_omitted_default")
    assert defaulted.omitted_default_formals == ["ConstraintFactShapeProbe::WithinLimit::limit"]

    typed = _by_name(facts, "typed_feature_chain_and_literal")
    actuals = {actual.name: actual for actual in typed.actuals}
    assert actuals["observed"].value is not None
    assert actuals["observed"].value.reference is not None
    assert actuals["observed"].value.reference.chain_segments == ["sensor", "reading"]
    assert actuals["limit"].value is not None
    assert actuals["limit"].value.literal is not None
    assert actuals["limit"].value.literal.value == 12.0


def test_inherited_into_and_context_facts_survive() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    inherited = _by_name(facts, "inherited_limit")
    assert inherited.inherited_into == [
        "ConstraintFactShapeProbe::DerivedProbe",
        "ConstraintFactShapeProbe::retyped_usage",
    ]
    contexts = {context.identity.name: context for context in facts.contexts}
    assert contexts["DerivedProbe"].general_types == ["ConstraintFactShapeProbe::BaseProbe"]
    assert contexts["retyped_usage"].types[0] == "ConstraintFactShapeProbe::BaseProbe"


def test_no_role_tag_on_feature_reference() -> None:
    import dataclasses

    facts = _neutral_facts(_load(SOURCE_FORMS))
    typed = _by_name(facts, "typed_feature_chain_and_literal")
    actuals = {actual.name: actual for actual in typed.actuals}
    reference = actuals["observed"].value.reference
    field_names = {f.name for f in dataclasses.fields(reference)}
    assert field_names == {"source_name", "target", "target_types", "chain_segments"}


def test_compound_boolean_tree_survives() -> None:
    facts = _neutral_facts(_load(TYPE_UNITS))
    compound = _by_name(facts, "compound_boolean")
    assert compound.predicate is not None
    assert compound.predicate.operator == "or"
    assert compound.predicate.operands[0].operator == "and"
    assert compound.predicate.operands[1].operator == "not"


def test_anonymous_assertion_identified_by_location() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    anonymous_inline = next(
        usage
        for usage in facts.usages
        if usage.source.form == "inline" and usage.identity.name is None
    )
    assert anonymous_inline.location is not None
    assert anonymous_inline.location.file.endswith("source_forms.sysml")


def test_no_str_enum_leaks_in_any_value() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    for usage in facts.usages:
        for actual in usage.actuals:
            assert actual.direction is None or "." not in actual.direction
        assert usage.membership_kind is None or "." not in usage.membership_kind


def test_owning_definition_present_and_tagged_on_every_usage() -> None:
    facts = _neutral_facts(_load(SOURCE_FORMS))
    for usage in facts.usages:
        assert usage.owner.owning_definition.kind in {
            "part_def",
            "calc_def",
            "requirement_def",
            "package",
        }
        assert usage.owner.owning_definition.qualified_name


def test_non_finite_literal_yields_extraction_diagnostic() -> None:
    """The D2a non-finite-literal diagnostic is observable through the public sink (F5).

    Uses a hand-built mock literal: SysML has no infinity/NaN literal syntax, so this
    path is unreachable via `try_load_model`.
    """

    class MockDocument:
        url = "file:///probe.sysml"

    class MockCstNode:
        class _StartPoint:
            line = 3
            character = 7

        start_point = _StartPoint()

    class MockLiteralRational:
        cached_result_type = None
        value = math.inf
        cst_node = MockCstNode()
        document = MockDocument()
        operator = None
        operands: list[Any] = []

    from agentic_mbse.sysml import extract_expression_ir
    from agentic_mbse.sysml.constraint_facts import ExtractionDiagnosticFact

    diagnostics: list[ExtractionDiagnosticFact] = []
    fact = extract_expression_ir(MockLiteralRational(), diagnostics=diagnostics)

    assert fact is not None
    assert fact.literal is not None
    assert fact.literal.value == math.inf
    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.kind == "non_finite_literal"
    assert diagnostic.operand_source is not None
    assert diagnostic.location is not None


def test_extract_expression_ir_public_single_node_entry() -> None:
    """Item 13 enabling wrapper: one bare expression node -> IR, same dispatch."""
    from agentic_mbse.sysml import extract_expression_ir
    from agentic_mbse.sysml.expression_ir import serialize_expression

    model = _load(SOURCE_FORMS)
    facts = _neutral_facts(model)
    inline = next(u for u in facts.usages if u.source.form == "inline" and u.predicate is not None)
    live = next(
        u
        for u in model.elements(syside.ConstraintUsage, include_subtypes=True)
        if getattr(u, "qualified_name", None)
        and inline.identity.qualified_name.replace("__", "::") in str(u.qualified_name)
        and getattr(u, "result_expression", None) is not None
    )
    ir = extract_expression_ir(live.result_expression)
    assert ir is not None
    assert serialize_expression(ir) == serialize_expression(inline.predicate)


def test_inherited_context_filter_uses_exact_document_tier() -> None:
    tier = syside.DocumentTier
    assert _is_standard_library_element(
        SimpleNamespace(document=SimpleNamespace(document_tier=tier.StandardLibrary))
    )
    assert not _is_standard_library_element(
        SimpleNamespace(document=SimpleNamespace(document_tier=tier.Project))
    )
    assert not _is_standard_library_element(
        SimpleNamespace(document=SimpleNamespace(document_tier=tier.External))
    )


def test_constraint_reference_without_exact_target_fails_by_name() -> None:
    class MockFeatureReferenceExpression:
        referent = None
        operands = ()
        qualified_name = "Probe::missing"
        document = SimpleNamespace(
            url="file:root-0/model.sysml", document_tier=syside.DocumentTier.Project
        )
        cst_node = SimpleNamespace(start_point=SimpleNamespace(line=2))

    with pytest.raises(SemanticEvidenceError) as caught:
        extract_expression_ir(MockFeatureReferenceExpression())

    assert caught.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert caught.value.reference == "Probe::missing"
    assert caught.value.location == ("root-0/model.sysml", 3)
