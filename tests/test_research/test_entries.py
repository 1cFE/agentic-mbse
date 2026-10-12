"""Hand-curated entries: listing, adding, replacing and removing them.

A hand-curated entry is a source the registry cannot capture, so its Location
points anywhere but `knowledge/sources/`. Every write holds the registry lock,
every addition passes the project's hold-out guard, and every refusal leaves the
registry as it was.
"""

import threading
from dataclasses import replace
from pathlib import Path

import pytest

from agentic_mbse.cli import get_template_path
from agentic_mbse.research import SourceMetadata, UrlSource, register
from agentic_mbse.research.index import (
    HandCuratedEntry,
    ListedEntry,
    add_entry,
    insert_block,
    list_entries,
    remove_entry,
    replace_entry,
)
from agentic_mbse.research.paths import registry_lock
from agentic_mbse.research.retire import retire
from tests.test_research.conftest import (
    GUARD_FILE_SOURCE,
    NO_GUARD,
    SEALED_TOKEN,
    FakeGuard,
    RecordingGuard,
    ScriptedGuard,
    registry_state,
    write_research_config,
)

ENTRY = HandCuratedEntry(
    title="Reference Code",
    type="codebase",
    location="/srv/reference/widget-model",
    use_for="Cross-checking widget sizing formulas.",
    validation="Compare model outputs against its sizing routine.",
)

SEALED_GUARD = FakeGuard(terms=(SEALED_TOKEN,), path_globs=("*/sealed/*",))

FAULT_PREFIX = "hold-out guard unavailable: "


def _add(tree, entry=ENTRY, guard=NO_GUARD):
    result = add_entry(entry, paths=tree.paths, guard=guard)
    assert result.outcome == "added", result.reason
    return result


def _place_block(tree, title: str, location: str) -> None:
    """An index block written by hand, as a person in an editor would."""
    insert_block(
        tree.index,
        "\n".join(
            [
                f"### {title}",
                "- **Type**: reference",
                f"- **Location**: {location}",
                "- **Use for**: Written by hand.",
                "- **Validation**: N/A",
            ]
        ),
    )


def _register(tree, local_site, title="Widget Coil Note"):
    metadata = SourceMetadata(
        title=title,
        use_for="Synthetic winding-pack geometry.",
        validation="Compare against the fixture page itself.",
        caveat="A test fixture.",
    )
    result = register(UrlSource(url=local_site.url("utf8.html")), metadata, paths=tree.paths)
    assert result.outcome == "registered", result.reason
    return result


# --- sources ----------------------------------------------------------------------


def test_a_fresh_target_lists_no_entries(knowledge_tree):
    """The shipped template's commented examples and its placeholder line are not entries."""
    assert list_entries(knowledge_tree.paths) == []


def test_sources_labels_every_entry(knowledge_tree, local_site):
    registered = _register(knowledge_tree, local_site)
    _add(knowledge_tree)
    _place_block(knowledge_tree, "Hand-Placed Capture", "knowledge/sources/hand_placed/")

    assert list_entries(knowledge_tree.paths) == [
        ListedEntry(
            label="registered",
            title="Widget Coil Note",
            type="url",
            location=f"knowledge/sources/{registered.slug}/",
        ),
        ListedEntry(
            label="hand-curated",
            title="Reference Code",
            type="codebase",
            location="/srv/reference/widget-model",
        ),
        ListedEntry(
            label="unregistered",
            title="Hand-Placed Capture",
            type="reference",
            location="knowledge/sources/hand_placed/",
        ),
    ]


def test_listing_takes_no_lock_and_writes_nothing(knowledge_tree):
    _place_block(knowledge_tree, "Hand-Placed Capture", "knowledge/sources/hand_placed/")
    before = registry_state(knowledge_tree)
    list_entries(knowledge_tree.paths)
    assert registry_state(knowledge_tree) == before
    assert not knowledge_tree.paths.lock.exists()


