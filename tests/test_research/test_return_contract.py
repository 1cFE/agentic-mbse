"""The return class is computed from receipts and the run log, not from the agent's report.

Covers every row of the class table, naming the limit a run stopped at, and
that what landed on disk outranks what the agent logged.
"""

import json

import pytest

from agentic_mbse.research.seam import (
    SeamError,
    SeamHome,
    close,
    log_candidate,
    log_failure,
    log_fault,
    log_search,
    open_run,
)

REQUEST = {
    "request_id": "REQ-100",
    "question": "Does the seam compute its own return class?",
    "consumer": "WI-901",
    "gap_type": "unsourced_value",
    "priority": "P1",
    "where_to_look": ["the receipts"],
    "limits": {"max_searches": 2, "max_captures": 2},
}


@pytest.fixture
def opened(tmp_path):
    root = tmp_path / "requests"
    root.mkdir()
    (root / "REQ-100.json").write_text(json.dumps(REQUEST))
    home = SeamHome(root=root)
    result = open_run(root / "REQ-100.json", home=home)
    assert result.outcome == "opened"
    return home, result.run_dir


def _receipt(
    run_dir,
    outcome,
    *,
    triage="keeper",
    slug=None,
    path=None,
    source_id=None,
    rule_id=None,
    reason="",
    captured=True,
    scope="candidate",
):
    """A receipt as `register` writes one, plus a field no reader knows, which `close` ignores."""
    directory = run_dir / "receipts"
    directory.mkdir(exist_ok=True)
    attempt = len(list(directory.iterdir())) + 1
    (directory / f"20260825T000000-{attempt:03d}.json").write_text(
        json.dumps(
            {
                "attempt": attempt,
                "outcome": outcome,
                "candidate": f"https://example.org/{attempt}",
                "slug": slug,
                "path": path,
                "source_id": source_id,
                "triage": triage,
                "reason": reason,
                "rule_id": rule_id,
                "captured": captured,
                "scope": scope,
                "at": "2026-08-25T00:00:00+00:00",
            }
        )
    )


CLASS_TABLE_ROWS = [
    ("any registered", [("registered", "keeper")], "REGISTERED"),
    (
        "registered beside a queued candidate",
        [("registered", "keeper"), ("holdout_hit", "keeper")],
        "REGISTERED",
    ),
    ("keeper duplicate only", [("duplicate", "keeper")], "REGISTERED"),
    ("rejected duplicate only", [("duplicate", "rejected")], "BOUNDED_NEGATIVE"),
    ("holdout hit only", [("holdout_hit", "keeper")], "OPERATOR_QUEUE"),
    ("capture failure only", [("capture_failed", "keeper")], "OPERATOR_QUEUE"),
    ("precondition failure only", [("precondition_failed", "keeper")], "OPERATOR_QUEUE"),
    ("limit reached only", [("limit_reached", "keeper")], "BOUNDED_NEGATIVE"),
    ("no receipts at all", [], "BOUNDED_NEGATIVE"),
]


@pytest.mark.parametrize(
    ("label", "receipts", "expected"), CLASS_TABLE_ROWS, ids=[row[0] for row in CLASS_TABLE_ROWS]
)
def test_the_class_is_computed_from_receipts(opened, label, receipts, expected):
    _, run_dir = opened
    for outcome, triage in receipts:
        found = outcome in {"registered", "duplicate"}
        _receipt(
            run_dir,
            outcome,
            triage=triage,
            slug="s" if found else None,
            path="knowledge/sources/s/" if found else None,
            source_id="a" * 64 if found else None,
        )
    assert close(run_dir)["class"] == expected


def test_a_keeper_duplicate_is_marked_pre_existing(opened):
    _, run_dir = opened
    _receipt(
        run_dir, "duplicate", slug="widget", path="knowledge/sources/widget/", source_id="a" * 64
    )
    returned = close(run_dir)
    assert returned["class"] == "REGISTERED"
    assert returned["registered"] == [
        {
            "slug": "widget",
            "path": "knowledge/sources/widget/",
            "source_id": "a" * 64,
            "pre_existing": True,
        }
    ]


def test_a_registration_is_not_marked_pre_existing(opened):
    _, run_dir = opened
    _receipt(
        run_dir, "registered", slug="widget", path="knowledge/sources/widget/", source_id="b" * 64
    )
    assert close(run_dir)["registered"][0]["pre_existing"] is False


def test_queued_candidates_ride_inside_a_registered_return(opened):
    _, run_dir = opened
    _receipt(
        run_dir, "registered", slug="widget", path="knowledge/sources/widget/", source_id="b" * 64
    )
    _receipt(run_dir, "holdout_hit", rule_id="term:example", reason="term:example matched 1x")
    returned = close(run_dir)
    assert returned["class"] == "REGISTERED"
    assert returned["queued"] == [
        {"candidate": "https://example.org/2", "reason": "term:example matched 1x"}
    ]


