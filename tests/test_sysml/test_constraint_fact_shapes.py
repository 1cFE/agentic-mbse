"""Kept live-SysIDE learning tests for constraint neutral-fact shapes (S1)."""

from __future__ import annotations

import json

from tests.constraint_fact_learning import FIXTURE_DIR, capture_all_facts


def _constraint_by_name(facts: dict, name: str) -> dict:
    return next(
        item
        for item in facts["source_forms"]["constraints"]
        if item["identity"]["name"] == name
    )


def _case_by_name(facts: dict, name: str) -> dict:
    return next(
        item for item in facts["type_units"]["equality_cases"] if item["name"] == name
    )


def test_live_constraint_facts_match_golden() -> None:
    expected = json.loads((FIXTURE_DIR / "golden.json").read_text())
    assert capture_all_facts() == expected


def test_all_four_constraint_source_forms_are_structurally_distinct() -> None:
    facts = capture_all_facts()
    source_forms = {
        item["source_form"] for item in facts["source_forms"]["constraints"]
    }
    assert {
        "inline",
        "definition_typed",
        "named_usage_reference",
        "satisfy",
    } <= source_forms

    typed = _constraint_by_name(facts, "typed_feature_chain_and_literal")
    assert typed["predicate"] is not None
    assert typed["predicate"] == facts["source_forms"]["definitions"][0]["predicate"]

    referenced = next(
        item
        for item in facts["source_forms"]["constraints"]
        if item["source_form"] == "named_usage_reference"
    )
    assert referenced["identity"]["name"] is None
    assert referenced["referenced_feature_target"]["name"] == "named_usage"

    anonymous_inline = next(
        item
        for item in facts["source_forms"]["constraints"]
        if item["source_form"] == "inline" and item["identity"]["name"] is None
    )
    assert anonymous_inline["location"]["file"] == "source_forms.sysml"

    compound = facts["type_units"]["compound_boolean"]
    assert compound["operator"] == "or"
    assert compound["operands"][0]["operator"] == "and"
    assert compound["operands"][1]["operator"] == "not"


def test_membership_polarity_ownership_actuals_and_inheritance_survive() -> None:
    facts = capture_all_facts()
    assert _constraint_by_name(facts, "positive_limit")["membership_kind"] == "assumption"
    assert _constraint_by_name(facts, "below_limit")["membership_kind"] == "requirement"
    assert _constraint_by_name(facts, "negated_inline")["is_negated"] is True

    assert _constraint_by_name(facts, "inline_owner_reference")["owner"]["kind"] == "PartDefinition"
    assert _constraint_by_name(facts, "calc_owned")["owner"]["kind"] == "CalculationDefinition"
    assert _constraint_by_name(facts, "direct_owned")["owner"]["kind"] == "PartUsage"

    typed = _constraint_by_name(facts, "typed_feature_chain_and_literal")
    actuals = {item["name"]: item for item in typed["actuals"]}
    assert actuals["observed"]["value"]["kind"] == "FeatureChainExpression"
    assert actuals["limit"]["value"]["kind"] == "LiteralRational"

    defaulted = _constraint_by_name(facts, "typed_omitted_default")
    assert defaulted["omitted_default_formals"] == [
        "ConstraintFactShapeProbe::WithinLimit::limit"
    ]

    inherited = _constraint_by_name(facts, "inherited_limit")
    assert inherited["inherited_into"] == [
        "ConstraintFactShapeProbe::DerivedProbe",
        "ConstraintFactShapeProbe::retyped_usage",
    ]
    contexts = {item["identity"]["name"]: item for item in facts["source_forms"]["contexts"]}
    assert contexts["DerivedProbe"]["general_types"] == [
        "ConstraintFactShapeProbe::BaseProbe"
    ]
    assert contexts["retyped_usage"]["types"][0] == "ConstraintFactShapeProbe::BaseProbe"


def test_equality_gate_is_decided_from_static_operand_facts() -> None:
    facts = capture_all_facts()
    expected = {
        "enum_own": "support_enum_same_enumeration",
        "enum_incompatible": "block_incompatible_enumerations",
        "integer_real": "block_real_equality_requires_tolerance",
        "integer_integer": "support_integer",
        "boolean_boolean": "support_boolean",
        "string_string": "support_string",
        "quantity_same_unit": "block_real_equality_requires_tolerance",
        "quantity_convertible_unit": "block_unit_conversion_required",
        "quantity_incompatible_dimension": "block_incompatible_dimensions",
        "unit_bearing_arithmetic": "block_real_equality_requires_tolerance",
        "unitless_dimensioned": "block_unitless_dimensioned",
        "quantity_feature_unknown_unit": "block_unknown_exact_unit",
        "unresolved_operand": "block_unresolved_operand",
        "inherited_alias_type": "block_real_equality_requires_tolerance",
    }
    assert {
        item["name"]: item["decision"]
        for item in facts["type_units"]["equality_cases"]
    } == expected

    same_dimension = _case_by_name(facts, "quantity_convertible_unit")
    assert same_dimension["left"]["unit"]["dimension"] == "ISQBase::Length"
    assert same_dimension["right"]["unit"]["dimension"] == "ISQBase::Length"
    assert same_dimension["left"]["unit"]["unit"] == "SI::metre"
    assert same_dimension["right"]["unit"]["unit"] == "SI::centimetre"

    unknown_unit = _case_by_name(facts, "quantity_feature_unknown_unit")
    assert unknown_unit["left"]["unit"] == {
        "unit": None,
        "dimension": "ISQBase::Length",
    }
    assert unknown_unit["decision"] == "block_unknown_exact_unit"

    inherited_alias = _case_by_name(facts, "inherited_alias_type")
    assert inherited_alias["left"]["types"][0] == "ConstraintTypeUnitProbe::DerivedReal"
    assert inherited_alias["right"]["types"][0] == "ScalarValues::Real"


def test_loader_diagnostics_are_golden_but_not_the_equality_gate() -> None:
    facts = capture_all_facts()
    assert facts["source_forms"]["diagnostics"] == []
    assert facts["type_units"]["diagnostics"] == [
        {
            "file": "type_units.sysml",
            "line": 39,
            "column": 48,
            "severity": "error",
            "code": "reference-error",
            "message": "No Feature named 'missing_value' found.",
        }
    ]
    assert _case_by_name(facts, "enum_incompatible")["decision"] == (
        "block_incompatible_enumerations"
    )
    assert _case_by_name(facts, "quantity_incompatible_dimension")["decision"] == (
        "block_incompatible_dimensions"
    )
