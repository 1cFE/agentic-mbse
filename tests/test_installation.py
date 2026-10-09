"""Installer lifecycle regressions across platforms, aliases, migration, and ownership."""

import json
import os
import shutil
from argparse import Namespace
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.cli import cmd_init, cmd_install_commands
from agentic_mbse.cli.installation import (
    LEGACY_MANIFEST,
    MANIFEST,
    Installer,
    fingerprint,
    legacy_link_target,
)
from tests.helpers.shipped import AGENTS, HOOKS, REPO_ROOT, SKILLS, bundle_files, frontmatter, kind

WORKFLOW = next(skill for skill in SKILLS if kind(skill) == "workflow")
OTHER_WORKFLOW = next(s for s in SKILLS if kind(s) == "workflow" and s != WORKFLOW)
SUPPORTING = next(skill for skill in SKILLS if kind(skill) == "supporting")
WITH_REFERENCES = next(s for s in SKILLS if (REPO_ROOT / "skills" / s / "references").is_dir())
# One shipped entry per location the pre-native installer linked: .claude/<kind>/<name>.
LEGACY_ENTRIES = {
    "commands": f"{WORKFLOW}.md",
    "skills": SUPPORTING,
    "agents": f"{AGENTS[0]}.md",
    "hooks": HOOKS[0],
}


def init(target, **options):
    return cmd_init(Namespace(path=str(target), force=False, dev=False, **options))


def fake_data_root(tmp_path: Path) -> Path:
    """A writable package source: skills/ and agents/ copied, the rest linked to this checkout."""
    data = tmp_path / "package"
    for name in ("skills", "agents"):
        shutil.copytree(REPO_ROOT / name, data / name)
    for name in ("adapters", "hooks", "docs", "project_templates"):
        (data / name).symlink_to(REPO_ROOT / name, target_is_directory=True)
    (data / "src" / "agentic_mbse").mkdir(parents=True)
    return data


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
    """Every file of every shipped bundle is reachable, byte-equal, for each runtime choice."""
    assert init(tmp_path, assistant=assistant, link_mode=link_mode) == 0
    assert sorted(p.name for p in (tmp_path / ".agents/skills").iterdir()) == SKILLS
    for name in SKILLS:
        canonical = tmp_path / ".agents/skills" / name
        alias = tmp_path / ".claude/skills" / name
        if assistant != "codex":
            assert alias.is_symlink() == (link_mode == "symlink")
            if alias.is_symlink():
                assert not os.path.isabs(os.readlink(alias))
        for inside in bundle_files(name):
            source = (REPO_ROOT / "skills" / name / inside).read_bytes()
            assert (canonical / inside).read_bytes() == source
            if assistant != "codex":
                assert (alias / inside).read_bytes() == source
    assert (tmp_path / ".claude").exists() == (assistant != "codex")
    assert (tmp_path / ".codex").exists() == (assistant != "claude")
    if assistant != "codex":
        assert sorted(p.stem for p in (tmp_path / ".claude/agents").glob("*.md")) == AGENTS
    if assistant != "claude":
        roles = sorted((tmp_path / ".codex/agents").glob("*.toml"))
        assert [p.stem for p in roles] == AGENTS
        for p in roles:
            role = tomllib.loads(p.read_text())
            assert role["name"] == p.stem
            assert "{SYS" not in role["developer_instructions"]
            tools = frontmatter(REPO_ROOT / "agents" / f"{p.stem}.md")[0]["tools"]
            assert (role.get("sandbox_mode") == "read-only") == ("Bash" not in tools)


def test_skipped_skill_edit_and_owner_resource_survive_four_inits(tmp_path):
    init(tmp_path)
    skill = tmp_path / ".agents/skills" / WITH_REFERENCES
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
def test_migrate_legacy_command_without_shadowing(tmp_path, modified, capsys):
    relative = f".claude/commands/{WORKFLOW}.md"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("Original command")
    baseline = fingerprint(path)
    (tmp_path / LEGACY_MANIFEST).write_text(json.dumps({"files": {relative: baseline}}))
    if modified:
        path.write_text("Owner command")
    for _ in range(3):
        init(tmp_path)
        assert path.exists() == modified
        assert (tmp_path / ".claude/skills" / WORKFLOW).exists() != modified
        if modified:
            assert path.read_text() == "Owner command"
            assert json.loads((tmp_path / MANIFEST).read_text())["files"][relative] == baseline

    if modified:
        output = capsys.readouterr().out
        assert f"Claude retains {relative}" in output
        assert f"Codex discovers .agents/skills/{WORKFLOW}/SKILL.md" in output
        assert "different versions" in output


