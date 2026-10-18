"""Reproduce the positional-binding prototype's tree results with the production L2 check.

    uv run python scripts/positional_binding/run_trees.py --final-rev REV

Plan Phase 6, design Appendix B. Every tree is read from a `git archive` export into a temp
directory; no sibling checkout is written, and each sibling's HEAD and status are compared
before and after (I7). The check runs from this checkout, which must be at `--final-rev` with
`src/` clean; that is the identity the evidence records.

fusion-tea `f96ad312` (`models/`):

- Run 0: L2 from `ccd57d83`'s archived `src/`, in a subprocess of this interpreter, asserting
  `agentic_mbse.__file__` resolves inside the archive (D17). This is L2 without the check.
- Run 1: the new L2 with no pin options; the pin list is looked for at the project root.
- Run 2: `--positional-pins <baseline> --positional-pins-root <export>`.
- Run 3: a second export with the baseline copied to `<root>/positional-pins.toml` and no
  options; its result must equal Run 2's.
- Mutation: a fresh export where two adjacent in-order inputs are swapped (site chosen from
  source text, recorded before the check runs); Run 2's options. Expect new ERRORs.
- Stale: a fresh export where the first pinned input is rewritten to `in :>> <name> = ...`;
  Run 2's options. Expect exactly that pin stale and no new ERROR.

dc3 `808464d` and `60b44d5` (`models/`): the new L2 with no pin options. Expect no positional
finding and no unverifiable result.

Writes `.project/active/positional-binding-check/evidence/run-trees.{md,json}` and
`run-trees-sites.md` (the mutation and stale sites). Exits 1 if any expectation fails, after
writing the evidence; an identity difference on fusion-tea or a dc3 result is a premise
surprise (plan "Premise-surprise rule"), never a reason to change the check.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "subset_profile"))

from probe import IsolationBreachError, git, resolve_rev, sibling_state  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = REPO_ROOT / ".project/active/positional-binding-check/evidence"
BASELINE = REPO_ROOT / "tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml"
BASE_REV = "ccd57d83"
FUSION_TEA = Path("/home/reid/src/fusion-tea")
DC3 = Path("/home/reid/src/dc3")
SYSML_CODEGEN = Path("/home/reid/src/sysml-codegen")
FUSION_TEA_REV = "f96ad312"
DC3_REVS = {"808464d": 302, "60b44d5": 391}  # prototype implicit_matching per tree
PROTOTYPE_OUTCOMES = {"implicit_matching": 5573, "implicit_mismatch": 125, "new_parameter": 1956}

POSITIONAL_CODES = {
    "L2_POSITIONAL_BINDING",
    "L2_POSITIONAL_PIN_STALE",
    "L2_POSITIONAL_PIN_LIST_INVALID",
}
_FIELDS = re.compile(
    r'\[owner = "(?P<owner>[^"]*)", input = "(?P<input>[^"]*)", '
    r'target = "(?P<target>[^"]*)", file = "(?P<file>[^"]*)", line = (?P<line>\d+)\]$'
)
_USAGE = re.compile(r"^\s*(calc|constraint)\s+(\w+)\s*:\s*([^{;]+?)\s*\{\s*$")
_IN_BOUND = re.compile(r"^\s*in\s+([A-Za-z_]\w*)\s*=[^;]*;\s*$")
# A definition's input line: `in <name>`, or `in attribute <name>` as fusion-tea writes them.
_IN_NAME = re.compile(r"^\s*in\s+(?:attribute\s+)?([A-Za-z_]\w*)\b")

Identity = tuple[str, str, str]

SKIPPED_LINKS: dict[str, list[str]] = {}


def export_tree(repo: Path, commit: str, dest: Path) -> None:
    """Extract `git archive <commit>` whole into `dest`, after checking its embedded commit id.

    Like `scripts/subset_profile/probe.py:export_tree`, except for which absolute symlinks it
    skips: any outside `models/` (fusion-tea's `.project/` holds links into `/tmp`), each named
    in the evidence. The check loads only `models/`, where an absolute link aborts the export.
    """
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
    skipped = SKIPPED_LINKS.setdefault(f"{repo.name}@{commit[:8]}", [])

    def outside_links_skipped(member: tarfile.TarInfo, path: str) -> tarfile.TarInfo | None:
        if member.issym() and os.path.isabs(member.linkname):
            if member.name.startswith("models/"):
                raise IsolationBreachError(
                    f"{member.name} links outside the tree to {member.linkname}"
                )
            if f"{member.name} -> {member.linkname}" not in skipped:
                skipped.append(f"{member.name} -> {member.linkname}")
            return None
        return tarfile.data_filter(member, path)

    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter=outside_links_skipped)


@dataclass
class L2Run:
    success: bool
    issues: list[dict[str, Any]]
    metrics: dict[str, Any]
    notes: list[str] = field(default_factory=list)

    def by_code(self) -> dict[str, int]:
        return dict(sorted(Counter(f"{i['code']} {i['severity']}" for i in self.issues).items()))

    def positional(self) -> list[dict[str, Any]]:
        return [i for i in self.issues if is_positional(i)]

    def non_positional(self) -> list[dict[str, Any]]:
        return [i for i in self.issues if not is_positional(i)]

    def finding_identities(self, severity: str | None = None) -> set[Identity]:
        found: set[Identity] = set()
        for issue in self.issues:
            if issue["code"] != "L2_POSITIONAL_BINDING":
                continue
            if severity is not None and issue["severity"] != severity:
                continue
            fields = _FIELDS.search(issue["message"])
            if fields is not None:
                found.add((fields["owner"], fields["input"], fields["target"]))
        return found

    def unpinnable(self) -> int:
        return sum(
            1
            for i in self.issues
            if i["code"] == "L2_POSITIONAL_BINDING" and _FIELDS.search(i["message"]) is None
        )

    def count(self, code: str, severity: str | None = None) -> int:
        return sum(
            1
            for i in self.issues
            if i["code"] == code and (severity is None or i["severity"] == severity)
        )

    def unverifiable(self) -> int:
        return sum(
            1
            for i in self.issues
            if i["code"] == "L2_CHECK_UNVERIFIABLE"
            and (i.get("reason_code") or "").startswith("POSITIONAL_")
        )

    def outcomes(self) -> dict[str, int]:
        text = self.metrics["Positional input outcomes"]
        return {name: int(n) for name, n in (part.split(" ") for part in text.split(", "))}

    def summary(self) -> dict[str, Any]:
        return {"success": self.success, "issues_by_code": self.by_code()}


def is_positional(issue: dict[str, Any]) -> bool:
    if issue["code"] in POSITIONAL_CODES:
        return True
    return issue["code"] == "L2_CHECK_UNVERIFIABLE" and (issue.get("reason_code") or "").startswith(
        "POSITIONAL_"
    )


def run_l2(models: Path, **options: Path) -> L2Run:
    """The production L2, in process, with its console output captured."""
    from agentic_mbse.validation.level2_structure import validate_structure

    with contextlib.redirect_stdout(io.StringIO()):
        result = validate_structure(str(models), **options)
    return L2Run(
        result.success,
        [i.model_dump(mode="json") for i in result.structured_issues],
        dict(result.metrics),
    )


_BASE_L2 = """
import contextlib, io, json, sys
from pathlib import Path
base_src = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(base_src))
import agentic_mbse
resolved = Path(agentic_mbse.__file__).resolve()
if not resolved.is_relative_to(base_src):
    raise SystemExit(f"agentic_mbse resolved to {resolved}, outside the archived {base_src}")
