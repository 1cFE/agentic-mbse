"""The acquisition skill carries the seam's protocol, not registry logic, and the guide tells an operator what to do with every return.

`skills/research-acquire/SKILL.md` is what an agent follows; `docs/research-seam.md`
is what the operator reads. Both show `agentic-mbse research` calls, and every one
of them must parse under the CLI as it is.
"""

from pathlib import Path

import pytest

from agentic_mbse.research.holdout import (
    first_file_hit,
    first_term_hit,
    input_path_hit,
    load_holdout_guard,
)
from tests.helpers.shipped import REPO_ROOT, frontmatter
from tests.test_research.shipped_text import (
    fenced_blocks,
    research_invocations,
    research_parser,
    section,
)

SKILL = REPO_ROOT / "skills" / "research-acquire" / "SKILL.md"
GUIDE = REPO_ROOT / "docs" / "research-seam.md"

#: The reasons `register` gives when the seam, not the source, needs repair.
SEAM_REPAIR_PREFIXES = (
    "hold-out guard unavailable:",
    "URL capture needs the web extra:",
    "source index missing:",
)

#: The hook table a target adds to its `pyproject.toml`, as the design fixes it.
HOOK_TABLE = '[tool.agentic-mbse.research]\nholdout-guard = "scripts/holdout_guard.py"\n'


@pytest.fixture(scope="module")
def skill_body() -> str:
    return SKILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def guide_body() -> str:
    return GUIDE.read_text(encoding="utf-8")


def _paragraph_with(text: str, needle: str) -> str:
    return next(paragraph for paragraph in text.split("\n\n") if needle in paragraph)


# --- the skill -------------------------------------------------------------------------


def test_the_skill_is_a_workflow_that_can_search_and_fetch():
    meta, _ = frontmatter(SKILL)
    assert meta["name"] == "research-acquire"
    assert meta["metadata"]["kind"] == "workflow"
    assert meta["user-invocable"] is True
    assert {"Bash", "WebSearch", "WebFetch"} <= set(meta["allowed-tools"])


def test_the_skill_calls_the_seam_through_the_cli(skill_body):
    used = {call[0] for call in research_invocations(skill_body)}
    assert used == {"open", "log", "register", "close"}


@pytest.mark.parametrize("call", research_invocations(SKILL.read_text(encoding="utf-8")))
def test_every_call_the_skill_shows_parses_under_the_cli(call):
    research_parser().parse_args(["research", *call])


@pytest.mark.parametrize(
    "forbidden",
    ["SOURCE_INDEX.md", "MANIFEST.jsonl", "RETIRED.jsonl", "--index", "--summarize", "--budget"],
)
def test_the_skill_never_touches_registry_files_or_extraction_flags_itself(skill_body, forbidden):
    assert forbidden not in skill_body


def test_the_skill_states_the_standing_prohibitions(skill_body):
    rules = section(skill_body, "## Standing Rules")
    lowered = rules.lower()
    assert "webfetch is for triage only" in lowered
    assert "you do not mint domain insights" in lowered and "/research" in rules
    assert "you do not write registry files" in lowered
    assert "never yours to waive" in lowered and "no flag" in lowered


def test_the_skill_names_the_three_decisions_it_leaves_to_the_agent(skill_body):
    decisions = _paragraph_with(skill_body, "You decide three things")
    for decision in ("search queries", "keeper", "three sentences"):
        assert decision in decisions


def test_the_skill_documents_every_request_field(skill_body):
    request = section(skill_body, "## The Request")
    (example,) = fenced_blocks(request, "json")
    for field in (
        "request_id",
        "question",
        "consumer",
        "gap_type",
        "priority",
        "where_to_look",
        "limits",
    ):
        assert f'"{field}"' in example
        assert f"`{field}`" in request


def test_the_skill_reports_blocker_itself_when_open_refuses_a_malformed_request(skill_body):
    refusal = _paragraph_with(section(skill_body, "### 1. Open the run"), "Exit 2")
    assert "malformed" in refusal and "`BLOCKER` yourself" in refusal


def test_the_skill_reads_the_three_seam_repair_reasons_as_repairs(skill_body):
    row = next(
        line
        for line in skill_body.splitlines()
        if all(prefix in line for prefix in SEAM_REPAIR_PREFIXES)
    )
    assert row.startswith("| `precondition_failed`")
    assert "repair" in row and "do not retry" in row


def test_the_skill_lists_the_four_classes(skill_body):
    classes = section(skill_body, "## The Four Return Classes")
    for klass in ("REGISTERED", "BOUNDED_NEGATIVE", "OPERATOR_QUEUE", "BLOCKER"):
        assert f"| `{klass}` |" in classes


