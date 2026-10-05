"""Tests for the PM operations module."""

import datetime
import difflib
from pathlib import Path

import pytest
import yaml

from agentic_mbse.pm import (
    BacklogData,
    parse_architecture,
    parse_backlog,
    parse_frontmatter,
    parse_knowledge,
    parse_overview,
    parse_requirements,
    parse_traceability,
    parse_validation_matrix,
)
from agentic_mbse.pm.operations import (
    _append_csv_row,
    _append_table_row,
    _format_decision_entry,
    _format_insight_entry,
    _format_table_row,
    _next_id,
    _registry_ids,
    _render_backlog_body,
    _single_match,
    _update_frontmatter_fields,
    _write_backlog,
)
from agentic_mbse.pm.parser import _split_table_row
from agentic_mbse.pm.types import (
    DecisionEntry,
    DecisionStatus,
    EpicEntry,
    EpicStatus,
    GoalInput,
    InsightEntry,
    InsightInput,
    InsightStatus,
    Priority,
    QuestionInput,
    StandaloneEntry,
    VerificationStatus,
    WorkItemEntry,
    WorkItemScale,
    WorkItemStatus,
)

TEMPLATES = Path(__file__).parent.parent / "project_templates"


# ---------------------------------------------------------------------------
# Phase 1: Foundation helpers
# ---------------------------------------------------------------------------


class TestNextId:
    def test_empty_list(self):
        assert _next_id("DI", []) == "DI-001"

    def test_sequential(self):
        assert _next_id("DI", ["DI-001", "DI-002"]) == "DI-003"

    def test_gap_uses_highest(self):
        assert _next_id("PR", ["PR-001", "PR-005"]) == "PR-006"

    def test_all_prefixes(self):
        for prefix in ("DI", "PR", "AD", "SV", "G", "AQ", "WI"):
            result = _next_id(prefix, [])
            assert result == f"{prefix}-001"

    def test_ignores_mismatched_prefix(self):
        assert _next_id("DI", ["PR-001", "PR-002"]) == "DI-001"


# design.md Appendix A: (text in the registry file, prefix, numbers it reserves)
_APPENDIX_A = [
    ("MAG-001", "G", []),
    ("`SV-034`", "SV", [34]),
    ("PR-1", "PR", [1]),
    ("SV-034a", "SV", [34]),
    ("SV-034-x", "SV", [34]),
    ("DI-001-DI-014", "DI", [1, 14]),
    ("X-SV-001", "SV", [1]),
    ("**PR-007**", "PR", [7]),
    ("id: WI-002", "WI", [2]),
    ("DI-001 through DI-014", "DI", [1, 14]),
    ("<!-- SV-900 -->", "SV", []),
    ("<!-- unclosed SV-900", "SV", [900]),
]


class TestRegistryIds:
    @pytest.mark.parametrize(("text", "prefix", "numbers"), _APPENDIX_A)
    def test_token_boundary(self, tmp_path, text, prefix, numbers):
        path = tmp_path / "REGISTRY.md"
        path.write_text(text + "\n", encoding="utf-8")
        found = _registry_ids(path, prefix, []).data
        assert sorted({int(t.split("-")[1]) for t in found}) == numbers

    def test_skips_html_comments(self, tmp_path):
        path = tmp_path / "VALIDATION_MATRIX.md"
        path.write_text(
            "<!-- Example:\n| SV-900 | x |\n-->\n| SV-001 | y |\n<!-- SV-901 --> SV-002\n",
            encoding="utf-8",
        )
        assert _registry_ids(path, "SV", []).data == ["SV-001", "SV-002"]

    @pytest.mark.parametrize(
        ("template", "prefix"),
        [
            ("KNOWLEDGE.md.template", "DI"),
            ("ARCHITECTURE.md.template", "AD"),
            ("REQUIREMENTS.md.template", "PR"),
            ("VALIDATION_MATRIX.md.template", "SV"),
            ("OVERVIEW.md.template", "G"),
            ("OVERVIEW.md.template", "AQ"),
            ("BACKLOG.md.template", "WI"),
        ],
    )
    def test_templates_reserve_nothing(self, template, prefix):
        # B2: every registry template holds its example IDs inside HTML comments only
        result = _registry_ids(TEMPLATES / template, prefix, [])
        assert result.data == []
        assert result.warnings == []

    def test_data_is_parsed_ids_then_tokens(self, tmp_path):
        path = tmp_path / "VALIDATION_MATRIX.md"
        path.write_text("| SV-001 | a |\n| SV-002 | b |\n", encoding="utf-8")
        assert _registry_ids(path, "SV", ["SV-001"]).data == ["SV-001", "SV-001", "SV-002"]

    def test_one_warning_per_unparsed_number_at_first_spelling(self, tmp_path):
        path = tmp_path / "VALIDATION_MATRIX.md"
        path.write_text(
            "SV-001 parsed. SV-34 cited, then SV-034, SV-040, SV-040.\n", encoding="utf-8"
        )
        result = _registry_ids(path, "SV", ["SV-001"])
        assert [w.location for w in result.warnings] == ["SV-34", "SV-040"]
        assert all(w.file == str(path) for w in result.warnings)
        assert result.warnings[0].message.startswith("SV-34 is named in VALIDATION_MATRIX.md")
        assert "reserved" in result.warnings[0].message

    def test_parsed_id_covers_padded_mention(self, tmp_path):
        path = tmp_path / "REQUIREMENTS.md"
        path.write_text("| PR-1 | r |\n\nSee PR-001.\n", encoding="utf-8")
        result = _registry_ids(path, "PR", ["PR-1"])
        assert result.warnings == []
        assert _next_id("PR", result.data) == "PR-002"

    def test_missing_file_returns_parsed_ids(self, tmp_path):
        result = _registry_ids(tmp_path / "VALIDATION_MATRIX.md", "SV", ["SV-001"])
        assert result.data == ["SV-001"]
        assert result.warnings == []


class TestSingleMatch:
    def test_returns_the_one_pair(self):
        assert _single_match([("line 5", 4)], "SV-001", "VALIDATION_MATRIX.md") == ("line 5", 4)

    def test_no_match_is_not_found(self):
        with pytest.raises(ValueError) as excinfo:
            _single_match([], "SV-001", "VALIDATION_MATRIX.md")
        assert str(excinfo.value) == "SV-001 not found in VALIDATION_MATRIX.md"

    def test_several_matches_name_every_location(self):
        matches = [("epics[0]", {}), ("epics[2]", {}), ("epics[3]", {})]
        with pytest.raises(ValueError) as excinfo:
            _single_match(matches, "Epic 'X'", "BACKLOG.md")
        message = str(excinfo.value)
        assert message.startswith("Epic 'X' appears 3 times in BACKLOG.md")
        assert all(location in message for location, _ in matches)
        assert "by hand" in message


class TestRenderBacklogBody:
    def test_empty_state(self):
        body = _render_backlog_body(BacklogData(epics=[], standalone=[]))
        assert "No epics or work items yet" in body

    def test_epic_with_items(self):
        data = BacklogData(
            epics=[
                EpicEntry(
                    name="Test Epic",
                    goal="G-001",
                    priority=Priority.P0,
                    status=EpicStatus.ACTIVE,
                    file="backlog/epic-test.md",
                    items=[
                        WorkItemEntry(
                            id="WI-001",
                            name="First item",
                            scale=WorkItemScale.STANDARD,
                            status=WorkItemStatus.ACTIVE,
                        ),
                        WorkItemEntry(
                            id="WI-002",
                            name="Done item",
                            scale=WorkItemScale.TRIVIAL,
                            status=WorkItemStatus.COMPLETED,
                            completed="2026-01-15",
                        ),
                    ],
                )
            ],
            standalone=[],
        )
        body = _render_backlog_body(data)
        assert "## Epic: Test Epic" in body
        assert "**Goal**: G-001" in body
        assert "| WI-001 | First item |" in body
        assert "| WI-002 | Done item |" in body
        assert "Completed 2026-01-15" in body

    def test_standalone_items(self):
        data = BacklogData(
            epics=[],
            standalone=[
                StandaloneEntry(
                    id="WI-010",
                    name="Standalone task",
                    scale=WorkItemScale.TRIVIAL,
                    priority=Priority.P1,
                    status=WorkItemStatus.BACKLOG,
                )
            ],
        )
        body = _render_backlog_body(data)
        assert "## Standalone Items" in body
        assert "| WI-010 | Standalone task |" in body
        assert "| P1 |" in body


class TestWriteBacklogRoundTrip:
    def test_round_trip(self, tmp_path):
        data = BacklogData(
            epics=[
                EpicEntry(
                    name="Round Trip Epic",
                    goal="G-001",
                    priority=Priority.P0,
                    status=EpicStatus.ACTIVE,
                    file="backlog/epic-roundtrip.md",
                    items=[
                        WorkItemEntry(
                            id="WI-001",
                            name="Some work",
                            scale=WorkItemScale.STANDARD,
                            status=WorkItemStatus.ACTIVE,
                        ),
                    ],
                )
            ],
            standalone=[
                StandaloneEntry(
                    id="WI-010",
                    name="Standalone",
                    scale=WorkItemScale.TRIVIAL,
                    priority=Priority.P2,
                    status=WorkItemStatus.BACKLOG,
                ),
            ],
        )
        path = tmp_path / "BACKLOG.md"
        _write_backlog(path, data)

        # Parse it back
        result = parse_backlog(path)
        assert len(result.data.epics) == 1
        assert result.data.epics[0].name == "Round Trip Epic"
        assert result.data.epics[0].items[0].id == "WI-001"
        assert len(result.data.standalone) == 1
        assert result.data.standalone[0].id == "WI-010"

        # Write again and verify stability
        first_content = path.read_text(encoding="utf-8")
        _write_backlog(path, result.data)
        second_content = path.read_text(encoding="utf-8")
        assert first_content == second_content


