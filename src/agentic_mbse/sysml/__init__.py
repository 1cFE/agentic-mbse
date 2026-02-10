"""SysML utilities for validation and analysis.

Public API for the sysml module.
"""

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
    extract_feature_refs,
    extract_operators,
    is_literal_expression,
    is_true_static_expression,
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
    # Expression utilities
    "traverse_expression",
    "extract_feature_refs",
    "extract_operators",
    "is_literal_expression",
    "is_true_static_expression",
    "evaluate_true_static_expression",
    "STANDARD_LIBRARY_PREFIXES",
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
