"""`agentic-mbse research`: the nine subcommands, run from a project root.

Each test runs the CLI through `agentic_mbse.cli.main` with the current
directory at a fresh target's project root, as an agent's Bash call would. It
checks what is printed, the exit code, and what the call wrote.
"""

import importlib
import json
import re
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from agentic_mbse.cli import get_template_path, main
from agentic_mbse.research import SourceMetadata, UrlSource, load_manifest_rows, register
from agentic_mbse.research.index import HandCuratedEntry, add_entry, insert_block, parse_index
from tests.test_research.conftest import (
    GUARD_FILE_SOURCE,
    NO_GUARD,
    SEALED_TOKEN,
    assert_nothing_written,
    write_research_config,
)

register_module = importlib.import_module("agentic_mbse.research.register")
retire_module = importlib.import_module("agentic_mbse.research.retire")

SUBCOMMANDS = (
    "open",
    "log",
    "close",
    "register",
    "retire",
    "verify",
    "sources",
    "add-entry",
    "remove-entry",
)

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the CLI.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)
METADATA_FLAGS = (
    "--title",
    METADATA.title,
    "--use-for",
    METADATA.use_for,
    "--validation",
    METADATA.validation,
    "--caveat",
    METADATA.caveat,
)
REASON = "Captured content is a fixture, not a paper (test)."

REQUEST_PATH = "knowledge/research/requests/REQ-001.json"
REQUEST = {
    "request_id": "REQ-001",
    "question": "What is the winding-pack geometry of the widget coil?",
    "consumer": "WI-901",
    "gap_type": "unsourced_value",
    "priority": "P2",
    "where_to_look": ["the loopback fixture site"],
    "limits": {"max_searches": 2, "max_captures": 1},
}

ENTRY_FLAGS = (
    "--title",
    "Reference Code",
    "--type",
    "codebase",
    "--location",
    "/srv/reference",
    "--use-for",
    "Cross-checking widget sizing formulas",
    "--validation",
    "N/A",
)


def research(*argv: str) -> int:
    return main(["research", *argv])


@pytest.fixture
def project(knowledge_tree, monkeypatch):
    """A fresh target, with the current directory at its project root as the CLI requires."""
    monkeypatch.chdir(knowledge_tree.paths.project_root)
    return knowledge_tree


def _configure_guard(project) -> None:
    """Name the conftest's guard file, which bars `SEALED_TOKEN`, in the project's `pyproject.toml`."""
    root = project.paths.project_root
    (root / "guard.py").write_text(GUARD_FILE_SOURCE)
    write_research_config(root, 'holdout-guard = "guard.py"')


def _write_request(request: dict = REQUEST) -> str:
    path = Path(REQUEST_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(request))
    return REQUEST_PATH


def _open(capsys) -> str:
    """Open a run on `REQUEST` through the CLI and return the run directory it printed."""
    assert research("open", _write_request()) == 0
    message, run_dir = capsys.readouterr().out.splitlines()
    assert message == f"run opened at {run_dir}"
    return run_dir


def _one_error_line(capsys) -> str:
    """The single stderr line of a refused call, which printed nothing to stdout."""
    captured = capsys.readouterr()
    assert captured.out == ""
    (line,) = captured.err.splitlines()
    return line


# --- the surface ---------------------------------------------------------------------


def test_help_lists_the_nine_subcommands(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["research", "--help"])
    assert exit_info.value.code == 0
    assert "{" + ",".join(SUBCOMMANDS) + "}" in capsys.readouterr().out


def test_no_subcommand_is_a_usage_error(capsys):
    assert research() == 2
    assert _one_error_line(capsys).startswith("Error: No operation specified.")


