"""The closed reference-use boundary — ``semantic-evidence/v2``.

One total inspection operation, :func:`inspect_reference_uses`, owns the complete
production reference walk.  It returns a closed union: an :class:`ExactReferenceUse`
carrying one provenance-complete :class:`ExactSemanticPath`, or an
:class:`IndexedReferenceUse` carrying only the authored reference and its location.

The point of the split is that an authored ``#(i)`` has no exact-path representation at
all.  A consumer cannot read a path off an indexed use and quietly drop the index,
because there is no path to read.  Turning one into the other needs an explicit
conversion that the static ownership gate forbids.

This module is one of the two places allowed to read a raw SysIDE selector
(``operands``, ``referent``, ``target_feature``, ``chaining_features``); the adapter owns
the metatype and document queries it delegates to.  Every other module consumes the
values built here.

See ``design.md#closed-reference-use-values`` and ``#one-total-inspection-operation``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.data_models import ResolvedTargetFact, SingletonTerm
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "MAX_EXPRESSION_DEPTH",
    "ExactReferenceUse",
    "ExactSemanticPath",
    "IndexedReferenceUse",
    "ReferenceForm",
    "ReferenceUse",
    "authored_reference_text",
    "build_aggregation_term",
    "evidence_error",
    "inspect_reference_uses",
    "is_standard_library_use",
    "materialize_operands",
    "operand_bearing_operands",
    "require_exact_reference_use",
    "resolved_chain_target",
    "resolved_chaining_features",
    "resolved_referent",
    "resolved_target_fact",
]

#: The one traversal budget.  Shared by every recursive production expression entry and
#: not selectable by a caller: a consumer that could widen it could also decide, per call
#: site, how much of an expression counts as evidence.
MAX_EXPRESSION_DEPTH = 100

#: The authored spelling of a reference.  ``bare`` is a name with no prefix, ``qualified``
#: carries a ``::`` package path, ``chain`` is a dotted feature chain.
ReferenceForm: TypeAlias = Literal["bare", "qualified", "chain"]

#: The metatypes that own an operand sequence.
_OPERAND_BEARING = ("FeatureChainExpression", "OperatorExpression", "InvocationExpression")


# ======================================================================================
# Values
# ======================================================================================


@dataclass(frozen=True)
class ExactSemanticPath:
    """One complete resolved path from a root occurrence to its leaf.

    Valid by construction: a non-null root and leaf, one fact per segment, the first
    segment being the root and the last being the leaf.  There is no public
    optional-root or optional-leaf state, so a partial walk cannot be handed on as if it
    were a resolved path.
    """

    root: ResolvedTargetFact
    segments: tuple[ResolvedTargetFact, ...]
    leaf: ResolvedTargetFact
    resolved_member_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError("an exact semantic path has at least one segment")
        if self.segments[0] is not self.root:
            raise ValueError("an exact semantic path starts at its root")
        if self.segments[-1] is not self.leaf:
            raise ValueError("an exact semantic path ends at its leaf")

    @property
    def segment_element_ids(self) -> tuple[Any, ...]:
        return tuple(segment.element_id for segment in self.segments)


@dataclass(frozen=True)
class ExactReferenceUse:
    """One reference the toolchain can honor exactly.

    Carries the resolved path plus the authored evidence a consumer would otherwise
    re-derive from the concrete syntax: the spelling, its segments, its package
    qualifier, whether the consuming context is plural, and the source location.
    """

    path: ExactSemanticPath
    form: ReferenceForm
    authored_text: str
    authored_segments: tuple[str, ...]
    authored_qualifier: str | None
    plural: bool
    location: tuple[str, int] | None


@dataclass(frozen=True)
class IndexedReferenceUse:
    """One authored ``#(i)`` reference, which has no exact representation.

    Deliberately holds nothing but the authored reference and its location — exactly what
    the unsupported-capability diagnostic needs, and nothing a consumer could mistake for
    a resolved path.
    """

    reference: str
    location: tuple[str, int] | None


ReferenceUse: TypeAlias = ExactReferenceUse | IndexedReferenceUse


# ======================================================================================
# Owned acquisition
# ======================================================================================


def evidence_error(
    code: SemanticEvidenceCode,
    operation: str,
    detail: str,
    element: Any,
    *,
    cause: BaseException | None = None,
) -> SemanticEvidenceError:
    """Build a located, referenced evidence failure for one expression element."""
    return SemanticEvidenceError(
        code,
        operation=operation,
        detail=detail,
        location=SysideAdapter.get_source_location(element),
        reference=_diagnostic_reference(element),
        cause=cause,
    )


def _diagnostic_reference(element: Any) -> str | None:
    value = getattr(element, "qualified_name", None) or getattr(element, "name", None)
    return str(value) if value else None


def materialize_operands(expression: Any) -> tuple[Any, ...]:
    """Read one expression's complete operand sequence exactly once."""
    try:
        return tuple(expression.operands)
    except Exception as cause:
        error = evidence_error(
            SemanticEvidenceCode.OPERAND_ITERATION_FAILED,
            "iterate_operands",
            "SysIDE could not materialize the expression operands",
            expression,
            cause=cause,
        )
        raise error from cause


