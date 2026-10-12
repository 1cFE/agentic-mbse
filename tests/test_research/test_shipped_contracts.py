"""Every shipped instruction about sources points at the research CLI, and the goal layer maps the seam's classes.

`/manage-sources` is the hands-on front end to `agentic-mbse research`: it makes
every change through the CLI and never edits the registry files. `run-goal` and the
goal runbook name the installed seam, and the runbook alone holds the class to
task-outcome table. The source-type tables in the guide and the traceability skill
agree with the types the code accepts.
"""

import re

import pytest

from agentic_mbse.research.index import HAND_CURATED_TYPES
from agentic_mbse.research.sources import REGISTRY_KINDS
from tests.helpers.shipped import REPO_ROOT
from tests.test_research.shipped_text import research_invocations, research_parser, section

MANAGE_SOURCES = REPO_ROOT / "skills" / "manage-sources" / "SKILL.md"
RUN_GOAL = REPO_ROOT / "skills" / "run-goal" / "SKILL.md"
RUNBOOK = REPO_ROOT / "project_templates" / "GOAL_RUNBOOK.md.template"
SOURCE_INDEX_GUIDE = REPO_ROOT / "docs" / "source-index.md"
TRACEABILITY = REPO_ROOT / "skills" / "source-traceability" / "SKILL.md"
TEMPLATE = REPO_ROOT / "SOURCE_INDEX.md.template"

REGISTRY_FILES = ("SOURCE_INDEX.md", "MANIFEST.jsonl", "RETIRED.jsonl", "knowledge/sources/")

#: The hand-edit instructions the shipped skills carried before the registry, gone for good.
HAND_EDITS = (
    "Append the new entry to `knowledge/SOURCE_INDEX.md`",
    "Use Edit to remove the section from `knowledge/SOURCE_INDEX.md`",
    "Edit manually: open `knowledge/SOURCE_INDEX.md`",
    "register them in `knowledge/SOURCE_INDEX.md`",
)


def _read(path) -> str:
    return path.read_text(encoding="utf-8")


# --- manage-sources ------------------------------------------------------------------------


def test_manage_sources_makes_every_change_through_the_cli():
    used = {call[0] for call in research_invocations(_read(MANAGE_SOURCES))}
    assert {"sources", "register", "add-entry", "remove-entry", "retire", "verify"} <= used


@pytest.mark.parametrize("call", research_invocations(MANAGE_SOURCES.read_text(encoding="utf-8")))
def test_every_call_manage_sources_shows_parses_under_the_cli(call):
    research_parser().parse_args(["research", *call])


def test_manage_sources_states_its_never_edit_rule():
    rule = next(
        paragraph for paragraph in _read(MANAGE_SOURCES).split("\n\n") if "never edits" in paragraph
    )
    for name in REGISTRY_FILES:
        assert name in rule


def test_manage_sources_edits_hand_curated_entries_with_replace():
    body = _read(MANAGE_SOURCES)
    assert any(
        call[:1] == ["add-entry"] and "--replace" in call for call in research_invocations(body)
    )


def test_manage_sources_resolves_a_queue_from_the_latest_run_without_rerunning_it():
    queue = section(_read(MANAGE_SOURCES), "#### Resolve a Queued Candidate")
    assert "newest run directory" in queue
    assert "knowledge/research/requests/runs/<request_id>/" in queue
    assert "does not re-run the request" in queue
    for prefix in (
        "hold-out guard unavailable:",
        "URL capture needs the web extra:",
        "source index missing:",
    ):
        assert prefix in queue


def test_manage_sources_reports_unregistered_entries_without_changing_them():
    body = _read(MANAGE_SOURCES)
    unregistered = next(p for p in body.split("\n\n") if p.startswith("An `unregistered` entry"))
    assert "`verify`" in unregistered and "do not change it" in unregistered


@pytest.mark.parametrize("instruction", HAND_EDITS)
def test_no_shipped_skill_tells_anyone_to_edit_the_index_by_hand(instruction):
    for skill in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        assert instruction not in _read(skill), skill.parent.name


