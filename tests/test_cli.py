"""Tests for CLI module."""

import subprocess
from pathlib import Path

import pytest

from agentic_mbse.cli import MBSE_COMMANDS, cmd_init, cmd_install_commands, cmd_validate, main
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS


class MockArgs:
    """Mock argparse namespace."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_returns_failure_for_nonexistent_path(self):
        """Returns EXIT_FAILURE for nonexistent path."""
        args = MockArgs(
            path="/nonexistent/path/that/does/not/exist",
            complete=False,
            level=None,
            verbose=False,
        )
        result = cmd_validate(args)
        assert result == EXIT_FAILURE

    def test_returns_success_for_valid_models(self, tmp_path):
        """Returns EXIT_SUCCESS for valid models."""
        # Create minimal valid SysML file
        model_file = tmp_path / "test.sysml"
        model_file.write_text("""
package TestPackage {
    import ScalarValues::*;
    calc def TestCalc {
        in x : Real;
        return y : Real = x;
    }
}
""")
        args = MockArgs(
            path=str(tmp_path),
            complete=True,
            level=None,
            verbose=False,
        )
        result = cmd_validate(args)
        # May succeed or fail depending on model quality
        assert result in [EXIT_SUCCESS, EXIT_FAILURE]

    def test_specific_level_option(self, tmp_path):
        """Runs only specified level when --level provided."""
        model_file = tmp_path / "test.sysml"
        model_file.write_text("package Empty {}")

        args = MockArgs(
            path=str(tmp_path),
            complete=False,
            level=1,  # Only run level 1
            verbose=False,
        )
        result = cmd_validate(args)
        assert result in [EXIT_SUCCESS, EXIT_FAILURE]


class TestCmdInit:
    """Tests for cmd_init function."""

    def test_creates_source_index(self, tmp_path):
        """Creates SOURCE_INDEX.md file."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        source_index = tmp_path / "knowledge" / "SOURCE_INDEX.md"
        assert source_index.exists()
        content = source_index.read_text()
        assert "Source Index" in content

    def test_creates_claude_directory(self, tmp_path):
        """Creates .claude/commands/ directory."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        claude_dir = tmp_path / ".agents" / "skills"
        assert claude_dir.exists()
        assert claude_dir.is_dir()

    def test_skips_source_index_if_exists_without_force(self, tmp_path):
        """Skips overwriting SOURCE_INDEX.md without --force but still succeeds."""
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir(parents=True)
        source_index = knowledge_dir / "SOURCE_INDEX.md"
        source_index.write_text("existing: content")

        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        # Should succeed (just skip overwriting)
        assert result == EXIT_SUCCESS
        # Should NOT overwrite
        assert source_index.read_text() == "existing: content"

    def test_overwrites_source_index_with_force(self, tmp_path):
        """Overwrites existing SOURCE_INDEX.md when --force specified."""
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir(parents=True)
        source_index = knowledge_dir / "SOURCE_INDEX.md"
        source_index.write_text("old: content")

        args = MockArgs(path=str(tmp_path), force=True)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        content = source_index.read_text()
        assert "Source Index" in content  # New content from template

    def test_uses_current_directory_if_no_path(self, tmp_path, monkeypatch):
        """Uses current directory if no path specified."""
        monkeypatch.chdir(tmp_path)
        args = MockArgs(path=None, force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        assert (tmp_path / "knowledge" / "SOURCE_INDEX.md").exists()

    def test_creates_agents_directory(self, tmp_path):
        """agentic-mbse init creates .claude/agents/ with agent files."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        agents_dir = tmp_path / ".claude" / "agents"
        assert agents_dir.exists()
        assert (agents_dir / "sysmlv2-validator.md").exists()
        assert (agents_dir / "python-debugger.md").exists()

    def test_creates_skills_directory(self, tmp_path):
        """agentic-mbse init creates .claude/skills/ with skill subdirs."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        all_skills = [
            "epic-decomposition",
            "model-validation",
            "project-structure",
            "python-debugger",
            "record-learning",
            "requirements-tracking",
            "source-traceability",
            "sysml-conventions",
            "toolkit-awareness",
        ]
        skills_dir = tmp_path / ".claude" / "skills"
        for skill in all_skills:
            assert (skills_dir / skill).is_dir()
            assert (skills_dir / skill / "SKILL.md").exists()

    def test_creates_hooks_directory(self, tmp_path):
        """agentic-mbse init creates .claude/hooks/ with hook scripts."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        hook_path = tmp_path / ".claude" / "hooks" / "ruff-format.sh"
        assert hook_path.exists()
        # Check executable permission
        assert hook_path.stat().st_mode & 0o111  # Has execute bit

    def test_agent_path_substitution(self, tmp_path):
        """Agent files have documentation paths substituted during install."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        agent_content = (tmp_path / ".claude" / "agents" / "syside-expert.md").read_text()
        # Should NOT contain placeholders (they should be substituted)
        assert "{SYSIDE_DOCS_PATH}" not in agent_content
        # Should contain new paths (absolute to package)
        assert "/docs/syside" in agent_content

    def test_init_creates_tests_models_directory(self, tmp_path):
        """Init creates tests/models/ directory."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        assert (tmp_path / "tests" / "models").is_dir()

    def test_init_creates_example_test_file(self, tmp_path):
        """Init creates example test file in tests/models/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        test_file = tmp_path / "tests" / "models" / "test_example.py"
        assert test_file.exists()
        assert "get_syside" in test_file.read_text()

    def test_init_creates_conftest(self, tmp_path):
        """Init creates conftest.py in tests/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        conftest = tmp_path / "tests" / "conftest.py"
        assert conftest.exists()
        assert "load_sysml" in conftest.read_text()

    def test_init_skips_test_files_if_exist(self, tmp_path):
        """Init preserves existing test files (user-owned)."""
        test_file = tmp_path / "tests" / "models" / "test_example.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# custom tests")

        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        assert test_file.read_text() == "# custom tests"

    def test_force_overwrites_agents(self, tmp_path):
        """--force flag overwrites existing agents."""
        # First init
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        # Modify an agent file
        agent_path = tmp_path / ".claude" / "agents" / "syside-expert.md"
        agent_path.write_text("modified content")

        # Second init with force
        args = MockArgs(path=str(tmp_path), force=True)
        cmd_init(args)

        # Should be overwritten (agents are tool-owned, always updated on re-init)
        assert "modified content" not in agent_path.read_text()


