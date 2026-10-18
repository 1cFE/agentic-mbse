"""The run-scoped model load and constraint extraction (Item 3 design D14, invariant I10, bet B5).

Every level's result must be identical with and without the shared session; inside one run the
model is loaded once for L2-L6 and its constraint facts are extracted once.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import os
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml import syside_adapter
from agentic_mbse.sysml.constraint_extraction import extract_identified_constraint_facts
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.validation import session as session_module
from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
from agentic_mbse.validation.level2_structure import validate_structure
from agentic_mbse.validation.level3_dataflow import validate_dataflow
from agentic_mbse.validation.level4_constraints import analyze_constraints
from agentic_mbse.validation.level5_traceability import validate_traceability
from agentic_mbse.validation.level6_architecture import validate_architecture
from agentic_mbse.validation.runner import run_all_checks
from agentic_mbse.validation.session import (
    ValidationSession,
    active_session,
    constraint_facts,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

# Every fixture model directory the levels can be pointed at (each level globs **/*.sysml).
SESSION_FIXTURES = [
    "sample_models",
    # sump_pump's three variants declare the same packages, so loading the whole folder varies
    # from load to load with or without a session (backlog VALIDATE-SUMP-PUMP-NONDETERMINISM).
    "sump_pump/right",
    "sump_pump/seed",
    "sump_pump/wrong",
    "adr002_violations",
    "l6_negative",
    "l6_expose_consistency",
    "item4_subtype",
    "item9",
    "item12",
    "vacuous_asserted_gate",
    "constraint_fact_shapes",
    "distinctness",
    "l8_extractability",
    "semantic_evidence",
    "expression_ir",
]

LEVELS = {
    2: validate_structure,
    3: validate_dataflow,
    4: analyze_constraints,
    5: validate_traceability,
    6: validate_architecture,
}


def result_view(level: int, models: Path) -> Any:
    """What a level reports: success, issues, warnings, metrics and structured issues, or its raise."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            result = LEVELS[level](str(models))
    except Exception as error:  # a raise is a result too; it must match with the session
        return ("raised", type(error).__name__, str(error))
    return {
        "success": result.success,
        "issues": result.issues,
        "warnings": result.warnings,
        "metrics": result.metrics,
        "structured_issues": [i.model_dump(mode="json") for i in result.structured_issues],
    }


@pytest.mark.syside
@pytest.mark.parametrize("fixture", SESSION_FIXTURES)
def test_level_results_are_identical_with_and_without_session(fixture: str) -> None:
    """B5: L2-L6 run in order inside one session, each matching its own standalone run."""
    models = FIXTURES / fixture
    without = {level: result_view(level, models) for level in LEVELS}
    with ValidationSession() as session:
        with_session = {level: result_view(level, models) for level in LEVELS}
    for level in LEVELS:
        assert with_session[level] == without[level], f"Level {level} differs on {fixture}"
    assert session.model_loads == 1
    assert session.constraint_extractions <= 1


@pytest.mark.syside
def test_constraint_facts_extracted_once_per_model_in_a_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extractions: list[Any] = []
    loads: list[Any] = []
    real_extract = session_module.extract_identified_constraint_facts
    real_load = syside_adapter.SysideAdapter.load_model

    def counting_extract(model: Any) -> Any:
        extractions.append(model)
        return real_extract(model)

    def counting_load(paths: list[Path]) -> Any:
        loads.append(paths)
        return real_load(paths)

    monkeypatch.setattr(session_module, "extract_identified_constraint_facts", counting_extract)
    monkeypatch.setattr(syside_adapter.SysideAdapter, "load_model", staticmethod(counting_load))
    with contextlib.redirect_stdout(io.StringIO()):
        aggregated = run_all_checks(str(FIXTURES / "sump_pump" / "right"), fail_fast=False)

    assert [r.level for r in aggregated.results] == [1, 2, 3, 4, 5, 6]
    assert len(extractions) == 1  # L4 extracts; L6 reads the memo
    assert (
        len(loads) == 2
    )  # L1 loads on its own (it does not use load_sysml_model); L2-L6 share one
    assert active_session() is None


class _Model:
    """A stand-in model object; the memo only needs its identity."""


