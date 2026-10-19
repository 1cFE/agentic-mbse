"""Run the subset-profile evaluator over the acceptance trees and record what it reports.

    uv run python scripts/subset_profile/run_trees.py --final-rev REV --codegen-rev REV --out DIR \
        (--tree NAME ... | --all)

Item 1 Phase 10's acceptance trees, rerun by Item 2a P7 against the 2a contract. `--codegen-rev`
names the sysml-codegen revision the findings are judged against (Item 1 used `b5663c07`). Trees:

- `dc3-baseline`: dc3 `808464df` `models/`. Every confirmed T-001 category B1-B8 must appear.
- `dc3-repaired`: dc3 `60b44d53` `models/`, which generates at that codegen. Zero `refused`.
- `corpus`: sysml-codegen at `--codegen-rev`, `tests/fixtures/v6_recapture_batch/batch.json`, one run per
  fixture directory. Zero `refused` on the snapshot fixtures; on the refusal fixtures every
  `refused` finding's code must be in the fixture's recorded code list (a lower bound) or be
  recorded for a conformance case.

Each tree is read from a `git archive` export into a temp directory, loaded with
`SysideAdapter.load_model`, extracted once and evaluated with the default (generator) roots.
The evaluator runs from this checkout, which must be at `--final-rev` with `src/` clean; that is
the identity every output records. Outputs: `<DIR>/<tree>.json` and `<DIR>/<tree>.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

from isolated_tree import CODEGEN_SIBLING, export_tree, git, resolve_rev  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEGEN_REPO = CODEGEN_SIBLING
DC3_REPO = Path.home() / "src" / "dc3"
DC3_BASELINE_REV = "808464df85d50521e4fbb9ba7cceb63d382aa832"
DC3_REPAIRED_REV = "60b44d53460fccd2f44811d8abfd42bc270e90b2"
BATCH = "tests/fixtures/v6_recapture_batch/batch.json"
TREES = ("dc3-baseline", "dc3-repaired", "corpus")

load_dotenv(REPO_ROOT / ".env")

from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: E402
from agentic_mbse.sysml.subset_facts import (  # noqa: E402
    InvocationsWalked,
    SubsetFacts,
)
from agentic_mbse.sysml.subset_profile import (  # noqa: E402
    PACKAGED_RULES,
    Outcome,
    SubsetFinding,
    SubsetProfileResult,
    UnverifiedCheck,
    evaluate_subset_profile,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402


class RunError(RuntimeError):
    """A run cannot vouch for its identity or its own self-check."""


@dataclass(frozen=True)
class Identity:
    agentic_rev: str
    codegen_rev: str
    tree_repo: str
    tree_rev: str
    tree_path: str
    syside_version: str


@dataclass(frozen=True)
class TreeRun:
    label: str
    identity: Identity
    #: The exported tree's root; locations are reported relative to it.
    root: Path
    facts: SubsetFacts
    result: SubsetProfileResult
    load_diagnostics: int


# ---- running -----------------------------------------------------------------------------------


def _syside_version() -> str:
    import syside

    return str(syside.__version__)


def require_final_checkout(final_rev: str) -> str:
    head = resolve_rev(REPO_ROOT, "HEAD")
    if head != resolve_rev(REPO_ROOT, final_rev):
        raise RunError(f"this checkout is at {head}, not the final revision {final_rev}")
    dirty = git(REPO_ROOT, "status", "--porcelain", "--", "src", "pyproject.toml", "uv.lock")
    if dirty:
        raise RunError(f"src/ is not clean at the final revision:\n{dirty}")
    return head


def evaluate_tree(label: str, models: Path, root: Path, identity: Identity) -> TreeRun:
    files = sorted(models.rglob("*.sysml"))
    if not files:
        raise RunError(f"{label}: no .sysml files under {models}")
    model, diagnostics = SysideAdapter.load_model(files)
    errors = list(diagnostics.errors)
    facts = extract_subset_facts(model)
    result = evaluate_subset_profile(facts)
    run = TreeRun(label, identity, root, facts, result, len(errors))
    self_check(run)
    return run


def self_check(run: TreeRun) -> None:
    """The plan's stencil: the roots used and both counts are reported, at the expected identity.

    With default roots, the roots used are the generator's roots, which a model with no
    package-level part usage does not have; roots that could not be computed are a result
    (verdict INCOMPLETE or REFUSED_INCOMPLETE), reported, not a run failure.
    """
    scope = run.result.scope
    if scope.roots_available and scope.roots_used != scope.generator_root_ids:
        raise RunError(f"{run.label}: default roots used {scope.roots_used} != generator roots")
    if run.result.counts.declarations is None or run.result.counts.occurrences is None:
        raise RunError(f"{run.label}: declaration or occurrence count missing")


def with_export(repo: Path, rev: str, subdir: str, work: Path) -> Path:
    dest = work / f"{repo.name}-{rev[:8]}"
    export_tree(repo, rev, dest)
    return dest / subdir


# ---- reporting ---------------------------------------------------------------------------------


def _names(facts: SubsetFacts) -> dict[UUID, str]:
    return {
        m.usage.element_id: m.usage.qualified_name or str(m.usage.element_id)
        for m in facts.multiplicities
    }


def _callables(facts: SubsetFacts) -> dict[UUID, tuple[str, ...]]:
    out = {}
    for site in facts.sites:
        if isinstance(site.inspection.invocations, InvocationsWalked):
            out[site.feature.element_id] = tuple(
                sorted(
                    {
                        u.callable_name or "<unresolved>"
                        for u in site.inspection.invocations.uses
                        if not u.supported
                    }
                )
            )
    return out


def _location(finding: SubsetFinding | UnverifiedCheck, root: Path) -> str:
    """`path:line` relative to the exported tree (SysIDE reports the absolute temp path)."""
    loc = finding.location if isinstance(finding, SubsetFinding) else finding.subject
    if loc is None:
        return "<no location>"
    file = loc.file or "?"
    at = file.find(str(root))
    if at >= 0:
        file = file[at + len(str(root)) :].lstrip("/")
    return f"{file}:{loc.line if loc.line is not None else '?'}"


def _expected_code(finding: SubsetFinding) -> str | None:
    return PACKAGED_RULES.rule(finding.rule_id).shape(finding.shape_id).expected_code


def finding_json(
    f: SubsetFinding, callables: dict[UUID, tuple[str, ...]], root: Path
) -> dict[str, Any]:
    return {
        "rule": f.rule_id,
        "shape": f.shape_id,
        "context": f.context_id.value,
        "outcome": f.outcome.value,
        "reason": f.reason,
        "detail_reasons": list(f.detail_reasons),
        "subject": f.subject.qualified_name,
        "subject_id": str(f.subject.element_id),
        "location": _location(f, root),
        "occurrence_count": f.occurrence_count,
        "via_roots": [str(r) for r in f.via_roots],
        "evidence": [
            getattr(e, "case_id", None) or getattr(e, "fixture", None) for e in f.evidence
        ],
        "expected_code": _expected_code(f),
        "unsupported_callables": list(callables.get(f.subject.element_id, ())),
    }


def unverified_json(u: UnverifiedCheck, root: Path) -> dict[str, Any]:
    return {
        "rule": u.rule_id,
        "context": u.context_id.value if u.context_id else None,
        "location": _location(u, root),
        "subject": u.subject.qualified_name if u.subject else None,
        "cause": str(u.cause.value),
        "detail": u.detail,
    }


def run_json(run: TreeRun) -> dict[str, Any]:
    names = _names(run.facts)
    callables = _callables(run.facts)
    r = run.result
    return {
        "label": run.label,
        "identity": run.identity.__dict__,
        "versions": {
            "subset_profile": r.subset_profile_version,
            "executable_profile": r.executable_profile_version,
        },
        "load_error_diagnostics": run.load_diagnostics,
        "verdict": r.verdict.value,
        "scope": {
            "roots_available": r.scope.roots_available,
            "generator_roots": [names.get(i, str(i)) for i in r.scope.generator_root_ids],
            "roots_used": [names.get(i, str(i)) for i in r.scope.roots_used],
            "narrowed": r.scope.narrowed,
            "not_enumerated": [k.value for k in r.scope.not_enumerated],
        },
        "counts": {
            "declarations": r.counts.declarations,
            "occurrences": r.counts.occurrences,
            "by_outcome": {o.value: n for o, n in r.counts.by_outcome},
            "unverified": r.counts.unverified,
            "unassessed_constraints": r.counts.unassessed_constraints,
        },
        "dedup": "findings keyed by (rule, shape, context, declaration UUID); occurrences per declaration in occurrence_count",
        "findings": [finding_json(f, callables, run.root) for f in r.findings],
        "unverified": [unverified_json(u, run.root) for u in r.unverified],
    }


def _table(rows: Iterable[tuple[str, ...]], header: tuple[str, ...]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in rows]
    return out


def run_markdown(data: dict[str, Any]) -> list[str]:
    ident = data["identity"]
    lines = [
        f"### {data['label']}",
        "",
        f"- **Identity:** agentic-mbse `{ident['agentic_rev']}`, judged against sysml-codegen `{ident['codegen_rev']}`, "
        f"SysIDE {ident['syside_version']}; tree {ident['tree_repo']} `{ident['tree_rev']}` `{ident['tree_path']}`.",
        f"- **Verdict:** `{data['verdict']}`. Load error diagnostics: {data['load_error_diagnostics']}.",
        f"- **Roots used ({len(data['scope']['roots_used'])}):** "
        + (", ".join(f"`{n}`" for n in data["scope"]["roots_used"]) or "none")
        + f". Narrowed: {data['scope']['narrowed']}. Not enumerated: {data['scope']['not_enumerated'] or 'none'}.",
        f"- **Counts:** {data['counts']['declarations']} declarations, {data['counts']['occurrences']} occurrences; "
        f"by outcome {data['counts']['by_outcome']}; {data['counts']['unverified']} unverified; "
        f"{data['counts']['unassessed_constraints']} unassessed constraints.",
        f"- **Dedup:** {data['dedup']}.",
        "",
    ]
    findings = data["findings"]
    groups = Counter((f["rule"], f["shape"], f["context"], f["outcome"]) for f in findings)
    occ: Counter[tuple[str, str, str, str]] = Counter()
    for f in findings:
        occ[(f["rule"], f["shape"], f["context"], f["outcome"])] += f["occurrence_count"] or 0
    if groups:
        lines += _table(
            (
                (r, s, c, o, str(n), str(occ[(r, s, c, o)]))
                for (r, s, c, o), n in sorted(groups.items())
            ),
            ("Rule", "Shape", "Context", "Outcome", "Declarations", "Occurrences"),
        )
        lines.append("")
    for outcome in ("refused", "unconfirmed"):
        chosen = [f for f in findings if f["outcome"] == outcome]
        if chosen:
            lines.append(f"**Every `{outcome}` finding ({len(chosen)}):**")
            lines.append("")
            lines += _table(
                (
                    (
                        f["rule"],
                        f["shape"],
                        f["context"],
                        f["subject"] or f["subject_id"],
                        f["location"],
                        str(f["occurrence_count"]),
                        ", ".join(f["unsupported_callables"]),
                        f["expected_code"] or "",
                    )
                    for f in chosen
                ),
                (
                    "Rule",
                    "Shape",
                    "Context",
                    "Subject",
                    "Location",
                    "Occurrences",
                    "Callables",
                    "Code",
                ),
            )
            lines.append("")
    if data["unverified"]:
        lines.append(f"**Every `unverified` check ({len(data['unverified'])}):**")
        lines.append("")
        lines += _table(
            (
                (
                    u["rule"],
                    u["context"] or "",
                    u["subject"] or "",
                    u["location"],
                    u["cause"],
                    u["detail"][:160],
                )
                for u in data["unverified"]
            ),
            ("Rule", "Context", "Subject", "Location", "Cause", "Detail"),
        )
        lines.append("")
    return lines


# ---- the three trees ------------------------------------------------------------------------------


def run_dc3(
    label: str, rev: str, agentic_rev: str, codegen_rev: str, work: Path
) -> list[dict[str, Any]]:
    models = with_export(DC3_REPO, rev, "models", work)
    identity = Identity(agentic_rev, codegen_rev, "dc3", rev, "models/", _syside_version())
    return [run_json(evaluate_tree(label, models, models.parent, identity))]


def run_corpus(
    agentic_rev: str, codegen_rev: str, work: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = with_export(CODEGEN_REPO, codegen_rev, ".", work)
    batch = json.loads((root / BATCH).read_text(encoding="utf-8"))
    runs = []
    for name in batch["fixtures"]:
        record = batch["records"][name]
        identity = Identity(
            agentic_rev,
            codegen_rev,
            "sysml-codegen",
            codegen_rev,
            f"tests/fixtures/{name}/",
            _syside_version(),
        )
        data = run_json(evaluate_tree(name, root / "tests" / "fixtures" / name, root, identity))
        data["batch_status"] = record["status"]
        data["batch_codes"] = record.get("codes", [])
        runs.append(data)
    manifest = {
        "fixtures": len(batch["fixtures"]),
        "captured": len(batch["captured"]),
        "refused": len(batch["refused"]),
        "status": batch["status"],
    }
    return runs, manifest


def corpus_checks(runs: list[dict[str, Any]], case_codes: set[str]) -> list[dict[str, Any]]:
    """Per fixture: snapshot fixtures need zero refused; refusal fixtures need each refused code listed."""
    checks = []
    for data in runs:
        refused = [f for f in data["findings"] if f["outcome"] == "refused"]
        if data["batch_status"] == "graph":
            ok = not refused
            note = (
                "snapshot fixture: zero refused"
                if ok
                else f"R2 STOP: {len(refused)} refused on a snapshot fixture"
            )
        else:
            outside = sorted({f["expected_code"] for f in refused} - set(data["batch_codes"]))
            uncased = [c for c in outside if c not in case_codes]
            ok = not uncased
            note = (
                f"refusal fixture: {len(refused)} refused, codes {sorted({f['expected_code'] for f in refused})}"
                + (f"; outside the record but case-recorded: {outside}" if outside else "")
                + (f"; NEEDS CASE: {uncased}" if uncased else "")
            )
        checks.append(
            {"fixture": data["label"], "status": data["batch_status"], "ok": ok, "note": note}
        )
    return checks


def recorded_refusal_codes() -> set[str]:
    return {
        shape.expected_code
        for rule in PACKAGED_RULES.rules
        for shape in rule.shapes
        if shape.expected_code and shape.contexts_with(Outcome.REFUSED)
    }


def write(out: Path, label: str, payload: dict[str, Any], markdown: list[str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{label}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / f"{label}.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {out / label}.{{json,md}}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--final-rev", required=True)
    parser.add_argument("--codegen-rev", required=True)
    parser.add_argument("--out", type=Path, required=True, help="directory for the run's evidence")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tree", action="append", choices=TREES)
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()
    agentic_rev = require_final_checkout(args.final_rev)
    codegen_rev = resolve_rev(CODEGEN_REPO, args.codegen_rev)
    trees = TREES if args.all else tuple(args.tree)
    with tempfile.TemporaryDirectory(prefix="subset-trees-") as tmp:
        work = Path(tmp)
        for tree in trees:
            title = f"# Subset-profile run: {tree}"
            if tree in ("dc3-baseline", "dc3-repaired"):
                rev = DC3_BASELINE_REV if tree == "dc3-baseline" else DC3_REPAIRED_REV
                runs = run_dc3(tree, rev, agentic_rev, codegen_rev, work)
                write(
                    args.out,
                    tree,
                    runs[0],
                    [
                        title,
                        "",
                        "Generated by `scripts/subset_profile/run_trees.py`.",
                        "",
                        *run_markdown(runs[0]),
                    ],
                )
                print(f"{tree}: verdict {runs[0]['verdict']}, counts {runs[0]['counts']}")
                continue
            runs, manifest = run_corpus(agentic_rev, codegen_rev, work)
            checks = corpus_checks(runs, recorded_refusal_codes())
            md = [
                title,
                "",
                "Generated by `scripts/subset_profile/run_trees.py`.",
                "",
                f"`{BATCH}` at `{codegen_rev}` (status `{manifest['status']}`): {manifest['fixtures']} fixtures, "
                f"{manifest['captured']} snapshot records, {manifest['refused']} typed refusal records (read from the manifest; the batch README says 15 and 22).",
                "",
                "The snapshot fixtures prove admission through elaboration and projection, not full generation. They contain no function invocations, no `ordered` or `nonunique` multiplicity and no range multiplicity, so they are a regression floor, not proof that the rules are not overbroad.",
                "",
                *_table(
                    (
                        (c["fixture"], c["status"], "ok" if c["ok"] else "FAIL", c["note"])
                        for c in checks
                    ),
                    ("Fixture", "Batch", "Check", "Note"),
                ),
                "",
            ]
            for data in runs:
                md += run_markdown(data)
            write(args.out, "corpus", {"manifest": manifest, "checks": checks, "runs": runs}, md)
            failed = [c for c in checks if not c["ok"]]
            print(f"corpus: {len(checks) - len(failed)}/{len(checks)} fixtures pass the check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
