"""Spike port of sysml-codegen b5663c07 occurrence reach and calc-usage writer selection.

Imports only agentic_mbse and SysIDE (through agentic_mbse). Never raises a generator code:
multiplicity outcomes are neutral resolution classes on the node, and the invariant failures
codegen raises (redefinition family, recursion, identity, writer ambiguity) become a
`FactFailure` the caller can read. Mirrors, function by function:

  semantic_owner, declaration_id_for            occurrence.py:116, identity.py:66
  FeatureSlotIndex (+ build_feature_slot_index) occurrence.py:222-344, 374-431
  _most_specific_definition                     occurrence.py:347-371
  _definition_supertypes, _effective_type       occurrence.py:635-691
  _modeled_integer_bound, _constant_integer_value occurrence.py:694-788
  _multiplicity_indices                         occurrence.py:812-899
  build_occurrence_index (roots, native children, add_usage) occurrence.py:902-1046
  occurrences_for_type / _for_declaration       occurrence.py:495-508
  _ExactElaborator._attachment                  elaborate.py:759-787
  _ExactElaborator._select_writer / _require_one_writer elaborate.py:901-952
  _build_calculation_nodes (selection half)     elaborate.py:1195-1233
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter

is_a = SysideAdapter.is_instance


class FactFailure(Exception):
    """A whole-structure failure: codegen would raise an invariant error here."""

    def __init__(self, cause: str, detail: str) -> None:
        super().__init__(f"{cause}: {detail}")
        self.cause = cause
        self.detail = detail


def qn(element: Any) -> str | None:
    value = getattr(element, "qualified_name", None)
    return None if value is None else str(value)


def semantic_owner(element: Any) -> Any:
    owning_type = getattr(element, "owning_type", None)
    return owning_type if owning_type is not None else getattr(element, "owner", None)


def decl(element: Any) -> UUID:
    if qn(element) is None:
        raise FactFailure("id_unstable", f"{type(element).__name__} has no qualified name")
    raw = SysideAdapter.element_id(element)
    if raw.version != 5:
        raise FactFailure("id_unstable", f"{type(element).__name__} id {raw} is not UUIDv5")
    return raw


# ---- redefinition slots ---------------------------------------------------------------


class SlotIndex:
    """Feature declaration -> root of its parser redefinition family."""

    def __init__(self, model: Any) -> None:
        self.declarations: set[UUID] = set()
        self.parents: dict[UUID, set[UUID]] = defaultdict(set)
        self._roots: dict[UUID, UUID] = {}
        features = list(SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True))
        for feature in features:
            if qn(feature) is not None:
                self.declarations.add(decl(feature))
        for feature in features:
            if qn(feature) is None:
                continue
            for relationship in getattr(feature, "owned_redefinitions", ()) or ():
                redefined = getattr(relationship, "redefined_feature", None)
                redefining = getattr(relationship, "redefining_feature", None)
                if redefined is None or redefining is None:
                    raise FactFailure("redefinition_invalid", f"missing endpoint on {qn(feature)}")
                chain = list(getattr(redefined, "chaining_features", ()) or ())
                endpoint = chain[-1] if chain else redefined
                if qn(endpoint) is None or qn(redefining) is None:
                    raise FactFailure("redefinition_invalid", f"unstable endpoint on {qn(feature)}")
                self.declarations.update((decl(endpoint), decl(redefining)))
                self.parents[decl(redefining)].add(decl(endpoint))
        for declaration in self.declarations:
            self.slot_of(declaration)

    def slot_of(self, declaration: UUID) -> UUID:
        if declaration not in self.declarations:
            raise KeyError(declaration)
        return self._root_of(declaration, ())

    def _root_of(self, declaration: UUID, active: tuple[UUID, ...]) -> UUID:
        if declaration in self._roots:
            return self._roots[declaration]
        if declaration in active:
            raise FactFailure("redefinition_invalid", f"cycle at {declaration}")
        parents = self.parents.get(declaration, set())
        if not parents:
            root = declaration
        else:
            roots = {self._root_of(parent, active + (declaration,)) for parent in parents}
            if len(roots) != 1:
                raise FactFailure("redefinition_invalid", f"{declaration} has unrelated roots")
            root = min(roots)
        self._roots[declaration] = root
        return root

    def _redefines(self, declaration: UUID, ancestor: UUID, active: tuple[UUID, ...]) -> bool:
        if declaration in active:
            raise FactFailure("redefinition_invalid", f"cycle at {declaration}")
        parents = self.parents.get(declaration, set())
        return ancestor in parents or any(
            self._redefines(parent, ancestor, active + (declaration,)) for parent in parents
        )

    def effective_declaration(self, candidates: set[UUID]) -> UUID:
        if not candidates or len({self.slot_of(c) for c in candidates}) != 1:
            raise FactFailure("redefinition_invalid", "candidates span slots or are empty")
        winners = {
            c for c in candidates
            if all(o == c or self._redefines(c, o, ()) for o in candidates)
        }
        if len(winners) != 1:
            raise FactFailure("redefinition_invalid", "no unique effective declaration")
        return next(iter(winners))


def most_specific_definition(candidates: set[UUID], closures: dict[UUID, frozenset[UUID]]) -> UUID:
    winners = {
        c for c in candidates if all(o == c or o in closures[c] for o in candidates)
    }
    if len(winners) != 1:
        raise FactFailure("redefinition_invalid", "no unique most-specific definition")
    return min(winners)


# ---- multiplicity -------------------------------------------------------------------


@dataclass(frozen=True)
class MultiplicityReading:
    """Neutral reading. `resolution` is codegen's first failing check, in its order."""

    present: bool
    ordered: bool = False
    nonunique: bool = False
    upper: int | None = None
    lower: int | None = None
    lower_present: bool = False

    @property
    def resolution(self) -> str:
        if not self.present:
            return "absent"
        if self.ordered:
            return "ordered"
        if self.nonunique:
            return "nonunique"
        if self.upper is None:
            return "unresolved_upper"
        if self.upper < 0:
            return "negative"
        if self.lower_present and self.lower is None:
            return "unresolved_lower"
        if self.lower_present and self.lower != self.upper:
            return "range"
        return "exact"


