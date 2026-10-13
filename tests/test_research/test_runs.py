"""The run directory: receipts, limits and the run log, as the registry and the bookkeeper share them."""

import json
from datetime import datetime, timezone

from agentic_mbse.research.runs import (
    append_run_log,
    is_run_dir,
    read_receipts,
    read_run_log,
    run_limits,
    write_receipt,
)

AT = datetime(2026, 10, 12, 9, 30, tzinfo=timezone.utc)


def _receipt(run_dir, outcome: str, at: datetime = AT):
    return write_receipt(
        run_dir,
        outcome=outcome,
        candidate="https://example.org/a",
        slug=None,
        path=None,
        source_id=None,
        triage="keeper",
        reason="",
        rule_id=None,
        captured=False,
        at=at,
    )


def test_receipts_are_numbered_in_write_order_and_read_oldest_first(run_dir):
    first = _receipt(run_dir, "capture_failed")
    second = _receipt(run_dir, "duplicate")
    assert (first.name, second.name) == ("20261012T093000-001.json", "20261012T093000-002.json")
    assert [(r["attempt"], r["outcome"]) for r in read_receipts(run_dir)] == [
        (1, "capture_failed"),
        (2, "duplicate"),
    ]


def test_a_receipt_creates_its_directory(tmp_path):
    _receipt(tmp_path, "registered")
    assert [r["outcome"] for r in read_receipts(tmp_path)] == ["registered"]


def test_a_run_without_receipts_has_none(tmp_path):
    assert read_receipts(tmp_path) == []


def test_run_limits_are_the_requests_declared_limits(make_run_dir):
    assert run_limits(make_run_dir(max_captures=1, max_searches=4)) == {
        "max_searches": 4,
        "max_captures": 1,
    }


def test_a_run_that_declared_no_limits_has_none(tmp_path):
    (tmp_path / "run.json").write_text(json.dumps({"request_id": "REQ-001"}))
    assert run_limits(tmp_path) == {}


def test_a_run_directory_is_one_with_a_run_record(run_dir, tmp_path):
    assert is_run_dir(run_dir)
    assert not is_run_dir(tmp_path / "elsewhere")


def test_the_run_log_appends_one_json_line_and_one_prose_line_per_step(run_dir):
    append_run_log(run_dir, {"kind": "search", "query": "widget"}, "- searched: `widget`")
    append_run_log(run_dir, {"kind": "fault", "reason": "x"}, "- **run fault**: x")
    assert read_run_log(run_dir) == [
        {"kind": "search", "query": "widget"},
        {"kind": "fault", "reason": "x"},
    ]
    assert (run_dir / "process_log.md").read_text() == "- searched: `widget`\n- **run fault**: x\n"


def test_a_run_with_no_log_has_no_entries(run_dir):
    assert read_run_log(run_dir) == []
