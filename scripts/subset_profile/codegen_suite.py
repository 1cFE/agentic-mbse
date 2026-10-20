"""Run sysml-codegen's own pytest suite against an agentic-mbse revision, in an isolated tree.

    uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev REV --codegen-rev REV \
        --label NAME --out DIR [--select PATH ...]
    uv run python scripts/subset_profile/codegen_suite.py diff RUN_A.json RUN_B.json

The pre-merge generator check (EXEC-SUBSET-CONTRACT Item 2a design D13). `run` builds a fresh tree
with `isolated_tree.py` (codegen at `--codegen-rev`, agentic-mbse at `--agentic-rev`,
`uv sync --frozen`, plus codegen's `dev` extra from the same lock), runs the selected codegen tests
(default `tests/conformance/subset_profile`) with codegen's own configuration from inside the tree,
and writes every test's outcome to `<DIR>/<NAME>.json` with the run identity, and the pytest
report to `<DIR>/<NAME>.log`. `diff` compares two such runs test by test; it exits non-zero on
any difference, so identical results are the only pass.

A run passes only when every selected test passed. A failure, an error or a skip fails it: the
only skip in codegen's subset tests is `requires_license`, and a run with license-gated skips
does not count. A passing run of the default selection writes the gate receipt
(`gate_receipt.py`) to this checkout's `tests/fixtures/subset_profile/codegen_gate.json`: the
digest of the covered files in the exported agentic-mbse tree, both revisions, and the packaged
case IDs that a passed codegen test was parametrized with. The run refuses to write it if any
packaged case has no passed test. A failing run leaves the receipt alone.

The sibling checkouts are only read with `git archive`; the run fails if codegen's HEAD or status
changes.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

# Both modules sit beside this script, whose directory is on sys.path when it runs.
import gate_receipt
from isolated_tree import (
    CODEGEN_SIBLING,
    REPO_ROOT,
    IsolationBreachError,
    build_tree,
    child_env,
    read_identity,
    read_license_key,
    resolve_rev,
    sibling_state,
)

DEFAULT_SELECT = ("tests/conformance/subset_profile",)
SUITE_TIMEOUT_S = 3600


def outcomes(junit: Path) -> dict[str, str]:
    """Test id → outcome (`passed`, `failed`, `error`, `skipped`), read from pytest's JUnit XML.

    A repeated id is an error: it would let one outcome hide another in the comparison.
    """
    found: dict[str, str] = {}
    for case in ElementTree.parse(junit).getroot().iter("testcase"):
        test_id = f"{case.get('classname')}::{case.get('name')}"
        tags = {child.tag for child in case}
        outcome = next(
            (tag for tag in ("error", "failure", "skipped") if tag in tags), "passed"
        ).replace("failure", "failed")
        if test_id in found:
            raise SystemExit(f"JUnit report repeats test id {test_id}")
        found[test_id] = outcome
    return found


def passed_case_ids(outcome_by_id: dict[str, str], packaged: set[str]) -> set[str]:
    """The packaged case IDs that some passed test was parametrized with, as its whole id."""
    params = {
        test_id[test_id.index("[") + 1 : -1]
        for test_id, outcome in outcome_by_id.items()
        if outcome == "passed" and test_id.endswith("]")
    }
    return packaged & params


def receipt(tree: Path, codegen: str, agentic: str, outcome_by_id: dict[str, str]) -> dict:
    """The gate receipt for a passing run (design D13). Raises SystemExit if a case went untested."""
    exported = tree / "agentic-mbse"
    packaged = gate_receipt.packaged_case_ids(exported)
    tested = passed_case_ids(outcome_by_id, packaged)
    if packaged - tested:
        raise SystemExit(f"no passed codegen test for packaged cases {sorted(packaged - tested)}")
    return {
        "digest": gate_receipt.digest(exported),
        "codegen_rev": codegen,
        "agentic_rev": agentic,
        "case_ids": sorted(tested),
    }


def run(args: argparse.Namespace) -> int:
    codegen_repo = args.codegen_repo.resolve()
    agentic = resolve_rev(REPO_ROOT, args.agentic_rev)
    codegen = resolve_rev(codegen_repo, args.codegen_rev)
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
    identity = read_identity(tree, python, env, codegen, agentic)
    junit = tree / "junit.xml"
    argv = [
        str(python),
        "-I",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "--color=no",
        f"--junitxml={junit}",
        *(args.select or DEFAULT_SELECT),
    ]
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
        "argv": [arg for arg in argv[1:] if arg != f"--junitxml={junit}"],
        "exit_code": done.returncode,
        "final_line": tail,
        "outcomes": dict(sorted(outcomes(junit).items())),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{args.label}.json").write_text(json.dumps(result, indent=1) + "\n")
    (args.out / f"{args.label}.log").write_text(report)
    counts: dict[str, int] = {}
    for outcome in result["outcomes"].values():
        counts[outcome] = counts.get(outcome, 0) + 1
    print(f"{args.label}: agentic {agentic[:12]} exit={done.returncode} {counts} | {tail}")
    passed = done.returncode == 0 and set(counts) == {"passed"}
    if passed and not args.select:
        written = receipt(tree, codegen, agentic, result["outcomes"])
        (REPO_ROOT / gate_receipt.RECEIPT).write_text(json.dumps(written, indent=1) + "\n")
        print(f"wrote {gate_receipt.RECEIPT}: {len(written['case_ids'])} cases")
    elif passed:
        print("not the default selection: no receipt written")
    else:
        print("the run did not pass: no receipt written")
    shutil.rmtree(tree)
    return 0 if passed else 1


def diff(args: argparse.Namespace) -> int:
    a = json.loads(args.a.read_text())
    b = json.loads(args.b.read_text())
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
    run_parser.add_argument("--codegen-rev", required=True)
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument(
        "--out", type=Path, required=True, help="directory for the run's report"
    )
    run_parser.add_argument(
        "--select",
        action="append",
        metavar="PATH",
        help=f"codegen test path to run, repeatable (default {DEFAULT_SELECT[0]})",
    )
    run_parser.add_argument("--codegen-repo", type=Path, default=CODEGEN_SIBLING)
    run_parser.add_argument("--tmp-root", type=Path, default=Path("/tmp/subset-profile"))
    diff_parser = sub.add_parser("diff")
    diff_parser.add_argument("a", type=Path, help="a run's <NAME>.json")
    diff_parser.add_argument("b", type=Path, help="another run's <NAME>.json")
    args = parser.parse_args()
    return run(args) if args.command == "run" else diff(args)


if __name__ == "__main__":
    sys.exit(main())
