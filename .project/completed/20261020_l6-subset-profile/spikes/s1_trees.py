"""Spike S1/S2-on-trees/S3/F5: run Item 1's contract and the two advisory walkers on real trees.

    uv run python .project/active/l6-subset-profile/spikes/s1_trees.py [--out PATH]

Throwaway. For each pinned consumer tree it:

1. exports the whole tree with `git archive` into a TemporaryDirectory under /tmp (sibling repos
   are only read), checking the embedded commit id and skipping absolute symlinks (listed);
2. records `find_project_root(start=<tree>/models)` and the root `pyproject.toml`'s `[tool]`
   tables (F5);
3. loads `models/**/*.sysml`, runs `extract_subset_facts` + `evaluate_subset_profile`, timing each
   and catching any exception with its traceback (S1);
4. runs the two advisory walkers the design names (D12) over the contract's own expression sites
   (S1 crash check + S2 "does any real site fire"):
   - opaque-expression: `reconstruct_expression`, detecting its last-resort `return str(node)` line
     with a line tracer, so the walker's own dispatch decides (no second classifier);
   - wrapper: `decompose_aggregation_expression(...).wrappers` on sites whose tree invokes `sum`;
5. compares the legacy `L6_DESIGN_ATTR_UNEXTRACTABLE` subjects' element ids with the contract's
   `string-value-omission` subject ids (S3).
"""

from __future__ import annotations

import argparse
import inspect
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(REPO_ROOT / ".env")

from agentic_mbse.project_root import find_project_root  # noqa: E402
from agentic_mbse.sysml import expression as expression_module  # noqa: E402
from agentic_mbse.sysml.aggregation import decompose_aggregation_expression  # noqa: E402
from agentic_mbse.sysml.expression import materialize_operands, reconstruct_expression  # noqa: E402
from agentic_mbse.sysml.subset_extraction import _site_candidates, extract_subset_facts  # noqa: E402
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile  # noqa: E402
from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402
from agentic_mbse.validation import level6_architecture as l6  # noqa: E402

TREES = (
    ("fusion-tea", Path.home() / "src" / "fusion-tea", "f96ad312"),
    ("dc3-baseline", Path.home() / "src" / "dc3", "808464d"),
    ("dc3-repaired", Path.home() / "src" / "dc3", "60b44d5"),
)


# ---- export ------------------------------------------------------------------------------------


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def export(repo: Path, rev: str, dest: Path) -> dict[str, Any]:
    full = git(repo, "rev-parse", f"{rev}^{{commit}}")
    archive = subprocess.run(
        ["git", "-C", str(repo), "archive", full], check=True, capture_output=True
    ).stdout
    embedded = subprocess.run(
        ["git", "get-tar-commit-id"], input=archive, check=True, capture_output=True
    ).stdout.decode().strip()
    if embedded != full:
        raise SystemExit(f"{repo}: archive carries {embedded}, expected {full}")
    skipped: list[str] = []

    def keep(member: tarfile.TarInfo, path: str) -> tarfile.TarInfo | None:
        if member.issym() and os.path.isabs(member.linkname):
            if member.name.startswith("models/"):
                raise SystemExit(f"absolute link inside models/: {member.name}")
            skipped.append(f"{member.name} -> {member.linkname}")
            return None
        return tarfile.data_filter(member, path)

    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter=keep)
    return {"commit": full, "skipped_absolute_links": skipped}


# ---- F5: root and settings ---------------------------------------------------------------------


def root_and_settings(tree: Path, parent: Path) -> dict[str, Any]:
    root = find_project_root(start=tree / "models")
    markers = {
        "work/BACKLOG.md": (tree / "work" / "BACKLOG.md").exists(),
        ".agentic-mbse/install.json": (tree / ".agentic-mbse" / "install.json").is_file(),
        ".claude/": (tree / ".claude").is_dir(),
    }
    out: dict[str, Any] = {
        "parent_root": str(find_project_root(start=parent)),
        "root": None if root is None else str(root.relative_to(tree.parent)),
        "root_is_tree": root == tree,
        "markers_at_tree": markers,
    }
    pyproject = (root or tree) / "pyproject.toml"
    if not pyproject.is_file():
        out["pyproject"] = "absent"
        return out
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    out["pyproject"] = str(pyproject.relative_to(tree.parent))
    out["tool_tables"] = sorted(tool)
    out["tool.agentic-mbse"] = tool.get("agentic-mbse", "absent")
    out["tool.agentic_mbse"] = tool.get("agentic_mbse", "absent")
    return out


# ---- S1: contract ------------------------------------------------------------------------------


