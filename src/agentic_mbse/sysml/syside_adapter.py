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

from collections.abc import Collection, Iterator
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

__all__ = [
    "SysideAdapter",
    "Model",
    "Diagnostics",
    "DiagnosticSeverity",
    "Element",
    "EXCLUDED_CONSTRAINT_TYPES",
    "is_droppable_constraint",
    "get_syside",
]

# Requirement-side ConstraintUsage subtypes that are NOT dropped executable
# predicates. This is the single production source of the drop-report exclusion
# policy (PIPELINE-TRUTH Item 4, INV-D). Both this repo and sysml-codegen import
# it; the string "RequirementUsage" must live in exactly one place.
#
# SatisfyRequirementUsage is a RequirementUsage subtype, so excluding
# "RequirementUsage" with a subtype-aware check also excludes `satisfy` — a
# deliberate choice (satisfy is requirement-side, not a free-standing dropped
# predicate). See the constraint-enumeration decision table in the module docs.
EXCLUDED_CONSTRAINT_TYPES: tuple[str, ...] = ("RequirementUsage",)

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

    Subtype-aware enumeration (PIPELINE-TRUTH Item 4)
    -------------------------------------------------
    ``model.elements(kind)`` matches ``kind`` exactly and never its subtypes.
    ``elements_of_type(..., include_subtypes=True)`` opts into the subtype
    sweep. This is per-call-site policy, recorded in the constraint-enumeration
    decision table (published in the adapter docs). The load-bearing rows:

      * ConstraintUsage drop report / non-executable checks: sweep with
        ``include_subtypes=True`` so ``assert`` (AssertConstraintUsage) is seen,
        and ``exclude=EXCLUDED_CONSTRAINT_TYPES`` so requirement-side usages
        (RequirementUsage and its ``satisfy`` subtype) are not counted as
        dropped predicates. Droppability is decided by
        :func:`is_droppable_constraint`.
      * Import dependency graph: sweep with ``include_subtypes=True`` because
        ``Import`` is abstract (only MembershipImport / NamespaceImport
        instantiate), so an exact-type query matches nothing.
      * AttributeUsage / Part* / Calc* sweeps stay exact-type (opt-OUT): no
        supported model needs their subtypes surfaced.

    Every ``elements_of_type`` and ``is_instance`` type name is resolved through
    TYPE_MAP; an unmapped name raises ``ValueError`` rather than silently
    no-opping (D6).
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
                # ConstraintUsage subtypes — required by subtype-aware constraint
                # enumeration and the kind-ladder (PIPELINE-TRUTH Item 4, D6).
                # AssertConstraintUsage <: ConstraintUsage;
                # SatisfyRequirementUsage <: RequirementUsage <: ConstraintUsage.
                "AssertConstraintUsage": syside.AssertConstraintUsage,
                "RequirementUsage": syside.RequirementUsage,
                "SatisfyRequirementUsage": syside.SatisfyRequirementUsage,
                "ConstraintDefinition": syside.ConstraintDefinition,
                "RequirementDefinition": syside.RequirementDefinition,
                "ReferenceUsage": syside.ReferenceUsage,
                "Import": syside.Import,
                "Comment": syside.Comment,
                "Documentation": syside.Documentation,
                "Package": syside.Package,
                # Constraint fact extraction (CONSTRAINT-EXEC Item 1): membership
                # kind, enum-leaf category, and formal-default recovery all need
                # a hierarchy-aware is_instance check rather than a silent
                # string-match.
                "RequirementConstraintMembership": syside.RequirementConstraintMembership,
                "EnumerationDefinition": syside.EnumerationDefinition,
                "FeatureValue": syside.FeatureValue,
                # Relationships / memberships
                "FeatureTyping": syside.FeatureTyping,
                # OwningMembership / Subclassification are used by codegen's
                # is_instance calls (extractor / usage_extractor) and previously
                # relied on the old silent string-match. D6's hard-error requires
                # every used name to resolve, so map them (strictly more correct:
                # the check becomes hierarchy-aware).
                "OwningMembership": syside.OwningMembership,
                "Subclassification": syside.Subclassification,
                # Expressions
                "FeatureChainExpression": syside.FeatureChainExpression,
                "FeatureReferenceExpression": syside.FeatureReferenceExpression,
                # NullExpression is used by codegen's expression reconstruction
                # (expression_utils) and likewise relied on the silent
                # string-match; map it under D6.
                "NullExpression": syside.NullExpression,
                # InvocationExpression is the base of OperatorExpression; the C5
                # function-invocation check (adr002.py) already used this name via
                # is_instance, relying on the old silent string-match. D6's
                # hard-error requires every used name to resolve, so map it.
                "InvocationExpression": syside.InvocationExpression,
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
    def _require_known_type(cls, type_name: str, type_map: dict[str, type]) -> None:
        """Raise if ``type_name`` is not a whitelisted type name.

        Turns a lookup miss into a loud failure instead of a silent wrong answer
        (PIPELINE-TRUTH Item 4, D6/INV-F): an unmapped name used to no-op through
        the enumeration and classification paths, shipping green on any model that
        lacked the shape it should have matched.
        """
        if type_name not in type_map:
            raise ValueError(
                f"Unknown type name '{type_name}'. "
                f"Valid types: {sorted(type_map)}"
            )

    @classmethod
    def elements_of_type(
        cls,
        model: Any,
        type_name: str,
        *,
        include_subtypes: bool = False,
        exclude: Collection[str] = (),
    ) -> Iterator[Any]:
        """Iterate elements of a given type.

        Args:
            model: Loaded syside model
            type_name: String name matching TYPE_MAP key
            include_subtypes: If True, also match subtypes of ``type_name``
                (syside ``all_nodes``); defaults to exact-type only (``nodes``).
                Opt-in per call site per the constraint-enumeration decision
                table — do NOT flip globally.
            exclude: Type names whose instances are dropped from the result
                (via subtype-aware ``is_instance``). Used to sweep a base type
                including subtypes while subtracting a requirement-side subtree,
                e.g. ``exclude=EXCLUDED_CONSTRAINT_TYPES`` on ``ConstraintUsage``.

        Returns:
            Iterator over matching elements

        Raises:
            ValueError: If ``type_name`` or any ``exclude`` name is not in TYPE_MAP.
        """
        type_map = cls._get_type_map()
        cls._require_known_type(type_name, type_map)
        for name in exclude:
            cls._require_known_type(name, type_map)
        elements = model.elements(
            type_map[type_name], include_subtypes=include_subtypes
        )
        if not exclude:
            return elements
        return (
            e
            for e in elements
            if not any(cls.is_instance(e, name) for name in exclude)
        )

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

        Raises:
            ValueError: If ``type_name`` is not in TYPE_MAP (D6/INV-F). Gated
                before the mock string-match fallback, so a mock whose name is a
                real (mapped) type still resolves by string match, but an
                unmapped name is loud instead of a silent False.
        """
        try:
            type_map = cls._get_type_map()
        except ImportError:
            # syside not available (CLI/mock path): no map to validate against,
            # so string-match only. D6's hard error targets the live path where
            # the map exists but lacks the name.
            return type_name in type(elem).__name__
        cls._require_known_type(type_name, type_map)
        sysml_type = type_map[type_name]
        if hasattr(elem, "isinstance"):
            try:
                return elem.isinstance(sysml_type)
            except Exception:
                pass
        # Fallback: string matching for mocks whose name is a mapped type.
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


def is_droppable_constraint(elem: Any) -> bool:
    """Whether a swept ``ConstraintUsage`` is a dropped executable predicate.

    A dropped predicate is an ``assert`` or a plain/``require`` constraint —
    something the pipeline cannot execute and therefore drops. Requirement-side
    usages (``RequirementUsage`` and its ``satisfy`` subtype) are excluded: they
    are requirements, not free-standing predicates.

    This is the single droppable-policy predicate (PIPELINE-TRUTH Item 4, INV-D):
    the exclusion is decided here, against :data:`EXCLUDED_CONSTRAINT_TYPES`, and
    both this repo's validators and sysml-codegen's manifest collector consume it.
    Callers pass an element already known to be a ``ConstraintUsage`` (subtypes
    included) from a subtype-aware sweep.
    """
    return not any(
        SysideAdapter.is_instance(elem, name) for name in EXCLUDED_CONSTRAINT_TYPES
    )
