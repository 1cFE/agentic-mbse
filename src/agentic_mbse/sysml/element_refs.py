"""Read a fact's references (:mod:`agentic_mbse.sysml.fact_refs`) from a SysIDE element.

:func:`element_ref` names an element by its identity and raises :class:`ElementIdentityError`
when SysIDE gives it none. :func:`safe_location` says where an element was authored and never
raises.
"""

from __future__ import annotations

from typing import Any

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = ["ElementIdentityError", "element_ref", "safe_location"]

#: The exceptions an attribute read raises on a partial SysIDE node.
_PARTIAL_NODE_ERRORS = (AttributeError, TypeError, ValueError, RuntimeError)


class ElementIdentityError(Exception):
    """SysIDE gave an element no usable identity."""


def _qualified_name(element: Any) -> str | None:
    value = getattr(element, "qualified_name", None)
    return None if value is None else str(value)


def element_ref(element: Any) -> ElementRef:
    """The element's parser UUID, qualified name and metatype name."""
    try:
        return ElementRef(
            SysideAdapter.element_id(element), _qualified_name(element), type(element).__name__
        )
    except ValueError as error:
        raise ElementIdentityError(str(error)) from error


def safe_location(element: Any) -> SafeLocation:
    """Where an element was authored, as far as SysIDE can say. Never raises.

    A read that fails on a partial node leaves that part absent, so the result says less, not
    something false.
    """
    try:
        location = SysideAdapter.get_source_location(element)
    except _PARTIAL_NODE_ERRORS:
        location = None
    try:
        qualified_name = _qualified_name(element)
    except _PARTIAL_NODE_ERRORS:
        qualified_name = None
    if location is None:
        return SafeLocation(None, None, qualified_name)
    return SafeLocation(location[0] or None, location[1], qualified_name)
