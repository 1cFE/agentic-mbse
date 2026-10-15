"""Claim 4, part 2: a prototype L2_POSITIONAL_BINDING detector, and its controls.

Throwaway prototype for evidence only; not repo source.

Rule (epic Item 4): flag an authored `in` parameter of a calculation or constraint
(usage or definition) whose *implicit* redefinition targets a differently named
formal, when no *explicit* redefinition accounts for it. The evidence is SysIDE's
resolved Redefinition relationships and their `is_implied` flag, never a comparison
of name sets.

Outcomes per inspected input:
  explicit            explicit redefinition present (`:>>`, `redefines`, `local redefines a`)
  anonymous           no declared name: positional by construction
  implicit_matching   implied redefinition to a same-named formal
  implicit_mismatch   implied redefinition to a differently named formal -> FINDING
  new_parameter       no redefinition and no unredefined inherited input to bind
  unverified          evidence missing or inspection raised -> FINDING (never clean)

Modes:
  fixtures                 run every 04-fixtures/detector/*.sysml, compare to its header
  naive                    same fixtures through a name-set-equality detector (control)
  tree <label> <dir>       scan one consumer model tree
  mutate <dir> <scratch>   copy a tree, swap two in-order unprefixed inputs, rescan
  unverified               inject an inspection failure and show it is reported
"""

from __future__ import annotations

import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import syside
from agentic_mbse.sysml.syside_adapter import SysideAdapter

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "04-fixtures" / "detector"
IN_DIRECTIONS = {syside.FeatureDirectionKind.In, syside.FeatureDirectionKind.Inout}
OWNER_KINDS = (
    syside.CalculationUsage,
    syside.ConstraintUsage,
    syside.CalculationDefinition,
    syside.ConstraintDefinition,
)


@dataclass(frozen=True)
class Finding:
    outcome: str
    qualified_name: str
    location: str
    detail: str


def _location(element: Any) -> str:
    try:
        location = SysideAdapter.get_source_location(element)
    except Exception:  # display only
        location = None
    return f"{location[0]}:{location[1]}" if location else "<location unavailable>"


def _qn(element: Any) -> str:
    try:
        return str(element.qualified_name)
    except Exception:
        return "<unnamed>"


def _owners(model: Any) -> list[Any]:
    seen: dict[int, Any] = {}
    for kind in OWNER_KINDS:
        for owner in model.nodes(kind, include_subtypes=True):
            seen.setdefault(id(owner), owner)
    return list(seen.values())


def _inputs(owner: Any) -> list[Any]:
    return [
        f for f in owner.owned_features.collect()
        if getattr(f, "direction", None) in IN_DIRECTIONS
    ]


def _default_heritage(feature: Any) -> list[Any]:
    return list(feature.heritage.relationships)


def scan(
    model: Any, heritage_of: Callable[[Any], list[Any]] = _default_heritage
) -> tuple[list[Finding], Counter]:
    findings: list[Finding] = []
    stats: Counter = Counter()
    for owner in _owners(model):
        try:
            inputs = _inputs(owner)
        except Exception as exc:
            stats["unverified"] += 1
            findings.append(Finding("UNVERIFIED", _qn(owner), _location(owner),
                                    f"could not enumerate inputs: {exc!r}"))
            continue
        try:
            bound_targets = {
                _qn(r.redefined_feature)
                for f in inputs
                for r in heritage_of(f)
                if isinstance(r, syside.Redefinition)
            }
        except Exception:
            bound_targets = set()
        for feature in inputs:
            try:
                redefs = [r for r in heritage_of(feature) if isinstance(r, syside.Redefinition)]
                declared = feature.declared_name
                explicit = [r for r in redefs if not r.is_implied]
                implied = [r for r in redefs if r.is_implied]
                if explicit:
                    stats["explicit"] += 1
                    continue
                if declared is None:
                    stats["anonymous"] += 1
                    continue
                if implied:
                    targets = [r.redefined_feature for r in implied]
                    wrong = [t for t in targets if t.name != declared]
                    if wrong:
                        stats["implicit_mismatch"] += 1
                        findings.append(Finding(
                            "L2_POSITIONAL_BINDING", _qn(feature), _location(feature),
                            f"input '{declared}' implicitly redefines "
                            + ", ".join(f"'{_qn(t)}'" for t in wrong)
                            + f" by position; write `in :>> {wrong[0].name}` (by name) "
                            f"or `in {declared} redefines {wrong[0].name}` (deliberate rename)",
                        ))
                    else:
                        stats["implicit_matching"] += 1
                    continue
                unbound = [
                    f for f in owner.inherited_features.collect()
                    if getattr(f, "direction", None) in IN_DIRECTIONS
                    and _qn(f) not in bound_targets
                ]
                if unbound:
                    stats["unverified"] += 1
                    findings.append(Finding(
                        "UNVERIFIED", _qn(feature), _location(feature),
                        "no redefinition evidence although the owner inherits "
                        f"{len(unbound)} input(s)",
                    ))
                else:
                    stats["new_parameter"] += 1
            except Exception as exc:
                stats["unverified"] += 1
                findings.append(Finding("UNVERIFIED", _qn(feature), _location(feature),
                                        f"inspection raised {exc!r}"))
    return findings, stats


