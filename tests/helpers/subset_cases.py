"""The packaged conformance cases, as the screen tests read them (Item 2a design D14).

A case belongs to the rule its id starts with (`<rule>__<shape>__<context>[__<variant>]`). A
`reproduction` case reproduces a candidate family that has no rule, so its id names the family
(`candidate-<family>__...`) and it belongs to no rule.
"""

from __future__ import annotations

from agentic_mbse.sysml.conformance_case import (
    CaseKind,
    PackagedCase,
    load_packaged_case,
    packaged_case_ids,
)
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import (
    SubsetFinding,
    SubsetProfileResult,
    evaluate_subset_profile,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

ALL_CASES = tuple(load_packaged_case(case_id) for case_id in packaged_case_ids())


def rule_of(case: PackagedCase) -> str | None:
    """The rule a case tests; None for a reproduction case."""
    return None if case.kind is CaseKind.REPRODUCTION else case.case_id.split("__")[0]


def cases_of(rules: set[str], kind: CaseKind | None = None) -> list[PackagedCase]:
    return [c for c in ALL_CASES if rule_of(c) in rules and (kind is None or c.kind is kind)]


def evaluate(case: PackagedCase) -> SubsetProfileResult:
    model, diagnostics = SysideAdapter.load_model(list(case.model_files()))
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return evaluate_subset_profile(extract_subset_facts(model))


def at_construct(result: SubsetProfileResult, case: PackagedCase, rule: str) -> list[SubsetFinding]:
    """The rule's findings located on the case's construct lines."""
    return [
        f
        for f in result.findings
        if f.rule_id == rule
        and f.location.line is not None
        and case.construct.contains(f.location.line)
    ]