class TestFormatInsightEntry:
    def _make_entry(self, **kwargs):
        defaults = dict(
            id="DI-001",
            title="Test Insight",
            source="research.md",
            context="A domain fact.",
            model_implications="Must model X",
            analysis_implications="Enables Y",
            status=InsightStatus.CAPTURED,
        )
        defaults.update(kwargs)
        return InsightEntry(**defaults)

    def test_with_rationale(self):
        entry = self._make_entry(rationale="Because physics")
        output = _format_insight_entry(entry)
        assert "- **Rationale**: Because physics" in output

    def test_without_rationale(self):
        entry = self._make_entry(rationale=None)
        output = _format_insight_entry(entry)
        assert "Rationale" not in output

    def test_round_trip(self, tmp_path):
        entry = self._make_entry()
        text = _format_insight_entry(entry)
        # Write to a file with the KNOWLEDGE.md header
        path = tmp_path / "KNOWLEDGE.md"
        path.write_text("# Domain Knowledge\n\n" + text, encoding="utf-8")
        result = parse_knowledge(path)
        assert len(result.data) == 1
        parsed = result.data[0]
        assert parsed.id == "DI-001"
        assert parsed.title == "Test Insight"
        assert parsed.source == "research.md"
        assert parsed.context == "A domain fact."
        assert parsed.status == InsightStatus.CAPTURED


class TestFormatDecisionEntry:
    def test_round_trip(self, tmp_path):
        entry = DecisionEntry(
            id="AD-001",
            title="Use metric units",
            decision="All models use SI units",
            rationale="Consistency",
            date="2026-02-01",
            status=DecisionStatus.ACTIVE,
        )
        text = _format_decision_entry(entry)
        path = tmp_path / "ARCHITECTURE.md"
        path.write_text("# Model Architecture\n\n## Key Decisions\n\n" + text, encoding="utf-8")
        result = parse_architecture(path)
        assert len(result.data) == 1
        parsed = result.data[0]
        assert parsed.id == "AD-001"
        assert parsed.title == "Use metric units"
        assert parsed.decision == "All models use SI units"
        assert parsed.status == DecisionStatus.ACTIVE


class TestFormatTableRow:
    def test_basic(self):
        row = _format_table_row(["PR-001", "All X SHALL Y", "DI-001", "Review", "Check"])
        assert row == "| PR-001 | All X SHALL Y | DI-001 | Review | Check |"

    def test_escapes_pipes(self):
        row = _format_table_row(["SV-001", "|x| < 1", "ends in \\"])
        assert row == "| SV-001 | \\|x\\| < 1 | ends in \\ |"
        assert _split_table_row(row) == ["SV-001", "|x| < 1", "ends in \\"]


