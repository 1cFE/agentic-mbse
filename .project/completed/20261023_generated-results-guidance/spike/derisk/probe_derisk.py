"""Phase 1 de-risk probe: design bets B1 (shapes), B2, B3 and B4 on real models.

Adapted from ../channel-trace/probe_channels.py and probe_count.py. Changes from the spike:
- native scope is the innermost occurrence's ``OccurrenceRecord.effective_usage_id`` (B3), not
  ``containment_slot.root_declaration``; the slot-root result is still printed, for contrast;
- every value is marked or not by the B2 rule, read from the instance graph only: a node whose
  scope lies inside an occurrence of a slot with a count other than 1, plus everything downstream
  over input edges;
- count rows: per (owning occurrence, slot with indexed occurrences), SysIDE's multiplicity bound
  for the effective usage, in the owner's effective-usage scope, against occurrences built;
- each item is checked against EXPECTED.md, which was written before this probe ran.

Read-only in sysml-codegen (imports its internals, including the private ``_Projection``).
Writes only under /tmp/grg-impl/derisk/. Run through ../codegen.sh, from spike/:

    ./codegen.sh derisk/probe_derisk.py [case ...]

Exit 0 only if every item and every EXPECTED row passes.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import syside
from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.cli import prepare as P
from sysml_codegen.elaboration.graph import InstanceGraph, NodeRef, ProducerRef
from sysml_codegen.elaboration.identity import ExpressionPortId, NodeId, OccurrenceId
from sysml_codegen.elaboration.project import _Projection
from sysml_codegen.orchestration import exact_pipeline_context as E
from sysml_codegen.snapshot.instance_graph import decode_instance_graph

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
SCRATCH = Path("/tmp/grg-impl/derisk")
REL_TOL = 1e-9


# --------------------------------------------------------------------------- graph side


@dataclass
class Item:
    kind: str  # "value" or "count"
    key: str
    channel: str = ""
    mark: str | None = None
    generated: Any = None
    native: Any = None
    native_diags: list[str] = field(default_factory=list)
    contrast: Any = None  # native with the slot root as scope (the spike's rule)
    detail: str = ""


def load_graph(models: Path) -> InstanceGraph:
    loaded = P.load_source(P.LiveModels((models,)))
    ctx = E.build_exact_pipeline_context_from_live_load(loaded)
    return decode_instance_graph(object.__getattribute__(ctx, "_instance_bytes"))


def occ_path(graph: InstanceGraph, occ: OccurrenceId) -> str:
    parts = []
    for i in range(len(occ.steps)):
        rec = graph.occurrences[OccurrenceId(occ.steps[: i + 1])]
        parts.append(rec.display_segment)  # the segment already carries the index, e.g. "cells[0]"
    return ".".join(parts)


def slot_segment(rec) -> str:
    """The segment without its index (probe-only display; production uses the graph's display helpers)."""
    return re.sub(r"\[\d+\]$", "", rec.display_segment)


def slot_counts(graph: InstanceGraph) -> dict[tuple, int]:
    counts: dict[tuple, int] = {}
    for rec in graph.occurrences.values():
        k = (rec.parent_id, rec.containment_slot)
        counts[k] = counts.get(k, 0) + 1
    return counts


def scope_mark(graph: InstanceGraph, counts: dict[tuple, int], scope: Any) -> str | None:
    """B2, first half: the outermost occurrence on the scope chain whose slot count is not 1."""
    if not isinstance(scope, OccurrenceId):
        return None
    for i in range(len(scope.steps)):
        oid = OccurrenceId(scope.steps[: i + 1])
        rec = graph.occurrences[oid]
        n = counts[(rec.parent_id, rec.containment_slot)]
        if n != 1:
            parent = occ_path(graph, rec.parent_id) if rec.parent_id is not None else ""
            path = f"{parent}.{slot_segment(rec)}" if parent else slot_segment(rec)
            return f"multiplicity {path} ({n})"
    return None


def b2_marks(graph: InstanceGraph) -> dict[NodeId, str]:
    """B2: scope marks, then the downstream closure over input and alias edges."""
    counts = slot_counts(graph)
    marks: dict[NodeId, str] = {}
    for pop in (graph.attrs, graph.calcs, graph.constraints):
        for nid, node in pop.items():
            m = scope_mark(graph, counts, node.scope)
            if m is not None:
                marks[nid] = m

    def edge_mark(edge: Any) -> str | None:
        if isinstance(edge, NodeRef):
            return marks.get(edge.target)
        if isinstance(edge, ProducerRef):
            return marks.get(edge.target.calculation)
        return None

    changed = True
    while changed:
        changed = False
        for nid, attr in graph.attrs.items():
            if nid not in marks and attr.alias_target is not None:
                m = edge_mark(attr.alias_target)
                if m is not None:
                    marks[nid] = m
                    changed = True
        for pop in (graph.calcs, graph.constraints):
            for nid, node in pop.items():
                if nid in marks:
                    continue
                for edge in node.inputs.values():
                    m = edge_mark(edge)
                    if m is not None:
                        marks[nid] = m
                        changed = True
                        break
    return marks


def zero_edge_aggregations(graph: InstanceGraph) -> list[str]:
    """The design's zero-occurrence rule input: an aggregation reference with no edge."""
    found = []
    for node in graph.calcs.values():
        ordinals_with_ports = {p.reference_ordinal for p in node.input_names if isinstance(p, ExpressionPortId)}
        for o in node.aggregation_reference_ordinals:
            if o not in ordinals_with_ports:
                found.append(f"{node.display_path} reference {o}")
    return found


def value_items(graph: InstanceGraph, marks: dict[NodeId, str]) -> tuple[list[Item], list[dict]]:
    proj = _Projection(graph)
    proj.run()
    items, refs = [], []
    for port, channel in sorted(proj.output_channels.items(), key=lambda kv: kv[1]):
        node = graph.calcs[port.calculation]
        scope = node.node_id.scope
        base = occ_path(graph, scope) if isinstance(scope, OccurrenceId) else ""
        out_name = node.output_names[port.output]
        name = out_name if node.is_computed else f"{node.display_name}.{out_name}"
        key = f"{base}.{name}" if base else name
        items.append(Item("value", key, channel=channel, mark=marks.get(node.node_id)))
        eu = slot_root = None
        if isinstance(scope, OccurrenceId):
            rec = graph.occurrences[scope]
            eu, slot_root = rec.effective_usage_id.value, scope.steps[-1].containment_slot.root_declaration.value
        refs.append(
            {
                "node_decl": node.declaration_id.value,
                "output_decl": port.output.value,
                "is_computed": node.is_computed,
                "scope_eu": eu,
                "scope_slot_root": slot_root,
            }
        )
    return items, refs


def count_items(graph: InstanceGraph, marks_scope) -> tuple[list[Item], list[dict]]:
    """One row per (owning occurrence, slot) whose occurrences carry an index (explicit multiplicity)."""
    counts = slot_counts(graph)
    groups: dict[tuple, list] = {}
    for rec in graph.occurrences.values():
        if rec.parent_id is None or rec.occurrence_index is None:
            continue
        groups.setdefault((rec.parent_id, rec.containment_slot), []).append(rec)
    items, refs = [], []
    for (parent, slot), recs in sorted(groups.items(), key=lambda kv: occ_path(graph, kv[0][0]) + kv[1][0].display_segment):
        eus = {r.effective_usage_id for r in recs}
        prec = graph.occurrences[parent]
        key = f"{occ_path(graph, parent)}/{slot_segment(recs[0])}"
        it = Item("count", key, generated=len(recs), mark=scope_mark(graph, counts, parent))
        if len(eus) != 1:
            it.detail = f"occurrences of one slot have {len(eus)} effective usages"
        items.append(it)
        refs.append(
            {
                "eu": next(iter(eus)).value,
                "owner_eu": prec.effective_usage_id.value,
                "slot_root": slot.root_declaration.value,
                "owner_slot_root": parent.steps[-1].containment_slot.root_declaration.value,
            }
        )
    return items, refs


# --------------------------------------------------------------------------- SysIDE side


def plain(v: Any) -> Any:
    return v if isinstance(v, (int, float, bool)) or v is None else repr(v)


def native(models: Path, values: list[Item], vrefs: list[dict], counts: list[Item], crefs: list[dict]) -> None:
    model, _ = syside.load_model([str(p) for p in sorted(models.rglob("*.sysml"))])
    by_id = {}
    for el in model.elements(syside.Element, include_subtypes=True):
        eid = getattr(el, "element_id", None)
        if eid is not None:
            by_id[eid] = el
    comp = syside.Compiler()

    def ev(feature, scope):
        v, rep = comp.evaluate_feature(feature, scope=scope, stdlib=model.lib)
        return plain(v), [str(d.message) for d in rep.diagnostics]

    for it, r in zip(values, vrefs):
        feature = by_id[r["output_decl"]]
        if not r["is_computed"] and r["node_decl"] != r["output_decl"]:
            scope = contrast_scope = by_id[r["node_decl"]]  # calc usage: the usage itself (spike rule)
        else:
            scope, contrast_scope = by_id[r["scope_eu"]], by_id[r["scope_slot_root"]]
        it.native, it.native_diags = ev(feature, scope)
        it.contrast = ev(feature, contrast_scope)[0]
        it.detail = f"feature {feature.qualified_name}, scope {scope.qualified_name}"

    def bound(usage, scope):
        mult = getattr(usage, "multiplicity", None)
        if mult is None:
            return "no multiplicity"
        b = getattr(mult, "upper_bound", None)
        if b is None:
            return "no upper bound"
        v, rep = comp.evaluate(b, stdlib=model.lib, scope=scope)
        return plain(v)

    for it, r in zip(counts, crefs):
        eu, owner = by_id[r["eu"]], by_id[r["owner_eu"]]
        it.native = bound(eu, owner)
        it.contrast = bound(by_id[r["slot_root"]], by_id[r["owner_slot_root"]])
        it.detail = (it.detail + "; " if it.detail else "") + f"usage {eu.qualified_name}, scope {owner.qualified_name}"


# --------------------------------------------------------------------------- generated side


def generated(models: Path, scratch: Path, name: str) -> dict[str, Any]:
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    pkg = scratch / "pkg"
    assert run_codegen(GenerationConfig(models_path=models, output_path=pkg, package_name=name, overwrite=True))
    loader = ProvisionalPackageLoader(package_dir=pkg, package_name=name, link_root=scratch / "link")
    module, _ = loader.load()
    registry = getattr(module, f"create_{name}_registry")()
    run = scratch / "run"
    if run.exists():
        shutil.rmtree(run)
    execute_pipeline(pkg / "pipelines/pipeline.yaml", run, registry=registry, custom_schema_types=module.CUSTOM_SCHEMA_TYPES)
    files = {f.stem: json.loads(f.read_text()) for f in run.rglob("*.json")}
    values = {}
    for art in files.get("manifest", {}).get("artifacts", []):
        stem = Path(art["relative_path"]).stem
        if stem in files:
            values[art["channel"]] = files[stem]
    return values


# --------------------------------------------------------------------------- expectations


def parse_value(s: str) -> Any:
    s = s.strip()
    if s == "-":
        return None
    if s in ("True", "False"):
        return s == "True"
    return float(s) if any(c in s for c in ".eE") else int(s)


def load_expected() -> list[dict]:
    text = (HERE / "EXPECTED.md").read_text().split("## Rows", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0] in ("model", "---") or set(cells[0]) <= {"-"}:
            continue
        model, kind, item, intended, gen, nat, result = cells
        pattern = re.compile("^" + re.escape(item).replace(r"\[\*\]", r"\[\d+\]") + "$")
        rows.append(
            {"model": model, "kind": kind, "item": item, "pattern": pattern, "intended": parse_value(intended),
             "generated": parse_value(gen), "native": parse_value(nat), "result": result, "hits": 0}
        )
    return rows


def same(a: Any, b: Any) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, int) and isinstance(b, int):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isnan(a) or math.isnan(b):
            return False
        return abs(a - b) <= REL_TOL * max(abs(a), abs(b))
    return False


