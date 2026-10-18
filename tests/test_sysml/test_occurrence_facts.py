"""Pure occurrence fact types: frozen values, closed vocabularies, validated shapes."""

from __future__ import annotations

import dataclasses
import subprocess
import sys
from uuid import UUID, uuid5

import pytest

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.occurrence_facts import (
    AttachmentCause,
    BuildStage,
    CalcAttachment,
    MultiplicityReading,
    MultiplicityResolution,
    OccurrenceAbort,
    OccurrenceFailure,
    OccurrenceNode,
    OccurrenceScope,
    OccurrenceStructure,
    PackageScope,
    PathStep,
    UsageVisit,
    WriterSelection,
)

NS = UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")


def uid(name: str) -> UUID:
    return uuid5(NS, name)


ROOT, CHILD, DEF, CALC_A, CALC_B, PKG = (uid(n) for n in ("root", "child", "def", "a", "b", "pkg"))


def test_the_abort_vocabulary_is_closed_and_complete() -> None:
    """Design Appendix A's seven members, plus IDENTITY_UNSTABLE (P-4) and the split of the
    spike's `redefinition_invalid` into a root-family and an effective-declaration member (P-5)."""
    assert {m.name for m in OccurrenceAbort} == {
        "SPECIALIZATION_CYCLE",
        "RECURSIVE_CONTAINMENT",
        "INCOMPARABLE_TYPINGS",
        "REPEATED_NATIVE_DECLARATION",
        "DUPLICATE_OCCURRENCE_IDENTITY",
        "REDEFINITION_ROOT_FAMILY",
        "EFFECTIVE_DECLARATION_AMBIGUOUS",
        "WRITER_AMBIGUOUS",
        "IDENTITY_UNSTABLE",
    }
    assert [s.value for s in BuildStage] == ["slots", "occurrences", "writers"]
    assert {c.value for c in AttachmentCause} == {
        "owner_absent",
        "owner_kind_unattachable",
        "owner_has_no_occurrences",
    }


def test_failure_rejects_an_open_cause() -> None:
    with pytest.raises(TypeError):
        OccurrenceFailure("specialization_cycle", BuildStage.OCCURRENCES, None, "")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        OccurrenceFailure(OccurrenceAbort.SPECIALIZATION_CYCLE, "occurrences", None, "")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("reading", "resolution", "indices"),
    [
        (MultiplicityReading.absent(), MultiplicityResolution.ABSENT, (None,)),
        (
            MultiplicityReading(True, False, False, 3, None, False),
            MultiplicityResolution.EXACT,
            (0, 1, 2),
        ),
        (MultiplicityReading(True, False, False, 0, None, False), MultiplicityResolution.EXACT, ()),
        (MultiplicityReading(True, False, False, 2, 2, True), MultiplicityResolution.EXACT, (0, 1)),
        (
            MultiplicityReading(True, True, True, None, None, False),
            MultiplicityResolution.ORDERED,
            None,
        ),
        (
            MultiplicityReading(True, False, True, None, None, False),
            MultiplicityResolution.NONUNIQUE,
            None,
        ),
        (
            MultiplicityReading(True, False, False, None, None, False),
            MultiplicityResolution.UNRESOLVED_UPPER,
            None,
        ),
        (
            MultiplicityReading(True, False, False, -1, None, False),
            MultiplicityResolution.NEGATIVE,
            None,
        ),
        (
            MultiplicityReading(True, False, False, 4, None, True),
            MultiplicityResolution.UNRESOLVED_LOWER,
            None,
        ),
        (MultiplicityReading(True, False, False, 4, 1, True), MultiplicityResolution.RANGE, None),
    ],
)
def test_resolution_is_the_first_failing_check_in_generator_order(
    reading: MultiplicityReading,
    resolution: MultiplicityResolution,
    indices: tuple[int | None, ...] | None,
) -> None:
    assert reading.resolution is resolution
    assert reading.indices == indices


@pytest.mark.parametrize(
    "fields",
    [
        (False, True, False, None, None, False),  # absent with a flag
        (False, False, False, 2, None, False),  # absent with a bound
        (True, True, False, 2, None, False),  # ordered, but a bound was read
        (True, False, False, None, 1, True),  # lower read after the upper failed
        (True, False, False, -2, 1, True),  # lower read after a negative upper
        (True, False, False, 2, 1, False),  # a lower value without a lower bound
    ],
)
def test_a_reading_holds_only_what_the_generator_reads(fields: tuple) -> None:
    with pytest.raises(ValueError):
        MultiplicityReading(*fields)


def test_counts_are_per_visit_so_per_parent_occurrence() -> None:
    four = UsageVisit(
        CHILD,
        (PathStep(ROOT, None),),
        ROOT,
        MultiplicityReading(True, False, False, 4, None, False),
    )
    unexpandable = UsageVisit(
        CHILD, (PathStep(ROOT, 0),), ROOT, MultiplicityReading(True, True, False, None, None, False)
    )
    assert four.count == 4
    assert unexpandable.count is None
    with pytest.raises(ValueError):
        UsageVisit(CHILD, (), ROOT, MultiplicityReading.absent())