VALID_CALLS = {
    "open": ("open", REQUEST_PATH),
    "log": ("log", "knowledge/research/requests/runs/REQ-001/x", "--search", "q"),
    "close": ("close", "knowledge/research/requests/runs/REQ-001/x"),
    "register": ("register", "--url", "http://127.0.0.1:9/x.html", *METADATA_FLAGS),
    "retire": ("retire", "--slug", "widget_coil_note", "--reason", REASON),
    "verify": ("verify",),
    "sources": ("sources",),
    "add-entry": ("add-entry", *ENTRY_FLAGS),
    "remove-entry": ("remove-entry", "--title", "Reference Code"),
}


@pytest.mark.parametrize("argv", VALID_CALLS.values(), ids=VALID_CALLS.keys())
def test_outside_a_project_root_every_subcommand_refuses_in_one_line(
    argv, tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)  # no knowledge/ here
    assert research(*argv) == 1
    assert _one_error_line(capsys) == (
        "Error: run 'agentic-mbse research' from the project root; "
        f"there is no knowledge/ directory in {tmp_path}"
    )
    assert list(tmp_path.iterdir()) == []


def test_inside_the_knowledge_directory_is_not_the_project_root(project, monkeypatch, capsys):
    """The root is never searched for upwards, so recorded paths always start at it."""
    monkeypatch.chdir(project.root)
    assert research("verify") == 1
    assert _one_error_line(capsys).endswith(f"there is no knowledge/ directory in {project.root}")


# --- open, log, close ------------------------------------------------------------------


def test_open_prints_and_records_paths_relative_to_the_project_root(project, capsys):
    run_dir = _open(capsys)

    assert run_dir.startswith("knowledge/research/requests/runs/REQ-001/")
    meta = json.loads((Path(run_dir) / "run.json").read_text())
    assert meta["request_path"] == REQUEST_PATH
    assert meta["home_root"] == "knowledge/research/requests"


def test_open_exits_2_on_a_malformed_request(project, capsys):
    request = {key: value for key, value in REQUEST.items() if key != "consumer"}
    assert research("open", _write_request(request)) == 2
    assert capsys.readouterr().out == "request is missing required field(s): consumer\n"
    assert not Path("knowledge/research/requests/runs").exists()


def test_open_exits_3_on_a_request_a_negative_answers(project, capsys):
    run_dir = _open(capsys)
    assert research("log", run_dir, "--search", "widget coil geometry") == 0
    assert research("close", run_dir) == 0
    negative = json.loads(capsys.readouterr().out)["negative"]
    assert negative.startswith("knowledge/research/requests/negatives/")

    assert research("open", REQUEST_PATH) == 3
    (message,) = capsys.readouterr().out.splitlines()
    assert message.startswith("a bounded negative already answers this request")
    assert negative in message

    assert research("open", REQUEST_PATH, "--override-reason", "a new preprint") == 0


def test_log_records_each_kind_of_step(project, capsys):
    run_dir = _open(capsys)
    calls = (
        ("--search", "widget coil geometry"),
        ("--candidate", "https://example.org/a", "--triage", "rejected", "--note", "off topic"),
        ("--failure", "https://example.org/b", "--reason", "paywalled"),
        ("--fault", "registry is not writable"),
    )
    for flags in calls:
        assert research("log", run_dir, *flags) == 0

    logged = [json.loads(line) for line in (Path(run_dir) / "run.jsonl").read_text().splitlines()]
    assert [entry["kind"] for entry in logged] == ["search", "candidate", "failure", "fault"]
    assert logged[2]["disposition"] == "queued"


@pytest.mark.parametrize(
    ("flags", "error"),
    [
        (("--candidate", "https://example.org/a"), "Error: --candidate requires --triage"),
        (("--failure", "https://example.org/b"), "Error: --failure requires --reason"),
    ],
)
def test_log_without_its_companion_flag_exits_2_and_records_nothing(project, capsys, flags, error):
    run_dir = _open(capsys)
    assert research("log", run_dir, *flags) == 2
    assert _one_error_line(capsys) == error
    assert (Path(run_dir) / "run.jsonl").read_text() == ""


