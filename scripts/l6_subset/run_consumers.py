"""Run full validation on the pinned consumer trees from `git archive` exports (Item 3 Appendix C).

    uv run python scripts/l6_subset/run_consumers.py baseline --base ebb3d467
    uv run python scripts/l6_subset/run_consumers.py session-equality [--trees fusion-tea ...]

Every consumer tree and every code revision is read from a `git archive` export in one
`TemporaryDirectory` under /tmp; no sibling checkout is written, and each sibling's HEAD and
status are compared before and after (Appendix C step 12). Each run is the venv's Python with
`PYTHONPATH=<code export>/src`, `cwd=<tree>`, `agentic_mbse validate --complete models`, target
unset. The child prints `agentic_mbse.__file__` first, and the run fails unless it lies inside
that run's code export (step 6).

`baseline` runs one code revision on all three trees, one at a time, and writes
`evidence/baseline-consumers.{json,md}`: per tree and level, the status parsed from the text
(`crashed, recorded as pass` for `❌ Error running Level N`), the level's printed block, the exit
code and the wall time.

`before-after --base B --branch HEAD [--trees ...] [--out STEM]` runs both revisions on each
tree (Appendix C steps 1-10 and 12), parsing both sides from text for now, and writes
`evidence/<STEM>.{json,md}`; it exits 1 on any pass -> fail, any L1-L5 text difference, a wrong
resolved root, or fusion-tea's branch time above 1.10 x base.

`session-equality` runs L1-L6 on each exported tree in this process, standalone and then inside
one `ValidationSession`, and compares every level's full result (Phase 1, I10/B5). It writes
`evidence/session-equality.json` and exits 1 if any level differs. Phase 11 completes `before-after`
(all trees, the report-based branch side, step 11) and adds `l6-evidence`.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import tomllib
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "subset_profile"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "positional_binding"))

from probe import (  # noqa: E402
    IsolationBreachError,
    child_env,
    read_license_key,
    resolve_rev,
    sibling_state,
)
from run_trees import SKIPPED_LINKS, export_tree  # noqa: E402

from agentic_mbse.project_root import find_project_root  # noqa: E402

EVIDENCE = REPO_ROOT / ".project/active/l6-subset-profile/evidence"
PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
FUSION_TEA = Path("/home/reid/src/fusion-tea")
DC3 = Path("/home/reid/src/dc3")
TREES = (
    ("fusion-tea", FUSION_TEA, "f96ad312"),
    ("dc3-baseline", DC3, "808464d"),
    ("dc3-repaired", DC3, "60b44d5"),
)

# Prints the module path first (step 6), then runs the CLI exactly as `-m agentic_mbse` would.
# `-P` keeps the tree's own directory off sys.path.
_CHILD = """
import runpy, sys
import agentic_mbse
print("AGENTIC_MBSE_FILE=" + agentic_mbse.__file__, flush=True)
sys.argv = ["agentic_mbse", *sys.argv[1:]]
runpy.run_module("agentic_mbse", run_name="__main__", alter_sys=True)
"""
_MODULE_FILE = re.compile(r"^AGENTIC_MBSE_FILE=(?P<path>.+)$", re.MULTILINE)
_LEVEL_STATUS = re.compile(r"^(?P<mark>✅|❌) Level (?P<level>[1-6]): ")
_LEVEL_CRASH = re.compile(r"^❌ Error running Level (?P<level>[1-6]): (?P<message>.*)$")


@dataclass
class LevelText:
    """One level as the text output shows it."""

    status: str  # passed | failed | crashed, recorded as pass | not run
    header: str = ""
    block: list[str] = field(default_factory=list)  # metrics, the first issues, counts


@dataclass
class TreeRun:
    tree: str
    tree_commit: str
    code_label: str
    code_commit: str
    module_file: str
    exit_code: int
    wall_time_s: float
    levels: dict[int, LevelText]
    stdout: str
    stderr: str


def parse_levels(stdout: str) -> dict[int, LevelText]:
    """Per-level status and printed block from the runner's text (Appendix C step 8, base side)."""
    levels = {level: LevelText("not run") for level in range(1, 7)}
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        crash = _LEVEL_CRASH.match(line)
        if crash:
            levels[int(crash["level"])] = LevelText(
                "crashed, recorded as pass", header=line, block=[crash["message"]]
            )
            continue
        status = _LEVEL_STATUS.match(line)
        if status is None:
            continue
        block: list[str] = []
        for following in lines[index + 1 :]:
            if following and not following.startswith("   "):
                break
            block.append(following)
        while block and not block[-1]:
            block.pop()
        levels[int(status["level"])] = LevelText(
            "passed" if status["mark"] == "✅" else "failed", header=line, block=block
        )
    return levels


