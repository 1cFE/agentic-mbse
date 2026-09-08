"""Throwaway probe for update risks in the existing installer."""

import contextlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agentic_mbse import cli


def init(target, answers):
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return answers

    with contextlib.redirect_stdout(io.StringIO()), patch("builtins.input", answer):
        status = cli.cmd_init(SimpleNamespace(path=str(target), force=False, dev=False))
    assert status == 0
    return len(prompts)


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="mbse-installer-probe-") as temporary:
        root = Path(temporary)
        command_project = root / "command-project"
        command_project.mkdir()
        init(command_project, "s")
        command_relative = ".claude/commands/spec-model.md"
        command = command_project / command_relative
        original_command = command.read_text()
        edited_command = "# Probe owner command edit\n"
        command.write_text(edited_command)
        second_prompts = init(command_project, "s")
        second_preserved = command.read_text() == edited_command
        second_hashes = json.loads((command_project / cli.HASH_FILE).read_text())
        third_prompts = init(command_project, "s")
        results["command_skip_then_reinit"] = {
            "second_init_prompts": second_prompts,
            "second_init_preserved_edit": second_preserved,
            "second_manifest_retains_command_hash": command_relative in second_hashes["files"],
            "third_init_prompts": third_prompts,
            "third_init_preserved_edit": command.read_text() == edited_command,
            "third_init_restored_shipped_content": command.read_text() == original_command,
        }

        skill_project = root / "skill-project"
        skill_project.mkdir()
        init(skill_project, "s")
        skill = skill_project / ".claude/skills/model-validation/SKILL.md"
        original_skill = skill.read_text()
        skill.write_text("# Probe owner skill edit\n")
        addition = skill.parent / "probe-local-note.txt"
        addition.write_text("Owner addition\n")
        skill_prompts = init(skill_project, "s")
        results["skill_update"] = {
            "prompts": skill_prompts,
            "restored_shipped_content": skill.read_text() == original_skill,
            "preserved_local_addition": addition.exists(),
        }

        source = root / "source"
        source.mkdir()
        (source / "probe.md").write_text("new source bytes\n")
        copy_project = root / "copy-project"
        destination = copy_project / ".claude/commands/probe.md"
        destination.parent.mkdir(parents=True)
        referent = root / "temporary-referent.md"
        referent.write_text("old referent bytes\n")
        destination.symlink_to(referent)
        with patch.object(cli, "MBSE_COMMANDS", ["probe.md"]), patch.object(
            cli, "get_commands_dir", return_value=source
        ), contextlib.redirect_stdout(io.StringIO()):
            status = cli.cmd_install_commands(
                SimpleNamespace(directory=str(copy_project), force=True, list=False)
            )
        assert status == 0
        results["command_only_forced_copy_to_symlink"] = {
            "destination_remains_symlink": destination.is_symlink(),
            "referent_was_overwritten": referent.read_text() == "new source bytes\n",
        }

        referent.write_text("old referent bytes\n")
        action, digest = cli._install_file_with_hash(source / "probe.md", destination, False)
        results["hash_aware_copy_to_symlink"] = {
            "action": action,
            "destination_remains_symlink": destination.is_symlink(),
            "referent_preserved": referent.read_text() == "old referent bytes\n",
            "copied_source_content": destination.read_text() == "new source bytes\n",
            "hash_returned": digest is not None,
        }

    rendered = json.dumps(results, indent=2) + "\n"
    Path(__file__).with_name("installer-results.json").write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
