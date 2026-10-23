"""Spike S2: trace each generated output channel to a SysML feature and occurrence path, run the
package, and compare with SysIDE's evaluate_feature at that path.

Read-only in sysml-codegen: imports its internals (including the private ``_Projection``) and
writes only under <scratch>. Run through ../codegen.sh so the interpreter is sysml-codegen's
venv with TEAx simkit on the path:

    spike/codegen.sh spike/channel-trace/probe_channels.py <model_dir> <scratch_dir> <package_name>
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import syside
from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.cli import prepare as P
from sysml_codegen.elaboration.identity import OccurrenceId
from sysml_codegen.elaboration.project import _Projection
from sysml_codegen.orchestration import exact_pipeline_context as E
from sysml_codegen.snapshot.instance_graph import decode_instance_graph


def trace(models: Path):
    """Pre-emission data: channel -> (calc node, output declaration, occurrence chain)."""
    loaded = P.load_source(P.LiveModels((models,)))
    ctx = E.build_exact_pipeline_context_from_live_load(loaded)
    ig = decode_instance_graph(object.__getattribute__(ctx, "_instance_bytes"))
    proj = _Projection(ig)
    proj.run()
    rows = []
    for port, channel in sorted(proj.output_channels.items(), key=lambda kv: kv[1]):
        node = ig.calcs[port.calculation]
        scope = node.node_id.scope
        chain = []
        if isinstance(scope, OccurrenceId):
            for i in range(len(scope.steps)):
                occ = ig.occurrences[OccurrenceId(scope.steps[: i + 1])]
                chain.append(
                    (occ.display_segment, occ.occurrence_index, scope.steps[i].containment_slot.root_declaration.value)
                )
        rows.append(
            {
                "channel": channel,
                "node_display_path": node.display_path,
                "node_decl": node.declaration_id.value,
                "calc_def": node.calc_def_qualified_name,
                "is_computed": node.is_computed,
                "output_name": node.output_names[port.output],
                "output_decl": port.output.value,
                "scope_kind": type(scope).__name__,
                "chain": chain,
            }
        )
    return rows


def native(models: Path, rows):
    files = [str(p) for p in models.rglob("*.sysml")]
    model, _ = syside.load_model(files)
    by_id = {}
    # Index every element of the user model by element_id.
    for el in model.elements(syside.Element, include_subtypes=True):
        eid = getattr(el, "element_id", None)
        if eid is not None:
            by_id[eid] = el
    for r in rows:
        try:
            chain_els = [by_id[d] for _, _, d in r["chain"]]
            node_el = by_id.get(r["node_decl"])
            out_el = by_id.get(r["output_decl"])
            # Scope: the innermost occurrence's declaring feature; for a calc usage, the usage itself.
            scope = chain_els[-1] if chain_els else None
            if node_el is not None and out_el is not None and node_el is not out_el:
                scope = node_el
            feature = out_el
            r["native_scope"] = getattr(scope, "qualified_name", None)
            r["native_feature"] = getattr(feature, "qualified_name", None)
            value, report = syside.Compiler().evaluate_feature(feature, scope=scope, stdlib=model.lib)
            r["native"] = value if isinstance(value, (int, float, bool)) or value is None else repr(value)
            r["native_diags"] = [str(d.message) for d in report.diagnostics]
        except Exception as e:  # noqa: BLE001
            r["native"] = f"ERROR {type(e).__name__}: {e}"


def generated(models: Path, scratch: Path, name: str):
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
    values = {}
    for f in run.rglob("*.json"):
        try:
            values[f.stem] = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            pass
    # Output files are named by alias; the run manifest maps each channel to its file.
    manifest = values.get("manifest", {})
    for art in manifest.get("artifacts", []):
        stem = Path(art["relative_path"]).stem
        if stem in values:
            values[art["channel"]] = values[stem]
    return values


def main() -> int:
    models, scratch, name = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
    scratch.mkdir(parents=True, exist_ok=True)
    rows = trace(models)
    native(models, rows)
    gen = generated(models, scratch, name)
    print(f"syside {syside.__version__}")
    for r in rows:
        g = gen.get(r["channel"], "<no file>")
        chain = ".".join(f"{s}" + (f"[{i}]" if i is not None else "") for s, i, _ in r["chain"])
        print(f"channel {r['channel']}")
        print(f"  pre-emission: occurrence {chain or '(package scope)'}; node {r['node_display_path']!r}; output {r['output_name']!r}; calc_def {r['calc_def']}; computed {r['is_computed']}")
        print(f"  native: evaluate_feature({r.get('native_feature')}, scope={r.get('native_scope')}) -> {r.get('native')} {r.get('native_diags', '')}")
        print(f"  generated: {g}")
        same = isinstance(g, (int, float)) and isinstance(r.get("native"), (int, float)) and abs(g - r["native"]) <= 1e-9 * max(abs(g), abs(r["native"]))
        print(f"  agree: {same}")
    others = sorted(set(gen) - {r["channel"] for r in rows})
    print("other run files (not traced output channels):", others)
    for k in others:
        v = gen[k]
        print(f"  {k}: {json.dumps(v)[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