def export_code(rev: str, dest: Path) -> str:
    """Export this repository at `rev` into `dest`; returns the full commit id."""
    commit = resolve_rev(REPO_ROOT, rev)
    export_tree(REPO_ROOT, commit, dest)
    return commit


def tree_settings(tree: Path) -> dict[str, Any]:
    """The project root L6 will resolve from `<tree>/models`, and its settings table (step 5)."""
    root = find_project_root(start=tree / "models")
    if root is None:
        raise IsolationBreachError(f"{tree}/models resolves no project root")
    pyproject = root / "pyproject.toml"
    tables: dict[str, Any] = {}
    if pyproject.is_file():
        tool = tomllib.loads(pyproject.read_text()).get("tool", {})
        for name in ("agentic-mbse", "agentic_mbse"):
            tables[name] = tool.get(name, "absent")
    return {
        "root": str(root.relative_to(tree.parent)),
        "pyproject": str(pyproject.relative_to(tree.parent)) if pyproject.is_file() else "absent",
        "tables": tables,
    }


def syside_version(env: dict[str, str]) -> str:
    return subprocess.run(
        [str(PYTHON), "-P", "-c", "import syside; print(syside.__version__)"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


def run_validate(
    tree: str, tree_dir: Path, tree_commit: str, code_label: str, code: Path, code_commit: str
) -> TreeRun:
    """`agentic_mbse validate --complete models` from `code`'s source, in `tree_dir` (step 6)."""
    env = child_env(read_license_key())
    env["PYTHONPATH"] = str(code / "src")
    started = time.perf_counter()
    completed = subprocess.run(
        [str(PYTHON), "-P", "-c", _CHILD, "validate", "--complete", "models"],
        cwd=tree_dir,
        capture_output=True,
        text=True,
        env=env,
    )
    wall = time.perf_counter() - started
    module = _MODULE_FILE.search(completed.stdout)
    if module is None:
        raise IsolationBreachError(f"{tree} ({code_label}) printed no module path")
    module_file = Path(module["path"])
    if not module_file.is_relative_to(code / "src"):
        raise IsolationBreachError(f"{tree} ({code_label}) imported {module_file}, not {code}")
    return TreeRun(
        tree=tree,
        tree_commit=tree_commit,
        code_label=code_label,
        code_commit=code_commit,
        module_file=str(module_file.relative_to(code.parent)),
        exit_code=completed.returncode,
        wall_time_s=round(wall, 1),
        levels=parse_levels(completed.stdout),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def export_trees(parent: Path, labels: list[str]) -> dict[str, dict[str, Any]]:
    """Export each named tree to `<parent>/trees/<label>`; its commit and settings input (3-5)."""
    if find_project_root(start=parent) is not None:
        raise IsolationBreachError(f"{parent} is inside a project root")
    trees: dict[str, dict[str, Any]] = {}
    for label, repo, rev in TREES:
        if label not in labels:
            continue
        commit = resolve_rev(repo, rev)
        tree_dir = parent / "trees" / label
        export_tree(repo, commit, tree_dir)
        trees[label] = {"commit": commit, "settings": tree_settings(tree_dir)}
    return trees


def baseline(base: str) -> int:
    siblings = {"dc3": DC3, "fusion-tea": FUSION_TEA}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    record: dict[str, Any] = {"command": f"baseline --base {base}", "trees": {}}
    runs: list[TreeRun] = []
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-consumers-") as scratch:
        parent = Path(scratch)
        code = parent / "code-base"
        code_commit = export_code(base, code)
        record["agentic_mbse"] = {"base": code_commit}
        record["syside_version"] = syside_version(child_env(read_license_key()))
        record["trees"] = export_trees(parent, [label for label, _, _ in TREES])
        for label, _repo, _rev in TREES:
            tree_dir = parent / "trees" / label
            commit = record["trees"][label]["commit"]
            print(f"running {label} at base {code_commit[:8]} ...", flush=True)
            run = run_validate(label, tree_dir, commit, "base", code, code_commit)
            print(f"  exit {run.exit_code}, {run.wall_time_s} s", flush=True)
            runs.append(run)
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    record["siblings_unchanged"] = before == after
    record["skipped_links"] = SKIPPED_LINKS
    record["runs"] = [
        {k: v for k, v in asdict(run).items() if k not in ("stdout", "stderr")} for run in runs
    ]
    record["stderr_tail"] = {run.tree: run.stderr.splitlines()[-5:] for run in runs}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "baseline-consumers.json").write_text(json.dumps(record, indent=2) + "\n")
    (EVIDENCE / "baseline-consumers.md").write_text(baseline_markdown(record, runs))
    if before != after:
        raise IsolationBreachError("a sibling checkout changed during the run")
    return 0


def _issue_count(level: LevelText) -> str:
    for line in level.block:
        if line.strip().startswith("Issues found:"):
            return line.strip().removeprefix("Issues found: ")
    return "0" if level.status in ("passed", "failed") else "-"


def baseline_markdown(record: dict[str, Any], runs: list[TreeRun]) -> str:
    out = [
        "# Consumer baseline: `validate --complete models` at the base revision",
        "",
        f"Written by `scripts/l6_subset/run_consumers.py {record['command']}`. agentic-mbse base `{record['agentic_mbse']['base']}`; SysIDE {record['syside_version']}. Each tree is a `git archive` export under /tmp; target unset. Sibling checkouts unchanged: {record['siblings_unchanged']}.",
        "",
        "| Tree | Commit | Exit | Wall time (s) | L1 | L2 | L3 | L4 | L5 | L6 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for run in runs:
        cells = [
            f"{run.levels[n].status} ({_issue_count(run.levels[n])} issues)" for n in range(1, 7)
        ]
        out.append(
            f"| {run.tree} | `{run.tree_commit[:8]}` | {run.exit_code} | {run.wall_time_s} | "
            + " | ".join(cells)
            + " |"
        )
    out += ["", "## Settings input per tree", ""]
    for label, tree in record["trees"].items():
        settings = tree["settings"]
        out.append(
            f"- {label}: root `{settings['root']}`, `{settings['pyproject']}`, tables {json.dumps(settings['tables'])}"
        )
    for run in runs:
        out += ["", f"## {run.tree} level blocks", ""]
        for n in range(1, 7):
            level = run.levels[n]
            out.append(f"### Level {n}: {level.status}")
            out.append("")
            out.append("```text")
            out.append(level.header)
            out.extend(level.block)
            out.append("```")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


TIME_LIMIT = 1.10  # fusion-tea branch wall time / base wall time (Appendix C step 10)
_PIN_LIST = re.compile(r"Positional pin list: .*\(looked at (?P<path>.+)/positional-pins\.toml\)")


def resolved_root(run: TreeRun) -> str | None:
    """The project root the run's L2 looked at for its pin list (Appendix C step 7)."""
    for line in run.levels[2].block:
        found = _PIN_LIST.search(line)
        if found:
            return found["path"]
    return None


def compare_runs(base: TreeRun, branch: TreeRun) -> dict[str, Any]:
    """Status per level before -> after, and whether L1-L5's printed blocks are identical (step 9)."""
    levels = {}
    flags: list[str] = []
    for n in range(1, 7):
        before, after = base.levels[n], branch.levels[n]
        identical = (before.header, before.block) == (after.header, after.block)
        levels[n] = {"before": before.status, "after": after.status, "identical_text": identical}
        if before.status != "failed" and after.status == "failed":
            flags.append(f"{base.tree} L{n}: {before.status} -> failed")
        if n <= 5 and not identical:
            flags.append(f"{base.tree} L{n}: printed result differs from base")
    if base.exit_code == 0 and branch.exit_code != 0:
        flags.append(f"{base.tree}: run passed at base and fails on the branch")
    return {"levels": levels, "flags": flags}


def before_after(base: str, branch: str, labels: list[str], out_name: str) -> int:
    """Appendix C steps 1-10 and 12; Phase 11 adds the report-based branch side and step 11."""
    dirty = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "status",
            "--porcelain",
            "--",
            "src",
            "pyproject.toml",
            "uv.lock",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"refusing a dirty branch:\n{dirty}")
    head = resolve_rev(REPO_ROOT, "HEAD")
    if resolve_rev(REPO_ROOT, branch) != head:
        raise SystemExit(f"--branch {branch} is not HEAD ({head})")
    siblings = {"dc3": DC3, "fusion-tea": FUSION_TEA}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    record: dict[str, Any] = {"command": f"before-after --base {base} --branch {branch}"}
    comparisons: dict[str, dict[str, Any]] = {}
    runs: dict[str, tuple[TreeRun, TreeRun]] = {}
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-before-after-") as scratch:
        parent = Path(scratch)
        codes = {"base": parent / "code-base", "branch": parent / "code-branch"}
        commits = {
            "base": export_code(base, codes["base"]),
            "branch": export_code(branch, codes["branch"]),
        }
        record["agentic_mbse"] = commits
        record["syside_version"] = syside_version(child_env(read_license_key()))
        record["trees"] = export_trees(parent, labels)
        for label, tree in record["trees"].items():
            tree_dir = parent / "trees" / label
            pair = []
            for side in ("base", "branch"):
                print(f"running {label} at {side} {commits[side][:8]} ...", flush=True)
                run = run_validate(
                    label, tree_dir, tree["commit"], side, codes[side], commits[side]
                )
                print(f"  exit {run.exit_code}, {run.wall_time_s} s", flush=True)
                pair.append(run)
            base_run, branch_run = pair
            runs[label] = (base_run, branch_run)
            comparison = compare_runs(base_run, branch_run)
            expected_root = str(parent / tree["settings"]["root"])
            for run in pair:
                if resolved_root(run) != expected_root:
                    comparison["flags"].append(
                        f"{label} ({run.code_label}): resolved root {resolved_root(run)}, expected {expected_root}"
                    )
            comparison["exit"] = [base_run.exit_code, branch_run.exit_code]
            comparison["wall_time_s"] = [base_run.wall_time_s, branch_run.wall_time_s]
            comparison["ratio"] = round(branch_run.wall_time_s / base_run.wall_time_s, 3)
            if label == "fusion-tea" and comparison["ratio"] > TIME_LIMIT:
                comparison["flags"].append(
                    f"fusion-tea branch time {branch_run.wall_time_s} s is over {TIME_LIMIT} x base {base_run.wall_time_s} s"
                )
            comparisons[label] = comparison
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    record["siblings_unchanged"] = before == after
    record["skipped_links"] = SKIPPED_LINKS
    record["comparisons"] = comparisons
    record["runs"] = {
        label: [
            {k: v for k, v in asdict(run).items() if k not in ("stdout", "stderr")} for run in pair
        ]
        for label, pair in runs.items()
    }
    flags = [flag for c in comparisons.values() for flag in c["flags"]]
    if before != after:
        flags.append("a sibling checkout changed during the run")
    record["flags"] = flags
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / f"{out_name}.json").write_text(json.dumps(record, indent=2) + "\n")
    (EVIDENCE / f"{out_name}.md").write_text(before_after_markdown(record))
    return 1 if flags else 0


def before_after_markdown(record: dict[str, Any]) -> str:
    commits = record["agentic_mbse"]
    out = [
        "# Before/after: `validate --complete models`, base vs branch",
        "",
        f"Written by `scripts/l6_subset/run_consumers.py {record['command']}`. Base `{commits['base']}`, branch `{commits['branch']}`; SysIDE {record['syside_version']}. Each tree and each code revision is a `git archive` export under /tmp; target unset; runs one at a time. Sibling checkouts unchanged: {record['siblings_unchanged']}.",
        "",
        "## Flags",
        "",
    ]
    out += [f"- **{flag}**" for flag in record["flags"]] or [
        "None. No level or run goes from pass to fail, L1-L5 print identically, and the time criterion holds."
    ]
    out += [
        "",
        "## Per tree",
        "",
        "| Tree | Exit base -> branch | Wall time base -> branch (s) | Ratio | L1 | L2 | L3 | L4 | L5 | L6 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label, c in record["comparisons"].items():
        cells = [
            f"{v['before']} -> {v['after']}{'' if v['identical_text'] else ' (text differs)'}"
            for v in c["levels"].values()
        ]
        out.append(
            f"| {label} | {c['exit'][0]} -> {c['exit'][1]} | {c['wall_time_s'][0]} -> {c['wall_time_s'][1]} | {c['ratio']} | "
            + " | ".join(cells)
            + " |"
        )
    out += ["", f"Time criterion: fusion-tea branch time at most {TIME_LIMIT} x base."]
    return "\n".join(out) + "\n"


def _level_view(check: Any, models: str) -> Any:
    """Everything a level returns, or its raise; compared exactly with and without the session."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            result = check(models)
    except Exception as error:  # a raise is a result too
        return {"raised": f"{type(error).__name__}: {error}"}
    return {
        "success": result.success,
        "issues": result.issues,
        "warnings": result.warnings,
        "metrics": {key: str(value) for key, value in result.metrics.items()},
        "structured_issues": [i.model_dump(mode="json") for i in result.structured_issues],
    }


def _working_tree_identity() -> dict[str, str]:
    """HEAD plus a hash of the uncommitted source, since this check runs the working tree."""
    diff = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "HEAD", "--", "src"],
        check=True,
        capture_output=True,
    ).stdout
    untracked = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard", "src"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    digest = hashlib.sha256(diff)
    for name in sorted(untracked):
        digest.update(name.encode() + (REPO_ROOT / name).read_bytes())
    return {
        "head": resolve_rev(REPO_ROOT, "HEAD"),
        "uncommitted_src_sha256": digest.hexdigest(),
        "untracked_src": ", ".join(sorted(untracked)),
    }


def session_equality(labels: list[str]) -> int:
    """L1-L6 on each tree, standalone and then inside one `ValidationSession`, compared exactly.

    Runs this checkout's code in process (the session is not committed yet), with `cwd=<tree>`
    as the CLI would. The standalone pass is what the base runner does, so its time is the
    base-equivalent time and the session pass's time is the branch-equivalent time.
    """
    from agentic_mbse.validation.runner import QUALITY_CHECKS
    from agentic_mbse.validation.session import ValidationSession

    siblings = {"dc3": DC3, "fusion-tea": FUSION_TEA}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    record: dict[str, Any] = {"code": _working_tree_identity(), "trees": {}}
    home = Path.cwd()
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-session-eq-") as scratch:
        parent = Path(scratch)
        if find_project_root(start=parent) is not None:
            raise IsolationBreachError(f"{parent} is inside a project root")
        for label, repo, rev in TREES:
            if label not in labels:
                continue
            commit = resolve_rev(repo, rev)
            tree_dir = parent / label
            export_tree(repo, commit, tree_dir)
            os.chdir(tree_dir)
            try:
                print(f"{label}: standalone levels ...", flush=True)
                started = time.perf_counter()
                without = [_level_view(check, "models") for _name, check in QUALITY_CHECKS]
                without_s = time.perf_counter() - started
                print(f"{label}: inside one session ...", flush=True)
                started = time.perf_counter()
                with ValidationSession() as session:
                    with_session = [_level_view(check, "models") for _name, check in QUALITY_CHECKS]
                with_s = time.perf_counter() - started
            finally:
                os.chdir(home)
            levels = {}
            for number, (a, b) in enumerate(zip(without, with_session, strict=True), start=1):
                levels[number] = {
                    "identical": a == b,
                    "success": a.get("success"),
                    "issues": len(a.get("issues", [])),
                    "raised": a.get("raised"),
                }
                if a != b:
                    levels[number]["without"] = a
                    levels[number]["with_session"] = b
            record["trees"][label] = {
                "commit": commit,
                "standalone_s": round(without_s, 1),
                "session_s": round(with_s, 1),
                "model_loads": session.model_loads,
                "constraint_extractions": session.constraint_extractions,
                "levels": levels,
            }
            print(
                f"{label}: identical {[n for n, v in levels.items() if v['identical']]}, "
                f"{round(without_s, 1)} s -> {round(with_s, 1)} s",
                flush=True,
            )
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    record["siblings_unchanged"] = before == after
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "session-equality.json").write_text(json.dumps(record, indent=2) + "\n")
    if before != after:
        raise IsolationBreachError("a sibling checkout changed during the run")
    differing = [
        f"{label} L{n}"
        for label, tree in record["trees"].items()
        for n, level in tree["levels"].items()
        if not level["identical"]
    ]
    return 1 if differing else 0


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    base = commands.add_parser("baseline", help="run one code revision on all three trees")
    base.add_argument("--base", required=True)
    equality = commands.add_parser(
        "session-equality", help="L1-L6 with and without the session, in process"
    )
    equality.add_argument("--trees", nargs="+", default=[label for label, _, _ in TREES])
    compare = commands.add_parser("before-after", help="base and branch on the named trees")
    compare.add_argument("--base", required=True)
    compare.add_argument("--branch", required=True)
    compare.add_argument("--trees", nargs="+", default=[label for label, _, _ in TREES])
    compare.add_argument("--out", default="before-after", help="evidence file stem")
    args = parser.parse_args()
    if args.command == "before-after":
        return before_after(args.base, args.branch, args.trees, args.out)
    if args.command == "baseline":
        return baseline(args.base)
    if args.command == "session-equality":
        return session_equality(args.trees)
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