from agentic_mbse.validation.level2_structure import validate_structure
with contextlib.redirect_stdout(io.StringIO()):
    result = validate_structure(sys.argv[2])
print(json.dumps({
    "file": str(resolved),
    "success": result.success,
    "issues": [i.model_dump(mode="json") for i in result.structured_issues],
    "metrics": result.metrics,
}))
"""


def run_base_l2(base_src: Path, models: Path) -> tuple[L2Run, str]:
    """L2 as `ccd57d83` shipped it, from its archived source (D17). Returns the run and module path."""
    env = {**os.environ, "PYTHONPATH": str(base_src)}
    completed = subprocess.run(
        [sys.executable, "-c", _BASE_L2, str(base_src), str(models)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    data = json.loads(completed.stdout.strip().splitlines()[-1])
    return L2Run(data["success"], data["issues"], data["metrics"]), data["file"]


def reference_identities() -> set[Identity]:
    from agentic_mbse.validation.positional_pins import PinList, load

    pins = load(BASELINE, pin_root=BASELINE.parent)
    if not isinstance(pins, PinList):
        raise SystemExit(f"the committed baseline does not load: {pins}")
    return {(p.identity.owner, p.identity.input, p.identity.target) for p in pins.pins}


def compare_identities(found: set[Identity], reference: set[Identity]) -> dict[str, list[Any]]:
    """Itemized difference: added, missing, and changed target for one (owner, input)."""
    found_by_input: dict[tuple[str, str], set[str]] = {}
    ref_by_input: dict[tuple[str, str], set[str]] = {}
    for owner, name, target in found:
        found_by_input.setdefault((owner, name), set()).add(target)
    for owner, name, target in reference:
        ref_by_input.setdefault((owner, name), set()).add(target)
    changed = [
        {"owner": k[0], "input": k[1], "reference": sorted(ref_by_input[k]), "found": sorted(v)}
        for k, v in sorted(found_by_input.items())
        if k in ref_by_input and v != ref_by_input[k]
    ]
    changed_keys = {(c["owner"], c["input"]) for c in changed}
    return {
        "added": sorted(i for i in found - reference if i[:2] not in changed_keys),
        "missing": sorted(i for i in reference - found if i[:2] not in changed_keys),
        "changed_target": changed,
    }


# ---- source-text site selection (design Appendix B) -----------------------------------------


def sysml_files(models: Path) -> list[Path]:
    return sorted(models.rglob("*.sysml"))


def definition_text(models: Path, definition: str) -> str | None:
    """The text of the single `calc def` / `constraint def` named by the usage's type, or None."""
    name = definition.split("::")[-1].strip()
    pattern = re.compile(rf"^\s*(calc|constraint)\s+def\s+{re.escape(name)}(\s|:|\{{|$)", re.M)
    hits: list[str] = []
    for path in sysml_files(models):
        text = path.read_text()
        for match in pattern.finditer(text):
            hits.append(_braced_block(text, match.start()))
    return hits[0] if len(hits) == 1 else None


