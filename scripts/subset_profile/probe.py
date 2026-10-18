"""Run probes against the pinned generator in an isolated tree and record what it did.

    uv run python scripts/subset_profile/probe.py run (--probe ID | --all) --agentic-rev REV [--base]

Design § Probe harness, steps 1-5. One run builds one fresh tree under `--tmp-root`:

1-3. `isolated_tree.py` exports sysml-codegen at the pin and agentic-mbse at REV as siblings,
   syncs the tree and checks that every package resolves inside it.
4. Each probe's `model.sysml` (read from this checkout, which must have it committed and clean)
   runs through `python -m sysml_codegen generate`.
5. The judge (`tests/helpers/subset_probe_judge.py`) certifies each run, and the result is
   written to the probe's `observation.json` (`observation.base.json` with `--base`).

The sibling checkouts are only read with `git archive`; the run fails if codegen's `git status`
changes. Logs go to `--log-dir`. Exit status is 0 only if every requested probe certifies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from isolated_tree import (  # noqa: E402
    CODEGEN_SIBLING,
    IsolationBreachError,
    build_tree,
    child_env,
    git,
    read_identity,
    read_license_key,
    resolve_rev,
    sibling_state,
)

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
BASE_REV = "a718efec"  # design base: the same-generator comparison point (design § Probe harness 6)
GENERATE_TIMEOUT_S = 900


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
    run.add_argument("--codegen-repo", type=Path, default=CODEGEN_SIBLING)
    run.add_argument("--log-dir", type=Path, required=True, help="where each probe's run log goes")
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
    identity = Identity(**read_identity(tree, python, env, codegen_rev, agentic_rev))
    print(f"tree {tree}\nidentity {json.dumps(vars(identity))}")

    suffix = ".base" if args.base else ""
    args.log_dir.mkdir(parents=True, exist_ok=True)
    failures: list[tuple[str, FailedCheck]] = []
    for probe in probes:
        obs = run_probe(
            probe, tree, python, env, identity, args.log_dir / f"{probe.id}{suffix}.log"
        )
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
