"""Bounded negatives, and the refusal to search a request again without saying why.

A run that searched adequately and found nothing files a negative under the
request's key. The next `open_run` of the same request refuses until an
override reason is given, and the override is recorded on the negative.
"""

import json
from pathlib import Path

import pytest

from agentic_mbse.research.seam import (
    SeamHome,
    close,
    log_candidate,
    log_failure,
    log_search,
    open_run,
    request_key,
)

REQUEST = {
    "request_id": "REQ-001",
    "question": "What is the winding-pack current density of the widget coil?",
    "consumer": "WI-901",
    "gap_type": "unsourced_value",
    "priority": "P1",
    "where_to_look": ["example.org/widgets", "example.com/coils"],
    "limits": {"max_searches": 3, "max_captures": 2},
}


@pytest.fixture
def seam(tmp_path):
    root = tmp_path / "requests"
    root.mkdir()
    request_path = root / "REQ-001.json"
    request_path.write_text(json.dumps(REQUEST))
    return SeamHome(root=root), request_path


def _negative_for(home, request_path) -> dict:
    key = request_key(json.loads(request_path.read_text()))
    return json.loads((home.negatives / f"{key}.json").read_text())


def _dry_run(home, request_path, adequacy="exhausted"):
    opened = open_run(request_path, home=home)
    assert opened.outcome == "opened"
    log_search(opened.run_dir, "widget coil current density")
    log_candidate(opened.run_dir, "https://example.org/a", "rejected", "paywalled")
    # `closed`, not the default: a queued failure would make this run
    # OPERATOR_QUEUE and file no negative. The default is covered in `test_triage_queue.py`.
    log_failure(opened.run_dir, "https://example.org/b", "404", disposition="closed")
    return close(opened.run_dir, adequacy=adequacy)


def test_an_adequate_zero_source_run_files_every_negative_field(seam):
    home, request_path = seam
    returned = _dry_run(home, request_path)

    assert returned["class"] == "BOUNDED_NEGATIVE"
    negative = json.loads(Path(returned["negative"]).read_text())
    assert list(negative) == [
        "request_key",
        "request_id",
        "queries",
        "candidates",
        "failures",
        "adequacy",
        "reopened",
        "recorded_at",
    ]
    assert negative["queries"] == ["widget coil current density"]
    assert negative["candidates"] == [
        {"ref": "https://example.org/a", "triage": "rejected", "note": "paywalled"}
    ]
    assert negative["failures"] == [{"ref": "https://example.org/b", "reason": "404"}]
    assert negative["adequacy"] == "exhausted"
    assert negative["reopened"] == []


def test_a_limited_run_files_its_negative_as_limit_reached(seam):
    home, request_path = seam
    opened = open_run(request_path, home=home)
    for i in range(REQUEST["limits"]["max_searches"]):
        log_search(opened.run_dir, f"query {i}")

    returned = close(opened.run_dir, adequacy="exhausted")

    assert returned["limit_reached"] == "max_searches"
    assert _negative_for(home, request_path)["adequacy"] == "limit_reached"


def test_the_negative_is_keyed_on_the_request_not_the_clock(seam):
    home, request_path = seam
    _dry_run(home, request_path)
    negative = _negative_for(home, request_path)
    assert negative["request_key"] == request_key(REQUEST)
    assert "expires" not in negative and "ttl" not in negative


def test_a_changed_premise_is_a_different_request_key():
    other = dict(REQUEST, question="A different question entirely")
    assert request_key(other) != request_key(REQUEST)


def test_where_to_look_order_does_not_change_the_key():
    reordered = dict(REQUEST, where_to_look=list(reversed(REQUEST["where_to_look"])))
    assert request_key(reordered) == request_key(REQUEST)


def test_priority_and_limits_do_not_change_the_key():
    harder = dict(REQUEST, priority="P0", limits={"max_searches": 9, "max_captures": 9})
    assert request_key(harder) == request_key(REQUEST)


def test_a_second_open_refuses_without_an_override(seam):
    home, request_path = seam
    _dry_run(home, request_path)
    runs_before = sorted((home.runs / "REQ-001").iterdir())

    again = open_run(request_path, home=home)

    assert again.outcome == "answered_by_negative"
    assert again.run_dir is None
    assert request_key(REQUEST) in again.message
    assert "--override-reason" in again.message
    assert sorted((home.runs / "REQ-001").iterdir()) == runs_before


def test_an_override_proceeds_and_is_recorded_on_the_negative(seam):
    home, request_path = seam
    _dry_run(home, request_path)

    again = open_run(request_path, home=home, override_reason="new preprint 2026-08")
    assert again.outcome == "opened" and again.run_dir is not None

    negative = _negative_for(home, request_path)
    assert negative["reopened"][-1]["reason"] == "new preprint 2026-08"
    assert negative["reopened"][-1]["run"] == str(again.run_dir)
    run_meta = json.loads((again.run_dir / "run.json").read_text())
    assert run_meta["override_reason"] == "new preprint 2026-08"


def test_a_reopened_run_that_finds_nothing_keeps_the_reopen_history(seam):
    home, request_path = seam
    _dry_run(home, request_path)
    again = open_run(request_path, home=home, override_reason="new preprint 2026-08")

    close(again.run_dir)

    reopened = _negative_for(home, request_path)["reopened"]
    assert [entry["reason"] for entry in reopened] == ["new preprint 2026-08"]


def test_an_empty_override_reason_is_not_an_override(seam):
    home, request_path = seam
    _dry_run(home, request_path)
    again = open_run(request_path, home=home, override_reason="   ")
    assert again.outcome == "answered_by_negative"


def test_a_malformed_request_is_refused_before_any_run_directory_exists(seam, tmp_path):
    home, _ = seam
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"request_id": "REQ-002"}))

    opened = open_run(bad, home=home)

    assert opened.outcome == "invalid_request" and opened.run_dir is None
    assert opened.message == (
        "request is missing required field(s): question, consumer, gap_type, priority, "
        "where_to_look"
    )
    assert not home.runs.exists()


def test_an_unreadable_request_is_refused(seam, tmp_path):
    home, _ = seam
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")

    opened = open_run(bad, home=home)

    assert opened.outcome == "invalid_request"
    assert opened.message.startswith("request is unreadable: ")
    assert not home.runs.exists()
