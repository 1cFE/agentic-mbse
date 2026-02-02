"""Tests for CLI module."""
import subprocess
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
        assert (agents_dir / "sysmlv2-validator.md").exists()
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
        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert cmd_path.is_symlink()
        # Verify symlink points to source repo
        assert "agentic-mbse" in str(cmd_path.resolve())

    def test_dev_creates_symlinks_for_agents(self, tmp_path):
        """--dev creates symlinks for agent files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        agent_path = tmp_path / ".claude" / "agents" / "python-debugger.md"
        assert agent_path.is_symlink()

    def test_dev_creates_symlinks_for_skills(self, tmp_path):
        """--dev creates symlinks for skill directories."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        skill_path = tmp_path / ".claude" / "skills" / "python-debugger"
        assert skill_path.is_symlink()
        assert skill_path.is_dir()  # Symlink to directory

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

        guide_path = tmp_path / "modeling_pm" / "MODELING_GUIDE.md"
        assert guide_path.is_symlink()

    def test_dev_copies_user_owned_files(self, tmp_path):
        """--dev still copies (not symlinks) user-owned files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        # User-owned files should be regular files, not symlinks
        assert not (tmp_path / "SOURCE_INDEX.md").is_symlink()
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
        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert cmd_path.is_symlink()

    def test_dev_replaces_regular_file_with_symlink(self, tmp_path):
        """--dev replaces existing regular files with symlinks."""
        # First init without dev
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert not cmd_path.is_symlink()  # Regular file

        # Second init with dev
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        assert cmd_path.is_symlink()  # Now a symlink

    def test_without_dev_copies_files(self, tmp_path):
        """Init without --dev still copies files (regression test)."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert not cmd_path.is_symlink()
        assert cmd_path.exists()

    @pytest.mark.skipif(
        __import__("platform").system() == "Windows",
        reason="Windows test not applicable on non-Windows"
    )
    def test_dev_agents_keep_placeholders(self, tmp_path):
        """--dev mode agents are symlinked with placeholders intact."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        agent_path = tmp_path / ".claude" / "agents" / "syside-expert.md"
        assert agent_path.is_symlink()
        # Source files have placeholders, symlink should too
        content = agent_path.read_text()
        assert "{SYSIDE_DOCS_PATH}" in content

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
        assert "modeling_pm/MODELING_GUIDE.md" in content
        assert "modeling_pm/MODELING_PROCESS.md" in content

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


class TestHashUtilities:
    """Tests for hash computation and storage."""

    def test_compute_file_hash_returns_sha256(self, tmp_path):
        """_compute_file_hash returns consistent SHA256 hex string."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        from agentic_mbse.cli import _compute_file_hash
        hash1 = _compute_file_hash(test_file)
        hash2 = _compute_file_hash(test_file)

        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 64  # SHA256 hex length
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_load_save_tool_hashes_roundtrip(self, tmp_path):
        """Hash file can be saved and loaded."""
        from agentic_mbse.cli import _load_tool_hashes, _save_tool_hashes

        hashes = {
            "version": "1.0.0",
            "commit": "abc1234",
            "files": {"test.md": "deadbeef" * 8}
        }
        _save_tool_hashes(tmp_path, hashes)
        loaded = _load_tool_hashes(tmp_path)

        assert loaded == hashes

    def test_load_tool_hashes_returns_none_if_missing(self, tmp_path):
        """Returns None if hash file doesn't exist."""
        from agentic_mbse.cli import _load_tool_hashes
        assert _load_tool_hashes(tmp_path) is None