def test_memo_reraises_the_same_extraction_error_on_every_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = SemanticEvidenceError(
        SemanticEvidenceCode.OPERAND_ITERATION_FAILED, "fake extraction", "fake failure"
    )
    calls: list[Any] = []

    def failing_extract(model: Any) -> Any:
        calls.append(model)
        raise error

    monkeypatch.setattr(session_module, "extract_identified_constraint_facts", failing_extract)
    model = _Model()
    with ValidationSession() as session:
        for _ in range(3):
            with pytest.raises(SemanticEvidenceError) as raised:
                constraint_facts(model)
            assert raised.value is error
    assert len(calls) == 1
    assert session.constraint_extractions == 1


def test_memo_keys_each_model_separately(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        session_module, "extract_identified_constraint_facts", lambda m: ("facts", m)
    )
    first, second = _Model(), _Model()
    with ValidationSession() as session:
        assert constraint_facts(first) == ("facts", first)
        assert constraint_facts(second) == ("facts", second)
        assert constraint_facts(first) == ("facts", first)
    assert session.constraint_extractions == 2


def test_cached_load_is_dropped_when_a_file_size_or_mtime_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    loads: list[list[Path]] = []

    def fake_load(paths: list[Path]) -> tuple[object, list[str]]:
        loads.append(list(paths))
        return object(), []

    monkeypatch.setattr(syside_adapter.SysideAdapter, "load_model", staticmethod(fake_load))
    a = tmp_path / "a.sysml"
    b = tmp_path / "b.sysml"
    a.write_text("package A;")
    b.write_text("package B;")

    with ValidationSession() as session:
        first = load_sysml_model([a, b])
        assert load_sysml_model([a, b]) is first

        # Same size, new mtime.
        stat = a.stat()
        os.utime(a, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        second = load_sysml_model([a, b])
        assert second is not first
        assert load_sysml_model([a, b]) is second

        # New size, mtime restored to the cached value.
        stat = b.stat()
        b.write_text("package B2;")
        os.utime(b, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        third = load_sysml_model([a, b])
        assert third is not second

        # A different file list is its own load.
        assert load_sysml_model([a]) is not third

    assert session.model_loads == 4
    assert len(loads) == 4


def test_session_refuses_a_directory_path(tmp_path: Path) -> None:
    with ValidationSession(), pytest.raises(ValueError, match="is not a file"):
        load_sysml_model([tmp_path])


def test_sessions_do_not_nest() -> None:
    with ValidationSession(), pytest.raises(RuntimeError, match="already active"):
        with ValidationSession():
            pass
    assert active_session() is None


def test_no_session_means_todays_behaviour(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    loads: list[list[Path]] = []
    extractions: list[Any] = []

    def fake_load(paths: list[Path]) -> tuple[object, list[str]]:
        loads.append(list(paths))
        return object(), []

    def fake_extract(model: Any) -> object:
        extractions.append(model)
        return object()

    monkeypatch.setattr(syside_adapter.SysideAdapter, "load_model", staticmethod(fake_load))
    monkeypatch.setattr(session_module, "extract_identified_constraint_facts", fake_extract)
    file = tmp_path / "a.sysml"
    file.write_text("package A;")

    assert active_session() is None
    assert load_sysml_model([file]) is not load_sysml_model([file])
    model = _Model()
    assert constraint_facts(model) is not constraint_facts(model)
    assert len(loads) == 2
    assert len(extractions) == 2


@pytest.mark.syside
def test_extract_subset_facts_default_keyword_matches_todays_output() -> None:
    """I4: the new keyword defaults to today's extractor, and the shared memo gives the same facts."""
    default = inspect.signature(extract_subset_facts).parameters["constraint_facts"].default
    assert default is extract_identified_constraint_facts

    model, _ = load_sysml_model(discover_sysml_files(str(FIXTURES / "sump_pump" / "right")))
    today = extract_subset_facts(model)
    with ValidationSession() as session:
        shared = extract_subset_facts(model, constraint_facts=session.constraint_facts)
        assert constraint_facts(model) is shared.constraints
    assert shared == today
    assert today.constraints is not None
    assert session.constraint_extractions == 1
