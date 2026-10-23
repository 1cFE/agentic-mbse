"""Phase R: run each generated probe package once, and ask SysIDE for the native values.

`check` and `generate` were run before this script, from the CLI (commands in ../risk1-reruns.md).
This script reads the packages `generate` wrote under /tmp/grg-impl/phaseR/<case>/pkg, runs each
once with simkit at the model's own values, and prints:
- every output channel value, or the exception if the run raised;
- every constraint verdict file the run wrote;
- SysIDE `evaluate_feature` for the features named in NATIVE below, with any diagnostic.

Read-only in sysml-codegen and TEAx. Writes only under /tmp/grg-impl/phaseR/. Run from this folder:

    ../../spike/codegen.sh run_phase_r.py > run_phase_r.txt 2>&1
"""

from __future__ import annotations

import json
import shutil
import traceback
from pathlib import Path
from typing import Any

import syside

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/grg-impl/phaseR")

# case -> list of (feature qualified name, scope qualified name). Only shapes Phase 1 found
# trustworthy are asked: no unit annotations, no redefinition above the scope (B4).
NATIVE: dict[str, list[tuple[str, str]]] = {
    "default_count_usage": [("Packs::Pack::cell_count", "Packs::pack")],
    "default_count_spec": [("Packs::Pack::cell_count", "Packs::pack"), ("Packs::Pack::cell_count", "Packs::BigPack")],
    "positional_reversed": [("PositionalReversed::Plant::result", "PositionalReversed::plant")],
    "positional_byname": [("PositionalByName::Plant::result", "PositionalByName::plant")],
    "string_dropped": [("fx::Gen::label", "fx::gen"), ("fx::Gen::t", "fx::gen")],
    "calc_def_simple_name": [("Plant::Site::ra", "Plant::site"), ("Plant::Site::rb", "Plant::site")],
    "assert_verdict": [
        ("AssertVerdict::Host::doubled_load", "AssertVerdict::host"),
        ("AssertVerdict::Host::neg_load", "AssertVerdict::host"),
    ],
}
# Cases whose calc usage fx::Site::m ends in its own result expression.
RESULT_EXPRESSION_CASES = {"result_expression", "cond_branch_in_result", "indexed_ref_in_result", "callable_in_result"}


def plain(v: Any) -> Any:
    return v if isinstance(v, (int, float, bool, str)) or v is None else repr(v)


def native(case: str) -> None:
    files = sorted(str(p) for p in (HERE / case).rglob("*.sysml"))
    model, _ = syside.load_model(files)
    els = {}
    for el in model.elements(syside.Element, include_subtypes=True):
        qn = getattr(el, "qualified_name", None)
        if qn is not None:
            els[str(qn)] = el
    comp = syside.Compiler()
    for feature, scope in NATIVE.get(case, []):
        v, rep = comp.evaluate_feature(els[feature], scope=els[scope], stdlib=model.lib)
        print(f"  native evaluate_feature({feature}, scope={scope}) -> {plain(v)!r} diagnostics={[str(d.message) for d in rep.diagnostics]}")
    if case in RESULT_EXPRESSION_CASES:
        # evaluate_feature on the usage returns the usage object, so ask for its own result
        # expression directly, and, for contrast, the definition's result with the usage as scope.
        usage = els["fx::Site::m"]
        v, rep = comp.evaluate(usage.result_expression, scope=usage, stdlib=model.lib)
        print(f"  native evaluate(fx::Site::m result expression, scope=fx::Site::m) -> {plain(v)!r} diagnostics={[str(d.message) for d in rep.diagnostics]}")
        v, rep = comp.evaluate_feature(usage.result, scope=usage, stdlib=model.lib)
        print(f"  native evaluate_feature({usage.result.qualified_name}, scope=fx::Site::m) -> {plain(v)!r} (the definition's body, for contrast)")


def run_package(case: str) -> None:
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    scratch = SCRATCH / case
    pkg = scratch / "pkg"
    loader = ProvisionalPackageLoader(package_dir=pkg, package_name=case, link_root=scratch / "link")
    module, _ = loader.load()
    registry = getattr(module, f"create_{case}_registry")()
    run = scratch / "run"
    if run.exists():
        shutil.rmtree(run)
    try:
        execute_pipeline(pkg / "pipelines/pipeline.yaml", run, registry=registry, custom_schema_types=module.CUSTOM_SCHEMA_TYPES)
    except Exception as exc:  # the probe records the failure; it is a result, not an error in the probe
        print(f"  package run failed: {type(exc).__name__}: {exc}")
        print("  " + traceback.format_exc().strip().splitlines()[-1])
        return
    files = {f.relative_to(run).as_posix(): json.loads(f.read_text()) for f in run.rglob("*.json")}
    manifest = next((v for k, v in files.items() if k.endswith("manifest.json")), {})
    for art in manifest.get("artifacts", []):
        rel = art["relative_path"]
        match = [v for k, v in files.items() if k.endswith(rel) or Path(k).stem == Path(rel).stem]
        print(f"  generated channel {art['channel']} = {match[0] if match else '<no file>'}")
    for k, v in sorted(files.items()):
        if "evaluation" in k or "constraint" in k or "verdict" in k:
            print(f"  run file {k}: {json.dumps(v)[:600]}")


def main() -> None:
    for d in sorted(p for p in HERE.iterdir() if p.is_dir()):
        case = d.name
        print(f"== {case}")
        if (SCRATCH / case / "pkg").exists():
            run_package(case)
        else:
            print("  no package (generate refused)")
        native(case)


if __name__ == "__main__":
    main()