def _braced_block(text: str, start: int) -> str:
    opening = text.index("{", start)
    depth = 0
    for index in range(opening, len(text)):
        depth += {"{": 1, "}": -1}.get(text[index], 0)
        if depth == 0:
            return text[start : index + 1]
    return text[start:]


def consecutive_in_pairs(text: str) -> set[tuple[str, str]]:
    names = [_IN_NAME.match(line) for line in text.splitlines()]
    return {
        (a[1], b[1])
        for a, b in zip(names, names[1:], strict=False)
        if a is not None and b is not None
    }


@dataclass(frozen=True)
class Site:
    file: Path
    usage_line: int  # 1-based
    first: int  # 1-based line of the first of the two inputs
    names: tuple[str, str]
    definition: str


def mutation_site(models: Path) -> Site | None:
    for path in sysml_files(models):
        lines = path.read_text().splitlines()
        for index, line in enumerate(lines[:-2]):
            usage = _USAGE.match(line)
            if usage is None:
                continue
            first, second = _IN_BOUND.match(lines[index + 1]), _IN_BOUND.match(lines[index + 2])
            if first is None or second is None:
                continue
            definition = definition_text(models, usage[3])
            if definition is None:
                continue
            if (first[1], second[1]) in consecutive_in_pairs(definition):
                return Site(path, index + 1, index + 2, (first[1], second[1]), usage[3])
    return None


def swap_lines(path: Path, first: int) -> None:
    lines = path.read_text().splitlines(keepends=True)
    lines[first - 1], lines[first] = lines[first], lines[first - 1]
    path.write_text("".join(lines))


@dataclass(frozen=True)
class StaleSite:
    identity: Identity
    file: Path
    line: int
    before: str
    after: str


def stale_site(root: Path) -> StaleSite | None:
    from agentic_mbse.validation.positional_pins import PinList, load

    pins = load(BASELINE, pin_root=root)
    assert isinstance(pins, PinList)
    for pin in pins.pins:  # sorted by identity, the reference file's order
        path = root / pin.file
        lines = path.read_text().splitlines()
        text = lines[pin.line - 1]
        match = re.match(rf"^(\s*)in\s+{re.escape(pin.identity.input)}\s*=\s*([^;]*);(.*)$", text)
        if match is None or match[2].strip() == pin.identity.input:
            continue
        after = f"{match[1]}in :>> {pin.identity.input} = {match[2].strip()};{match[3]}"
        identity = (pin.identity.owner, pin.identity.input, pin.identity.target)
        return StaleSite(identity, path, pin.line, text, after)
    return None