def naive_scan(model: Any) -> list[str]:
    """Control: flag a usage input whose name is not among its types' input names."""
    flagged = []
    for kind in (syside.CalculationUsage, syside.ConstraintUsage):
        for usage in model.nodes(kind, include_subtypes=True):
            formal_names = set()
            for typ in usage.types.collect():
                for f in typ.features.collect():
                    if getattr(f, "direction", None) in IN_DIRECTIONS and f.name:
                        formal_names.add(f.name)
            if not formal_names:
                continue
            for f in _inputs(usage):
                if f.declared_name and f.declared_name not in formal_names:
                    flagged.append(_qn(f))
    return flagged


def _load(paths: list[Path]) -> Any:
    model, _diagnostics = syside.load_model([str(p) for p in paths])
    return model


def _short(qn: str, package: str) -> str:
    return qn.replace(f"'{package}'::", "").replace(f"{package}::", "").replace("'", "")


def _expectation(path: Path) -> tuple[str, set[str]]:
    text = path.read_text()
    expect = re.search(r"// expect: (\w+)", text)[1]
    flagged = re.search(r"// flagged: (.*)", text)[1].strip()
    return expect, (set() if flagged == "-" else set(flagged.split()))


def run_fixtures() -> int:
    print(f"{'fixture':40} {'expect':7} {'got':7} {'flagged inputs (got)':38} ok")
    failures = 0
    totals: Counter = Counter()
    for path in sorted(FIXTURES.glob("*.sysml")):
        expect, expected_flags = _expectation(path)
        findings, stats = scan(_load([path]))
        totals.update(stats)
        got_flags = {_short(f.qualified_name, path.stem) for f in findings
                     if f.outcome == "L2_POSITIONAL_BINDING"}
        unverified = [f for f in findings if f.outcome == "UNVERIFIED"]
        got = "FLAG" if got_flags else ("UNVERIF" if unverified else "PASS")
        ok = got == expect and got_flags == expected_flags
        failures += not ok
        print(f"{path.stem:40} {expect:7} {got:7} {' '.join(sorted(got_flags)) or '-':38} "
              f"{'yes' if ok else 'NO'}")
    print(f"\ninput outcome totals: {dict(totals)}")
    print(f"fixtures failing expectation: {failures}")
    return 1 if failures else 0


def run_naive() -> int:
    print("Control: name-set-equality detector on the same fixtures\n")
    print(f"{'fixture':40} {'expect':7} {'naive':7} {'resolved-evidence':17} naive right?")
    wrong = 0
    for path in sorted(FIXTURES.glob("*.sysml")):
        expect, _ = _expectation(path)
        model = _load([path])
        naive = "FLAG" if naive_scan(model) else "PASS"
        findings, _ = scan(model)
        resolved = "FLAG" if any(f.outcome == "L2_POSITIONAL_BINDING" for f in findings) else "PASS"
        right = naive == expect
        wrong += not right
        print(f"{path.stem:40} {expect:7} {naive:7} {resolved:17} {'yes' if right else 'NO'}")
    print(f"\nnaive detector wrong on {wrong} fixture(s)")
    return 0


def _tree_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.sysml"))


