"""Installer lifecycle regressions across platforms, aliases, migration, and ownership."""

import json
import os
from argparse import Namespace
from pathlib import Path

import pytest
import tomllib
import yaml

from agentic_mbse.cli import MBSE_COMMANDS, MBSE_SKILLS, cmd_init, cmd_install_commands
from agentic_mbse.cli.installation import LEGACY_MANIFEST, MANIFEST, Installer, fingerprint


def init(target, **options):
    return cmd_init(Namespace(path=str(target), force=False, dev=False, **options))


def test_fingerprint_tracks_link_without_reading_target(tmp_path):
    source = tmp_path / "source"
    source.write_text("private")
    link = tmp_path / "link"
    link.symlink_to(source)
    assert fingerprint(link) == "link:" + str(source)
    source.unlink()
    assert fingerprint(link) == "link:" + str(source)
    assert fingerprint(source) is None


@pytest.mark.parametrize("assistant", ["claude", "codex", "both"])
@pytest.mark.parametrize("link_mode", ["symlink", "copy"])
def test_native_install_catalog_and_roles(tmp_path, assistant, link_mode):
    assert init(tmp_path, assistant=assistant, link_mode=link_mode) == 0
    expected = {Path(n).stem for n in MBSE_COMMANDS} | set(MBSE_SKILLS)
    assert {p.name for p in (tmp_path / ".agents/skills").iterdir()} == expected
    for name in expected:
        source = tmp_path / ".agents/skills" / name / "SKILL.md"
        meta = yaml.safe_load(source.read_text().split("---", 2)[1])
        assert meta["name"] == name
        assert meta["description"]
        assert "skills" not in meta
        if assistant != "codex":
            alias = tmp_path / ".claude/skills" / name
            assert alias.is_symlink() == (link_mode == "symlink")
            if alias.is_symlink():
                assert not os.path.isabs(os.readlink(alias))
            assert (alias / "SKILL.md").read_bytes() == source.read_bytes()
    assert (tmp_path / ".claude").exists() == (assistant != "codex")
    assert (tmp_path / ".codex").exists() == (assistant != "claude")
    if assistant != "claude":
        roles = list((tmp_path / ".codex/agents").glob("*.toml"))
        assert len(roles) == 5
        for p in roles:
            role = tomllib.loads(p.read_text())
            assert role["name"] == p.stem
            assert "{SYS" not in role["developer_instructions"]
            if p.stem in ("kerml-expert", "sysml-expert", "syside-expert"):
                assert role["sandbox_mode"] == "read-only"


def test_skipped_skill_edit_and_owner_resource_survive_four_inits(tmp_path):
    init(tmp_path)
    skill = tmp_path / ".agents/skills/pdf-analysis"
    entry = skill / "SKILL.md"
    relative = entry.relative_to(tmp_path).as_posix()
    original = json.loads((tmp_path / MANIFEST).read_text())["files"][relative]
    entry.write_text("Owner customization")
    (skill / "references/owner.md").write_text("Owner addition")
    for _ in range(3):
        init(tmp_path)
        assert entry.read_text() == "Owner customization"
        assert (skill / "references/owner.md").read_text() == "Owner addition"
        assert json.loads((tmp_path / MANIFEST).read_text())["files"][relative] == original


@pytest.mark.parametrize("modified", [False, True])
def test_migrate_legacy_command_without_shadowing(tmp_path, modified):
    path = tmp_path / ".claude/commands/design-model.md"
    path.parent.mkdir(parents=True)
    path.write_text("Original command")
    baseline = fingerprint(path)
    (tmp_path / LEGACY_MANIFEST).write_text(
        json.dumps({"files": {".claude/commands/design-model.md": baseline}})
    )
    if modified:
        path.write_text("Owner command")
    for _ in range(3):
        init(tmp_path)
        assert path.exists() == modified
        assert (tmp_path / ".claude/skills/design-model").exists() != modified
        if modified:
            assert path.read_text() == "Owner command"
            assert (
                json.loads((tmp_path / MANIFEST).read_text())["files"][
                    ".claude/commands/design-model.md"
                ]
                == baseline
            )


def test_unknown_legacy_command_is_preserved(tmp_path):
    path = tmp_path / ".claude/commands/research.md"
    path.parent.mkdir(parents=True)
    path.write_text("Custom research")
    init(tmp_path)
    assert path.read_text() == "Custom research"
    assert not (tmp_path / ".claude/skills/research").exists()


def test_forced_command_install_never_writes_through_symlink(tmp_path):
    outside = tmp_path / "referent"
    outside.write_text("Do not change")
    path = tmp_path / ".claude/commands/design-model.md"
    path.parent.mkdir(parents=True)
    path.symlink_to(outside)
    canonical = tmp_path / ".agents/skills/research/SKILL.md"
    canonical.parent.mkdir(parents=True)
    canonical.symlink_to(outside)
    assert cmd_install_commands(Namespace(directory=str(tmp_path), force=True, list=False)) == 0
    assert outside.read_text() == "Do not change"
    assert not path.exists()
    assert not canonical.is_symlink()
    assert (tmp_path / ".claude/skills/design-model/SKILL.md").is_file()


