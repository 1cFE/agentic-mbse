"""The decision version pins the records and the invocation allowlist (design invariant 9).

Changing either changes the digest below. When it does, bump `SUBSET_PROFILE_VERSION` and add
the new version's digest here; a version maps to exactly one digest, so an edit cannot ride
under an old version. `v1` is Item 1's contract as merged. Item 2a moves to `v2` at its first
record change and re-pins `v2` with each later one until it merges (Item 2a design
Implementation Notes); the plan's implementation notes record each re-pin.
"""

from __future__ import annotations

import hashlib
from uuid import UUID

import pytest

from agentic_mbse.sysml.invocation_allowlist import SUPPORTED_INVOCATION_IDS
from agentic_mbse.sysml.subset_profile import SUBSET_PROFILE_VERSION
from tests.helpers.subset_records import RECORDS_RESOURCE

PINNED = {
    "subset-profile/v1": "30491315a96efaf8b75a6349787f0dd3498519d565b907a14211ab41bd68456b",
    "subset-profile/v2": "4db684d65b29d82399478bd071446c8455b90a1dc561d8ab045dc307f9314a04",
}


def contract_digest() -> str:
    digest = hashlib.sha256()
    digest.update(RECORDS_RESOURCE.read_bytes())
    for callable_id in sorted(str(i) for i in SUPPORTED_INVOCATION_IDS):
        digest.update(callable_id.encode())
    return digest.hexdigest()


def test_version_pins_the_records_and_the_allowlist() -> None:
    assert PINNED[SUBSET_PROFILE_VERSION] == contract_digest(), (
        "the records or the allowlist changed: bump SUBSET_PROFILE_VERSION and pin the new digest"
    )


def test_the_digest_covers_the_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    before = contract_digest()
    widened = SUPPORTED_INVOCATION_IDS | {UUID(int=1)}
    monkeypatch.setattr(f"{__name__}.SUPPORTED_INVOCATION_IDS", widened)
    assert contract_digest() != before
