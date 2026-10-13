"""The hold-out checks in `register`, and what a hit or a guard fault leaves behind.

Hits come from a guard barring a neutral token, either the fake guard a test
passes in or a guard file the project's `pyproject.toml` names. A fault is a
configured guard that cannot answer. Every fault refuses as
`precondition_failed` with a receipt, on a source that would otherwise
register, so a test here fails if a broken guard is bypassed.
"""

import hashlib
import inspect
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from agentic_mbse.research import LocalPdfSource, SourceMetadata, UrlSource, register
from agentic_mbse.research.runs import read_receipts
from tests.test_research.conftest import (
    GUARD_FILE_SOURCE,
    NO_GUARD,
    SEALED_TOKEN,
    FakeGuard,
    FakeMatch,
    ScriptedGuard,
    assert_nothing_written,
    write_research_config,
)

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the hold-out checks.",
    validation="Not applicable: this is a refusal fixture.",
    caveat="A test fixture.",
)

SEALED_GUARD = FakeGuard(terms=(SEALED_TOKEN,), path_globs=("*/sealed/*",))

FAULT_PREFIX = "hold-out guard unavailable: "


@pytest.fixture
def sealed_pdf(generated_pdf, tmp_path) -> Path:
    """A real PDF at an input path the guards bar."""
    path = tmp_path / "sealed" / "widget_coil_note.pdf"
    path.parent.mkdir()
    shutil.copyfile(generated_pdf, path)
    return path


# --- hits from a caller-supplied guard ---------------------------------------------


