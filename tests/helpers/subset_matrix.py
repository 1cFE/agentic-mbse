"""Load the capability/refusal matrix (`tests/fixtures/subset_profile/inventory/matrix.toml`).

The matrix places every case the spec names (ES-001 to ES-012, self-binding, indexed and
deep-qualified references, the ten PUSH-DOWN profile rows, L6-LIBRARY-ALIAS-SOURCE, G1/G2 and
the gaps Item 1's probes found), gives each exactly one class and an owner, and cross-references
the dc3 blockers (T-001 B1-B9) and upstream findings (U1-U7). Shared-rule rows join the packaged
rule records; the join itself is asserted in `tests/test_subset_matrix.py`.

Pure and stdlib-only, so the renderer (`scripts/subset_profile/render_matrix.py`) and the tests
read one copy of the schema. Every closed field is validated here; a bad matrix raises
`MatrixError` at load.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, TypeVar

import tomllib

MATRIX_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "subset_profile"
    / "inventory"
    / "matrix.toml"
)


_E = TypeVar("_E", bound=StrEnum)


class MatrixError(ValueError):
    """The matrix breaks its schema."""


class RowClass(StrEnum):
    SHARED_RULE = "shared_rule"
    CODEGEN_CHECK = "codegen_check"
    ADVISORY_OMISSION_POLICY = "advisory_omission_policy"
    TRACKED_GAP = "tracked_gap"
    INTERNAL_INVARIANT = "internal_invariant"


class RowOutcome(StrEnum):
    """What the pinned generator does with the row's shape, as far as the evidence shows."""

    REFUSED = "refused"
    ADMITTED = "admitted"
    EXCLUDED = "excluded"
    OMITTED = "omitted"
    UNCONFIRMED = "unconfirmed"


class RowEvidence(StrEnum):
    #: The three rule-record statuses; a shared-rule row carries its rule's status.
    PROBE_OBSERVED = "probe_observed"
    PARTIAL = "partial"
    CODE_READ_PENDING_ITEM_2 = "code_read_pending_item_2"
    #: A certified `reproduction` probe of a candidate family (no record cites it).
    REPRODUCTION_PROBE = "reproduction_probe"
    #: A certified `control` probe: the generator runs the shape and no rule recognizes it.
    CONTROL_PROBE = "control_probe"
    #: Seen in the generated output of certified `record` probes taken for another rule.
    OBSERVED_IN_RECORD_PROBES = "observed_in_record_probes"
    #: A record of the generator's owner-accepted corpus (`v6_recapture_batch/batch.json`).
    CORPUS_RECORD = "corpus_record"
    #: Read from code or a backlog row; no run of the pinned generator observed it in Item 1.
    CODE_READ = "code_read"
    #: Reported by a dc3 worker and not reproduced.
    REPORTED_NOT_REPRODUCED = "reported_not_reproduced"


RULE_STATUSES = frozenset(
    {RowEvidence.PROBE_OBSERVED, RowEvidence.PARTIAL, RowEvidence.CODE_READ_PENDING_ITEM_2}
)
DC3_ITEMS = frozenset(f"B{n}" for n in range(1, 10))
UPSTREAM_ITEMS = frozenset(f"U{n}" for n in range(1, 8))
BINDING_KINDS = ("literal", "single_reference", "self_binding", "indexed", "other_expression")

#: `probe:<id>`, `corpus:<fixture>`, `backlog:<agentic-mbse row>`, `dc3:<path>`, `doc:<path>`, or a
#: code citation `sysml_codegen/...py:<line>` (at the pin) / `agentic_mbse/...py:<line>`.
_EVIDENCE_REF = re.compile(
    r"(probe|corpus|backlog|dc3|doc):[A-Za-z0-9_./#-]+"
    r"|(sysml_codegen|agentic_mbse)/[a-z0-9_/]+\.py:\d+(-\d+)?"
)

_ROW_REQUIRED = {
    "id",
    "title",
    "class",
    "contexts",
    "outcome",
    "evidence_status",
    "evidence",
    "owner",
    "coverage_limitation",
    "sites",
    "no_raise_site",
    "dc3",
    "upstream",
}
_ROW_OPTIONAL = {"rule", "shapes", "l2_relation", "statement", "split"}


