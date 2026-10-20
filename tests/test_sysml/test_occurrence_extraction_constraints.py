"""Constraint attachments: every constraint usage gets one, keyed by its SysIDE element ID.

The generator takes a constraint usage's stable identity in `_index_constraint_associations`
(sysml-codegen `elaboration/elaborate.py:592-604`), as a model-wide identity check, not as
part of building occurrences. So an anonymous usage, which has no qualified name and so no
`declaration_id`, must not abort the occurrence structure here: it is attached like any
other, under its element ID.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
from agentic_mbse.sysml.occurrence_facts import OccurrenceStructure
from agentic_mbse.sysml.syside_adapter import SysideAdapter

CASES = Path(__file__).parents[1] / "fixtures" / "subset_profile" / "cases"


@pytest.fixture(scope="module")
def model() -> Any:
    loaded, diagnostics = SysideAdapter.load_model([CASES / "anonymous_assertion.sysml"])
    assert not diagnostics.contains_errors()
    return loaded


def constraint_usages(model: Any) -> list[Any]:
    return list(SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True))


def site_definition_id(model: Any) -> Any:
    (site,) = [
        d
        for d in SysideAdapter.elements_of_type(model, "PartDefinition")
        if str(d.qualified_name) == "anon::Site"
    ]
    return SysideAdapter.element_id(site)


def test_the_model_holds_one_anonymous_assertion(model: Any) -> None:
    anonymous = [u for u in constraint_usages(model) if u.qualified_name is None]
    assert [type(u).__name__ for u in anonymous] == ["AssertConstraintUsage"]


def test_an_anonymous_assertion_by_reference_is_attached_by_element_id(model: Any) -> None:
    result = extract_occurrence_structure(model)
    assert isinstance(result, OccurrenceStructure), result
    by_usage = {a.usage_id: a for a in result.constraint_attachments}
    assert set(by_usage) == {SysideAdapter.element_id(u) for u in constraint_usages(model)}
    owner = site_definition_id(model)
    for attachment in by_usage.values():
        assert attachment.owner_id == owner
        assert attachment.cause is None
        assert [scope.root_id for scope in attachment.scopes] == list(result.generator_root_ids)
