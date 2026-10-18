"""Pure occurrence facts: what the pinned generator instantiates, as neutral values.

These are the facts the summary occurrence port (`occurrence_extraction.py`) produces from
SysIDE. They answer, without SysIDE or the generator:

- which part usages are generator roots, and which extra roots a caller asked about;
- every visit of a part usage under a parent occurrence, with its multiplicity reading, so
  counts are per parent occurrence (design review S4);
- every occurrence by its full path (redefinition slot and index at each level);
- which scopes each calculation usage's owner attaches to, and which calculation usage is
  the winning writer in each scope.

Two kinds of failure are kept apart. A multiplicity the generator cannot expand is a fact
(`MultiplicityReading.resolution`), recorded and traversal continues past it, so one
unexpandable usage does not hide the rest. A whole-structure abort the generator would
raise is an :class:`OccurrenceFailure` instead of a structure, carrying one closed
:class:`OccurrenceAbort` member.

Every collection is a tuple in a documented deterministic order. Nothing here imports
SysIDE, `reference_use` or the generator.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from agentic_mbse.sysml.fact_refs import SafeLocation

__all__ = [
    "AttachmentCause",
    "BuildStage",
    "CalcAttachment",
    "MultiplicityReading",
    "MultiplicityResolution",
    "OccurrenceAbort",
    "OccurrenceFailure",
    "OccurrenceNode",
    "OccurrenceScope",
    "OccurrenceStructure",
    "PackageScope",
    "PathStep",
    "Scope",
    "UsageVisit",
    "WriterSelection",
]


class OccurrenceAbort(StrEnum):
    """Why the generator would refuse the whole model while building occurrences.

    Each member names one family of raise sites in sysml-codegen `b5663c07` (paths under
    `src/sysml_codegen/elaboration/`). The generator code each one carries is evidence, not
    vocabulary, and is mapped only in the test suite.
    """

    #: `occurrence.py:651-658`: a part definition specializes itself.
    SPECIALIZATION_CYCLE = "specialization_cycle"
    #: `occurrence.py:972-981`: containment re-enters a definition already on the path.
    RECURSIVE_CONTAINMENT = "recursive_containment"
    #: `occurrence.py:683-690`: a part usage has incomparable user-definition typings.
    INCOMPARABLE_TYPINGS = "incomparable_typings"
    #: `occurrence.py:944-951`: a usage view repeats one declaration as different objects.
    REPEATED_NATIVE_DECLARATION = "repeated_native_declaration"
    #: `occurrence.py:1033-1039`: two different occurrences get one identity.
    DUPLICATE_OCCURRENCE_IDENTITY = "duplicate_occurrence_identity"
    #: `occurrence.py:385-417` (missing or unstable redefinition endpoint), `:296-341` (family
    #: cycle, unrelated roots), and `elaborate.py:1209-1222` (a calculation slot without
    #: exactly one root declaration).
    REDEFINITION_ROOT_FAMILY = "redefinition_root_family"
    #: `occurrence.py:249-285`: the candidates for one slot have no unique effective
    #: declaration, or span slots.
    EFFECTIVE_DECLARATION_AMBIGUOUS = "effective_declaration_ambiguous"
    #: `occurrence.py:347-371` (no unique most-specific definition writer, reached from
    #: `:740-756` and `elaborate.py:926-939`) and `elaborate.py:943-953` (incomparable writers).
    WRITER_AMBIGUOUS = "writer_ambiguous"
    #: `identity.py:66-80`: a declaration has no qualified name or a non-UUIDv5 identity.
    IDENTITY_UNSTABLE = "identity_unstable"


class BuildStage(StrEnum):
    """Which build step aborted, in the generator's order."""

    #: `build_feature_slot_index` (`occurrence.py:374-431`).
    SLOTS = "slots"
    #: `build_occurrence_index` (`occurrence.py:902-1053`).
    OCCURRENCES = "occurrences"
    #: Calculation attachment and writer selection (`elaborate.py:1195-1233`).
    WRITERS = "writers"


class MultiplicityResolution(StrEnum):
    """How the generator resolves one usage's multiplicity under one parent.

    `ABSENT` and `EXACT` expand. Every other member is the first failing check in the
    generator's order (`occurrence.py:812-899`), and the usage then has no occurrence there.
    """

    ABSENT = "absent"
    EXACT = "exact"
    ORDERED = "ordered"
    NONUNIQUE = "nonunique"
    UNRESOLVED_UPPER = "unresolved_upper"
    NEGATIVE = "negative"
    UNRESOLVED_LOWER = "unresolved_lower"
    RANGE = "range"