def test_parent_symlink_is_preserved_even_under_force(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "owner.md").write_text("keep")
    (tmp_path / ".agents").symlink_to(outside, target_is_directory=True)
    cmd_install_commands(Namespace(directory=str(tmp_path), force=True, list=False))
    assert list(outside.iterdir()) == [outside / "owner.md"]


def test_copy_link_dev_transitions_preserve_owner_additions(tmp_path):
    init(tmp_path, link_mode="copy")
    alias = tmp_path / ".claude/skills/pdf-analysis"
    (alias / "owner.md").write_text("keep")
    init(tmp_path, link_mode="symlink")
    assert not alias.is_symlink()
    assert (alias / "owner.md").read_text() == "keep"
    untouched = tmp_path / ".claude/skills/design-model"
    assert untouched.is_symlink()
    cmd_init(Namespace(path=str(tmp_path), force=False, dev=True))
    canonical = tmp_path / ".agents/skills/design-model/SKILL.md"
    assert canonical.is_symlink()
    init(tmp_path, link_mode="copy")
    assert not canonical.is_symlink()
    assert not untouched.is_symlink()
    assert (alias / "owner.md").read_text() == "keep"


def test_native_owner_configuration_preserved_with_force(tmp_path):
    originals = {
        "AGENTS.md": "My rules",
        "CLAUDE.md": "My other rules",
        ".codex/config.toml": 'model = "custom"',
        ".claude/settings.json": '{"permissions": {"deny": ["Bash"]}}',
    }
    for name, content in originals.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    cmd_init(Namespace(path=str(tmp_path), force=True, dev=False))
    for name, content in originals.items():
        if name == ".codex/config.toml":
            installed = tomllib.loads((tmp_path / name).read_text())
            assert installed["model"] == "custom"
            assert (tmp_path / name).read_text().startswith(content)
        else:
            assert (tmp_path / name).read_text() == content


def test_relocated_aliases_and_support_files(tmp_path):
    project = tmp_path / "original"
    project.mkdir()
    init(project)
    moved = tmp_path / "relocated"
    project.rename(moved)
    for p in (moved / ".claude/skills").iterdir():
        assert (p / "SKILL.md").is_file()
    assert (moved / ".claude/skills/pdf-analysis/scripts/extract_page.py").is_file()
    assert (moved / ".claude/skills/sysml-conventions/references/stencils.md").is_file()


def test_backup_then_update_and_skipped_baseline(tmp_path):
    installer = Installer(tmp_path, force=False, decide=lambda path: "backup")
    installer.write("file.md", b"original")
    installer.save()
    (tmp_path / "file.md").write_text("local")
    installer = Installer(tmp_path, force=False, decide=lambda path: "backup")
    installer.write("file.md", b"updated")
    installer.save()
    assert (tmp_path / "file.md.backup").read_text() == "local"
    assert (tmp_path / "file.md").read_text() == "updated"


def test_owner_directory_at_file_destination_is_backed_up(tmp_path):
    path = tmp_path / "file.md"
    path.mkdir()
    (path / "owner.txt").write_text("keep")
    installer = Installer(tmp_path, force=True, decide=lambda path: "skip")
    installer.write("file.md", b"installed")
    assert (tmp_path / "file.md.backup/owner.txt").read_text() == "keep"
    assert path.read_text() == "installed"


def test_native_manifest_finds_codex_only_project(tmp_path, monkeypatch):
    from agentic_mbse.cli import find_project_root

    cmd_install_commands(
        Namespace(directory=str(tmp_path), force=False, list=False, assistant="codex")
    )
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)
    assert find_project_root() == tmp_path


def test_empty_owner_directory_survives_copy_to_link(tmp_path):
    init(tmp_path, link_mode="copy")
    skill = tmp_path / ".claude/skills/research"
    (skill / "my-references").mkdir()
    init(tmp_path)
    assert (skill / "my-references").is_dir()
    assert not skill.is_symlink()


def test_codex_role_registration_preserves_owner_roles_and_comments(tmp_path):
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    original = '# Owner settings\n[agents."sysml-expert"]\ndescription = "My expert"\nconfig_file = "custom.toml"\n'
    config.write_text(original)
    init(tmp_path, assistant="codex")
    installed = config.read_text()
    parsed = tomllib.loads(installed)
    assert installed.startswith(original)
    assert parsed["agents"]["sysml-expert"]["config_file"] == "custom.toml"
    assert parsed["agents"]["kerml-expert"]["config_file"] == "agents/kerml-expert.toml"
    init(tmp_path, assistant="codex")
    assert config.read_text() == installed


def test_codex_registration_does_not_write_through_owner_symlink(tmp_path):
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    owner = tmp_path / "owner.toml"
    owner.write_text('# owner\nmodel = "custom"\n')
    config.symlink_to(owner)
    init(tmp_path, assistant="codex")
    assert config.is_symlink()
    assert owner.read_text() == '# owner\nmodel = "custom"\n'


def test_inline_codex_agents_table_is_not_corrupted(tmp_path, capsys):
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    original = 'agents = { owner = { description = "Owner role" } }\n'
    config.write_text(original)
    init(tmp_path, assistant="codex")
    assert config.read_text() == original
    assert "merge MBSE role registrations manually" in capsys.readouterr().out
    assert tomllib.loads(config.read_text())["agents"]["owner"]["description"] == "Owner role"
