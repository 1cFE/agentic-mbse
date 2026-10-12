"""A candidate blocked at triage reaches OPERATOR_QUEUE.

A paywall, a login wall or a repeated fetch failure is found at triage, before
anything is worth calling `register` on, so it leaves no receipt. Reading the
class from receipts alone would close such a run `BOUNDED_NEGATIVE` and file a
negative that blocks the request, burying a named candidate a person could
still get under "nothing there". The run log's failures carry it instead.
"""

import json

import pytest

from agentic_mbse.cli import main
from agentic_mbse.research.seam import (
    SeamError,
    SeamHome,
    close,
    log_candidate,
    log_failure,
    log_search,
    open_run,
    request_key,
)

REQUEST = {
    "request_id": "REQ-200",
    "question": "Where is the paywalled widget conductor paper?",
    "consumer": "WI-901",
    "gap_type": "unsourced_value",
    "priority": "P1",
    "where_to_look": ["a publisher behind a paywall"],
    "limits": {"max_searches": 3, "max_captures": 2},
}


@pytest.fixture
def opened(tmp_path):
    """A run opened in a project at `tmp_path`, so the CLI can run from its root."""
    root = tmp_path / "knowledge" / "research" / "requests"
    root.mkdir(parents=True)
    (root / "REQ-200.json").write_text(json.dumps(REQUEST))
    home = SeamHome(root=root)
    result = open_run(root / "REQ-200.json", home=home)
    assert result.outcome == "opened"
    return home, result.run_dir


def _negative_path(home):
    return home.negatives / f"{request_key(REQUEST)}.json"


def _write_receipt(run_dir, outcome, candidate, **fields):
    receipts = run_dir / "receipts"
    receipts.mkdir(exist_ok=True)
    (receipts / "20260826T000000-001.json").write_text(
        json.dumps(
            {
                "attempt": 1,
                "outcome": outcome,
                "candidate": candidate,
                "slug": None,
                "path": None,
                "source_id": None,
                "triage": "keeper",
                "reason": "",
                "rule_id": None,
                "captured": False,
                "at": "2026-08-26T00:00:00+00:00",
            }
            | fields
        )
    )


def test_the_guides_paywall_sequence_closes_operator_queue(opened):
    _, run_dir = opened
    log_search(run_dir, "widget conductor paper")
    log_failure(run_dir, "https://example.org/b", "paywalled")

    returned = close(run_dir)

    assert returned["class"] == "OPERATOR_QUEUE"
    assert returned["queued"] == [{"candidate": "https://example.org/b", "reason": "paywalled"}]
    assert returned["registered"] == []


def test_no_negative_is_filed_when_a_candidate_is_queued(opened):
    """Negatives stop fruitless repeats; they must not bury a source behind a paywall."""
    home, run_dir = opened
    log_failure(run_dir, "https://example.org/b", "paywalled")

    returned = close(run_dir)

    assert returned["negative"] is None
    assert not _negative_path(home).exists()


def test_a_queued_run_does_not_block_the_next_run(opened):
    """The request stays searchable while a person works the queue."""
    home, run_dir = opened
    log_failure(run_dir, "https://example.org/b", "login wall")
    assert close(run_dir)["class"] == "OPERATOR_QUEUE"

    again = open_run(home.root / "REQ-200.json", home=home)
    assert again.outcome == "opened", again.message


@pytest.mark.parametrize(
    "reason", ["paywalled", "login wall required", "repeated fetch failure after 3 attempts"]
)
def test_every_named_queue_reason_queues(opened, reason):
    _, run_dir = opened
    log_failure(run_dir, "https://example.org/b", reason)
    returned = close(run_dir)
    assert returned["class"] == "OPERATOR_QUEUE"
    assert returned["queued"][0]["reason"] == reason