def test_a_queued_receipt_without_a_reason_is_queued_under_its_outcome(opened):
    _, run_dir = opened
    _receipt(run_dir, "capture_failed", reason="")
    assert close(run_dir)["queued"] == [
        {"candidate": "https://example.org/1", "reason": "capture_failed"}
    ]


def test_an_agent_claim_of_a_negative_is_overridden_by_a_registered_receipt(opened):
    """What landed on disk is the truth; the agent's log entry is advisory."""
    _, run_dir = opened
    log_candidate(run_dir, "https://example.org/1", "rejected", "nothing usable")
    _receipt(
        run_dir, "registered", slug="widget", path="knowledge/sources/widget/", source_id="b" * 64
    )
    returned = close(run_dir, adequacy="exhausted")
    assert returned["class"] == "REGISTERED"
    assert returned["negative"] is None


def test_a_limit_reached_receipt_names_the_limit(opened):
    _, run_dir = opened
    _receipt(
        run_dir,
        "limit_reached",
        reason="run has spent its max_captures limit of 2",
        captured=False,
    )
    returned = close(run_dir)
    assert returned["class"] == "BOUNDED_NEGATIVE"
    assert returned["limit_reached"] == "max_captures"


def test_a_declared_search_limit_is_named_at_close(opened):
    _, run_dir = opened
    for i in range(REQUEST["limits"]["max_searches"]):
        log_search(run_dir, f"query {i}")
    returned = close(run_dir)
    assert returned["limit_reached"] == "max_searches"


def test_a_search_count_under_the_limit_names_no_limit(opened):
    _, run_dir = opened
    log_search(run_dir, "query 0")
    assert close(run_dir)["limit_reached"] is None


def test_a_run_scoped_fault_with_no_candidates_is_a_blocker(opened):
    _, run_dir = opened
    log_fault(run_dir, "registry is not writable")
    returned = close(run_dir)
    assert returned["class"] == "BLOCKER"
    assert returned["reason"] == "registry is not writable"
    assert returned["negative"] is None


def test_a_queued_candidate_outranks_a_run_scoped_fault(opened):
    """A person can still resolve the named candidate, so the run is not a blocker."""
    _, run_dir = opened
    log_failure(run_dir, "https://example.org/b", "paywalled")
    log_fault(run_dir, "registry is not writable")
    returned = close(run_dir)
    assert returned["class"] == "OPERATOR_QUEUE"
    assert returned["reason"] == "registry is not writable"


def test_a_run_scoped_fault_after_a_registration_stays_registered(opened):
    _, run_dir = opened
    _receipt(
        run_dir, "registered", slug="widget", path="knowledge/sources/widget/", source_id="b" * 64
    )
    log_fault(run_dir, "registry went read-only afterwards")
    returned = close(run_dir)
    assert returned["class"] == "REGISTERED"
    assert returned["reason"] == "registry went read-only afterwards"


def test_a_run_scoped_fault_after_a_refused_receipt_is_a_negative_not_a_blocker(opened):
    _, run_dir = opened
    _receipt(run_dir, "duplicate", triage="rejected", slug="s", path="knowledge/sources/s/")
    log_fault(run_dir, "registry went read-only afterwards")
    returned = close(run_dir)
    assert returned["class"] == "BOUNDED_NEGATIVE"
    assert returned["reason"] == "registry went read-only afterwards"


def test_every_return_resolves_to_native_references(opened):
    """A reader reaches the evidence without reconstructing what the agent did."""
    _, run_dir = opened
    _receipt(
        run_dir, "registered", slug="widget", path="knowledge/sources/widget/", source_id="b" * 64
    )
    returned = close(run_dir)
    assert list(returned) == [
        "request_id",
        "run",
        "class",
        "registered",
        "queued",
        "negative",
        "limit_reached",
        "reason",
    ]
    assert returned["request_id"] == "REQ-100"
    assert returned["run"] == str(run_dir)
    assert returned["registered"][0]["path"].startswith("knowledge/sources/")
    assert json.loads((run_dir / "return.json").read_text()) == returned


def test_close_refuses_a_directory_that_is_not_a_run(tmp_path):
    with pytest.raises(SeamError, match=r"is not a run directory — no run\.json$"):
        close(tmp_path)
    assert not (tmp_path / "return.json").exists()


def test_logging_refuses_a_directory_that_is_not_a_run(tmp_path):
    with pytest.raises(SeamError, match=r"is not a run directory — no run\.json$"):
        log_search(tmp_path, "query")
    assert list(tmp_path.iterdir()) == []