def rewrite_line(path: Path, line: int, text: str) -> None:
    lines = path.read_text().splitlines(keepends=True)
    ending = "\n" if lines[line - 1].endswith("\n") else ""
    lines[line - 1] = text + ending
    path.write_text("".join(lines))


# ---- the runs ---------------------------------------------------------------------------------


class Checks:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []

    def expect(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, ok, detail))
        print(f"{'PASS' if ok else 'FAIL'}  {name}{': ' + detail if detail else ''}")

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.results)


def fusion_tea(
    scratch: Path, rev: str, checks: Checks, record: dict[str, Any], sites: list[str]
) -> None:
    export = scratch / "fusion-tea"
    export_tree(FUSION_TEA, rev, export)
    models = export / "models"
    reference = reference_identities()

    base_src = scratch / "agentic-mbse-base"
    export_tree(REPO_ROOT, resolve_rev(REPO_ROOT, BASE_REV), base_src)
    run0, base_file = run_base_l2(base_src / "src", models)
    checks.expect(
        "Run 0 imports agentic_mbse from the archived base",
        Path(base_file).is_relative_to((base_src / "src").resolve()),
        base_file,
    )

    from agentic_mbse.project_root import find_project_root

    run1 = run_l2(models)
    root = find_project_root(start=models)
    run1.notes.append(f"find_project_root from the export's models/: {root}")
    checks.expect(
        "Run 1 finds no pin list",
        str(run1.metrics["Positional pin list"]).startswith("none"),
        str(run1.metrics["Positional pin list"]),
    )
    checks.expect(
        "Run 1's non-positional issues equal Run 0's issues",
        run1.non_positional() == run0.issues,
        f"{len(run1.non_positional())} vs {len(run0.issues)}",
    )

    run2 = run_l2(models, positional_pins=BASELINE, pin_root=export)
    found = run2.finding_identities()
    difference = compare_identities(found, reference)
    checks.expect(
        "Run 2 identities equal the prototype's 125",
        not any(difference.values()),
        f"added {len(difference['added'])}, missing {len(difference['missing'])}, "
        f"changed target {len(difference['changed_target'])}",
    )
    checks.expect("Run 2: 125 WARNINGs", run2.count("L2_POSITIONAL_BINDING", "warning") == 125)
    checks.expect("Run 2: 0 positional ERRORs", run2.count("L2_POSITIONAL_BINDING", "error") == 0)
    checks.expect("Run 2: 0 unverifiable", run2.unverifiable() == 0)
    checks.expect("Run 2: 0 stale", run2.count("L2_POSITIONAL_PIN_STALE") == 0)
    inspected = int(run2.metrics["Positional inputs inspected"])
    checks.expect("Run 2 inspects inputs (Insp-3)", inspected > 0, str(inspected))
    outcomes = run2.outcomes()
    outcome_diff = {
        k: {"prototype": v, "production": outcomes.get(k, 0)}
        for k, v in PROTOTYPE_OUTCOMES.items()
        if outcomes.get(k, 0) != v
    }

    discovery = scratch / "fusion-tea-discovery"
    export_tree(FUSION_TEA, rev, discovery)
    markers = [
        m
        for m in ("work/BACKLOG.md", ".agentic-mbse/install.json", ".claude")
        if (discovery / m).exists()
    ]
    created_marker = False
    if not markers:
        (discovery / "work").mkdir(exist_ok=True)
        (discovery / "work" / "BACKLOG.md").write_text("")
        created_marker = True
    shutil.copy(BASELINE, discovery / "positional-pins.toml")
    run3 = run_l2(discovery / "models")
    run3.notes.append(f"project-root markers in the export: {markers or 'none'}")
    run3.notes.append(f"created work/BACKLOG.md: {created_marker}")
    checks.expect(
        "Run 3 discovers the root pin list",
        str(run3.metrics["Positional pin list"]).startswith(
            str(discovery / "positional-pins.toml")
        ),
        str(run3.metrics["Positional pin list"]),
    )
    # Other L2 messages carry the export's absolute path, so compare with each root replaced.
    same_metrics = {k: v for k, v in run3.metrics.items() if k != "Positional pin list"} == {
        k: v for k, v in run2.metrics.items() if k != "Positional pin list"
    }
    same_issues = _rooted(run3.issues, discovery) == _rooted(run2.issues, export)
    checks.expect(
        "Run 3 equals Run 2",
        same_issues and run3.success == run2.success and same_metrics,
    )

    mutation = scratch / "fusion-tea-mutation"
    export_tree(FUSION_TEA, rev, mutation)
    site = mutation_site(mutation / "models")
    mutation_record: dict[str, Any] = {"site": None}
    if site is None:
        checks.expect("mutation site found", False, "no site matches the source-text rule")
    else:
        relative = site.file.relative_to(mutation)
        sites.append(
            f"- **Mutation site** (chosen before the check runs): `{relative}` usage line "
            f"{site.usage_line} (type `{site.definition}`), inputs `{site.names[0]}` (line "
            f"{site.first}) and `{site.names[1]}` (line {site.first + 1}), in the order the "
            f"definition declares them. Swapped."
        )
        write_sites(sites)
        pins_before = BASELINE.read_bytes()
        before = run_l2(mutation / "models", positional_pins=BASELINE, pin_root=mutation)
        swap_lines(site.file, site.first)
        after = run_l2(mutation / "models", positional_pins=BASELINE, pin_root=mutation)
        new_errors = after.finding_identities("error") - before.finding_identities("error")
        checks.expect(
            "mutation: one or more new ERROR identities",
            len(new_errors) >= 1,
            str(sorted(new_errors)),
        )
        checks.expect("mutation: L2 fails", not after.success)
        checks.expect("mutation: pin list unchanged", BASELINE.read_bytes() == pins_before)
        mutation_record = {
            "site": {
                "file": str(relative),
                "usage_line": site.usage_line,
                "first_input_line": site.first,
                "names": list(site.names),
                "definition": site.definition,
            },
            "new_error_identities": [list(i) for i in sorted(new_errors)],
            "before": before.summary(),
            "after": after.summary(),
        }

    stale = scratch / "fusion-tea-stale"
    export_tree(FUSION_TEA, rev, stale)
    target = stale_site(stale)
    stale_record: dict[str, Any] = {"site": None}
    if target is None:
        checks.expect(
            "stale site found",
            False,
            "no pinned input has a right-hand side other than its own name",
        )
    else:
        relative = target.file.relative_to(stale)
        sites.append(
            f"- **Stale site** (chosen before the check runs): pin `{' | '.join(target.identity)}`, "
            f"`{relative}:{target.line}`, rewritten from `{target.before.strip()}` to "
            f"`{target.after.strip()}`."
        )
        write_sites(sites)
        rewrite_line(target.file, target.line, target.after)
        after = run_l2(stale / "models", positional_pins=BASELINE, pin_root=stale)
        stale_issues = [i for i in after.issues if i["code"] == "L2_POSITIONAL_PIN_STALE"]
        stale_ids = [i["message"] for i in stale_issues]
        checks.expect(
            "stale: exactly that pin is stale",
            len(stale_issues) == 1 and " | ".join(target.identity) in stale_ids[0],
            "; ".join(stale_ids),
        )
        checks.expect(
            "stale: every other pin matched", after.count("L2_POSITIONAL_BINDING", "warning") == 124
        )
        new_errors_by_code = Counter(
            i["code"] for i in after.issues if i["severity"] == "error"
        ) - Counter(i["code"] for i in run2.issues if i["severity"] == "error")
        new_errors_by_code.pop("L2_POSITIONAL_PIN_STALE", None)
        checks.expect(
            "stale: no new ERROR of any other L2 code",
            not new_errors_by_code,
            str(dict(new_errors_by_code)),
        )
        checks.expect("stale: L2 fails", not after.success)
        stale_record = {
            "site": {
                "identity": list(target.identity),
                "file": str(relative),
                "line": target.line,
                "before": target.before,
                "after": target.after,
            },
            "stale_messages": stale_ids,
            "after": after.summary(),
        }

    record["fusion_tea"] = {
        "revision": resolve_rev(FUSION_TEA, rev),
        "run0_without_check": {**run0.summary(), "agentic_mbse_file": base_file},
        "run1_check_no_pins": {
            **run1.summary(),
            "notes": run1.notes,
            "pin_list": run1.metrics["Positional pin list"],
            "metrics": _positional_metrics(run1),
        },
        "run2_check_with_pins": {**run2.summary(), "metrics": _positional_metrics(run2)},
        "run3_discovery": {
            **run3.summary(),
            "notes": run3.notes,
            "pin_list": run3.metrics["Positional pin list"],
        },
        "identity_difference": difference,
        "found_identities": len(found),
        "reference_identities": len(reference),
        "unpinnable_findings": run2.unpinnable(),
        "outcomes": outcomes,
        "outcome_difference_from_prototype": outcome_diff,
        "mutation": mutation_record,
        "stale": stale_record,
    }