def test_content_hit_writes_nothing_and_names_the_rule(local_site, knowledge_tree):
    result = register(
        UrlSource(url=local_site.url("marker.html")),
        METADATA,
        paths=knowledge_tree.paths,
        guard=SEALED_GUARD,
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == f"term:{SEALED_TOKEN}"
    assert result.offsets
    assert_nothing_written(knowledge_tree)


def test_barred_url_is_refused_before_any_fetch(knowledge_tree, no_capture):
    result = register(
        UrlSource(url=f"https://example.org/mirror/{SEALED_TOKEN}.pdf"),
        METADATA,
        paths=knowledge_tree.paths,
        guard=SEALED_GUARD,
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == f"term:{SEALED_TOKEN}"
    assert_nothing_written(knowledge_tree)


def test_barred_title_is_refused_before_any_fetch(local_site, knowledge_tree, no_capture):
    result = register(
        UrlSource(url=local_site.url("utf8.html")),
        replace(METADATA, title=f"Notes on {SEALED_TOKEN}"),
        paths=knowledge_tree.paths,
        guard=SEALED_GUARD,
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == f"term:{SEALED_TOKEN}"
    assert_nothing_written(knowledge_tree)


def test_barred_local_pdf_input_path_is_refused(knowledge_tree, sealed_pdf, no_capture):
    result = register(
        LocalPdfSource(path=sealed_pdf), METADATA, paths=knowledge_tree.paths, guard=SEALED_GUARD
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == "path:*/sealed/*"
    assert_nothing_written(knowledge_tree)


def test_no_parameter_can_waive_a_hit():
    """The Python API has no waiver: a hit has no in-code way past it."""
    assert list(inspect.signature(register).parameters) == [
        "source",
        "metadata",
        "paths",
        "guard",
        "budget",
        "run_dir",
        "triage",
    ]


# --- the guard the project configures ------------------------------------------------


@pytest.mark.parametrize(
    "pyproject",
    [
        pytest.param(None, id="no pyproject"),
        pytest.param('[project]\nname = "target"\n', id="no research table"),
        pytest.param("[tool.agentic-mbse.research]\n", id="empty research table"),
    ],
)
def test_no_configured_guard_registers(pyproject, local_site, knowledge_tree):
    if pyproject is not None:
        (knowledge_tree.paths.project_root / "pyproject.toml").write_text(pyproject)

    result = register(
        UrlSource(url=local_site.url("marker.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "registered", result.reason


def _configure_guard_file(tree, source: str = GUARD_FILE_SOURCE) -> None:
    root = tree.paths.project_root
    write_research_config(root, 'holdout-guard = "guard.py"')
    (root / "guard.py").write_text(source)


def test_a_configured_guard_file_bars_content(local_site, knowledge_tree):
    _configure_guard_file(knowledge_tree)
    result = register(
        UrlSource(url=local_site.url("marker.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == f"term:{SEALED_TOKEN}"
    assert_nothing_written(knowledge_tree)


def test_a_configured_guard_file_bars_an_input_path(knowledge_tree, sealed_pdf, no_capture):
    _configure_guard_file(knowledge_tree)
    result = register(LocalPdfSource(path=sealed_pdf), METADATA, paths=knowledge_tree.paths)
    assert result.outcome == "holdout_hit"
    assert result.rule_id == "path:*/sealed/*"


def test_a_configured_guard_file_lets_a_clean_source_through(local_site, knowledge_tree):
    _configure_guard_file(knowledge_tree)
    result = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "registered", result.reason


# --- a configured guard that cannot answer ---------------------------------------------

#: Each way a configured guard can be broken: the research table's body, the guard
#: file beside it (None for none), and a fragment of the refusal's reason. Every
#: case would register `utf8.html` if the fault were ignored.
BROKEN_CONFIGURATIONS = [
    pytest.param(
        'holdout_guard = "guard.py"',
        GUARD_FILE_SOURCE,
        "unknown key 'holdout_guard'",
        id="misspelled key",
    ),
    pytest.param(
        'holdout-guard = "guard.py"\nstrict = true',
        GUARD_FILE_SOURCE,
        "unknown key 'strict'",
        id="unknown key beside the guard",
    ),
    pytest.param('holdout-guard = ""', None, "must be a non-empty path", id="empty value"),
    pytest.param("holdout-guard = 3", None, "must be a non-empty path", id="integer value"),
    pytest.param('holdout-guard = "missing.py"', None, "no file at", id="missing file"),
    pytest.param(
        'holdout-guard = "guard.py"',
        "raise RuntimeError('protocol file unreadable')\n",
        "failed to load: RuntimeError: protocol file unreadable",
        id="fails to load",
    ),
    pytest.param(
        'holdout-guard = "guard.py"',
        GUARD_FILE_SOURCE.replace("def scan_file", "def _scan_file"),
        "lacks scan_file",
        id="missing function",
    ),
    pytest.param(
        'holdout-guard = "guard.py"',
        GUARD_FILE_SOURCE
        + "\n\ndef scan_terms(text):\n    raise RuntimeError('term list did not parse')\n",
        "scan_terms raised RuntimeError: term list did not parse",
        id="raises during a check",
    ),
]


@pytest.mark.parametrize(("table_body", "guard_source", "fragment"), BROKEN_CONFIGURATIONS)
def test_a_broken_configured_guard_refuses_with_a_receipt(
    table_body, guard_source, fragment, local_site, knowledge_tree, run_dir
):
    root = knowledge_tree.paths.project_root
    write_research_config(root, table_body)
    if guard_source is not None:
        (root / "guard.py").write_text(guard_source)

    result = register(
        UrlSource(url=local_site.url("utf8.html")),
        METADATA,
        paths=knowledge_tree.paths,
        run_dir=run_dir,
    )

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith(FAULT_PREFIX)
    assert fragment in result.reason
    (receipt,) = read_receipts(run_dir)
    assert receipt["outcome"] == "precondition_failed"
    assert receipt["reason"] == result.reason
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


@pytest.mark.parametrize(
    ("table", "fragment"),
    [
        pytest.param(
            "[tool.agentic-mbse.reseach]",
            "unknown key 'reseach' in [tool.agentic-mbse]",
            id="research misspelled",
        ),
        pytest.param(
            "[tool.agentic_mbse.research]",
            "[tool.agentic_mbse] is not read",
            id="underscore toolkit table",
        ),
    ],
)
def test_a_misspelled_table_name_refuses_with_a_receipt(
    table, fragment, local_site, knowledge_tree, run_dir
):
    """The guard named under the misspelled table would load and answer; ignored, `utf8.html` registers."""
    root = knowledge_tree.paths.project_root
    (root / "pyproject.toml").write_text(f'{table}\nholdout-guard = "guard.py"\n')
    (root / "guard.py").write_text(GUARD_FILE_SOURCE)

    result = register(
        UrlSource(url=local_site.url("utf8.html")),
        METADATA,
        paths=knowledge_tree.paths,
        run_dir=run_dir,
    )

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith(FAULT_PREFIX)
    assert fragment in result.reason
    (receipt,) = read_receipts(run_dir)
    assert receipt["reason"] == result.reason
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


@pytest.mark.parametrize(
    ("guard", "reason"),
    [
        pytest.param(
            ScriptedGuard(raises_in="check_input_path"),
            "check_input_path raised RuntimeError: check_input_path could not run",
            id="input path check raises",
        ),
        pytest.param(
            ScriptedGuard(raises_in="scan_terms"),
            "scan_terms raised RuntimeError: scan_terms could not run",
            id="term scan raises",
        ),
        pytest.param(
            ScriptedGuard(input_path_answer=True),
            "check_input_path answered a match without a rule_id",
            id="input path answer is not a match",
        ),
        pytest.param(
            ScriptedGuard(terms_answer=None),
            "scan_terms answered NoneType, not a sequence of matches",
            id="term scan answers None",
        ),
        pytest.param(
            ScriptedGuard(terms_answer=[FakeMatch(rule_id="", count=1, offsets=(0,))]),
            "scan_terms answered a match without a rule_id",
            id="match with an empty rule id",
        ),
        pytest.param(
            ScriptedGuard(terms_answer=[FakeMatch(rule_id="term:x", count=1, offsets=None)]),
            "scan_terms answered a match without integer offsets",
            id="match without offsets",
        ),
    ],
)
def test_a_guard_that_cannot_answer_before_capture_refuses_with_a_receipt(
    guard, reason, knowledge_tree, generated_pdf, run_dir, no_capture
):
    result = register(
        LocalPdfSource(path=generated_pdf),
        METADATA,
        paths=knowledge_tree.paths,
        guard=guard,
        run_dir=run_dir,
    )

    assert result.outcome == "precondition_failed"
    assert result.reason == FAULT_PREFIX + reason
    assert result.source_id is None
    (receipt,) = read_receipts(run_dir)
    assert receipt["outcome"] == "precondition_failed"
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


def test_a_guard_fault_after_capture_counts_the_capture(local_site, knowledge_tree, make_run_dir):
    """The extractor ran, so the refusal carries its source id and spends the run's capture."""
    run = make_run_dir(max_captures=1)
    faulted = register(
        UrlSource(url=local_site.url("utf8.html")),
        METADATA,
        paths=knowledge_tree.paths,
        guard=ScriptedGuard(raises_in="scan_file"),
        run_dir=run,
    )
    after = register(
        UrlSource(url=local_site.url("latin1.html")),
        replace(METADATA, title="Cable Note"),
        paths=knowledge_tree.paths,
        guard=NO_GUARD,
        run_dir=run,
    )

    assert faulted.outcome == "precondition_failed"
    assert faulted.reason == FAULT_PREFIX + "scan_file raised RuntimeError: scan_file could not run"
    assert faulted.source_id == hashlib.sha256(local_site.fetched_bytes("utf8.html")).hexdigest()
    assert after.outcome == "limit_reached"
    first, second = read_receipts(run)
    assert first["outcome"] == "precondition_failed"
    assert first["captured"] is True
    assert first["source_id"] == faulted.source_id
    assert second["outcome"] == "limit_reached"
    assert_nothing_written(knowledge_tree)