# --- add, replace, remove ------------------------------------------------------------


def test_add_then_remove_restores_the_shipped_index(knowledge_tree):
    _add(knowledge_tree)
    assert remove_entry("Reference Code", paths=knowledge_tree.paths).outcome == "removed"
    assert knowledge_tree.index.read_bytes() == get_template_path().read_bytes()
    assert not knowledge_tree.manifest.exists()


@pytest.mark.parametrize(
    ("given", "written"),
    [
        ("./docs/widget_spec.pdf", "docs/widget_spec.pdf"),
        ("  docs/widget_spec.pdf  ", "docs/widget_spec.pdf"),
        ("https://standards.example.com/api", "https://standards.example.com/api"),
        ("/srv/reference/widget-model", "/srv/reference/widget-model"),
    ],
)
def test_an_added_entry_is_written_stripped_with_its_location_normalized(
    knowledge_tree, given, written
):
    _add(knowledge_tree, replace(ENTRY, title="  Reference Code ", location=given))

    (listed,) = list_entries(knowledge_tree.paths)
    assert listed == ListedEntry(
        label="hand-curated", title="Reference Code", type="codebase", location=written
    )
    assert f"### Reference Code\n- **Type**: codebase\n- **Location**: {written}\n" in (
        knowledge_tree.index.read_text()
    )


def test_an_absolute_location_inside_the_project_is_written_relative(knowledge_tree):
    inside = knowledge_tree.root.parent.resolve() / "docs" / "widget_spec.pdf"
    _add(knowledge_tree, replace(ENTRY, location=str(inside)))
    (listed,) = list_entries(knowledge_tree.paths)
    assert listed.location == "docs/widget_spec.pdf"


def test_replace_rewrites_the_one_entry_in_place(knowledge_tree):
    _add(knowledge_tree)
    second = HandCuratedEntry(
        title="Standards API",
        type="database",
        location="https://example.org/api",
        use_for="Widget safety limits.",
        validation="N/A",
    )
    _add(knowledge_tree, second)
    before = knowledge_tree.index.read_text()

    revised = replace(ENTRY, use_for="Widget sizing and coil geometry.", validation="N/A")
    result = replace_entry(revised, paths=knowledge_tree.paths, guard=NO_GUARD)

    assert result.outcome == "replaced"
    old_lines = (
        "- **Use for**: Cross-checking widget sizing formulas.\n"
        "- **Validation**: Compare model outputs against its sizing routine."
    )
    new_lines = "- **Use for**: Widget sizing and coil geometry.\n- **Validation**: N/A"
    assert before.count(old_lines) == 1
    assert knowledge_tree.index.read_text() == before.replace(old_lines, new_lines)
    assert [entry.title for entry in list_entries(knowledge_tree.paths)] == [
        "Reference Code",
        "Standards API",
    ]


def test_a_registered_entry_may_share_a_hand_curated_title(knowledge_tree, local_site):
    _register(knowledge_tree, local_site, title="Reference Code")
    registered_state = registry_state(knowledge_tree)

    _add(knowledge_tree)
    assert remove_entry("Reference Code", paths=knowledge_tree.paths).outcome == "removed"

    assert registry_state(knowledge_tree) == registered_state


def test_removing_a_hand_placed_entry_above_the_commented_examples_leaves_them(knowledge_tree):
    """The block ends where the comment opens, so the examples and placeholder line survive."""
    template = knowledge_tree.index.read_text()
    heading = "## Primary Sources\n\n"
    assert template.count(heading) == 1
    hand_placed = (
        "### Reference Code\n"
        "- **Type**: codebase\n"
        "- **Location**: /srv/reference/widget-model\n"
        "- **Use for**: Cross-checking widget sizing formulas.\n"
        "- **Validation**: N/A\n\n"
    )
    knowledge_tree.index.write_text(template.replace(heading, heading + hand_placed))

    result = remove_entry("Reference Code", paths=knowledge_tree.paths)

    assert result.outcome == "removed"
    assert knowledge_tree.index.read_bytes() == get_template_path().read_bytes()


