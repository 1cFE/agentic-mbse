"""Tests for the PM parser module."""

from pathlib import Path

from agentic_mbse.pm import (
    BacklogData,
    InsightStatus,
    OverviewData,
    parse_architecture,
    parse_backlog,
    parse_frontmatter,
    parse_knowledge,
    parse_overview,
    parse_requirements,
    parse_traceability,
    parse_validation_matrix,
)

TEMPLATES = Path(__file__).parent.parent / "project_templates"
FIXTURES = Path(__file__).parent / "fixtures" / "pm"


# ---------------------------------------------------------------------------
# Phase 1: Frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nStatus: active\nCreated: 2026-02-01\n---\n# Body\n")
        result = parse_frontmatter(f)
        assert result.data["Status"] == "active"
        assert isinstance(result.data["Created"], str)
        assert result.warnings == []

    def test_missing_file(self, tmp_path):
        result = parse_frontmatter(tmp_path / "nope.md")
        assert result.data == {}
        assert len(result.warnings) == 1
        assert "not found" in result.warnings[0].message.lower()

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert result.warnings == []

    def test_no_opening_delimiter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Just a heading\nSome content\n")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert len(result.warnings) == 1

    def test_malformed_yaml(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\n: bad: yaml: here\n---\n")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert len(result.warnings) == 1

    def test_yaml_date_coercion(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nCreated: 2026-02-01\nFlag: yes\n---\n")
        result = parse_frontmatter(f)
        assert result.data["Created"] == "2026-02-01"
        assert result.data["Flag"] == "True"

    def test_no_closing_delimiter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nStatus: active\n# No closing\n")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert len(result.warnings) == 1
        assert "closing" in result.warnings[0].message.lower()


# ---------------------------------------------------------------------------
# Phase 2: Table-based parsers
# ---------------------------------------------------------------------------


class TestParseRequirements:
    def test_populated(self, tmp_path):
        f = tmp_path / "REQUIREMENTS.md"
        f.write_text(
            "# Modeling Requirements\n\n## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-001 | All costs exposed | G-001 | Review | AST check |\n"
            "| PR-002 | Cite sources | G-003 | Level 6 | Doc parser |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 2
        assert result.data[0].id == "PR-001"
        assert result.data[0].requirement == "All costs exposed"
        assert result.data[1].id == "PR-002"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_requirements(TEMPLATES / "REQUIREMENTS.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_invalid_id_skipped(self, tmp_path):
        f = tmp_path / "REQUIREMENTS.md"
        f.write_text(
            "## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| XX-001 | Bad id | G-001 | Review | Check |\n"
            "| PR-002 | Good id | G-002 | Review | Check |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 1
        assert result.data[0].id == "PR-002"
        assert len(result.warnings) == 1

    def test_missing_file(self, tmp_path):
        result = parse_requirements(tmp_path / "nope.md")
        assert result.data == []
        assert len(result.warnings) == 1

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("")
        result = parse_requirements(f)
        assert result.data == []
        assert result.warnings == []


class TestParseValidationMatrix:
    def test_populated(self, tmp_path):
        f = tmp_path / "VALIDATION_MATRIX.md"
        f.write_text(
            "## Verification Registry\n\n"
            "| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |\n"
            "|----|-------------|------|-----------|----------|-----------|--------|------|--------|\n"
            "| SV-001 | Cost ballpark | reasonableness | test | $3B-$15B | range | judgment | test_cost | pending |\n"
        )
        result = parse_validation_matrix(f)
        assert len(result.data) == 1
        assert result.data[0].id == "SV-001"
        assert result.data[0].type.value == "reasonableness"
        assert result.data[0].mechanism.value == "test"
        assert result.data[0].status.value == "pending"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_validation_matrix(TEMPLATES / "VALIDATION_MATRIX.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_invalid_enum_skipped(self, tmp_path):
        f = tmp_path / "VALIDATION_MATRIX.md"
        f.write_text(
            "## Verification Registry\n\n"
            "| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |\n"
            "|----|-------------|------|-----------|----------|-----------|--------|------|--------|\n"
            "| SV-001 | Bad type | invalid_type | test | x | x | x | x | pending |\n"
        )
        result = parse_validation_matrix(f)
        assert result.data == []
        assert len(result.warnings) == 1

    def test_missing_file(self, tmp_path):
        result = parse_validation_matrix(tmp_path / "nope.md")
        assert result.data == []
        assert len(result.warnings) == 1


class TestParseOverview:
    def test_populated(self, tmp_path):
        f = tmp_path / "OVERVIEW.md"
        f.write_text(
            "# Overview\n\n"
            "## Goals Registry\n\n"
            "| ID | Goal | Priority | Status | Source | Traced Requirements |\n"
            "|----|------|----------|--------|--------|---------------------|\n"
            "| G-001 | Validate thermal | P0 | active | stakeholder | PR-001, PR-003 |\n"
            "\n---\n\n"
            "## Analysis Questions\n\n"
            "| ID | Question | Implies | Source | Status |\n"
            "|----|----------|---------|--------|--------|\n"
            "| AQ-001 | Thermal margin? | Thermal model | G-001 | open |\n"
        )
        result = parse_overview(f)
        assert len(result.data.goals) == 1
        assert result.data.goals[0].id == "G-001"
        assert len(result.data.questions) == 1
        assert result.data.questions[0].id == "AQ-001"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_overview(TEMPLATES / "OVERVIEW.md.template")
        assert result.data == OverviewData(goals=[], questions=[])
        assert result.warnings == []

    def test_invalid_ids(self, tmp_path):
        f = tmp_path / "OVERVIEW.md"
        f.write_text(
            "## Goals Registry\n\n"
            "| ID | Goal | Priority | Status | Source | Traced Requirements |\n"
            "|----|------|----------|--------|--------|---------------------|\n"
            "| BAD-001 | Bad goal | P0 | active | x | x |\n"
            "\n## Analysis Questions\n\n"
            "| ID | Question | Implies | Source | Status |\n"
            "|----|----------|---------|--------|--------|\n"
            "| BAD-001 | Bad question | x | x | open |\n"
        )
        result = parse_overview(f)
        assert result.data.goals == []
        assert result.data.questions == []
        assert len(result.warnings) == 2

    def test_missing_file(self, tmp_path):
        result = parse_overview(tmp_path / "nope.md")
        assert result.data == OverviewData()
        assert len(result.warnings) == 1


class TestMarkdownTableEdgeCases:
    def test_horizontal_rule_stops_table(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text(
            "## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-001 | First | G-001 | Review | Check |\n"
            "\n---\n\n"
            "## Other Section\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-099 | Should not appear | G-999 | Review | Check |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 1
        assert result.data[0].id == "PR-001"

    def test_html_comments_ignored(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text(
            "## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "<!-- | PR-999 | Comment row | G-000 | None | None | -->\n"
            "| PR-001 | Real row | G-001 | Review | Check |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 1
        assert result.data[0].id == "PR-001"

    def test_unclosed_html_comment(self, tmp_path):
        """Unclosed <!-- should not consume the rest of the file."""
        f = tmp_path / "test.md"
        f.write_text(
            "## Requirements\n\n"
            "<!-- This comment is never closed\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-001 | Real row | G-001 | Review | Check |\n"
        )
        result = parse_requirements(f)
        # Non-greedy regex won't match without -->, so comment is not stripped
        # and the table row is still parseable
        assert len(result.data) == 1
        assert result.data[0].id == "PR-001"

    def test_extra_columns_ignored(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text(
            "## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method | Extra |\n"
            "|----|-------------|--------|-------------|-------------------|-------|\n"
            "| PR-001 | Test | G-001 | Review | Check | bonus |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 1
        assert result.data[0].id == "PR-001"


# ---------------------------------------------------------------------------
# Phase 3: Section parsers + Backlog
# ---------------------------------------------------------------------------


class TestParseKnowledge:
    def test_populated(self, tmp_path):
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "# Domain Knowledge\n\n"
            "### DI-001: Heat Transfer Limits\n"
            "- **Source**: approved research\n"
            "- **Context**: Max temp is 650C\n"
            "- **Model implications**: Thermal cap needed\n"
            "- **Analysis implications**: Sensitivity analysis\n"
            "- **Status**: captured\n"
        )
        result = parse_knowledge(f)
        assert len(result.data) == 1
        assert result.data[0].id == "DI-001"
        assert result.data[0].title == "Heat Transfer Limits"
        assert result.data[0].status == InsightStatus.CAPTURED
        assert result.data[0].source == "approved research"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_knowledge(TEMPLATES / "KNOWLEDGE.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_html_comment_sections_ignored(self, tmp_path):
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "# Domain Knowledge\n\n"
            "<!-- ### DI-999: Comment Entry\n"
            "- **Source**: should not appear\n"
            "- **Context**: inside comment\n"
            "- **Model implications**: none\n"
            "- **Analysis implications**: none\n"
            "- **Status**: captured\n"
            "-->\n\n"
            "### DI-001: Real Entry\n"
            "- **Source**: real source\n"
            "- **Context**: real context\n"
            "- **Model implications**: real implications\n"
            "- **Analysis implications**: real analysis\n"
            "- **Status**: addressed\n"
        )
        result = parse_knowledge(f)
        assert len(result.data) == 1
        assert result.data[0].id == "DI-001"

    def test_missing_required_fields(self, tmp_path):
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "### DI-001: Partial Entry\n- **Source**: only source\n- **Status**: captured\n"
        )
        result = parse_knowledge(f)
        assert len(result.data) == 1
        assert result.data[0].source == "only source"
        assert result.data[0].context == ""
        # Should have warnings for missing Context, Model implications, Analysis implications
        assert len(result.warnings) == 3

    def test_missing_file(self, tmp_path):
        result = parse_knowledge(tmp_path / "nope.md")
        assert result.data == []
        assert len(result.warnings) == 1

    def test_multi_line_field_continuation(self, tmp_path):
        """Lines without a field marker append to the previous field value."""
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "### DI-001: Multi Line\n"
            "- **Source**: approved research\n"
            "- **Context**: First line of context.\n"
            "  Second line of context.\n"
            "  Third line of context.\n"
            "- **Model implications**: implications here\n"
            "- **Analysis implications**: analysis here\n"
            "- **Status**: captured\n"
        )
        result = parse_knowledge(f)
        assert len(result.data) == 1
        assert "First line" in result.data[0].context
        assert "Second line" in result.data[0].context
        assert "Third line" in result.data[0].context
        assert result.warnings == []

    def test_invalid_status_skips(self, tmp_path):
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "### DI-001: Bad Status\n"
            "- **Source**: src\n"
            "- **Context**: ctx\n"
            "- **Model implications**: mi\n"
            "- **Analysis implications**: ai\n"
            "- **Status**: unknown\n"
        )
        result = parse_knowledge(f)
        assert result.data == []
        assert len(result.warnings) == 1


class TestParseArchitecture:
    def test_populated_unbulleted_fields(self, tmp_path):
        f = tmp_path / "ARCHITECTURE.md"
        f.write_text(
            "# Model Architecture\n\n## Key Decisions\n\n"
            "### AD-001: Package Layout\n"
            "**Decision**: Use flat structure\n"
            "**Rationale**: Simpler imports\n"
            "**Date**: 2026-01-15\n"
            "**Status**: active\n"
        )
        result = parse_architecture(f)
        assert len(result.data) == 1
        assert result.data[0].id == "AD-001"
        assert result.data[0].decision == "Use flat structure"
        assert result.data[0].rationale == "Simpler imports"
        assert result.data[0].date == "2026-01-15"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_architecture(TEMPLATES / "ARCHITECTURE.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_missing_key_decisions_section(self, tmp_path):
        f = tmp_path / "ARCHITECTURE.md"
        f.write_text("# Architecture\n\n## Other Section\n\nSome content\n")
        result = parse_architecture(f)
        assert result.data == []
        assert result.warnings == []

    def test_invalid_status_skips(self, tmp_path):
        f = tmp_path / "ARCHITECTURE.md"
        f.write_text(
            "## Key Decisions\n\n"
            "### AD-001: Bad Status\n"
            "**Decision**: something\n"
            "**Rationale**: reason\n"
            "**Date**: 2026-01-15\n"
            "**Status**: unknown\n"
        )
        result = parse_architecture(f)
        assert result.data == []
        assert len(result.warnings) == 1

    def test_missing_file(self, tmp_path):
        result = parse_architecture(tmp_path / "nope.md")
        assert result.data == []
        assert len(result.warnings) == 1

    def test_missing_required_fields(self, tmp_path):
        f = tmp_path / "ARCHITECTURE.md"
        f.write_text("## Key Decisions\n\n### AD-001: Sparse\n**Status**: active\n")
        result = parse_architecture(f)
        assert len(result.data) == 1
        assert result.data[0].decision == ""
        # Warnings for missing Decision, Rationale, Date
        assert len(result.warnings) == 3


class TestParseBacklog:
    def test_populated(self, tmp_path):
        f = tmp_path / "BACKLOG.md"
        f.write_text(
            "---\n"
            "epics:\n"
            "  - name: Core Model\n"
            "    goal: G-001\n"
            "    priority: P0\n"
            "    status: active\n"
            "    file: backlog/epic-core.md\n"
            "    items:\n"
            "      - id: WI-001\n"
            "        name: Setup foundations\n"
            "        scale: standard\n"
            "        status: completed\n"
            "        completed: 2026-01-20\n"
            "      - id: WI-002\n"
            "        name: Add thermal model\n"
            "        scale: standard\n"
            "        status: active\n"
            "standalone:\n"
            "  - id: WI-010\n"
            "    name: Fix README\n"
            "    scale: trivial\n"
            "    priority: P3\n"
            "    status: backlog\n"
            "---\n"
            "# Backlog\n"
        )
        result = parse_backlog(f)
        assert len(result.data.epics) == 1
        assert result.data.epics[0].name == "Core Model"
        assert result.data.epics[0].goal == "G-001"
        assert len(result.data.epics[0].items) == 2
        assert result.data.epics[0].items[0].id == "WI-001"
        assert len(result.data.standalone) == 1
        assert result.data.standalone[0].id == "WI-010"
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_backlog(TEMPLATES / "BACKLOG.md.template")
        assert result.data == BacklogData(epics=[], standalone=[])
        assert result.warnings == []

    def test_invalid_status_skips_item(self, tmp_path):
        f = tmp_path / "BACKLOG.md"
        f.write_text(
            "---\n"
            "epics:\n"
            "  - name: Test Epic\n"
            "    priority: P0\n"
            "    status: unknown_status\n"
            "    file: backlog/epic-test.md\n"
            "standalone: []\n"
            "---\n"
        )
        result = parse_backlog(f)
        assert result.data.epics == []
        assert len(result.warnings) == 1

    def test_completed_without_date_warns(self, tmp_path):
        f = tmp_path / "BACKLOG.md"
        f.write_text(
            "---\n"
            "epics: []\n"
            "standalone:\n"
            "  - id: WI-001\n"
            "    name: Done item\n"
            "    scale: trivial\n"
            "    priority: P1\n"
            "    status: completed\n"
            "---\n"
        )
        result = parse_backlog(f)
        assert len(result.data.standalone) == 1
        assert len(result.warnings) == 1
        assert "completed" in result.warnings[0].message.lower()

    def test_missing_file(self, tmp_path):
        result = parse_backlog(tmp_path / "nope.md")
        assert result.data == BacklogData()
        assert len(result.warnings) == 1

    def test_invalid_work_item_id(self, tmp_path):
        f = tmp_path / "BACKLOG.md"
        f.write_text(
            "---\n"
            "epics: []\n"
            "standalone:\n"
            "  - id: BAD-001\n"
            "    name: Bad id item\n"
            "    scale: trivial\n"
            "    priority: P1\n"
            "    status: backlog\n"
            "---\n"
        )
        result = parse_backlog(f)
        assert result.data.standalone == []
        assert len(result.warnings) == 1


# ---------------------------------------------------------------------------
# Phase 4: CSV parser + AP-1 sweep
# ---------------------------------------------------------------------------


class TestParseTraceability:
    def test_populated(self, tmp_path):
        f = tmp_path / "traceability.csv"
        f.write_text(
            "Element,File,Type,Knowledge,Requirement,Source_Type,"
            "Source_Document,Source_Location,Confidence,Assumptions,Last_Verified\n"
            "MagnetCostCalc,models/lib/magnet.sysml,calc def,"
            '"DI-003, DI-012",PR-005,codebase,PyFECONS,magnet.py:94,'
            "High,2024 costs,2026-01-28\n"
        )
        result = parse_traceability(f)
        assert len(result.data) == 1
        assert result.data[0].element == "MagnetCostCalc"
        assert result.data[0].knowledge == ["DI-003", "DI-012"]
        assert result.data[0].requirement == ["PR-005"]
        assert result.warnings == []

    def test_template_empty_state(self):
        result = parse_traceability(TEMPLATES / "data" / "traceability_matrix.csv")
        assert result.data == []
        assert result.warnings == []

    def test_missing_file(self, tmp_path):
        result = parse_traceability(tmp_path / "nope.csv")
        assert result.data == []
        assert len(result.warnings) == 1

    def test_multi_value_split(self, tmp_path):
        f = tmp_path / "trace.csv"
        f.write_text(
            "Element,File,Type,Knowledge,Requirement,Source_Type,"
            "Source_Document,Source_Location,Confidence,Assumptions,Last_Verified\n"
            'Comp,f.sysml,part,"DI-001, DI-002, DI-003","PR-001, PR-002",'
            "codebase,doc,loc,High,none,2026-01-01\n"
        )
        result = parse_traceability(f)
        assert len(result.data) == 1
        assert result.data[0].knowledge == ["DI-001", "DI-002", "DI-003"]
        assert result.data[0].requirement == ["PR-001", "PR-002"]

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_text("")
        result = parse_traceability(f)
        assert result.data == []
        assert result.warnings == []


class TestAP1EmptyState:
    """Parse every real template file -- all must produce empty data, no warnings."""

    def test_backlog_template(self):
        result = parse_backlog(TEMPLATES / "BACKLOG.md.template")
        assert result.data == BacklogData(epics=[], standalone=[])
        assert result.warnings == []

    def test_requirements_template(self):
        result = parse_requirements(TEMPLATES / "REQUIREMENTS.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_validation_matrix_template(self):
        result = parse_validation_matrix(TEMPLATES / "VALIDATION_MATRIX.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_knowledge_template(self):
        result = parse_knowledge(TEMPLATES / "KNOWLEDGE.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_architecture_template(self):
        result = parse_architecture(TEMPLATES / "ARCHITECTURE.md.template")
        assert result.data == []
        assert result.warnings == []

    def test_overview_template(self):
        result = parse_overview(TEMPLATES / "OVERVIEW.md.template")
        assert result.data == OverviewData(goals=[], questions=[])
        assert result.warnings == []

    def test_traceability_template(self):
        result = parse_traceability(TEMPLATES / "data" / "traceability_matrix.csv")
        assert result.data == []
        assert result.warnings == []