def dc3(scratch: Path, checks: Checks, record: dict[str, Any]) -> None:
    record["dc3"] = {}
    for rev, prototype_matching in DC3_REVS.items():
        full = resolve_rev(DC3, rev)
        export = scratch / f"dc3-{rev}"
        export_tree(DC3, full, export)
        run = run_l2(export / "models")
        findings = run.count("L2_POSITIONAL_BINDING")
        unverifiable = run.unverifiable()
        checks.expect(f"dc3 {rev}: 0 findings", findings == 0, str(findings))
        checks.expect(f"dc3 {rev}: 0 unverifiable", unverifiable == 0, str(unverifiable))
        inspected = int(run.metrics["Positional inputs inspected"])
        checks.expect(f"dc3 {rev}: inspects inputs (Insp-3)", inspected > 0, str(inspected))
        outcomes = run.outcomes()
        record["dc3"][rev] = {
            "revision": full,
            **run.summary(),
            "metrics": _positional_metrics(run),
            "outcomes": outcomes,
            "prototype_implicit_matching": prototype_matching,
            "positional_issues": run.positional(),
        }


def _rooted(issues: list[dict[str, Any]], root: Path) -> str:
    """The issue list as JSON with the export's absolute path replaced by `<root>`."""
    return json.dumps(issues, sort_keys=True).replace(str(root), "<root>")