def operand_bearing_operands(expression: Any) -> tuple[Any, ...]:
    """Operands of an expression whose metatype owns a sequence; ``()`` otherwise."""
    owns_operands = any(
        SysideAdapter.is_instance(expression, type_name) for type_name in _OPERAND_BEARING
    )
    return materialize_operands(expression) if owns_operands else ()


def resolved_referent(expression: Any) -> Any | None:
    """The exact ``referent`` SysIDE resolved for a feature reference."""
    return getattr(expression, "referent", None)


def resolved_chain_target(expression: Any) -> Any | None:
    """The exact ``target_feature`` SysIDE resolved for a feature chain."""
    return getattr(expression, "target_feature", None)


def resolved_chaining_features(feature: Any) -> tuple[Any, ...]:
    """The exact chaining features of a resolved feature, in authored order."""
    return tuple(getattr(feature, "chaining_features", None) or ())


def resolved_target_fact(element: Any) -> ResolvedTargetFact | None:
    """Capture one resolved element as an immutable fact.

    Returns ``None`` for an element SysIDE never resolved to a named feature.  Deciding
    whether that absence is fatal is the caller's, because the answer differs between a
    chain leaf (always fatal, B8) and a redefinition endpoint (often simply absent).
    """
    if element is None:
        return None
    qualified_name = getattr(element, "qualified_name", None)
    if qualified_name is None:
        return None
    owner = getattr(element, "owning_type", None)
    owner_qn = getattr(owner, "qualified_name", None) if owner is not None else None
    redefined_names: list[str] = []
    redefined_ids = []
    for redefinition in getattr(element, "owned_redefinitions", None) or []:
        redefined_feature = getattr(redefinition, "redefined_feature", None)
        redefined_qn = getattr(redefined_feature, "qualified_name", None)
        if redefined_qn is not None:
            redefined_names.append(str(redefined_qn))
        if redefined_feature is not None:
            redefined_ids.append(SysideAdapter.element_id(redefined_feature))
    document = getattr(element, "document", None)
    document_url = getattr(document, "url", None) if document else None
    return ResolvedTargetFact(
        element_id=SysideAdapter.element_id(element),
        owner_element_id=(SysideAdapter.element_id(owner) if owner is not None else None),
        redefined_element_ids=tuple(redefined_ids),
        qualified_name=str(qualified_name),
        element_kind=type(element).__name__,
        element_name=str(getattr(element, "name", None) or ""),
        owner_qualified_name=str(owner_qn) if owner_qn is not None else "",
        owner_kind=type(owner).__name__ if owner is not None else "",
        owner_is_definition=_owner_is_definition(owner),
        redefined_qualified_names=tuple(redefined_names),
        declares_value=bool(getattr(element, "feature_value_expression", None)),
        document_url=str(document_url) if document_url else "",
        document_tier=_document_tier_name(element),
        source_location=SysideAdapter.get_source_location(element),
    )