def test_onboard_adds_listed_sources_through_manage_sources():
    configure = section(_read(REPO_ROOT / "skills/onboard/SKILL.md"), "### 3. Configure Sources")
    assert "**manage-sources**" in configure
    assert "agentic-mbse research register" in configure
    assert "agentic-mbse research add-entry" in configure


def test_toolkit_awareness_knows_the_research_cli_and_the_acquisition_skill():
    body = _read(REPO_ROOT / "skills/toolkit-awareness/SKILL.md")
    assert "uv run agentic-mbse research <subcommand>" in body
    assert "| `/research-acquire` |" in body


# --- run-goal and the runbook ----------------------------------------------------------------


def test_run_goal_names_the_installed_seam():
    text = _read(RUN_GOAL)
    assert "research-acquire" in text and "agentic-mbse research" in text
    assert "Use the research procedure the project's instructions name" not in text
    assert "knowledge/research/requests/<request-id>.json" in text
    assert "`GOAL_RUNBOOK.md` § The native seams" in text


def test_the_class_table_lives_only_in_the_runbook():
    assert "| `REGISTERED` |" not in _read(RUN_GOAL)


def test_the_runbook_maps_every_seam_class():
    seams = section(_read(RUNBOOK), "## The native seams")
    for row in (
        "| `REGISTERED` | `COMPLETE` |",
        "| `OPERATOR_QUEUE` | `OWNER_GATE` |",
        "| `BLOCKER` | `PREREQUISITE` |",
        "| `BOUNDED_NEGATIVE` | `BOUNDED_NEGATIVE` |",
    ):
        assert row in seams
    assert "When `open` refuses there is no `return.json`." in seams
    assert "the research procedure the project's instructions name" not in seams


def test_a_queue_of_seam_repairs_is_a_prerequisite_in_the_runbook():
    """The runbook's own rule makes a seam repair `PREREQUISITE`, so the class table yields to it."""
    seams = section(_read(RUNBOOK), "## The native seams")
    assert "An `OPERATOR_QUEUE` whose every queued candidate is a seam repair" in seams
    assert "Record `PREREQUISITE` naming the seam" in seams


# --- the source types ------------------------------------------------------------------------


def _types_after(text: str, label: str) -> set[str]:
    """The backticked first-column types of the table that follows the paragraph starting `label`."""
    after = text[text.index(label) :]
    table = re.search(r"^\|.*?(?=^[^|])", after, flags=re.MULTILINE | re.DOTALL)
    assert table is not None, label
    return set(re.findall(r"^\| `([a-z_]+)` \|", table.group(0), flags=re.MULTILINE))


@pytest.mark.parametrize("path", [SOURCE_INDEX_GUIDE, TRACEABILITY], ids=["guide", "traceability"])
def test_the_type_tables_match_the_types_the_code_accepts(path):
    text = _read(path)
    assert _types_after(text, "**Hand-curated types.**") == set(HAND_CURATED_TYPES)
    assert _types_after(text, "**Registered types.**") == set(REGISTRY_KINDS)


def test_the_traceability_skill_mirrors_the_guides_type_tables():
    guide = section(_read(SOURCE_INDEX_GUIDE), "## Source Types")
    mirrored = _read(TRACEABILITY)
    for line in guide.splitlines():
        if line.startswith("| `"):
            assert line in mirrored


def test_the_entry_format_spells_use_for_as_the_writers_do():
    for path in (SOURCE_INDEX_GUIDE, TRACEABILITY):
        assert "**Use For**" not in _read(path), path.name


# --- the shipped index template --------------------------------------------------------------


def test_the_template_points_new_sources_at_the_cli():
    adding = section(_read(TEMPLATE), "## Adding New Sources")
    assert "/manage-sources" in adding
    assert "agentic-mbse research" in adding


def test_the_templates_type_comment_names_both_kinds_of_type():
    comment = section(_read(TEMPLATE), "## Primary Sources")
    for name in (*HAND_CURATED_TYPES, *sorted(REGISTRY_KINDS)):
        assert name in comment
