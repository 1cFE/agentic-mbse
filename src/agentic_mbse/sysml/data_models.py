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
    "ResolvedTargetFact",
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


@dataclass(frozen=True)
class ResolvedTargetFact:
    """The exact SysIDE-resolved target of one reference (SOURCE-IDENTITY Item 4).

    Immutable evidence of what a reference resolved to, captured while the AST is
    live. Records the resolved element itself — never a same-named substitute — so
    downstream identity work can distinguish a definition-level referent (owner is
    a Definition) from an occurrence-level one (owner is a Usage), and can follow
    the redefinition relationships the referent declares.
    """

    qualified_name: str
    element_kind: str
    element_name: str = ""
    owner_qualified_name: str = ""
    owner_is_definition: bool = False
    redefined_qualified_names: tuple[str, ...] = ()


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
    # Exact value-site identity (SOURCE-IDENTITY Item 4, D2): the redefining
    # member's own qualified name (None when the deep-path member is anonymous)
    # and the exact qualified names of the redefined target — the redefined
    # feature itself, or its chaining features for a deep path. Kept out of the
    # snapshot wire format until the v6 cut owns serialization.
    member_qualified_name: str | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    redefined_target_qns: tuple[str, ...] = field(
        default=(), metadata={"snapshot_exclude": True}
    )


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
    # Exact structural chain evidence (SOURCE-IDENTITY Item 4): the resolved
    # leaf target, the resolved chain root (the occurrence anchor), and the
    # resolved member names from root to leaf. Evidence only until snapshot v6
    # owns serialization.
    resolved_target: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    chain_root: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    resolved_member_names: tuple[str, ...] = field(
        default=(), metadata={"snapshot_exclude": True}
    )


@dataclass
class SingletonTerm:
    """A non-sum child attribute reference in an aggregation expression."""

    source_path: str
    resolved_target: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    chain_root: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    resolved_member_names: tuple[str, ...] = field(
        default=(), metadata={"snapshot_exclude": True}
    )


@dataclass
class LocalTerm:
    """A PartDef-local attribute reference in an aggregation expression."""

    attribute_name: str
    resolved_target: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    chain_root: ResolvedTargetFact | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    resolved_member_names: tuple[str, ...] = field(
        default=(), metadata={"snapshot_exclude": True}
    )