def _owner_is_definition(owner: Any) -> bool:
    if owner is None:
        return False
    return any(
        SysideAdapter.is_instance(owner, type_name)
        for type_name in (
            "PartDefinition",
            "CalculationDefinition",
            "ConstraintDefinition",
            "RequirementDefinition",
        )
    )


def _document_tier_name(element: Any) -> str:
    """The element's exact SysIDE document tier, as its enum member name.

    D6: the tier is the sole standard-library classifier — a URL, path, package name, or
    qualified name has no classification role.  A resolved reference target that cannot
    produce a tier is a named adapter failure, which propagates: recording an empty tier
    here would let a consumer read "not standard library" out of missing evidence.
    """
    return str(SysideAdapter.document_tier(element).name)


# ======================================================================================
# The one total inspection operation
# ======================================================================================


def inspect_reference_uses(expression: Any) -> tuple[ReferenceUse, ...]:
    """Return every reference use in one expression, in first-seen order.

    Total over the supported expression kinds: every reference resolves to an exact use
    or to the closed indexed variant, and anything that cannot is a named failure rather
    than a shortened path or an empty result.  Standard-library filtering is not applied
    here — the tier travels on each target fact and the call site decides.
    """
    return tuple(_walk(expression, plural=False, depth=0))


def _walk(node: Any, *, plural: bool, depth: int) -> list[ReferenceUse]:
    if node is None:
        return []
    if depth >= MAX_EXPRESSION_DEPTH:
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED,
            "inspect_reference_uses",
            "maximum expression traversal depth exhausted before all operands were visited",
            node,
        )

    # Order matters: in SysIDE's type system IndexExpression and FeatureChainExpression
    # are both operator expressions, so the specific metatypes dispatch first.
    if SysideAdapter.is_instance(node, "IndexExpression"):
        return [_indexed_use(node)]
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return [_chain_use(node, plural=plural)]
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return [_reference_use(node, plural=plural)]

    unit_value = _unit_annotation_value(node)
    if unit_value is not None:
        return _walk(unit_value, plural=plural, depth=depth + 1)

    operands = operand_bearing_operands(node)
    if not operands:
        return []
    operand_plural = plural or _is_plural_invocation(node)
    collected: list[ReferenceUse] = []
    for operand in operands:
        collected.extend(_walk(operand, plural=operand_plural, depth=depth + 1))
    return collected


def _unit_annotation_value(node: Any) -> Any | None:
    """The value operand of a structural unit annotation, or ``None`` if this is not one.

    A unit annotation (``3.0 [SI::metre]``) is structure, not data flow: the unit names the
    scale the value is written in, and nothing downstream depends on it as a reference.  So
    the annotation's shape is validated here and its value operand is walked, but the unit
    operand is never emitted as a data reference.

    Filtering it downstream by document tier would be the wrong place *and* the wrong rule:
    a project-scoped unit (``3.0 [MyUnits::widget]``) is tier ``Project`` and would reach a
    consumer as a design dependency.
    """
    if not SysideAdapter.is_instance(node, "OperatorExpression"):
        return None
    if str(getattr(node, "operator", "") or "") != "[":
        return None

    operands = materialize_operands(node)
    if len(operands) != 2:
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
            "inspect_reference_uses",
            f"unit annotation carries {len(operands)} operands, expected a value and a unit",
            node,
        )

    unit = operands[1]
    if not SysideAdapter.is_instance(unit, "FeatureReferenceExpression"):
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
            "inspect_reference_uses",
            "unit annotation's unit operand is not a feature reference",
            node,
        )
    if resolved_referent(unit) is None:
        raise evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "inspect_reference_uses",
            "unit annotation's unit operand has no exact referent",
            unit,
        )
    return operands[0]