@pytest.mark.parametrize(
    ("operation", "outcome"),
    [
        (
            lambda paths: add_entry(
                replace(ENTRY, title="Second Code"), paths=paths, guard=NO_GUARD
            ),
            "added",
        ),
        (lambda paths: replace_entry(ENTRY, paths=paths, guard=NO_GUARD), "replaced"),
        (lambda paths: remove_entry("Reference Code", paths=paths), "removed"),
        (
            lambda paths: retire("no_such_source", "test", paths=paths, guard=NO_GUARD),
            "unknown_slug",
        ),
    ],
    ids=["add", "replace", "remove", "retire"],
)
def test_a_registry_write_waits_for_the_lock(knowledge_tree, operation, outcome):
    """A registration holding the lock cannot lose its index write to a hand edit, or the reverse."""
    _add(knowledge_tree)
    before = registry_state(knowledge_tree)
    results = []
    worker = threading.Thread(target=lambda: results.append(operation(knowledge_tree.paths)))

    with registry_lock(knowledge_tree.paths):
        worker.start()
        worker.join(timeout=0.3)
        assert worker.is_alive()
        assert registry_state(knowledge_tree) == before
    worker.join(timeout=10)

    assert [result.outcome for result in results] == [outcome]


# --- refusals write nothing ----------------------------------------------------------


def _assert_refused(result, reason: str) -> None:
    assert (result.outcome, result.reason) == ("precondition_failed", reason)


def test_add_refuses_a_title_a_hand_curated_entry_has(knowledge_tree):
    _add(knowledge_tree)
    before = registry_state(knowledge_tree)

    result = add_entry(
        replace(ENTRY, title=" Reference Code"), paths=knowledge_tree.paths, guard=NO_GUARD
    )

    _assert_refused(
        result, "a hand-curated entry titled 'Reference Code' already exists; replace it instead"
    )
    assert registry_state(knowledge_tree) == before


@pytest.mark.parametrize("operation", ["replace", "remove"])
def test_a_title_no_hand_curated_entry_has_refuses(knowledge_tree, operation):
    _add(knowledge_tree)
    before = registry_state(knowledge_tree)

    if operation == "replace":
        result = replace_entry(
            replace(ENTRY, title="Missing Code"), paths=knowledge_tree.paths, guard=NO_GUARD
        )
    else:
        result = remove_entry("Missing Code", paths=knowledge_tree.paths)

    _assert_refused(result, "no hand-curated entry titled 'Missing Code'")
    assert registry_state(knowledge_tree) == before


@pytest.mark.parametrize("operation", ["replace", "remove"])
def test_an_ambiguous_title_refuses(knowledge_tree, operation):
    _place_block(knowledge_tree, "Reference Code", "/srv/reference/widget-model")
    _place_block(knowledge_tree, "Reference Code", "/srv/reference/widget-model-v2")
    before = registry_state(knowledge_tree)

    if operation == "replace":
        result = replace_entry(ENTRY, paths=knowledge_tree.paths, guard=NO_GUARD)
    else:
        result = remove_entry("Reference Code", paths=knowledge_tree.paths)

    _assert_refused(
        result,
        "2 hand-curated entries are titled 'Reference Code'; tell them apart in the index first",
    )
    assert registry_state(knowledge_tree) == before


@pytest.mark.parametrize("operation", ["replace", "remove"])
def test_a_registered_entry_is_never_replaced_or_removed_by_hand(
    knowledge_tree, local_site, operation
):
    _register(knowledge_tree, local_site, title="Reference Code")
    before = registry_state(knowledge_tree)

    if operation == "replace":
        result = replace_entry(ENTRY, paths=knowledge_tree.paths, guard=NO_GUARD)
    else:
        result = remove_entry("Reference Code", paths=knowledge_tree.paths)

    _assert_refused(
        result,
        "no hand-curated entry titled 'Reference Code'; the entry with that title is under "
        "knowledge/sources/, so retire it by its slug",
    )
    assert registry_state(knowledge_tree) == before