def capture(fn: Any, *args: Any) -> tuple[Any, dict[str, Any]]:
    print(f"   {getattr(fn, '__name__', fn)} ...", flush=True)
    start = time.perf_counter()
    try:
        value = fn(*args)
    except Exception as error:  # the spike's question: does anything raise?
        print(f"   RAISED {type(error).__name__}: {error}", flush=True)
        return None, {
            "raised": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
            "seconds": round(time.perf_counter() - start, 2),
        }
    seconds = round(time.perf_counter() - start, 2)
    print(f"   done in {seconds}s", flush=True)
    return value, {"raised": None, "seconds": seconds}


def contract_summary(facts: Any, result: Any) -> dict[str, Any]:
    by_rule: Counter[str] = Counter(
        f"{f.rule_id}/{f.shape_id}/{f.context_id.value}/{f.outcome.value}" for f in result.findings
    )
    return {
        "verdict": result.verdict.value,
        "declarations": result.counts.declarations,
        "occurrences": result.counts.occurrences,
        "by_outcome": {o.value: n for o, n in result.counts.by_outcome},
        "unverified": result.counts.unverified,
        "unassessed_constraints": result.counts.unassessed_constraints,
        "roots_available": result.scope.roots_available,
        "roots_used": len(result.scope.roots_used),
        "generator_roots": len(result.scope.generator_root_ids),
        "narrowed": result.scope.narrowed,
        "not_enumerated": [k.value for k in result.scope.not_enumerated],
        "fact_failures": [
            {k: str(v) for k, v in vars(f).items()} if hasattr(f, "__dict__") else repr(f)
            for f in facts.failures
        ],
        "unverified_by_cause": dict(
            Counter(f"{u.rule_id} / {u.cause.value}" for u in result.unverified)
        ),
        "unverified_entries": [
            {
                "rule": u.rule_id,
                "context": None if u.context_id is None else u.context_id.value,
                "cause": u.cause.value,
                "detail": u.detail,
                "subject": None
                if u.subject is None
                else f"{u.subject.file}:{u.subject.line} {u.subject.qualified_name}",
            }
            for u in result.unverified
        ],
        "findings_by_rule_shape_context_outcome": dict(sorted(by_rule.items())),
    }


# ---- S1/S2: advisory walkers -------------------------------------------------------------------

_RECONSTRUCT = reconstruct_expression.__code__
_FALLBACK_LINE = next(
    _RECONSTRUCT.co_firstlineno + i
    for i, line in enumerate(inspect.getsourcelines(reconstruct_expression)[0])
    if line.strip() == "return str(expr_node)"
)


def opaque_nodes(expr: Any) -> list[str]:
    """Node types for which reconstruct_expression reached its `return str(expr_node)` line."""
    hits: list[str] = []

    def tracer(frame: Any, event: str, arg: Any) -> Any:
        if frame.f_code is not _RECONSTRUCT:
            return None
        if event == "line" and frame.f_lineno == _FALLBACK_LINE:
            hits.append(type(frame.f_locals["expr_node"]).__name__)
        return tracer

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        reconstruct_expression(expr)
    finally:
        sys.settrace(previous)
    return hits


def invokes_sum(node: Any, depth: int = 0) -> bool:
    if node is None or depth > 64:
        return False
    function = getattr(node, "function", None)
    if function is not None and str(getattr(function, "name", "")) == "sum":
        return True
    try:
        operands = materialize_operands(node)
    except Exception:
        return False
    return any(invokes_sum(op, depth + 1) for op in operands)


def advisories(model: Any) -> dict[str, Any]:
    candidates = _site_candidates(model)
    opaque: list[dict[str, Any]] = []
    wrappers: list[dict[str, Any]] = []
    failures: Counter[str] = Counter()
    failure_examples: dict[str, str] = {}
    sum_sites = 0
    for candidate in candidates:
        where = SysideAdapter.get_source_location(candidate.expression)
        name = str(getattr(candidate.declaration, "qualified_name", None))
        try:
            hits = opaque_nodes(candidate.expression)
            if hits:
                opaque.append({"site": name, "where": str(where), "nodes": hits})
        except Exception as error:
            key = f"opaque: {type(error).__name__}"
            failures[key] += 1
            failure_examples.setdefault(key, f"{name}: {error}")
        try:
            if invokes_sum(candidate.expression):
                sum_sites += 1
                decomposition = decompose_aggregation_expression(candidate.expression)
                if decomposition.wrappers:
                    wrappers.append(
                        {
                            "site": name,
                            "where": str(where),
                            "wrappers": [
                                (w.function_name, w.reason, w.depth)
                                for w in decomposition.wrappers
                            ],
                        }
                    )
        except Exception as error:
            key = f"wrapper: {type(error).__name__}"
            failures[key] += 1
            failure_examples.setdefault(key, f"{name}: {error}")
    return {
        "sites": len(candidates),
        "sum_sites": sum_sites,
        "opaque_firings": opaque,
        "wrapper_firings": wrappers,
        "walker_failures": dict(failures),
        "walker_failure_examples": failure_examples,
    }