@pytest.mark.parametrize("operation", ["log", "close"])
def test_a_directory_that_is_not_a_run_is_one_error_line(project, capsys, operation):
    not_a_run = Path("knowledge/research/requests/runs/REQ-001/made-up")
    not_a_run.mkdir(parents=True)
    argv = (
        ("log", str(not_a_run), "--search", "q")
        if operation == "log"
        else ("close", str(not_a_run))
    )

    assert research(*argv) == 1
    assert _one_error_line(capsys) == f"Error: {not_a_run} is not a run directory — no run.json"
    assert list(not_a_run.iterdir()) == []


def test_close_prints_the_return_it_writes(project, capsys):
    run_dir = _open(capsys)
    assert (
        research("log", run_dir, "--failure", "https://example.org/b", "--reason", "paywalled") == 0
    )

    assert research("close", run_dir) == 0

    returned = json.loads(capsys.readouterr().out)
    assert returned == json.loads((Path(run_dir) / "return.json").read_text())
    assert returned["class"] == "OPERATOR_QUEUE"
    assert returned["run"] == run_dir


def test_a_whole_run_goes_through_the_cli(project, local_site, capsys):
    url = local_site.url("utf8.html")
    run_dir = _open(capsys)
    assert research("log", run_dir, "--search", "widget coil note") == 0
    assert research("log", run_dir, "--candidate", url, "--triage", "keeper") == 0
    assert research("register", "--url", url, *METADATA_FLAGS, "--run", run_dir) == 0
    registered = json.loads(capsys.readouterr().out)

    assert research("close", run_dir) == 0

    returned = json.loads(capsys.readouterr().out)
    assert returned["class"] == "REGISTERED"
    assert returned["registered"] == [
        {
            "slug": "widget_coil_note",
            "path": "knowledge/sources/widget_coil_note/",
            "source_id": registered["source_id"],
            "pre_existing": False,
        }
    ]
    assert len(list((Path(run_dir) / "receipts").iterdir())) == 1
    assert research("verify") == 0


# --- register --------------------------------------------------------------------------


def test_register_prints_the_registration_fields(project, local_site, capsys):
    assert research("register", "--url", local_site.url("utf8.html"), *METADATA_FLAGS) == 0

    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == [
        "outcome",
        "slug",
        "location",
        "source_id",
        "raw_sha256",
        "raw_artifact_sha256",
        "extract_sha256",
    ]
    assert payload["outcome"] == "registered"
    assert payload["location"] == "knowledge/sources/widget_coil_note/"
    assert payload["raw_sha256"] == payload["source_id"]
    assert load_manifest_rows(project.paths)[0]["slug"] == "widget_coil_note"


def test_a_refused_registration_exits_1_and_prints_why(project, local_site, capsys):
    url = local_site.url("utf8.html")
    first = register(UrlSource(url=url), METADATA, paths=project.paths, guard=NO_GUARD)

    assert research("register", "--url", url, *METADATA_FLAGS) == 1

    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == ["outcome", "reason", "source_id", "existing_slug", "existing_path"]
    assert payload["outcome"] == "duplicate"
    assert payload["existing_slug"] == first.slug


def test_a_holdout_hit_prints_its_rule_and_offsets(project, local_site, capsys):
    _configure_guard(project)

    assert research("register", "--url", local_site.url("marker.html"), *METADATA_FLAGS) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "holdout_hit"
    assert payload["rule_id"] == f"term:{SEALED_TOKEN}"
    assert payload["offsets"] and all(isinstance(offset, int) for offset in payload["offsets"])
    assert_nothing_written(project)


def test_no_flag_waives_a_holdout_hit(project, local_site, capsys):
    _configure_guard(project)
    with pytest.raises(SystemExit) as exit_info:
        research(
            "register", "--url", local_site.url("marker.html"), *METADATA_FLAGS, "--holdout-ack"
        )
    assert exit_info.value.code == 2
    assert "unrecognized arguments: --holdout-ack" in capsys.readouterr().err
    assert_nothing_written(project)


