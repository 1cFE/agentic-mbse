"""`register` with a run directory: one receipt per returned outcome, and `max_captures` honoured.

A raised error writes no receipt: a commit that failed and was rolled back, or a
capture that overran its timeout, propagates to the caller as it always has.
"""

import importlib
import subprocess
from dataclasses import replace

import pytest

from agentic_mbse.research import (
    LocalPdfSource,
    RegistrationError,
    SourceMetadata,
    UrlSource,
    load_manifest_rows,
    register,
)
from agentic_mbse.research.runs import read_receipts
from tests.test_research.conftest import SEALED_TOKEN, FakeGuard

# The package attribute `register` is the function, so the module comes from importlib.
register_module = importlib.import_module("agentic_mbse.research.register")

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises receipts.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)

OUTCOMES = {
    "registered",
    "duplicate",
    "holdout_hit",
    "capture_failed",
    "precondition_failed",
    "limit_reached",
}


def _register(tree, run, url, title=None, **kwargs):
    metadata = METADATA if title is None else replace(METADATA, title=title)
    return register(UrlSource(url=url), metadata, paths=tree.paths, run_dir=run, **kwargs)


def test_a_receipt_is_written_for_a_successful_registration(local_site, knowledge_tree, run_dir):
    result = _register(knowledge_tree, run_dir, local_site.url("utf8.html"))

    (receipt,) = read_receipts(run_dir)
    assert receipt["outcome"] == "registered" == result.outcome
    assert receipt["attempt"] == 1
    assert receipt["candidate"] == local_site.url("utf8.html")
    assert receipt["slug"] == result.slug
    assert receipt["path"] == result.location
    assert receipt["source_id"] == result.source_id
    assert receipt["triage"] == "keeper"
    assert receipt["captured"] is True
    assert receipt["at"].endswith("+00:00")


def test_a_receipt_is_written_for_a_refusal_too(knowledge_tree, run_dir):
    result = _register(knowledge_tree, run_dir, "http://127.0.0.1:1/nothing.html")

    (receipt,) = read_receipts(run_dir)
    assert receipt["outcome"] == "capture_failed" == result.outcome
    assert receipt["reason"]
    assert receipt["slug"] is None
    assert receipt["captured"] is True


def test_a_pre_capture_refusal_does_not_spend_a_capture(knowledge_tree, run_dir):
    guard = FakeGuard(terms=(SEALED_TOKEN,))
    _register(
        knowledge_tree, run_dir, f"https://example.org/mirror/{SEALED_TOKEN}.pdf", guard=guard
    )

    (receipt,) = read_receipts(run_dir)
    assert receipt["outcome"] == "holdout_hit"
    assert receipt["captured"] is False
    assert receipt["rule_id"] == f"term:{SEALED_TOKEN}"
    assert receipt["reason"] == f"term:{SEALED_TOKEN} matched 1x"


def test_the_capture_after_the_limit_is_refused_and_named(local_site, knowledge_tree, make_run_dir):
    run = make_run_dir(max_captures=1)
    first = _register(knowledge_tree, run, local_site.url("utf8.html"))
    second = _register(knowledge_tree, run, local_site.url("latin1.html"), title="Cable Note")

    assert first.outcome == "registered"
    assert second.outcome == "limit_reached"
    assert second.reason == "run has spent its max_captures limit of 1"
    assert len(load_manifest_rows(knowledge_tree.paths)) == 1
    assert [r["outcome"] for r in read_receipts(run)] == ["registered", "limit_reached"]


def test_a_run_dir_is_optional_so_a_standalone_call_is_unaffected(local_site, knowledge_tree):
    result = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "registered"


def test_the_triage_decision_is_recorded(knowledge_tree, run_dir):
    _register(knowledge_tree, run_dir, "http://127.0.0.1:1/nothing.html", triage="rejected")
    (receipt,) = read_receipts(run_dir)
    assert receipt["triage"] == "rejected"


# --- one receipt per returned outcome, none per raised error ------------------------


def test_every_returned_outcome_writes_exactly_one_receipt(
    local_site, knowledge_tree, make_run_dir, tmp_path
):
    """Six attempts in one run, one for each outcome, leave six receipts in attempt order."""
    run = make_run_dir(max_captures=3)
    attempts = [
        lambda: _register(knowledge_tree, run, local_site.url("utf8.html")),
        lambda: _register(knowledge_tree, run, local_site.url("utf8.html")),
        lambda: _register(
            knowledge_tree,
            run,
            local_site.url("latin1.html"),
            guard=FakeGuard(terms=(SEALED_TOKEN,)),
            title=f"Notes on {SEALED_TOKEN}",
        ),
        lambda: _register(knowledge_tree, run, "http://127.0.0.1:1/nothing.html"),
        lambda: register(
            LocalPdfSource(path=tmp_path / "absent.pdf"),
            METADATA,
            paths=knowledge_tree.paths,
            run_dir=run,
        ),
        lambda: _register(knowledge_tree, run, local_site.url("latin1.html"), title="Cable Note"),
    ]
    outcomes = [attempt().outcome for attempt in attempts]

    assert set(outcomes) == OUTCOMES
    receipts = read_receipts(run)
    assert [r["outcome"] for r in receipts] == outcomes
    assert [r["attempt"] for r in receipts] == [1, 2, 3, 4, 5, 6]
    assert [r["captured"] for r in receipts] == [True, True, False, True, False, False]


def test_a_duplicate_of_a_row_with_a_source_id_counts_as_a_capture(
    local_site, knowledge_tree, run_dir
):
    """Found before any fetch, yet counted: the count has always worked this way."""
    _register(knowledge_tree, run_dir, local_site.url("utf8.html"))
    duplicate = _register(knowledge_tree, run_dir, local_site.url("utf8.html"))

    assert duplicate.outcome == "duplicate"
    assert duplicate.reason.startswith("already registered as")
    assert [r["captured"] for r in read_receipts(run_dir)] == [True, True]


def test_a_failed_commit_writes_no_receipt(local_site, knowledge_tree, run_dir, monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("injected failure at the index")

    monkeypatch.setattr(register_module, "insert_block", boom)

    with pytest.raises(RegistrationError):
        _register(knowledge_tree, run_dir, local_site.url("utf8.html"))

    assert read_receipts(run_dir) == []


def test_a_capture_timeout_writes_no_receipt(local_site, knowledge_tree, run_dir, monkeypatch):
    def overrun(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", overrun)

    with pytest.raises(subprocess.TimeoutExpired):
        _register(knowledge_tree, run_dir, local_site.url("utf8.html"))

    assert read_receipts(run_dir) == []
    assert not list(knowledge_tree.paths.staging.iterdir())