# ---- S3: String id match -----------------------------------------------------------------------


def string_id_match(model: Any, result: Any) -> dict[str, Any]:
    """Run the legacy check with its evaluator wrapped to record which attrs it flagged."""
    by_expression = {
        SysideAdapter.element_id(attr.feature_value_expression): attr
        for attr in SysideAdapter.elements_of_type(model, "AttributeUsage")
        if getattr(attr, "feature_value_expression", None) is not None
    }
    flagged: list[Any] = []
    original = l6.evaluate_true_static_expression

    def recording(expr: Any) -> Any:
        try:
            return original(expr)
        except (ValueError, TypeError):
            # Look up the attr owning this exact expression element by its element id.
            attr = by_expression.get(SysideAdapter.element_id(expr))
            flagged.append(attr)
            raise

    l6.evaluate_true_static_expression = recording
    try:
        issues, checked = l6.check_design_attr_completeness(model, "designs")
    finally:
        l6.evaluate_true_static_expression = original
    unextractable = [i for i in issues if i.code.name == "L6_DESIGN_ATTR_UNEXTRACTABLE"]
    legacy_ids = {str(SysideAdapter.element_id(a)): str(a.qualified_name) for a in flagged if a}
    string_ids = {
        str(f.subject.element_id): f.subject.qualified_name
        for f in result.findings
        if f.rule_id == "string-value-omission"
    }
    return {
        "attrs_checked": checked,
        "legacy_unextractable_issues": len(unextractable),
        "legacy_flagged_with_id": len(legacy_ids),
        "unmapped_flags": sum(1 for a in flagged if a is None),
        "string_findings": len(string_ids),
        "legacy_ids_in_string_ids": len(set(legacy_ids) & set(string_ids)),
        "legacy_not_string": {k: v for k, v in legacy_ids.items() if k not in string_ids},
        "string_not_legacy": {k: v for k, v in string_ids.items() if k not in legacy_ids},
        "legacy_issue_names": sorted(i.element_name or "" for i in unextractable),
        "legacy_ids_names": sorted(legacy_ids.values()),
    }


# ---- driver ------------------------------------------------------------------------------------


def run_tree(label: str, repo: Path, rev: str, work: Path) -> dict[str, Any]:
    tree = work / label
    out: dict[str, Any] = {"label": label, "repo": repo.name, "rev": rev}
    out["export"] = export(repo, rev, tree)
    out["settings"] = root_and_settings(tree, work)
    files = sorted((tree / "models").rglob("*.sysml"))
    out["files"] = len(files)
    loaded, out["load"] = capture(SysideAdapter.load_model, files)
    if loaded is None:
        return out
    model, diagnostics = loaded
    out["load"]["error_diagnostics"] = len(list(diagnostics.errors))
    facts, out["extract"] = capture(extract_subset_facts, model)
    if facts is not None:
        result, out["evaluate"] = capture(evaluate_subset_profile, facts)
        if result is not None:
            out["contract"] = contract_summary(facts, result)
            out["string_id_match"], out["string_id_run"] = capture(string_id_match, model, result)
    out["advisories"], out["advisory_run"] = capture(advisories, model)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", help="tree label(s) to run")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("s1-results.json"))
    args = parser.parse_args()
    import syside

    results: dict[str, Any] = {
        "agentic_mbse_head": git(REPO_ROOT, "rev-parse", "HEAD"),
        "src_dirty": git(REPO_ROOT, "status", "--porcelain", "--", "src"),
        "syside": str(syside.__version__),
        "fallback_line": f"expression.py:{_FALLBACK_LINE}",
        "expression_module": expression_module.__file__,
        "trees": [],
    }
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-spike-") as tmp:
        work = Path(tmp)
        for label, repo, rev in TREES:
            if args.only and label not in args.only:
                continue
            before = (git(repo, "rev-parse", "HEAD"), git(repo, "status", "--porcelain"))
            print(f"== {label}", flush=True)
            results["trees"].append(run_tree(label, repo, rev, work))
            after = (git(repo, "rev-parse", "HEAD"), git(repo, "status", "--porcelain"))
            results["trees"][-1]["sibling_unchanged"] = before == after
    args.out.write_text(json.dumps(results, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