def test_node_shape_is_validated() -> None:
    path = (PathStep(ROOT, None),)
    node = OccurrenceNode(path, ROOT, DEF, frozenset({DEF}), (), ROOT)
    assert node.parent is None
    child = OccurrenceNode(path + (PathStep(CHILD, 1),), CHILD, None, frozenset(), (), ROOT)
    assert child.parent == path
    with pytest.raises(ValueError):
        OccurrenceNode((), ROOT, None, frozenset(), (), ROOT)
    with pytest.raises(ValueError):
        OccurrenceNode(path, ROOT, DEF, frozenset(), (), ROOT)  # typed with an empty closure
    with pytest.raises(ValueError):
        OccurrenceNode(
            path, ROOT, None, frozenset(), tuple(sorted((CHILD, DEF), key=str, reverse=True)), ROOT
        )
    with pytest.raises(ValueError):
        PathStep(ROOT, -1)


def test_attachment_has_scopes_or_a_cause() -> None:
    scope = OccurrenceScope(ROOT, (PathStep(ROOT, None),))
    CalcAttachment(CALC_A, DEF, (scope,), None)
    CalcAttachment(CALC_A, None, (), AttachmentCause.OWNER_ABSENT)
    with pytest.raises(ValueError):
        CalcAttachment(CALC_A, DEF, (), None)
    with pytest.raises(ValueError):
        CalcAttachment(CALC_A, DEF, (scope,), AttachmentCause.OWNER_HAS_NO_OCCURRENCES)
    with pytest.raises(ValueError):
        CalcAttachment(CALC_A, DEF, (), AttachmentCause.OWNER_ABSENT)


def _structure(writers: tuple[WriterSelection, ...]) -> OccurrenceStructure:
    path = (PathStep(ROOT, None),)
    return OccurrenceStructure(
        generator_root_ids=(ROOT,),
        caller_root_ids=(),
        visits=(UsageVisit(ROOT, None, ROOT, MultiplicityReading.absent()),),
        nodes=(OccurrenceNode(path, ROOT, DEF, frozenset({DEF}), (), ROOT),),
        part_definition_ids=(DEF,),
        calc_attachments=(),
        writers=writers,
    )


def test_selected_and_overridden_scopes_per_usage() -> None:
    """Implementation Note (a): a usage selected in some scopes and overridden in others."""
    first = OccurrenceScope(ROOT, (PathStep(ROOT, 0),))
    second = OccurrenceScope(ROOT, (PathStep(ROOT, 1),))
    both = tuple(sorted((CALC_A, CALC_B), key=str))
    structure = _structure(
        (
            WriterSelection(CALC_A, first, CALC_A, CALC_A, both),
            WriterSelection(CALC_A, second, CALC_A, CALC_B, both),
        )
    )
    assert structure.selected_scopes(CALC_A) == (first,)
    assert structure.overridden_scopes(CALC_A) == (second,)
    assert structure.selected_scopes(CALC_B) == (second,)
    assert structure.overridden_scopes(CALC_B) == (first,)
    assert structure.definition_occurrence_count(DEF) == 1
    assert structure.occurrence_counts() == {ROOT: 1}


def test_structure_order_and_roots_are_enforced() -> None:
    with pytest.raises(ValueError):
        dataclasses.replace(_structure(()), caller_root_ids=(ROOT,))
    with pytest.raises(ValueError):
        dataclasses.replace(_structure(()), generator_root_ids=())  # a node from no listed root
    scope_a, scope_b = PackageScope(uid("p1")), PackageScope(uid("p2"))
    lo, hi = sorted((scope_a, scope_b), key=lambda s: str(s.package_id))
    unordered = (
        WriterSelection(CALC_A, hi, CALC_A, CALC_A, (CALC_A,)),
        WriterSelection(CALC_A, lo, CALC_A, CALC_A, (CALC_A,)),
    )
    with pytest.raises(ValueError):
        _structure(unordered)
    with pytest.raises(ValueError):
        WriterSelection(CALC_A, lo, CALC_A, CALC_B, (CALC_A,))  # the winner is not applicable


def test_types_are_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        PathStep(ROOT, None).index = 1  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        _structure(()).nodes = ()  # type: ignore[misc]


def test_element_refs_need_stable_identity() -> None:
    ElementRef(ROOT, "P::root", "PartUsage")
    with pytest.raises(ValueError):
        ElementRef(UUID("12345678-1234-4234-8234-123456789abc"), "P::x", "PartUsage")  # UUIDv4
    with pytest.raises(ValueError):
        ElementRef(ROOT, "", "PartUsage")
    with pytest.raises(ValueError):
        SafeLocation("f.sysml", -1, None)


def test_the_fact_types_import_no_parser() -> None:
    code = (
        "import sys, agentic_mbse.sysml.occurrence_facts, agentic_mbse.sysml.fact_refs;"
        "bad = [m for m in sys.modules if m == 'syside' or m.endswith('syside_adapter') "
        "or m.endswith('reference_use') or m.startswith('sysml_codegen')];"
        "assert not bad, bad"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