def test_register_takes_only_its_documented_flags(capsys):
    """No flag, under any name, can carry a candidate past the guard."""
    with pytest.raises(SystemExit):
        main(["research", "register", "--help"])
    assert set(re.findall(r"--[a-z][a-z-]*", capsys.readouterr().out)) == {
        "--help",
        "--url",
        "--local-pdf",
        "--title",
        "--use-for",
        "--validation",
        "--caveat",
        "--budget",
        "--run",
        "--triage",
    }


def test_register_refuses_a_run_that_open_did_not_create(project, local_site, capsys):
    not_a_run = Path("knowledge/research/requests/runs/REQ-001/made-up")
    not_a_run.mkdir(parents=True)

    code = research(
        "register", "--url", local_site.url("utf8.html"), *METADATA_FLAGS, "--run", str(not_a_run)
    )

    assert code == 1
    assert _one_error_line(capsys) == f"Error: {not_a_run} is not a run directory — no run.json"
    assert list(not_a_run.iterdir()) == []
    assert_nothing_written(project)


def test_a_failed_commit_is_one_error_line_and_leaves_no_receipt(
    project, local_site, capsys, monkeypatch
):
    url = local_site.url("utf8.html")
    run_dir = _open(capsys)

    def disk_full(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(register_module, "insert_block", disk_full)

    assert research("register", "--url", url, *METADATA_FLAGS, "--run", run_dir) == 1
    assert _one_error_line(capsys) == f"Error: commit failed for {url}: disk full"
    assert list((Path(run_dir) / "receipts").iterdir()) == []
    assert_nothing_written(project)


def test_a_capture_timeout_is_one_error_line_and_leaves_no_receipt(
    project, local_site, capsys, monkeypatch
):
    run_dir = _open(capsys)

    def overrun(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr("agentic_mbse.research.capture.subprocess.run", overrun)

    code = research(
        "register", "--url", local_site.url("utf8.html"), *METADATA_FLAGS, "--run", run_dir
    )

    assert code == 1
    line = _one_error_line(capsys)
    assert line.startswith("Error: capture timed out, nothing registered: Command ")
    assert line.endswith("timed out after 900 seconds")
    assert list((Path(run_dir) / "receipts").iterdir()) == []
    assert_nothing_written(project)


# --- retire ----------------------------------------------------------------------------


@pytest.fixture
def two_sources(project, local_site):
    """Two registered entries, registered through the Python API."""
    kept = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=project.paths, guard=NO_GUARD
    )
    gone = register(
        UrlSource(url=local_site.url("latin1.html")),
        replace(METADATA, title="Cable Note"),
        paths=project.paths,
        guard=NO_GUARD,
    )
    assert kept.outcome == gone.outcome == "registered"
    return kept, gone


def test_retire_prints_the_removal_and_the_retired_line(project, two_sources, capsys):
    _, gone = two_sources
    row = next(r for r in load_manifest_rows(project.paths) if r["slug"] == gone.slug)
    blocks = parse_index(project.index.read_text(), project_root=project.paths.project_root)
    (block,) = [b for b in blocks if b.slug == gone.slug]

    assert research("retire", "--slug", gone.slug, "--reason", REASON) == 0

    retired_line = project.paths.retired.read_text().rstrip("\n")
    assert capsys.readouterr().out == "\n".join(
        [
            f"retired {gone.slug}",
            f"  removed manifest row:   {json.dumps(row)}",
            f"  removed source dir:     knowledge/sources/{gone.slug}/",
            "  removed raw copy:       (none stored outside the source dir)",
            "  removed index block:",
            *[f"    {line}" for line in block.text.splitlines()],
            "  RETIRED.jsonl line:",
            f"    {retired_line}",
            "",
        ]
    )
    assert json.loads(retired_line)["reason"] == REASON


def test_a_retire_refusal_exits_1_with_the_reason(project, two_sources, capsys):
    assert research("retire", "--slug", "no_such_source", "--reason", REASON) == 1
    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == ["outcome", "reason"]
    assert payload["outcome"] == "unknown_slug"
    assert not project.paths.retired.exists()


def test_a_retire_holdout_hit_prints_its_rule_and_offsets(project, capsys):
    _configure_guard(project)
    assert research("retire", "--slug", SEALED_TOKEN, "--reason", REASON) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "outcome": "holdout_hit",
        "reason": payload["reason"],
        "rule_id": f"term:{SEALED_TOKEN}",
        "offsets": [0],
    }