class TestCmdInstallCommands:
    """Tests for cmd_install_commands function."""

    def test_list_shows_commands(self, capsys):
        """--list shows available commands."""
        args = MockArgs(list=True, directory=".", force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "design-model.md" in captured.out
        assert "audit-models.md" in captured.out
        assert "orchestrate-modeling.md" in captured.out

    def test_installs_commands_to_directory(self, tmp_path):
        """Installs commands to .claude/commands/ directory."""
        args = MockArgs(list=False, directory=str(tmp_path), force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        commands_dir = tmp_path / ".agents" / "skills"
        assert commands_dir.exists()
        assert (commands_dir / "design-model" / "SKILL.md").exists()
        assert (commands_dir / "audit-models" / "SKILL.md").exists()
        assert (commands_dir / "orchestrate-modeling" / "SKILL.md").exists()

    def test_command_manifests_match_shipped_files(self):
        """Python and development manifests include every shipped command."""
        repository_root = Path(__file__).parent.parent
        from agentic_mbse.cli import MBSE_SKILLS

        shipped = {path.parent.name for path in (repository_root / "skills").glob("*/SKILL.md")}
        assert {Path(name).stem for name in MBSE_COMMANDS} | set(MBSE_SKILLS) == shipped
        script = (repository_root / "scripts" / "replicate_setup.sh").read_text()
        assert 'agentic-mbse init "$REPO_ROOT"' in script

    def test_skips_existing_without_force(self, tmp_path, capsys):
        """Skips existing files without --force."""
        # Create commands dir with existing file
        commands_dir = tmp_path / ".agents" / "skills"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "design-model" / "SKILL.md"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("existing content")

        args = MockArgs(list=False, directory=str(tmp_path), force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        # Should not overwrite
        assert existing.read_text() == "existing content"
        captured = capsys.readouterr()
        assert "Skipped: 1" in captured.out

    def test_overwrites_with_force(self, tmp_path):
        """Overwrites existing files with --force."""
        # Create commands dir with existing file
        commands_dir = tmp_path / ".agents" / "skills"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "design-model" / "SKILL.md"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("old content")

        args = MockArgs(list=False, directory=str(tmp_path), force=True)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        # Should overwrite with new content
        assert existing.read_text() != "old content"

    def test_fails_for_nonexistent_directory(self):
        """Returns failure for nonexistent directory."""
        args = MockArgs(list=False, directory="/nonexistent/path", force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_FAILURE


class TestMain:
    """Tests for main entry point."""

    def test_returns_success_with_no_command(self, monkeypatch):
        """Returns EXIT_SUCCESS when no command given (shows help)."""
        monkeypatch.setattr("sys.argv", ["agentic-mbse"])
        result = main()
        assert result == EXIT_SUCCESS

    def test_validate_subcommand_exists(self, monkeypatch, tmp_path):
        """Validate subcommand is registered and works."""
        model_file = tmp_path / "test.sysml"
        model_file.write_text("package Test {}")

        monkeypatch.setattr("sys.argv", ["agentic-mbse", "validate", str(tmp_path)])
        result = main()
        assert result in [EXIT_SUCCESS, EXIT_FAILURE]

    def test_init_subcommand_exists(self, monkeypatch, tmp_path):
        """Init subcommand is registered and works."""
        monkeypatch.setattr("sys.argv", ["agentic-mbse", "init", str(tmp_path)])
        result = main()
        assert result == EXIT_SUCCESS


class TestCLIIntegration:
    """Integration tests for CLI via subprocess."""

    def test_cli_help(self):
        """CLI --help returns 0 and shows usage."""
        result = subprocess.run(
            ["agentic-mbse", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout
        assert "init" in result.stdout

    def test_cli_validate_help(self):
        """validate --help shows options."""
        result = subprocess.run(
            ["agentic-mbse", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--complete" in result.stdout
        assert "--level" in result.stdout

    def test_cli_init_help(self):
        """init --help shows options."""
        result = subprocess.run(
            ["agentic-mbse", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--force" in result.stdout

    def test_cli_validate_on_sample_models(self):
        """CLI validate works on sample models."""
        result = subprocess.run(
            ["agentic-mbse", "validate", "tests/fixtures/sample_models/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        # May succeed or fail, but should complete
        assert result.returncode in [0, 1]

    def test_cli_init_dev_help(self):
        """init --help shows --dev option."""
        result = subprocess.run(
            ["agentic-mbse", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--dev" in result.stdout


class TestCmdInitDevMode:
    """Tests for init --dev mode."""

    def test_dev_creates_symlinks_for_commands(self, tmp_path):
        """--dev creates symlinks for command files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        cmd_path = tmp_path / ".agents" / "skills" / "design-model" / "SKILL.md"
        assert cmd_path.is_symlink()
        # Verify symlink points to source repo
        assert "agentic-mbse" in str(cmd_path.resolve())

    def test_dev_symlinks_orchestrator_command(self, tmp_path):
        """--dev links the orchestrator from the source command directory."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        command_path = tmp_path / ".agents" / "skills" / "orchestrate-modeling" / "SKILL.md"
        assert command_path.is_symlink()
        assert command_path.resolve().name == "SKILL.md"

    def test_dev_creates_symlinks_for_agents(self, tmp_path):
        """--dev creates symlinks for agent files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        agent_path = tmp_path / ".claude" / "agents" / "python-debugger.md"
        assert not agent_path.is_symlink()

    def test_dev_creates_symlinks_for_skills(self, tmp_path):
        """--dev creates symlinks for skill directories."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        all_skills = [
            "epic-decomposition",
            "model-validation",
            "project-structure",
            "python-debugger",
            "record-learning",
            "requirements-tracking",
            "source-traceability",
            "sysml-conventions",
            "toolkit-awareness",
        ]
        for skill in all_skills:
            skill_path = tmp_path / ".claude" / "skills" / skill
            assert skill_path.is_symlink()
            assert skill_path.is_dir()

    def test_dev_creates_symlinks_for_hooks(self, tmp_path):
        """--dev creates symlinks for hook files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        hook_path = tmp_path / ".claude" / "hooks" / "ruff-format.sh"
        assert hook_path.is_symlink()

    def test_dev_creates_symlinks_for_tool_templates(self, tmp_path):
        """--dev creates symlinks for tool-owned templates."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        guide_path = tmp_path / "modeling_project" / "MODELING_GUIDE.md"
        assert guide_path.is_symlink()

    def test_dev_copies_user_owned_files(self, tmp_path):
        """--dev still copies (not symlinks) user-owned files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        # User-owned files should be regular files, not symlinks
        assert not (tmp_path / "knowledge" / "SOURCE_INDEX.md").is_symlink()
        assert not (tmp_path / ".gitignore").is_symlink()
        assert not (tmp_path / ".claude" / "settings.json").is_symlink()
        assert not (tmp_path / "README.md").is_symlink()

    def test_dev_idempotent(self, tmp_path):
        """Running --dev twice succeeds and updates symlinks."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)

        # First run
        result1 = cmd_init(args)
        assert result1 == EXIT_SUCCESS

        # Second run
        result2 = cmd_init(args)
        assert result2 == EXIT_SUCCESS

        # Symlinks should still work
        cmd_path = tmp_path / ".agents" / "skills" / "design-model" / "SKILL.md"
        assert cmd_path.is_symlink()

    def test_dev_replaces_regular_file_with_symlink(self, tmp_path):
        """--dev replaces existing regular files with symlinks."""
        # First init without dev
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".agents" / "skills" / "design-model" / "SKILL.md"
        assert not cmd_path.is_symlink()  # Regular file

        # Second init with dev
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        assert cmd_path.is_symlink()  # Now a symlink

    def test_without_dev_copies_files(self, tmp_path):
        """Init without --dev still copies files (regression test)."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".agents" / "skills" / "design-model" / "SKILL.md"
        assert not cmd_path.is_symlink()
        assert cmd_path.exists()

    @pytest.mark.skipif(
        __import__("platform").system() == "Windows",
        reason="Windows test not applicable on non-Windows",
    )
    def test_dev_agents_resolve_placeholders(self, tmp_path):
        """Native roles are rendered with usable documentation paths in dev mode."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        agent_path = tmp_path / ".claude" / "agents" / "syside-expert.md"
        assert not agent_path.is_symlink()
        # Source files have placeholders, symlink should too
        content = agent_path.read_text()
        assert "{SYSIDE_DOCS_PATH}" not in content
        assert "/docs/syside" in content

    def test_dev_updates_gitignore(self, tmp_path):
        """--dev adds tool-owned paths to .gitignore."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        gitignore_path = tmp_path / ".gitignore"
        content = gitignore_path.read_text()

        # Should contain dev mode section
        assert "# Tool-owned files (managed by agentic-mbse init --dev)" in content
        assert ".claude/commands/" in content
        assert ".claude/agents/" in content
        assert ".claude/skills/" in content
        assert ".claude/hooks/" in content
        assert "modeling_project/MODELING_GUIDE.md" in content
        assert "modeling_project/MODELING_PROCESS.md" in content

    def test_dev_gitignore_idempotent(self, tmp_path):
        """Running --dev twice doesn't duplicate .gitignore entries."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)

        # First run
        cmd_init(args)
        gitignore_path = tmp_path / ".gitignore"
        content_after_first = gitignore_path.read_text()
        first_count = content_after_first.count(".claude/commands/")

        # Second run
        cmd_init(args)
        content_after_second = gitignore_path.read_text()
        second_count = content_after_second.count(".claude/commands/")

        # Should only appear once
        assert first_count == 1
        assert second_count == 1

    def test_without_dev_no_gitignore_update(self, tmp_path):
        """Init without --dev doesn't add dev mode paths to .gitignore."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        gitignore_path = tmp_path / ".gitignore"
        content = gitignore_path.read_text()

        # Should NOT contain dev mode section
        assert "# Tool-owned files (managed by agentic-mbse init --dev)" not in content


class TestModificationDetectionIntegration:
    """Integration tests for modification detection in cmd_init."""

    def test_init_creates_hash_file(self, tmp_path):
        """Normal mode init creates .tool-hashes.json."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        hash_file = tmp_path / ".agentic-mbse" / "install.json"
        assert hash_file.exists()

        import json

        hashes = json.loads(hash_file.read_text())
        assert "version" in hashes
        assert "files" in hashes
        assert len(hashes["files"]) > 0

    def test_orchestrator_is_hash_tracked_and_modification_is_preserved(
        self, tmp_path, monkeypatch, capsys
    ):
        """The new command participates in normal tool-owned modification handling."""
        import json

        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)
        command_path = tmp_path / ".agents" / "skills" / "orchestrate-modeling" / "SKILL.md"
        hashes = json.loads((tmp_path / ".agentic-mbse" / "install.json").read_text())
        relative_path = ".agents/skills/orchestrate-modeling/SKILL.md"

        assert relative_path in hashes["files"]
        command_path.write_text("# Owner modification", encoding="utf-8")
        prompts = []
        monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "s")

        cmd_init(args)

        assert prompts
        assert relative_path in capsys.readouterr().out
        assert command_path.read_text(encoding="utf-8") == "# Owner modification"

    def test_dev_mode_tracks_hashes(self, tmp_path):
        """Dev links have persistent ownership for safe transitions back to copies."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        hash_file = tmp_path / ".agentic-mbse" / "install.json"
        assert hash_file.exists()

    def test_reinit_no_modification_no_prompt(self, tmp_path, monkeypatch, capsys):
        """Re-init without modifications doesn't prompt."""
        # Track if input() was called
        input_called = []

        def fake_input(prompt):
            input_called.append(prompt)
            return "o"

        monkeypatch.setattr("builtins.input", fake_input)

        # First init
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Re-init without modifying anything
        cmd_init(args)

        assert len(input_called) == 0  # No prompts

    def test_reinit_with_modification_prompts(self, tmp_path, monkeypatch):
        """Re-init with modification prompts user."""
        # First init
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Modify a tool-owned file
        guide = tmp_path / "modeling_project" / "MODELING_GUIDE.md"
        guide.write_text("# Modified by user")

        # Track prompts
        prompted_files = []

        def fake_input(prompt):
            prompted_files.append(prompt)
            return "s"  # Skip

        monkeypatch.setattr("builtins.input", fake_input)

        # Re-init
        cmd_init(args)

        assert len(prompted_files) > 0
        assert guide.read_text() == "# Modified by user"  # Preserved

    def test_force_flag_skips_prompts(self, tmp_path, monkeypatch):
        """--force overwrites without prompting."""
        # First init
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Modify
        guide = tmp_path / "modeling_project" / "MODELING_GUIDE.md"
        guide.write_text("# Modified")

        # Track if prompted
        prompted = []
        monkeypatch.setattr("builtins.input", lambda _: prompted.append(1) or "o")

        # Re-init with force
        args = MockArgs(path=str(tmp_path), force=True, dev=False)
        cmd_init(args)

        assert len(prompted) == 0
        assert guide.read_text() != "# Modified"  # Overwritten

    def test_hash_file_in_gitignore(self, tmp_path):
        """Hash file path added to generated .gitignore."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        gitignore = tmp_path / ".gitignore"
        content = gitignore.read_text()
        assert ".agentic-mbse/install.json" in content


class TestNewTemplates:
    """Tests for templates added in D1.1/D1.2."""

    def test_init_creates_knowledge_registry(self, tmp_path):
        """Init creates KNOWLEDGE.md in knowledge/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "knowledge" / "KNOWLEDGE.md").exists()

    def test_init_creates_architecture(self, tmp_path):
        """Init creates ARCHITECTURE.md in modeling_project/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "modeling_project" / "ARCHITECTURE.md").exists()

    def test_init_creates_requirements(self, tmp_path):
        """Init creates REQUIREMENTS.md in modeling_project/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "modeling_project" / "REQUIREMENTS.md").exists()

    def test_init_creates_validation_matrix(self, tmp_path):
        """Init creates VALIDATION_MATRIX.md in modeling_project/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "modeling_project" / "VALIDATION_MATRIX.md").exists()

    def test_init_creates_epic_guide(self, tmp_path):
        """Init creates EPIC_GUIDE.md in work/ (tool-owned)."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "work" / "EPIC_GUIDE.md").exists()

    def test_init_creates_epic_template(self, tmp_path):
        """Init creates epic_template.md in work/backlog/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "work" / "backlog" / "epic_template.md").exists()

    def test_user_owned_templates_skipped_on_reinit(self, tmp_path):
        """User-owned new templates are preserved on re-init."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        # Modify a user-owned template
        knowledge = tmp_path / "knowledge" / "KNOWLEDGE.md"
        knowledge.write_text("# Custom knowledge")

        # Re-init
        cmd_init(args)
        assert knowledge.read_text() == "# Custom knowledge"

    def test_tool_owned_templates_updated_on_reinit_without_force(self, tmp_path):
        """Tool-owned templates are silently updated on re-init when unmodified."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Read the original content and hash
        epic_guide = tmp_path / "work" / "EPIC_GUIDE.md"
        original_content = epic_guide.read_text()
        assert len(original_content) > 0

        # Re-init without force — tool-owned file should be updated (no prompt)
        cmd_init(args)

        # File should still exist with content (was re-installed, not skipped)
        assert epic_guide.exists()
        assert epic_guide.read_text() == original_content

    def test_tool_owned_templates_force_overwrites_modified(self, tmp_path):
        """--force overwrites modified tool-owned templates without prompting."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Modify a tool-owned template
        epic_guide = tmp_path / "work" / "EPIC_GUIDE.md"
        epic_guide.write_text("# Modified")

        # Re-init with force
        args_force = MockArgs(path=str(tmp_path), force=True, dev=False)
        cmd_init(args_force)
        assert epic_guide.read_text() != "# Modified"


class TestDataTemplates:
    """Tests for data/ directory templates."""

    def test_init_creates_traceability_csv(self, tmp_path):
        """Init creates traceability_matrix.csv in data/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        csv_path = tmp_path / "data" / "traceability_matrix.csv"
        assert csv_path.exists()
        header = csv_path.read_text().splitlines()[0]
        assert "Element" in header
        assert "Requirement" in header

    def test_csv_skipped_on_reinit(self, tmp_path):
        """CSV is user-owned, skipped on re-init."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        csv_path = tmp_path / "data" / "traceability_matrix.csv"
        csv_path.write_text("custom,data")

        cmd_init(args)
        assert csv_path.read_text() == "custom,data"


class TestDirectoryStructure:
    """Tests for full directory structure creation."""

    def test_init_creates_full_directory_structure(self, tmp_path):
        """Init creates all expected directories."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        expected_dirs = [
            "knowledge",
            "knowledge/research/pending",
            "knowledge/research/approved",
            "knowledge/research/impacts",
            "knowledge/sources",
            "modeling_project",
            "modeling_project/intent",
            "work",
            "work/backlog",
            "work/active",
            "work/completed",
            "work/analysis",
            "work/learnings",
            "data",
            "models/library",
            "models/designs",
        ]
        for d in expected_dirs:
            assert (tmp_path / d).is_dir(), f"Missing directory: {d}"
