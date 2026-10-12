"""Contract tests for the shipped modeling workflow commands and documentation."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def read_repo_file(relative_path: str) -> str:
    """Read a UTF-8 repository file used as a shipped command contract."""
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_canonical_flow_covers_standard_and_epic_routes():
    flow = read_repo_file("project_templates/MODELING_PROCESS.md.template")

    assert "Command-Level Modeling Flow" in flow
    assert "Standard work" in flow
    assert "Epic work" in flow
    for stage in (
        "/research",
        "/spec-model",
        "/design-model",
        "/review-model",
        "/plan-model",
        "/implement-model",
        "/audit-models",
    ):
        assert stage in flow
    assert "owner" in flow.lower() and "close" in flow.lower()


def test_canonical_flow_marks_optional_and_completion_stages():
    flow = read_repo_file("project_templates/MODELING_PROCESS.md.template")

    assert "Optional stages" in flow
    assert "Process Selection" in flow
    assert "Review Brief and Context Limits" in flow
    assert "cross-item integration" in flow
    assert "dependency" in flow.lower()


def test_epic_audit_has_explicit_integration_scope():
    audit = read_repo_file("skills/audit-models/SKILL.md")

    assert "Epic audit" in audit
    assert "epic success criteria" in audit
    assert "item audit" in audit
    assert "cross-item integration" in audit


def test_touched_workflow_docs_have_no_stale_commands_or_validation_levels():
    touched_paths = (
        "skills/backlog/SKILL.md",
        "skills/status/SKILL.md",
        "skills/plan-model/SKILL.md",
        "skills/implement-model/SKILL.md",
        "project_templates/EPIC_GUIDE.md.template",
        "project_templates/README.md.template",
    )
    content = "\n".join(read_repo_file(path) for path in touched_paths)

    assert "pm add-to-backlog" not in content
    assert "/backlog clear" not in content
    assert "Levels 4-8" not in content
    assert "Levels 7-8" not in content


def test_orchestrator_frontmatter_and_single_alignment_contract():
    command = read_repo_file("skills/orchestrate-modeling/SKILL.md")

    assert "name: orchestrate-modeling" in command
    assert "Agent" in command.partition("---")[2].partition("---")[0]
    assert "user-invocable: true" in command
    assert command.count("## Align Once") == 1
    assert "only planned owner checkpoint" in command
    assert "before launching any stage" in command
    assert "work/orchestration/<objective-slug>.md" in command


def test_orchestrator_distinguishes_author_continuity_from_independent_review():
    command = read_repo_file("skills/orchestrate-modeling/SKILL.md")
    normalized_command = " ".join(command.split())
    lowercase_command = normalized_command.lower()

    assert "continuing author" in normalized_command
    assert "self-contained brief" in normalized_command
    assert "Resume the author after clarifications and repairs" in normalized_command
    assert "fresh non-author context without inherited author conversation" in normalized_command
    assert "blocking questions to the coordinator" in lowercase_command


def test_orchestrator_declares_routes_decision_tiers_and_bounded_repair():
    command = read_repo_file("skills/orchestrate-modeling/SKILL.md")

    assert "Standard route" in command and "Epic route" in command
    assert "Execution detail" in command
    assert "Reserved gate" in command
    assert "Premise surprise" in command
    assert "two unsuccessful repair-and-audit rounds" in command
    assert "no material progress" in command
    assert "owner decides whether to close" in command


def test_orchestrator_does_not_embed_a_runtime_or_automatic_close():
    command = read_repo_file("skills/orchestrate-modeling/SKILL.md").lower()

    for prohibited in (
        "orchestrate-stage.sh",
        "session_id",
        "run database",
        "fixed state table",
        "automatically close",
        "automatically archive",
    ):
        assert prohibited not in command


def section(text: str, heading: str) -> str:
    """The body of a `## heading` section, up to the next H2."""
    return text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]


def test_process_selection_routes_design_choice_changes():
    rows = section(
        read_repo_file("project_templates/MODELING_PROCESS.md.template"), "Process Selection"
    )

    assert any(
        "Changed design-variable role" in row and "design-choices.md" in row
        for row in rows.splitlines()
    )


def test_point_of_use_table_has_the_design_choice_row():
    rows = section(
        read_repo_file("project_templates/MODELING_PROCESS.md.template"),
        "Technical Patterns: Read at the Point of Use",
    )

    assert any(
        row.startswith("| Design variables, equipment or capacity bindings")
        and row.endswith("`design-choices.md` |")
        for row in rows.splitlines()
    )


def test_goal_runbook_trigger_table_mirrors_the_design_choice_row():
    rows = section(
        read_repo_file("project_templates/GOAL_RUNBOOK.md.template"),
        "Review scope and evidence reuse",
    )

    assert any(
        "Changed design-variable role" in row and "design-choice pattern" in row
        for row in rows.splitlines()
    )


def test_goal_template_points_at_the_design_choice_pattern():
    goal = read_repo_file("project_templates/goal.md.template")

    assert "apply the design-choice pattern (`design-choices.md`" in goal


def test_design_choice_pattern_and_equality_intent_name_each_other():
    assert "[design-choices.md](design-choices.md)" in read_repo_file(
        "docs/patterns/constraints.md"
    )
    assert "docs/patterns/design-choices.md" in read_repo_file("skills/sysml-conventions/SKILL.md")
    assert "[constraints.md](constraints.md)" in read_repo_file("docs/patterns/design-choices.md")


def test_design_choice_obligations_are_stated_once():
    """Only the pattern states the rule's obligations; everything else points at it."""
    shipped = [
        path
        for folder in ("skills", "project_templates", "docs/patterns")
        for path in sorted((REPO_ROOT / folder).rglob("*"))
        if path.is_file()
    ]
    pattern = REPO_ROOT / "docs/patterns/design-choices.md"

    for obligation in (
        "must be evaluable without rerunning the policy",
        "Unknown compliance cannot count as completed remediation",
        "must not conceal automatic adequacy",
    ):
        stating = [p for p in shipped if obligation in p.read_text(encoding="utf-8")]
        assert stating == [pattern], obligation


def test_design_choice_pattern_names_no_project_authority():
    pattern = read_repo_file("docs/patterns/design-choices.md")

    assert not re.search(r"MR-[0-9]|fusion|rubric|depth|\.project/", pattern, re.IGNORECASE)
