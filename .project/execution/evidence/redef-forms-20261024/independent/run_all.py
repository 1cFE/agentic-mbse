import json, shutil, sys, traceback, io, contextlib, logging
from pathlib import Path
P = Path("/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/probe2")
logging.disable(logging.CRITICAL)

def run_package(case):
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader
    scratch = P / "out" / case
    pkg = scratch / "pkg"
    loader = ProvisionalPackageLoader(package_dir=pkg, package_name=case, link_root=scratch / "link")
    module, _ = loader.load()
    registry = getattr(module, f"create_{case}_registry")()
    run = scratch / "run"
    if run.exists(): shutil.rmtree(run)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            execute_pipeline(pkg / "pipelines/pipeline.yaml", run, registry=registry, custom_schema_types=module.CUSTOM_SCHEMA_TYPES)
    except Exception as exc:
        return [f"RUN FAILED {type(exc).__name__}: {str(exc)[:300]}"]
    files = {f.relative_to(run).as_posix(): json.loads(f.read_text()) for f in run.rglob("*.json")}
    manifest = next((v for k, v in files.items() if k.endswith("manifest.json")), {})
    out = []
    for art in manifest.get("artifacts", []):
        rel = art["relative_path"]
        match = [v for k, v in files.items() if k.endswith(rel) or Path(k).stem == Path(rel).stem]
        out.append(f"{art['channel']}={match[0] if match else '<none>'}")
    return out

cases = sys.argv[1:] or sorted(p.name for p in (P / "out").iterdir())
for c in cases:
    pkg = P / "out" / c / "pkg"
    if not pkg.exists():
        print(f"== {c}: no package"); continue
    inputs = {}
    for f in sorted((pkg / "inputs").glob("*.json")):
        inputs.update(json.loads(f.read_text()))
    print(f"== {c}: inputs={json.dumps(inputs)}")
    for line in run_package(c):
        print("   ", line)
