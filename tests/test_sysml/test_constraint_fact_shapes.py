"""Re-anchored constraint fact shape tests: production extractor vs S1 fixtures.

Runs the **production** extractor (`agentic_mbse.sysml.constraint_extraction`) over S1's two
committed fixtures, self-compares a regenerated production golden, and asserts fact fields only
against `golden.json` as the semantic oracle. `golden.json` stays read-only (N4) — production
writes its own `production_facts.json`, regenerated and byte-compared against itself, not
against the S1 golden's byte layout.

The S1 golden's `type_units.equality_cases[].decision` verdicts are Item 3's eligibility gate,
not Item 1 facts, and are excluded here (spec Known Requirements — Tests).
"""

from __future__ import annotations

import json
from pathlib import Path

from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintUsageFact,
    parse,
    serialize,
)
from agentic_mbse.sysml.executable_profile import CONSTRAINT_USAGE_FACT_FIELD_CONSUMERS
from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "constraint_fact_shapes"
PRODUCTION_GOLDEN = FIXTURE_DIR / "production_facts.json"
S1_GOLDEN = FIXTURE_DIR / "golden.json"

# Loaded by a path relative to the repo root (CLAUDE.md's documented `uv run pytest tests/`
# invocation), not `Path(__file__)` resolved absolute — `location.file` in the extracted facts
# echoes whatever path string is passed to `try_load_model`, and the byte-stable
# `production_facts.json` golden below must not bake in a machine-specific absolute path.
_SOURCE_FORMS_REL = "tests/fixtures/constraint_fact_shapes/source_forms.sysml"
_TYPE_UNITS_REL = "tests/fixtures/constraint_fact_shapes/type_units.sysml"


def _extract_both_fixtures() -> ConstraintFacts:
    model, _diagnostics = syside.try_load_model([_SOURCE_FORMS_REL, _TYPE_UNITS_REL])
    return extract_constraint_facts(model)


def _by_name(facts: ConstraintFacts, name: str) -> ConstraintUsageFact:
    return next(usage for usage in facts.usages if usage.identity.name == name)


def test_constraint_usage_fact_field_consumers_are_exhaustive() -> None:
    from dataclasses import fields

    assert set(CONSTRAINT_USAGE_FACT_FIELD_CONSUMERS) == {
        field.name for field in fields(ConstraintUsageFact)
    }


def _s1_case_by_name(oracle: dict, name: str) -> dict:
    return next(item for item in oracle["type_units"]["equality_cases"] if item["name"] == name)


def test_production_golden_self_compares() -> None:
    """Step 2 of the re-anchor: regenerated production output byte-matches the stored golden."""
    facts = _extract_both_fixtures()
    produced = serialize(facts)
    assert produced == PRODUCTION_GOLDEN.read_text()


def test_round_trip_over_real_facts() -> None:
    """Byte-stable at the pinned version pair, over real extracted facts (not just hand-built)."""
    facts = _extract_both_fixtures()
    once = serialize(facts)
    assert serialize(parse(once)) == once


def test_six_source_forms_are_structurally_distinct() -> None:
    facts = _extract_both_fixtures()
    source_forms = {usage.source.form for usage in facts.usages}
    assert {
        "inline",
        "definition_typed",
        "named_usage_reference",
        "satisfy",
        "requirement_constraint",
        "plain_usage",
    } <= source_forms

    typed = _by_name(facts, "typed_feature_chain_and_literal")
    assert typed.predicate is not None
    assert typed.predicate == facts.definitions[0].predicate

    referenced = next(
        usage for usage in facts.usages if usage.source.form == "named_usage_reference"
    )
    assert referenced.identity.name is None
    assert referenced.source.referenced_feature_target is not None
    assert referenced.source.referenced_feature_target.name == "named_usage"

    anonymous_inline = next(
        usage
        for usage in facts.usages
        if usage.source.form == "inline" and usage.identity.name is None
    )
    assert anonymous_inline.location is not None
    assert anonymous_inline.location.file.endswith("source_forms.sysml")

    compound = _by_name(facts, "compound_boolean")
    assert compound.predicate is not None
    assert compound.predicate.operator == "or"
    assert compound.predicate.operands[0].operator == "and"
    assert compound.predicate.operands[1].operator == "not"


