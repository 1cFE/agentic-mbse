"""The site account is total over the scanner's forms, joined to the matrix, owned and witnessed.

Pure: reads `tests/fixtures/subset_profile/inventory/` and the packaged cases' witness lists. Totality against the tree itself is
the recorded `scan_sites.py --reconcile` run; this file checks everything the account and the
matrix can show on their own. The account holds agentic-mbse sites only: the sysml-codegen sites
have their own account and drift test in sysml-codegen (EXEC-SUBSET-CONTRACT Item 2a D7).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import tomllib

from agentic_mbse.sysml.conformance_case import load_packaged_case, packaged_case_ids
from tests.helpers.subset_matrix import RowClass, SiteStatus, load_matrix
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
WITNESSES = {
    case_id: load_packaged_case(case_id).agentic_site_witnesses for case_id in packaged_case_ids()
}


def test_sites_join_matrix() -> None:
    for s in ACCOUNT.rows:
        assert set(s.matrix_rows) <= MATRIX.keys(), s.site_id
        if s.disposition is Disposition.IN_SCOPE:
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
    assert "scanner: scan_sites/" in header
    assert "agentic-mbse: " in header
    assert f"sites: {len(ACCOUNT.rows)} (agentic-mbse)" in header


def test_scanner_toml_lists_the_required_blind_spots() -> None:
    data = tomllib.loads((INVENTORY / "scanner.toml").read_text(encoding="utf-8"))
    spots = {b["id"]: b["statement"] for b in data["blind_spot"]}
    assert REQUIRED_BLIND_SPOTS <= spots.keys()
    assert all(statement.strip() for statement in spots.values())
    assert data["scanner_revision"].startswith("scan_sites/2")


def test_the_five_computed_reason_sites_are_accounted_and_mapped() -> None:
    data = tomllib.loads((INVENTORY / "scanner.toml").read_text(encoding="utf-8"))
    mapped = {c["site_id"] for c in data["computed_site"]}
    computed = {s.site_id for s in ACCOUNT.rows if s.channel == "coded-DYNAMIC"}
    assert computed == mapped
    assert len(mapped) == COMPUTED_PROFILE_SITES


def test_no_evidence_gap_site_is_a_capability_refusal_by_code_alone() -> None:
    for s in ACCOUNT.rows:
        if "EVIDENCE_INCOMPLETE" in s.code and s.disposition is Disposition.IN_SCOPE:
            assert any(e.startswith("case:") for e in s.evidence), s.site_id


def test_an_internal_invariant_cites_the_guard_that_keeps_valid_input_away() -> None:
    for s in ACCOUNT.rows:
        if s.role is Role.INTERNAL_INVARIANT:
            guard = any(".py:" in e or e.startswith("no caller under src/") for e in s.evidence[1:])
            assert guard, s.site_id


def test_an_in_scope_site_is_a_capability_refusal_or_its_relay() -> None:
    for s in ACCOUNT.rows:
        if s.disposition is Disposition.IN_SCOPE:
            assert s.role in {Role.PUBLIC_CAPABILITY, Role.RELAY_PLUMBING}, s.site_id


def test_only_agentic_mbse_sites_are_accounted() -> None:
    assert {s.file.split("/", 1)[0] for s in ACCOUNT.rows} == {"agentic_mbse"}


def test_an_explicit_follow_up_may_name_the_row_it_is_routed_to() -> None:
    routed = [
        s for s in ACCOUNT.rows if s.disposition is Disposition.EXPLICIT_FOLLOW_UP and s.matrix_rows
    ]
    assert {s.matrix_rows for s in routed} == {("PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS",)}
    assert len(routed) == 4


def _linked_public_sites() -> set[str]:
    """The rows a shared rule links to that refuse a public capability (plan PD5, from P2)."""
    return {s.site_id for s in ACCOUNT.rows if s.rules and s.role is Role.PUBLIC_CAPABILITY}


def test_every_witness_names_an_accounted_site() -> None:
    accounted = {s.site_id for s in ACCOUNT.rows}
    named = {(case_id, w) for case_id, ws in WITNESSES.items() for w in ws}
    assert {(c, w) for c, w in named if w not in accounted} == set()


def test_every_linked_public_site_has_a_packaged_witness_or_says_why_none_can() -> None:
    """Whether each witness really fires its site is sysml-codegen's live check."""
    data = tomllib.loads((INVENTORY / "scanner.toml").read_text(encoding="utf-8"))
    unwitnessed = {u["site_id"]: u["statement"] for u in data["unwitnessed_site"]}
    witnessed = {w for ws in WITNESSES.values() for w in ws}
    linked = _linked_public_sites()
    assert all(statement.strip() for statement in unwitnessed.values())
    assert unwitnessed.keys() <= linked
    assert linked - witnessed == unwitnessed.keys()


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
