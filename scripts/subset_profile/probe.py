"""Run probes against the pinned generator in an isolated tree and record what it did.

    uv run python scripts/subset_profile/probe.py run (--probe ID | --all) --agentic-rev REV [--base]

Design § Probe harness, steps 1-5. One run builds one fresh tree under `--tmp-root`:

1. `git archive` exports sysml-codegen at the pin and agentic-mbse at REV as siblings, so
   codegen's `path = "../agentic-mbse"` resolves inside the tree. Each export's embedded commit
   id is checked against the requested revision.
2. `uv sync --frozen` against codegen's `uv.lock`. The SysIDE key comes from this repo's `.env`;
   only its presence is recorded.
3. `python -I` reports the package versions and `__file__` paths. Any package resolving outside
   the tree aborts the run.
4. Each probe's `model.sysml` (read from this checkout, which must have it committed and clean)
   runs through `python -m sysml_codegen generate`.
5. The judge (`tests/helpers/subset_probe_judge.py`) certifies each run, and the result is
   written to the probe's `observation.json` (`observation.base.json` with `--base`).

The sibling checkouts are only read with `git archive`; the run fails if codegen's `git status`
changes. Logs go to `.project/active/exec-subset-profile/evidence/probes/`. Exit status is 0 only
if every requested probe certifies.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tests.helpers.subset_probe_judge import (  # noqa: E402
    PINNED_CODEGEN_REV,
    FailedCheck,
    Identity,
    Observation,
    Probe,
    judge,
    load_probe,
    observation_to_json,
)

PROBES_DIR = REPO_ROOT / "tests" / "fixtures" / "subset_profile" / "probes"
LOG_DIR = REPO_ROOT / ".project" / "active" / "exec-subset-profile" / "evidence" / "probes"
BASE_REV = "a718efec"  # design base: the same-generator comparison point (design § Probe harness 6)
GENERATE_TIMEOUT_S = 900
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
) -> Identity:
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
    return Identity(
        codegen_rev=codegen_rev,
        agentic_rev=agentic_rev,
        uv_lock_sha256=hashlib.sha256(
            (tree / "sysml-codegen" / "uv.lock").read_bytes()
        ).hexdigest(),
        tree_root=str(tree),
        license_key_present=bool(env.get("SYSIDE_LICENSE_KEY")),
        **reported,
    )


def require_committed(probe_dir: Path) -> None:
    """A probe can only cite a committed fixture: probe.toml and model.sysml must be tracked and clean."""
    for name in ("probe.toml", "model.sysml"):
        path = str((probe_dir / name).relative_to(REPO_ROOT))
        if not git(REPO_ROOT, "ls-files", "--", path):
            raise SystemExit(f"{path} is not committed; commit probes before running them")
        if git(REPO_ROOT, "status", "--porcelain=v1", "--", path):
            raise SystemExit(f"{path} has uncommitted changes; commit probes before running them")


def generated_files(out: Path) -> dict[str, str]:
    if not out.exists():
        return {}
    return {
        str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.rglob("*"))
        if p.is_file()
    }


def catalog_names(out: Path) -> tuple[str, ...] | None:
    """Parameter qualified names and output channel names from `contracts/model_contract.json`."""
    catalog = out / "contracts" / "model_contract.json"
    if not catalog.exists():
        return None
    data = json.loads(catalog.read_text(encoding="utf-8"))
    names = [p["qualified_name"] for p in data["parameters"]] + [
        o["channel_name"] for o in data["outputs"]
    ]
    return tuple(sorted(names))


def mentions(
    out: Path, files: dict[str, str], names: tuple[str, ...]
) -> dict[str, tuple[str, ...]]:
    """For each name, the generated files whose text contains it as a whole identifier."""
    found: dict[str, tuple[str, ...]] = {}
    for name in names:
        token = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])")
        found[name] = tuple(
            f
            for f in files
            if token.search((out / f).read_text(encoding="utf-8", errors="replace"))
        )
    return found


def run_probe(
    probe: Probe, tree: Path, python: Path, env: dict[str, str], identity: Identity, log: Path
) -> Observation:
    work = tree / "probes" / probe.id
    model = work / "in" / probe.construct.file
    model.parent.mkdir(parents=True)
    shutil.copyfile(PROBES_DIR / probe.id / probe.construct.file, model)
    out = work / "out"
    argv = [
        str(python),
        "-I",
        "-m",
        "sysml_codegen",
        "generate",
        "--models",
        str(model),
        "--output",
        str(out),
    ]
    try:
        done = subprocess.run(
            argv, cwd=tree, env=env, capture_output=True, text=True, timeout=GENERATE_TIMEOUT_S
        )
        exit_code, stdout, stderr, timed_out = done.returncode, done.stdout, done.stderr, False
    except subprocess.TimeoutExpired as expired:
        exit_code, timed_out = -1, True
        stdout, stderr = str(expired.stdout or ""), str(expired.stderr or "")
    log.write_text(
        f"$ {' '.join(argv)}\nexit={exit_code} timed_out={timed_out}\n--- stdout\n{stdout}--- stderr\n{stderr}"
    )
    files = generated_files(out)
    return Observation(
        probe_id=probe.id,
        model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
        identity=identity,
        argv=tuple(argv),
        exit_code=exit_code,
        timed_out=timed_out,
        error_lines=tuple(
            line for line in (stdout + stderr).splitlines() if line.startswith("ERROR: ")
        ),
        generated_files=files,
        catalog_names=catalog_names(out),
        mentions=mentions(out, files, probe.declared_names()),
    )


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run probes in a fresh isolated tree")
    which = run.add_mutually_exclusive_group(required=True)
    which.add_argument("--probe", help="one probe id (its directory name)")
    which.add_argument(
        "--all", action="store_true", help="every probe under tests/fixtures/subset_profile/probes"
    )
    run.add_argument("--agentic-rev", required=True, help="agentic-mbse revision to export")
    run.add_argument(
        "--base", action="store_true", help=f"same-generator comparison run at {BASE_REV}"
    )
    run.add_argument("--codegen-repo", type=Path, default=Path.home() / "src" / "sysml-codegen")
    run.add_argument("--tmp-root", type=Path, default=Path("/tmp/subset-profile"))
    run.add_argument(
        "--keep-tree",
        action="store_true",
        help="keep the temp tree even when every probe certifies",
    )
    args = parser.parse_args()

    codegen_repo = args.codegen_repo.resolve()
    agentic_rev = resolve_rev(REPO_ROOT, args.agentic_rev)
    if args.base and agentic_rev != resolve_rev(REPO_ROOT, BASE_REV):
        raise SystemExit(f"--base observations are taken at {BASE_REV}, not {agentic_rev}")
    codegen_rev = resolve_rev(codegen_repo, PINNED_CODEGEN_REV)

    probe_dirs = (
        sorted(d for d in PROBES_DIR.iterdir() if d.is_dir())
        if args.all
        else [PROBES_DIR / args.probe]
    )
    probes = [load_probe(d) for d in probe_dirs]
    for d in probe_dirs:
        require_committed(d)

    args.tmp_root.mkdir(parents=True, exist_ok=True)
    tree = Path(tempfile.mkdtemp(prefix="run-", dir=args.tmp_root)).resolve()
    for checkout in (codegen_repo, REPO_ROOT):
        if tree.is_relative_to(checkout):
            raise IsolationBreachError(f"temp tree {tree} is inside the checkout {checkout}")
    codegen_before = sibling_state(codegen_repo)

    env = child_env(read_license_key())
    python = build_tree(tree, codegen_repo, codegen_rev, agentic_rev, env)
    identity = read_identity(tree, python, env, codegen_rev, agentic_rev)
    print(f"tree {tree}\nidentity {json.dumps(vars(identity))}")

    suffix = ".base" if args.base else ""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[tuple[str, FailedCheck]] = []
    for probe in probes:
        obs = run_probe(probe, tree, python, env, identity, LOG_DIR / f"{probe.id}{suffix}.log")
        certification = judge(probe, obs)
        document = observation_to_json(obs, certification)
        (PROBES_DIR / probe.id / f"observation{suffix}.json").write_text(
            json.dumps(document, indent=2) + "\n"
        )
        print(
            f"{probe.id}: exit={obs.exit_code} certifies={certification.certifies} failed_check={certification.failed_check}"
        )
        if certification.failed_check is not None:
            failures.append((probe.id, certification.failed_check))
            if certification.failed_check == FailedCheck.REFUSED_PROBE_ADMITTED:
                print(
                    f"R2: {probe.id} expected a refusal and the pinned generator admitted it. Stop this pair; see the plan's R2 map."
                )

    if sibling_state(codegen_repo) != codegen_before:
        raise IsolationBreachError(f"{codegen_repo} changed during the run")
    if failures or args.keep_tree:
        print(f"kept tree {tree}")
    else:
        shutil.rmtree(tree)
    print(f"{len(probes) - len(failures)}/{len(probes)} probes certify")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
