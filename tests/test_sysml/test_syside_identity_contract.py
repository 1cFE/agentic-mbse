"""Raw SysIDE identity contract required by the exact-ID codegen front end."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from agentic_mbse.sysml.expression import feature_chain_facts, resolved_target_fact
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

syside = get_syside()

_LIBRARY = """\
package IdentityContractLib {
    private import ScalarValues::Real;

    calc def PassThrough {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def Sensor {
        attribute reading : Real default = 1.0;
    }

    part def BetterSensor :> Sensor {
        :>> reading = 2.0;
    }

    part def BaseStation {
        part sensor : Sensor;
        calc pass : PassThrough {
            in x = sensor.reading;
        }
    }

    part def SpecializedStation :> BaseStation {
        part :>> sensor : BetterSensor;
    }
}
"""

_DESIGN = """\
package IdentityContractDesign {
    private import IdentityContractLib::*;
    part station : SpecializedStation;
}
"""


def _write_fixture(root: Path) -> list[Path]:
    root.mkdir(parents=True)
    library = root / "library.sysml"
    design = root / "design.sysml"
    library.write_text(_LIBRARY)
    design.write_text(_DESIGN)
    return [library, design]


def _load(paths: list[Path]) -> Any:
    model, diagnostics = syside.try_load_model([str(path) for path in paths])
    assert not list(diagnostics.all), list(diagnostics.all)
    return model


def _named_ids(model: Any) -> dict[str, UUID]:
    return {
        str(element.qualified_name): UUID(str(element.element_id))
        for element in model.elements(syside.Element, include_subtypes=True)
        if getattr(element, "qualified_name", None) is not None
    }


def _redefinition_facts(
    model: Any,
) -> dict[tuple[str, str, bool], tuple[UUID, UUID, UUID]]:
    result: dict[tuple[str, str, bool], tuple[UUID, UUID, UUID]] = {}
    for feature in model.elements(syside.Feature, include_subtypes=True):
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = relationship.redefined_feature
            redefining = relationship.redefining_feature
            assert redefined is not None
            assert redefining is not None
            key = (
                str(redefining.qualified_name),
                str(redefined.qualified_name),
                bool(relationship.is_implied),
            )
            result[key] = (
                UUID(str(redefining.element_id)),
                UUID(str(redefined.element_id)),
                UUID(str(relationship.element_id)),
            )
    return result


def test_named_element_ids_and_resolved_referents_are_exact(tmp_path: Path) -> None:
    model = _load(_write_fixture(tmp_path / "first"))
    named_ids = _named_ids(model)
    assert named_ids
    assert all(element_id.version == 5 for element_id in named_ids.values())

    checked = 0
    for expression in model.elements(
        syside.FeatureReferenceExpression, include_subtypes=True
    ):
        referent = getattr(expression, "referent", None)
        qualified_name = getattr(referent, "qualified_name", None)
        if qualified_name is None:
            continue
        assert SysideAdapter.element_id(referent) == named_ids[str(qualified_name)]
        fact = resolved_target_fact(referent)
        assert fact is not None
        assert fact.element_id == named_ids[str(qualified_name)]
        assert fact.owner_element_id is not None
        checked += 1
    assert checked >= 2

    with pytest.raises(ValueError, match="element_id"):
        SysideAdapter.element_id(object())


def test_chain_and_typing_surfaces_retain_exact_endpoint_ids(tmp_path: Path) -> None:
    model = _load(_write_fixture(tmp_path / "chain"))
    named_ids = _named_ids(model)

    chains = list(
        model.elements(syside.FeatureChainExpression, include_subtypes=True)
    )
    chain = next(
        expression
        for expression in chains
        if str(getattr(expression.target_feature, "qualified_name", "")).endswith(
            "::reading"
        )
    )
    root_expression = chain.operands[0]
    root = root_expression.referent
    leaf = chain.target_feature
    assert UUID(str(root.element_id)) == named_ids[str(root.qualified_name)]
    assert UUID(str(leaf.element_id)) == named_ids[str(leaf.qualified_name)]

    chain_fact = feature_chain_facts(chain)
    assert chain_fact.root is not None
    assert chain_fact.leaf is not None
    assert chain_fact.root.element_id == named_ids[str(root.qualified_name)]
    assert chain_fact.leaf.element_id == named_ids[str(leaf.qualified_name)]
    assert chain_fact.segment_element_ids[-1] == chain_fact.leaf.element_id
    assert not chain_fact.has_index_segment

    station = next(
        usage
        for usage in model.elements(syside.PartUsage, include_subtypes=True)
        if getattr(usage, "name", None) == "station"
    )
    explicit_typing = next(iter(station.owned_typings))
    typed_definition = explicit_typing.type
    assert UUID(str(typed_definition.element_id)) == named_ids[
        "IdentityContractLib::SpecializedStation"
    ]


def test_authored_and_implied_redefinitions_use_stable_endpoints(
    tmp_path: Path,
) -> None:
    first_paths = _write_fixture(tmp_path / "first")
    second_paths = _write_fixture(tmp_path / "relocated")
    first = _redefinition_facts(_load(first_paths))
    second = _redefinition_facts(_load(list(reversed(second_paths))))

    assert first.keys() == second.keys()
    assert any(key[2] for key in first)
    assert any(not key[2] for key in first)
    for key in first:
        first_redefining, first_redefined, first_relationship = first[key]
        second_redefining, second_redefined, second_relationship = second[key]
        assert (first_redefining, first_redefined) == (
            second_redefining,
            second_redefined,
        )
        assert first_redefining.version == 5
        assert first_redefined.version == 5
        assert first_relationship.version == 4
        assert second_relationship.version == 4
        assert first_relationship != second_relationship
