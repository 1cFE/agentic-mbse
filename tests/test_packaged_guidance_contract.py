"""The packaged distribution carries the source tree unchanged and installs from it.

`docs/patterns/plant-idiom.md` is the one authoritative copy of the calculation-binding
rule (self-binding-replacement D1). Two consumption modes exist and both must serve the
same bytes:

* editable development — `agentic_mbse.cli.get_docs_dir()` resolves the source checkout,
  so an edit is live immediately;
* an installed distribution — the wheel bundles a *copy* under
  ``agentic_mbse_data/docs/``, and a stale or missing copy would silently serve the old
  rule.

The same holds for every folder the installer reads (skills, agents, adapters, hooks,
templates). So the contract is behavioral: the public resolver finds the source tree in
editable mode, a freshly built wheel carries every packaged file byte for byte, and `init`
run from the extracted wheel installs every asset.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.cli import get_docs_dir
from tests.helpers.shipped import AGENTS, HOOKS, REPO_ROOT, SKILLS

PLANT_IDIOM = Path("docs") / "patterns" / "plant-idiom.md"
PACKAGED_PLANT_IDIOM = "agentic_mbse_data/docs/patterns/plant-idiom.md"
FORCE_INCLUDE: dict[str, str] = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["tool"][
    "hatch"
]["build"]["targets"]["wheel"]["force-include"]
DOCS_GAP = pytest.mark.xfail(
    strict=True,
    reason="Known packaging gap that predates the native-skill reconciliation: the wheel omits "
    "docs/syside/python/v0.8.4/syside/ (340 files). Remove this mark when it is packaged.",
)

# Runs inside the extracted wheel: argv is the extracted folder, then the install target.
INIT_FROM_WHEEL = """
import sys
from argparse import Namespace
from pathlib import Path

import agentic_mbse
from agentic_mbse.cli import cmd_init, get_docs_dir

assert Path(agentic_mbse.__file__).is_relative_to(sys.argv[1]), agentic_mbse.__file__
assert cmd_init(Namespace(path=sys.argv[2], force=False, dev=True)) == 1, "--dev from a wheel"
assert cmd_init(Namespace(path=sys.argv[2], force=False, dev=False)) == 0
print(get_docs_dir())
"""


def test_public_resolver_serves_the_source_checkout_in_editable_mode() -> None:
    """In a source checkout the resolver must return the live tree, not a copy:
    that is what makes an edit to the authoritative document take effect without
    a reinstall, and what the codegen drift contract reads through."""
    docs = get_docs_dir()
    assert docs == REPO_ROOT / "docs"
    assert (docs / "patterns" / "plant-idiom.md").is_file()


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(out)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    wheels = sorted(out.glob("agentic_mbse-*.whl"))
    assert len(wheels) == 1, [w.name for w in wheels]
    return wheels[0]


@pytest.mark.parametrize(
    "source", [pytest.param(s, marks=DOCS_GAP) if s == "docs" else s for s in FORCE_INCLUDE]
)
def test_built_wheel_carries_every_packaged_file_unchanged(wheel: Path, source: str) -> None:
    """Compares every force-included file with its wheel member: the only comparison
    that can catch a packaging omission or a stale include list."""
    root = REPO_ROOT / source
    files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
    with zipfile.ZipFile(wheel) as archive:
        members = set(archive.namelist())
        for path in files:
            if "__pycache__" in path.parts:
                continue
            name = FORCE_INCLUDE[source]
            if path != root:
                name += "/" + path.relative_to(root).as_posix()
            assert name in members, name
            assert archive.read(name) == path.read_bytes(), name


def test_built_wheel_carries_the_authoritative_document_and_no_claude_folder(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        assert archive.read(PACKAGED_PLANT_IDIOM) == (REPO_ROOT / PLANT_IDIOM).read_bytes()
        assert not [n for n in archive.namelist() if n.startswith("agentic_mbse_data/claude/")]


def test_extracted_wheel_installs_every_asset(wheel: Path, tmp_path: Path) -> None:
    """`init` from the wheel's own data installs every bundle, role and hook, and the
    docs resolver points into the packaged data (I6). `--dev` is refused there."""
    extracted = tmp_path / "site-packages"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(extracted)
    target = tmp_path / "target"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-c", INIT_FROM_WHEEL, str(extracted), str(target)],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(extracted)},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.splitlines()[-1]) == extracted / "agentic_mbse_data" / "docs"
    for skill in SKILLS:
        assert (target / ".agents/skills" / skill / "SKILL.md").is_file(), skill
        assert (target / ".claude/skills" / skill / "SKILL.md").is_file(), skill
    for agent in AGENTS:
        assert (target / ".claude/agents" / f"{agent}.md").is_file(), agent
        assert (target / ".codex/agents" / f"{agent}.toml").is_file(), agent
    for hook in HOOKS:
        assert (target / ".claude/hooks" / hook).is_file(), hook
