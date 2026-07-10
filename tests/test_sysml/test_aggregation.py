"""Tests for shared aggregation decomposition."""

import ast
import inspect
from dataclasses import fields, is_dataclass
from types import SimpleNamespace
from typing import Any

import agentic_mbse.sysml as sysml
from agentic_mbse.sysml import aggregation, data_models, expression
from agentic_mbse.sysml.aggregation import (
    FeatureChainNode,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    SumNode,
    UnsupportedNode,
    decompose_aggregation_expression,
)
from agentic_mbse.sysml.data_models import LocalTerm, SingletonTerm, SumTerm
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.test_sysml.conftest import (
    MockFeatureChainExpression,
    MockFeatureReferenceExpression,
    MockLiteralRational,
    MockOperatorExpression,
)


class MockInvocationExpression:
    def __init__(self, function_name: str, operands: list[Any] | None = None) -> None:
        self.function = SimpleNamespace(name=function_name)
        self.operands = operands or []


class MockUnsupportedNode:
    def __str__(self) -> str:
        return "UnsupportedNode()"


class MockFeatureChainExpressionOperatorExpression(MockFeatureChainExpression):
    def __init__(self) -> None:
        super().__init__(instance_name="module", attr_name="cost")
        self.operator = "+"


class MockLiteralRationalInvocation(MockLiteralRational):
    def __init__(self, value: float = 5.0) -> None:
        super().__init__(value=value)
        self.function = SimpleNamespace(name="looks_like_invocation")


class MockNullExpression:
    pass


def invocation(name: str, *operands: Any) -> MockInvocationExpression:
    return MockInvocationExpression(name, list(operands))


def chain(part: str = "module", attr: str = "cost") -> MockFeatureChainExpression:
    return MockFeatureChainExpression(instance_name=part, attr_name=attr)


def ref(name: str = "misc") -> MockFeatureReferenceExpression:
    return MockFeatureReferenceExpression(name=name)


def assert_no_codegen_fields(result: object) -> None:
    forbidden = {
        "input_channels",
        "entry_points",
        "aliases",
        "transformed_expression",
        "AggregationExpressionData",
    }
    names = set(vars(result))
    assert forbidden.isdisjoint(names)


def test_term_dataclass_contract_and_import_identity() -> None:
    assert is_dataclass(SumTerm)
    assert [f.name for f in fields(SumTerm)] == [
        "part_usage_name",
        "attribute_name",
        "multiplicity_attr",
        "multiplicity_count",
    ]
    assert [f.name for f in fields(SingletonTerm)] == ["source_path"]
    assert [f.name for f in fields(LocalTerm)] == ["attribute_name"]

    assert aggregation.SumTerm is data_models.SumTerm is sysml.SumTerm
    assert aggregation.SingletonTerm is data_models.SingletonTerm is sysml.SingletonTerm
    assert aggregation.LocalTerm is data_models.LocalTerm is sysml.LocalTerm


def test_decompose_sum_singleton_local_and_literal_without_codegen_leaks() -> None:
    expr = MockOperatorExpression(
        "+",
        [
            invocation("sum", chain("module", "cost")),
            MockOperatorExpression("+", [chain("allocation", "total"), ref("misc")]),
            MockLiteralRational(5.0),
        ],
    )

    result = decompose_aggregation_expression(expr)

    assert_no_codegen_fields(result)
    assert isinstance(result.root, OperatorNode)
    assert result.root.operator == "+"
    assert result.sum_terms == [SumTerm("module", "cost", None, None)]
    assert result.singleton_terms == [SingletonTerm("allocation.total")]
    assert result.local_terms == [LocalTerm("misc")]
    assert not result.has_unsupported


def test_wrapper_facts_and_permissive_sum_operand_unwrap() -> None:
    expr = invocation("sum", invocation("filter", chain("module", "cost")))

    result = decompose_aggregation_expression(expr)

    assert isinstance(result.root, SumNode)
    assert result.root.wrapper_context == "filter"
    assert result.sum_terms == [SumTerm("module", "cost", None, None)]
    assert [w.function_name for w in result.wrappers] == ["filter"]
    assert [w.reason for w in result.wrappers] == ["sum_operand"]
    assert not result.has_unsupported


