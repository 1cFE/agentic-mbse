"""The summary occurrence port: sysml-codegen `b5663c07` instantiation, read from SysIDE.

This is the approved summary port (R1, Option A, owner 2026-10-18), productionized from spike
F1 (`.project/completed/20261018_exec-subset-profile/spikes/f1-occurrence-port/occurrence_port.py`). It
agrees with the generator by imitation, not by shared code, so it is held to the generator by a
permanent parity test in sysml-codegen's licensed suite (end condition (ii)):
`tests/conformance/subset_profile/test_occurrence_parity.py` compares this port with codegen's
occurrence index, live, over the parity seed (moved there by EXEC-SUBSET-CONTRACT Item 2a) and
codegen's corpus fixtures.

It mirrors codegen function by function. Paths are under `src/sysml_codegen/elaboration/`. The
last column is the :class:`OccurrenceAbort` member each mirrored raise becomes (P-5); the spike
used three coarse causes for all of them.

| Here | Codegen | Abort member |
|---|---|---|
| `semantic_owner`, `declaration_id` | `occurrence.py:116`, `identity.py:66-80` | `IDENTITY_UNSTABLE` |
| `_SlotIndex.build` | `occurrence.py:374-431` | `REDEFINITION_ROOT_FAMILY` |
| `_SlotIndex._root_of`, `._redefines` | `occurrence.py:296-341` | `REDEFINITION_ROOT_FAMILY` |
| `_SlotIndex.effective_declaration` | `occurrence.py:249-285` | `EFFECTIVE_DECLARATION_AMBIGUOUS` |
| `_most_specific_definition` | `occurrence.py:347-371` | `WRITER_AMBIGUOUS` |
| `_Builder._definition_closures` | `_definition_supertypes`, `occurrence.py:635-664` | `SPECIALIZATION_CYCLE` |
| `_Builder._effective_type` | `occurrence.py:667-691` | `INCOMPARABLE_TYPINGS` |
| `_Builder._bound`, `_constant_integer` | `_modeled_integer_bound`, `occurrence.py:694-788` | `WRITER_AMBIGUOUS` |
| `_Builder.reading` | `_multiplicity_indices`, `occurrence.py:812-899` | none: a neutral resolution |
| `_Builder._children` | `native_child_declarations`, `occurrence.py:927-963` | `REPEATED_NATIVE_DECLARATION` |
| `_Builder._add` | `add_usage`, `occurrence.py:965-1046` | `RECURSIVE_CONTAINMENT`, `DUPLICATE_OCCURRENCE_IDENTITY` |
| `_Builder._attachment` | `_ExactElaborator._attachment`, `elaborate.py:759-787`; `occurrences_for_type` / `_for_declaration`, `occurrence.py:495-508` | `IDENTITY_UNSTABLE` (owner only; a constraint usage is keyed by element ID, see `constraint_attachments`) |
| `_Builder.select_writer`, `_one_writer` | `_select_writer`, `_require_one_writer`, `elaborate.py:901-953` | `WRITER_AMBIGUOUS` |
| `_Builder._writers` | `_build_calculation_nodes` selection half, `elaborate.py:1195-1233` | `REDEFINITION_ROOT_FAMILY` |

Two generator behaviors are mirrored on purpose and not fixed (design D14, matrix rows G1/G2):

- G1: a part redefinition that omits bounds reads no multiplicity, so it expands to one
  occurrence and loses `ordered` (`multiplicity` is not inherited through `:>>` in SysIDE 0.8.4).
- G2: a usage-level override of a definition-owned referenced bound is ignored, because
  `_bound` looks only at definition-owned writers when the multiplicity's owner is a part def.

What the port leaves out is what codegen uses only for messages: display names, written
reference text and authored sites. Two raw selector reads go through `reference_use` (P-1):
`resolved_referent` for a referenced bound and `resolved_chaining_features` for a redefined
endpoint. Caller roots (design D7) are traversed with the same rules after the generator's,
each in its own occurrence namespace, and every visit and node records the root that reached it.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.fact_refs import SafeLocation
from agentic_mbse.sysml.occurrence_facts import (
    Attachment,
    AttachmentCause,
    BuildStage,
    MultiplicityReading,
    OccurrenceAbort,
    OccurrenceFailure,
    OccurrenceNode,
    OccurrenceScope,
    OccurrenceStructure,
    PackageScope,
    PartUsageReading,
    PathStep,
    Scope,
    UsageVisit,
    WriterSelection,
)
from agentic_mbse.sysml.reference_use import resolved_chaining_features, resolved_referent
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "declaration_id",
    "extract_occurrence_structure",
    "safe_location",
    "semantic_owner",
]

_is = SysideAdapter.is_instance


class _AbortError(Exception):
    """A mirrored generator raise, converted to an :class:`OccurrenceFailure` at the boundary."""

    def __init__(self, abort: OccurrenceAbort, element: Any, detail: str) -> None:
        super().__init__(f"{abort.value}: {detail}")
        self.abort = abort
        self.element = element
        self.detail = detail


# ---- identity and owners ---------------------------------------------------------------


def _qualified_name(element: Any) -> str | None:
    value = getattr(element, "qualified_name", None)
    return None if value is None else str(value)


def semantic_owner(element: Any) -> Any:
    """The owning type, or the owner when there is none (`occurrence.py:116`)."""
    owning_type = getattr(element, "owning_type", None)
    return owning_type if owning_type is not None else getattr(element, "owner", None)


def declaration_id(element: Any) -> UUID:
    """The reload-stable declaration identity the generator accepts (`identity.py:66-80`)."""
    if _qualified_name(element) is None:
        raise _AbortError(
            OccurrenceAbort.IDENTITY_UNSTABLE,
            element,
            f"{type(element).__name__} has no qualified name",
        )
    raw = SysideAdapter.element_id(element)
    if raw.version != 5:
        raise _AbortError(
            OccurrenceAbort.IDENTITY_UNSTABLE,
            element,
            f"{type(element).__name__} id {raw} is not UUIDv5",
        )
    return raw


def safe_location(element: Any) -> SafeLocation:
    """Where an element was authored, as far as SysIDE can say. Never raises.

    The reads are attribute lookups on the element and its document. The exceptions caught
    are the ones those lookups raise on a partial node; the result then says less, not
    something false.
    """
    try:
        location = SysideAdapter.get_source_location(element)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        location = None
    try:
        qualified_name = _qualified_name(element)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        qualified_name = None
    if location is None:
        return SafeLocation(None, None, qualified_name)
    return SafeLocation(location[0] or None, location[1], qualified_name)


# ---- redefinition slots ----------------------------------------------------------------


class _SlotIndex:
    """Feature declaration → root of its parser redefinition family (`FeatureSlotIndex`)."""

    def __init__(self, declarations: set[UUID], parents: dict[UUID, set[UUID]]) -> None:
        self._declarations = declarations
        self._parents = parents
        self._roots: dict[UUID, UUID] = {}
        self._elements: dict[UUID, Any] = {}

    @classmethod
    def build(cls, model: Any) -> _SlotIndex:
        declarations: set[UUID] = set()
        parents: dict[UUID, set[UUID]] = defaultdict(set)
        elements: dict[UUID, Any] = {}
        features = list(SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True))
        for feature in features:
            if _qualified_name(feature) is not None:
                declarations.add(declaration_id(feature))
                elements[declaration_id(feature)] = feature
        for feature in features:
            # Operator-expression formals are parser-local UUIDv4 objects with no qualified
            # name; they never enter the stable slot domain (`occurrence.py:383-385`).
            if _qualified_name(feature) is None:
                continue
            for relationship in getattr(feature, "owned_redefinitions", ()) or ():
                redefined = getattr(relationship, "redefined_feature", None)
                redefining = getattr(relationship, "redefining_feature", None)
                if redefined is None or redefining is None:
                    raise _AbortError(
                        OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                        feature,
                        "a redefinition relationship has a missing semantic endpoint",
                    )
                chain = resolved_chaining_features(redefined)
                endpoint = chain[-1] if chain else redefined
                if _qualified_name(endpoint) is None or _qualified_name(redefining) is None:
                    raise _AbortError(
                        OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                        feature,
                        "a redefinition endpoint has no stable declaration identity",
                    )
                endpoint_id, redefining_id = declaration_id(endpoint), declaration_id(redefining)
                declarations.update((endpoint_id, redefining_id))
                elements.setdefault(endpoint_id, endpoint)
                elements.setdefault(redefining_id, redefining)
                parents[redefining_id].add(endpoint_id)
        index = cls(declarations, parents)
        index._elements = elements
        for declaration in declarations:
            index.slot_of(declaration)
        return index

    def has(self, declaration: UUID) -> bool:
        return declaration in self._declarations

    def slot_of(self, declaration: UUID) -> UUID:
        if declaration not in self._declarations:
            raise KeyError(f"unknown feature declaration {declaration}")
        return self._root_of(declaration, ())

    def _root_of(self, declaration: UUID, active: tuple[UUID, ...]) -> UUID:
        cached = self._roots.get(declaration)
        if cached is not None:
            return cached
        if declaration in active:
            raise _AbortError(
                OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                self._elements.get(declaration),
                f"redefinition family contains a cycle at {declaration}",
            )
        parents = self._parents.get(declaration, set())
        if not parents:
            root = declaration
        else:
            roots = {self._root_of(parent, active + (declaration,)) for parent in parents}
            if len(roots) != 1:
                raise _AbortError(
                    OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                    self._elements.get(declaration),
                    f"redefinition declaration {declaration} has unrelated roots",
                )
            root = min(roots)
        self._roots[declaration] = root
        return root

    def _redefines(self, declaration: UUID, ancestor: UUID, active: tuple[UUID, ...]) -> bool:
        if declaration in active:
            raise _AbortError(
                OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                self._elements.get(declaration),
                f"redefinition family contains a cycle at {declaration}",
            )
        parents = self._parents.get(declaration, set())
        return ancestor in parents or any(
            self._redefines(parent, ancestor, active + (declaration,)) for parent in parents
        )

    def effective_declaration(self, candidates: set[UUID]) -> UUID:
        """The sole candidate that redefines every other candidate."""
        anchor = self._elements.get(min(candidates)) if candidates else None
        if not candidates or len({self.slot_of(c) for c in candidates}) != 1:
            raise _AbortError(
                OccurrenceAbort.EFFECTIVE_DECLARATION_AMBIGUOUS,
                anchor,
                "effective declaration candidates are empty or belong to different slots",
            )
        winners = {
            candidate
            for candidate in candidates
            if all(
                other == candidate or self._redefines(candidate, other, ()) for other in candidates
            )
        }
        if len(winners) != 1:
            raise _AbortError(
                OccurrenceAbort.EFFECTIVE_DECLARATION_AMBIGUOUS,
                anchor,
                "native usage view has no unique effective declaration for one slot",
            )
        return next(iter(winners))


def _most_specific_definition(
    candidates: set[UUID], closures: dict[UUID, frozenset[UUID]], element: Any
) -> UUID:
    winners = {c for c in candidates if all(o == c or o in closures[c] for o in candidates)}
    if len(winners) != 1:
        raise _AbortError(
            OccurrenceAbort.WRITER_AMBIGUOUS,
            element,
            "applicable definition writers have no unique most-specific owner",
        )
    return min(winners)


def _constant_integer(expression: Any) -> int | None:
    if expression is None:
        return None
    try:
        value = evaluate_true_static_expression(expression)
    except (ArithmeticError, TypeError, ValueError):
        return None
    if not math.isfinite(value) or not value.is_integer():
        return None
    return int(value)


def _one_writer(candidates: list[Any]) -> Any:
    if len(candidates) != 1:
        raise _AbortError(
            OccurrenceAbort.WRITER_AMBIGUOUS,
            candidates[0] if candidates else None,
            f"a scope has {len(candidates)} incomparable value writers",
        )
    return candidates[0]


def _scope_order(scope: Scope) -> tuple[int, str, tuple[tuple[str, int], ...]]:
    if isinstance(scope, PackageScope):
        return (0, str(scope.package_id), ())
    return (1, str(scope.root_id), tuple(step.sort_key() for step in scope.path))


# ---- the occurrence build --------------------------------------------------------------


class _Builder:
    """`build_occurrence_index` plus the elaborator's attachment and writer selection."""

    def __init__(self, model: Any, slots: _SlotIndex) -> None:
        self.model = model
        self.slots = slots
        self.definitions = {
            declaration_id(d): d for d in SysideAdapter.elements_of_type(model, "PartDefinition")
        }
        self.closures = self._definition_closures()
        usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
        self.usages = usages
        self.usage_ids = {declaration_id(usage) for usage in usages}
        self.attributes_by_slot: dict[UUID, list[Any]] = defaultdict(list)
        for attribute in SysideAdapter.elements_of_type(model, "AttributeUsage"):
            if _qualified_name(attribute) is not None:
                self.attributes_by_slot[slots.slot_of(declaration_id(attribute))].append(attribute)
        self.generator_roots = sorted(
            (
                usage
                for usage in usages
                if not (
                    _is(semantic_owner(usage), "PartDefinition")
                    or _is(semantic_owner(usage), "PartUsage")
                )
            ),
            key=lambda usage: str(declaration_id(usage)),
        )
        #: One occurrence namespace per root kind: the generator's roots share one, as in
        #: codegen, and each caller root gets its own.
        self.nodes: dict[UUID, dict[tuple[PathStep, ...], OccurrenceNode]] = {}
        self.namespace_of_root: dict[UUID, UUID] = {}
        self.visits: list[UsageVisit] = []

    def _definition_closures(self) -> dict[UUID, frozenset[UUID]]:
        direct: dict[UUID, set[UUID]] = defaultdict(set)
        for definition_id, definition in self.definitions.items():
            for specialization in getattr(definition, "owned_specializations", ()) or ():
                supertype = getattr(specialization, "superclassifier", None)
                if supertype is None or _qualified_name(supertype) is None:
                    continue
                if declaration_id(supertype) in self.definitions:
                    direct[definition_id].add(declaration_id(supertype))

        def closure(definition_id: UUID, active: tuple[UUID, ...]) -> frozenset[UUID]:
            if definition_id in active:
                raise _AbortError(
                    OccurrenceAbort.SPECIALIZATION_CYCLE,
                    self.definitions.get(definition_id),
                    f"part-definition specialization cycle at {definition_id}",
                )
            result = {definition_id}
            for parent in direct.get(definition_id, set()):
                result |= closure(parent, active + (definition_id,))
            return frozenset(result)

        return {d: closure(d, ()) for d in self.definitions}

    def _effective_type(self, usage: Any) -> UUID | None:
        candidates = {
            declaration_id(t)
            for t in (getattr(usage, "types", None) or ())
            if _qualified_name(t) is not None and declaration_id(t) in self.definitions
        }
        specific = {
            c for c in candidates if not any(c != o and c in self.closures[o] for o in candidates)
        }
        if len(specific) > 1:
            raise _AbortError(
                OccurrenceAbort.INCOMPARABLE_TYPINGS,
                usage,
                "part usage has incomparable exact user-definition typings",
            )
        return min(specific, default=None)

    def _children(self, usage: Any) -> tuple[Any, ...]:
        native: dict[UUID, Any] = {}
        for candidate in getattr(usage, "usages", ()) or ():
            if not _is(candidate, "PartUsage") or not bool(
                getattr(candidate, "is_composite", False)
            ):
                continue
            if _qualified_name(candidate) is None:
                continue
            candidate_id = declaration_id(candidate)
            # `usages` also exposes inherited standard-library features; only declarations in
            # the loaded user model are in the generator's containment population.
            if candidate_id not in self.usage_ids:
                continue
            existing = native.get(candidate_id)
            if existing is not None and existing is not candidate:
                raise _AbortError(
                    OccurrenceAbort.REPEATED_NATIVE_DECLARATION,
                    candidate,
                    "native usage view repeats one declaration",
                )
            native[candidate_id] = candidate
        by_slot: dict[UUID, set[UUID]] = defaultdict(set)
        for candidate_id in native:
            by_slot[self.slots.slot_of(candidate_id)].add(candidate_id)
        selected = {self.slots.effective_declaration(c) for c in by_slot.values()}
        return tuple(native[i] for i in sorted(selected, key=str))

    def _bound(self, bound: Any, usage: Any, parent: OccurrenceNode | None) -> int | None:
        direct = _constant_integer(bound)
        if direct is not None:
            return direct
        if not _is(bound, "FeatureReferenceExpression"):
            return None
        referent = resolved_referent(bound)
        if referent is None or _qualified_name(referent) is None:
            return None
        referent_id = declaration_id(referent)
        if not self.slots.has(referent_id):
            return None
        candidates = self.attributes_by_slot.get(self.slots.slot_of(referent_id), [])
        owner = semantic_owner(usage)
        if _is(owner, "PartUsage"):
            candidates = [
                c
                for c in candidates
                if _is(semantic_owner(c), "PartUsage")
                and declaration_id(semantic_owner(c)) == declaration_id(owner)
            ]
        elif _is(owner, "PartDefinition") and parent is not None:
            # G2: only definition-owned writers are read here, so a usage-level override of a
            # definition-owned bound is ignored, exactly as the generator ignores it.
            writers = [
                c
                for c in candidates
                if _is(semantic_owner(c), "PartDefinition")
                and declaration_id(semantic_owner(c)) in parent.type_closure
            ]
            if writers:
                chosen = _most_specific_definition(
                    {declaration_id(semantic_owner(c)) for c in writers}, self.closures, usage
                )
                candidates = [c for c in writers if declaration_id(semantic_owner(c)) == chosen]
            else:
                candidates = []
        elif _is(owner, "Package"):
            candidates = [
                c
                for c in candidates
                if _is(semantic_owner(c), "Package")
                and declaration_id(semantic_owner(c)) == declaration_id(owner)
            ]
        else:
            candidates = []
        if len(candidates) != 1:
            return None
        return _constant_integer(getattr(candidates[0], "feature_value_expression", None))

    def reading(self, usage: Any, parent: OccurrenceNode | None) -> MultiplicityReading:
        multiplicity = getattr(usage, "multiplicity", None)
        if multiplicity is None:
            return MultiplicityReading.absent()
        ordered = bool(getattr(usage, "is_ordered", False))
        nonunique = bool(getattr(usage, "is_nonunique", False))
        if ordered or nonunique:  # the generator reads no bound in these cases
            return MultiplicityReading(True, ordered, nonunique, None, None, False)
        upper_expr = getattr(multiplicity, "upper_bound", None)
        lower_expr = getattr(multiplicity, "lower_bound", None)
        upper = self._bound(upper_expr, usage, parent) if upper_expr is not None else None
        if upper is None or upper < 0:  # the generator stops before the lower bound
            return MultiplicityReading(True, False, False, upper, None, False)
        lower = self._bound(lower_expr, usage, parent) if lower_expr is not None else None
        return MultiplicityReading(True, False, False, upper, lower, lower_expr is not None)

    def part_usage_readings(self) -> tuple[PartUsageReading, ...]:
        """Every user-model part usage read once with no parent, sorted by usage."""
        readings = [
            PartUsageReading(
                declaration_id(usage),
                bool(getattr(usage, "is_composite", False)),
                self.reading(usage, None),
            )
            for usage in self.usages
        ]
        return tuple(sorted(readings, key=lambda r: str(r.usage_id)))

    def traverse(self, root: Any, namespace_key: UUID) -> None:
        """Visit one root and everything it reaches, into the given occurrence namespace."""
        self.namespace_of_root[declaration_id(root)] = namespace_key
        self._add(root, None, (), declaration_id(root), self.nodes.setdefault(namespace_key, {}))

    def _add(
        self,
        usage: Any,
        parent: OccurrenceNode | None,
        active: tuple[UUID, ...],
        root_id: UUID,
        namespace: dict[tuple[PathStep, ...], OccurrenceNode],
    ) -> None:
        usage_id = declaration_id(usage)
        type_id = self._effective_type(usage)
        if type_id is not None and type_id in active:
            raise _AbortError(
                OccurrenceAbort.RECURSIVE_CONTAINMENT,
                usage,
                f"containment re-enters definition {type_id}",
            )
        closure = self.closures[type_id] if type_id is not None else frozenset()
        children = self._children(usage)
        child_ids = tuple(declaration_id(c) for c in children)
        slot = self.slots.slot_of(usage_id)
        reading = self.reading(usage, parent)
        self.visits.append(UsageVisit(usage_id, parent.path if parent else None, root_id, reading))
        indices = reading.indices
        if indices is None:
            return  # unexpandable: no occurrence here, nothing beneath it is reached
        for index in indices:
            path = (parent.path if parent else ()) + (PathStep(slot, index),)
            node = OccurrenceNode(path, usage_id, type_id, closure, child_ids, root_id)
            existing = namespace.get(path)
            if existing is not None and existing != node:
                raise _AbortError(
                    OccurrenceAbort.DUPLICATE_OCCURRENCE_IDENTITY,
                    usage,
                    "two different occurrences have one exact identity",
                )
            namespace[path] = node
            for child in children:
                self._add(
                    child,
                    node,
                    active + ((type_id,) if type_id is not None else ()),
                    root_id,
                    namespace,
                )

    # ---- attachment and writer selection -----------------------------------------------

    def all_nodes(self) -> list[OccurrenceNode]:
        return [node for namespace in self.nodes.values() for node in namespace.values()]

    def _node_at(self, scope: OccurrenceScope) -> OccurrenceNode:
        return self.nodes[self.namespace_of_root[scope.root_id]][scope.path]

    def _attachment(self, owner: Any) -> tuple[tuple[Scope, ...], AttachmentCause | None]:
        if owner is None:
            return (), AttachmentCause.OWNER_ABSENT
        scopes: tuple[Scope, ...]
        if _is(owner, "PartDefinition"):
            owner_id = declaration_id(owner)
            scopes = tuple(
                OccurrenceScope(n.root_id, n.path)
                for n in self.all_nodes()
                if owner_id in n.type_closure
            )
        elif _is(owner, "PartUsage"):
            slot = self.slots.slot_of(declaration_id(owner))
            scopes = tuple(
                OccurrenceScope(n.root_id, n.path)
                for n in self.all_nodes()
                if n.path[-1].slot == slot
            )
        elif _is(owner, "Package"):
            return (PackageScope(declaration_id(owner)),), None
        else:
            return (), AttachmentCause.OWNER_KIND_UNATTACHABLE
        scopes = tuple(sorted(scopes, key=_scope_order))
        return scopes, None if scopes else AttachmentCause.OWNER_HAS_NO_OCCURRENCES

    def select_writer(self, base: Any, candidates: list[Any], scope: Scope) -> Any:
        if not candidates:
            return base
        node = self._node_at(scope) if isinstance(scope, OccurrenceScope) else None
        usage_writers = [c for c in candidates if _is(semantic_owner(c), "PartUsage")]
        if node is not None:
            exact = [c for c in usage_writers if declaration_id(semantic_owner(c)) == node.usage_id]
            if exact:
                return _one_writer(exact)
        if usage_writers:
            return _one_writer(usage_writers)
        definition_writers = [c for c in candidates if _is(semantic_owner(c), "PartDefinition")]
        if definition_writers:
            owner = _most_specific_definition(
                {declaration_id(semantic_owner(c)) for c in definition_writers},
                self.closures,
                definition_writers[0],
            )
            return _one_writer(
                [c for c in definition_writers if declaration_id(semantic_owner(c)) == owner]
            )
        return _one_writer(candidates)

    def _attachment_of(self, usage: Any, usage_id: UUID) -> Attachment:
        """Where the usage's semantic owner attaches it (`elaborate.py:759-787`)."""
        owner = semantic_owner(usage)
        scopes, cause = self._attachment(owner)
        return Attachment(usage_id, None if owner is None else declaration_id(owner), scopes, cause)

    def constraint_attachments(self) -> tuple[Attachment, ...]:
        """Every constraint usage, subtypes included, as `_build_constraint_nodes` reads them.

        Keyed by SysIDE element ID, as the constraint facts key their usages
        (`subset_extraction.py`), not by `declaration_id`. Codegen takes a constraint usage's
        stable identity in `_index_constraint_associations` (`elaborate.py:592-604`), an
        identity check that refuses the whole model, not an occurrence answer. So an
        anonymous usage (`assert positive;`, no qualified name) still gets its attachment
        here, and the generator's `SI_ID_UNSTABLE` refusal of it stays the generator's. For a
        usage with a qualified name the two IDs are the same value.
        """
        usages = SysideAdapter.elements_of_type(
            self.model, "ConstraintUsage", include_subtypes=True
        )
        attachments = {
            a.usage_id: a
            for a in (self._attachment_of(u, SysideAdapter.element_id(u)) for u in usages)
        }
        return tuple(attachments[k] for k in sorted(attachments, key=str))

    def calc_attachments_and_writers(
        self,
    ) -> tuple[tuple[Attachment, ...], tuple[WriterSelection, ...]]:
        usages = list(SysideAdapter.elements_of_type(self.model, "CalculationUsage"))
        attachments = {
            a.usage_id: a for a in (self._attachment_of(u, declaration_id(u)) for u in usages)
        }
        by_slot: dict[UUID, list[Any]] = defaultdict(list)
        for usage in usages:
            by_slot[self.slots.slot_of(declaration_id(usage))].append(usage)
        selections: list[WriterSelection] = []
        for slot, alternatives in by_slot.items():
            roots = [u for u in alternatives if declaration_id(u) == slot]
            if len(roots) != 1:
                raise _AbortError(
                    OccurrenceAbort.REDEFINITION_ROOT_FAMILY,
                    alternatives[0],
                    f"calculation slot {slot} has {len(roots)} exact root declarations",
                )
            slot_scopes = {s for u in alternatives for s in attachments[declaration_id(u)].scopes}
            for scope in sorted(slot_scopes, key=_scope_order):
                applicable = [
                    u for u in alternatives if scope in attachments[declaration_id(u)].scopes
                ]
                chosen = self.select_writer(roots[0], applicable, scope)
                selections.append(
                    WriterSelection(
                        slot=slot,
                        scope=scope,
                        base_id=declaration_id(roots[0]),
                        selected_id=declaration_id(chosen),
                        applicable_ids=tuple(
                            sorted((declaration_id(a) for a in applicable), key=str)
                        ),
                    )
                )
        return (
            tuple(attachments[k] for k in sorted(attachments, key=str)),
            tuple(sorted(selections, key=lambda w: (_scope_order(w.scope), str(w.slot)))),
        )