def test_unknown_legacy_command_is_preserved(tmp_path):
    path = tmp_path / f".claude/commands/{WORKFLOW}.md"
    path.parent.mkdir(parents=True)
    path.write_text("Custom command")
    init(tmp_path)
    assert path.read_text() == "Custom command"
    assert not (tmp_path / ".claude/skills" / WORKFLOW).exists()


def test_forced_command_install_never_writes_through_symlink(tmp_path):
    outside = tmp_path / "referent"
    outside.write_text("Do not change")
    path = tmp_path / f".claude/commands/{WORKFLOW}.md"
    path.parent.mkdir(parents=True)
    path.symlink_to(outside)
    canonical = tmp_path / ".agents/skills" / SUPPORTING / "SKILL.md"
    canonical.parent.mkdir(parents=True)
    canonical.symlink_to(outside)
    assert cmd_install_commands(Namespace(directory=str(tmp_path), force=True, list=False)) == 0
    assert outside.read_text() == "Do not change"
    assert not path.exists()
    assert not canonical.is_symlink()
    assert (tmp_path / ".claude/skills" / WORKFLOW / "SKILL.md").is_file()


def test_parent_symlink_is_preserved_even_under_force(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "owner.md").write_text("keep")
    (tmp_path / ".agents").symlink_to(outside, target_is_directory=True)
    cmd_install_commands(Namespace(directory=str(tmp_path), force=True, list=False))
    assert list(outside.iterdir()) == [outside / "owner.md"]


def test_copy_link_dev_transitions_preserve_owner_additions(tmp_path):
    init(tmp_path, link_mode="copy")
    alias = tmp_path / ".claude/skills" / SUPPORTING
    (alias / "owner.md").write_text("keep")
    init(tmp_path, link_mode="symlink")
    assert not alias.is_symlink()
    assert (alias / "owner.md").read_text() == "keep"
    untouched = tmp_path / ".claude/skills" / WORKFLOW
    assert untouched.is_symlink()
    cmd_init(Namespace(path=str(tmp_path), force=False, dev=True))
    canonical = tmp_path / ".agents/skills" / WORKFLOW
    assert canonical.is_symlink()
    init(tmp_path, link_mode="copy")
    assert not canonical.is_symlink()
    assert not (canonical / "SKILL.md").is_symlink()
    assert not untouched.is_symlink()
    assert (alias / "owner.md").read_text() == "keep"


def test_dev_over_per_file_dev_install_links_each_folder(tmp_path, monkeypatch, capsys):
    """The earlier --dev made a real folder of file links per bundle; each becomes one link."""
    data = fake_data_root(tmp_path)
    monkeypatch.setattr("agentic_mbse.cli._get_data_root", lambda: data)
    target = tmp_path / "target"
    target.mkdir()
    earlier = Installer(target, force=False, decide=lambda path: "skip")
    for name in SKILLS:
        earlier.copy_tree(data / "skills" / name, f".agents/skills/{name}", dev=True)
    earlier.save()
    assert (target / ".agents/skills" / WORKFLOW / "SKILL.md").is_symlink()

    cmd_init(Namespace(path=str(target), force=False, dev=True))
    assert "instead of linking it" not in capsys.readouterr().out
    files = json.loads((target / MANIFEST).read_text())["files"]
    for name in SKILLS:
        source = data / "skills" / name
        assert os.readlink(target / ".agents/skills" / name) == str(source.resolve())
        assert not [key for key in files if key.startswith(f".agents/skills/{name}/")]
        # Replacing the folder of links removed only the links, never what they named.
        for inside in bundle_files(name):
            assert (source / inside).read_bytes() == (
                REPO_ROOT / "skills" / name / inside
            ).read_bytes()


