"""Roots: the default set is the generator's rule, and caller roots are reported apart (D7)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
from agentic_mbse.sysml.occurrence_facts import OccurrenceStructure
from agentic_mbse.sysml.syside_adapter import SysideAdapter

CASES = Path(__file__).parents[1] / "fixtures" / "subset_profile" / "cases"


@pytest.fixture(scope="module")
def model() -> Any:
    loaded, diagnostics = SysideAdapter.load_model([CASES / "roots_mixed_owners.sysml"])
    assert not diagnostics.contains_errors()
    return loaded


def part_usage(model: Any, qualified_name: str) -> Any:
    (usage,) = [
        u
        for u in SysideAdapter.elements_of_type(model, "PartUsage")
        if str(u.qualified_name) == qualified_name
    ]
    return usage


def names(model: Any, ids: tuple[UUID, ...]) -> set[str]:
    by_id = {
        SysideAdapter.element_id(u): str(u.qualified_name)
        for u in SysideAdapter.elements_of_type(model, "PartUsage")
    }
    return {by_id[i] for i in ids}


def structure(model: Any, extra: tuple[Any, ...] = ()) -> OccurrenceStructure:
    result = extract_occurrence_structure(model, extra)
    assert isinstance(result, OccurrenceStructure), result
    return result


def test_default_roots_equal_generator_rule(model: Any) -> None:
    """Nested-package, package-level and item-def-owned usages are roots; part-def- and
    part-usage-owned ones are not (`occurrence.py:916-923`)."""
    result = structure(model)
    assert names(model, result.generator_root_ids) == {
        "roots::car",
        "roots::fleet",
        "roots::depot::reserve",
        "roots::Crate::tag",
    }
    assert result.caller_root_ids == ()
    assert {v.root_id for v in result.visits if v.parent is None} == set(result.generator_root_ids)


def test_caller_roots_are_traversed_and_tagged_apart(model: Any) -> None:
    template = part_usage(model, "roots::Template::site")
    default = structure(model)
    widened = structure(model, (template,))
    (caller,) = widened.caller_root_ids
    assert caller == SysideAdapter.element_id(template)
    assert widened.generator_root_ids == default.generator_root_ids
    generator_nodes = tuple(n for n in widened.nodes if widened.is_generator_root(n.root_id))
    assert generator_nodes == default.nodes
    reached = {n.usage_id for n in widened.nodes if n.root_id == caller}
    assert names(model, tuple(reached)) == {"roots::Template::site", "roots::Car::engine"}


def test_a_generator_root_passed_as_extra_adds_nothing(model: Any) -> None:
    assert structure(model, (part_usage(model, "roots::fleet"),)) == structure(model)


def test_an_extra_root_must_be_a_part_usage(model: Any) -> None:
    (definition,) = [
        d
        for d in SysideAdapter.elements_of_type(model, "PartDefinition")
        if str(d.qualified_name) == "roots::Car"
    ]
    with pytest.raises(TypeError, match="PartUsage"):
        extract_occurrence_structure(model, (definition,))
