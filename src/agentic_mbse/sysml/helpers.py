"""Shared helper functions for SysML element processing.

These functions are used across multiple codegen modules for common
operations like extracting names, locations, and default values from
SysML AST elements.

Consolidates duplicated implementations from:
- sysml_to_teax.py
- usage_extractor.py
- parameter_group_derivation.py
"""

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

# Type alias for SysML elements (avoids tight coupling to syside types)
SysMLElement = Any


def get_calc_def_name(elem: SysMLElement) -> str | None:
    """Extract calculation definition name from element's heritage.

    Traverses the heritage relationships to find the FeatureTyping
    that links a CalculationUsage to its CalculationDefinition.

    Args:
        elem: SysML element (typically a CalculationUsage)

    Returns:
        The calculation definition name, or None if not found
    """
    if not hasattr(elem, "heritage"):
        return None
    for relationship, target in elem.heritage:
        if SysideAdapter.is_instance(relationship, "FeatureTyping"):
            if hasattr(target, "name") and target.name:
                return target.name
    return None


def get_document_url(elem: SysMLElement) -> str | None:
    """Get document URL for an element.

    Traverses up ownership chain if needed to find containing document.

    Args:
        elem: SysML element

    Returns:
        Document URL string, or None if not found
    """
    current = elem
    while current:
        if hasattr(current, "document") and current.document:
            if hasattr(current.document, "url"):
                return str(current.document.url)
        if hasattr(current, "owner"):
            current = current.owner
        else:
            break
    return None


def get_source_file(elem: SysMLElement) -> Path:
    """Extract source file path from element (without line number).

    Lightweight version of get_source_location for early filtering.

    Args:
        elem: SysML element with source position

    Returns:
        Path to source file, or Path("unknown") if not found
    """
    doc_url = get_document_url(elem)
    if doc_url:
        file_path = doc_url.replace("file:", "").replace("file://", "")
        return Path(file_path)
    return Path("unknown")


def get_source_location(elem: SysMLElement) -> tuple[Path, int]:
    """Get source file path and line number for an element.

    Uses document.url for file path and cst_node.start_point for line.

    Args:
        elem: SysML element with source position

    Returns:
        Tuple of (file_path, line_number)
    """
    source_file = get_source_file(elem)
    source_line = 0

    # Get line number from CST node
    if hasattr(elem, "cst_node") and hasattr(elem.cst_node, "start_point"):
        source_line = elem.cst_node.start_point.line + 1

    return source_file, source_line


def get_parent_part_name(elem: SysMLElement) -> str:
    """Get the name of the parent part containing this element.

    Uses owning_namespace to find the containing PartUsage directly.
    Falls back to ownership chain traversal if needed.

    Args:
        elem: SysML element

    Returns:
        Parent part name, or empty string if none found
    """
    # Primary approach: use owning_namespace (direct parent)
    if hasattr(elem, "owning_namespace") and elem.owning_namespace:
        ns = elem.owning_namespace
        if SysideAdapter.is_instance(ns, "PartUsage"):
            if hasattr(ns, "name") and ns.name:
                return ns.name

    # Fallback: traverse up the ownership chain
    current = elem
    while hasattr(current, "owner") and current.owner:
        owner = current.owner
        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem:
                if SysideAdapter.is_instance(owning_elem, "PartUsage"):
                    if hasattr(owning_elem, "name") and owning_elem.name:
                        return owning_elem.name
        current = owner

    return ""
