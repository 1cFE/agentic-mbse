"""What agentic-mbse ships, read from the source tree with the tests' own globs.

Installer tests compare against these instead of the installer's own discovery, so a test can
disagree with the installer. Adding a skill, role or hook changes them with no edit here.
"""

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = sorted(p.parent.name for p in (REPO_ROOT / "skills").glob("*/SKILL.md"))
AGENTS = sorted(p.stem for p in (REPO_ROOT / "agents").glob("*.md"))
HOOKS = sorted(p.name for p in (REPO_ROOT / "hooks").iterdir() if p.is_file())


def frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """A Markdown file's frontmatter, parsed, and the text below its closing `---` line."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[0] == "---\n", f"{path} has no frontmatter"
    close = next(i for i in range(1, len(lines)) if lines[i].rstrip("\n") == "---")
    return yaml.safe_load("".join(lines[1:close])), "".join(lines[close + 1 :])


def kind(skill: str) -> str:
    """A shipped skill's declared `metadata.kind`."""
    return str(frontmatter(REPO_ROOT / "skills" / skill / "SKILL.md")[0]["metadata"]["kind"])


def bundle_files(skill: str) -> list[str]:
    """Every file in a shipped bundle, relative to the bundle."""
    bundle = REPO_ROOT / "skills" / skill
    return sorted(
        p.relative_to(bundle).as_posix()
        for p in bundle.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )
