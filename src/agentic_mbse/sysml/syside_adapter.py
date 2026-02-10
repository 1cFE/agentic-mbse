"""Centralized syside integration point.

ALL syside imports in the package MUST go through this module.
No other module may contain `import syside`.

This adapter provides four key patterns:
1. Model Loading - Load SysML models from file paths
2. Element Iteration - Iterate elements by type name
3. Type Checking - Check element types (works with mocks)
4. Source Location - Extract file paths and line numbers

NOTE: syside is imported lazily to allow CLI operations (like `init`)
to work without a syside license key. The license check only happens
when actually using syside parsing functionality.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

__all__ = [
    "SysideAdapter",
    "Model",
    "Diagnostics",
    "DiagnosticSeverity",
    "Element",
    "get_syside",
]

# Lazy syside import
_syside = None


def get_syside():
    """Lazily import syside module.

    Raises ImportError with helpful message if license key not configured.
    """
    global _syside
    if _syside is None:
        try:
            import syside

            _syside = syside
        except ImportError as e:
            if "license" in str(e).lower():
                raise ImportError(
                    "syside requires a license key. Set SYSIDE_LICENSE_KEY environment "
                    "variable or configure via keyring. See syside documentation."
                ) from e
            raise
    return _syside


# DiagnosticSeverity stub for type hints and fallback
# Use title case to match syside's actual enum names
class _DiagnosticSeverityStub(IntEnum):
    """Diagnostic severity levels (stub for when syside not loaded)."""

    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


def _get_diagnostic_severity():
    """Get real DiagnosticSeverity from syside if available."""
    try:
        syside = get_syside()
        return syside.DiagnosticSeverity
    except ImportError:
        return _DiagnosticSeverityStub


# Export DiagnosticSeverity - will be real syside version when available
DiagnosticSeverity = _get_diagnostic_severity()


# Type aliases for when syside not loaded
if TYPE_CHECKING:
    import syside

    Model = syside.Model
    Diagnostics = syside.Diagnostics
    Element = syside.Element
else:
    # Runtime: these will be resolved when actually used
    Model = None
    Diagnostics = None
    Element = None


def _get_model_type():
    """Get Model type from syside."""
    return get_syside().Model


def _get_diagnostics_type():
    """Get Diagnostics type from syside."""
    return get_syside().Diagnostics


def _get_element_type():
    """Get Element type from syside."""
    return get_syside().Element


class SysideAdapter:
    """Centralized syside integration point.

    All syside operations should go through this class's methods.
    This enables:
    - Consistent error handling
    - Easy mocking for tests
    - Single point for syside version compatibility

    IMPORTANT: For mock compatibility in tests, mock class names MUST
    include the type name. Example: MockCalculationDefinition, not MockCalcDef.
    The is_instance() method falls back to `type_name in type(elem).__name__`.
    """

    _type_map: dict[str, type] | None = None

    @classmethod
    def _get_type_map(cls) -> dict[str, type]:
        """Lazily build type map from syside."""
        if cls._type_map is None:
            syside = get_syside()
            cls._type_map = {
                # Core definitions and usages
                "CalculationDefinition": syside.CalculationDefinition,
                "CalculationUsage": syside.CalculationUsage,
                "AttributeUsage": syside.AttributeUsage,
                "PartDefinition": syside.PartDefinition,
                "PartUsage": syside.PartUsage,
                "ConstraintUsage": syside.ConstraintUsage,
                "ConstraintDefinition": syside.ConstraintDefinition,
                "RequirementDefinition": syside.RequirementDefinition,
                "ReferenceUsage": syside.ReferenceUsage,
                "Import": syside.Import,
                "Comment": syside.Comment,
                "Documentation": syside.Documentation,
                # Relationships
                "FeatureTyping": syside.FeatureTyping,
                # Expressions
                "FeatureChainExpression": syside.FeatureChainExpression,
                "FeatureReferenceExpression": syside.FeatureReferenceExpression,
                "OperatorExpression": syside.OperatorExpression,
                "LiteralInteger": syside.LiteralInteger,
                "LiteralRational": syside.LiteralRational,
                "LiteralString": syside.LiteralString,
                "LiteralBoolean": syside.LiteralBoolean,
                "LiteralInfinity": syside.LiteralInfinity,
            }
        return cls._type_map

    # === Pattern 1: Model Loading ===

    @staticmethod
    def load_model(paths: list[Path]) -> tuple[Any, Any]:
        """Load SysML model from paths.

        Args:
            paths: List of file or directory paths to load

        Returns:
            (model, diagnostics) tuple from syside.try_load_model
        """
        syside = get_syside()
        files: list[str] = []
        for p in paths:
            if p.is_dir():
                files.extend(syside.collect_files_recursively(str(p)))
            else:
                files.append(str(p))
        return syside.try_load_model(files)

    @staticmethod
    def collect_files(path: Path) -> list[str]:
        """Recursively collect .sysml files from directory.

        Args:
            path: Directory path to search

        Returns:
            List of absolute file path strings
        """
        syside = get_syside()
        return syside.collect_files_recursively(str(path))

    # === Pattern 2: Element Iteration ===

    @classmethod
    def elements_of_type(cls, model: Any, type_name: str) -> Iterator[Any]:
        """Iterate elements of a given type.

        Args:
            model: Loaded syside model
            type_name: String name matching TYPE_MAP key

        Returns:
            Iterator over matching elements

        Raises:
            KeyError: If type_name not in TYPE_MAP
        """
        type_map = cls._get_type_map()
        if type_name not in type_map:
            raise KeyError(f"Unknown type '{type_name}'. Valid types: {list(type_map.keys())}")
        return model.elements(type_map[type_name])

    @classmethod
    def get_type(cls, type_name: str) -> type:
        """Get syside type by name.

        Args:
            type_name: String name matching TYPE_MAP key

        Returns:
            The syside type class
        """
        return cls._get_type_map()[type_name]

    # === Pattern 3: Type Checking ===

    @classmethod
    def is_instance(cls, elem: Any, type_name: str) -> bool:
        """Check if element is instance of type.

        Works with both real syside elements and mock objects.
        For mocks, falls back to string matching on type name.

        Args:
            elem: Element to check
            type_name: String name matching TYPE_MAP key

        Returns:
            True if element matches type
        """
        try:
            type_map = cls._get_type_map()
            sysml_type = type_map.get(type_name)
            if sysml_type is not None:
                if hasattr(elem, "isinstance"):
                    try:
                        return elem.isinstance(sysml_type)
                    except Exception:
                        pass
        except ImportError:
            # syside not available, fall back to string matching
            pass
        # Fallback: string matching for mocks/tests
        return type_name in type(elem).__name__

    # === Pattern 4: Source Location ===

    @staticmethod
    def get_source_location(elem: Any) -> tuple[str, int] | None:
        """Extract file path and line number from element.

        Args:
            elem: SysML element with source position

        Returns:
            (file_path, line_number) tuple, or None if unavailable
        """
        if not hasattr(elem, "document") or not elem.document:
            return None
        doc_url = str(elem.document.url) if elem.document.url else ""
        file_path = doc_url.replace("file:", "").replace("file://", "")
        line = 0
        if hasattr(elem, "cst_node") and elem.cst_node:
            if hasattr(elem.cst_node, "start_point") and elem.cst_node.start_point:
                line = elem.cst_node.start_point.line + 1
        return (file_path, line)

    @staticmethod
    def get_document_url(elem: Any) -> str | None:
        """Get document URL for an element.

        Traverses up ownership chain if needed.

        Args:
            elem: SysML element

        Returns:
            Document URL string, or None if not found
        """
        current = elem
        while current:
            if hasattr(current, "document") and current.document:
                if hasattr(current.document, "url") and current.document.url:
                    return str(current.document.url)
            if hasattr(current, "owner"):
                current = current.owner
            else:
                break
        return None
