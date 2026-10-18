"""Run sysml-codegen's own pytest suite against an agentic-mbse revision, in an isolated tree.

    uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev REV --label NAME
    uv run python scripts/subset_profile/codegen_suite.py diff NAME_A NAME_B

The same-generator check (design § Probe harness step 6, plan P-9). `run` builds a fresh tree with
the `probe.py` pattern (codegen at the pin, agentic-mbse at REV, `uv sync --frozen`, plus
codegen's `dev` extra from the same lock), runs
codegen's suite with its own configuration from inside the tree, and writes every test's outcome
to `evidence/codegen-suite/<NAME>.json` with the run identity. `diff` compares two such runs
test by test; it exits non-zero on any difference, so identical results are the only pass.

The sibling checkouts are only read with `git archive`; the run fails if codegen's HEAD or status
changes.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from probe import (  # noqa: E402  (this directory is on sys.path when the script runs)
    IsolationBreachError,
    build_tree,
    child_env,
    read_identity,
    read_license_key,
    resolve_rev,
    sibling_state,
)

from tests.helpers.subset_probe_judge import PINNED_CODEGEN_REV  # noqa: E402

OUT_DIR = REPO_ROOT / ".project" / "active" / "exec-subset-profile" / "evidence" / "codegen-suite"
SUITE_TIMEOUT_S = 3600
#: One `-rA` short-summary line: outcome, then the node id, then an optional reason.
_SUMMARY = re.compile(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (\S+)")


def outcomes(report: str) -> dict[str, str]:
    """Node id → outcome, read from pytest's `-rA` short test summary."""
    found: dict[str, str] = {}
    in_summary = False
    for line in report.splitlines():
        if "short test summary info" in line:
            in_summary = True
            continue
        if not in_summary:
            continue
        match = _SUMMARY.match(line)
        if match:
            outcome, node = match.groups()
            if outcome == "SKIPPED":  # `SKIPPED [n] path:line: reason` carries no node id
                continue
            found[node] = outcome
    return found


def run(args: argparse.Namespace) -> int:
    codegen_repo = args.codegen_repo.resolve()
    agentic = resolve_rev(REPO_ROOT, args.agentic_rev)
    codegen = resolve_rev(codegen_repo, PINNED_CODEGEN_REV)
    args.tmp_root.mkdir(parents=True, exist_ok=True)
    tree = Path(tempfile.mkdtemp(prefix="suite-", dir=args.tmp_root)).resolve()
    for checkout in (codegen_repo, REPO_ROOT):
        if tree.is_relative_to(checkout):
            raise IsolationBreachError(f"temp tree {tree} is inside the checkout {checkout}")
    before = sibling_state(codegen_repo)
    env = child_env(read_license_key())
    python = build_tree(tree, codegen_repo, codegen, agentic, env)
    # The suite needs codegen's `dev` extra (pytest, jsonschema), still pinned by its uv.lock.
    dev = subprocess.run(
        ["uv", "sync", "--frozen", "--extra", "dev"],
        cwd=tree / "sysml-codegen",
        env=env,
        capture_output=True,
        text=True,
    )
    if dev.returncode != 0:
        raise SystemExit(f"uv sync --frozen --extra dev failed in {tree}:\n{dev.stderr}")
    identity = {k: v for k, v in vars(read_identity(tree, python, env, codegen, agentic)).items()}
    argv = [str(python), "-I", "-m", "pytest", "-rA", "-p", "no:cacheprovider", "--color=no"]
    done = subprocess.run(
        argv,
        cwd=tree / "sysml-codegen",
        env=env,
        capture_output=True,
        text=True,
        timeout=SUITE_TIMEOUT_S,
    )
    if sibling_state(codegen_repo) != before:
        raise IsolationBreachError(f"{codegen_repo} changed during the run")
    report = done.stdout + done.stderr
    tail = [line for line in report.splitlines() if line.strip()][-1]
    result = {
        "label": args.label,
        "identity": {k: v for k, v in identity.items() if k != "tree_root"},
        "argv": argv[1:],
        "exit_code": done.returncode,
        "final_line": tail,
        "outcomes": dict(sorted(outcomes(report).items())),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{args.label}.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT_DIR / f"{args.label}.log").write_text(report)
    counts: dict[str, int] = {}
    for outcome in result["outcomes"].values():
        counts[outcome] = counts.get(outcome, 0) + 1
    print(f"{args.label}: agentic {agentic[:12]} exit={done.returncode} {counts} | {tail}")
    shutil.rmtree(tree)
    return 0


def diff(args: argparse.Namespace) -> int:
    a = json.loads((OUT_DIR / f"{args.a}.json").read_text())
    b = json.loads((OUT_DIR / f"{args.b}.json").read_text())
    lines = [
        f"{args.a}: agentic {a['identity']['agentic_rev']} exit={a['exit_code']} | {a['final_line']}",
        f"{args.b}: agentic {b['identity']['agentic_rev']} exit={b['exit_code']} | {b['final_line']}",
    ]
    for key in ("codegen_rev", "syside_version", "uv_lock_sha256", "python_version"):
        if a["identity"][key] != b["identity"][key]:
            lines.append(f"identity differs on {key}: {a['identity'][key]} vs {b['identity'][key]}")
    nodes = sorted(set(a["outcomes"]) | set(b["outcomes"]))
    changed = [
        f"  {n}: {a['outcomes'].get(n, 'absent')} -> {b['outcomes'].get(n, 'absent')}"
        for n in nodes
        if a["outcomes"].get(n) != b["outcomes"].get(n)
    ]
    same = not changed and a["exit_code"] == b["exit_code"] and len(lines) == 2
    lines.append(
        f"{len(nodes)} tests compared, {len(changed)} differ: {'IDENTICAL' if same else 'DIFFERENT'}"
    )
    lines += changed
    print("\n".join(lines))
    return 0 if same else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--agentic-rev", required=True)
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument(
        "--codegen-repo", type=Path, default=Path.home() / "src" / "sysml-codegen"
    )
    run_parser.add_argument("--tmp-root", type=Path, default=Path("/tmp/subset-profile"))
    diff_parser = sub.add_parser("diff")
    diff_parser.add_argument("a")
    diff_parser.add_argument("b")
    args = parser.parse_args()
    return run(args) if args.command == "run" else diff(args)


if __name__ == "__main__":
    sys.exit(main())
