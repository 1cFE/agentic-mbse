"""The site account is total over the scanner's forms, joined to the matrix, and owned.

Pure: reads `tests/fixtures/subset_profile/inventory/` only. Totality against the trees
themselves is the recorded `scan_sites.py --reconcile` run (spec: the reconciliation is a script
run, because this suite cannot assume a sysml-codegen checkout); this file checks everything the
account and the matrix can show on their own.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import tomllib

from tests.helpers.subset_matrix import RowClass, SiteStatus, load_matrix
from tests.helpers.subset_probe_judge import PINNED_CODEGEN_REV
from tests.helpers.subset_site_account import (
    ACCOUNT_PATH,
    Disposition,
    Role,
    SiteAccountError,
    load_site_account,
)

INVENTORY = Path(__file__).parent / "fixtures" / "subset_profile" / "inventory"
REQUIRED_BLIND_SPOTS = {
    "silent-omission",
    "computed-code-beyond-resolver",
    "unrecognized-exception-class-or-helper",
    "unproven-public-reachability",
}
COMPUTED_PROFILE_SITES = 5

ACCOUNT = load_site_account()
MATRIX = load_matrix()


def test_sites_join_matrix() -> None:
    for s in ACCOUNT.rows:
        if s.disposition is Disposition.IN_SCOPE:
            assert set(s.matrix_rows) <= MATRIX.keys(), s.site_id
            rules = {MATRIX[m].rule for m in s.matrix_rows if MATRIX[m].cls is RowClass.SHARED_RULE}
            assert set(s.rules) == rules and len(s.rules) == len(rules), s.site_id
        if s.disposition is Disposition.EXPLICIT_FOLLOW_UP:
            assert s.owner and s.coverage_limitation, s.site_id
    for row in MATRIX.values():
        assert row.sites or row.site_status is not SiteStatus.LISTED, row.row_id


def test_matrix_sites_are_exactly_the_in_scope_sites_naming_the_row() -> None:
    for row in MATRIX.values():
        assert set(row.sites) == {s.site_id for s in ACCOUNT.by_matrix_row(row.row_id)}, row.row_id


def test_ids_are_stable_scanner_ids_that_agree_with_their_columns() -> None:
    for s in ACCOUNT.rows:
        parts = s.site_id.split("::")
        file, channel, code, ordinal = parts[0], parts[2], "::".join(parts[3:-1]), parts[-1]
        assert (file, channel, code) == (s.file, s.channel, s.code), s.site_id
        assert ordinal.isdigit(), s.site_id


def test_header_names_the_scan_identity_and_the_count() -> None:
    header = "\n".join(ACCOUNT.header)
    assert "scanner: scan_sites/1" in header
    assert f"sysml-codegen: {PINNED_CODEGEN_REV}" in header
    assert "agentic-mbse: " in header
    assert f"sites: {len(ACCOUNT.rows)} (" in header


def test_scanner_toml_lists_the_required_blind_spots() -> None:
    data = tomllib.loads((INVENTORY / "scanner.toml").read_text(encoding="utf-8"))
    spots = {b["id"]: b["statement"] for b in data["blind_spot"]}
    assert REQUIRED_BLIND_SPOTS <= spots.keys()
    assert all(statement.strip() for statement in spots.values())
    assert data["scanner_revision"].startswith("scan_sites/1")


def test_the_five_computed_reason_sites_are_accounted_and_mapped() -> None:
    data = tomllib.loads((INVENTORY / "scanner.toml").read_text(encoding="utf-8"))
    mapped = {c["site_id"] for c in data["computed_site"]}
    computed = {
        s.site_id
        for s in ACCOUNT.rows
        if s.channel == "coded-DYNAMIC" and s.file.startswith("agentic_mbse/")
    }
    assert computed == mapped
    assert len(mapped) == COMPUTED_PROFILE_SITES


def test_no_evidence_gap_site_is_a_capability_refusal_by_code_alone() -> None:
    for s in ACCOUNT.rows:
        if "EVIDENCE_INCOMPLETE" in s.code and s.disposition is Disposition.IN_SCOPE:
            assert any(e.startswith("probe:") for e in s.evidence), s.site_id


def test_an_internal_invariant_cites_the_guard_that_keeps_valid_input_away() -> None:
    for s in ACCOUNT.rows:
        if s.role is Role.INTERNAL_INVARIANT:
            guard = any(".py:" in e or e.startswith("no caller under src/") for e in s.evidence[1:])
            assert guard, s.site_id


def test_an_in_scope_site_is_a_capability_refusal_or_its_relay() -> None:
    for s in ACCOUNT.rows:
        if s.disposition is Disposition.IN_SCOPE:
            assert s.role in {Role.PUBLIC_CAPABILITY, Role.RELAY_PLUMBING}, s.site_id


def test_both_trees_are_accounted() -> None:
    trees = {s.file.split("/", 1)[0] for s in ACCOUNT.rows}
    assert trees == {"sysml_codegen", "agentic_mbse"}


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("disposition", "deferred"),
        ("role", "plumbing"),
        ("owner", ""),
        ("matrix_row", "ES-004"),
        ("evidence", "elsewhere.py:1"),
    ],
)
def test_loader_rejects(tmp_path: Path, column: str, value: str) -> None:
    import csv

    lines = ACCOUNT_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    header = [line for line in lines if line.startswith("#")]
    rows = list(csv.DictReader(line for line in lines if not line.startswith("#")))
    victim = next(r for r in rows if r["disposition"] == "handled_elsewhere")
    victim[column] = value
    path = tmp_path / "site_account.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        fh.writelines(header)
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(SiteAccountError):
        load_site_account(path)