@pytest.mark.parametrize("force", [False, True])
def test_dev_copies_a_bundle_folder_holding_owner_files(tmp_path, capsys, force):
    """An owner file or edit keeps its bundle a real folder: a plain copy, never file links."""
    init(tmp_path)
    added = tmp_path / ".agents/skills" / WORKFLOW / "owner.md"
    added.write_text("owner addition")
    edited = tmp_path / ".agents/skills" / OTHER_WORKFLOW / "SKILL.md"
    edited.write_text("owner edit")
    capsys.readouterr()

    cmd_init(Namespace(path=str(tmp_path), force=force, dev=True))
    output = capsys.readouterr().out
    assert added.read_text() == "owner addition"
    assert (edited.read_text() == "owner edit") != force
    for name in SKILLS:
        shared = tmp_path / ".agents/skills" / name
        blocked = name in (WORKFLOW, OTHER_WORKFLOW)
        assert shared.is_symlink() != blocked
        assert (f"Copied .agents/skills/{name} instead of linking it" in output) == blocked
        assert not (shared / "SKILL.md").is_symlink()
        if blocked:
            for inside in bundle_files(name):
                assert not (shared / inside).is_symlink()
        assert (tmp_path / ".claude/skills" / name / "SKILL.md").is_file()
    assert (tmp_path / ".agents/skills" / WORKFLOW / "SKILL.md").read_bytes() == (
        REPO_ROOT / "skills" / WORKFLOW / "SKILL.md"
    ).read_bytes()


def test_plain_init_over_dev_copies_every_bundle(tmp_path, monkeypatch):
    """Plain init replaces each --dev folder link with a copy, without writing through it."""
    data = fake_data_root(tmp_path)
    monkeypatch.setattr("agentic_mbse.cli._get_data_root", lambda: data)
    target = tmp_path / "target"
    target.mkdir()
    cmd_init(Namespace(path=str(target), force=False, dev=True))
    assert (target / ".agents/skills" / WORKFLOW).is_symlink()
    sources = sorted((data / "skills").rglob("*"))

    init(target)
    assert sorted((data / "skills").rglob("*")) == sources
    files = json.loads((target / MANIFEST).read_text())["files"]
    for name in SKILLS:
        shared = target / ".agents/skills" / name
        assert not shared.is_symlink()
        assert f".agents/skills/{name}" not in files
        for inside in bundle_files(name):
            assert not (shared / inside).is_symlink()
            assert (shared / inside).read_bytes() == (data / "skills" / name / inside).read_bytes()
            assert f".agents/skills/{name}/{inside}" in files


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
    for name in SKILLS:
        for inside in bundle_files(name):
            assert (moved / ".claude/skills" / name / inside).is_file()


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
    skill = tmp_path / ".claude/skills" / WORKFLOW
    (skill / "my-references").mkdir()
    init(tmp_path)
    assert (skill / "my-references").is_dir()
    assert not skill.is_symlink()


def test_codex_role_registration_preserves_owner_roles_and_comments(tmp_path):
    owned, installed_role = AGENTS[0], AGENTS[1]
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    original = f'# Owner settings\n[agents."{owned}"]\ndescription = "My expert"\nconfig_file = "custom.toml"\n'
    config.write_text(original)
    init(tmp_path, assistant="codex")
    installed = config.read_text()
    parsed = tomllib.loads(installed)
    assert installed.startswith(original)
    assert parsed["agents"][owned]["config_file"] == "custom.toml"
    assert parsed["agents"][installed_role]["config_file"] == f"agents/{installed_role}.toml"
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


