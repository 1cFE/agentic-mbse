"""Shared data models for SysML analysis.

These types are imported by downstream packages (sysml-codegen).
Changes here may require updates to dependent packages.
"""

from dataclasses import dataclass
from typing import Any

from agentic_mbse.sysml.types import BindingType, ExpressionRef

__all__ = [
    "ExpressionRef",
    "AttributeInfo",
]

# Re-export ExpressionRef from types for clean API surface
ExpressionRef = ExpressionRef  # noqa: PLW0127


@dataclass
class AttributeInfo:
    """Core attribute metadata - used by validation AND codegen.

    This is the primary shared type between agentic-mbse and sysml-codegen.

    Attributes:
        name: Attribute name (e.g., "power_output")
        sysml_type: SysML type annotation (e.g., "Real", "Power")
        default_value: Default value if specified
        binding_type: How the attribute receives its value
        is_input: True if marked as input (direction In)
        is_output: True if marked as output (direction Out/Return)
    """

    name: str
    sysml_type: str | None = None
    default_value: Any = None
    binding_type: BindingType = BindingType.UNBOUND
    is_input: bool = False
    is_output: bool = False