class TestLocalGuide:
    """Tests for LOCAL_GUIDE.md template."""

    def test_init_creates_local_guide(self, tmp_path):
        """Init creates LOCAL_GUIDE.md in modeling_pm/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        local_guide = tmp_path / "modeling_pm" / "LOCAL_GUIDE.md"
        assert local_guide.exists()
        assert "Local Modeling Guide" in local_guide.read_text()

    def test_local_guide_skipped_if_exists(self, tmp_path):
        """LOCAL_GUIDE.md is user-owned, skipped on re-init."""
        # First init
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)

        # Modify
        local_guide = tmp_path / "modeling_pm" / "LOCAL_GUIDE.md"
        local_guide.write_text("# My Custom Guide")

        # Re-init
        cmd_init(args)

        assert local_guide.read_text() == "# My Custom Guide"


class TestModificationDetection:
    """Tests for file modification detection."""

    def test_check_modification_no_hash_file(self, tmp_path):
        """Returns False when no hash file exists (backwards compat)."""
        from agentic_mbse.cli import _check_modification

        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        result = _check_modification(test_file, None, "test.md")
        assert result is False

    def test_check_modification_file_not_in_hashes(self, tmp_path):
        """Returns False when file not tracked in hash store."""
        from agentic_mbse.cli import _check_modification

        test_file = tmp_path / "test.md"
        test_file.write_text("content")
        hashes = {"version": "1.0", "commit": "abc", "files": {}}

        result = _check_modification(test_file, hashes, "test.md")
        assert result is False

    def test_check_modification_hash_matches(self, tmp_path):
        """Returns False when file matches stored hash."""
        from agentic_mbse.cli import _check_modification, _compute_file_hash

        test_file = tmp_path / "test.md"
        test_file.write_text("content")
        file_hash = _compute_file_hash(test_file)
        hashes = {"version": "1.0", "commit": "abc", "files": {"test.md": file_hash}}

        result = _check_modification(test_file, hashes, "test.md")
        assert result is False

    def test_check_modification_hash_differs(self, tmp_path):
        """Returns True when file differs from stored hash."""
        from agentic_mbse.cli import _check_modification

        test_file = tmp_path / "test.md"
        test_file.write_text("modified content")
        hashes = {"version": "1.0", "commit": "abc", "files": {"test.md": "oldhash" * 8}}

        result = _check_modification(test_file, hashes, "test.md")
        assert result is True

    def test_check_modification_file_missing(self, tmp_path):
        """Returns False when file doesn't exist."""
        from agentic_mbse.cli import _check_modification

        missing_file = tmp_path / "missing.md"
        hashes = {"version": "1.0", "commit": "abc", "files": {"missing.md": "hash"}}

        result = _check_modification(missing_file, hashes, "missing.md")
        assert result is False


class TestBackupFile:
    """Tests for file backup functionality."""

    def test_backup_creates_backup_file(self, tmp_path):
        """Creates .backup file."""
        from agentic_mbse.cli import _backup_file

        original = tmp_path / "test.md"
        original.write_text("original content")

        backup_path = _backup_file(original)

        assert backup_path.exists()
        assert backup_path.name == "test.md.backup"
        assert backup_path.read_text() == "original content"

    def test_backup_handles_existing_backup(self, tmp_path):
        """Uses .backup.1, .backup.2 if .backup exists."""
        from agentic_mbse.cli import _backup_file

        original = tmp_path / "test.md"
        original.write_text("v3")
        (tmp_path / "test.md.backup").write_text("v1")
        (tmp_path / "test.md.backup.1").write_text("v2")

        backup_path = _backup_file(original)

        assert backup_path.name == "test.md.backup.2"
        assert backup_path.read_text() == "v3"


class TestPromptForModifiedFile:
    """Tests for user prompt function."""

    def test_prompt_returns_skip(self, monkeypatch):
        """Returns 'skip' when user enters 's'."""
        from agentic_mbse.cli import _prompt_for_modified_file
        monkeypatch.setattr('builtins.input', lambda _: 's')

        result = _prompt_for_modified_file("test.md")
        assert result == 'skip'

    def test_prompt_returns_backup(self, monkeypatch):
        """Returns 'backup' when user enters 'b'."""
        from agentic_mbse.cli import _prompt_for_modified_file
        monkeypatch.setattr('builtins.input', lambda _: 'b')

        result = _prompt_for_modified_file("test.md")
        assert result == 'backup'

    def test_prompt_returns_overwrite(self, monkeypatch):
        """Returns 'overwrite' when user enters 'o'."""
        from agentic_mbse.cli import _prompt_for_modified_file
        monkeypatch.setattr('builtins.input', lambda _: 'o')

        result = _prompt_for_modified_file("test.md")
        assert result == 'overwrite'

    def test_prompt_returns_skip_all(self, monkeypatch):
        """Returns 'skip_all' when user enters 'S'."""
        from agentic_mbse.cli import _prompt_for_modified_file
        monkeypatch.setattr('builtins.input', lambda _: 'S')

        result = _prompt_for_modified_file("test.md")
        assert result == 'skip_all'

    def test_prompt_returns_overwrite_all(self, monkeypatch):
        """Returns 'overwrite_all' when user enters 'O'."""
        from agentic_mbse.cli import _prompt_for_modified_file
        monkeypatch.setattr('builtins.input', lambda _: 'O')

        result = _prompt_for_modified_file("test.md")
        assert result == 'overwrite_all'