@dataclass(frozen=True)
class OutcomeSplit:
    """One of several distinct generator outcomes a row's dc3 item carries (B8)."""

    label: str
    count: int
    outcome: RowOutcome
    shape: str


@dataclass(frozen=True)
class MatrixRow:
    row_id: str
    title: str
    cls: RowClass
    #: The rule record, iff the class is `shared_rule`.
    rule: str | None
    #: The rule's shapes this row covers; empty unless `shared_rule`.
    shapes: tuple[str, ...]
    #: For a shared rule, the record contexts with `outcome`; otherwise where the outcome holds,
    #: in words.
    contexts: tuple[str, ...]
    outcome: RowOutcome
    evidence_status: RowEvidence
    #: Evidence references (see `_EVIDENCE_REF`).
    evidence: tuple[str, ...]
    owner: str
    #: What stays uncovered; empty only for a shared rule implemented in Item 1.
    coverage_limitation: str
    #: Site-account IDs (filled from `site_account.csv`).
    sites: tuple[str, ...]
    #: True when the case has no raise site at all (a silent omission or admission).
    no_raise_site: bool
    dc3: tuple[str, ...]
    upstream: tuple[str, ...]
    l2_relation: str
    statement: str
    split: tuple[OutcomeSplit, ...]

    def probe_ids(self) -> tuple[str, ...]:
        return tuple(e.removeprefix("probe:") for e in self.evidence if e.startswith("probe:"))


@dataclass(frozen=True)
class ClassifierPlacement:
    """Where one outcome of the generator's binding-source classifier lives in the matrix."""

    kind: str
    row: str
    outcome: RowOutcome
    #: The generator code a refusal of this kind carries; empty when admitted.
    code: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class Pointer:
    """A finding the matrix deliberately does not classify, and where it belongs."""

    finding: str
    destination: str
    reason: str


class Matrix(Mapping[str, MatrixRow]):
    def __init__(
        self,
        rows: tuple[MatrixRow, ...],
        classifier: tuple[ClassifierPlacement, ...],
        pointers: tuple[Pointer, ...],
    ) -> None:
        self._rows = {r.row_id: r for r in rows}
        self.order = tuple(r.row_id for r in rows)
        self.classifier = classifier
        self.pointers = pointers

    def __getitem__(self, key: str) -> MatrixRow:
        return self._rows[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.order)

    def __len__(self) -> int:
        return len(self._rows)

    def by_dc3(self, item: str) -> set[str]:
        return {r.row_id for r in self._rows.values() if item in r.dc3}

    def by_upstream(self, item: str) -> set[str]:
        return {r.row_id for r in self._rows.values() if item in r.upstream}


def _keys(table: Mapping[str, Any], required: set[str], optional: set[str], where: str) -> None:
    missing = required - table.keys()
    unknown = table.keys() - required - optional
    if missing or unknown:
        raise MatrixError(f"{where}: missing {sorted(missing)}, unknown {sorted(unknown)}")


