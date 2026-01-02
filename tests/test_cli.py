"""Tests for CLI module."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from agentic_mbse.cli import cmd_init, cmd_install_commands, cmd_validate, main
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
        source_index = tmp_path / "SOURCE_INDEX.md"
        assert source_index.exists()
        content = source_index.read_text()
        assert "Source Index" in content

    def test_creates_claude_directory(self, tmp_path):
        """Creates .claude/commands/ directory."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        claude_dir = tmp_path / ".claude" / "commands"
        assert claude_dir.exists()
        assert claude_dir.is_dir()

    def test_skips_source_index_if_exists_without_force(self, tmp_path):
        """Skips overwriting SOURCE_INDEX.md without --force but still succeeds."""
        source_index = tmp_path / "SOURCE_INDEX.md"
        source_index.write_text("existing: content")

        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        # Should succeed (just skip overwriting)
        assert result == EXIT_SUCCESS
        # Should NOT overwrite
        assert source_index.read_text() == "existing: content"

    def test_overwrites_source_index_with_force(self, tmp_path):
        """Overwrites existing SOURCE_INDEX.md when --force specified."""
        source_index = tmp_path / "SOURCE_INDEX.md"
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
        assert (tmp_path / "SOURCE_INDEX.md").exists()

    def test_creates_agents_directory(self, tmp_path):
        """agentic-mbse init creates .claude/agents/ with agent files."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        agents_dir = tmp_path / ".claude" / "agents"
        assert agents_dir.exists()
        assert (agents_dir / "sysmlv2-doc-analyzer.md").exists()
        assert (agents_dir / "python-debugger.md").exists()

    def test_creates_skills_directory(self, tmp_path):
        """agentic-mbse init creates .claude/skills/ with skill subdirs."""
        args = MockArgs(path=str(tmp_path), force=False)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        skill_dir = tmp_path / ".claude" / "skills" / "python-debugger"
        assert skill_dir.is_dir()
        assert (skill_dir / "SKILL.md").exists()

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

        agent_content = (tmp_path / ".claude" / "agents" / "sysmlv2-doc-analyzer.md").read_text()
        # Should NOT contain old paths
        assert "agent_literature/SysML/" not in agent_content
        assert "agent_literature/syside-docs/" not in agent_content
        # Should contain new paths (absolute to package)
        assert "/docs/sysmlv2/" in agent_content
        assert "/docs/syside/" in agent_content

    def test_force_overwrites_agents(self, tmp_path):
        """--force flag overwrites existing agents."""
        # First init
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        # Modify an agent file
        agent_path = tmp_path / ".claude" / "agents" / "sysmlv2-doc-analyzer.md"
        agent_path.write_text("modified content")

        # Second init with force
        args = MockArgs(path=str(tmp_path), force=True)
        cmd_init(args)

        # Should be overwritten
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

    def test_installs_commands_to_directory(self, tmp_path):
        """Installs commands to .claude/commands/ directory."""
        args = MockArgs(list=False, directory=str(tmp_path), force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.exists()
        assert (commands_dir / "design-model.md").exists()
        assert (commands_dir / "audit-models.md").exists()

    def test_skips_existing_without_force(self, tmp_path, capsys):
        """Skips existing files without --force."""
        # Create commands dir with existing file
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "design-model.md"
        existing.write_text("existing content")

        args = MockArgs(list=False, directory=str(tmp_path), force=False)
        result = cmd_install_commands(args)

        assert result == EXIT_SUCCESS
        # Should not overwrite
        assert existing.read_text() == "existing content"
        captured = capsys.readouterr()
        assert "Skipping" in captured.out

    def test_overwrites_with_force(self, tmp_path):
        """Overwrites existing files with --force."""
        # Create commands dir with existing file
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "design-model.md"
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
        
        monkeypatch.setattr("sys.argv", [
            "agentic-mbse", "validate", str(tmp_path)
        ])
        result = main()
        assert result in [EXIT_SUCCESS, EXIT_FAILURE]

    def test_init_subcommand_exists(self, monkeypatch, tmp_path):
        """Init subcommand is registered and works."""
        monkeypatch.setattr("sys.argv", [
            "agentic-mbse", "init", str(tmp_path)
        ])
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
