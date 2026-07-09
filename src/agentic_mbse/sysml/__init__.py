"""SysML utilities for validation and analysis.

Public API for the sysml module.
"""
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
from agentic_mbse.sysml.binding import (
    classify_binding,
    extract_bindings,
)
from agentic_mbse.sysml.data_models import (
    AttributeInfo,
)
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
from agentic_mbse.sysml.graph import (
    detect_cycles,
    topological_sort,
)
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