def constant_integer(expression: Any) -> int | None:
    if expression is None:
        return None
    try:
        value = evaluate_true_static_expression(expression)
    except (ArithmeticError, TypeError, ValueError):
        return None
    if not math.isfinite(value) or not value.is_integer():
        return None
    return int(value)


@dataclass
class Node:
    path: tuple[tuple[UUID, int | None], ...]
    usage: UUID
    type_id: UUID | None
    closure: frozenset[UUID]
    parent: Node | None
    children: tuple[UUID, ...]


class OccurrenceStructure:
    def __init__(self, model: Any) -> None:
        self.model = model
        self.slots = SlotIndex(model)
        self.definitions = {decl(d): d for d in SysideAdapter.elements_of_type(model, "PartDefinition")}
        self.closures = self._supertypes()
        usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
        self.usage_ids = {decl(usage) for usage in usages}
        self.attributes_by_slot: dict[UUID, list[Any]] = defaultdict(list)
        for attribute in SysideAdapter.elements_of_type(model, "AttributeUsage"):
            if qn(attribute) is not None:
                self.attributes_by_slot[self.slots.slot_of(decl(attribute))].append(attribute)
        self.roots = [
            usage for usage in usages
            if not (is_a(semantic_owner(usage), "PartDefinition") or is_a(semantic_owner(usage), "PartUsage"))
        ]
        self.nodes: dict[tuple, Node] = {}
        self.visits: list[tuple[UUID, Node | None, MultiplicityReading]] = []
        for root in sorted(self.roots, key=lambda r: str(decl(r))):
            self._add(root, None, ())

    def _supertypes(self) -> dict[UUID, frozenset[UUID]]:
        direct: dict[UUID, set[UUID]] = defaultdict(set)
        for definition_id, definition in self.definitions.items():
            for specialization in getattr(definition, "owned_specializations", ()) or ():
                supertype = getattr(specialization, "superclassifier", None)
                if supertype is not None and qn(supertype) is not None and decl(supertype) in self.definitions:
                    direct[definition_id].add(decl(supertype))

        def closure(definition_id: UUID, active: tuple[UUID, ...]) -> frozenset[UUID]:
            if definition_id in active:
                raise FactFailure("containment_recursive", f"specialization cycle at {definition_id}")
            result = {definition_id}
            for parent in direct.get(definition_id, set()):
                result |= closure(parent, active + (definition_id,))
            return frozenset(result)

        return {d: closure(d, ()) for d in self.definitions}

    def _effective_type(self, usage: Any) -> UUID | None:
        candidates = {
            decl(t) for t in (getattr(usage, "types", None) or ())
            if qn(t) is not None and decl(t) in self.definitions
        }
        specific = {c for c in candidates if not any(c != o and c in self.closures[o] for o in candidates)}
        if len(specific) > 1:
            raise FactFailure("redefinition_invalid", f"incomparable typings on {qn(usage)}")
        return min(specific, default=None)

    def _children(self, usage: Any) -> tuple[Any, ...]:
        native: dict[UUID, Any] = {}
        for candidate in getattr(usage, "usages", ()) or ():
            if not is_a(candidate, "PartUsage") or not bool(getattr(candidate, "is_composite", False)):
                continue
            if qn(candidate) is None or decl(candidate) not in self.usage_ids:
                continue
            existing = native.get(decl(candidate))
            if existing is not None and existing is not candidate:
                raise FactFailure("redefinition_invalid", f"usage view repeats {qn(candidate)}")
            native[decl(candidate)] = candidate
        by_slot: dict[UUID, set[UUID]] = defaultdict(set)
        for candidate_id in native:
            by_slot[self.slots.slot_of(candidate_id)].add(candidate_id)
        selected = {self.slots.effective_declaration(c) for c in by_slot.values()}
        return tuple(native[i] for i in sorted(selected, key=str))

    def _bound(self, bound: Any, usage: Any, parent: Node | None) -> int | None:
        direct = constant_integer(bound)
        if direct is not None:
            return direct
        if not is_a(bound, "FeatureReferenceExpression"):
            return None
        referent = getattr(bound, "referent", None)
        if referent is None or qn(referent) is None:
            return None
        try:
            slot = self.slots.slot_of(decl(referent))
        except KeyError:
            return None
        candidates = self.attributes_by_slot.get(slot, [])
        owner = semantic_owner(usage)
        if is_a(owner, "PartUsage"):
            candidates = [
                c for c in candidates
                if is_a(semantic_owner(c), "PartUsage") and decl(semantic_owner(c)) == decl(owner)
            ]
        elif is_a(owner, "PartDefinition") and parent is not None:
            writers = [
                c for c in candidates
                if is_a(semantic_owner(c), "PartDefinition") and decl(semantic_owner(c)) in parent.closure
            ]
            if writers:
                chosen = most_specific_definition({decl(semantic_owner(c)) for c in writers}, self.closures)
                candidates = [c for c in writers if decl(semantic_owner(c)) == chosen]
            else:
                candidates = []
        elif is_a(owner, "Package"):
            candidates = [
                c for c in candidates
                if is_a(semantic_owner(c), "Package") and decl(semantic_owner(c)) == decl(owner)
            ]
        else:
            candidates = []
        if len(candidates) != 1:
            return None
        return constant_integer(getattr(candidates[0], "feature_value_expression", None))

    def reading(self, usage: Any, parent: Node | None) -> MultiplicityReading:
        multiplicity = getattr(usage, "multiplicity", None)
        if multiplicity is None:
            return MultiplicityReading(present=False)
        ordered = bool(getattr(usage, "is_ordered", False))
        nonunique = bool(getattr(usage, "is_nonunique", False))
        if ordered or nonunique:  # codegen reads no bound in these cases
            return MultiplicityReading(True, ordered, nonunique)
        upper_expr = getattr(multiplicity, "upper_bound", None)
        lower_expr = getattr(multiplicity, "lower_bound", None)
        upper = self._bound(upper_expr, usage, parent) if upper_expr is not None else None
        if upper is None or upper < 0:  # codegen stops before reading the lower bound
            return MultiplicityReading(True, upper=upper)
        lower = self._bound(lower_expr, usage, parent) if lower_expr is not None else None
        return MultiplicityReading(True, upper=upper, lower=lower, lower_present=lower_expr is not None)

    def _add(self, usage: Any, parent: Node | None, active: tuple[UUID, ...]) -> None:
        usage_id = decl(usage)
        type_id = self._effective_type(usage)
        if type_id is not None and type_id in active:
            raise FactFailure("containment_recursive", f"re-enters {type_id} at {qn(usage)}")
        closure = self.closures[type_id] if type_id is not None else frozenset()
        children = self._children(usage)
        slot = self.slots.slot_of(usage_id)
        reading = self.reading(usage, parent)
        self.visits.append((usage_id, parent, reading))
        if reading.resolution == "absent":
            indices: tuple[int | None, ...] = (None,)
        elif reading.resolution == "exact":
            indices = tuple(range(reading.upper or 0))
        else:
            return  # unexpandable: no occurrence, nothing beneath it is reached
        for index in indices:
            path = (parent.path if parent else ()) + ((slot, index),)
            node = Node(path, usage_id, type_id, closure, parent, tuple(decl(c) for c in children))
            if path in self.nodes:
                raise FactFailure("redefinition_invalid", f"duplicate occurrence {path}")
            self.nodes[path] = node
            for child in children:
                self._add(child, node, active + ((type_id,) if type_id is not None else ()))

    # ---- attachment and writer selection ----------------------------------------------

    def attachment(self, owner: Any) -> tuple[tuple[Any, ...], str | None]:
        """Scopes are node paths, or ("pkg", uuid) for a package scope."""
        if owner is None:
            return (), "owner_absent"
        if is_a(owner, "PartDefinition"):
            scopes = tuple(p for p, n in sorted(self.nodes.items(), key=_key) if decl(owner) in n.closure)
            return scopes, None if scopes else "owner_has_no_occurrences"
        if is_a(owner, "PartUsage"):
            slot = self.slots.slot_of(decl(owner))
            scopes = tuple(p for p in sorted(self.nodes, key=_pkey) if p[-1][0] == slot)
            return scopes, None if scopes else "owner_has_no_occurrences"
        if is_a(owner, "Package"):
            return (("pkg", decl(owner)),), None
        return (), "owner_kind_unattachable"

    def select_writer(self, base: Any, candidates: list[Any], scope: Any) -> Any:
        if not candidates:
            return base
        node = self.nodes.get(scope) if not _is_pkg(scope) else None
        usage_writers = [c for c in candidates if is_a(semantic_owner(c), "PartUsage")]
        if node is not None:
            exact = [c for c in usage_writers if decl(semantic_owner(c)) == node.usage]
            if exact:
                return _one(exact)
        if usage_writers:
            return _one(usage_writers)
        definition_writers = [c for c in candidates if is_a(semantic_owner(c), "PartDefinition")]
        if definition_writers:
            owner = most_specific_definition({decl(semantic_owner(c)) for c in definition_writers}, self.closures)
            return _one([c for c in definition_writers if decl(semantic_owner(c)) == owner])
        return _one(candidates)

    def calc_writers(self) -> list[tuple[Any, UUID, UUID, list[UUID]]]:
        """(scope, slot base usage, selected usage, applicable usages) per scope."""
        usages = list(SysideAdapter.elements_of_type(self.model, "CalculationUsage"))
        scopes_by = {decl(u): self.attachment(semantic_owner(u))[0] for u in usages}
        by_slot: dict[UUID, list[Any]] = defaultdict(list)
        for usage in usages:
            by_slot[self.slots.slot_of(decl(usage))].append(usage)
        result = []
        for slot, alternatives in by_slot.items():
            roots = [u for u in alternatives if decl(u) == slot]
            if len(roots) != 1:
                raise FactFailure("redefinition_invalid", f"calc slot {slot} has {len(roots)} roots")
            scopes = {s for u in alternatives for s in scopes_by[decl(u)]}
            for scope in scopes:
                applicable = [u for u in alternatives if scope in scopes_by[decl(u)]]
                chosen = self.select_writer(roots[0], applicable, scope)
                result.append((scope, decl(roots[0]), decl(chosen), [decl(a) for a in applicable]))
        return result


def _one(candidates: list[Any]) -> Any:
    if len(candidates) != 1:
        raise FactFailure("redefinition_invalid", "incomparable value writers")
    return candidates[0]


def _is_pkg(scope: Any) -> bool:
    return isinstance(scope, tuple) and len(scope) == 2 and scope[0] == "pkg"


def _pkey(path: tuple) -> str:
    return "/".join(f"{slot}[{'' if index is None else index}]" for slot, index in path)


def _key(item: tuple) -> str:
    return _pkey(item[0])
