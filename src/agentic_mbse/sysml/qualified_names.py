"""Qualified-name utilities for SysML model analysis.

These helpers normalize SysML names and qualified names into Python-safe
identifier forms. They are intentionally policy-free: codegen-specific module,
channel, parameter, and alias naming stays in sysml-codegen.
"""

import keyword
import re
from typing import Any


def sanitize_name(name: str | None) -> str:
    """Sanitize a SysML name into a legal Python identifier.

    The result is always non-empty, is always ``.isidentifier()``, and is never
    a Python keyword.
    """
    if not name:
        return "unnamed"
    name = name.strip("\'\"")
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_") or "unnamed"
    if name[0].isdigit():
        name = f"n_{name}"
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name


def build_element_qualified_name(elem: object, use_double_underscore: bool = True) -> str:
    """Build a fully qualified name for a SysML element from its owner chain."""
    separator = "__" if use_double_underscore else "::"
    chain = _build_owner_chain_with_packages(elem)
    elem_name = getattr(elem, "name", None)

    if elem_name:
        elem_name = sanitize_name(elem_name)
        if chain:
            return separator.join(chain + [elem_name])
        return elem_name

    return ""


def _build_owner_chain_with_packages(elem: object) -> list[str]:
    """Build ownership chain including packages for an element."""
    chain: list[str] = []
    current: Any = elem

    while hasattr(current, "owner") and current.owner:
        owner = current.owner

        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem and hasattr(owning_elem, "name") and owning_elem.name:
                chain.insert(0, sanitize_name(owning_elem.name))
        elif hasattr(owner, "name") and owner.name:
            chain.insert(0, sanitize_name(owner.name))

        current = owner

        if len(chain) >= 50:
            break

    return chain


def sysml_to_python_qualified_name(sysml_qname: str) -> str:
    """Convert a SysML qualified name separator from ``::`` to ``__``."""
    return sysml_qname.replace("::", "__")


def sanitize_qualified_name(sysml_qname: str) -> str:
    """Per-segment sanitize a ``::`` qualified name into a ``__`` qualified name.

    Apply exactly once at the ``::``-form to ``__``-form boundary. This helper is
    not re-entrant on an already ``__``-joined name because ``sanitize_name``
    collapses underscore runs inside a segment.
    """
    return "__".join(sanitize_name(seg) for seg in sysml_qname.split("::"))


def python_to_sysml_qualified_name(python_qname: str) -> str:
    """Convert a Python-safe qualified name separator from ``__`` to ``::``."""
    return python_qname.replace("__", "::")


def extract_simple_name(qualified_path: str) -> str:
    """Extract the leaf name from SysML, Python-safe, or dotted qualified paths."""
    if "::" in qualified_path:
        return qualified_path.split("::")[-1]
    if "__" in qualified_path:
        return qualified_path.split("__")[-1]
    if "." in qualified_path:
        return qualified_path.split(".")[-1]
    return qualified_path


__all__ = [
    "sanitize_name",
    "build_element_qualified_name",
    "sysml_to_python_qualified_name",
    "sanitize_qualified_name",
    "python_to_sysml_qualified_name",
    "extract_simple_name",
]