@pytest.mark.parametrize(
    "location",
    [
        "knowledge/sources/widget_note/",
        "./knowledge/sources/widget_note/",
        "knowledge/sources/widget_note",
        "knowledge/sources/widget_note/output.md",
    ],
)
@pytest.mark.parametrize("operation", [add_entry, replace_entry])
def test_a_location_under_the_registry_refuses(knowledge_tree, location, operation):
    before = registry_state(knowledge_tree)

    result = operation(
        replace(ENTRY, location=location), paths=knowledge_tree.paths, guard=NO_GUARD
    )

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith("location knowledge/sources/widget_note")
    assert result.reason.endswith(
        " is under knowledge/sources/, which only register writes; register the source instead"
    )
    assert registry_state(knowledge_tree) == before


def test_an_absolute_location_under_the_registry_refuses(knowledge_tree):
    absolute = knowledge_tree.sources.resolve() / "widget_note"
    result = add_entry(
        replace(ENTRY, location=f"{absolute}/"), paths=knowledge_tree.paths, guard=NO_GUARD
    )
    _assert_refused(
        result,
        "location knowledge/sources/widget_note/ is under knowledge/sources/, which only "
        "register writes; register the source instead",
    )


@pytest.mark.parametrize(
    ("entry", "reason"),
    [
        (
            replace(ENTRY, title=" ", validation=""),
            "caller must supply non-empty title, validation",
        ),
        (
            replace(ENTRY, use_for="Line one.\nLine two."),
            "use_for must be one line and must not open an HTML comment",
        ),
        (
            replace(ENTRY, title="Reference\r\nCode", validation="N/A <!-- hidden"),
            "title, validation must be one line and must not open an HTML comment",
        ),
        (
            replace(ENTRY, type="url"),
            "type 'url' is not a hand-curated type; use one of codebase, documentation, database, reference",
        ),
        (
            replace(ENTRY, type="notes"),
            "type 'notes' is not a hand-curated type; use one of codebase, documentation, database, reference",
        ),
    ],
)
@pytest.mark.parametrize("operation", [add_entry, replace_entry])
def test_an_entry_that_cannot_be_written_as_one_block_refuses(
    knowledge_tree, entry, reason, operation
):
    before = registry_state(knowledge_tree)
    _assert_refused(operation(entry, paths=knowledge_tree.paths, guard=NO_GUARD), reason)
    assert registry_state(knowledge_tree) == before


def test_a_blank_title_refuses_removal(knowledge_tree):
    _assert_refused(
        remove_entry("  ", paths=knowledge_tree.paths), "caller must supply non-empty title"
    )


@pytest.mark.parametrize("operation", ["add", "replace", "remove"])
def test_a_missing_index_refuses_and_creates_nothing(knowledge_tree, operation):
    knowledge_tree.index.unlink()

    if operation == "add":
        result = add_entry(ENTRY, paths=knowledge_tree.paths, guard=NO_GUARD)
    elif operation == "replace":
        result = replace_entry(ENTRY, paths=knowledge_tree.paths, guard=NO_GUARD)
    else:
        result = remove_entry("Reference Code", paths=knowledge_tree.paths)

    _assert_refused(result, f"source index missing: {knowledge_tree.index}")
    assert not knowledge_tree.index.exists()
    assert not knowledge_tree.paths.lock.exists()