@dataclass(frozen=True)
class MultiplicityReading:
    """What the generator read from one usage's multiplicity under one parent.

    The fields hold only what the generator reads before it stops: no bound is read for an
    ordered or nonunique usage, and no lower bound once the upper bound fails.
    """

    present: bool
    ordered: bool
    nonunique: bool
    upper: int | None
    lower: int | None
    lower_present: bool

    def __post_init__(self) -> None:
        if not self.present and (
            self.ordered or self.nonunique or self.upper is not None or self.lower_present
        ):
            raise ValueError("an absent multiplicity has no flags or bounds")
        if (self.ordered or self.nonunique) and (self.upper is not None or self.lower_present):
            raise ValueError("no bound is read for an ordered or nonunique multiplicity")
        if (self.upper is None or self.upper < 0) and self.lower_present:
            raise ValueError("no lower bound is read once the upper bound fails")
        if not self.lower_present and self.lower is not None:
            raise ValueError("a lower bound value needs a present lower bound")

    @classmethod
    def absent(cls) -> MultiplicityReading:
        return cls(False, False, False, None, None, False)

    @property
    def resolution(self) -> MultiplicityResolution:
        if not self.present:
            return MultiplicityResolution.ABSENT
        if self.ordered:
            return MultiplicityResolution.ORDERED
        if self.nonunique:
            return MultiplicityResolution.NONUNIQUE
        if self.upper is None:
            return MultiplicityResolution.UNRESOLVED_UPPER
        if self.upper < 0:
            return MultiplicityResolution.NEGATIVE
        if self.lower_present and self.lower is None:
            return MultiplicityResolution.UNRESOLVED_LOWER
        if self.lower_present and self.lower != self.upper:
            return MultiplicityResolution.RANGE
        return MultiplicityResolution.EXACT

    @property
    def indices(self) -> tuple[int | None, ...] | None:
        """The occurrence indices the generator expands, or ``None`` if it cannot expand."""
        resolution = self.resolution
        if resolution is MultiplicityResolution.ABSENT:
            return (None,)
        if resolution is MultiplicityResolution.EXACT:
            assert self.upper is not None
            return tuple(range(self.upper))
        return None


@dataclass(frozen=True, order=True)
class PathStep:
    """One level of an occurrence path: the redefinition slot and the index within it."""

    slot: UUID
    index: int | None

    def __post_init__(self) -> None:
        if self.index is not None and self.index < 0:
            raise ValueError(f"occurrence index must be non-negative, got {self.index}")

    def sort_key(self) -> tuple[str, int]:
        return (str(self.slot), -1 if self.index is None else self.index)


def _path_key(path: tuple[PathStep, ...]) -> tuple[tuple[str, int], ...]:
    return tuple(step.sort_key() for step in path)


@dataclass(frozen=True)
class UsageVisit:
    """One visit of a part usage under one parent occurrence (``None`` for a root).

    `root_id` is the root whose traversal made the visit. Visits are kept in the generator's
    traversal order, which decides which unexpandable multiplicity it reports first.
    """

    usage_id: UUID
    parent: tuple[PathStep, ...] | None
    root_id: UUID
    reading: MultiplicityReading

    def __post_init__(self) -> None:
        if self.parent == ():
            raise ValueError("a root visit has parent None, not an empty path")

    @property
    def count(self) -> int | None:
        """Occurrences this visit produces, or ``None`` when the generator cannot expand it."""
        indices = self.reading.indices
        return None if indices is None else len(indices)


@dataclass(frozen=True)
class OccurrenceNode:
    """One occurrence the generator instantiates."""

    path: tuple[PathStep, ...]
    usage_id: UUID
    type_id: UUID | None
    type_closure: frozenset[UUID]
    child_ids: tuple[UUID, ...]
    root_id: UUID

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("an occurrence path has at least one step")
        if (self.type_id is None) != (not self.type_closure):
            raise ValueError("a typed occurrence has a non-empty closure, an untyped one none")
        if self.type_id is not None and self.type_id not in self.type_closure:
            raise ValueError("an occurrence's type closure contains its own type")
        if list(self.child_ids) != sorted(self.child_ids, key=str):
            raise ValueError("child declarations are in UUID string order")

    @property
    def parent(self) -> tuple[PathStep, ...] | None:
        return self.path[:-1] or None


@dataclass(frozen=True, order=True)
class OccurrenceScope:
    """An attachment scope that is one occurrence, reached from `root_id`."""

    root_id: UUID
    path: tuple[PathStep, ...]

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("an occurrence scope has a non-empty path")


@dataclass(frozen=True, order=True)
class PackageScope:
    """The one attachment scope a package owner always gets."""

    package_id: UUID


Scope = OccurrenceScope | PackageScope


def _scope_key(scope: Scope) -> tuple[int, str, tuple[tuple[str, int], ...]]:
    if isinstance(scope, PackageScope):
        return (0, str(scope.package_id), ())
    return (1, str(scope.root_id), _path_key(scope.path))


class AttachmentCause(StrEnum):
    """Why an owner attaches to no scope (`elaborate.py:759-787`)."""

    OWNER_ABSENT = "owner_absent"
    OWNER_KIND_UNATTACHABLE = "owner_kind_unattachable"
    OWNER_HAS_NO_OCCURRENCES = "owner_has_no_occurrences"