def test_a_referenced_source_prints_what_depends_on_it(project, two_sources, capsys):
    _, gone = two_sources
    entry = HandCuratedEntry(
        title="Coil Review",
        type="documentation",
        location="docs/coil_review.md",
        use_for=f"Reads {gone.slug} alongside the review",
        validation="N/A",
    )
    assert add_entry(entry, paths=project.paths, guard=NO_GUARD).outcome == "added"

    assert research("retire", "--slug", gone.slug, "--reason", REASON) == 1

    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == ["outcome", "reason", "references"]
    assert payload["outcome"] == "referenced"
    assert payload["references"] == ["SOURCE_INDEX.md block (### Coil Review)"]


def test_a_failed_retire_rung_is_one_error_line(project, two_sources, capsys, monkeypatch):
    _, gone = two_sources

    def disk_full(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(retire_module, "_append_retired_line", disk_full)

    assert research("retire", "--slug", gone.slug, "--reason", REASON) == 1
    assert _one_error_line(capsys) == f"Error: retire failed for {gone.slug}: disk full"
    assert (project.sources / gone.slug).is_dir()


# --- verify ----------------------------------------------------------------------------


def test_verify_on_a_clean_registry_prints_only_the_summary(project, capsys):
    assert research("verify") == 0
    assert capsys.readouterr().out == "\n0 fault(s), 0 legacy entry(ies)\n"
    assert not project.paths.lock.exists()
    assert not project.paths.staging.exists()


def test_verify_prints_each_finding_then_the_summary_and_exits_1_on_a_fault(project, capsys):
    (project.sources / "old_pages").mkdir()
    (project.sources / "stray").mkdir()
    project.paths.baseline.write_text(
        json.dumps({"orphan_source_dirs": ["knowledge/sources/old_pages/"], "loose_files": []})
    )

    assert research("verify") == 1

    assert capsys.readouterr().out == (
        "legacy  orphan_source_dir    knowledge/sources/old_pages — "
        "source directory with no manifest row\n"
        "fault   orphan_source_dir    knowledge/sources/stray — "
        "source directory with no manifest row\n"
        "\n"
        "1 fault(s), 1 legacy entry(ies)\n"
    )


def test_verify_with_only_legacy_findings_exits_0(project, capsys):
    (project.sources / "old_pages").mkdir()
    project.paths.baseline.write_text(
        json.dumps({"orphan_source_dirs": ["knowledge/sources/old_pages/"], "loose_files": []})
    )
    assert research("verify") == 0
    assert capsys.readouterr().out.endswith("\n0 fault(s), 1 legacy entry(ies)\n")


# --- sources, add-entry, remove-entry ------------------------------------------------------


def test_sources_lists_no_commented_example_on_a_fresh_target(project, capsys):
    assert research("sources") == 0
    assert capsys.readouterr().out == ""


def test_sources_labels_every_entry_in_file_order(project, local_site, capsys):
    register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=project.paths, guard=NO_GUARD
    )
    assert research("add-entry", *ENTRY_FLAGS) == 0
    insert_block(
        project.index,
        "### Orphan Pages\n- **Type**: documentation\n- **Location**: knowledge/sources/orphan_pages/",
    )
    insert_block(project.index, "### Bare Note")
    capsys.readouterr()

    assert research("sources") == 0

    assert capsys.readouterr().out.splitlines() == [
        "registered url Widget Coil Note — knowledge/sources/widget_coil_note/",
        "hand-curated codebase Reference Code — /srv/reference",
        "unregistered documentation Orphan Pages — knowledge/sources/orphan_pages/",
        "hand-curated (no type) Bare Note — (no location)",
    ]


