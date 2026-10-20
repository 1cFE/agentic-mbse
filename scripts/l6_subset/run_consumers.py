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
tree (Appendix C steps 1-12) and writes `evidence/<STEM>.{json,md}`. The base side is parsed
from text; the branch side runs with `--json-report` and is read from the report. It exits 1 on
any pass -> fail, any L1-L5 text difference, a wrong resolved root, a branch run with other than
one constraint extraction, or fusion-tea's branch time above 1.10 x base. Expected new String
warnings and UNEXTRACTABLE counts (step 11) are listed apart and never set the exit code.

`l6-evidence --branch HEAD` runs the branch's `validate --level=6 --json-report` on dc3: the
baseline under `generated` and unset, the repaired tree under `generated`. It writes
`evidence/dc3-baseline-l6.md` and `evidence/dc3-repaired-l6.md`, every count read from the report.

`session-equality` runs L1-L6 on each exported tree in this process, standalone and then inside
one `ValidationSession`, and compares every level's full result (Phase 1, I10/B5). It writes
`evidence/session-equality.json` and exits 1 if any level differs.
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
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import tomllib
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "subset_profile"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "positional_binding"))

from isolated_tree import (  # noqa: E402
    IsolationBreachError,
    child_env,
    read_license_key,
    resolve_rev,
    sibling_state,
)
from run_trees import SKIPPED_LINKS, export_tree  # noqa: E402

from agentic_mbse.project_root import find_project_root  # noqa: E402