# --- the hold-out guard ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("change", "rule_id"),
    [
        ({"title": f"Reference Code ({SEALED_TOKEN})"}, f"term:{SEALED_TOKEN}"),
        ({"location": f"https://example.org/{SEALED_TOKEN}.pdf"}, f"term:{SEALED_TOKEN}"),
        ({"use_for": f"Sizing, as in {SEALED_TOKEN}."}, f"term:{SEALED_TOKEN}"),
        ({"validation": f"Compare against {SEALED_TOKEN}."}, f"term:{SEALED_TOKEN}"),
        ({"location": "/srv/sealed/widget-model"}, "path:*/sealed/*"),
    ],
)
@pytest.mark.parametrize("operation", [add_entry, replace_entry])
def test_a_guard_hit_refuses_with_its_rule(knowledge_tree, change, rule_id, operation):
    if operation is replace_entry:
        _add(knowledge_tree)
    before = registry_state(knowledge_tree)

    result = operation(replace(ENTRY, **change), paths=knowledge_tree.paths, guard=SEALED_GUARD)

    assert result.outcome == "holdout_hit"
    assert result.rule_id == rule_id
    assert result.reason == f"{rule_id} matched 1x"
    assert result.offsets
    assert registry_state(knowledge_tree) == before


@pytest.mark.parametrize(
    ("location", "path_checked"),
    [("/srv/reference/widget-model", True), ("https://example.org/api", False)],
)
def test_the_guard_checks_a_path_location_then_scans_each_field(
    knowledge_tree, location, path_checked
):
    guard = RecordingGuard()
    _add(knowledge_tree, replace(ENTRY, location=location), guard=guard)

    scans = [
        ("scan_terms", ENTRY.title),
        ("scan_terms", location),
        ("scan_terms", ENTRY.use_for),
        ("scan_terms", ENTRY.validation),
    ]
    assert guard.calls == ([("check_input_path", Path(location))] if path_checked else []) + scans


def test_a_guard_file_the_project_names_bars_an_entry(knowledge_tree):
    project = knowledge_tree.root.parent
    (project / "guard.py").write_text(GUARD_FILE_SOURCE)
    write_research_config(project, 'holdout-guard = "guard.py"')

    result = add_entry(
        replace(ENTRY, location="/srv/sealed/widget-model"), paths=knowledge_tree.paths
    )

    assert result.outcome == "holdout_hit" and result.rule_id == "path:*/sealed/*"
    assert (
        _add(knowledge_tree, guard=None).outcome == "added"
    )  # the same guard passes a clean entry


@pytest.mark.parametrize(
    "guard",
    [
        pytest.param(ScriptedGuard(raises_in="check_input_path"), id="input path check raises"),
        pytest.param(ScriptedGuard(raises_in="scan_terms"), id="term scan raises"),
        pytest.param(ScriptedGuard(terms_answer=None), id="term scan answers None"),
    ],
)
@pytest.mark.parametrize("operation", [add_entry, replace_entry])
def test_a_guard_that_cannot_answer_refuses(knowledge_tree, guard, operation):
    if operation is replace_entry:
        _add(knowledge_tree)
    before = registry_state(knowledge_tree)

    result = operation(ENTRY, paths=knowledge_tree.paths, guard=guard)

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith(FAULT_PREFIX)
    assert registry_state(knowledge_tree) == before


def test_a_misconfigured_project_guard_refuses_an_entry_that_would_pass(knowledge_tree):
    write_research_config(knowledge_tree.root.parent, 'holdout_guard = "guard.py"')

    result = add_entry(ENTRY, paths=knowledge_tree.paths)

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith(FAULT_PREFIX) and "holdout_guard" in result.reason
    assert knowledge_tree.index.read_bytes() == get_template_path().read_bytes()


def test_removal_does_not_ask_the_guard(knowledge_tree):
    """Removing an entry lets nothing in, so even a broken guard does not block it."""
    _add(knowledge_tree)
    write_research_config(knowledge_tree.root.parent, 'holdout_guard = "guard.py"')
    assert remove_entry("Reference Code", paths=knowledge_tree.paths).outcome == "removed"
