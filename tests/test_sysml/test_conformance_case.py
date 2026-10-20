"""The packaged-case reader refuses a malformed case, and stored screen answers round-trip.

Pure: builds case directories under `tmp_path` and reads them with `load_case`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.conformance_case import (
    CASE_SCHEMA,
    CaseFormatError,
    CaseKind,
    load_case,
    packaged_case_ids,
    screen_answer_from_json,
    screen_answer_to_json,
)
from agentic_mbse.sysml.subset_profile import ContextId, Outcome, Verdict

FINDING = {
    "rule": "binding-source",
    "shape": "expression_source",
    "context": "owner_instantiated",
    "outcome": "refused",
    "subject": "fx::Site::t::xs",
    "line": 7,
}


def document(**changes: Any) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "schema": CASE_SCHEMA,
        "kind": "record",
        "construct": {"file": "model.sysml", "lines": [7, 7], "description": "a tuple actual"},
        "screen": {"verdict": "refused", "findings": [FINDING]},
        "agentic_site_witnesses": [],
        "provenance": {"note": "written for this test"},
    }
    doc.update(changes)
    return doc


def write_case(tmp_path: Path, doc: dict[str, Any], name: str = "a__b__owner_instantiated") -> Path:
    directory = tmp_path / name
    directory.mkdir()
    (directory / "model.sysml").write_text("package fx {}\n", encoding="utf-8")
    (directory / "case.json").write_text(json.dumps(doc), encoding="utf-8")
    return directory


def test_a_well_formed_case_loads(tmp_path: Path) -> None:
    case = load_case(write_case(tmp_path, document(provenance={"note": "n", "from_probe": "p"})))
    assert (case.case_id, case.kind, case.from_probe) == (
        "a__b__owner_instantiated",
        CaseKind.RECORD,
        "p",
    )
    assert case.construct.contains(7) and not case.construct.contains(8)
    (finding,) = case.screen.findings
    assert (finding.context, finding.outcome) == (ContextId.OWNER_INSTANTIATED, Outcome.REFUSED)
    assert case.screen.verdict is Verdict.REFUSED
    assert case.model_files() == (case.directory / "model.sysml",)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"schema": "subset-case/0"}, "schema"),
        ({"kind": "variation"}, "not a CaseKind"),
        ({"construct": {"file": "model.sysml", "lines": [8, 7], "description": "d"}}, "is after"),
        (
            {"construct": {"file": "other.sysml", "lines": [7, 7], "description": "d"}},
            "not a model file",
        ),
        ({"construct": {"file": "model.sysml", "lines": [7], "description": "d"}}, "first, last"),
        ({"provenance": {"note": ""}}, "non-empty text"),
        ({"observation": {}}, "unknown"),
        (
            {"screen": {"verdict": "clear", "findings": [{**FINDING, "context": "everywhere"}]}},
            "ContextId",
        ),
    ],
)
def test_a_malformed_case_is_refused(tmp_path: Path, changes: dict[str, Any], message: str) -> None:
    with pytest.raises(CaseFormatError, match=message):
        load_case(write_case(tmp_path, document(**changes)))


def test_stored_findings_must_be_in_sorted_order() -> None:
    later = {**FINDING, "subject": "fx::Site::u::xs", "line": 8}
    with pytest.raises(CaseFormatError, match="sorted"):
        screen_answer_from_json({"verdict": "refused", "findings": [later, FINDING]}, "here")


def test_a_stored_answer_round_trips() -> None:
    stored = {
        "verdict": "refused",
        "findings": [
            FINDING,
            {**FINDING, "subject": "<anonymous AssertConstraintUsage>", "line": None},
        ],
    }
    stored["findings"].sort(key=lambda f: (f["subject"], -1 if f["line"] is None else f["line"]))
    answer = screen_answer_from_json(stored, "here")
    assert screen_answer_to_json(answer) == stored


def test_the_package_ships_cases() -> None:
    assert len(packaged_case_ids()) >= 80