def test_membership_polarity_ownership_actuals_and_inheritance_match_s1_oracle() -> None:
    """Step 3 of the re-anchor: map each S1 golden fact field to its production field."""
    facts = _extract_both_fixtures()

    assert _by_name(facts, "positive_limit").membership_kind == "assumption"
    assert _by_name(facts, "below_limit").membership_kind == "requirement"
    assert _by_name(facts, "negated_inline").is_negated is True

    assert _by_name(facts, "inline_owner_reference").owner.owning_definition.kind == "part_def"
    assert _by_name(facts, "calc_owned").owner.owning_definition.kind == "calc_def"
    assert _by_name(facts, "direct_owned").owner.owning_definition.kind == "package"

    typed = _by_name(facts, "typed_feature_chain_and_literal")
    actuals = {actual.name: actual for actual in typed.actuals}
    assert actuals["observed"].value is not None
    assert actuals["observed"].value.reference.chain_segments != []
    assert actuals["limit"].value is not None
    assert actuals["limit"].value.literal.kind == "LiteralRational"

    defaulted = _by_name(facts, "typed_omitted_default")
    assert defaulted.omitted_default_formals == ["ConstraintFactShapeProbe::WithinLimit::limit"]

    inherited = _by_name(facts, "inherited_limit")
    assert inherited.inherited_into == [
        "ConstraintFactShapeProbe::DerivedProbe",
        "ConstraintFactShapeProbe::retyped_usage",
    ]
    contexts = {context.identity.name: context for context in facts.contexts}
    assert contexts["DerivedProbe"].general_types == ["ConstraintFactShapeProbe::BaseProbe"]
    assert contexts["retyped_usage"].types[0] == "ConstraintFactShapeProbe::BaseProbe"


def test_operand_facts_match_s1_type_unit_oracle() -> None:
    """Operand category/enumeration/unit facts match S1's `type_units.equality_cases` evidence.

    Excludes `decision` (Item 3's). `dimension` is asserted against the real
    `ISQBase::LengthUnit`/`MassUnit` QN (MF4) — the S1 golden's `ISQBase::Length`/`Mass` values
    are the retired `Unit`-suffix strip artifact, not real elements.
    """
    facts = _extract_both_fixtures()
    oracle = json.loads(S1_GOLDEN.read_text())

    def operand_type(case_name: str, side: int):
        usage = _by_name(facts, case_name)
        assert usage.predicate is not None
        return usage.predicate.operands[side].operand_type

    for case_name in (
        "enum_own",
        "enum_incompatible",
        "integer_real",
        "integer_integer",
        "boolean_boolean",
        "string_string",
        "unresolved_operand",
        "inherited_alias_type",
    ):
        oracle_case = _s1_case_by_name(oracle, case_name)
        for side, side_key in ((0, "left"), (1, "right")):
            produced = operand_type(case_name, side)
            oracle_side = oracle_case[side_key]
            assert produced is not None
            assert produced.category == oracle_side["category"]
            assert produced.enumeration == oracle_side["enumeration"]

    same_unit = operand_type("quantity_same_unit", 0)
    assert same_unit is not None
    assert same_unit.unit is not None
    assert same_unit.unit.unit == "SI::metre"
    assert same_unit.unit.dimension == "ISQBase::LengthUnit"

    convertible_left = operand_type("quantity_convertible_unit", 0)
    convertible_right = operand_type("quantity_convertible_unit", 1)
    assert convertible_left is not None and convertible_right is not None
    assert convertible_left.unit is not None and convertible_right.unit is not None
    assert convertible_left.unit.unit == "SI::metre"
    assert convertible_right.unit.unit == "SI::centimetre"
    assert convertible_left.unit.dimension == "ISQBase::LengthUnit"
    assert convertible_right.unit.dimension == "ISQBase::LengthUnit"

    incompatible_left = operand_type("quantity_incompatible_dimension", 0)
    incompatible_right = operand_type("quantity_incompatible_dimension", 1)
    assert incompatible_left is not None and incompatible_right is not None
    assert incompatible_left.unit is not None and incompatible_right.unit is not None
    assert incompatible_left.unit.dimension == "ISQBase::LengthUnit"
    assert incompatible_right.unit.dimension == "ISQBase::MassUnit"

    unknown_unit = operand_type("quantity_feature_unknown_unit", 0)
    assert unknown_unit is not None
    assert unknown_unit.category == "quantity"
    assert unknown_unit.unit is not None
    assert unknown_unit.unit.unit is None
    assert unknown_unit.unit.dimension == "ISQBase::LengthUnit"

    arithmetic_left = operand_type("unit_bearing_arithmetic", 0)
    arithmetic_right = operand_type("unit_bearing_arithmetic", 1)
    assert arithmetic_left is not None and arithmetic_right is not None
    assert arithmetic_left.category == "quantity"
    assert arithmetic_right.category == "quantity"

    unitless = operand_type("unitless_dimensioned", 0)
    dimensioned = operand_type("unitless_dimensioned", 1)
    assert unitless is not None and dimensioned is not None
    assert unitless.category == "real"
    assert dimensioned.category == "quantity"


def test_no_str_enum_in_any_actual_direction_or_membership_kind() -> None:
    facts = _extract_both_fixtures()
    for usage in facts.usages:
        for actual in usage.actuals:
            assert actual.direction is None or actual.direction in {"in", "out", "inout"}
        assert usage.membership_kind is None or usage.membership_kind in {
            "requirement",
            "assumption",
        }


def test_owning_definition_present_and_tagged_on_every_usage() -> None:
    facts = _extract_both_fixtures()
    for usage in facts.usages:
        assert usage.owner.owning_definition.kind in {
            "part_def",
            "calc_def",
            "requirement_def",
            "package",
        }
        assert usage.owner.owning_definition.qualified_name
