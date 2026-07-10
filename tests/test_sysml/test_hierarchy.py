"""Tests for shared SysML hierarchy primitive extraction."""

from __future__ import annotations

import ast
import dataclasses
import inspect
from pathlib import Path
from typing import Any

import agentic_mbse.sysml as sysml
from agentic_mbse.sysml import hierarchy
from agentic_mbse.sysml.hierarchy import (
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    classify_redefinition,
    extract_multiplicities,
    extract_redefinitions,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter


class MockLiteralInteger:
    def __init__(self, value: int):
        self.value = value


class MockFeatureReferenceExpression:
    def __init__(self, name: str):
        self.referent = type("Referent", (), {"name": name})()


class MockFeatureChainExpression:
    def __init__(self, parts: list[str]):
        self.operands = [MockFeatureReferenceExpression(parts[0])] if parts else []
        self.target_feature = type("Target", (), {"name": parts[-1]})() if len(parts) > 1 else None
        self.memberships = []


class MockOperatorExpression:
    def __init__(self, operator: str, operands: list[Any]):
        self.operator = operator
        self.operands = operands


class MockRedefinedFeature:
    def __init__(self, name: str | None = None, chaining_features: list[Any] | None = None):
        self.name = name
        self.chaining_features = chaining_features or []


class MockRedefinition:
    def __init__(self, feature: MockRedefinedFeature):
        self.redefined_feature = feature


class MockReferenceUsage:
    def __init__(
        self,
        name: str,
        feature: MockRedefinedFeature,
        expression: Any | None,
        owned_redefinitions: list[MockRedefinition] | None = None,
    ):
        self.name = name
        self.owned_redefinitions = owned_redefinitions
        if owned_redefinitions is None:
            self.owned_redefinitions = [MockRedefinition(feature)]
        self.feature_value_expression = expression


class MockPartUsage:
    def __init__(self, name: str, multiplicity: Any | None = None):
        self.name = name
        self.multiplicity = multiplicity


class MockPartDefinition:
    def __init__(self, name: str, owned_members: list[Any] | None = None):
        self.name = name
        self.owned_members = owned_members or []


class MockMultiplicity:
    def __init__(self, cached_lower_bound: Any, upper_bound: Any | None = None):
        self.cached_lower_bound = cached_lower_bound
        self.upper_bound = upper_bound


class MockUpperBound:
    def __init__(self, referent: Any):
        self.referent = referent


class MockReferent:
    def __init__(self, name: str, value: Any | None = None):
        self.name = name
        self.feature_value_expression = MockLiteralInteger(value) if value is not None else None


def _field_contract(cls: type) -> list[tuple[str, object, object, object]]:
    return [(f.name, f.type, f.default, f.default_factory) for f in dataclasses.fields(cls)]


def test_package_root_exports_hierarchy_api() -> None:
    assert sysml.RedefinitionType is hierarchy.RedefinitionType
    assert sysml.RedefinitionData is hierarchy.RedefinitionData
    assert sysml.MultiplicityData is hierarchy.MultiplicityData
    assert sysml.classify_redefinition is hierarchy.classify_redefinition
    assert sysml.extract_redefinitions is hierarchy.extract_redefinitions
    assert sysml.extract_multiplicities is hierarchy.extract_multiplicities


def test_hierarchy_all_is_exact_shared_surface() -> None:
    assert hierarchy.__all__ == [
        "RedefinitionType",
        "RedefinitionData",
        "MultiplicityData",
        "classify_redefinition",
        "extract_redefinitions",
        "extract_multiplicities",
    ]


def test_redefinition_model_contract() -> None:
    assert [item.value for item in RedefinitionType] == ["literal", "chain", "expression"]
    assert _field_contract(RedefinitionData) == [
        ("owning_part_qn", str, dataclasses.MISSING, dataclasses.MISSING),
        ("attribute_name", str, dataclasses.MISSING, dataclasses.MISSING),
        ("redefinition_type", RedefinitionType, dataclasses.MISSING, dataclasses.MISSING),
        ("literal_value", float | int | str | bool | None, None, dataclasses.MISSING),
        ("source_path", str | None, None, dataclasses.MISSING),
        ("expression_ast", Any, None, dataclasses.MISSING),
        ("expression_text", str, "", dataclasses.MISSING),
        ("target_path", list[str], dataclasses.MISSING, list),
        ("is_deep_path", bool, False, dataclasses.MISSING),
        (
            "source_file",
            Path,
            dataclasses.MISSING,
            dataclasses.fields(RedefinitionData)[9].default_factory,
        ),
        ("source_line", int, 0, dataclasses.MISSING),
    ]
    assert RedefinitionData("A", "b", RedefinitionType.LITERAL).source_file == Path("unknown")


def test_multiplicity_model_contract() -> None:
    assert _field_contract(MultiplicityData) == [
        ("part_usage_name", str, dataclasses.MISSING, dataclasses.MISSING),
        ("owning_part_def_qn", str, dataclasses.MISSING, dataclasses.MISSING),
        ("count", int | None, dataclasses.MISSING, dataclasses.MISSING),
        ("count_attribute_name", str | None, dataclasses.MISSING, dataclasses.MISSING),
        ("default_value", int | None, dataclasses.MISSING, dataclasses.MISSING),
    ]


def test_classify_redefinition_literal_chain_expression() -> None:
    literal = classify_redefinition(
        MockReferenceUsage("cost", MockRedefinedFeature("cost"), MockLiteralInteger(7)),
        "Plant::Driver",
    )
    chain = classify_redefinition(
        MockReferenceUsage(
            "cost", MockRedefinedFeature("cost"), MockFeatureChainExpression(["economics", "rate"])
        ),
        "Plant::Driver",
    )
    expr = classify_redefinition(
        MockReferenceUsage(
            "cost",
            MockRedefinedFeature("cost"),
            MockOperatorExpression(
                "+", [MockFeatureReferenceExpression("base"), MockFeatureReferenceExpression("fee")]
            ),
        ),
        "Plant::Driver",
    )

    assert literal is not None
    assert literal.redefinition_type is RedefinitionType.LITERAL
    assert literal.literal_value == 7
    assert chain is not None
    assert chain.redefinition_type is RedefinitionType.CHAIN
    assert chain.source_path == "economics.rate"
    assert expr is not None
    assert expr.redefinition_type is RedefinitionType.EXPRESSION
    assert expr.expression_text == "base + fee"


def test_classify_redefinition_skips_type_only_and_non_reference_usage() -> None:
    assert classify_redefinition(MockPartUsage("not_ref"), "Owner") is None
    assert (
        classify_redefinition(
            MockReferenceUsage("cost", MockRedefinedFeature("cost"), None), "Owner"
        )
        is None
    )
    assert (
        classify_redefinition(
            MockReferenceUsage(
                "cost", MockRedefinedFeature("cost"), MockLiteralInteger(1), owned_redefinitions=[]
            ),
            "Owner",
        )
        is None
    )


def test_classify_redefinition_deep_target_path() -> None:
    member = MockReferenceUsage(
        "unused",
        MockRedefinedFeature(
            chaining_features=[
                type("Named", (), {"name": "pv module"})(),
                type("Named", (), {"name": "wattage"})(),
            ]
        ),
        MockLiteralInteger(400),
    )

    result = classify_redefinition(member, "Design::plant")

    assert result is not None
    assert result.attribute_name == "wattage"
    assert result.target_path == ["pv_module", "wattage"]
    assert result.is_deep_path is True


def test_extract_redefinitions_scans_owned_members() -> None:
    part = MockPartDefinition(
        "Solar Array",
        [
            MockPartUsage("child"),
            MockReferenceUsage("cost", MockRedefinedFeature("cost"), MockLiteralInteger(10)),
        ],
    )

    assert extract_redefinitions(part) == [
        RedefinitionData(
            owning_part_qn="Solar_Array",
            attribute_name="cost",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=10,
        )
    ]


def test_extract_multiplicities_count_default_and_singleton_exclusion() -> None:
    count_ref = MockReferent("module_count", value=20)
    part = MockPartDefinition(
        "Solar Array",
        [
            MockPartUsage("pv module", MockMultiplicity(20.0, MockUpperBound(count_ref))),
            MockPartUsage("inverter"),
            MockReferenceUsage("ignored", MockRedefinedFeature("ignored"), MockLiteralInteger(1)),
        ],
    )

    assert extract_multiplicities(part) == [
        MultiplicityData(
            part_usage_name="pv_module",
            owning_part_def_qn="Solar_Array",
            count=20,
            count_attribute_name="module_count",
            default_value=20,
        )
    ]


def test_direct_type_map_inventory_is_mapped() -> None:
    source = inspect.getsource(hierarchy)
    tree = ast.parse(source)
    direct_strings = {
        call.args[1].value
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr in {"is_instance", "elements_of_type"}
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "SysideAdapter"
        and len(call.args) >= 2
        and isinstance(call.args[1], ast.Constant)
        and isinstance(call.args[1].value, str)
    }

    assert direct_strings == {
        "ReferenceUsage",
        "FeatureChainExpression",
        "FeatureReferenceExpression",
        "PartUsage",
    }

    # Assert against the REAL adapter map, not a fake built from the inventory —
    # a new is_instance string added to hierarchy.py must be proven whitelisted.
    assert direct_strings <= set(SysideAdapter._get_type_map())