#: The namespace key shared by every generator root, as codegen's one occurrence dict.
_GENERATOR = UUID(int=0)


def _str_sorted(ids: Iterable[UUID]) -> list[UUID]:
    return sorted(ids, key=str)


def _node_order(node: OccurrenceNode) -> tuple[str, tuple[tuple[str, int], ...]]:
    return (str(node.root_id), tuple(step.sort_key() for step in node.path))


def _failure(error: _AbortError, stage: BuildStage) -> OccurrenceFailure:
    subject = None if error.element is None else safe_location(error.element)
    return OccurrenceFailure(error.abort, stage, subject, error.detail)


def extract_occurrence_structure(
    model: Any, extra_roots: Iterable[Any] = ()
) -> OccurrenceStructure | OccurrenceFailure:
    """Compute what the generator instantiates, or the abort it would raise instead.

    `extra_roots` are caller-supplied `PartUsage` roots (design D7). One that is already a
    generator root adds nothing; any other is traversed after the generator's roots, and its
    reach is tagged with it. Whether a finding reachable only from one counts is the
    evaluator's decision, not this function's.

    A SysIDE adapter failure (`SemanticEvidenceError`) is not a generator abort and propagates
    to the caller, which records it as a failed fact.
    """
    extra = list(extra_roots)
    for root in extra:
        if not _is(root, "PartUsage"):
            raise TypeError(f"an extra root must be a PartUsage, got {type(root).__name__}")
    try:
        slots = _SlotIndex.build(model)
    except _AbortError as error:
        return _failure(error, BuildStage.SLOTS)
    try:
        builder = _Builder(model, slots)
        generator_ids = {declaration_id(r) for r in builder.generator_roots}
        callers = sorted(
            {declaration_id(r): r for r in extra if declaration_id(r) not in generator_ids}.items(),
            key=lambda item: str(item[0]),
        )
        for root in builder.generator_roots:
            builder.traverse(root, _GENERATOR)
        for caller_id, root in callers:
            builder.traverse(root, caller_id)
        part_usages = builder.part_usage_readings()
    except _AbortError as error:
        return _failure(error, BuildStage.OCCURRENCES)
    try:
        attachments, writers = builder.calc_attachments_and_writers()
        constraint_attachments = builder.constraint_attachments()
    except _AbortError as error:
        return _failure(error, BuildStage.WRITERS)
    return OccurrenceStructure(
        generator_root_ids=tuple(sorted(generator_ids, key=str)),
        caller_root_ids=tuple(_str_sorted(caller_id for caller_id, _root in callers)),
        visits=tuple(builder.visits),
        nodes=tuple(sorted(builder.all_nodes(), key=_node_order)),
        part_definition_ids=tuple(_str_sorted(builder.definitions)),
        part_usages=part_usages,
        calc_attachments=attachments,
        constraint_attachments=constraint_attachments,
        writers=writers,
    )