class TestAppendTableRow:
    def test_append_to_existing_table(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text(
            "# Title\n\n## Requirements\n\n| ID | Req |\n|-----|-----|\n| PR-001 | First |\n",
            encoding="utf-8",
        )
        _append_table_row(path, "## Requirements", "| PR-002 | Second |")
        content = path.read_text(encoding="utf-8")
        assert "| PR-001 | First |" in content
        assert "| PR-002 | Second |" in content

    def test_append_to_empty_table(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text(
            "## Requirements\n\n| ID | Req |\n|-----|-----|\n",
            encoding="utf-8",
        )
        _append_table_row(path, "## Requirements", "| PR-001 | First |")
        content = path.read_text(encoding="utf-8")
        assert "| PR-001 | First |" in content

    def test_preserves_content_after_table(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text(
            "## Requirements\n\n"
            "| ID | Req |\n"
            "|-----|-----|\n"
            "| PR-001 | First |\n\n"
            "## Next Section\n\nSome content\n",
            encoding="utf-8",
        )
        _append_table_row(path, "## Requirements", "| PR-002 | Second |")
        content = path.read_text(encoding="utf-8")
        assert "| PR-002 | Second |" in content
        assert "## Next Section" in content
        assert "Some content" in content


class TestAppendCsvRow:
    def test_append_to_existing_csv(self, tmp_path):
        path = tmp_path / "data.csv"
        path.write_text("Element,File,Type\nFoo,bar.sysml,part def\n", encoding="utf-8")
        _append_csv_row(path, {"Element": "Baz", "File": "qux.sysml", "Type": "calc def"})
        content = path.read_text(encoding="utf-8")
        assert "Baz" in content
        assert "qux.sysml" in content

    def test_creates_csv_with_headers(self, tmp_path):
        path = tmp_path / "data.csv"
        _append_csv_row(path, {"Element": "Foo", "File": "bar.sysml", "Type": "part def"})
        content = path.read_text(encoding="utf-8")
        assert "Element,File,Type" in content
        assert "Foo" in content


class TestUpdateFrontmatterFields:
    def test_update_status(self, tmp_path):
        path = tmp_path / "spec.md"
        path.write_text("---\nStatus: active\nOwner: Reid\n---\n# Body\n", encoding="utf-8")
        _update_frontmatter_fields(path, {"Status": "completed"})
        content = path.read_text(encoding="utf-8")
        assert "Status: completed" in content
        assert "Owner: Reid" in content
        assert "# Body" in content

    def test_preserves_unknown_fields(self, tmp_path):
        path = tmp_path / "spec.md"
        path.write_text("---\nStatus: active\nCustom: hello\n---\n# Body\n", encoding="utf-8")
        _update_frontmatter_fields(path, {"Status": "completed"})
        content = path.read_text(encoding="utf-8")
        assert "Custom: hello" in content

    def test_preserves_body(self, tmp_path):
        path = tmp_path / "spec.md"
        path.write_text(
            "---\nStatus: active\n---\n# Title\n\nParagraph content.\n",
            encoding="utf-8",
        )
        _update_frontmatter_fields(path, {"Status": "completed", "Updated": "2026-02-02"})
        content = path.read_text(encoding="utf-8")
        assert "Paragraph content." in content
        assert "Updated: '2026-02-02'" in content or "Updated: 2026-02-02" in content


# ---------------------------------------------------------------------------
# Phase 2: Simple append operations
# ---------------------------------------------------------------------------


def _setup_knowledge(tmp_path):
    """Create a minimal project with KNOWLEDGE.md."""
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    src = TEMPLATES / "KNOWLEDGE.md.template"
    (kdir / "KNOWLEDGE.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def _setup_requirements(tmp_path):
    """Create a minimal project with REQUIREMENTS.md."""
    mdir = tmp_path / "modeling_project"
    mdir.mkdir()
    src = TEMPLATES / "REQUIREMENTS.md.template"
    (mdir / "REQUIREMENTS.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def _setup_architecture(tmp_path):
    """Create a minimal project with ARCHITECTURE.md."""
    mdir = tmp_path / "modeling_project"
    mdir.mkdir(exist_ok=True)
    src = TEMPLATES / "ARCHITECTURE.md.template"
    (mdir / "ARCHITECTURE.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def _setup_validation_matrix(tmp_path):
    """Create a minimal project with VALIDATION_MATRIX.md."""
    mdir = tmp_path / "modeling_project"
    mdir.mkdir(exist_ok=True)
    src = TEMPLATES / "VALIDATION_MATRIX.md.template"
    (mdir / "VALIDATION_MATRIX.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


# The E1 reproduction rows. The labels are the reverse of fusion-tea's matrix by design:
# here SV-034 is the escaped (valid) row and SV-035 the malformed one.
_E1_ROWS = {
    "valid": "| SV-033 | plain | baseline | test | x | 1e-6 | s | t | passing |",
    "escaped": "| SV-034 | bar (\\|rel dev\\| <= 1e-6) | baseline | test | x | 1e-6 | s | t | passing |",
    "malformed": "| SV-035 | bar (|rel dev| <= 1e-6) | baseline | test | x | 1e-6 | s | t | passing |",
}


def _write_matrix(root, rows):
    """Write a VALIDATION_MATRIX.md holding only the registry table with the given rows."""
    mdir = root / "modeling_project"
    mdir.mkdir(exist_ok=True)
    path = mdir / "VALIDATION_MATRIX.md"
    path.write_text(
        "## Verification Registry\n\n"
        "| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |\n"
        "|----|-------------|------|-----------|----------|-----------|--------|------|--------|\n"
        + "".join(row + "\n" for row in rows),
        encoding="utf-8",
    )
    return path


def _file_bytes(root):
    """Map every file under root to its bytes, so a refusal test can show nothing changed."""
    return {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def _insight(di_id):
    """Return a valid captured InsightEntry with the given ID."""
    return InsightEntry(
        id=di_id,
        title=f"Insight {di_id}",
        source="s",
        context="c",
        model_implications="m",
        analysis_implications="a",
        status=InsightStatus.CAPTURED,
    )


def _write_knowledge(root, text):
    """Write knowledge/KNOWLEDGE.md with the given text and return its path."""
    kdir = root / "knowledge"
    kdir.mkdir(exist_ok=True)
    path = kdir / "KNOWLEDGE.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_archived_knowledge(root):
    """Write fusion-tea's KNOWLEDGE.md shape: DI-001 to DI-011 under a note naming DI-014."""
    records = "\n".join(_format_insight_entry(_insight(f"DI-{n:03d}")) for n in range(1, 12))
    note = "Previous entries (DI-001 through DI-014) archived.\n\n"
    return _write_knowledge(root, "# Domain Knowledge\n\n" + note + records)


def _decision(ad_id):
    """Return a valid active DecisionEntry with the given ID."""
    return DecisionEntry(
        id=ad_id,
        title=f"Decision {ad_id}",
        decision="d",
        rationale="r",
        date="2026-01-01",
        status=DecisionStatus.ACTIVE,
    )


def _assert_one_record_added(before, after, new_id, *, table):
    """Assert the write added one contiguous block holding the new record, and nothing else.

    The block is the record plus its blank separators: one row for a table registry,
    the heading and field lines for a heading registry. Exactly one added line names new_id.
    """
    a, b = before.splitlines(), after.splitlines()
    ops = [op for op in difflib.SequenceMatcher(None, a, b).get_opcodes() if op[0] != "equal"]
    assert len(ops) == 1 and ops[0][0] == "insert"
    added = b[ops[0][3] : ops[0][4]]
    assert sum(new_id in line for line in added) == 1
    if table:
        assert len([line for line in added if line.strip()]) == 1


def _comment_example_above_table(path, heading, example_row):
    """Put a commented example table between heading and the real table (audit A1's layout).

    Returns the comment block, so a test can check the write left it unchanged.
    """
    example = f"<!-- Example:\n{example_row}\n-->\n\n"
    text = path.read_text(encoding="utf-8")
    assert text.count(f"{heading}\n\n") == 1
    path.write_text(text.replace(f"{heading}\n\n", f"{heading}\n\n{example}"), encoding="utf-8")
    return example


class TestAddInsight:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        root = _setup_knowledge(tmp_path)
        result = add_insight(
            root,
            title="HTS magnets are expensive",
            source="research.md",
            context="A domain fact.",
            model_implications="Must model cost",
            analysis_implications="Enables cost analysis",
        )
        assert result.success
        assert result.ids_assigned["DI"] == "DI-001"
        # Verify via parser
        parsed = parse_knowledge(root / "knowledge" / "KNOWLEDGE.md")
        assert len(parsed.data) == 1
        assert parsed.data[0].title == "HTS magnets are expensive"

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        root = _setup_knowledge(tmp_path)
        r1 = add_insight(
            root,
            title="First",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        r2 = add_insight(
            root,
            title="Second",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        assert r1.ids_assigned["DI"] == "DI-001"
        assert r2.ids_assigned["DI"] == "DI-002"

    def test_missing_field(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        root = _setup_knowledge(tmp_path)
        result = add_insight(
            root,
            title="",
            source="x",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        assert not result.success
        assert "title" in result.message.lower()

    def test_with_rationale(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        root = _setup_knowledge(tmp_path)
        result = add_insight(
            root,
            title="Fact",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
            rationale="Because physics",
        )
        assert result.success
        parsed = parse_knowledge(root / "knowledge" / "KNOWLEDGE.md")
        assert parsed.data[0].rationale == "Because physics"

    def test_archive_note_reserves_di_014(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        _write_archived_knowledge(tmp_path)
        result = add_insight(
            tmp_path,
            title="t",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        assert result.ids_assigned["DI"] == "DI-015"

    def test_mints_above_unparsed_record(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight

        dropped = _format_insight_entry(_insight("DI-002")).replace("captured", "bogus")
        path = _write_knowledge(
            tmp_path, _format_insight_entry(_insight("DI-001")) + "\n" + dropped
        )
        assert [e.id for e in parse_knowledge(path).data] == ["DI-001"]
        before = path.read_text(encoding="utf-8")
        result = add_insight(
            tmp_path,
            title="t",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        assert result.ids_assigned["DI"] == "DI-003"
        _assert_one_record_added(before, path.read_text(encoding="utf-8"), "DI-003", table=False)


class TestSaveResearch:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import save_research

        result = save_research(tmp_path, topic="HTS magnets", content="# Research\nSome content")
        assert result.success
        assert len(result.files_modified) == 1
        saved_path = Path(result.files_modified[0])
        assert saved_path.exists()
        assert "hts-magnets" in saved_path.name

    def test_creates_pending_dir(self, tmp_path):
        from agentic_mbse.pm.operations import save_research

        pending_dir = tmp_path / "knowledge" / "research" / "pending"
        assert not pending_dir.exists()
        save_research(tmp_path, topic="Test", content="x")
        assert pending_dir.exists()

    def test_kebab_case(self, tmp_path):
        from agentic_mbse.pm.operations import save_research

        result = save_research(tmp_path, topic="Cost Model Updates!", content="x")
        assert result.success
        saved_path = Path(result.files_modified[0])
        assert "cost-model-updates" in saved_path.name

    def test_empty_topic(self, tmp_path):
        from agentic_mbse.pm.operations import save_research

        result = save_research(tmp_path, topic="", content="x")
        assert not result.success


class TestPromoteRequirement:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        result = promote_requirement(
            root,
            requirement="All X SHALL Y",
            source="DI-001",
            enforcement="Design review",
            validation_method="Manual check",
        )
        assert result.success
        assert result.ids_assigned["PR"] == "PR-001"
        parsed = parse_requirements(root / "modeling_project" / "REQUIREMENTS.md")
        assert len(parsed.data) == 1
        assert parsed.data[0].requirement == "All X SHALL Y"

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        r1 = promote_requirement(
            root, requirement="First", source="DI-001", enforcement="e", validation_method="v"
        )
        r2 = promote_requirement(
            root, requirement="Second", source="G-001", enforcement="e", validation_method="v"
        )
        assert r1.ids_assigned["PR"] == "PR-001"
        assert r2.ids_assigned["PR"] == "PR-002"

    def test_invalid_source_pattern(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        result = promote_requirement(
            root, requirement="R", source="invalid", enforcement="e", validation_method="v"
        )
        assert not result.success
        assert "DI-XXX or G-XXX" in result.message

    def test_value_with_pipe_round_trips(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        result = promote_requirement(
            root,
            requirement="Margin SHALL keep |dT| under 5 K",
            source="DI-001",
            enforcement="e",
            validation_method="v",
        )
        assert result.success
        parsed = parse_requirements(root / "modeling_project" / "REQUIREMENTS.md")
        assert parsed.data[0].requirement == "Margin SHALL keep |dT| under 5 K"
        assert parsed.data[0].source == "DI-001"
        assert parsed.data[0].validation_method == "v"

    def test_refuses_line_break(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        before = _file_bytes(root)
        result = promote_requirement(
            root,
            requirement="First line\nsecond line",
            source="DI-001",
            enforcement="e",
            validation_method="v",
        )
        assert not result.success
        assert "First line\\nsecond line" in result.message
        assert _file_bytes(root) == before

    def test_mints_above_unparsed_record(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        mdir = tmp_path / "modeling_project"
        mdir.mkdir()
        path = mdir / "REQUIREMENTS.md"
        path.write_text(
            "## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-001 | r | DI-001 | e | v |\n"
            "| **PR-002** | r | DI-001 | e | v |\n",
            encoding="utf-8",
        )
        assert [e.id for e in parse_requirements(path).data] == ["PR-001"]
        before = path.read_text(encoding="utf-8")
        result = promote_requirement(
            tmp_path, requirement="new", source="DI-001", enforcement="e", validation_method="v"
        )
        assert result.ids_assigned["PR"] == "PR-003"
        _assert_one_record_added(before, path.read_text(encoding="utf-8"), "PR-003", table=True)

    @pytest.mark.parametrize(
        "text",
        [
            "# Requirements\n\nNo table yet.\n",
            "## Requirements\n\nNo table yet.\n",
            "## Requirements\n\nNo table yet.\n\n## Glossary\n\n| Term | Meaning |\n|---|---|\n",
        ],
        ids=["no heading", "no table", "table only in a later section"],
    )
    def test_missing_section_refuses(self, tmp_path, text):
        from agentic_mbse.pm.operations import promote_requirement

        mdir = tmp_path / "modeling_project"
        mdir.mkdir()
        (mdir / "REQUIREMENTS.md").write_text(text, encoding="utf-8")
        before = _file_bytes(tmp_path)
        result = promote_requirement(
            tmp_path, requirement="r", source="DI-001", enforcement="e", validation_method="v"
        )
        assert not result.success
        assert "'## Requirements'" in result.message
        assert "REQUIREMENTS.md" in result.message
        assert _file_bytes(tmp_path) == before

    def test_skips_commented_table_above_real_table(self, tmp_path):
        from agentic_mbse.pm.operations import promote_requirement

        root = _setup_requirements(tmp_path)
        path = root / "modeling_project" / "REQUIREMENTS.md"
        example = _comment_example_above_table(
            path, "## Requirements", "| PR-001 | ex | DI-001 | e | v |"
        )
        first = promote_requirement(
            root, requirement="first", source="DI-001", enforcement="e", validation_method="v"
        )
        assert [(e.id, e.requirement) for e in parse_requirements(path).data] == [
            ("PR-001", "first")
        ]
        second = promote_requirement(
            root, requirement="second", source="DI-001", enforcement="e", validation_method="v"
        )
        assert [first.ids_assigned["PR"], second.ids_assigned["PR"]] == ["PR-001", "PR-002"]
        assert [e.id for e in parse_requirements(path).data] == ["PR-001", "PR-002"]
        assert example in path.read_text(encoding="utf-8")


class TestRegisterDecision:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import register_decision

        root = _setup_architecture(tmp_path)
        result = register_decision(
            root,
            title="Use metric units",
            decision="All models use SI units",
            rationale="Consistency across subsystems",
        )
        assert result.success
        assert result.ids_assigned["AD"] == "AD-001"
        parsed = parse_architecture(root / "modeling_project" / "ARCHITECTURE.md")
        assert len(parsed.data) == 1
        assert parsed.data[0].title == "Use metric units"
        assert parsed.data[0].status == DecisionStatus.ACTIVE

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import register_decision

        root = _setup_architecture(tmp_path)
        r1 = register_decision(root, title="First", decision="d", rationale="r")
        r2 = register_decision(root, title="Second", decision="d", rationale="r")
        assert r1.ids_assigned["AD"] == "AD-001"
        assert r2.ids_assigned["AD"] == "AD-002"

    def test_missing_field(self, tmp_path):
        from agentic_mbse.pm.operations import register_decision

        root = _setup_architecture(tmp_path)
        result = register_decision(root, title="", decision="d", rationale="r")
        assert not result.success

    def test_mints_above_unparsed_record(self, tmp_path):
        from agentic_mbse.pm.operations import register_decision

        dropped = _format_decision_entry(_decision("AD-002")).replace("active", "bogus")
        mdir = tmp_path / "modeling_project"
        mdir.mkdir()
        path = mdir / "ARCHITECTURE.md"
        path.write_text(
            "# Model Architecture\n\n## Key Decisions\n\n"
            + _format_decision_entry(_decision("AD-001"))
            + "\n"
            + dropped,
            encoding="utf-8",
        )
        assert [e.id for e in parse_architecture(path).data] == ["AD-001"]
        before = path.read_text(encoding="utf-8")
        result = register_decision(tmp_path, title="t", decision="d", rationale="r")
        assert result.ids_assigned["AD"] == "AD-003"
        _assert_one_record_added(before, path.read_text(encoding="utf-8"), "AD-003", table=False)


class TestAddValidation:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        result = add_validation(
            root,
            description="Total cost ballpark",
            type="reasonableness",
            mechanism="test",
            expected="$3B-$15B",
            tolerance="range",
            source="engineering judgment",
            test="test_capital_cost_range",
        )
        assert result.success
        assert result.ids_assigned["SV"] == "SV-001"
        parsed = parse_validation_matrix(root / "modeling_project" / "VALIDATION_MATRIX.md")
        assert len(parsed.data) == 1
        assert parsed.data[0].description == "Total cost ballpark"
        assert parsed.data[0].status == VerificationStatus.PENDING

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        r1 = add_validation(
            root,
            description="First",
            type="reasonableness",
            mechanism="test",
            expected="x",
            tolerance="t",
        )
        r2 = add_validation(
            root,
            description="Second",
            type="baseline",
            mechanism="manual",
            expected="y",
            tolerance="t",
        )
        assert r1.ids_assigned["SV"] == "SV-001"
        assert r2.ids_assigned["SV"] == "SV-002"

    def test_invalid_type(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        result = add_validation(
            root, description="X", type="invalid", mechanism="test", expected="x", tolerance="t"
        )
        assert not result.success
        assert "type" in result.message.lower()

    def test_invalid_mechanism(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        result = add_validation(
            root,
            description="X",
            type="reasonableness",
            mechanism="invalid",
            expected="x",
            tolerance="t",
        )
        assert not result.success
        assert "mechanism" in result.message.lower()

    def test_value_with_pipe_round_trips(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        result = add_validation(
            root,
            description="bar (|rel dev| <= 1e-6)",
            type="baseline",
            mechanism="test",
            expected="|a - b| < 2",
            tolerance="t",
        )
        assert result.success
        parsed = parse_validation_matrix(root / "modeling_project" / "VALIDATION_MATRIX.md")
        assert parsed.warnings == []
        assert parsed.data[0].description == "bar (|rel dev| <= 1e-6)"
        assert parsed.data[0].expected == "|a - b| < 2"
        assert parsed.data[0].type.value == "baseline"

    def test_refuses_comment_marker(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        before = _file_bytes(root)
        result = add_validation(
            root,
            description="see <!-- note",
            type="baseline",
            mechanism="test",
            expected="x",
            tolerance="t",
        )
        assert not result.success
        assert "'<!--'" in result.message
        assert "see <!-- note" in result.message
        assert _file_bytes(root) == before

    def test_e1_three_record_reproduction(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        vm = _write_matrix(tmp_path, list(_E1_ROWS.values()))
        parsed = parse_validation_matrix(vm)
        assert [e.id for e in parsed.data] == ["SV-033", "SV-034"]
        assert parsed.data[1].description == "bar (|rel dev| <= 1e-6)"
        assert any(w.location == "row 2" for w in parsed.warnings)  # malformed SV-035 stays warned
        result = add_validation(
            tmp_path,
            description="new",
            type="baseline",
            mechanism="test",
            expected="e",
            tolerance="t",
        )
        assert result.ids_assigned["SV"] == "SV-036"

    def test_mints_above_unparsed_record(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        valid = _E1_ROWS["valid"].replace("SV-033", "SV-001")
        dropped = _E1_ROWS["valid"].replace("SV-033", "SV-002").replace("passing", "done")
        vm = _write_matrix(tmp_path, [valid, dropped])
        assert [e.id for e in parse_validation_matrix(vm).data] == ["SV-001"]
        before = vm.read_text(encoding="utf-8")
        result = add_validation(
            tmp_path,
            description="new",
            type="baseline",
            mechanism="test",
            expected="e",
            tolerance="t",
        )
        assert result.ids_assigned["SV"] == "SV-003"
        _assert_one_record_added(before, vm.read_text(encoding="utf-8"), "SV-003", table=True)

    def test_reports_reserved_id_after_parse_warnings(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        vm = _write_matrix(tmp_path, list(_E1_ROWS.values()))
        parse_warnings = parse_validation_matrix(vm).warnings
        assert [w.location for w in parse_warnings] == ["row 2"]
        result = add_validation(
            tmp_path,
            description="new",
            type="baseline",
            mechanism="test",
            expected="e",
            tolerance="t",
        )
        assert result.warnings[: len(parse_warnings)] == parse_warnings
        reserved = result.warnings[len(parse_warnings) :]
        assert [w.location for w in reserved] == ["SV-035"]
        assert reserved[0].file == str(vm)
        assert "SV-035" in reserved[0].message and "reserved" in reserved[0].message

    @pytest.mark.parametrize(
        "text",
        [
            "# Validation Matrix\n\nNo registry yet.\n",
            "## Verification Registry\n\nNo table yet.\n",
            "## Verification Registry\n\nNo table yet.\n\n## Notes\n\n| Note |\n|---|\n",
            "## Verification Registry\n\n<!-- Example:\n| ID | Status |\n|---|---|\n-->\n",
        ],
        ids=["no heading", "no table", "table only in a later section", "table only in a comment"],
    )
    def test_missing_section_refuses(self, tmp_path, text):
        from agentic_mbse.pm.operations import add_validation

        mdir = tmp_path / "modeling_project"
        mdir.mkdir()
        (mdir / "VALIDATION_MATRIX.md").write_text(text, encoding="utf-8")
        before = _file_bytes(tmp_path)
        result = add_validation(
            tmp_path,
            description="d",
            type="baseline",
            mechanism="test",
            expected="e",
            tolerance="t",
        )
        assert not result.success
        assert "'## Verification Registry'" in result.message
        assert "VALIDATION_MATRIX.md" in result.message
        assert _file_bytes(tmp_path) == before

    def test_skips_commented_table_above_real_table(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        root = _setup_validation_matrix(tmp_path)
        vm = root / "modeling_project" / "VALIDATION_MATRIX.md"
        example = _comment_example_above_table(
            vm,
            "## Verification Registry",
            "| SV-001 | ex | baseline | test | x | t |  |  | pending |",
        )
        fields = {"type": "baseline", "mechanism": "test", "expected": "e", "tolerance": "t"}
        first = add_validation(root, description="first", **fields)
        assert [(e.id, e.description) for e in parse_validation_matrix(vm).data] == [
            ("SV-001", "first")
        ]
        second = add_validation(root, description="second", **fields)
        assert [first.ids_assigned["SV"], second.ids_assigned["SV"]] == ["SV-001", "SV-002"]
        assert [e.id for e in parse_validation_matrix(vm).data] == ["SV-001", "SV-002"]
        assert example in vm.read_text(encoding="utf-8")

    def test_refuses_row_that_would_land_in_a_comment(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        # The table's last row opens a comment that closes on the next line
        _write_matrix(tmp_path, [_E1_ROWS["valid"] + " <!-- recheck", "with the owner -->"])
        before = _file_bytes(tmp_path)
        result = add_validation(
            tmp_path,
            description="d",
            type="baseline",
            mechanism="test",
            expected="e",
            tolerance="t",
        )
        assert not result.success
        assert "comment" in result.message and "'## Verification Registry'" in result.message
        assert _file_bytes(tmp_path) == before


# ---------------------------------------------------------------------------
# Phase 3: Cross-file and multi-file operations
# ---------------------------------------------------------------------------


def _setup_overview(tmp_path):
    """Create a minimal project with OVERVIEW.md."""
    mdir = tmp_path / "modeling_project"
    mdir.mkdir(exist_ok=True)
    src = TEMPLATES / "OVERVIEW.md.template"
    (mdir / "OVERVIEW.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def _write_overview(root, goal_rows, question_rows):
    """Write an OVERVIEW.md holding only the goals and questions tables with the given rows."""
    mdir = root / "modeling_project"
    mdir.mkdir(exist_ok=True)
    path = mdir / "OVERVIEW.md"
    path.write_text(
        "## Goals Registry\n\n"
        "| ID | Goal | Priority | Status | Source | Traced Requirements |\n"
        "|----|------|----------|--------|--------|---------------------|\n"
        + "".join(row + "\n" for row in goal_rows)
        + "\n## Analysis Questions\n\n"
        "| ID | Question | Implies | Source | Status |\n"
        "|----|----------|---------|--------|--------|\n"
        + "".join(row + "\n" for row in question_rows),
        encoding="utf-8",
    )
    return path


# Each table holds a valid record and a dropped one with a decorated ID cell.
_OVERVIEW_GOAL_ROWS = [
    "| G-001 | g | P0 | active | s |  |",
    "| **G-002** | g | P0 | active | s |  |",
]
_OVERVIEW_QUESTION_ROWS = ["| AQ-001 | q | i | s | open |", "| **AQ-002** | q | i | s | open |"]


def _setup_traceability(tmp_path):
    """Create a minimal project with traceability_matrix.csv."""
    ddir = tmp_path / "data"
    ddir.mkdir(exist_ok=True)
    src = TEMPLATES / "data" / "traceability_matrix.csv"
    (ddir / "traceability_matrix.csv").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


class TestTraceElement:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import add_insight, promote_requirement, trace_element

        root = _setup_knowledge(tmp_path)
        _setup_requirements(root)
        _setup_traceability(root)
        add_insight(
            root,
            title="Fact",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )
        promote_requirement(
            root, requirement="R", source="DI-001", enforcement="e", validation_method="v"
        )

        result = trace_element(
            root,
            element="MagnetCostCalc",
            file="models/library/magnet_cost.sysml",
            type="calc def",
            knowledge=["DI-001"],
            requirement=["PR-001"],
        )
        assert result.success
        parsed = parse_traceability(root / "data" / "traceability_matrix.csv")
        assert len(parsed.data) == 1
        assert parsed.data[0].element == "MagnetCostCalc"

    def test_invalid_knowledge_id(self, tmp_path):
        from agentic_mbse.pm.operations import trace_element

        root = _setup_knowledge(tmp_path)
        _setup_traceability(root)
        result = trace_element(
            root,
            element="X",
            file="x.sysml",
            type="part def",
            knowledge=["DI-999"],
        )
        assert not result.success
        assert "DI-999" in result.message

    def test_duplicate_rejected(self, tmp_path):
        from agentic_mbse.pm.operations import trace_element

        root = _setup_traceability(tmp_path)
        trace_element(root, element="X", file="x.sysml", type="part def")
        result = trace_element(root, element="X", file="x.sysml", type="part def")
        assert not result.success
        assert "Duplicate" in result.message


class TestApproveResearch:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import approve_research

        root = _setup_knowledge(tmp_path)
        pending_dir = root / "knowledge" / "research" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "20260202-120000_hts.md"
        pending_file.write_text("# HTS Research\nContent here.", encoding="utf-8")

        result = approve_research(
            root,
            pending_file=str(pending_file),
            insights=[
                InsightInput(
                    title="Fact 1",
                    source="hts.md",
                    context="c",
                    model_implications="m",
                    analysis_implications="a",
                ),
                InsightInput(
                    title="Fact 2",
                    source="hts.md",
                    context="c2",
                    model_implications="m2",
                    analysis_implications="a2",
                ),
            ],
        )
        assert result.success
        # File should be moved
        assert not pending_file.exists()
        approved = root / "knowledge" / "research" / "approved" / "20260202-120000_hts.md"
        assert approved.exists()
        # Knowledge entries should exist
        parsed = parse_knowledge(root / "knowledge" / "KNOWLEDGE.md")
        assert len(parsed.data) == 2
        # ids_assigned uses DI-XXX keys with title values
        assert "DI-001" in result.ids_assigned
        assert result.ids_assigned["DI-001"] == "Fact 1"
        assert "DI-002" in result.ids_assigned
        assert result.ids_assigned["DI-002"] == "Fact 2"

    def test_file_not_in_pending(self, tmp_path):
        from agentic_mbse.pm.operations import approve_research

        root = _setup_knowledge(tmp_path)
        wrong_dir = root / "knowledge" / "research" / "approved"
        wrong_dir.mkdir(parents=True)
        f = wrong_dir / "test.md"
        f.write_text("x", encoding="utf-8")
        result = approve_research(
            root,
            pending_file=str(f),
            insights=[
                InsightInput(
                    title="T",
                    source="s",
                    context="c",
                    model_implications="m",
                    analysis_implications="a",
                ),
            ],
        )
        assert not result.success

    def test_missing_file(self, tmp_path):
        from agentic_mbse.pm.operations import approve_research

        root = _setup_knowledge(tmp_path)
        pending_dir = root / "knowledge" / "research" / "pending"
        pending_dir.mkdir(parents=True)
        result = approve_research(
            root,
            pending_file=str(pending_dir / "nonexistent.md"),
            insights=[
                InsightInput(
                    title="T",
                    source="s",
                    context="c",
                    model_implications="m",
                    analysis_implications="a",
                )
            ],
        )
        assert not result.success

    def test_mints_above_archive_note(self, tmp_path):
        from agentic_mbse.pm.operations import approve_research

        _write_archived_knowledge(tmp_path)
        pending_file = tmp_path / "knowledge" / "research" / "pending" / "20260202-120000_r.md"
        pending_file.parent.mkdir(parents=True)
        pending_file.write_text("# Research\n", encoding="utf-8")
        result = approve_research(
            tmp_path,
            pending_file=str(pending_file),
            insights=[
                InsightInput(
                    title=title,
                    source="r.md",
                    context="c",
                    model_implications="m",
                    analysis_implications="a",
                )
                for title in ("First", "Second")
            ],
        )
        assert result.ids_assigned == {"DI-015": "First", "DI-016": "Second"}


class TestRegisterIntent:
    def test_goals_only(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        result = register_intent(
            root,
            goals=[GoalInput(goal="Validate thermal", priority="P0", source="stakeholder")],
        )
        assert result.success
        assert any(k.startswith("G-") for k in result.ids_assigned)
        parsed = parse_overview(root / "modeling_project" / "OVERVIEW.md")
        assert len(parsed.data.goals) == 1

    def test_questions_only(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        result = register_intent(
            root,
            questions=[QuestionInput(question="What is steady-state margin?", source="G-001")],
        )
        assert result.success
        assert any(k.startswith("AQ-") for k in result.ids_assigned)

    def test_both(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        result = register_intent(
            root,
            goals=[GoalInput(goal="Goal 1", priority="P0", source="s")],
            questions=[QuestionInput(question="Question 1", source="G-001")],
        )
        assert result.success
        assert any(k.startswith("G-") for k in result.ids_assigned)
        assert any(k.startswith("AQ-") for k in result.ids_assigned)

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        register_intent(root, goals=[GoalInput(goal="G1", priority="P0", source="s")])
        result = register_intent(root, goals=[GoalInput(goal="G2", priority="P1", source="s")])
        assert "G-002" in result.ids_assigned

    def test_value_with_pipe_round_trips(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        result = register_intent(
            root,
            goals=[GoalInput(goal="Keep |dT| under 5 K", priority="P0", source="s")],
            questions=[QuestionInput(question="Is |x| bounded?", source="G-001")],
        )
        assert result.success
        parsed = parse_overview(root / "modeling_project" / "OVERVIEW.md")
        assert parsed.warnings == []
        assert parsed.data.goals[0].goal == "Keep |dT| under 5 K"
        assert parsed.data.goals[0].priority == "P0"
        assert parsed.data.questions[0].question == "Is |x| bounded?"
        assert parsed.data.questions[0].source == "G-001"

    def test_refused_second_goal_writes_nothing(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        before = _file_bytes(root)
        result = register_intent(
            root,
            goals=[
                GoalInput(goal="Fine goal", priority="P0", source="s"),
                GoalInput(goal="Hidden <!-- note", priority="P1", source="s"),
            ],
        )
        assert not result.success
        assert "Hidden <!-- note" in result.message
        assert _file_bytes(root) == before

    @pytest.mark.parametrize(
        ("new_id", "intent"),
        [
            ("G-003", {"goals": [GoalInput(goal="new", priority="P0", source="s")]}),
            ("AQ-003", {"questions": [QuestionInput(question="new?", source="s")]}),
        ],
    )
    def test_mints_above_unparsed_record(self, tmp_path, new_id, intent):
        from agentic_mbse.pm.operations import register_intent

        path = _write_overview(tmp_path, _OVERVIEW_GOAL_ROWS, _OVERVIEW_QUESTION_ROWS)
        parsed = parse_overview(path).data
        assert [e.id for e in parsed.goals + parsed.questions] == ["G-001", "AQ-001"]
        before = path.read_text(encoding="utf-8")
        result = register_intent(tmp_path, **intent)
        assert list(result.ids_assigned) == [new_id]
        _assert_one_record_added(before, path.read_text(encoding="utf-8"), new_id, table=True)

    def test_multiple_goals_mint_above_unparsed(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        _write_overview(tmp_path, _OVERVIEW_GOAL_ROWS, [])
        result = register_intent(
            tmp_path,
            goals=[
                GoalInput(goal="first", priority="P0", source="s"),
                GoalInput(goal="second", priority="P1", source="s"),
            ],
        )
        assert result.ids_assigned == {"G-003": "first", "G-004": "second"}

    def test_missing_questions_section_writes_nothing(self, tmp_path):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        path = root / "modeling_project" / "OVERVIEW.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("## Analysis Questions", "## Open Questions"), encoding="utf-8"
        )
        before = _file_bytes(root)
        result = register_intent(
            root,
            goals=[GoalInput(goal="g", priority="P0", source="s")],
            questions=[QuestionInput(question="q?", source="G-001")],
        )
        assert not result.success
        assert "'## Analysis Questions'" in result.message
        assert "OVERVIEW.md" in result.message
        assert _file_bytes(root) == before

    @pytest.mark.parametrize(
        ("kind", "heading", "example_row", "item", "minted"),
        [
            pytest.param(
                "goals",
                "## Goals Registry",
                "| G-001 | ex | P0 | active | s |  |",
                lambda text: GoalInput(goal=text, priority="P0", source="s"),
                ["G-001", "G-002"],
                id="G",
            ),
            pytest.param(
                "questions",
                "## Analysis Questions",
                "| AQ-001 | ex? | i | s | open |",
                lambda text: QuestionInput(question=text, source="s"),
                ["AQ-001", "AQ-002"],
                id="AQ",
            ),
        ],
    )
    def test_skips_commented_table_above_real_table(
        self, tmp_path, kind, heading, example_row, item, minted
    ):
        from agentic_mbse.pm.operations import register_intent

        root = _setup_overview(tmp_path)
        path = root / "modeling_project" / "OVERVIEW.md"
        example = _comment_example_above_table(path, heading, example_row)
        first = register_intent(root, **{kind: [item("first")]})
        assert [e.id for e in getattr(parse_overview(path).data, kind)] == minted[:1]
        second = register_intent(root, **{kind: [item("second")]})
        assert [*first.ids_assigned, *second.ids_assigned] == minted
        assert [e.id for e in getattr(parse_overview(path).data, kind)] == minted
        assert example in path.read_text(encoding="utf-8")


class TestImpactQuery:
    def test_by_knowledge_id(self, tmp_path):
        from agentic_mbse.pm.operations import impact_query, trace_element

        root = _setup_traceability(tmp_path)
        _setup_knowledge(root)
        # Manually add DI-001 to knowledge so trace_element validation passes
        from agentic_mbse.pm.operations import add_insight

        add_insight(
            root,
            title="Fact",
            source="s",
            context="c",
            model_implications="m",
            analysis_implications="a",
        )

        trace_element(root, element="A", file="a.sysml", type="part", knowledge=["DI-001"])
        trace_element(root, element="B", file="b.sysml", type="part", knowledge=["DI-001"])
        trace_element(root, element="C", file="c.sysml", type="part")

        result = impact_query(root, query_id="DI-001")
        assert len(result.affected_elements) == 2

    def test_missing_csv(self, tmp_path):
        from agentic_mbse.pm.operations import impact_query

        result = impact_query(tmp_path, query_id="DI-001")
        assert result.affected_elements == []
        assert len(result.warnings) > 0

    def test_invalid_query_id(self, tmp_path):
        from agentic_mbse.pm.operations import impact_query

        result = impact_query(tmp_path, query_id="invalid")
        assert len(result.warnings) > 0
        assert "Invalid" in result.warnings[0].message


# ---------------------------------------------------------------------------
# Phase 4: BACKLOG.md mutation operations
# ---------------------------------------------------------------------------


def _setup_backlog(tmp_path, data=None):
    """Create a minimal project with BACKLOG.md."""
    wdir = tmp_path / "work"
    wdir.mkdir(exist_ok=True)
    path = wdir / "BACKLOG.md"
    if data is None:
        src = TEMPLATES / "BACKLOG.md.template"
        path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        _write_backlog(path, data)
    return tmp_path


def _write_backlog_text(root, text):
    """Write work/BACKLOG.md with the given text and return its path."""
    wdir = root / "work"
    wdir.mkdir(exist_ok=True)
    path = wdir / "BACKLOG.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_raw_backlog(root, epics=(), standalone=()):
    """Write work/BACKLOG.md from raw mappings, which BacklogData cannot hold when invalid."""
    frontmatter = yaml.dump(
        {"epics": list(epics), "standalone": list(standalone)},
        default_flow_style=False,
        sort_keys=False,
    )
    return _write_backlog_text(root, f"---\n{frontmatter}---\n\n# Project Backlog\n")


def _wi(wi_id, **overrides):
    """Return one valid standalone work-item mapping, with any fields overridden."""
    item = {
        "id": wi_id,
        "name": f"Item {wi_id}",
        "scale": "standard",
        "priority": "P1",
        "status": "backlog",
        "completed": None,
    }
    item.update(overrides)
    return item


def _epic(name, **overrides):
    """Return one valid epic mapping with no items, with any fields overridden."""
    epic = {
        "name": name,
        "goal": None,
        "priority": "P1",
        "status": "active",
        "file": "backlog/epic.md",
        "items": [],
    }
    epic.update(overrides)
    return epic


# BACKLOG.md texts whose frontmatter cannot be read whole, each with the reader's warning (R1)
_UNREADABLE_BACKLOGS = {
    "malformed YAML": ("---\nstandalone: [\n---\n", "Malformed YAML"),
    "no frontmatter": ("# Project Backlog\n\nNo items yet.\n", "No opening frontmatter delimiter"),
    "standalone twice": (
        "---\n"
        "standalone:\n"
        "- id: WI-001\n"
        "  name: first\n"
        "  scale: standard\n"
        "  priority: P1\n"
        "  status: backlog\n"
        "standalone: []\n"
        "---\n",
        "found repeated key 'standalone'",
    ),
    "items twice in one epic": (
        "---\n"
        "epics:\n"
        "- name: X\n"
        "  priority: P1\n"
        "  status: active\n"
        "  file: backlog/epic.md\n"
        "  items:\n"
        "  - id: WI-001\n"
        "    name: first\n"
        "    scale: standard\n"
        "    status: backlog\n"
        "  items: []\n"
        "standalone: []\n"
        "---\n",
        "found repeated key 'items'",
    ),
    "closing --- only indented": (
        "---\nstandalone: []\n  ---\n\n# Project Backlog\n",
        "No closing frontmatter delimiter",
    ),
}


class TestAddItem:
    def test_standalone(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        root = _setup_backlog(tmp_path)
        result = add_item(root, name="Fix redefines", scale="trivial", priority="P1")
        assert result.success
        assert result.ids_assigned["WI"] == "WI-001"
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        assert len(parsed.data.standalone) == 1
        assert parsed.data.standalone[0].name == "Fix redefines"

    def test_under_epic(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        data = BacklogData(
            epics=[
                EpicEntry(
                    name="End-to-End Pipeline",
                    priority=Priority.P0,
                    status=EpicStatus.ACTIVE,
                    file="backlog/epic-pipeline.md",
                    items=[],
                )
            ],
            standalone=[],
        )
        root = _setup_backlog(tmp_path, data)
        result = add_item(
            root, name="Solar model", scale="standard", priority="P0", epic="End-to-End Pipeline"
        )
        assert result.success
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        assert len(parsed.data.epics[0].items) == 1
        assert parsed.data.epics[0].items[0].name == "Solar model"

    def test_epic_not_found(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        root = _setup_backlog(tmp_path)
        result = add_item(root, name="X", scale="trivial", priority="P1", epic="Nonexistent")
        assert not result.success
        assert "not found" in result.message.lower()

    def test_sequential_ids(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        root = _setup_backlog(tmp_path)
        r1 = add_item(root, name="First", scale="trivial", priority="P1")
        r2 = add_item(root, name="Second", scale="standard", priority="P0")
        assert r1.ids_assigned["WI"] == "WI-001"
        assert r2.ids_assigned["WI"] == "WI-002"

    def test_mints_above_invalid_item(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        path = _write_raw_backlog(
            tmp_path, standalone=[_wi("WI-001"), _wi("WI-002", status="in-progress")]
        )
        assert [e.id for e in parse_backlog(path).data.standalone] == ["WI-001"]
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert result.ids_assigned["WI"] == "WI-003"

    def test_mints_above_unparsed_record(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        path = _write_raw_backlog(
            tmp_path, standalone=[_wi("WI-001"), _wi("WI-002", status="in-progress")]
        )
        assert [e.id for e in parse_backlog(path).data.standalone] == ["WI-001"]
        before = parse_frontmatter(path).data
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert result.ids_assigned["WI"] == "WI-003"
        after = parse_frontmatter(path).data
        before["standalone"].append(after["standalone"][-1])
        assert after == before and after["standalone"][-1] == _wi("WI-003", name="new")

    def test_carries_forward_invalid_item(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        epic = _epic("X", items=[_wi("WI-001"), _wi("WI-002", scale="huge")])
        path = _write_raw_backlog(
            tmp_path, epics=[epic], standalone=[_wi("WI-003", status="in-progress")]
        )
        before = parse_frontmatter(path).data
        result = add_item(tmp_path, name="new", scale="trivial", priority="P2", epic="X")
        assert result.success, result.message
        new_item = {"id": "WI-004", "name": "new", "scale": "trivial", "status": "backlog"}
        before["epics"][0]["items"].append({**new_item, "completed": None})
        assert parse_frontmatter(path).data == before

    @pytest.mark.parametrize(
        ("text", "warning"),
        list(_UNREADABLE_BACKLOGS.values()),
        ids=list(_UNREADABLE_BACKLOGS),
    )
    def test_refuses_unreadable_frontmatter(self, tmp_path, text, warning):
        from agentic_mbse.pm.operations import add_item

        _write_backlog_text(tmp_path, text)
        before = _file_bytes(tmp_path)
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert not result.success
        assert warning in result.message and "by hand" in result.message
        assert _file_bytes(tmp_path) == before

    def test_keeps_items_after_indented_dashes(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        path = _write_backlog_text(
            tmp_path,
            "---\n"
            "epics:\n"
            "- name: X\n"
            "  goal: |\n"
            "    first line\n"
            "    ---\n"
            "    last line\n"
            "  priority: P1\n"
            "  status: active\n"
            "  file: backlog/epic.md\n"
            "  items:\n"
            "  - id: WI-001\n"
            "    name: first\n"
            "    scale: standard\n"
            "    status: backlog\n"
            "standalone:\n"
            "- id: WI-002\n"
            "  name: second\n"
            "  scale: trivial\n"
            "  priority: P1\n"
            "  status: backlog\n"
            "---\n",
        )
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert result.success, result.message
        after = parse_frontmatter(path).data
        assert after["epics"][0]["goal"] == "first line\n---\nlast line\n"
        assert [item["id"] for item in after["epics"][0]["items"]] == ["WI-001"]
        assert [item["id"] for item in after["standalone"]] == ["WI-002", "WI-003"]

    def test_refuses_non_list_standalone(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        _write_backlog_text(tmp_path, "---\nstandalone:\n  id: WI-001\n  name: lone\n---\n")
        before = _file_bytes(tmp_path)
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert not result.success
        assert "'standalone'" in result.message and "not a list" in result.message
        assert _file_bytes(tmp_path) == before

    def test_refuses_non_list_epic_items(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        _write_raw_backlog(tmp_path, epics=[_epic("X", items={"id": "WI-001", "name": "lone"})])
        before = _file_bytes(tmp_path)
        result = add_item(tmp_path, name="new", scale="standard", priority="P1", epic="X")
        assert not result.success
        assert "'epics[0].items'" in result.message and "not a list" in result.message
        assert _file_bytes(tmp_path) == before

    def test_null_standalone_starts_a_list(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        path = _write_backlog_text(tmp_path, "---\nepics: []\nstandalone:\n---\n")
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert result.success, result.message
        assert parse_frontmatter(path).data == {
            "epics": [],
            "standalone": [_wi("WI-001", name="new")],
        }

    @pytest.mark.parametrize("existing", ["missing", "empty"])
    def test_fresh_backlog_matches_typed_write(self, tmp_path, existing):
        from agentic_mbse.pm.operations import add_item

        path = _write_backlog_text(tmp_path, "")
        if existing == "missing":
            path.unlink()
        assert add_item(tmp_path, name="new", scale="standard", priority="P1").success
        expected = tmp_path / "expected.md"
        entry = StandaloneEntry(
            id="WI-001",
            name="new",
            scale=WorkItemScale.STANDARD,
            priority=Priority.P1,
            status=WorkItemStatus.BACKLOG,
        )
        _write_backlog(expected, BacklogData(standalone=[entry]))
        assert path.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")

    def test_refuses_duplicate_epic_names(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        _write_raw_backlog(tmp_path, epics=[_epic("X", status="bogus"), _epic("X")])
        before = _file_bytes(tmp_path)
        result = add_item(tmp_path, name="new", scale="standard", priority="P1", epic="X")
        assert not result.success
        assert "epics[0]" in result.message and "epics[1]" in result.message
        assert "by hand" in result.message
        assert _file_bytes(tmp_path) == before

    def test_refuses_rejected_epic_quoting_warning(self, tmp_path):
        from agentic_mbse.pm.operations import add_item

        _write_raw_backlog(tmp_path, epics=[_epic("X", status="bogus")])
        before = _file_bytes(tmp_path)
        result = add_item(tmp_path, name="new", scale="standard", priority="P1", epic="X")
        assert not result.success
        assert "not a valid record" in result.message
        assert "epics[0]" in result.message and "Invalid status 'bogus'" in result.message
        assert _file_bytes(tmp_path) == before


class TestAddEpic:
    def _write_epic_file(self, root, name="epic-thermal.md"):
        epic_file = root / "work" / "backlog" / name
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text("---\nStatus: approved\n---\n# Thermal Model\n", encoding="utf-8")
        return epic_file

    def test_register_then_add_item_to_empty_backlog(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic, add_item

        root = _setup_backlog(tmp_path)
        epic_file = self._write_epic_file(root)

        result = add_epic(
            root,
            name="Thermal Model",
            priority="P1",
            file=str(epic_file.relative_to(root)),
            goal="G-001",
        )

        assert result.success
        assert add_item(
            root,
            name="Radiator",
            scale="standard",
            priority="P1",
            epic="Thermal Model",
        ).success
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        assert parsed.data.epics == [
            EpicEntry(
                name="Thermal Model",
                goal="G-001",
                priority=Priority.P1,
                status=EpicStatus.DRAFT,
                file="backlog/epic-thermal.md",
                items=[
                    WorkItemEntry(
                        id="WI-001",
                        name="Radiator",
                        scale=WorkItemScale.STANDARD,
                        status=WorkItemStatus.BACKLOG,
                    )
                ],
            )
        ]
        assert "## Epic: Thermal Model" in (root / "work" / "BACKLOG.md").read_text()

    def test_registers_alongside_existing_epic(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        existing = EpicEntry(
            name="Existing",
            priority=Priority.P0,
            status=EpicStatus.ACTIVE,
            file="backlog/epic-existing.md",
        )
        root = _setup_backlog(tmp_path, BacklogData(epics=[existing]))
        epic_file = self._write_epic_file(root)

        result = add_epic(root, name="Thermal Model", priority="P2", file=str(epic_file))

        assert result.success
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        assert [epic.name for epic in parsed.data.epics] == ["Existing", "Thermal Model"]

    @pytest.mark.parametrize("priority", ["urgent", "p1", ""])
    def test_rejects_invalid_priority_without_changing_backlog(self, tmp_path, priority):
        from agentic_mbse.pm.operations import add_epic

        root = _setup_backlog(tmp_path)
        epic_file = self._write_epic_file(root)
        before = (root / "work" / "BACKLOG.md").read_text()

        result = add_epic(root, name="Thermal Model", priority=priority, file=str(epic_file))

        assert not result.success
        assert "invalid priority" in result.message.lower()
        assert (root / "work" / "BACKLOG.md").read_text() == before

    def test_rejects_duplicate_name_without_changing_backlog(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        existing = EpicEntry(
            name="Thermal Model",
            priority=Priority.P0,
            status=EpicStatus.ACTIVE,
            file="backlog/epic-existing.md",
        )
        root = _setup_backlog(tmp_path, BacklogData(epics=[existing]))
        epic_file = self._write_epic_file(root)
        before = (root / "work" / "BACKLOG.md").read_text()

        result = add_epic(root, name=" Thermal Model ", priority="P1", file=str(epic_file))

        assert not result.success
        assert "already exists" in result.message.lower()
        assert (root / "work" / "BACKLOG.md").read_text() == before

    def test_rejects_missing_file_without_changing_backlog(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        root = _setup_backlog(tmp_path)
        before = (root / "work" / "BACKLOG.md").read_text()

        result = add_epic(
            root,
            name="Thermal Model",
            priority="P1",
            file="work/backlog/missing.md",
        )

        assert not result.success
        assert "does not exist" in result.message.lower()
        assert (root / "work" / "BACKLOG.md").read_text() == before

    def test_rejects_file_outside_work_directory(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        root = _setup_backlog(tmp_path)
        outside_file = root / "epic.md"
        outside_file.write_text("# Outside", encoding="utf-8")

        result = add_epic(root, name="Outside", priority="P1", file=str(outside_file))

        assert not result.success
        assert "work directory" in result.message.lower()

    def test_carries_forward_invalid_item(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        epics = [
            _epic("Existing", items=[_wi("WI-001", scale="huge")]),
            _epic("Rejected", status="bogus"),
        ]
        path = _write_raw_backlog(
            tmp_path, epics=epics, standalone=[_wi("WI-002", status="in-progress")]
        )
        epic_file = self._write_epic_file(tmp_path)
        before = parse_frontmatter(path).data

        result = add_epic(
            tmp_path, name="Thermal Model", priority="P2", file=str(epic_file), goal="G-001"
        )

        assert result.success, result.message
        before["epics"].append(
            _epic(
                "Thermal Model",
                goal="G-001",
                priority="P2",
                status="draft",
                file="backlog/epic-thermal.md",
            )
        )
        assert parse_frontmatter(path).data == before

    def test_refuses_malformed_yaml(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        _write_backlog_text(tmp_path, "---\nepics: [\n---\n")
        epic_file = self._write_epic_file(tmp_path)
        before = _file_bytes(tmp_path)

        result = add_epic(tmp_path, name="Thermal Model", priority="P1", file=str(epic_file))

        assert not result.success
        assert "Malformed YAML" in result.message and "by hand" in result.message
        assert _file_bytes(tmp_path) == before

    def test_refuses_non_list_epics(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        _write_backlog_text(tmp_path, "---\nepics:\n  name: Existing\n  priority: P0\n---\n")
        epic_file = self._write_epic_file(tmp_path)
        before = _file_bytes(tmp_path)

        result = add_epic(tmp_path, name="Thermal Model", priority="P1", file=str(epic_file))

        assert not result.success
        assert "'epics'" in result.message and "not a list" in result.message
        assert _file_bytes(tmp_path) == before

    def test_refuses_name_of_rejected_epic(self, tmp_path):
        from agentic_mbse.pm.operations import add_epic

        _write_raw_backlog(tmp_path, epics=[_epic("Thermal Model", status="bogus")])
        epic_file = self._write_epic_file(tmp_path)
        before = _file_bytes(tmp_path)

        result = add_epic(tmp_path, name="Thermal Model", priority="P1", file=str(epic_file))

        assert not result.success
        assert "already exists" in result.message
        assert "epics[0]" in result.message and "Invalid status 'bogus'" in result.message
        assert _file_bytes(tmp_path) == before


class TestCloseItem:
    def _setup_active_item(self, tmp_path, wi_id="WI-001", name="solar-model"):
        """Create a full project with an active work item."""
        root = tmp_path
        # Create work directories
        active_dir = root / "work" / "active"
        active_dir.mkdir(parents=True)
        item_dir = active_dir / f"{wi_id}_{name}"
        item_dir.mkdir()
        # Create spec.md
        (item_dir / "spec.md").write_text(
            "---\nStatus: active\nOwner: Reid\n---\n# Spec\n",
            encoding="utf-8",
        )
        # Create design.md
        (item_dir / "design.md").write_text(
            "---\nStatus: draft\nOwner: Reid\n---\n# Design\n",
            encoding="utf-8",
        )
        # Create plan.md
        (item_dir / "plan.md").write_text(
            "---\nStatus: draft\n---\n# Plan\n",
            encoding="utf-8",
        )
        # Create BACKLOG.md with the item
        data = BacklogData(
            epics=[
                EpicEntry(
                    name="Test Epic",
                    priority=Priority.P0,
                    status=EpicStatus.ACTIVE,
                    file="backlog/epic-test.md",
                    items=[
                        WorkItemEntry(
                            id=wi_id,
                            name=name.replace("-", " "),
                            scale=WorkItemScale.STANDARD,
                            status=WorkItemStatus.ACTIVE,
                        )
                    ],
                )
            ],
            standalone=[],
        )
        _write_backlog(root / "work" / "BACKLOG.md", data)
        return root

    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        result = close_item(root, "WI-001")
        assert result.success

        # Verify directory moved
        assert not (root / "work" / "active" / "WI-001_solar-model").exists()
        completed_dirs = list((root / "work" / "completed").iterdir())
        assert len(completed_dirs) == 1
        assert "WI-001" in completed_dirs[0].name

        # Verify spec.md frontmatter updated
        spec = completed_dirs[0] / "spec.md"
        content = spec.read_text(encoding="utf-8")
        assert "Status: completed" in content

        # Verify design.md frontmatter updated
        design = completed_dirs[0] / "design.md"
        content = design.read_text(encoding="utf-8")
        assert "Status: complete" in content

        # Verify BACKLOG.md updated
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        item = parsed.data.epics[0].items[0]
        assert item.status == WorkItemStatus.COMPLETED
        assert item.completed is not None

    def test_not_found(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        result = close_item(root, "WI-999")
        assert not result.success

    def test_not_in_backlog(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = tmp_path
        # Create item dir but empty BACKLOG.md
        active_dir = root / "work" / "active"
        active_dir.mkdir(parents=True)
        item_dir = active_dir / "WI-001_orphan"
        item_dir.mkdir()
        (item_dir / "spec.md").write_text("---\nStatus: active\n---\n# Spec\n", encoding="utf-8")
        _setup_backlog(root)

        result = close_item(root, "WI-001")
        assert not result.success
        assert "BACKLOG.md" in result.message

    def test_spec_only(self, tmp_path):
        """Should succeed even without design.md or plan.md."""
        from agentic_mbse.pm.operations import close_item

        root = tmp_path
        active_dir = root / "work" / "active"
        active_dir.mkdir(parents=True)
        item_dir = active_dir / "WI-001_minimal"
        item_dir.mkdir()
        (item_dir / "spec.md").write_text("---\nStatus: active\n---\n# Spec\n", encoding="utf-8")

        data = BacklogData(
            epics=[],
            standalone=[
                StandaloneEntry(
                    id="WI-001",
                    name="minimal",
                    scale=WorkItemScale.TRIVIAL,
                    priority=Priority.P1,
                    status=WorkItemStatus.ACTIVE,
                )
            ],
        )
        _write_backlog(root / "work" / "BACKLOG.md", data)

        result = close_item(root, "WI-001")
        assert result.success
        completed_dirs = list((root / "work" / "completed").iterdir())
        assert len(completed_dirs) == 1

    def test_carries_forward_invalid_item(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        epic = _epic(
            "Test Epic", items=[_wi("WI-001", status="active"), _wi("WI-002", scale="huge")]
        )
        path = _write_raw_backlog(
            root,
            epics=[epic, _epic("Rejected", status="bogus")],
            standalone=[_wi("WI-003", status="in-progress")],
        )
        before = parse_frontmatter(path).data

        result = close_item(root, "WI-001")

        assert result.success, result.message
        after = parse_frontmatter(path).data
        completed = after["epics"][0]["items"][0]["completed"]
        assert datetime.date.fromisoformat(completed)
        before["epics"][0]["items"][0].update(status="completed", completed=completed)
        assert after == before

    @pytest.mark.parametrize(
        ("text", "warning"),
        [
            ("---\nepics: [\n---\n", "Malformed YAML"),
            (
                # Last-wins would find WI-001 in the second list and drop the first
                "---\n"
                "standalone:\n"
                "- id: WI-002\n"
                "  name: other\n"
                "  scale: trivial\n"
                "  priority: P1\n"
                "  status: backlog\n"
                "standalone:\n"
                "- id: WI-001\n"
                "  name: solar model\n"
                "  scale: standard\n"
                "  priority: P1\n"
                "  status: active\n"
                "---\n",
                "found repeated key 'standalone'",
            ),
        ],
        ids=["malformed YAML", "standalone twice"],
    )
    def test_refusal_leaves_item_active(self, tmp_path, text, warning):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        _write_backlog_text(root, text)
        before = _file_bytes(root)

        result = close_item(root, "WI-001")

        assert not result.success
        assert warning in result.message
        assert (root / "work" / "active" / "WI-001_solar-model" / "spec.md").is_file()
        assert _file_bytes(root) == before

    def test_refuses_duplicate_work_item_ids(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        _write_raw_backlog(
            root,
            epics=[_epic("Test Epic", items=[_wi("WI-001", status="active")])],
            standalone=[_wi("WI-001", status="active")],
        )
        before = _file_bytes(root)

        result = close_item(root, "WI-001")

        assert not result.success
        assert "epics[0].items[0]" in result.message and "standalone[0]" in result.message
        assert _file_bytes(root) == before

    def test_refuses_invalid_item_quoting_warning(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = self._setup_active_item(tmp_path)
        _write_raw_backlog(root, standalone=[_wi("WI-001", status="in-progress")])
        before = _file_bytes(root)

        result = close_item(root, "WI-001")

        assert not result.success
        assert "not a valid record" in result.message
        assert "standalone[0]" in result.message
        assert "Invalid status 'in-progress'" in result.message
        assert _file_bytes(root) == before


class TestUpdateValidation:
    def test_happy_path(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation, update_validation

        root = _setup_validation_matrix(tmp_path)
        add_validation(
            root,
            description="Test check",
            type="reasonableness",
            mechanism="test",
            expected="x",
            tolerance="t",
        )

        result = update_validation(root, sv_id="SV-001", status="passing")
        assert result.success
        parsed = parse_validation_matrix(root / "modeling_project" / "VALIDATION_MATRIX.md")
        assert parsed.data[0].status == VerificationStatus.PASSING

    def test_not_found(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        root = _setup_validation_matrix(tmp_path)
        result = update_validation(root, sv_id="SV-999", status="passing")
        assert not result.success

    def test_invalid_status(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        root = _setup_validation_matrix(tmp_path)
        result = update_validation(root, sv_id="SV-001", status="invalid")
        assert not result.success

    def test_preserves_other_rows(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation, update_validation

        root = _setup_validation_matrix(tmp_path)
        add_validation(
            root,
            description="First",
            type="reasonableness",
            mechanism="test",
            expected="x",
            tolerance="t",
        )
        add_validation(
            root,
            description="Second",
            type="baseline",
            mechanism="manual",
            expected="y",
            tolerance="t",
        )

        update_validation(root, sv_id="SV-001", status="passing")
        parsed = parse_validation_matrix(root / "modeling_project" / "VALIDATION_MATRIX.md")
        assert parsed.data[0].status == VerificationStatus.PASSING
        assert parsed.data[1].status == VerificationStatus.PENDING

    def test_escaped_row_changes_only_status(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        vm = _write_matrix(tmp_path, [_E1_ROWS["escaped"].replace("passing", "pending")])
        before = vm.read_text(encoding="utf-8")
        assert update_validation(tmp_path, sv_id="SV-034", status="passing").success
        assert vm.read_text(encoding="utf-8") == before.replace("| pending |", "| passing |")

    def test_refuses_row_with_inline_comment_and_leaves_file_unchanged(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        row = "| SV-001 | ratio <!-- check --> | baseline | test | x | t | s | t | pending |"
        vm = _write_matrix(tmp_path, [row])
        assert [e.id for e in parse_validation_matrix(vm).data] == ["SV-001"]
        before = _file_bytes(tmp_path)
        result = update_validation(tmp_path, sv_id="SV-001", status="passing")
        assert not result.success
        assert "comment" in result.message
        assert _file_bytes(tmp_path) == before

    def test_ignores_commented_example_rows(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation, update_validation

        root = _setup_validation_matrix(tmp_path)  # template: example SV-001, SV-002 in <!-- -->
        add_validation(
            root, description="real", type="baseline", mechanism="test", expected="x", tolerance="t"
        )
        vm = root / "modeling_project" / "VALIDATION_MATRIX.md"
        before = vm.read_text(encoding="utf-8")
        assert update_validation(root, sv_id="SV-001", status="passing").success
        real = "| SV-001 | real | baseline | test | x | t |  |  | "
        assert vm.read_text(encoding="utf-8") == before.replace(
            real + "pending |", real + "passing |"
        )

    @pytest.mark.parametrize("sv_id", ["SV-001", "SV-002"])
    def test_commented_example_rows_are_not_found(self, tmp_path, sv_id):
        from agentic_mbse.pm.operations import update_validation

        root = _setup_validation_matrix(tmp_path)
        before = _file_bytes(root)
        result = update_validation(root, sv_id=sv_id, status="passing")
        assert not result.success
        assert result.message == f"{sv_id} not found in VALIDATION_MATRIX.md"
        assert _file_bytes(root) == before

    def test_refuses_duplicate_rows(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        _write_matrix(tmp_path, [_E1_ROWS["valid"], _E1_ROWS["valid"].replace("plain", "copy")])
        before = _file_bytes(tmp_path)
        result = update_validation(tmp_path, sv_id="SV-033", status="failing")
        assert not result.success
        assert "line 5" in result.message and "line 6" in result.message
        assert _file_bytes(tmp_path) == before

    def test_ignores_rows_outside_registry_section(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        row = _E1_ROWS["valid"].replace("passing", "pending")
        vm = _write_matrix(tmp_path, [row])
        registry = vm.read_text(encoding="utf-8")
        table = registry.removeprefix("## Verification Registry\n\n")
        vm.write_text(f"## Summary\n\n{table}\n{registry}\n## Archive\n\n{table}", encoding="utf-8")
        before = vm.read_text(encoding="utf-8").split("\n")
        assert update_validation(tmp_path, sv_id="SV-033", status="passing").success
        after = vm.read_text(encoding="utf-8").split("\n")
        assert [i for i, (a, b) in enumerate(zip(before, after, strict=True)) if a != b] == [10]
        assert after[10] == row.replace("pending", "passing")

    def test_refuses_unparsed_row(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        vm = _write_matrix(tmp_path, [_E1_ROWS["valid"], _E1_ROWS["malformed"]])
        parsed = parse_validation_matrix(vm)
        assert [e.id for e in parsed.data] == ["SV-033"]
        before = _file_bytes(tmp_path)
        result = update_validation(tmp_path, sv_id="SV-035", status="failing")
        assert not result.success
        assert "\\|" in result.message and "by hand" in result.message
        assert result.warnings == parsed.warnings
        assert _file_bytes(tmp_path) == before

    def test_refuses_comment_in_status_cell(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        row = "| SV-001 | d | baseline | test | x | t | s | t | pending <!-- recheck --> |"
        vm = _write_matrix(tmp_path, [row])
        assert [e.status for e in parse_validation_matrix(vm).data] == [VerificationStatus.PENDING]
        before = _file_bytes(tmp_path)
        result = update_validation(tmp_path, sv_id="SV-001", status="passing")
        assert not result.success
        assert "comment" in result.message
        assert _file_bytes(tmp_path) == before


# ---------------------------------------------------------------------------
# Phase 5: Stubs and delegation
# ---------------------------------------------------------------------------


class TestGetStatus:
    def test_delegates_to_dashboard(self, tmp_path):
        from agentic_mbse.pm.operations import get_status
        from agentic_mbse.pm.types import DashboardResult

        root = tmp_path
        (root / "work").mkdir()
        (root / "work" / "BACKLOG.md").write_text(
            "---\nepics: []\nstandalone: []\n---\n", encoding="utf-8"
        )
        result = get_status(root)
        assert isinstance(result, DashboardResult)
        assert "## Project:" in result.markdown


class TestSupersedeInsight:
    def test_raises_not_implemented(self, tmp_path):
        from agentic_mbse.pm.operations import supersede_insight

        with pytest.raises(NotImplementedError, match="supersede-insight"):
            supersede_insight(tmp_path, old_id="DI-001", new_insight={}, reason="test")


# ---------------------------------------------------------------------------
# Audit gap coverage (G1-G5)
# ---------------------------------------------------------------------------


class TestSaveResearchContent:
    """G1: Verify written file content matches input."""

    def test_content_matches_input(self, tmp_path):
        from agentic_mbse.pm.operations import save_research

        content = "# HTS Research\n\nDetailed findings about HTS magnets.\n"
        result = save_research(tmp_path, topic="HTS magnets", content=content)
        assert result.success
        saved_path = Path(result.files_modified[0])
        assert saved_path.read_text(encoding="utf-8") == content


class TestCloseItemStandalone:
    """G2: close_item with standalone items in BACKLOG.md."""

    def test_standalone_close(self, tmp_path):
        from agentic_mbse.pm.operations import close_item

        root = tmp_path
        active_dir = root / "work" / "active"
        active_dir.mkdir(parents=True)
        item_dir = active_dir / "WI-001_fix-redefines"
        item_dir.mkdir()
        (item_dir / "spec.md").write_text(
            "---\nStatus: active\n---\n# Spec\n", encoding="utf-8"
        )

        data = BacklogData(
            epics=[],
            standalone=[
                StandaloneEntry(
                    id="WI-001",
                    name="fix redefines",
                    scale=WorkItemScale.TRIVIAL,
                    priority=Priority.P1,
                    status=WorkItemStatus.ACTIVE,
                )
            ],
        )
        _write_backlog(root / "work" / "BACKLOG.md", data)

        result = close_item(root, "WI-001")
        assert result.success

        # Verify BACKLOG.md standalone item updated
        parsed = parse_backlog(root / "work" / "BACKLOG.md")
        assert parsed.data.standalone[0].status == WorkItemStatus.COMPLETED
        assert parsed.data.standalone[0].completed is not None

        # Verify directory moved
        completed_dirs = list((root / "work" / "completed").iterdir())
        assert len(completed_dirs) == 1
        assert "WI-001" in completed_dirs[0].name


class TestRegisterDecisionDate:
    """G4: Verify register_decision auto-sets today's date."""

    def test_date_auto_set(self, tmp_path):
        import datetime

        from agentic_mbse.pm.operations import register_decision

        root = _setup_architecture(tmp_path)
        result = register_decision(
            root, title="Use metric units", decision="SI only", rationale="Consistency"
        )
        assert result.success
        parsed = parse_architecture(root / "modeling_project" / "ARCHITECTURE.md")
        assert parsed.data[0].date == datetime.date.today().isoformat()


class TestTraceElementInvalidRequirement:
    """G5: trace_element with invalid PR-XXX reference."""

    def test_invalid_requirement_id(self, tmp_path):
        from agentic_mbse.pm.operations import trace_element

        root = _setup_requirements(tmp_path)
        _setup_traceability(root)
        result = trace_element(
            root,
            element="X",
            file="x.sysml",
            type="part def",
            requirement=["PR-999"],
        )
        assert not result.success
        assert "PR-999" in result.message


class TestImportsFromPackage:
    def test_operations_importable(self):
        import agentic_mbse.pm as pm

        expected_names = [
            "OperationResult",
            "ImpactResult",
            "InsightInput",
            "GoalInput",
            "QuestionInput",
            "add_insight",
            "save_research",
            "approve_research",
            "promote_requirement",
            "register_decision",
            "add_validation",
            "trace_element",
            "impact_query",
            "register_intent",
            "add_item",
            "close_item",
            "update_validation",
            "get_status",
            "supersede_insight",
        ]
        for name in expected_names:
            assert hasattr(pm, name), f"Missing export: {name}"
            assert name in pm.__all__, f"Missing from __all__: {name}"
