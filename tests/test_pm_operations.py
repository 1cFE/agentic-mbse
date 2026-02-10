"""Tests for the PM operations module."""

from pathlib import Path

from agentic_mbse.pm import (
    BacklogData,
    parse_architecture,
    parse_backlog,
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
    _render_backlog_body,
    _update_frontmatter_fields,
    _write_backlog,
)
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
    """Tests for supersede_insight() operation (TASK-003)."""

    def _setup_knowledge_with_insights(self, root: Path) -> None:
        """Create KNOWLEDGE.md with test insights."""
        knowledge_dir = root / "knowledge"
        knowledge_dir.mkdir(parents=True)
        knowledge_path = knowledge_dir / "KNOWLEDGE.md"

        content = """# Domain Knowledge

## Domain Insights

### DI-001: HTS magnets cost more than LTS
- **Source**: CATF 2024 report
- **Context**: Cost modeling assumptions
- **Model implications**: Need separate cost models for HTS vs LTS
- **Analysis implications**: Cost sensitivity analysis must account for magnet type
- **Status**: captured

### DI-002: Blanket lifetime drives maintenance
- **Source**: Engineering analysis
- **Context**: Operational planning
- **Model implications**: Blanket replacement schedule affects uptime
- **Analysis implications**: Maintenance costs are significant
- **Status**: captured

### DI-003: Uniform magnet costing is incorrect
- **Source**: PyFECONS assumptions
- **Context**: Legacy cost model treats all magnets uniformly
- **Model implications**: Single cost multiplier is insufficient
- **Analysis implications**: LCOE estimates may be optimistic by 15-20%
- **Status**: captured
"""
        knowledge_path.write_text(content, encoding="utf-8")

    def _setup_traceability(self, root: Path) -> None:
        """Create traceability matrix with DI-003 references."""
        data_dir = root / "data"
        data_dir.mkdir(parents=True)
        csv_path = data_dir / "traceability_matrix.csv"

        content = """Element,File,Type,Requirement,Knowledge
MagnetSystemCostCalc,models/library/magnet_cost.sysml,calc def,PR-005,DI-003
TFCoilCostCalc,models/library/tf_coil_cost.sysml,calc def,PR-005,DI-003
PFCoilCostCalc,models/library/pf_coil_cost.sysml,calc def,PR-012,DI-003
BlanketLifetime,models/library/blanket.sysml,attribute,PR-008,DI-002
"""
        csv_path.write_text(content, encoding="utf-8")

    def test_supersede_basic_flow(self, tmp_path):
        """Supersession updates old insight, creates new insight, and generates impact report."""
        from agentic_mbse.pm.operations import supersede_insight

        root = tmp_path / "project"
        root.mkdir()
        self._setup_knowledge_with_insights(root)
        self._setup_traceability(root)

        new_insight = {
            "title": "HTS vs LTS cost differentiation required",
            "source": "Updated CATF 2024 data with HTS/LTS breakdown",
            "context": "New research shows 3x cost difference between HTS and LTS at scale",
            "model_implications": "Cost models must split HTS and LTS paths",
            "analysis_implications": "Scenario analysis should vary magnet technology choice",
        }

        result = supersede_insight(
            root,
            old_id="DI-003",
            new_insight=new_insight,
            reason="New research on HTS vs LTS cost structures",
        )

        assert result.success
        assert "DI" in result.ids_assigned
        assert result.ids_assigned["DI"] == "DI-004"

        # Check KNOWLEDGE.md updated
        knowledge_path = root / "knowledge" / "KNOWLEDGE.md"
        knowledge_content = knowledge_path.read_text(encoding="utf-8")

        # Old insight marked as superseded
        assert "### DI-003:" in knowledge_content
        assert "**Status**: superseded" in knowledge_content
        assert "**Superseded-by**: DI-004" in knowledge_content

        # New insight created
        assert "### DI-004: HTS vs LTS cost differentiation required" in knowledge_content
        assert "**Supersedes**: DI-003" in knowledge_content
        assert "**Status**: captured" in knowledge_content

        # Check impact report generated
        impact_path = root / "knowledge" / "research" / "impacts" / "DI-003_superseded.md"
        assert impact_path.exists()
        impact_content = impact_path.read_text(encoding="utf-8")

        assert "Impact Report: DI-003 Superseded" in impact_content
        assert "Superseded by**: DI-004" in impact_content
        assert "New research on HTS vs LTS cost structures" in impact_content
        assert "MagnetSystemCostCalc" in impact_content
        assert "TFCoilCostCalc" in impact_content
        assert "PFCoilCostCalc" in impact_content

    def test_invalid_old_id_format(self, tmp_path):
        """Reject invalid old_id format."""
        from agentic_mbse.pm.operations import supersede_insight

        result = supersede_insight(
            tmp_path,
            old_id="INVALID",
            new_insight={"title": "test"},
            reason="test",
        )

        assert not result.success
        assert "Invalid old_id" in result.message

    def test_missing_required_fields_in_new_insight(self, tmp_path):
        """Reject new_insight with missing required fields."""
        from agentic_mbse.pm.operations import supersede_insight

        root = tmp_path / "project"
        root.mkdir()
        self._setup_knowledge_with_insights(root)

        # Missing model_implications
        new_insight = {
            "title": "test",
            "source": "test",
            "context": "test",
            "analysis_implications": "test",
        }

        result = supersede_insight(
            root,
            old_id="DI-001",
            new_insight=new_insight,
            reason="test",
        )

        assert not result.success
        assert "model_implications" in result.message

    def test_old_id_not_found(self, tmp_path):
        """Reject supersession of non-existent insight."""
        from agentic_mbse.pm.operations import supersede_insight

        root = tmp_path / "project"
        root.mkdir()
        self._setup_knowledge_with_insights(root)

        new_insight = {
            "title": "test",
            "source": "test",
            "context": "test",
            "model_implications": "test",
            "analysis_implications": "test",
        }

        result = supersede_insight(
            root,
            old_id="DI-999",
            new_insight=new_insight,
            reason="test",
        )

        assert not result.success
        assert "DI-999 not found" in result.message

    def test_already_superseded(self, tmp_path):
        """Reject supersession of already-superseded insight."""
        from agentic_mbse.pm.operations import supersede_insight

        root = tmp_path / "project"
        root.mkdir()
        knowledge_dir = root / "knowledge"
        knowledge_dir.mkdir(parents=True)
        knowledge_path = knowledge_dir / "KNOWLEDGE.md"

        # DI-001 already superseded by DI-002
        content = """# Domain Knowledge

## Domain Insights

### DI-001: Old insight
- **Source**: test
- **Context**: test
- **Model implications**: test
- **Analysis implications**: test
- **Status**: superseded
- **Superseded-by**: DI-002

### DI-002: New insight
- **Source**: test
- **Context**: test
- **Model implications**: test
- **Analysis implications**: test
- **Status**: captured
- **Supersedes**: DI-001
"""
        knowledge_path.write_text(content, encoding="utf-8")

        new_insight = {
            "title": "test",
            "source": "test",
            "context": "test",
            "model_implications": "test",
            "analysis_implications": "test",
        }

        result = supersede_insight(
            root,
            old_id="DI-001",
            new_insight=new_insight,
            reason="test",
        )

        assert not result.success
        assert "already superseded" in result.message
        assert "DI-002" in result.message

    def test_no_affected_elements(self, tmp_path):
        """Impact report shows 'No model elements' when traceability empty."""
        from agentic_mbse.pm.operations import supersede_insight

        root = tmp_path / "project"
        root.mkdir()
        self._setup_knowledge_with_insights(root)

        # Empty traceability
        data_dir = root / "data"
        data_dir.mkdir(parents=True)
        csv_path = data_dir / "traceability_matrix.csv"
        csv_path.write_text("Element,File,Type,Requirement,Knowledge\n", encoding="utf-8")

        new_insight = {
            "title": "test",
            "source": "test",
            "context": "test",
            "model_implications": "test",
            "analysis_implications": "test",
        }

        result = supersede_insight(
            root,
            old_id="DI-001",
            new_insight=new_insight,
            reason="test",
        )

        assert result.success

        impact_path = root / "knowledge" / "research" / "impacts" / "DI-001_superseded.md"
        impact_content = impact_path.read_text(encoding="utf-8")
        assert "No model elements traced" in impact_content


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
        (item_dir / "spec.md").write_text("---\nStatus: active\n---\n# Spec\n", encoding="utf-8")

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