# Under --dev the shared folder is one link to the source, so only Claude's copy has files to retire.
@pytest.mark.parametrize(
    ("dev", "link_mode", "copied"),
    [
        (False, "symlink", ".agents/skills"),
        (False, "copy", ".agents/skills"),
        (True, "copy", ".claude/skills"),
    ],
)
def test_bundle_retirement_prunes_only_unchanged_resources(
    tmp_path, monkeypatch, capsys, dev, link_mode, copied
):
    data = fake_data_root(tmp_path)
    source = data / "skills" / WORKFLOW
    for name in ("retired.md", "edited.md", "missing.md"):
        (source / name).write_text("original")
    target = tmp_path / "target"
    target.mkdir()
    monkeypatch.setattr("agentic_mbse.cli._get_data_root", lambda: data)
    args = Namespace(path=str(target), force=False, dev=dev, link_mode=link_mode)
    cmd_init(args)
    bundle = f"{copied}/{WORKFLOW}"
    canonical = target / bundle
    edited = canonical / "edited.md"
    # Replace a dev link to make a target-local edit without changing the source.
    if edited.is_symlink():
        edited.unlink()
    edited.write_text("owner edit")
    (canonical / "missing.md").unlink()
    (canonical / "owner.md").write_text("owner addition")
    before = json.loads((target / MANIFEST).read_text())["files"]
    for name in ("retired.md", "edited.md", "missing.md"):
        (source / name).unlink()
    for _ in range(2):
        # Even force must preserve edited retired files: they are no longer current assets.
        args.force = True
        cmd_init(args)
        state = json.loads((target / MANIFEST).read_text())["files"]
        assert not (canonical / "retired.md").exists()
        assert not (canonical / "retired.md").is_symlink()
        assert (canonical / "edited.md").read_text() == "owner edit"
        assert (canonical / "owner.md").read_text() == "owner addition"
        assert f"{bundle}/retired.md" not in state
        assert f"{bundle}/missing.md" not in state
        assert state[f"{bundle}/edited.md"] == before[f"{bundle}/edited.md"]
        assert not (target / ".claude/skills" / WORKFLOW / "retired.md").exists()
    output = capsys.readouterr().out
    assert "Removed (" in output
    assert f"Preserved retired resource {bundle}/edited.md" in output


def test_added_skill_and_role_need_no_other_edit(tmp_path, monkeypatch, capsys):
    """SC5: a new bundle folder and a new role file are installed and listed, nothing else edited."""
    data = fake_data_root(tmp_path)
    skill = data / "skills/new-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: new-skill\ndescription: A new workflow.\nmetadata:\n  kind: workflow\n---\n\nSteps.\n"
    )
    (data / "agents/new-role.md").write_text(
        "---\nname: new-role\ndescription: A new expert.\ntools: Read, Grep\n---\n\nAdvice.\n"
    )
    monkeypatch.setattr("agentic_mbse.cli._get_data_root", lambda: data)
    target = tmp_path / "target"
    target.mkdir()

    assert init(target, assistant="both") == 0
    assert (target / ".agents/skills/new-skill/SKILL.md").is_file()
    assert (target / ".claude/skills/new-skill/SKILL.md").is_file()
    assert (target / ".claude/agents/new-role.md").is_file()
    assert (target / ".codex/agents/new-role.toml").is_file()
    assert "new-role" in tomllib.loads((target / ".codex/config.toml").read_text())["agents"]
    capsys.readouterr()
    cmd_install_commands(Namespace(list=True, directory=str(target), force=False))
    workflows = capsys.readouterr().out.split("Supporting skills (")[0]
    assert "  - new-skill\n" in workflows


def test_pruning_does_not_follow_redirected_parent_or_manifest_path(tmp_path, capsys):
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("entry")
    outside = tmp_path / "outside"
    outside.mkdir()
    resource = outside / "old.md"
    resource.write_text("keep")
    installer = Installer(tmp_path, force=True, decide=lambda _: "overwrite")
    redirected = tmp_path / ".agents/skills/test/references"
    redirected.parent.mkdir(parents=True)
    redirected.symlink_to(outside, target_is_directory=True)
    for key in (
        ".agents/skills/test/references/old.md",
        ".agents/skills/test/../../../outside/old.md",
    ):
        installer.files[key] = fingerprint(resource)
    installer.copy_tree(source, ".agents/skills/test")
    assert resource.read_text() == "keep"
    assert len(installer.actions["skipped"]) == 2
    assert "redirected path" in capsys.readouterr().out


@pytest.mark.parametrize("decision", ["skip_all", "overwrite_all", "backup", "overwrite"])
def test_conflict_decisions_apply_across_files_and_reinit(tmp_path, decision):
    installer = Installer(tmp_path, force=False, decide=lambda _: "skip")
    for name in ("one.md", "two.md"):
        installer.write(name, b"original")
    installer.save()
    for name in ("one.md", "two.md"):
        (tmp_path / name).write_text("local")
    decisions = []

    def decide(path):
        decisions.append(path)
        return decision

    installer = Installer(tmp_path, force=False, decide=decide)
    for name in ("one.md", "two.md"):
        installer.write(name, b"updated")
    installer.save()
    assert len(decisions) == (1 if decision.endswith("_all") else 2)
    for name in ("one.md", "two.md"):
        assert (tmp_path / name).read_text() == ("local" if decision == "skip_all" else "updated")
        if decision == "backup":
            assert (tmp_path / (name + ".backup")).read_text() == "local"
    decisions.clear()
    installer = Installer(tmp_path, force=False, decide=decide)
    for name in ("one.md", "two.md"):
        installer.write(name, b"updated")
    assert len(decisions) == (1 if decision == "skip_all" else 0)