def test_a_closed_failure_stays_in_the_negative_and_does_not_queue(opened):
    """A dead link nobody should chase is recorded, not routed to a person."""
    home, run_dir = opened
    log_search(run_dir, "widget conductor paper")
    log_failure(run_dir, "https://example.org/gone", "404, link is dead", disposition="closed")

    returned = close(run_dir)

    assert returned["class"] == "BOUNDED_NEGATIVE"
    assert returned["queued"] == []
    negative = json.loads(_negative_path(home).read_text())
    assert negative["failures"] == [
        {"ref": "https://example.org/gone", "reason": "404, link is dead"}
    ]


def test_a_failure_logged_without_a_disposition_queues(opened):
    """A run log written before dispositions existed reads its failures as queued."""
    _, run_dir = opened
    with open(run_dir / "run.jsonl", "a") as handle:
        handle.write(
            json.dumps({"kind": "failure", "ref": "https://example.org/b", "reason": "paywalled"})
            + "\n"
        )
    assert close(run_dir)["class"] == "OPERATOR_QUEUE"


def test_a_rejected_candidate_is_not_a_queue_entry(opened):
    """Triaged and judged useless is not the same event as could not be brought in."""
    _, run_dir = opened
    log_candidate(run_dir, "https://example.org/c", "rejected", "off topic")

    returned = close(run_dir)

    assert returned["class"] == "BOUNDED_NEGATIVE"
    assert returned["queued"] == []


def test_a_registration_still_outranks_a_queued_candidate(opened):
    """The queue rides inside a REGISTERED return."""
    _, run_dir = opened
    log_failure(run_dir, "https://example.org/b", "paywalled")
    _write_receipt(
        run_dir,
        "registered",
        "https://example.org/a",
        slug="widget",
        path="knowledge/sources/widget/",
        source_id="a" * 64,
        captured=True,
    )

    returned = close(run_dir)

    assert returned["class"] == "REGISTERED"
    assert len(returned["queued"]) == 1
    assert returned["negative"] is None


def test_receipt_and_triage_queue_entries_share_one_shape(opened):
    """Both kinds of queue entry read the same to the operator."""
    _, run_dir = opened
    log_failure(run_dir, "https://example.org/b", "paywalled")
    _write_receipt(
        run_dir,
        "holdout_hit",
        "https://example.org/h",
        reason="term:example matched 1x",
        rule_id="term:example",
    )

    returned = close(run_dir)

    assert returned["class"] == "OPERATOR_QUEUE"
    assert returned["queued"] == [
        {"candidate": "https://example.org/h", "reason": "term:example matched 1x"},
        {"candidate": "https://example.org/b", "reason": "paywalled"},
    ]


def test_an_unknown_disposition_is_refused(opened):
    _, run_dir = opened
    with pytest.raises(SeamError, match="disposition must be one of"):
        log_failure(run_dir, "https://example.org/b", "paywalled", disposition="parked")
    assert (run_dir / "run.jsonl").read_text() == ""


# --- the same through `agentic-mbse research log` --------------------------------------


def test_the_cli_defaults_a_failure_to_queued(opened, tmp_path, monkeypatch):
    _, run_dir = opened
    monkeypatch.chdir(tmp_path)
    assert (
        main(
            [
                "research",
                "log",
                str(run_dir),
                "--failure",
                "https://example.org/b",
                "--reason",
                "paywalled",
            ]
        )
        == 0
    )
    assert close(run_dir)["class"] == "OPERATOR_QUEUE"


def test_the_cli_can_close_a_failure_explicitly(opened, tmp_path, monkeypatch):
    _, run_dir = opened
    monkeypatch.chdir(tmp_path)
    assert (
        main(
            [
                "research",
                "log",
                str(run_dir),
                "--failure",
                "https://example.org/gone",
                "--reason",
                "404",
                "--disposition",
                "closed",
            ]
        )
        == 0
    )
    assert close(run_dir)["class"] == "BOUNDED_NEGATIVE"
