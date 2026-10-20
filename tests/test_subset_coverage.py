"""The coverage list a `clear` verdict carries (Item 3 design D11; spec § Library additions).

Pure: reads `tests/fixtures/subset_profile/inventory/` and the module only.
"""

from __future__ import annotations

import hashlib
import json

from agentic_mbse.sysml.subset_coverage import (
    FOLLOW_UP_SITES,
    NO_RULE_FAMILIES,
    SUBSET_COVERAGE_VERSION,
)
from agentic_mbse.sysml.subset_profile import SUBSET_PROFILE_VERSION
from tests.helpers.subset_matrix import RowClass, RowOutcome, load_matrix
from tests.helpers.subset_site_account import Disposition, load_site_account
from tests.test_sysml.test_subset_profile_version import PINNED, contract_digest

# A version maps to exactly one list. Changing the list means a new version and a new digest.
COVERAGE_PINNED = {
    "subset-coverage/v1": "531d8fd53be0fee4fa548a53d4cacab25d9fab8d7e875130b122aa4b78424781",
}

# `SUBSET_PROFILE_VERSION`'s digest at ebb3d467, before Item 3 (I4: library additions only add).
PROFILE_AT_EBB3D467 = (
    "subset-profile/v1",
    "30491315a96efaf8b75a6349787f0dd3498519d565b907a14211ab41bd68456b",
)


def coverage_digest() -> str:
    payload = [SUBSET_COVERAGE_VERSION, list(NO_RULE_FAMILIES), list(FOLLOW_UP_SITES)]
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


def test_coverage_list_pinned_to_its_version():
    assert COVERAGE_PINNED[SUBSET_COVERAGE_VERSION] == coverage_digest(), (
        "the coverage list changed: bump SUBSET_COVERAGE_VERSION and pin the new digest"
    )


def test_coverage_list_matches_no_rule_rows_of_the_matrix_fixture():
    matrix = load_matrix()
    no_rule = {
        row.row_id
        for row in matrix.values()
        if row.cls is RowClass.TRACKED_GAP and row.outcome is RowOutcome.REFUSED
    }
    # The module keeps the order the verdict's coverage line prints (design "What a user sees").
    assert len(set(NO_RULE_FAMILIES)) == len(NO_RULE_FAMILIES)
    assert set(NO_RULE_FAMILIES) == no_rule


def test_follow_up_sites_match_the_site_account():
    account = load_site_account()
    follow_up = sorted(
        row.site_id for row in account.rows if row.disposition is Disposition.EXPLICIT_FOLLOW_UP
    )
    assert list(FOLLOW_UP_SITES) == follow_up


def test_subset_profile_version_and_digest_unchanged_from_ebb3d467():
    assert (SUBSET_PROFILE_VERSION, contract_digest()) == PROFILE_AT_EBB3D467
    assert PINNED[SUBSET_PROFILE_VERSION] == PROFILE_AT_EBB3D467[1]
