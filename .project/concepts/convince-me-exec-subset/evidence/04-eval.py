"""Claim 4, part 1: what value does each binding spelling produce, natively and generated?

Native: SysIDE Compiler.evaluate_feature on `a - b` for four spellings of the same
calc usage (a = 10, b = 3, so the intended answer is 7).

Generated: sysml-codegen `generate` on two part-hosted fixtures (by-name and the
reversed unprefixed form), then the sealed package is loaded and its pipeline run
through real TEAx (simkit), exactly as sysml-codegen tests/execution/real_teax.py does.

Run with an interpreter that has syside, sysml-codegen and teax-simkit installed
(dc3's venv provides all three as editable sibling checkouts):
    /home/reid/src/dc3/.venv/bin/python -I 04-eval.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import syside

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "04-fixtures"
SCRATCH = Path(
    "/tmp/claude-1000/-home-reid-src-agentic-mbse/"
    "8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c4"
)
CODEGEN = Path("/home/reid/src/sysml-codegen")

CALC_DEF = (
    "calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }"
)

SPELLINGS = {
    "in-order unprefixed": "in a = 10; in b = 3;",
    "reversed unprefixed": "in b = 3; in a = 10;",
    "reversed explicit :>>": "in :>> b = 3; in :>> a = 10;",
    "explicit rename (local redefines a)": "in local redefines a = 10; in b = 3;",
}
EXPECTED_INTENT = 7


def native_value(body: str) -> float:
    src = (
        "package P { private import ScalarValues::*; "
        f"{CALC_DEF} part q {{ calc c : Sub {{ {body} }} attribute v : Real = c.r; }} }}"
    )
    model, _ = syside.load_model(sysml_source=src)
    q = next(p for p in model.nodes(syside.PartUsage) if p.name == "q")
    v = next(f for f in q.owned_features.collect() if f.name == "v")
    value, report = syside.Compiler().evaluate_feature(v, scope=q, stdlib=model.lib)
    assert report, f"evaluation report failed for {body!r}"
    return value


def generated_value(case: str) -> tuple[float, dict[str, str]]:
    name = f"gen_{case}"
    out = SCRATCH / f"out_{case}"
    shutil.rmtree(out, ignore_errors=True)
    proc = subprocess.run(
        [
            sys.executable, "-m", "sysml_codegen", "generate",
            "--models", str(FIXTURES / name),
            "--output", str(out),
            "--package-name", name,
        ],
        capture_output=True, text=True, cwd=CODEGEN,
    )
    (SCRATCH / f"generate_{case}.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"generate failed for {case}: {proc.stderr[-2000:]}")

    import yaml
    spec = yaml.safe_load((out / "pipelines/pipeline.yaml").read_text())
    [module_key] = [k for k in spec["modules"] if k.endswith("__plant__diff")]
    wiring = spec["modules"][module_key]["inputs"]

    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    run_root = SCRATCH / f"run_{case}"
    shutil.rmtree(run_root, ignore_errors=True)
    loader = ProvisionalPackageLoader(
        package_dir=out, package_name=name, link_root=run_root / "link"
    )
    module, _fingerprint = loader.load()
    registry = getattr(module, f"create_{name}_registry")()
    result = execute_pipeline(
        out / "pipelines/pipeline.yaml", run_root / "run",
        registry=registry, custom_schema_types=module.CUSTOM_SCHEMA_TYPES,
    )
    [result_file] = list((run_root / "run").rglob("plant__result.json"))
    value = json.loads(result_file.read_text())
    del result
    return float(value), wiring


def main() -> int:
    print(f"syside {syside.__version__}; python {sys.executable}")
    print(f"calc def: {CALC_DEF}  (a = 10, b = 3; intended a - b = {EXPECTED_INTENT})\n")
    print("== Native (SysIDE Compiler.evaluate_feature) ==")
    print(f"{'spelling':40} {'body':38} {'value':>6}  matches intent")
    for label, body in SPELLINGS.items():
        value = native_value(body)
        print(f"{label:40} {body:38} {value:>6}  {value == EXPECTED_INTENT}")

    print("\n== Native, on the generator fixtures themselves (attribute result) ==")
    for case in ("byname", "reversed"):
        model, _ = syside.load_model([FIXTURES / f"gen_{case}" / "model.sysml"])
        plant = next(p for p in model.nodes(syside.PartUsage) if p.name == "plant")
        result = next(f for f in plant.inherited_features.collect() if f.name == "result")
        value, report = syside.Compiler().evaluate_feature(
            result, scope=plant, stdlib=model.lib
        )
        print(f"gen_{case:10} native plant.result = {value}")

    print("\n== Generated (sysml-codegen generate -> sealed load -> TEAx execute_pipeline) ==")
    for case in ("byname", "reversed"):
        value, wiring = generated_value(case)
        print(f"gen_{case:10} wiring {wiring}")
        print(f"gen_{case:10} generated plant.result = {value}  matches intent {value == EXPECTED_INTENT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