def test_each_installed_skill_routes_to_existing_native_adapters(tmp_path):
    import re

    from agentic_mbse.cli import _get_data_root

    init(tmp_path)
    for skill in (tmp_path / ".agents/skills").glob("*/SKILL.md"):
        body = skill.read_text().split("---", 2)[2].lstrip()
        preamble = body.split("\n\n", 1)[0]
        paths = set(re.findall(r"`(\.agentic-mbse/[^`]+\.md)`", preamble))
        assert paths == {".agentic-mbse/claude.md", ".agentic-mbse/codex.md"}, skill
        for path in paths:
            assert (tmp_path / path).read_bytes() == (
                _get_data_root() / "adapters" / Path(path).name
            ).read_bytes()


def old_checkout(tmp_path: Path) -> Path:
    """A pre-native agentic-mbse checkout after the merge: src/agentic_mbse kept, claude/ gone.

    `x/` exists so that a `{old}/x/../...` link still names this checkout; only the `..` check
    may reject it.
    """
    root = tmp_path / "old"
    (root / "src" / "agentic_mbse").mkdir(parents=True)
    (root / "x").mkdir()
    return root


def entry_state(path: Path) -> object:
    """An entry as it stands, without following links: its link text, bytes, or child states."""
    if path.is_symlink():
        return ("link", os.readlink(path))
    if path.is_file():
        return ("file", path.read_bytes())
    return ("dir", sorted((child.name, entry_state(child)) for child in path.iterdir()))


@pytest.mark.parametrize(
    "text, adopted",
    [
        ("{old}/claude/commands/{cmd}.md", True),
        ("{old}/claude/skills/{cmd}.md", False),  # tail does not mirror the entry
        ("{old}/claude/commands/{other}.md", False),  # another shipped entry's name
        ("{plain}/claude/commands/{cmd}.md", False),  # root lacks src/agentic_mbse
        ("../../old/claude/commands/{cmd}.md", False),  # relative text
        ("{old}/x/../claude/commands/{cmd}.md", False),  # '..' segment
        ("{old}/./claude/commands/{cmd}.md", False),  # '.' segment, which pathlib would hide
        ("{old}/claude/commands/{cmd}.md/", False),  # empty segment
    ],
)
def test_legacy_link_target_accepts_exactly_what_the_old_installer_wrote(tmp_path, text, adopted):
    old = old_checkout(tmp_path)
    (tmp_path / "plain").mkdir()
    relative = f".claude/commands/{WORKFLOW}.md"
    link = tmp_path / "target" / relative
    link.parent.mkdir(parents=True)
    written = text.format(old=old, plain=tmp_path / "plain", cmd=WORKFLOW, other=OTHER_WORKFLOW)
    os.symlink(written, link)  # the raw text; pathlib would normalize it
    assert legacy_link_target(tmp_path / "target", relative) == (written if adopted else None)


@pytest.mark.parametrize("referent_exists", [True, False])
@pytest.mark.parametrize("location", LEGACY_ENTRIES)
def test_legacy_link_is_adopted_and_replaced_by_the_install(
    tmp_path, capsys, location, referent_exists
):
    name = LEGACY_ENTRIES[location]
    referent = old_checkout(tmp_path) / "claude" / location / name
    old_file = referent / "SKILL.md" if location == "skills" else referent
    if referent_exists:
        old_file.parent.mkdir(parents=True)
        old_file.write_text("old installer's copy")
    entry = tmp_path / "target/.claude" / location / name
    entry.parent.mkdir(parents=True)
    os.symlink(str(referent), entry)

    assert init(tmp_path / "target") == 0
    report = capsys.readouterr().out.splitlines()
    assert f"  A .claude/{location}/{name} (was -> {referent})" in report
    # Listed once: an adopted entry is not also counted as created, updated or symlinked.
    assert not {f"  {mark} .claude/{location}/{name}" for mark in "+~@"} & set(report)
    if location == "commands":
        assert not entry.exists() and not entry.is_symlink()
        entry = tmp_path / "target/.claude/skills" / WORKFLOW
    if location in ("commands", "skills"):
        assert entry.is_symlink() and not os.path.isabs(os.readlink(entry))
        assert (entry / "SKILL.md").is_file()
    else:
        assert entry.is_file() and not entry.is_symlink()
    if location == "hooks":
        assert entry.stat().st_mode & 0o111
    if referent_exists:
        assert old_file.read_text() == "old installer's copy"