def run_tree(label: str, root: Path) -> int:
    files = _tree_files(root)
    print(f"tree {label}: {root} ({len(files)} .sysml files)")
    findings, stats = scan(_load(files))
    print(f"input outcome totals: {dict(sorted(stats.items()))}")
    print(f"findings: {len(findings)}")
    for f in sorted(findings, key=lambda f: f.location):
        print(f"  {f.outcome:22} {f.location.replace(str(root) + '/', '')}  {f.qualified_name}\n"
              f"      {f.detail}")
    return 0


UNPREFIXED = re.compile(r"^(\s*)in\s+('[^']+'|\w+)\s*=")


def run_mutation(root: Path, scratch: Path) -> int:
    """Swap the first pair of adjacent, same-named, unprefixed inputs in a copy."""
    model = _load(_tree_files(root))
    candidate = None
    for owner in sorted(_owners(model), key=_location):
        if not isinstance(owner, (syside.CalculationUsage, syside.ConstraintUsage)):
            continue
        ins = _inputs(owner)
        implicit = [
            f for f in ins
            if f.declared_name
            and all(r.is_implied for r in f.heritage.relationships
                    if isinstance(r, syside.Redefinition))
            and any(isinstance(r, syside.Redefinition) for r in f.heritage.relationships)
        ]
        if len(implicit) == len(ins) >= 2:
            candidate = (owner, ins[0], ins[1])
            break
    if candidate is None:
        print("no in-order unprefixed calc/constraint usage with >=2 inputs found")
        return 1
    owner, first, second = candidate
    file_a, line_a = _location(first).rsplit(":", 1)
    _, line_b = _location(second).rsplit(":", 1)
    rel = Path(file_a).relative_to(root)
    print(f"mutation target: {_qn(owner)} at {rel}:{line_a}")
    print(f"  swapping input lines {line_a} ('{first.declared_name}') and {line_b} "
          f"('{second.declared_name}')")

    shutil.rmtree(scratch, ignore_errors=True)
    shutil.copytree(root, scratch)
    target = scratch / rel
    lines = target.read_text().splitlines(keepends=True)
    a, b = int(line_a) - 1, int(line_b) - 1
    assert UNPREFIXED.match(lines[a]) and UNPREFIXED.match(lines[b]), (lines[a], lines[b])
    lines[a], lines[b] = lines[b], lines[a]
    target.write_text("".join(lines))
    print("  mutated lines now:")
    print("    " + lines[a].rstrip())
    print("    " + lines[b].rstrip())

    before, _ = scan(_load(_tree_files(root)))
    after, _ = scan(_load(_tree_files(scratch)))
    print(f"\nfindings before mutation: {len(before)}")
    print(f"findings after mutation:  {len(after)}")
    for f in after:
        print(f"  {f.outcome:22} {f.location.replace(str(scratch) + '/', '')}  {f.qualified_name}\n"
              f"      {f.detail}")
    caught = {f.qualified_name for f in after} - {f.qualified_name for f in before}
    print(f"\nnew findings caused by the swap: {len(caught)}")
    return 0 if caught else 1


def run_unverified() -> int:
    """Inject an inspection failure into one feature; it must not read as clean."""
    path = FIXTURES / "calc_in_order.sysml"
    model = _load([path])
    findings, stats = scan(model)
    print(f"{path.name} normal scan: findings={len(findings)} stats={dict(stats)}")

    def broken(feature: Any) -> list[Any]:
        if feature.declared_name == "b":
            raise RuntimeError("simulated SysIDE heritage failure")
        return _default_heritage(feature)

    findings, stats = scan(model, heritage_of=broken)
    print(f"{path.name} with injected failure on 'b': findings={len(findings)} "
          f"stats={dict(stats)}")
    for f in findings:
        print(f"  {f.outcome:22} {f.qualified_name}  {f.detail}")
    clean = not findings
    print(f"\nreported clean despite failed inspection: {clean}")
    return 1 if clean else 0


def main(argv: list[str]) -> int:
    print(f"syside {syside.__version__}")
    mode = argv[1]
    if mode == "fixtures":
        return run_fixtures()
    if mode == "naive":
        return run_naive()
    if mode == "tree":
        return run_tree(argv[2], Path(argv[3]))
    if mode == "mutate":
        return run_mutation(Path(argv[2]), Path(argv[3]))
    if mode == "unverified":
        return run_unverified()
    raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
