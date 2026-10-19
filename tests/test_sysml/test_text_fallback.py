"""`reconstruct_expression`'s output is unchanged by the text-fallback predicate (Item 3 Phase 6).

The texts were recorded from `expression.py` at `ebb3d467`, before its dispatch was shared with
`falls_to_text_fallback` (`scripts/l6_subset/record_reconstruct_texts.py`). Item 2's agent
depends on `reconstruct_expression`, so every text must match exactly (design D12a, I4).
"""

from __future__ import annotations

import json

import pytest

from tests.helpers.reconstruct_texts import FIXTURES, RECORD, reconstruct_file


@pytest.mark.syside
def test_reconstruct_expression_output_unchanged_on_every_fixture_expression():
    recorded = json.loads(RECORD.read_text(encoding="utf-8"))
    assert len(recorded) >= 268
    now = {relative: reconstruct_file(FIXTURES / relative) for relative in recorded}
    changed = sorted(relative for relative in recorded if now[relative] != recorded[relative])
    assert changed == []