# --- the guide -------------------------------------------------------------------------


@pytest.mark.parametrize("call", research_invocations(GUIDE.read_text(encoding="utf-8")))
def test_every_call_the_guide_shows_parses_under_the_cli(call):
    research_parser().parse_args(["research", *call])


def test_the_guide_shows_every_subcommand(guide_body):
    used = {call[0] for call in research_invocations(guide_body)}
    assert used == {
        "open",
        "log",
        "close",
        "register",
        "retire",
        "verify",
        "sources",
        "add-entry",
        "remove-entry",
    }


def test_the_guide_covers_all_four_return_classes(guide_body):
    classes = section(guide_body, "## The four return classes")
    for klass in ("REGISTERED", "BOUNDED_NEGATIVE", "OPERATOR_QUEUE", "BLOCKER"):
        assert f"| `{klass}` |" in classes


def test_the_guides_blocker_example_is_a_fault_logged_after_open(guide_body):
    blocker = _paragraph_with(section(guide_body, "## The four return classes"), "log --fault")
    assert "BLOCKER" in blocker and "exit 2" in blocker


def test_the_guide_covers_the_three_operator_actions_and_the_blind_spot(guide_body):
    for heading in (
        "## Act on a queued source",
        "## Act on a bounded negative",
        "## Read a `verify` report",
    ):
        assert heading in guide_body.splitlines()
    blind_spot = section(guide_body, "## What this does not protect you from")
    assert "term scan" in blind_spot and "read what you register" in blind_spot.lower()


def test_acting_on_a_queue_reads_the_seam_repair_reasons_as_repairs(guide_body):
    queue = section(guide_body, "## Act on a queued source")
    repair = _paragraph_with(queue, SEAM_REPAIR_PREFIXES[0])
    assert all(prefix in repair for prefix in SEAM_REPAIR_PREFIXES)
    assert "repair" in repair


def test_the_guide_names_the_capture_gaps(guide_body):
    gaps = section(guide_body, "## Known capture gaps")
    for gap in ("file://", "raw.pdf", "re-encoded", "flat"):
        assert gap in gaps


def test_verify_kinds_are_all_documented(guide_body):
    report = section(guide_body, "## Read a `verify` report")
    for kind in (
        "orphan_source_dir",
        "row_without_block",
        "unresolvable_path",
        "loose_file",
        "retired_reappeared",
        "block_without_row",
    ):
        assert f"| `{kind}` |" in report


def test_the_guide_says_a_retired_title_reuses_its_slug(guide_body):
    reuse = _paragraph_with(guide_body, "reuses")
    assert "retired" in reuse and "retired_reappeared" in reuse


def test_the_guide_records_the_identity_decision(guide_body):
    decisions = section(guide_body, "## Decisions")
    assert "SHA-256 of its raw bytes as fetched" in decisions
    assert "2026-08-25" in decisions


# --- the hook guide ----------------------------------------------------------------------


def test_the_hook_guide_gives_the_configuration_and_the_loading_rules(guide_body):
    hook = section(guide_body, "## The hold-out hook")
    assert HOOK_TABLE in fenced_blocks(hook, "toml")
    assert "import on its own" in hook
    assert "project root" in hook
    assert SEAM_REPAIR_PREFIXES[0] in hook


def test_the_hook_guides_example_guard_loads_and_answers(guide_body, tmp_path):
    """The example in the guide is a working guard: configured as shown, it bars a term and a path."""
    hook = section(guide_body, "## The hold-out hook")
    (example_guard,) = fenced_blocks(hook, "python")
    (config,) = fenced_blocks(hook, "toml")
    guard_file = tmp_path / "scripts" / "holdout_guard.py"
    guard_file.parent.mkdir()
    guard_file.write_text(example_guard, encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(config, encoding="utf-8")
    sealed = tmp_path / "sealed.md"
    sealed.write_text("An appendix of the Sealed-Widget-Report.\n", encoding="utf-8")

    guard = load_holdout_guard(tmp_path)

    term = first_term_hit(guard, "see the sealed-widget-report, table 3")
    assert term is not None and term.rule_id == "term:sealed-widget-report"
    assert term.offsets == (8,)
    path = input_path_hit(guard, Path("knowledge/sealed/report.pdf"))
    assert path is not None and path.rule_id.startswith("path:")
    assert first_file_hit(guard, sealed) is not None
    assert first_term_hit(guard, "an open widget datasheet") is None
    assert input_path_hit(guard, Path("inbox/datasheet.pdf")) is None