def _text(value: Any, where: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise MatrixError(f"{where}: expected a non-empty string, got {value!r}")
    return value


def _texts(value: Any, where: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise MatrixError(f"{where}: expected a list, got {value!r}")
    items = tuple(_text(v, where) for v in value)
    if len(set(items)) != len(items):
        raise MatrixError(f"{where}: duplicate entries in {items}")
    return items


def _member(enum: type[_E], value: Any, where: str) -> _E:
    try:
        return enum(value)
    except ValueError as exc:
        raise MatrixError(f"{where}: {value!r} is not a {enum.__name__}") from exc


def _split(table: Mapping[str, Any], where: str) -> OutcomeSplit:
    _keys(table, {"label", "count", "outcome", "shape"}, set(), where)
    count = table["count"]
    if not isinstance(count, int) or count < 1:
        raise MatrixError(f"{where}: count must be a positive integer")
    return OutcomeSplit(
        label=_text(table["label"], where),
        count=count,
        outcome=_member(RowOutcome, table["outcome"], where),
        shape=_text(table["shape"], where),
    )


def _row(table: Mapping[str, Any]) -> MatrixRow:
    where = f"row {table.get('id', '?')!r}"
    _keys(table, _ROW_REQUIRED, _ROW_OPTIONAL, where)
    cls = _member(RowClass, table["class"], where)
    shared = cls is RowClass.SHARED_RULE
    if shared != ("rule" in table) or shared != ("shapes" in table):
        raise MatrixError(f"{where}: `rule` and `shapes` are required iff class is shared_rule")
    evidence_status = _member(RowEvidence, table["evidence_status"], where)
    if shared != (evidence_status in RULE_STATUSES):
        raise MatrixError(f"{where}: a rule status belongs to shared-rule rows only")
    evidence = _texts(table["evidence"], f"{where} evidence")
    for ref in evidence:
        if not _EVIDENCE_REF.fullmatch(ref):
            raise MatrixError(f"{where}: evidence {ref!r} is not a recognized reference")
    if evidence_status is not RowEvidence.CODE_READ_PENDING_ITEM_2 and not evidence:
        raise MatrixError(f"{where}: evidence is empty")
    dc3 = _texts(table["dc3"], f"{where} dc3")
    upstream = _texts(table["upstream"], f"{where} upstream")
    if not set(dc3) <= DC3_ITEMS or not set(upstream) <= UPSTREAM_ITEMS:
        raise MatrixError(f"{where}: dc3 must be in B1-B9 and upstream in U1-U7")
    no_raise_site = table["no_raise_site"]
    if not isinstance(no_raise_site, bool):
        raise MatrixError(f"{where}: no_raise_site must be a boolean")
    contexts = _texts(table["contexts"], f"{where} contexts")
    if not contexts:
        raise MatrixError(f"{where}: contexts is empty")
    return MatrixRow(
        row_id=_text(table["id"], where),
        title=_text(table["title"], where),
        cls=cls,
        rule=_text(table["rule"], where) if shared else None,
        shapes=_texts(table["shapes"], where) if shared else (),
        contexts=contexts,
        outcome=_member(RowOutcome, table["outcome"], where),
        evidence_status=evidence_status,
        evidence=evidence,
        owner=_text(table["owner"], where),
        coverage_limitation=_text(table["coverage_limitation"], where, empty=True),
        sites=_texts(table["sites"], f"{where} sites"),
        no_raise_site=no_raise_site,
        dc3=dc3,
        upstream=upstream,
        l2_relation=_text(table.get("l2_relation", ""), where, empty=True),
        statement=_text(table.get("statement", ""), where, empty=True),
        split=tuple(_split(s, f"{where} split") for s in table.get("split", [])),
    )


def _placement(table: Mapping[str, Any]) -> ClassifierPlacement:
    where = f"classifier {table.get('kind', '?')!r}"
    _keys(table, {"kind", "row", "outcome", "code", "evidence"}, set(), where)
    return ClassifierPlacement(
        kind=_text(table["kind"], where),
        row=_text(table["row"], where),
        outcome=_member(RowOutcome, table["outcome"], where),
        code=_text(table["code"], where, empty=True),
        evidence=_texts(table["evidence"], where),
    )


def _pointer(table: Mapping[str, Any]) -> Pointer:
    where = f"pointer {table.get('finding', '?')!r}"
    _keys(table, {"finding", "destination", "reason"}, set(), where)
    return Pointer(
        finding=_text(table["finding"], where),
        destination=_text(table["destination"], where),
        reason=_text(table["reason"], where),
    )


def load_matrix(path: Path = MATRIX_PATH) -> Matrix:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    _keys(data, {"schema", "row", "classifier", "pointer"}, set(), str(path))
    if data["schema"] != 1:
        raise MatrixError(f"unknown matrix schema {data['schema']!r}")
    rows = tuple(_row(r) for r in data["row"])
    ids = [r.row_id for r in rows]
    if len(set(ids)) != len(ids):
        raise MatrixError(f"duplicate row ids in {ids}")
    classifier = tuple(_placement(c) for c in data["classifier"])
    if tuple(c.kind for c in classifier) != BINDING_KINDS:
        raise MatrixError(f"classifier must place exactly {BINDING_KINDS}, in that order")
    for placement in classifier:
        if placement.row not in ids:
            raise MatrixError(f"classifier {placement.kind!r} names unknown row {placement.row!r}")
    pointers = tuple(_pointer(p) for p in data["pointer"])
    return Matrix(rows, classifier, pointers)