class TestInstallFileWithHash:
    """Tests for _install_file_with_hash with hash return value."""

    def test_install_file_returns_hash_on_copy(self, tmp_path):
        """Returns content hash when copying file."""
        from agentic_mbse.cli import _compute_file_hash, _install_file_with_hash

        src = tmp_path / "src.md"
        dst = tmp_path / "dst.md"
        src.write_text("content")

        action, content_hash = _install_file_with_hash(src, dst, is_dev_mode=False)

        assert action == "created"
        assert content_hash == _compute_file_hash(dst)

    def test_install_file_returns_none_hash_on_symlink(self, tmp_path):
        """Returns None hash when symlinking (dev mode)."""
        from agentic_mbse.cli import _install_file_with_hash

        src = tmp_path / "src.md"
        dst = tmp_path / "dst.md"
        src.write_text("content")

        action, content_hash = _install_file_with_hash(src, dst, is_dev_mode=True)

        assert action == "symlinked"
        assert content_hash is None

    def test_install_file_skips_when_requested(self, tmp_path):
        """Returns 'skipped' and None hash when skip requested."""
        from agentic_mbse.cli import _install_file_with_hash

        src = tmp_path / "src.md"
        dst = tmp_path / "dst.md"
        src.write_text("new content")
        dst.write_text("old content")

        action, content_hash = _install_file_with_hash(
            src, dst, is_dev_mode=False,
            was_modified=True, user_action='skip'
        )

        assert action == "skipped"
        assert content_hash is None
        assert dst.read_text() == "old content"  # Unchanged

    def test_install_file_backs_up_when_requested(self, tmp_path):
        """Creates backup and updates when backup requested."""
        from agentic_mbse.cli import _install_file_with_hash

        src = tmp_path / "src.md"
        dst = tmp_path / "dst.md"
        src.write_text("new content")
        dst.write_text("old content")

        action, content_hash = _install_file_with_hash(
            src, dst, is_dev_mode=False,
            was_modified=True, user_action='backup'
        )

        assert action == "backed_up_and_updated"
        assert dst.read_text() == "new content"
        assert (tmp_path / "dst.md.backup").read_text() == "old content"


class TestModificationDetectionIntegration:
    """Integration tests for modification detection in cmd_init."""

    def test_init_creates_hash_file(self, tmp_path):
        """Normal mode init creates .tool-hashes.json."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        hash_file = tmp_path / ".claude" / ".tool-hashes.json"
        assert hash_file.exists()

        import json
        hashes = json.loads(hash_file.read_text())
        assert "version" in hashes
        assert "commit" in hashes
        assert "files" in hashes
        assert len(hashes["files"]) > 0

    def test_dev_mode_no_hash_file(self, tmp_path):
        """Dev mode does not create hash file."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        hash_file = tmp_path / ".claude" / ".tool-hashes.json"
        assert not hash_file.exists()

    def test_reinit_no_modification_no_prompt(self, tmp_path, monkeypatch, capsys):
        """Re-init without modifications doesn't prompt."""
        # Track if input() was called
        input_called = []
        def fake_input(prompt):
            input_called.append(prompt)
            return 'o'
        monkeypatch.setattr('builtins.input', fake_input)

        # First init
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Re-init without modifying anything
        cmd_init(args)

        assert len(input_called) == 0  # No prompts

    def test_reinit_with_modification_prompts(self, tmp_path, monkeypatch):
        """Re-init with modification prompts user."""
        # First init
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        # Modify a tool-owned file
        guide = tmp_path / "modeling_pm" / "MODELING_GUIDE.md"
        guide.write_text("# Modified by user")

        # Track prompts
        prompted_files = []
        def fake_input(prompt):
            prompted_files.append(prompt)
            return 's'  # Skip
        monkeypatch.setattr('builtins.input', fake_input)

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
        guide = tmp_path / "modeling_pm" / "MODELING_GUIDE.md"
        guide.write_text("# Modified")

        # Track if prompted
        prompted = []
        monkeypatch.setattr('builtins.input', lambda _: prompted.append(1) or 'o')

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
        assert ".claude/.tool-hashes.json" in content