def test_known_non_sum_wrapper_unwraps() -> None:
    result = decompose_aggregation_expression(
        invocation("Evaluation", chain("allocation", "total"))
    )

    assert isinstance(result.root, FeatureChainNode)
    assert result.root.source_path == "allocation.total"
    assert [w.function_name for w in result.wrappers] == ["Evaluation"]
    assert [w.reason for w in result.wrappers] == ["known_wrapper"]


def test_unsupported_invocation_keeps_operands_and_diagnostic() -> None:
    result = decompose_aggregation_expression(invocation("filter", chain("module", "cost")))

    assert isinstance(result.root, InvocationNode)
    assert result.root.function_name == "filter"
    assert result.root.unsupported
    assert isinstance(result.root.operands[0], FeatureChainNode)
    assert result.diagnostics[0].kind == "unsupported_invocation"


def test_unsupported_operator_keeps_symbol_and_diagnostic() -> None:
    result = decompose_aggregation_expression(MockOperatorExpression("??", [ref("a"), ref("b")]))

    assert isinstance(result.root, OperatorNode)
    assert result.root.operator == "??"
    assert result.root.unsupported
    assert result.diagnostics[0].kind == "unsupported_operator"


def test_unknown_node_fallback_is_neutral() -> None:
    result = decompose_aggregation_expression(MockUnsupportedNode())

    assert isinstance(result.root, UnsupportedNode)
    assert result.root.fallback_render == "UnsupportedNode()"
    assert result.root.diagnostic_id == result.diagnostics[0].diagnostic_id


def test_single_element_sum_becomes_local_reference() -> None:
    result = decompose_aggregation_expression(invocation("sum", ref("misc")))

    assert isinstance(result.root, FeatureReferenceNode)
    assert result.local_terms == [LocalTerm("misc")]
    assert result.sum_terms == []


def test_dispatch_order_feature_chain_before_operator() -> None:
    result = decompose_aggregation_expression(MockFeatureChainExpressionOperatorExpression())

    assert isinstance(result.root, FeatureChainNode)
    assert result.root.source_path == "module.cost"
    assert result.local_terms == []


def test_dispatch_order_literal_before_invocation() -> None:
    result = decompose_aggregation_expression(MockLiteralRationalInvocation(7.0))

    assert isinstance(result.root, LiteralNode)
    assert result.root.render_text == "7.0"
    assert result.local_terms == []
    assert not result.has_unsupported


def test_null_expression_is_literal_node(monkeypatch) -> None:
    class NullExpressionType:
        pass

    monkeypatch.setattr(
        SysideAdapter,
        "_get_type_map",
        classmethod(lambda cls: {"NullExpression": NullExpressionType}),
    )
    SysideAdapter._type_map = None
    node = MockNullExpression()

    assert SysideAdapter.is_instance(node, "NullExpression")


def _adapter_string_literals(module: object) -> set[str]:
    source = inspect.getsource(module)
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr not in {"is_instance", "elements_of_type"}:
            continue
        if len(node.args) < 2:
            continue
        arg = node.args[1]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            names.add(arg.value)
    return names


def test_combined_type_map_inventory_is_mapped() -> None:
    used_names = _adapter_string_literals(aggregation) | _adapter_string_literals(expression)

    # Check every adapter string against the REAL type map — a new is_instance
    # string added to aggregation.py/expression.py must be proven whitelisted,
    # not asserted against a fake map built from the inventory itself.
    real_type_map = SysideAdapter._get_type_map()
    for name in used_names:
        SysideAdapter._require_known_type(name, real_type_map)

    assert {"FeatureChainExpression", "OperatorExpression", "FeatureReferenceExpression"}.issubset(
        used_names
    )
    assert {
        "LiteralInteger",
        "LiteralRational",
        "LiteralString",
        "LiteralBoolean",
        "LiteralInfinity",
        "NullExpression",
    }.issubset(used_names)