@pytest.mark.parametrize(
    "case",
    [
        "unshipped name",
        "non-checkout root",
        "non-mirrored tail",
        "another entry's name",
        "relative text",
        "'..' segment",
        "real file",
        "real directory",
    ],
)
def test_entries_the_old_installer_did_not_make_keep_prompt_or_preserve(tmp_path, case):
    old = old_checkout(tmp_path)
    (tmp_path / "plain" / "src").mkdir(parents=True)
    target = tmp_path / "target"
    commands = target / ".claude/commands"
    commands.mkdir(parents=True)
    entry = commands / ("not-shipped.md" if case == "unshipped name" else f"{WORKFLOW}.md")
    links = {
        "unshipped name": f"{old}/claude/commands/not-shipped.md",
        "non-checkout root": f"{tmp_path}/plain/claude/commands/{WORKFLOW}.md",
        "non-mirrored tail": f"{old}/claude/skills/{WORKFLOW}.md",
        "another entry's name": f"{old}/claude/commands/{OTHER_WORKFLOW}.md",
        "relative text": f"../../../old/claude/commands/{WORKFLOW}.md",
        "'..' segment": f"{old}/x/../claude/commands/{WORKFLOW}.md",
    }
    if case in links:
        os.symlink(links[case], entry)
    elif case == "real file":
        entry.write_text("owner command")
    else:
        entry.mkdir()
        (entry / "notes.md").write_text("owner notes")
    before = entry_state(entry)

    assert init(target) == 0
    assert entry_state(entry) == before
    # A preserved command keeps Claude on it: no skill alias may shadow it.
    assert (target / ".claude/skills" / WORKFLOW).is_symlink() == (case == "unshipped name")


@pytest.mark.parametrize("command", ["init", "install-commands"])
def test_mixed_legacy_tree_adopts_every_shipped_link_and_keeps_owner_entries(
    tmp_path, capsys, command
):
    old = old_checkout(tmp_path)
    target = tmp_path / "target"
    shipped = [
        *(f"commands/{s}.md" for s in SKILLS if kind(s) == "workflow"),
        *(f"skills/{s}" for s in SKILLS if kind(s) == "supporting"),
        *(f"agents/{a}.md" for a in AGENTS),
        *(f"hooks/{h}" for h in HOOKS),
    ]
    for entry in shipped:
        link = target / ".claude" / entry
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(f"{old}/claude/{entry}", link)
    owner_skill = target / ".claude/skills/owner-skill"
    owner_skill.mkdir()
    (owner_skill / "SKILL.md").write_text("---\nname: owner-skill\n---\n")
    owner_command = target / ".claude/commands/owner-command.md"
    os.symlink(f"{old}/claude/commands/owner-command.md", owner_command)
    owner_link = target / ".agents/skills/owner-skill"
    owner_link.parent.mkdir(parents=True)
    os.symlink("../../.claude/skills/owner-skill", owner_link)
    owners = [owner_skill, owner_command, owner_link]
    before = [entry_state(p) for p in owners]

    if command == "init":
        assert init(target) == 0
        assert f"Adopted ({len(shipped)})" in capsys.readouterr().out
    else:
        args = Namespace(directory=str(target), force=False, list=False)
        assert cmd_install_commands(args) == 0
        assert f"Adopted: {len(shipped)}" in capsys.readouterr().out
    for skill in SKILLS:
        assert (target / ".claude/skills" / skill / "SKILL.md").is_file(), skill
    assert [entry_state(p) for p in owners] == before
