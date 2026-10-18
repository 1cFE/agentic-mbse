"""Load the site account (`tests/fixtures/subset_profile/inventory/site_account.csv`).

One row per candidate refusal site that `scripts/subset_profile/scan_sites.py` recognizes in
sysml-codegen at the pin and in agentic-mbse at the implementation revision. Each row carries
its D2 disposition, semantic role, owner, evidence pointer and, for an in-scope site, the matrix
row that covers it. The join to the matrix is asserted in `tests/test_subset_site_account.py`.

Pure and stdlib-only. Leading `#` lines are the scan identity and are kept as `header`.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypeVar

ACCOUNT_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "subset_profile"
    / "inventory"
    / "site_account.csv"
)
FIELDS = (
    "site_id",
    "file",
    "line",
    "channel",
    "code",
    "disposition",
    "role",
    "owner",
    "matrix_row",
    "rule",
    "evidence",
    "coverage_limitation",
    "note",
)


_E = TypeVar("_E", bound=StrEnum)


class SiteAccountError(ValueError):
    """The site account breaks its schema."""


class Disposition(StrEnum):
    """Owner decision D2."""

    IN_SCOPE = "in_scope"
    HANDLED_ELSEWHERE = "handled_elsewhere"
    EXPLICIT_FOLLOW_UP = "explicit_follow_up"


class Role(StrEnum):
    """What the site is for, where the code shows it (spec § Inventory content)."""

    PUBLIC_CAPABILITY = "public_capability"
    MALFORMED_INPUT = "malformed_input"
    ENVIRONMENT = "environment"
    SNAPSHOT_INTEGRITY = "snapshot_integrity"
    RELAY_PLUMBING = "relay_plumbing"
    INTERNAL_INVARIANT = "internal_invariant"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SiteRow:
    site_id: str
    file: str
    line: int
    channel: str
    code: str
    disposition: Disposition
    role: Role
    owner: str
    #: The matrix rows covering the site (`;`-separated in the file); non-empty iff in scope.
    #: One generator site can be the raise site of several rows (the binding-source classifier).
    matrix_rows: tuple[str, ...]
    #: The rule records of the shared-rule matrix rows, `;`-separated in the file. More than one
    #: when one site serves rows of several rules (elaborate.py:1939 also emits the indexed
    #: source refusal, which the matrix places at INDEXED-REFERENCE).
    rules: tuple[str, ...]
    #: `file.py:line` at the scanned revision, then any further pointers, `;`-separated.
    evidence: tuple[str, ...]
    #: Required for an explicit follow-up.
    coverage_limitation: str
    note: str


@dataclass(frozen=True)
class SiteAccount:
    header: tuple[str, ...]
    rows: tuple[SiteRow, ...]

    def by_matrix_row(self, row_id: str) -> tuple[SiteRow, ...]:
        return tuple(r for r in self.rows if row_id in r.matrix_rows)


def _member(enum: type[_E], value: str, where: str) -> _E:
    try:
        return enum(value)
    except ValueError as exc:
        raise SiteAccountError(f"{where}: {value!r} is not a {enum.__name__}") from exc


def _row(raw: dict[str, str]) -> SiteRow:
    where = f"site {raw.get('site_id', '?')!r}"
    disposition = _member(Disposition, raw["disposition"], where)
    role = _member(Role, raw["role"], where)
    evidence = tuple(e.strip() for e in raw["evidence"].split(";") if e.strip())
    row = SiteRow(
        site_id=raw["site_id"],
        file=raw["file"],
        line=int(raw["line"]),
        channel=raw["channel"],
        code=raw["code"],
        disposition=disposition,
        role=role,
        owner=raw["owner"].strip(),
        matrix_rows=tuple(m.strip() for m in raw["matrix_row"].split(";") if m.strip()),
        rules=tuple(r.strip() for r in raw["rule"].split(";") if r.strip()),
        evidence=evidence,
        coverage_limitation=raw["coverage_limitation"].strip(),
        note=raw["note"].strip(),
    )
    if not row.owner or not row.evidence or not row.note:
        raise SiteAccountError(f"{where}: owner, evidence and note are required")
    if not row.evidence[0].startswith(f"{row.file}:{row.line}"):
        raise SiteAccountError(f"{where}: evidence must start with the site, {row.file}:{row.line}")
    if (disposition is Disposition.IN_SCOPE) != bool(row.matrix_rows):
        raise SiteAccountError(f"{where}: matrix_row is required iff the site is in scope")
    if len(set(row.matrix_rows)) != len(row.matrix_rows):
        raise SiteAccountError(f"{where}: matrix_row repeats a row")
    if row.rules and not row.matrix_rows:
        raise SiteAccountError(f"{where}: a rule needs a matrix row")
    if (disposition is Disposition.EXPLICIT_FOLLOW_UP) != bool(row.coverage_limitation):
        raise SiteAccountError(f"{where}: coverage_limitation is required iff explicit follow-up")
    return row


def load_site_account(path: Path = ACCOUNT_PATH) -> SiteAccount:
    with path.open(newline="", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    header = tuple(line[2:] for line in lines if line.startswith("# "))
    reader = csv.DictReader(line for line in lines if not line.startswith("#"))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise SiteAccountError(f"{path}: columns must be {FIELDS}, got {reader.fieldnames}")
    rows = tuple(_row(raw) for raw in reader)
    ids = [r.site_id for r in rows]
    if len(set(ids)) != len(ids):
        raise SiteAccountError(f"{path}: repeated site ids")
    return SiteAccount(header=header, rows=rows)
