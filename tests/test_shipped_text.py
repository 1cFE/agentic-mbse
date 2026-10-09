"""Properties of the shipped text: each bundle's envelope, and what installed text points at."""

import re
from argparse import Namespace
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.cli import TOOL_OWNED_TEMPLATES, cmd_init
from tests.helpers.shipped import REPO_ROOT, SKILLS, frontmatter

SLASH_REFERENCE = re.compile(r"`(/[a-z0-9-]+)`")
SKILL_PATH = re.compile(r"\.agents/skills/([a-z0-9-]+)((?:/[\w.-]+)*)")


@pytest.mark.parametrize("skill", SKILLS)
def test_bundle_declares_its_name_description_and_kind(skill):
    meta, _ = frontmatter(REPO_ROOT / "skills" / skill / "SKILL.md")
    assert meta["name"] == skill
    assert meta["description"]
    assert meta["metadata"]["kind"] in ("workflow", "supporting")
    assert "skills" not in meta


def test_every_bundle_opens_with_one_shared_preface():
    first_paragraphs = {
        frontmatter(REPO_ROOT / "skills" / skill / "SKILL.md")[1].lstrip("\n").split("\n\n")[0]
        for skill in SKILLS
    }
    assert len(first_paragraphs) == 1


@pytest.fixture(scope="module")
def installed(tmp_path_factory) -> Path:
    target = tmp_path_factory.mktemp("installed")
    assert cmd_init(Namespace(path=str(target), force=False, dev=False, assistant="both")) == 0
    return target


def runtime_neutral_text(target: Path) -> dict[str, str]:
    """Installed text both runtimes read: bundles, tool-owned templates, Codex role instructions."""
    texts = {
        p.relative_to(target).as_posix(): p.read_text(encoding="utf-8")
        for p in (target / ".agents/skills").rglob("*")
        if p.is_file()
    }
    for _, destination in TOOL_OWNED_TEMPLATES:
        texts[destination] = (target / destination).read_text(encoding="utf-8")
    for role in (target / ".codex/agents").glob("*.toml"):
        texts[role.relative_to(target).as_posix()] = tomllib.loads(role.read_text())[
            "developer_instructions"
        ]
    return texts


def test_installed_references_name_installed_skills(installed):
    """The deletion guard: removing a skill that other text names fails here."""
    bundles = {p.parent.name for p in (installed / ".agents/skills").glob("*/SKILL.md")}
    texts = runtime_neutral_text(installed)
    for p in [
        *(installed / ".agentic-mbse").glob("*.md"),
        *(installed / ".claude/agents").glob("*.md"),
    ]:
        texts[p.relative_to(installed).as_posix()] = p.read_text(encoding="utf-8")
    for path, text in texts.items():
        for reference in SLASH_REFERENCE.findall(text):
            assert reference[1:] in bundles, f"{path} names `{reference}`"
        for name, inside in SKILL_PATH.findall(text):
            assert name in bundles, f"{path} names .agents/skills/{name}"
            named = installed / ".agents/skills" / name / inside.strip("/").rstrip(".")
            assert named.exists(), f"{path} names {named.relative_to(installed)}"


def test_runtime_neutral_text_names_no_claude_path(installed):
    """Claude roles carry the Claude adapter, which may name .claude/; nothing else may."""
    for path, text in runtime_neutral_text(installed).items():
        assert ".claude/" not in text, path


def test_guide_locates_pattern_docs_for_either_runtime(installed):
    """SC4: main's resolver text, with no Claude-only settings path."""
    guide = (installed / "modeling_project/MODELING_GUIDE.md").read_text(encoding="utf-8")
    assert "get_docs_dir()" in guide
    assert ".claude/settings.json" not in guide