@dataclass(frozen=True)
class CalcAttachment:
    """The scopes one calculation usage's semantic owner attaches to, or why there are none."""

    usage_id: UUID
    owner_id: UUID | None
    scopes: tuple[Scope, ...]
    cause: AttachmentCause | None

    def __post_init__(self) -> None:
        if (self.cause is None) == (not self.scopes):
            raise ValueError("an attachment has scopes or a cause, never both or neither")
        if (self.owner_id is None) != (self.cause is AttachmentCause.OWNER_ABSENT):
            raise ValueError("only an absent owner has no owner id")
        if list(self.scopes) != sorted(self.scopes, key=_scope_key):
            raise ValueError("attachment scopes are in scope order")


@dataclass(frozen=True)
class WriterSelection:
    """The calculation usage the generator classifies in one scope of one redefinition slot.

    `base_id` is the slot's root declaration, `applicable_ids` every alternative attached to
    the scope (never empty, because scopes are the union of the alternatives' attachments),
    and `selected_id` the winning writer among them (`elaborate.py:901-952`).
    """

    slot: UUID
    scope: Scope
    base_id: UUID
    selected_id: UUID
    applicable_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        if self.selected_id not in self.applicable_ids:
            raise ValueError("the selected writer is one of the scope's applicable alternatives")
        if list(self.applicable_ids) != sorted(self.applicable_ids, key=str):
            raise ValueError("applicable writers are in UUID string order")


@dataclass(frozen=True)
class OccurrenceStructure:
    """Everything the summary port reads about instantiation, in deterministic order.

    - `generator_root_ids`: the generator's roots (`occurrence.py:916-923`), sorted.
    - `caller_root_ids`: extra roots a caller asked about that are not generator roots
      (design D7), sorted. Their reach is computed with the same rules and tagged by root.
    - `visits`: generator traversal order (generator roots, then caller roots).
    - `nodes`: sorted by (root, path).
    - `part_definition_ids`: every user-model part definition, sorted.
    - `calc_attachments`: one per calculation usage, sorted by usage.
    - `writers`: sorted by (scope, slot).
    """

    generator_root_ids: tuple[UUID, ...]
    caller_root_ids: tuple[UUID, ...]
    visits: tuple[UsageVisit, ...]
    nodes: tuple[OccurrenceNode, ...]
    part_definition_ids: tuple[UUID, ...]
    calc_attachments: tuple[CalcAttachment, ...]
    writers: tuple[WriterSelection, ...]

    def __post_init__(self) -> None:
        for name, values in (
            ("generator_root_ids", self.generator_root_ids),
            ("caller_root_ids", self.caller_root_ids),
            ("part_definition_ids", self.part_definition_ids),
        ):
            if list(values) != sorted(set(values), key=str):
                raise ValueError(f"{name} are unique and in UUID string order")
        if set(self.generator_root_ids) & set(self.caller_root_ids):
            raise ValueError("a caller root is never also a generator root")
        roots = set(self.generator_root_ids) | set(self.caller_root_ids)
        if any(v.root_id not in roots for v in self.visits) or any(
            n.root_id not in roots for n in self.nodes
        ):
            raise ValueError("every visit and node is reached from a listed root")
        keys = [(str(n.root_id), _path_key(n.path)) for n in self.nodes]
        if keys != sorted(set(keys)):
            raise ValueError("nodes are unique and in (root, path) order")
        usages = [a.usage_id for a in self.calc_attachments]
        if usages != sorted(set(usages), key=str):
            raise ValueError("calc attachments are unique and in usage order")
        writer_keys = [(_scope_key(w.scope), str(w.slot)) for w in self.writers]
        if writer_keys != sorted(set(writer_keys)):
            raise ValueError("writer selections are unique and in (scope, slot) order")

    def is_generator_root(self, root_id: UUID) -> bool:
        return root_id in self.generator_root_ids

    def occurrence_counts(self) -> dict[UUID, int]:
        """Occurrences per effective usage, over every root."""
        return dict(Counter(node.usage_id for node in self.nodes))

    def definition_occurrence_count(self, definition_id: UUID) -> int:
        """Occurrences whose type closure includes the definition (`occurrence.py:505-508`)."""
        return sum(1 for node in self.nodes if definition_id in node.type_closure)

    def selected_scopes(self, usage_id: UUID) -> tuple[Scope, ...]:
        """The scopes in which this calculation usage is the winning writer."""
        return tuple(w.scope for w in self.writers if w.selected_id == usage_id)

    def overridden_scopes(self, usage_id: UUID) -> tuple[Scope, ...]:
        """The scopes this usage attaches to in which another writer wins (Implementation Note (a))."""
        return tuple(
            w.scope
            for w in self.writers
            if w.selected_id != usage_id and usage_id in w.applicable_ids
        )


@dataclass(frozen=True)
class OccurrenceFailure:
    """The generator would refuse the whole model here; no structure exists."""

    abort: OccurrenceAbort
    stage: BuildStage
    subject: SafeLocation | None
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.abort, OccurrenceAbort):
            raise TypeError(f"abort must be an OccurrenceAbort, got {self.abort!r}")
        if not isinstance(self.stage, BuildStage):
            raise TypeError(f"stage must be a BuildStage, got {self.stage!r}")
