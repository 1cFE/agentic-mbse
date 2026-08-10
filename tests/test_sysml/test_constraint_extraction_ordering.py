"""Canonical-order stability across model load order (F9 regression, live SysIDE).

Two anonymous assert constraints at the same line number in *different* files used to share
a sort key `(line, "")`, so serialized order — and therefore canonical bytes — depended on
the order files were passed to `try_load_model`. The extended key breaks the tie with file
path and column.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import agentic_mbse.sysml.constraint_extraction as constraint_extraction
from agentic_mbse.sysml.constraint_extraction import (
    extract_constraint_facts,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.constraint_facts import serialize
from agentic_mbse.sysml.executable_profile import evaluate_identified_profile
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

syside = get_syside()

# Both files put an anonymous assert on the same line number (line 3) so the old
# `(line, qualified_name or "")` key collides: anonymous asserts have no qualified name.
_FILE_A = """package OrderProbeA {
    part def ProbeA {
        assert constraint { 1 <= 2 }
    }
}
"""

_FILE_B = """package OrderProbeB {
    part def ProbeB {
        assert constraint { 3 <= 4 }
    }
}
"""


def _serialize_for(paths: list[str]) -> str:
    model, diagnostics = syside.try_load_model(paths)
    assert not list(diagnostics.all), list(diagnostics.all)
    return serialize(extract_constraint_facts(model))


def test_two_file_anonymous_asserts_serialize_identically_for_both_load_orders(
    tmp_path: Path,
) -> None:
    file_a = tmp_path / "order_probe_a.sysml"
    file_b = tmp_path / "order_probe_b.sysml"
    file_a.write_text(_FILE_A)
    file_b.write_text(_FILE_B)

    forward = _serialize_for([str(file_a), str(file_b)])
    reverse = _serialize_for([str(file_b), str(file_a)])

    assert forward == reverse


class _ReverseElementOrderModel:
    def __init__(self, model: object) -> None:
        self._model = model

    def elements(self, kind: type, *, include_subtypes: bool = False):
        elements = self._model.elements(kind, include_subtypes=include_subtypes)
        return iter(reversed(list(elements)))


class _AlternatingConstraintOrderModel:
    def __init__(self, model: object) -> None:
        self._model = model
        self._constraint_calls = 0

    def elements(self, kind: type, *, include_subtypes: bool = False):
        elements = list(self._model.elements(kind, include_subtypes=include_subtypes))
        if kind.__name__ == "ConstraintUsage":
            self._constraint_calls += 1
            if self._constraint_calls % 2 == 0:
                elements.reverse()
        return iter(elements)


def test_identified_anonymous_usages_keep_exact_ids_when_enumeration_reverses(
    tmp_path: Path,
) -> None:
    file_a = tmp_path / "order_probe_a.sysml"
    file_b = tmp_path / "order_probe_b.sysml"
    file_a.write_text(_FILE_A)
    file_b.write_text(_FILE_B)
    model, diagnostics = syside.try_load_model([str(file_a), str(file_b)])
    assert not list(diagnostics.all), list(diagnostics.all)

    constraints = list(
        SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True)
    )
    expected_ids = {SysideAdapter.element_id(item) for item in constraints}
    forward = extract_identified_constraint_facts(model)
    reversed_result = extract_identified_constraint_facts(_ReverseElementOrderModel(model))

    assert {item.usage_id for item in forward.usages} == expected_ids
    assert all(item.fact.identity.qualified_name is None for item in forward.usages)
    assert [item.usage_id for item in forward.usages] == [
        item.usage_id for item in reversed_result.usages
    ]
    profile = evaluate_identified_profile(forward)
    assert {item.usage_id for item in profile.decisions} == expected_ids
    assert not profile.missing_usage_ids
    assert serialize(forward.facts) == serialize(extract_constraint_facts(model))


def test_identified_fact_pairing_uses_usage_identity_not_parallel_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_a = tmp_path / "order_probe_a.sysml"
    file_b = tmp_path / "order_probe_b.sysml"
    file_a.write_text(_FILE_A)
    file_b.write_text(_FILE_B)
    model, diagnostics = syside.try_load_model([str(file_a), str(file_b)])
    assert not list(diagnostics.all), list(diagnostics.all)

    constraints = list(
        SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True)
    )
    expected_file_by_id = {
        SysideAdapter.element_id(item): SysideAdapter.get_source_location(item)[0]
        for item in constraints
    }
    monkeypatch.setattr(
        constraint_extraction,
        "_constraint_sort_key",
        lambda _constraint: (0, "", "", 0),
    )

    identified = extract_identified_constraint_facts(_AlternatingConstraintOrderModel(model))

    assert {
        item.usage_id: item.fact.location.file if item.fact.location is not None else None
        for item in identified.usages
    } == expected_file_by_id