def _positional_metrics(run: L2Run) -> dict[str, Any]:
    return {k: v for k, v in run.metrics.items() if k.startswith("Positional")}


def write_sites(sites: list[str]) -> None:
    (EVIDENCE / "run-trees-sites.md").write_text(
        "# Mutation and stale sites (written before each check runs)\n\n"
        "Selected by `scripts/positional_binding/run_trees.py` from source text alone, by the "
        "rules in design Appendix B.\n\n" + "\n".join(sites) + "\n"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--final-rev", required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    load_dotenv(REPO_ROOT / ".env")
    head = resolve_rev(REPO_ROOT, "HEAD")
    if resolve_rev(REPO_ROOT, args.final_rev) != head:
        raise SystemExit(f"--final-rev {args.final_rev} is not this checkout's HEAD {head}")
    if git(REPO_ROOT, "status", "--porcelain", "--", "src"):
        raise SystemExit("src/ has uncommitted changes; the evidence must name the code that ran")
    from importlib.metadata import version

    siblings = {"fusion-tea": FUSION_TEA, "dc3": DC3, "sysml-codegen": SYSML_CODEGEN}
    before = {name: sibling_state(repo) for name, repo in siblings.items()}
    checks = Checks()
    record: dict[str, Any] = {
        "agentic_mbse": {"revision": head, "base_revision": resolve_rev(REPO_ROOT, BASE_REV)},
        "syside": version("syside"),
        "baseline": str(BASELINE.relative_to(REPO_ROOT)),
    }
    sites: list[str] = []
    with tempfile.TemporaryDirectory(prefix="positional-trees-") as tmp:
        scratch = Path(tmp)
        fusion_tea(scratch, resolve_rev(FUSION_TEA, FUSION_TEA_REV), checks, record, sites)
        dc3(scratch, checks, record)
    after = {name: sibling_state(repo) for name, repo in siblings.items()}
    for name in siblings:
        checks.expect(f"{name} HEAD and status unchanged (I7)", before[name] == after[name])
    record["siblings"] = {name: before[name].splitlines()[0] for name in siblings}
    record["skipped_absolute_links"] = SKIPPED_LINKS
    record["checks"] = [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks.results]
    (EVIDENCE / "run-trees.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    (EVIDENCE / "run-trees.md").write_text(render_markdown(record))
    print(f"wrote {(EVIDENCE / 'run-trees.md').relative_to(REPO_ROOT)}")
    return 0 if checks.ok else 1


def render_markdown(record: dict[str, Any]) -> str:
    ft = record["fusion_tea"]
    lines = [
        "# Positional-binding reproduction on the consumer trees (plan Phase 6)",
        "",
        "Generated by `scripts/positional_binding/run_trees.py`; the full record is `run-trees.json`.",
        "",
        f"- agentic-mbse: `{record['agentic_mbse']['revision']}` (Run 0 base `{record['agentic_mbse']['base_revision']}`)",
        f"- fusion-tea: `{ft['revision']}`",
        *(f"- dc3: `{d['revision']}`" for d in record["dc3"].values()),
        f"- SysIDE: {record['syside']}",
        f"- Pin list: `{record['baseline']}`",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
        *(
            f"| {c['name']} | {'pass' if c['ok'] else '**FAIL**'} | {c['detail']} |"
            for c in record["checks"]
        ),
        "",
        "## fusion-tea L2 results (R4-3 evidence)",
        "",
        "| Run | L2 passes | Issues by code and severity |",
        "|---|---|---|",
    ]
    for label, key in (
        ("Run 0: L2 without the check (`ccd57d83`)", "run0_without_check"),
        ("Run 1: with the check, no pins", "run1_check_no_pins"),
        ("Run 2: with the check and the pin list", "run2_check_with_pins"),
        ("Run 3: pin list discovered at the root", "run3_discovery"),
    ):
        run = ft[key]
        codes = "; ".join(f"{k}: {v}" for k, v in run["issues_by_code"].items()) or "none"
        lines.append(f"| {label} | {'yes' if run['success'] else 'no'} | {codes} |")
    diff = ft["identity_difference"]
    lines += [
        "",
        "## fusion-tea identities versus the prototype",
        "",
        f"- Production identities (Run 2): {ft['found_identities']}; reference: {ft['reference_identities']}; unpinnable findings: {ft['unpinnable_findings']}.",
        f"- Added: {len(diff['added'])}. Missing: {len(diff['missing'])}. Changed target: {len(diff['changed_target'])}.",
        *(f"  - added `{' | '.join(i)}`" for i in diff["added"]),
        *(f"  - missing `{' | '.join(i)}`" for i in diff["missing"]),
        *(
            f"  - changed `{c['owner']} | {c['input']}`: {c['reference']} -> {c['found']}"
            for c in diff["changed_target"]
        ),
        f"- Outcome counts (Run 2): {ft['outcomes']}.",
        f"- Differences from the prototype's counts: {ft['outcome_difference_from_prototype'] or 'none'}.",
        "",
        "## Mutation and stale",
        "",
        f"- Mutation: {json.dumps(ft['mutation'], sort_keys=True)}",
        f"- Stale: {json.dumps(ft['stale'], sort_keys=True)}",
        "",
        "## dc3",
        "",
        "| Revision | L2 passes | Positional findings | Unverifiable | Inputs inspected | implicit_matching (prototype) | Issues by code |",
        "|---|---|---|---|---|---|---|",
    ]
    for rev, d in record["dc3"].items():
        codes = "; ".join(f"{k}: {v}" for k, v in d["issues_by_code"].items()) or "none"
        lines.append(
            f"| `{rev}` | {'yes' if d['success'] else 'no'} | {d['metrics']['Positional bindings (blocking)'] + d['metrics']['Positional bindings pinned (legacy warning)']} "
            f"| {d['metrics']['Positional unverifiable']} | {d['metrics']['Positional inputs inspected']} "
            f"| {d['outcomes']['implicit_matching']} ({d['prototype_implicit_matching']}) | {codes} |"
        )
    lines += [
        "",
        "## Siblings",
        "",
        *(f"- {n}: HEAD `{h}`" for n, h in record["siblings"].items()),
        "",
        "## Absolute symlinks skipped by the export",
        "",
        "None is under `models/` (one there aborts the export). The full list is in the JSON.",
        "",
    ]
    for tree, links in record["skipped_absolute_links"].items():
        tops = sorted({link.split("/", 1)[0] for link in links})
        lines.append(f"- {tree}: {len(links)}" + (f", under {', '.join(tops)}" if tops else ""))
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