def _is_plural_invocation(node: Any) -> bool:
    """Whether this invocation makes the references beneath it plural.

    A supported ``sum`` invocation consumes a collection, so its contained references are
    plural.  Every other supported context stays scalar.  This preserves the existing
    aggregation semantics without choosing a concrete occurrence.
    """
    function = getattr(node, "function", None)
    return bool(function is not None and getattr(function, "name", None) == "sum")


def _indexed_use(node: Any) -> IndexedReferenceUse:
    return IndexedReferenceUse(
        reference=authored_reference_text(node),
        location=SysideAdapter.get_source_location(node),
    )


def _reference_use(node: Any, *, plural: bool) -> ExactReferenceUse:
    referent = resolved_referent(node)
    fact = resolved_target_fact(referent)
    if fact is None:
        raise evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "inspect_reference_uses",
            "resolved reference has no exact target",
            node,
        )
    authored = authored_reference_text(node)
    qualifier = _authored_qualifier(authored)
    return ExactReferenceUse(
        path=ExactSemanticPath(
            root=fact, segments=(fact,), leaf=fact, resolved_member_names=()
        ),
        form="qualified" if qualifier else "bare",
        authored_text=authored,
        authored_segments=tuple(authored.split(".")),
        authored_qualifier=qualifier,
        plural=plural,
        location=SysideAdapter.get_source_location(node),
    )


def _chain_use(node: Any, *, plural: bool) -> ReferenceUse:
    """Build the exact path of one feature chain, or refuse it as indexed."""
    authored = authored_reference_text(node)
    head_segments = _chain_head_segments(node, authored)
    if head_segments is None:
        return IndexedReferenceUse(
            reference=authored, location=SysideAdapter.get_source_location(node)
        )
    root, segments, member_names = head_segments

    target = resolved_chain_target(node)
    if target is None:
        raise evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "inspect_reference_uses",
            "resolved feature chain has no exact target",
            node,
        )

    chaining = resolved_chaining_features(target)
    tail = chaining if chaining else (target,)
    for chained in tail:
        chained_fact = resolved_target_fact(chained)
        if chained_fact is None:
            raise evidence_error(
                SemanticEvidenceCode.RESOLVED_LEAF_MISSING,
                "inspect_reference_uses",
                "resolved feature chain has an incomplete exact segment",
                node,
            )
        segments.append(chained_fact)
        if chained_fact.element_name:
            member_names.append(chained_fact.element_name)

    return ExactReferenceUse(
        path=ExactSemanticPath(
            root=root,
            segments=tuple(segments),
            leaf=segments[-1],
            resolved_member_names=tuple(member_names),
        ),
        form="chain",
        authored_text=authored,
        authored_segments=tuple(authored.split(".")),
        authored_qualifier=_authored_qualifier(authored),
        plural=plural,
        location=SysideAdapter.get_source_location(node),
    )


def _chain_head_segments(
    node: Any, authored: str
) -> tuple[ResolvedTargetFact, list[ResolvedTargetFact], list[str]] | None:
    """Resolve the chain's head into (root, segments, member names).

    Returns ``None`` when the head is an authored index, which makes the whole chain an
    indexed use.  A head of any other kind is refused by name rather than rendered: a
    chain rooted in arbitrary math is not a reference the toolchain can honor.
    """
    operands = materialize_operands(node)
    if not operands:
        raise evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "inspect_reference_uses",
            "resolved feature chain has no root operand",
            node,
        )
    head = operands[0]

    if SysideAdapter.is_instance(head, "IndexExpression"):
        return None

    if SysideAdapter.is_instance(head, "FeatureChainExpression"):
        inner = _chain_use(head, plural=False)
        if isinstance(inner, IndexedReferenceUse):
            return None
        return (
            inner.path.root,
            list(inner.path.segments),
            list(inner.path.resolved_member_names),
        )

    if SysideAdapter.is_instance(head, "FeatureReferenceExpression"):
        root = resolved_target_fact(resolved_referent(head))
        if root is None:
            raise evidence_error(
                SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                "inspect_reference_uses",
                "resolved chain root has no exact referent",
                head,
            )
        return root, [root], []

    raise evidence_error(
        SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
        "inspect_reference_uses",
        f"feature chain rooted in an unsupported expression kind: {authored}",
        node,
    )