def judge(it: Item, row: dict) -> list[str]:
    errs = []
    if row["generated"] is not None and not same(it.generated, row["generated"]):
        errs.append(f"generated {it.generated!r} != expected {row['generated']!r}")
    if row["native"] is not None and not same(it.native, row["native"]):
        errs.append(f"native {it.native!r} != expected {row['native']!r}")
    res = row["result"]
    if res.startswith("nc "):
        if it.mark != res[3:]:
            errs.append(f"mark {it.mark!r} != expected {res[3:]!r}")
    else:
        if it.mark is not None:
            errs.append(f"marked {it.mark!r}, expected unmarked")
        agree = same(it.native, it.generated)
        if res == "agree" and not agree:
            errs.append(f"native {it.native!r} and generated {it.generated!r} differ")
        if res == "differ" and agree:
            errs.append("native and generated agree, expected a difference")
    return errs


# --------------------------------------------------------------------------- main


def run_case(case: str, expected: list[dict]) -> bool:
    models = MODELS / case
    scratch = SCRATCH / case
    scratch.mkdir(parents=True, exist_ok=True)
    graph = load_graph(models)
    marks = b2_marks(graph)
    values, vrefs = value_items(graph, marks)
    counts, crefs = count_items(graph, marks)
    native(models, values, vrefs, counts, crefs)
    gen = generated(models, scratch, case)
    for it in values:
        it.generated = gen.get(it.channel, "<no run file>")
    rows = [r for r in expected if r["model"] == case]
    ok = True
    print(f"=== {case}")
    zero = zero_edge_aggregations(graph)
    print(f"  occurrences: {len(graph.occurrences)}; marked nodes: {len(marks)}; zero-edge aggregation references: {zero or 'none'}")
    for it in values + counts:
        matching = [r for r in rows if r["kind"] == it.kind and r["pattern"].match(it.key)]
        if len(matching) != 1:
            verdict, errs = "FAIL", [f"{len(matching)} EXPECTED rows match this item"]
        else:
            matching[0]["hits"] += 1
            errs = judge(it, matching[0])
            verdict = "FAIL" if errs else "PASS"
        ok &= verdict == "PASS"
        label = "built" if it.kind == "count" else "generated"
        print(f"  {verdict} {it.kind} {it.key}  native {it.native!r}  {label} {it.generated!r}  mark {it.mark or '-'}")
        print(f"       {it.detail}; slot-root scope gives {it.contrast!r}" + (f"; channel {it.channel}" if it.channel else ""))
        if it.native_diags:
            print(f"       native diagnostics: {it.native_diags}")
        for e in errs:
            print(f"       ! {e}")
    for r in rows:
        if r["hits"] == 0:
            ok = False
            print(f"  FAIL EXPECTED row matched nothing: {r['kind']} {r['item']}")
    other = sorted(set(gen) - {it.channel for it in values})
    if other:
        print(f"  run channels not traced as outputs: {other}")
    return ok


def main() -> int:
    expected = load_expected()
    cases = sys.argv[1:] or sorted(p.name for p in MODELS.iterdir() if p.is_dir())
    unknown = sorted({r["model"] for r in expected} - set(cases)) if not sys.argv[1:] else []
    print(f"syside {syside.__version__}; cases {cases}")
    results = {c: run_case(c, expected) for c in cases}
    for m in unknown:
        print(f"FAIL EXPECTED names a model with no folder: {m}")
    print("SUMMARY " + " ".join(f"{c}={'PASS' if ok else 'FAIL'}" for c, ok in results.items()))
    return 0 if all(results.values()) and not unknown else 1


if __name__ == "__main__":
    sys.exit(main())