EVIDENCE = REPO_ROOT / ".project/completed/20261020_l6-subset-profile/evidence"
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
    report: dict[str, Any] | None = None  # the `--json-report` file, for branch runs


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
    tree: str,
    tree_dir: Path,
    tree_commit: str,
    code_label: str,
    code: Path,
    code_commit: str,
    options: tuple[str, ...] = ("--complete",),
    report: Path | None = None,
) -> TreeRun:
    """`agentic_mbse validate <options> models` from `code`'s source, in `tree_dir` (step 6).

    With `report`, the run adds `--json-report <report>` and the parsed file is kept.
    """
    env = child_env(read_license_key())
    env["PYTHONPATH"] = str(code / "src")
    command = [str(PYTHON), "-P", "-c", _CHILD, "validate", *options]
    if report is not None:
        command += ["--json-report", str(report)]
    started = time.perf_counter()
    completed = subprocess.run(
        [*command, "models"], cwd=tree_dir, capture_output=True, text=True, env=env
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
        report=None if report is None else json.loads(report.read_text()),
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
# Every `Execution target` wording that names a file: from, no key in, or an override.
_TARGET_ROOT = re.compile(r"(?P<path>/[^ ;()]+)/pyproject\.toml")
_LEGACY_METRIC = re.compile(r"^\s+(?P<code>(?:L6|V\d)_[A-Z_0-9]+): (?P<count>\d+)$")
_PASSING = ("passed", "crashed, recorded as pass")

# Appendix C step 11: expected, not a stop. `omitted` is the new L6_SUBSET_OMITTED WARNINGs;
# `unextractable` is L6_DESIGN_ATTR_UNEXTRACTABLE before -> after.
EXPECTED: dict[str, dict[str, Any]] = {
    "fusion-tea": {"omitted": 131, "unextractable": (108, 108)},
    "dc3-baseline": {"omitted": 32, "unextractable": (3, 0)},
    "dc3-repaired": {"omitted": 30, "unextractable": (0, 0)},
}
OMITTED = "L6_SUBSET_OMITTED"
UNEXTRACTABLE = "L6_DESIGN_ATTR_UNEXTRACTABLE"


def resolved_root(run: TreeRun) -> str | None:
    """The project root the run's L2 looked at for its pin list (Appendix C step 7)."""
    for line in run.levels[2].block:
        found = _PIN_LIST.search(line)
        if found:
            return found["path"]
    return None


def report_level(report: dict[str, Any], number: int) -> dict[str, Any] | None:
    return next((lv for lv in report["levels"] if lv["level"] == number), None)


def report_root(report: dict[str, Any]) -> str | None:
    """The project root L6's `Execution target` metric names (step 7, branch side)."""
    l6 = report_level(report, 6)
    if l6 is None:
        return None
    found = _TARGET_ROOT.search(str(l6["metrics"].get("Execution target", "")))
    return None if found is None else found["path"]


def report_statuses(report: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Per level: status and issue count from the report (step 8, branch side)."""
    out = {n: {"status": "not run", "issues": None} for n in range(1, 7)}
    for level in report["levels"]:
        out[level["level"]] = {
            "status": level["status"],
            "issues": len(level["issues"]) + len(level["unstructured"]),
        }
    return out


def text_issue_count(level: LevelText) -> int | None:
    for line in level.block:
        if line.strip().startswith("Issues found:"):
            return int(line.strip().removeprefix("Issues found: "))
    return 0 if level.status in ("passed", "failed") else None


def text_code_counts(level: LevelText) -> Counter[str]:
    """The legacy L6 code counts the base prints as metrics (`L6_...: N`)."""
    counts: Counter[str] = Counter()
    for line in level.block:
        found = _LEGACY_METRIC.match(line)
        if found:
            counts[found["code"]] = int(found["count"])
    return counts


def report_code_counts(report: dict[str, Any], number: int) -> Counter[str]:
    """Issue codes the report lists for one level, shown and summarized, per display."""
    level = report_level(report, number)
    counts: Counter[str] = Counter()
    if level is None:
        return counts
    for issue in level["issues"] + level["summarized"]:
        counts[f"{issue['code']} ({issue['display']})"] += 1
    return counts


def compare_runs(base: TreeRun, branch: TreeRun) -> dict[str, Any]:
    """Status per level before -> after, and whether L1-L5's printed blocks are identical (step 9).

    The base status comes from its text; the branch status from its report, which must agree
    with the branch's own text.
    """
    if branch.report is None:
        raise ValueError(f"{branch.tree}: the branch run has no report")
    after_levels = report_statuses(branch.report)
    levels = {}
    flags: list[str] = []
    for n in range(1, 7):
        before, after_text = base.levels[n], branch.levels[n]
        after = after_levels[n]["status"]
        identical = (before.header, before.block) == (after_text.header, after_text.block)
        levels[n] = {
            "before": before.status,
            "after": after,
            "issues": [text_issue_count(before), after_levels[n]["issues"]],
            "identical_text": identical,
        }
        if before.status in _PASSING and after not in ("passed", "not run"):
            flags.append(f"{base.tree} L{n}: {before.status} -> {after}")
        if n <= 5 and not identical:
            flags.append(f"{base.tree} L{n}: printed result differs from base")
        # The branch prints a crashed level as a failed one; the report names it crashed.
        agrees = after == after_text.status or (
            after == "crashed" and after_text.status == "failed"
        )
        if not agrees:
            flags.append(f"{base.tree} L{n}: report says {after}, text says {after_text.status}")
    if base.exit_code == 0 and branch.exit_code != 0:
        flags.append(f"{base.tree}: run passed at base and fails on the branch")
    extractions = branch.report["run_info"]["constraint_extractions"]
    if extractions != 1:
        flags.append(f"{base.tree}: branch ran {extractions} constraint extractions, not 1")
    return {"levels": levels, "flags": flags, "constraint_extractions": extractions}


def time_flag(label: str, base_s: float, branch_s: float) -> str | None:
    """Step 10: only fusion-tea is held to the 1.10 x limit."""
    if label == "fusion-tea" and branch_s > TIME_LIMIT * base_s:
        return f"fusion-tea branch time {branch_s} s is over {TIME_LIMIT} x base {base_s} s"
    return None


def branch_refusal(dirty: str, branch_commit: str, head: str) -> str | None:
    """Step 1: why the branch side cannot be trusted, or None."""
    if dirty.strip():
        return f"refusing a dirty branch:\n{dirty.strip()}"
    if branch_commit != head:
        return f"--branch {branch_commit} is not HEAD ({head})"
    return None


def report_metric_counts(report: dict[str, Any], number: int) -> dict[str, Any]:
    """The legacy L6 code counts the branch prints as metrics; a value may be `not computed`."""
    level = report_level(report, number)
    if level is None:
        return {}
    return {
        key: value
        for key, value in level["metrics"].items()
        if re.fullmatch(r"(?:L6|V\d)_[A-Z_0-9]+", key)
    }


def l6_changes(label: str, base: TreeRun, branch: TreeRun) -> dict[str, Any]:
    """Step 11: the expected new warnings, and every legacy L6 count that changed.

    Legacy counts are compared metric to metric, the same printed count on both sides.
    """
    if branch.report is None:
        raise ValueError(f"{label}: the branch run has no report")
    metric_before = text_code_counts(base.levels[6])
    metric_after = report_metric_counts(branch.report, 6)
    issues_after = report_code_counts(branch.report, 6)
    unextractable_after = sum(
        n for key, n in issues_after.items() if key.startswith(UNEXTRACTABLE + " ")
    )
    expected = EXPECTED[label]
    return {
        "omitted_warnings": issues_after[f"{OMITTED} (warning)"],
        "omitted_expected": expected["omitted"],
        "unextractable": [metric_before.get(UNEXTRACTABLE, 0), unextractable_after],
        "unextractable_metric_after": metric_after.get(UNEXTRACTABLE),
        "unextractable_expected": list(expected["unextractable"]),
        "metric_changes": {
            code: [metric_before.get(code), metric_after.get(code)]
            for code in sorted(set(metric_before) | set(metric_after))
            if metric_before.get(code) != metric_after.get(code)
        },
        "branch_codes": dict(sorted(issues_after.items())),
    }


def _git_dirty(paths: tuple[str, ...]) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", *paths],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def before_after(base: str, branch: str, labels: list[str], out_name: str) -> int:
    """Appendix C steps 1-12."""
    head = resolve_rev(REPO_ROOT, "HEAD")
    refusal = branch_refusal(
        _git_dirty(("src", "pyproject.toml", "uv.lock")), resolve_rev(REPO_ROOT, branch), head
    )
    if refusal:
        raise SystemExit(refusal)
    siblings = {"dc3": DC3, "fusion-tea": FUSION_TEA}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    record: dict[str, Any] = {"command": f"before-after --base {base} --branch {branch}"}
    record["siblings_before"] = before
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
        record["scratch"] = str(parent)
        for label, tree in record["trees"].items():
            tree_dir = parent / "trees" / label
            print(f"running {label} at base {commits['base'][:8]} ...", flush=True)
            base_run = run_validate(
                label, tree_dir, tree["commit"], "base", codes["base"], commits["base"]
            )
            print(f"  exit {base_run.exit_code}, {base_run.wall_time_s} s", flush=True)
            print(f"running {label} at branch {commits['branch'][:8]} ...", flush=True)
            branch_run = run_validate(
                label,
                tree_dir,
                tree["commit"],
                "branch",
                codes["branch"],
                commits["branch"],
                report=parent / f"report-{label}.json",
            )
            print(f"  exit {branch_run.exit_code}, {branch_run.wall_time_s} s", flush=True)
            runs[label] = (base_run, branch_run)
            comparison = compare_runs(base_run, branch_run)
            expected_root = str(tree_dir.parent / tree["settings"]["root"])
            assert branch_run.report is not None
            roots = {
                "base (L2 pin list)": resolved_root(base_run),
                "branch (L2 pin list)": resolved_root(branch_run),
                "branch (L6 execution target)": report_root(branch_run.report),
            }
            comparison["roots"] = {
                k: v and str(Path(v).relative_to(parent)) for k, v in roots.items()
            }
            for where, root in roots.items():
                if root != expected_root:
                    comparison["flags"].append(
                        f"{label} {where}: resolved root {root}, expected {expected_root}"
                    )
            comparison["exit"] = [base_run.exit_code, branch_run.exit_code]
            comparison["wall_time_s"] = [base_run.wall_time_s, branch_run.wall_time_s]
            comparison["ratio"] = round(branch_run.wall_time_s / base_run.wall_time_s, 3)
            slow = time_flag(label, base_run.wall_time_s, branch_run.wall_time_s)
            if slow:
                comparison["flags"].append(slow)
            comparison["l6_changes"] = l6_changes(label, base_run, branch_run)
            comparison["pass_notes"] = branch_run.report["pass_notes"]
            comparisons[label] = comparison
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    record["siblings_unchanged"] = before == after
    record["skipped_links"] = SKIPPED_LINKS
    record["comparisons"] = comparisons
    record["runs"] = {
        label: [
            {k: v for k, v in asdict(run).items() if k not in ("stdout", "stderr", "report")}
            for run in pair
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
        f"Written by `scripts/l6_subset/run_consumers.py {record['command']}`. Base `{commits['base']}`, branch `{commits['branch']}`; SysIDE {record['syside_version']}. Each tree and each code revision is a `git archive` export under one /tmp directory; target unset; runs one at a time. The base side is read from its text output, the branch side from its `--json-report`. Sibling checkouts unchanged: {record['siblings_unchanged']}.",
        "",
        "## Flags (stop-and-show)",
        "",
    ]
    out += [f"- **{flag}**" for flag in record["flags"]] or [
        "None. No level or run goes from pass to fail, L1-L5 print identically, every run resolved the expected project root, each branch run extracted constraints once, and the time criterion holds."
    ]
    out += [
        "",
        "## Per tree",
        "",
        "Each level cell is `status before -> after (issues before -> after)`.",
        "",
        "| Tree | Exit | Wall time (s) | Ratio | L1 | L2 | L3 | L4 | L5 | L6 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label, c in record["comparisons"].items():
        cells = []
        for v in c["levels"].values():
            differs = "" if v["identical_text"] else ", text differs"
            cells.append(
                f"{v['before']} -> {v['after']} ({v['issues'][0]} -> {v['issues'][1]}{differs})"
            )
        out.append(
            f"| {label} | {c['exit'][0]} -> {c['exit'][1]} | {c['wall_time_s'][0]} -> {c['wall_time_s'][1]} | {c['ratio']} | "
            + " | ".join(cells)
            + " |"
        )
    out += [
        "",
        f"Time criterion: fusion-tea branch time at most {TIME_LIMIT} x base. L6's text differs by design (new title, contract lines), so only L1-L5 text is compared.",
        "",
        "## Resolved project root",
        "",
        "| Tree | Settings input (step 5) | Base (L2 pin list) | Branch (L2 pin list) | Branch (L6 execution target) | Constraint extractions (branch) |",
        "|---|---|---|---|---|---|",
    ]
    for label, c in record["comparisons"].items():
        settings = record["trees"][label]["settings"]
        roots = list(c["roots"].values())
        out.append(
            f"| {label} | root `{settings['root']}`, `{settings['pyproject']}`, tables {json.dumps(settings['tables'])} | `{roots[0]}` | `{roots[1]}` | `{roots[2]}` | {c['constraint_extractions']} |"
        )
    out += [
        "",
        "## Expected L6 changes (step 11, not a stop)",
        "",
        "| Tree | New `L6_SUBSET_OMITTED` WARNINGs (expected) | `L6_DESIGN_ATTR_UNEXTRACTABLE` before -> after (expected) | Branch pass notes |",
        "|---|---|---|---|",
    ]
    for label, c in record["comparisons"].items():
        ch = c["l6_changes"]
        out.append(
            f"| {label} | {ch['omitted_warnings']} ({ch['omitted_expected']}) | {ch['unextractable'][0]} -> {ch['unextractable'][1]} ({ch['unextractable_expected'][0]} -> {ch['unextractable_expected'][1]}) | {'; '.join(c['pass_notes']) or 'none'} |"
        )
    out += [
        "",
        "UNEXTRACTABLE after is the report's issue count, shown and summarized, after the String suppression (design D10). The printed metric after is in the next table.",
        "",
        "## Legacy L6 counts that changed",
        "",
        "Both sides are the legacy count metrics L6 prints (`<CODE>: N`), so each pair counts the same thing. `None` means the side prints no such metric.",
        "",
    ]
    for label, c in record["comparisons"].items():
        changed = c["l6_changes"]["metric_changes"]
        if not changed:
            out.append(f"- {label}: none")
            continue
        listed = ", ".join(f"`{code}` {b} -> {a}" for code, (b, a) in changed.items())
        out.append(f"- {label}: {listed}")
    out += ["", "## Branch L6 issue codes by display", ""]
    for label, c in record["comparisons"].items():
        codes = ", ".join(f"`{k}` {n}" for k, n in c["l6_changes"]["branch_codes"].items())
        out.append(f"- {label}: {codes or 'none'}")
    return "\n".join(out) + "\n"


# ---- l6-evidence -------------------------------------------------------------------------------

# dc3's blocker categories (dc3 T-001) and the contract rule/shape/context each is (Item 1
# acceptance.md:21-31).
DC3_CATEGORIES = (
    ("B1", "calc-owned-assertion", "asserted_constraint", "calc_usage_owner"),
    ("B2", "binding-source", "expression_source", "owner_instantiated"),
    ("B3", "part-multiplicity", "unresolved_bound", "expanded_part_usage"),
    ("B4", "invocation-callable", "unsupported_callable", "calc_definition_feature_value"),
    ("B5", "invocation-callable", "unsupported_callable", "binding_value"),
    (
        "B6",
        "conditional-expression",
        "conditional_unresolved_branch",
        "calc_definition_feature_value",
    ),
    ("B7", "string-value-omission", "string_value", "attribute_value"),
    ("B8", "constraint-predicate", "non_numerical_predicate", "owner_other"),
    ("B8", "constraint-predicate", "blocked_predicate", "owner_other"),
)
# Item 1's record (`completed/20261018_exec-subset-profile/evidence/dc3-baseline.md`,
# `dc3-repaired.md`); the spec requires these counts and any difference explained.
DC3_EXPECTED = {
    "dc3-baseline": {
        "verdict": "refused_incomplete",
        "refused": 236,
        "omitted": 32,
        "unconfirmed": 6,
        "unverified": 50,
    },
    "dc3-repaired": {
        "verdict": "clear",
        "refused": 0,
        "omitted": 30,
        "unconfirmed": 0,
        "unverified": 0,
    },
}
L6_RUNS = (
    ("dc3-baseline", "generated", ("--level=6", "--execution-target=generated")),
    ("dc3-baseline", "unset", ("--level=6",)),
    ("dc3-repaired", "generated", ("--level=6", "--execution-target=generated")),
)


def l6_summary(report: dict[str, Any]) -> dict[str, Any]:
    """The L6 facts the evidence files state, all from one report."""
    l6 = report_level(report, 6)
    if l6 is None:
        raise ValueError("the report has no L6")
    profile = l6["profile"]
    findings = profile["findings"]
    by_category = []
    for name, rule, shape, context in DC3_CATEGORIES:
        rows = [
            f
            for f in findings
            if (f["rule_id"], f["shape_id"], f["context_id"]) == (rule, shape, context)
        ]
        by_category.append(
            {
                "category": name,
                "rule": f"{rule} / {shape} / {context}",
                "count": len(rows),
                # None when no finding in the category counts occurrences.
                "occurrences": sum(f["occurrence_count"] for f in rows)
                if any(f["occurrence_count"] is not None for f in rows)
                else None,
                "outcomes": sorted({f["outcome"] for f in rows}),
                "displays": sorted({f["display"] for f in rows}),
                "shadowed_by": sorted(
                    {
                        f"{f['shadowed_by']['rule_id']}/{f['shadowed_by']['shape_id']}"
                        for f in rows
                        if f["shadowed_by"]
                    }
                ),
                "unshadowed": sum(1 for f in rows if not f["shadowed_by"]),
                "example": rows[0] if rows else None,
            }
        )
    listed = {(c[1], c[2], c[3]) for c in DC3_CATEGORIES}
    others = Counter(
        f"{f['rule_id']} / {f['shape_id']} / {f['context_id']} ({f['outcome']})"
        for f in findings
        if (f["rule_id"], f["shape_id"], f["context_id"]) not in listed
    )
    return {
        "status": l6["status"],
        "exit_code": report["exit_code"],
        "pass_notes": report["pass_notes"],
        "metrics": l6["metrics"],
        "verdict": profile["verdict"],
        "counts": profile["counts"],
        "findings": len(findings),
        "by_outcome_listed": dict(Counter(f["outcome"] for f in findings)),
        "unverified": len(profile["unverified"]),
        "unverified_by_rule": dict(Counter(u["rule_id"] for u in profile["unverified"])),
        "advisories": len(profile["advisories"] or []),
        "check_errors": profile["check_errors"],
        "categories": by_category,
        "other_findings": dict(others),
        "codes": dict(sorted(report_code_counts(report, 6).items())),
        "constraint_extractions": report["run_info"]["constraint_extractions"],
        "root": report_root(report),
    }


def l6_evidence(branch: str) -> int:
    """Appendix C's `l6-evidence`: steps 1-5, then the three L6 runs on dc3 (see `L6_RUNS`)."""
    head = resolve_rev(REPO_ROOT, "HEAD")
    refusal = branch_refusal(
        _git_dirty(("src", "pyproject.toml", "uv.lock")), resolve_rev(REPO_ROOT, branch), head
    )
    if refusal:
        raise SystemExit(refusal)
    siblings = {"dc3": DC3, "fusion-tea": FUSION_TEA}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-evidence-") as scratch:
        parent = Path(scratch)
        code = parent / "code-branch"
        commit = export_code(branch, code)
        version = syside_version(child_env(read_license_key()))
        trees = export_trees(parent, ["dc3-baseline", "dc3-repaired"])
        for label, target, options in L6_RUNS:
            tree_dir = parent / "trees" / label
            print(f"running {label} --level=6, target {target} ...", flush=True)
            run = run_validate(
                label,
                tree_dir,
                trees[label]["commit"],
                "branch",
                code,
                commit,
                options=options,
                report=parent / f"report-{label}-{target}.json",
            )
            assert run.report is not None
            summary = l6_summary(run.report)
            summary["wall_time_s"] = run.wall_time_s
            summary["process_exit"] = run.exit_code
            summary["root"] = summary["root"] and str(Path(summary["root"]).relative_to(parent))
            summary["options"] = " ".join(options)
            summaries[label, target] = summary
            print(f"  exit {run.exit_code}, verdict {summary['verdict']}", flush=True)
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    context = {"commit": commit, "syside": version, "trees": trees, "unchanged": before == after}
    (EVIDENCE / "dc3-baseline-l6.md").write_text(
        dc3_markdown(
            "dc3 baseline: L6 under `generated`, and unset",
            "dc3-baseline",
            [summaries["dc3-baseline", "generated"], summaries["dc3-baseline", "unset"]],
            context,
        )
    )
    (EVIDENCE / "dc3-repaired-l6.md").write_text(
        dc3_markdown(
            "dc3 repaired: L6 under `generated`",
            "dc3-repaired",
            [summaries["dc3-repaired", "generated"]],
            context,
        )
    )
    if before != after:
        raise IsolationBreachError("a sibling checkout changed during the run")
    return 0


def _against_expected(label: str, summary: dict[str, Any]) -> str:
    expected = DC3_EXPECTED[label]
    found = {
        "verdict": summary["verdict"],
        **{
            k: summary["counts"]["by_outcome"].get(k, 0)
            for k in ("refused", "omitted", "unconfirmed")
        },
        "unverified": summary["unverified"],
    }
    differs = [f"{k} {found[k]} (expected {v})" for k, v in expected.items() if found[k] != v]
    if differs:
        return "DIFFERS: " + ", ".join(differs)
    return "same (" + ", ".join(f"{k} {v}" for k, v in expected.items()) + ")"


def dc3_markdown(
    title: str, label: str, summaries: list[dict[str, Any]], context: dict[str, Any]
) -> str:
    tree = context["trees"][label]
    out = [
        f"# {title}",
        "",
        f"Written by `scripts/l6_subset/run_consumers.py l6-evidence`. agentic-mbse branch `{context['commit']}`; SysIDE {context['syside']}; dc3 `{tree['commit']}` from a `git archive` export under /tmp. Settings input: root `{tree['settings']['root']}`, `{tree['settings']['pyproject']}`, tables {json.dumps(tree['settings']['tables'])}. Sibling checkouts unchanged: {context['unchanged']}. Every count below is read from the run's `--json-report`.",
    ]
    for s in summaries:
        counts = s["counts"]
        out += [
            "",
            f"## `validate {s['options']} models`",
            "",
            f"- Exit {s['process_exit']} (report {s['exit_code']}); L6 {s['status']}; wall time {s['wall_time_s']} s; constraint extractions {s['constraint_extractions']}; resolved root `{s['root']}`.",
            f"- Pass notes: {'; '.join(s['pass_notes']) or 'none'}.",
            f"- Against Item 1's record: {_against_expected(label, s)}.",
            f"- Verdict `{s['verdict']}`. Findings {s['findings']}, by outcome {json.dumps(counts['by_outcome'])} (declarations {counts['declarations']}, occurrences {counts['occurrences']}); unverified {s['unverified']} {json.dumps(s['unverified_by_rule'])}; unassessed constraints {counts['unassessed_constraints']}; advisories {s['advisories']}; check errors {len(s['check_errors'])}.",
            "",
            "Metrics as printed:",
            "",
            "```text",
            *[f"{k}: {v}" for k, v in s["metrics"].items()],
            "```",
            "",
            "| Category | Rule / shape / context | Declarations (occurrences) | Outcome | Shown as | Shadowed by |",
            "|---|---|---|---|---|---|",
        ]
        for c in s["categories"]:
            if not c["count"]:
                out.append(f"| {c['category']} | `{c['rule']}` | 0 | - | - | - |")
                continue
            shadow = ", ".join(c["shadowed_by"]) or "-"
            declared = str(c["count"])
            if c["occurrences"] is not None:
                declared += f" ({c['occurrences']})"
            if c["shadowed_by"]:
                shadow += f" ({c['count'] - c['unshadowed']} of {c['count']})"
            out.append(
                f"| {c['category']} | `{c['rule']}` | {declared} | {', '.join(c['outcomes'])} | {', '.join(c['displays'])} | {shadow} |"
            )
        if s["other_findings"]:
            out += [
                "",
                "Findings outside B1-B8: "
                + ", ".join(f"`{k}` {n}" for k, n in s["other_findings"].items())
                + ".",
            ]
        out += [
            "",
            "L6 issue codes by display: "
            + (", ".join(f"`{k}` {n}" for k, n in s["codes"].items()) or "none")
            + ".",
        ]
        out += ["", "### One finding per category: location, reason, remedy", ""]
        for c in s["categories"]:
            example = c["example"]
            if example is None:
                continue
            location = example["location"] or {}
            out.append(
                f"- **{c['category']}** `{example['subject']['qualified_name']}` at `{location.get('file')}:{location.get('line')}`: {example['outcome']}, reason `{example['reason']}`. Remedy: {example['remedy']}"
            )
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
    evidence = commands.add_parser("l6-evidence", help="the dc3 L6 evidence files")
    evidence.add_argument("--branch", required=True)
    args = parser.parse_args()
    if args.command == "l6-evidence":
        return l6_evidence(args.branch)
    if args.command == "before-after":
        return before_after(args.base, args.branch, args.trees, args.out)
    if args.command == "baseline":
        return baseline(args.base)
    if args.command == "session-equality":
        return session_equality(args.trees)
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
