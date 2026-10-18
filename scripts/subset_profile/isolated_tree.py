"""Build an isolated sysml-codegen + agentic-mbse tree from `git archive` exports.

The helpers the subset-profile scripts share (design D13 of EXEC-SUBSET-CONTRACT Item 2a):

1. `git archive` exports sysml-codegen and agentic-mbse at the requested revisions as siblings,
   so codegen's `path = "../agentic-mbse"` resolves inside the tree. Each export's embedded commit
   id is checked against the requested revision.
2. `uv sync --frozen` against codegen's `uv.lock`. The SysIDE key comes from this repo's `.env`;
   only its presence is recorded.
3. `python -I` reports the package versions and `__file__` paths. Any package resolving outside
   the tree aborts the run.

The sibling checkouts are only read with `git archive`. Callers compare `sibling_state` before and
after a run, so a run that changes a checkout fails.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parents[2]
# The sysml-codegen checkout beside this one, the same layout as codegen's `../agentic-mbse` path
# dependency, so a worktree pair reads its own sibling.
CODEGEN_SIBLING = REPO_ROOT.parent / "sysml-codegen"
# Variables that would point the child at a Python environment other than the tree's own.
_FOREIGN_ENV = ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "UV_PROJECT_ENVIRONMENT", "CONDA_PREFIX")

IDENTITY_SCRIPT = """
import importlib.metadata as m, json, sys
import agentic_mbse, syside, sysml_codegen
print(json.dumps({
    "sysml_codegen_version": m.version("sysml-codegen"),
    "agentic_mbse_version": m.version("agentic-mbse"),
    "syside_version": syside.__version__,
    "python_version": sys.version.split()[0],
    "sysml_codegen_file": sysml_codegen.__file__,
    "agentic_mbse_file": agentic_mbse.__file__,
    "syside_file": syside.__file__,
}))
"""


class IsolationBreachError(RuntimeError):
    """The run touched, or resolved code from, something outside its temp tree."""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def resolve_rev(repo: Path, rev: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}")


def sibling_state(repo: Path) -> str:
    """HEAD plus the full porcelain status; any difference after a run is a breach."""
    return (
        git(repo, "rev-parse", "HEAD")
        + "\n"
        + git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    )


def export_tree(repo: Path, commit: str, dest: Path) -> None:
    """Extract `git archive <commit>` into `dest`, after checking the archive's embedded commit id."""
    archive = subprocess.run(
        ["git", "-C", str(repo), "archive", commit], check=True, capture_output=True
    ).stdout
    embedded = (
        subprocess.run(["git", "get-tar-commit-id"], input=archive, check=True, capture_output=True)
        .stdout.decode()
        .strip()
    )
    if embedded != commit:
        raise IsolationBreachError(
            f"archive of {repo} carries commit {embedded!r}, expected {commit}"
        )
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter=_assistant_links_skipped)


# A link to an absolute path would reach outside the tree. The only ones the pinned exports carry
# are assistant configuration (sysml-codegen's `.claude/agents/*`, `.claude/skills/*`), which the
# generator never reads; those are skipped and named on the console. Any other aborts the export.
_ASSISTANT_CONFIG = ".claude/"


def _assistant_links_skipped(member: tarfile.TarInfo, dest: str) -> tarfile.TarInfo | None:
    if member.issym() and os.path.isabs(member.linkname):
        if not member.name.startswith(_ASSISTANT_CONFIG):
            raise IsolationBreachError(f"{member.name} links outside the tree to {member.linkname}")
        print(f"skipped absolute link {member.name} -> {member.linkname}")
        return None
    return tarfile.data_filter(member, dest)


def read_license_key() -> str:
    key = dotenv_values(REPO_ROOT / ".env").get("SYSIDE_LICENSE_KEY")
    if not key:
        raise SystemExit(f"SYSIDE_LICENSE_KEY is missing from {REPO_ROOT / '.env'}")
    return key


def child_env(license_key: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _FOREIGN_ENV}
    env["SYSIDE_LICENSE_KEY"] = license_key
    return env


def read_identity(
    tree: Path, python: Path, env: dict[str, str], codegen_rev: str, agentic_rev: str
) -> dict[str, str | bool]:
    """The tree's resolved environment. Raises IsolationBreachError if any package lives outside it."""
    reported = json.loads(
        subprocess.run(
            [str(python), "-I", "-c", IDENTITY_SCRIPT],
            cwd=tree,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    for key in ("sysml_codegen_file", "agentic_mbse_file", "syside_file"):
        if not Path(reported[key]).resolve().is_relative_to(tree):
            raise IsolationBreachError(f"{key} resolves outside the tree {tree}: {reported[key]}")
    return {
        "codegen_rev": codegen_rev,
        "agentic_rev": agentic_rev,
        "uv_lock_sha256": hashlib.sha256(
            (tree / "sysml-codegen" / "uv.lock").read_bytes()
        ).hexdigest(),
        "tree_root": str(tree),
        "license_key_present": bool(env.get("SYSIDE_LICENSE_KEY")),
        **reported,
    }


def build_tree(
    tree: Path, codegen_repo: Path, codegen_rev: str, agentic_rev: str, env: dict[str, str]
) -> Path:
    """Steps 1-2. Returns the tree's Python."""
    export_tree(codegen_repo, codegen_rev, tree / "sysml-codegen")
    export_tree(REPO_ROOT, agentic_rev, tree / "agentic-mbse")
    sync = subprocess.run(
        ["uv", "sync", "--frozen"],
        cwd=tree / "sysml-codegen",
        env=env,
        capture_output=True,
        text=True,
    )
    (tree / "uv-sync.log").write_text(sync.stdout + sync.stderr)
    if sync.returncode != 0:
        raise SystemExit(f"uv sync --frozen failed in {tree}; see {tree / 'uv-sync.log'}")
    return tree / "sysml-codegen" / ".venv" / "bin" / "python"
