"""Shared SysML hierarchy primitive extraction.

This module extracts neutral hierarchy facts. Codegen-specific design override
scanning, usage-type indexing, aggregation rewriting, and orchestration stay in
sysml-codegen.
"""

from typing import Any

from agentic_mbse.sysml.data_models import (
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
)
from agentic_mbse.sysml.expression import (
    extract_feature_chain_name,
    extract_feature_reference_name,
    extract_literal_value,
    is_literal_node,
    reconstruct_expression,
)
from agentic_mbse.sysml.qualified_names import build_element_qualified_name, sanitize_name
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "RedefinitionType",
    "RedefinitionData",
    "MultiplicityData",
    "classify_redefinition",
    "extract_redefinitions",
    "extract_multiplicities",
]


def classify_redefinition(member: Any, owning_qn: str) -> RedefinitionData | None:
    """Classify one ``ReferenceUsage`` redefinition into a primitive fact."""
    if not SysideAdapter.is_instance(member, "ReferenceUsage"):
        return None

    owned_redefs = getattr(member, "owned_redefinitions", None)
    if not owned_redefs:
        return None

    redef = owned_redefs[0]
    redefined_feature = redef.redefined_feature

    chaining = list(getattr(redefined_feature, "chaining_features", []))
    if chaining:
        target_path = [sanitize_name(c.name) for c in chaining]
        attr_name = target_path[-1]
        is_deep_path = True
        # Exact value-site identity (SOURCE-IDENTITY Item 4): a deep-path
        # redefined feature is an anonymous chained Feature; its chaining
        # features carry the exact qualified names.
        redefined_target_qns = tuple(
            str(c.qualified_name)
            for c in chaining
            if getattr(c, "qualified_name", None) is not None
        )
    else:
        attr_name = sanitize_name(getattr(redefined_feature, "name", None)) or sanitize_name(
            getattr(member, "name", None)
        )
        target_path = []
        is_deep_path = False
        redefined_qn = getattr(redefined_feature, "qualified_name", None)
        redefined_target_qns = (str(redefined_qn),) if redefined_qn is not None else ()

    member_qn = getattr(member, "qualified_name", None)
    member_qualified_name = str(member_qn) if member_qn is not None else None

    expr = getattr(member, "feature_value_expression", None)
    if expr is None:
        return None

    if is_literal_node(expr):
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=extract_literal_value(expr),
            target_path=target_path,
            is_deep_path=is_deep_path,
            member_qualified_name=member_qualified_name,
            redefined_target_qns=redefined_target_qns,
        )

    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.CHAIN,
            source_path=extract_feature_chain_name(expr),
            target_path=target_path,
            is_deep_path=is_deep_path,
            member_qualified_name=member_qualified_name,
            redefined_target_qns=redefined_target_qns,
        )

    if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.CHAIN,
            source_path=extract_feature_reference_name(expr),
            target_path=target_path,
            is_deep_path=is_deep_path,
            member_qualified_name=member_qualified_name,
            redefined_target_qns=redefined_target_qns,
        )

    return RedefinitionData(
        owning_part_qn=owning_qn,
        attribute_name=attr_name,
        redefinition_type=RedefinitionType.EXPRESSION,
        expression_ast=expr,
        expression_text=reconstruct_expression(expr),
        target_path=target_path,
        is_deep_path=is_deep_path,
        member_qualified_name=member_qualified_name,
        redefined_target_qns=redefined_target_qns,
    )


def extract_redefinitions(part_element: Any) -> list[RedefinitionData]:
    """Scan owned members for ``:>>`` redefinition facts."""
    owning_qn = build_element_qualified_name(part_element)
    results: list[RedefinitionData] = []

    for member in getattr(part_element, "owned_members", []):
        redef_data = classify_redefinition(member, owning_qn)
        if redef_data is not None:
            results.append(redef_data)

    return results


def extract_multiplicities(part_element: Any) -> list[MultiplicityData]:
    """Extract multiplicity facts from child ``PartUsage`` owned members."""
    owning_qn = build_element_qualified_name(part_element)
    results: list[MultiplicityData] = []

    for member in getattr(part_element, "owned_members", []):
        if not SysideAdapter.is_instance(member, "PartUsage"):
            continue

        mult = getattr(member, "multiplicity", None)
        if mult is None:
            continue

        raw_count = getattr(mult, "cached_lower_bound", None)
        count = int(raw_count) if raw_count is not None else None

        count_attr_name = None
        default_value = None
        upper = getattr(mult, "upper_bound", None)
        if upper and hasattr(upper, "referent"):
            referent = upper.referent
            count_attr_name = getattr(referent, "name", None)
            fve = getattr(referent, "feature_value_expression", None)
            if fve and hasattr(fve, "value"):
                raw_default = fve.value
                default_value = int(raw_default) if raw_default is not None else None

        results.append(
            MultiplicityData(
                part_usage_name=sanitize_name(member.name),
                owning_part_def_qn=owning_qn,
                count=count,
                count_attribute_name=count_attr_name,
                default_value=default_value,
            )
        )

    return results
