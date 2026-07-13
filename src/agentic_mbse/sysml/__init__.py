"""SysML utilities for validation and analysis.

Public API for the sysml module.

Every name below resolves lazily (PEP 562 `__getattr__`), not via eager import at package-load
time. Several submodules (`constraint_facts`, `expression_facts`, `expression_ir`,
`executable_profile`) are deliberately syside-free — a downstream consumer or a structural test
can `import agentic_mbse.sysml.constraint_facts` (or any single pure submodule) without pulling
in syside, which an eager barrel import here would defeat regardless of that submodule's own
purity (I4, executable-profile design D2).
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_mbse.sysml.aggregation import (
        AggregationDecomposition,
        AggregationDiagnostic,
        FeatureChainNode,
        FeatureReferenceNode,
        InvocationNode,
        LiteralNode,
        LocalTerm,
        NullNode,
        OperatorNode,
        SingletonTerm,
        SumNode,
        SumTerm,
        UnsupportedNode,
        WrapperFact,
        decompose_aggregation_expression,
    )
    from agentic_mbse.sysml.binding import classify_binding, extract_bindings
    from agentic_mbse.sysml.constraint_extraction import (
        extract_constraint_facts,
        extract_expression_ir,
    )
    from agentic_mbse.sysml.constraint_facts import (
        CONSTRAINT_FACTS_SCHEMA_VERSION,
        ActualFact,
        ConstraintDefinitionFact,
        ConstraintFacts,
        ConstraintSource,
        ConstraintUsageFact,
        ContextFact,
        ExtractionDiagnosticFact,
        FormalFact,
        LocationFact,
        OwnerFact,
        OwningDefinitionFact,
        RedefinitionFact,
        parse,
        serialize,
    )
    from agentic_mbse.sysml.data_models import AttributeInfo
    from agentic_mbse.sysml.expression import (
        STANDARD_LIBRARY_PREFIXES,
        evaluate_true_static_expression,
        extract_feature_chain_name,
        extract_feature_chain_segments,
        extract_feature_reference_name,
        extract_feature_refs,
        extract_literal_value,
        extract_operators,
        is_literal_expression,
        is_literal_node,
        is_true_static_expression,
        reconstruct_expression,
        reconstruct_operator_expression,
        traverse_expression,
    )
    from agentic_mbse.sysml.expression_facts import (
        FeatureReferenceFact,
        IdentityFact,
        LiteralFact,
        OperandTypeFact,
        UnitFact,
    )
    from agentic_mbse.sysml.expression_ir import (
        EXPRESSION_IR_SCHEMA_VERSION,
        ExpressionIR,
        UnitAnnotationNode,
        parse_expression,
        serialize_expression,
    )
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode as IrFeatureReferenceNode
    from agentic_mbse.sysml.expression_ir import InvocationNode as IrInvocationNode
    from agentic_mbse.sysml.expression_ir import LiteralNode as IrLiteralNode
    from agentic_mbse.sysml.expression_ir import OperatorNode as IrOperatorNode
    from agentic_mbse.sysml.expression_ir import UnsupportedNode as IrUnsupportedNode
    from agentic_mbse.sysml.graph import detect_cycles, topological_sort
    from agentic_mbse.sysml.helpers import (
        get_calc_def_name,
        get_document_url,
        get_parent_part_name,
        get_source_file,
        get_source_location,
    )
    from agentic_mbse.sysml.hierarchy import (
        MultiplicityData,
        RedefinitionData,
        RedefinitionType,
        classify_redefinition,
        extract_multiplicities,
        extract_redefinitions,
    )
    from agentic_mbse.sysml.qualified_names import (
        build_element_qualified_name,
        extract_simple_name,
        python_to_sysml_qualified_name,
        sanitize_name,
        sanitize_qualified_name,
        sysml_to_python_qualified_name,
    )
    from agentic_mbse.sysml.syside_adapter import (
        Diagnostics,
        DiagnosticSeverity,
        Element,
        Model,
        SysideAdapter,
    )
    from agentic_mbse.sysml.types import (
        BindingInfo,
        BindingType,
        CalcUsageInfo,
        ExpressionRef,
        Severity,
        ValidationCode,
        ValidationIssue,
    )

__all__ = [
    # Types
    "BindingType",
    "Severity",
    "ValidationCode",
    "ValidationIssue",
    "BindingInfo",
    "CalcUsageInfo",
    # Data Models (shared with sysml-codegen)
    "ExpressionRef",
    "AttributeInfo",
    # Constraint facts (shared with sysml-codegen; CONSTRAINT-EXEC epic)
    "CONSTRAINT_FACTS_SCHEMA_VERSION",
    "EXPRESSION_IR_SCHEMA_VERSION",
    "ActualFact",
    "ConstraintDefinitionFact",
    "ConstraintFacts",
    "ConstraintSource",
    "ConstraintUsageFact",
    "ContextFact",
    "ExpressionIR",
    "ExtractionDiagnosticFact",
    "FeatureReferenceFact",
    "FormalFact",
    "IdentityFact",
    "LiteralFact",
    "LocationFact",
    "OperandTypeFact",
    "OwnerFact",
    "OwningDefinitionFact",
    "IrFeatureReferenceNode",
    "IrInvocationNode",
    "IrLiteralNode",
    "IrOperatorNode",
    "IrUnsupportedNode",
    "RedefinitionFact",
    "UnitAnnotationNode",
    "UnitFact",
    "extract_constraint_facts",
    "extract_expression_ir",
    "parse",
    "parse_expression",
    "serialize",
    "serialize_expression",
    "SumTerm",
    "SingletonTerm",
    "LocalTerm",
    "AggregationDecomposition",
    "AggregationDiagnostic",
    "WrapperFact",
    "SumNode",
    "FeatureChainNode",
    "FeatureReferenceNode",
    "LiteralNode",
    "OperatorNode",
    "InvocationNode",
    "UnsupportedNode",
    "NullNode",
    "decompose_aggregation_expression",
    # Expression utilities
    "traverse_expression",
    "extract_feature_refs",
    "extract_operators",
    "is_literal_expression",
    "is_true_static_expression",
    "evaluate_true_static_expression",
    "extract_literal_value",
    "is_literal_node",
    "extract_feature_chain_segments",
    "extract_feature_chain_name",
    "extract_feature_reference_name",
    "reconstruct_operator_expression",
    "reconstruct_expression",
    "STANDARD_LIBRARY_PREFIXES",
    "sanitize_name",
    "build_element_qualified_name",
    "sysml_to_python_qualified_name",
    "sanitize_qualified_name",
    "python_to_sysml_qualified_name",
    "extract_simple_name",
    "RedefinitionType",
    "RedefinitionData",
    "MultiplicityData",
    "classify_redefinition",
    "extract_redefinitions",
    "extract_multiplicities",
    # Binding utilities
    "classify_binding",
    "extract_bindings",
    # Graph utilities
    "detect_cycles",
    "topological_sort",
    # Helpers
    "get_calc_def_name",
    "get_document_url",
    "get_source_file",
    "get_source_location",
    "get_parent_part_name",
    # Syside adapter
    "SysideAdapter",
    "Model",
    "Diagnostics",
    "DiagnosticSeverity",
    "Element",
]

# name -> (module, attribute-in-that-module). Most names are re-exported under their own name;
# the `Ir*` aliases pull a differently-named attribute out of `expression_ir`.
_LAZY: dict[str, tuple[str, str]] = {}
for _name in (
    "AggregationDecomposition",
    "AggregationDiagnostic",
    "FeatureChainNode",
    "FeatureReferenceNode",
    "InvocationNode",
    "LiteralNode",
    "LocalTerm",
    "NullNode",
    "OperatorNode",
    "SingletonTerm",
    "SumNode",
    "SumTerm",
    "UnsupportedNode",
    "WrapperFact",
    "decompose_aggregation_expression",
):
    _LAZY[_name] = ("agentic_mbse.sysml.aggregation", _name)
for _name in ("classify_binding", "extract_bindings"):
    _LAZY[_name] = ("agentic_mbse.sysml.binding", _name)
for _name in ("extract_constraint_facts", "extract_expression_ir"):
    _LAZY[_name] = ("agentic_mbse.sysml.constraint_extraction", _name)
for _name in (
    "CONSTRAINT_FACTS_SCHEMA_VERSION",
    "ActualFact",
    "ConstraintDefinitionFact",
    "ConstraintFacts",
    "ConstraintSource",
    "ConstraintUsageFact",
    "ContextFact",
    "ExtractionDiagnosticFact",
    "FormalFact",
    "LocationFact",
    "OwnerFact",
    "OwningDefinitionFact",
    "RedefinitionFact",
    "parse",
    "serialize",
):
    _LAZY[_name] = ("agentic_mbse.sysml.constraint_facts", _name)
_LAZY["AttributeInfo"] = ("agentic_mbse.sysml.data_models", "AttributeInfo")
for _name in (
    "STANDARD_LIBRARY_PREFIXES",
    "evaluate_true_static_expression",
    "extract_feature_chain_name",
    "extract_feature_chain_segments",
    "extract_feature_reference_name",
    "extract_feature_refs",
    "extract_literal_value",
    "extract_operators",
    "is_literal_expression",
    "is_literal_node",
    "is_true_static_expression",
    "reconstruct_expression",
    "reconstruct_operator_expression",
    "traverse_expression",
):
    _LAZY[_name] = ("agentic_mbse.sysml.expression", _name)
for _name in ("FeatureReferenceFact", "IdentityFact", "LiteralFact", "OperandTypeFact", "UnitFact"):
    _LAZY[_name] = ("agentic_mbse.sysml.expression_facts", _name)
for _name in (
    "EXPRESSION_IR_SCHEMA_VERSION",
    "ExpressionIR",
    "UnitAnnotationNode",
    "parse_expression",
    "serialize_expression",
):
    _LAZY[_name] = ("agentic_mbse.sysml.expression_ir", _name)
_LAZY["IrFeatureReferenceNode"] = ("agentic_mbse.sysml.expression_ir", "FeatureReferenceNode")
_LAZY["IrInvocationNode"] = ("agentic_mbse.sysml.expression_ir", "InvocationNode")
_LAZY["IrLiteralNode"] = ("agentic_mbse.sysml.expression_ir", "LiteralNode")
_LAZY["IrOperatorNode"] = ("agentic_mbse.sysml.expression_ir", "OperatorNode")
_LAZY["IrUnsupportedNode"] = ("agentic_mbse.sysml.expression_ir", "UnsupportedNode")
for _name in ("detect_cycles", "topological_sort"):
    _LAZY[_name] = ("agentic_mbse.sysml.graph", _name)
for _name in (
    "get_calc_def_name",
    "get_document_url",
    "get_parent_part_name",
    "get_source_file",
    "get_source_location",
):
    _LAZY[_name] = ("agentic_mbse.sysml.helpers", _name)
for _name in (
    "MultiplicityData",
    "RedefinitionData",
    "RedefinitionType",
    "classify_redefinition",
    "extract_multiplicities",
    "extract_redefinitions",
):
    _LAZY[_name] = ("agentic_mbse.sysml.hierarchy", _name)
for _name in (
    "build_element_qualified_name",
    "extract_simple_name",
    "python_to_sysml_qualified_name",
    "sanitize_name",
    "sanitize_qualified_name",
    "sysml_to_python_qualified_name",
):
    _LAZY[_name] = ("agentic_mbse.sysml.qualified_names", _name)
for _name in ("Diagnostics", "DiagnosticSeverity", "Element", "Model", "SysideAdapter"):
    _LAZY[_name] = ("agentic_mbse.sysml.syside_adapter", _name)
for _name in (
    "BindingInfo",
    "BindingType",
    "CalcUsageInfo",
    "ExpressionRef",
    "Severity",
    "ValidationCode",
    "ValidationIssue",
):
    _LAZY[_name] = ("agentic_mbse.sysml.types", _name)
del _name


def __getattr__(name: str) -> Any:
    target = _LAZY.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