def test_sources_without_an_index_is_one_error_line(project, capsys):
    project.index.unlink()
    assert research("sources") == 1
    assert _one_error_line(capsys) == "Error: source index missing: knowledge/SOURCE_INDEX.md"


def test_add_replace_and_remove_an_entry(project, capsys):
    assert research("add-entry", *ENTRY_FLAGS) == 0
    assert json.loads(capsys.readouterr().out) == {"outcome": "added", "reason": ""}
    assert "### Reference Code\n- **Type**: codebase\n" in project.index.read_text()

    replaced = (*ENTRY_FLAGS[:-1], "Compare model outputs against it", "--replace")
    assert research("add-entry", *replaced) == 0
    assert json.loads(capsys.readouterr().out) == {"outcome": "replaced", "reason": ""}
    assert "- **Validation**: Compare model outputs against it\n" in project.index.read_text()

    assert research("remove-entry", "--title", "Reference Code") == 0
    assert json.loads(capsys.readouterr().out) == {"outcome": "removed", "reason": ""}
    assert project.index.read_bytes() == get_template_path().read_bytes()


ENTRY_REFUSALS = {
    "add a duplicate title": ("add-entry", *ENTRY_FLAGS),
    "replace a missing title": ("add-entry", "--title", "Missing", *ENTRY_FLAGS[2:], "--replace"),
    "remove a missing title": ("remove-entry", "--title", "Missing"),
    "a registered type": ("add-entry", *ENTRY_FLAGS[:2], "--type", "url", *ENTRY_FLAGS[4:]),
    "a registry location": (
        "add-entry",
        *ENTRY_FLAGS[:4],
        "--location",
        "./knowledge/sources/widget/",
        *ENTRY_FLAGS[6:],
    ),
}


@pytest.mark.parametrize("argv", ENTRY_REFUSALS.values(), ids=ENTRY_REFUSALS.keys())
def test_an_entry_refusal_exits_1_and_writes_nothing(project, capsys, argv):
    assert research("add-entry", *ENTRY_FLAGS) == 0
    capsys.readouterr()
    before = project.index.read_bytes()

    assert research(*argv) == 1

    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == ["outcome", "reason"]
    assert payload["outcome"] == "precondition_failed" and payload["reason"]
    assert project.index.read_bytes() == before


def test_an_entry_holdout_hit_prints_its_rule_and_offsets(project, capsys):
    _configure_guard(project)
    title = f"Notes on {SEALED_TOKEN}"

    assert research("add-entry", "--title", title, *ENTRY_FLAGS[2:]) == 1

    payload = json.loads(capsys.readouterr().out)
    assert list(payload) == ["outcome", "reason", "rule_id", "offsets"]
    assert payload["outcome"] == "holdout_hit"
    assert payload["rule_id"] == f"term:{SEALED_TOKEN}"
    assert payload["offsets"] == [title.index(SEALED_TOKEN)]
    assert project.index.read_bytes() == get_template_path().read_bytes()


def test_a_broken_guard_refuses_an_entry(project, capsys):
    write_research_config(project.paths.project_root, 'holdout-guard = "missing.py"')

    assert research("add-entry", *ENTRY_FLAGS) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "precondition_failed"
    assert payload["reason"].startswith("hold-out guard unavailable: ")
    assert project.index.read_bytes() == get_template_path().read_bytes()
