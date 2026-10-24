import json, shutil, sys
from pathlib import Path
import syside
S = Path(sys.argv[1])
def native(c):
    model, _ = syside.load_model([str(S / c / "model.sysml")])
    els = {str(e.qualified_name): e for e in model.elements(syside.Element, include_subtypes=True) if getattr(e, "qualified_name", None) is not None}
    comp = syside.Compiler()
    v, rep = comp.evaluate_feature(els[f"{c}::Base::x"], scope=els[f"{c}::p"], stdlib=model.lib)
    return v, [str(d.message) for d in rep.diagnostics]
def run(c):
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader
    scratch = S / "out" / c; pkg = scratch / "pkg"
    module, _ = ProvisionalPackageLoader(package_dir=pkg, package_name=c, link_root=scratch / "link").load()
    reg = getattr(module, f"create_{c}_registry")()
    out = scratch / "run"; shutil.rmtree(out, ignore_errors=True)
    execute_pipeline(pkg / "pipelines/pipeline.yaml", out, registry=reg, custom_schema_types=module.CUSTOM_SCHEMA_TYPES)
    res = {}
    for f in out.rglob("*.json"):
        if "manifest" in f.name: continue
        res[f.relative_to(out).as_posix()] = json.loads(f.read_text())
    params = {p.name: json.loads(p.read_text()) for p in pkg.rglob("*params*.json")}
    return params, res
for c in sorted(p.name for p in S.iterdir() if (p / "model.sysml").exists()):
    print("==", c)
    try:
        params, res = run(c); print("  package inputs:", json.dumps(params)[:300]); print("  package outputs:", json.dumps(res)[:300])
    except Exception as e:
        print("  run failed:", type(e).__name__, str(e)[:200])
    print("  native x:", native(c))
