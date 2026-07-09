"""Shared data models for SysML analysis.

These types are imported by downstream packages (sysml-codegen).
Changes here may require updates to dependent packages.
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.types import BindingType, ExpressionRef

__all__ = [
    "ExpressionRef",
    "AttributeInfo",
    "RedefinitionType",
    "RedefinitionData",
    "MultiplicityData",
    "SumTerm",
    "SingletonTerm",
    "LocalTerm",
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

class RedefinitionType(str, Enum):
    """Classification of a ``:>>`` redefinition's RHS expression."""

    LITERAL = "literal"
    CHAIN = "chain"
    EXPRESSION = "expression"


@dataclass
class RedefinitionData:
    """Extracted data for one ``:>>`` redefinition."""

    owning_part_qn: str
    attribute_name: str
    redefinition_type: RedefinitionType
    literal_value: float | int | str | bool | None = None
    source_path: str | None = None
    expression_ast: Any = None
    expression_text: str = ""
    target_path: list[str] = field(default_factory=list)
    is_deep_path: bool = False
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0


@dataclass
class MultiplicityData:
    """Multiplicity information for a PartUsage within a PartDefinition."""

    part_usage_name: str
    owning_part_def_qn: str
    count: int | None
    count_attribute_name: str | None
    default_value: int | None

@dataclass
class SumTerm:
    """One sum() operand in an aggregation expression."""

    part_usage_name: str
    attribute_name: str
    multiplicity_attr: str | None
    multiplicity_count: int | None


@dataclass
class SingletonTerm:
    """A non-sum child attribute reference in an aggregation expression."""

    source_path: str


@dataclass
class LocalTerm:
    """A PartDef-local attribute reference in an aggregation expression."""

    attribute_name: str

