"""6-level validation framework for SysML models."""

from agentic_mbse.validation.common import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    AggregatedResult,
    QualityCheckResult,
    discover_sysml_files,
    load_sysml_model,
)
from agentic_mbse.validation.level1_syntax import validate_syntax
from agentic_mbse.validation.level2_structure import validate_structure
from agentic_mbse.validation.level3_dataflow import validate_dataflow
from agentic_mbse.validation.level4_constraints import analyze_constraints
from agentic_mbse.validation.level5_traceability import validate_traceability
from agentic_mbse.validation.level6_architecture import validate_architecture
from agentic_mbse.validation.runner import QUALITY_CHECKS, run_all_checks

__all__ = [
    "run_all_checks",
    "QUALITY_CHECKS",
    "QualityCheckResult",
    "AggregatedResult",
    "discover_sysml_files",
    "load_sysml_model",
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
    "validate_syntax",
    "validate_structure",
    "validate_dataflow",
    "analyze_constraints",
    "validate_traceability",
    "validate_architecture",
]
