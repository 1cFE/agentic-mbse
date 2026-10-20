"""The model-wide rules and the candidate reproductions on their packaged cases.

Every packaged case of `calc-owned-assertion`, `calc-usage-result`, `indexed-reference`,
`invocation-callable`, `conditional-expression` and `string-value-omission`, every control of
those rules, and every reproduction case of a candidate family with no rule, reproduces its stored screen answer: the
verdict and every finding (Item 2a design D14). The stored answers are held to the records by
`tests/test_subset_case_citations.py`, and to the generator by sysml-codegen.
"""

from __future__ import annotations

import pytest

from agentic_mbse.sysml.conformance_case import (
    CaseKind,
    PackagedCase,
    load_packaged_case,
    screen_answer,
)
from agentic_mbse.sysml.subset_profile import Outcome
from tests.helpers.subset_cases import ALL_CASES, at_construct, cases_of, evaluate

RULES = {
    "calc-owned-assertion",
    "calc-usage-result",
    "indexed-reference",
    "invocation-callable",
    "conditional-expression",
    "string-value-omission",
}
REPRODUCTIONS = [c for c in ALL_CASES if c.kind is CaseKind.REPRODUCTION]


@pytest.mark.parametrize("case", cases_of(RULES) + REPRODUCTIONS, ids=lambda c: c.case_id)
def test_screen_reproduces_the_stored_answer(case: PackagedCase) -> None:
    assert screen_answer(evaluate(case)) == case.screen


def test_a_calc_usage_owned_constraint_is_reported_on_the_constraint_not_its_owner() -> None:
    case = load_packaged_case("calc-owned-assertion__asserted_constraint__calc_usage_owner")
    (finding,) = at_construct(evaluate(case), case, "calc-owned-assertion")
    assert finding.subject.qualified_name == "fx::Site::path::f1"
    assert finding.location.line == 11  # the generator locates the refusal at the owner, line 8


def test_every_string_spelling_and_reading_is_omitted() -> None:
    prefix = "string-value-omission__string_value__attribute_value__"
    variants = [c for c in cases_of({"string-value-omission"}) if c.case_id.startswith(prefix)]
    assert {c.case_id.removeprefix(prefix) for c in variants} == {
        "attribute_declaration",
        "read_by_attribute",
        "read_by_attribute_shorthand",
        "redefinition_shorthand",
        "template",
        "template_shorthand",
    }
    for case in variants:
        (finding,) = at_construct(evaluate(case), case, "string-value-omission")
        assert finding.outcome is Outcome.OMITTED
