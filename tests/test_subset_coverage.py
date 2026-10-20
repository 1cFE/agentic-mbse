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
    "subset-coverage/v2": "bb67041223ba4703fb463e0eac895f3ac75528c087de4d40b72fd81d2c86da78",
}

# The profile as Item 2a left it (I4: Item 3's library additions only add). Item 3 pinned v1 at
# ebb3d467; Item 2a's v2 replaced it before Item 3's additions were rebased onto it.
PROFILE_BEFORE_ITEM_3_ADDITIONS = (
    "subset-profile/v2",
    "02d82855eb2a7a37e4d65244649a2ab481ea073db70e7c5e45504f9559d43e51",
)


# Site IDs of sysml-codegen's raise sites, whose account lives in sysml-codegen since Item 2a.
CODEGEN_PREFIX = "sysml_codegen/"


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


def test_follow_up_sites_are_sorted_and_unique():
    assert list(FOLLOW_UP_SITES) == sorted(set(FOLLOW_UP_SITES))


def test_agentic_follow_up_sites_match_the_site_account():
    """The sysml-codegen half is checked against codegen's own account, by codegen's suite."""
    account = load_site_account()
    follow_up = sorted(
        row.site_id for row in account.rows if row.disposition is Disposition.EXPLICIT_FOLLOW_UP
    )
    assert [s for s in FOLLOW_UP_SITES if not s.startswith(CODEGEN_PREFIX)] == follow_up


def test_subset_profile_version_and_digest_unchanged_by_item_3_additions():
    assert (SUBSET_PROFILE_VERSION, contract_digest()) == PROFILE_BEFORE_ITEM_3_ADDITIONS
    assert PINNED[SUBSET_PROFILE_VERSION] == PROFILE_BEFORE_ITEM_3_ADDITIONS[1]
