"""Contract tests for the shipped modeling workflow commands and documentation."""

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
    assert "positive independent audit" in flow
    assert "cross-item integration" in flow
    assert "dependency" in flow.lower()


def test_epic_audit_has_explicit_integration_scope():
    audit = read_repo_file("claude/commands/audit-models.md")

    assert "Epic audit" in audit
    assert "epic success criteria" in audit
    assert "item audit" in audit
    assert "cross-item integration" in audit


def test_touched_workflow_docs_have_no_stale_commands_or_validation_levels():
    touched_paths = (
        "claude/commands/backlog.md",
        "claude/commands/status.md",
        "claude/commands/plan-model.md",
        "claude/commands/implement-model.md",
        "project_templates/EPIC_GUIDE.md.template",
        "project_templates/README.md.template",
    )
    content = "\n".join(read_repo_file(path) for path in touched_paths)

    assert "pm add-to-backlog" not in content
    assert "/backlog clear" not in content
    assert "Levels 4-8" not in content
    assert "Levels 7-8" not in content


def test_orchestrator_frontmatter_and_single_alignment_contract():
    command = read_repo_file("claude/commands/orchestrate-modeling.md")

    assert "name: orchestrate-modeling" in command
    assert "Task" in command.partition("---")[2].partition("---")[0]
    assert "user-invocable: true" in command
    assert command.count("## Align Once") == 1
    assert "only planned owner checkpoint" in command
    assert "before launching any stage" in command
    assert "work/orchestration/<objective-slug>.md" in command


def test_orchestrator_uses_fresh_self_contained_noninteractive_tasks():
    command = read_repo_file("claude/commands/orchestrate-modeling.md")
    normalized_command = " ".join(command.split())
    lowercase_command = normalized_command.lower()

    assert "fresh Task agent" in normalized_command
    assert "self-contained stage brief" in normalized_command
    assert "Do not interact with the owner" in normalized_command
    assert "return all blocking questions before writing" in lowercase_command
    assert "original brief plus the answers" in normalized_command
    assert "fresh authoring and audit contexts" in normalized_command


def test_orchestrator_declares_routes_decision_tiers_and_bounded_repair():
    command = read_repo_file("claude/commands/orchestrate-modeling.md")

    assert "Standard route" in command and "Epic route" in command
    assert "Execution detail" in command
    assert "Reserved gate" in command
    assert "Premise surprise" in command
    assert "two unsuccessful repair-and-audit rounds" in command
    assert "no material progress" in command
    assert "owner decides whether to close" in command


def test_orchestrator_does_not_embed_a_runtime_or_automatic_close():
    command = read_repo_file("claude/commands/orchestrate-modeling.md").lower()

    for prohibited in (
        "orchestrate-stage.sh",
        "session_id",
        "run database",
        "fixed state table",
        "automatically close",
        "automatically archive",
    ):
        assert prohibited not in command