def authored_reference_text(node: Any) -> str:
    """The authored spelling of one reference expression.

    A live SysIDE element carries its concrete syntax, so the spelling is read from the
    source exactly as written.  A non-live test double has no source at all; that is the
    explicit test-double path B1 allows, and it renders from the resolved names instead.
    """
    if SysideAdapter.is_live_element(node):
        return SysideAdapter.authored_text(node)
    return _rendered_reference_spelling(node)


def _rendered_reference_spelling(node: Any) -> str:
    """Render a reference double's spelling from its resolved names (test-double path)."""
    if SysideAdapter.is_instance(node, "IndexExpression"):
        operands = materialize_operands(node)
        head = _rendered_reference_spelling(operands[0]) if operands else ""
        index = str(getattr(operands[1], "value", "")) if len(operands) > 1 else ""
        return f"{head}#({index})"
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        operands = materialize_operands(node)
        head = _rendered_reference_spelling(operands[0]) if operands else ""
        target = resolved_chain_target(node)
        chaining = resolved_chaining_features(target)
        names = [str(getattr(feature, "name", "") or "") for feature in chaining] or [
            str(getattr(target, "name", "") or "")
        ]
        return ".".join(part for part in [head, *names] if part)
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        referent = resolved_referent(node)
        return str(getattr(referent, "name", "") or getattr(node, "name", "") or "")
    return str(getattr(node, "name", "") or "")


def is_standard_library_use(use: ReferenceUse) -> bool:
    """Whether this use resolves into the SysIDE standard library.

    Mechanism only — a tier comparison over evidence the exact route already captured.
    Whether standard-library references should be filtered is the consumer's policy, and
    an indexed use is never one: it has no resolved target to classify.
    """
    return isinstance(use, ExactReferenceUse) and use.path.leaf.document_tier == "StandardLibrary"


def _authored_qualifier(authored: str) -> str | None:
    """The authored ``::`` package qualifier of a reference, if the author wrote one."""
    head = authored.split(".", 1)[0]
    if "::" not in head:
        return None
    return head.rsplit("::", 1)[0]


# ======================================================================================
# Closed-union consumption
# ======================================================================================


def require_exact_reference_use(use: ReferenceUse, *, operation: str) -> ExactReferenceUse:
    """Narrow the closed union to its exact variant, or refuse by name.

    Exhaustive over the union: an indexed use is the named unsupported capability, and
    anything else reaching here is an invariant failure rather than something to coerce.
    The runtime check is deliberate — the repository's full static type lane is not a
    green gate, so a legacy fact or lookalike must not duck-type its way through.
    """
    if isinstance(use, ExactReferenceUse):
        return use
    if isinstance(use, IndexedReferenceUse):
        raise SemanticEvidenceError(
            SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED,
            operation=operation,
            detail="an authored index has no exact reference representation",
            location=use.location,
            reference=use.reference,
        )
    raise TypeError(f"{operation} requires a ReferenceUse, got {type(use).__name__}")


def build_aggregation_term(use: ReferenceUse) -> SingletonTerm:
    """Build one aggregation term from a reference use, refusing an indexed one by name.

    The refusal happens in :func:`require_exact_reference_use`, before any term object
    exists, so no aggregation site can manufacture an index-free term.
    """
    exact = require_exact_reference_use(use, operation="build_aggregation_term")
    return SingletonTerm(
        source_path=exact.authored_text,
        resolved_target=exact.path.leaf,
        chain_root=exact.path.root,
        resolved_member_names=exact.path.resolved_member_names,
    )
