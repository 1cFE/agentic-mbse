"""The generated (sysml-codegen + TEAx) side of the positional-binding counterexample (spec XR-2).

    uv run python .project/active/positional-binding-check/evidence/cross-route/eval_generated.py

Runs `sysml_codegen generate` on the two retained generator fixtures,
`tests/fixtures/positional_binding/native_values/gen_byname/` (inputs written by name) and
`gen_reversed/` (`in b = small; in a = big;`), then loads each generated package and runs its
pipeline through real TEAx, as the prototype's `04-eval.py` did. Natively the two give 7 and -7
(`tests/test_validation/test_positional_binding_native_values.py`); this records what the
generated route gives.

Pinned revisions: sysml-codegen `b5663c07`, TEAx `8d877460`. Both are exported with
`git archive` into a temp directory and put first on the child's import path; the child asserts
`sysml_codegen` and `simkit` resolve inside the exports. The interpreter is dc3's venv, which
has SysIDE and the generator's dependencies. Nothing is written in either checkout (bytecode
writing is off and every working directory is the temp directory); their status is compared
before and after. Writes `eval_generated.log` beside this file.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
FIXTURES = REPO_ROOT / "tests/fixtures/positional_binding/native_values"
LOG = HERE / "eval_generated.log"
INTERPRETER = Path("/home/reid/src/dc3/.venv/bin/python")
CODEGEN = Path("/home/reid/src/sysml-codegen")
TEAX = Path("/home/reid/src/teax")
CODEGEN_REV = "b5663c07"
TEAX_REV = "8d877460"
EXPECTED_INTENT = 7.0


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def state(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD") + "\n" + git(repo, "status", "--porcelain=v1")


def export(repo: Path, rev: str, dest: Path, *paths: str) -> str:
    full = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}")
    dest.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "-C", str(repo), "archive", full, *paths], check=True, capture_output=True
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive, check=True)
    return full


def license_key() -> str:
    from dotenv import dotenv_values

    key = dotenv_values(REPO_ROOT / ".env").get("SYSIDE_LICENSE_KEY")
    if not key:
        raise SystemExit(f"SYSIDE_LICENSE_KEY is missing from {REPO_ROOT / '.env'}")
    return key


def parent() -> int:
    if not INTERPRETER.exists():
        LOG.write_text(f"dc3 venv interpreter not found at {INTERPRETER}; XR-2 not run\n")
        print(LOG.read_text())
        return 1
    before = {repo: state(repo) for repo in (CODEGEN, TEAX)}
    with tempfile.TemporaryDirectory(prefix="positional-cross-route-") as tmp:
        scratch = Path(tmp)
        codegen_rev = export(CODEGEN, CODEGEN_REV, scratch / "sysml-codegen", "src")
        teax_rev = export(TEAX, TEAX_REV, scratch / "teax", "packages/teax-simkit")
        codegen_src = scratch / "sysml-codegen" / "src"
        simkit_src = scratch / "teax" / "packages" / "teax-simkit"
        env = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join([str(codegen_src), str(simkit_src)]),
            "PYTHONDONTWRITEBYTECODE": "1",
            "SYSIDE_LICENSE_KEY": license_key(),
        }
        child = subprocess.run(
            [str(INTERPRETER), str(Path(__file__).resolve()), "--child", str(scratch)],
            capture_output=True,
            text=True,
            env=env,
            cwd=scratch,
        )
    after = {repo: state(repo) for repo in (CODEGEN, TEAX)}
    unchanged = all(before[repo] == after[repo] for repo in before)
    header = [
        f"sysml-codegen {codegen_rev} (exported; checkout HEAD {before[CODEGEN].splitlines()[0]})",
        f"TEAx {teax_rev} (exported packages/teax-simkit; checkout HEAD {before[TEAX].splitlines()[0]})",
        f"interpreter {INTERPRETER}",
        f"checkouts unchanged after the run: {unchanged}",
        "",
    ]
    LOG.write_text(
        "\n".join(header) + child.stdout + (child.stderr[-4000:] if child.returncode else "")
    )
    print(LOG.read_text())
    return 0 if child.returncode == 0 and unchanged else 1


def child(scratch: Path) -> int:
    import simkit
    import syside
    import sysml_codegen
    import yaml
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    for module in (sysml_codegen, simkit):
        resolved = Path(module.__file__ or "").resolve()
        if not resolved.is_relative_to(scratch.resolve()):
            raise SystemExit(f"{module.__name__} resolved to {resolved}, outside the export")
        print(f"{module.__name__} from {resolved.relative_to(scratch.resolve())}")
    print(f"syside {syside.__version__}; python {sys.version.split()[0]}")
    print(
        "calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }; big = 10, small = 3"
    )
    print()
    for case in ("byname", "reversed"):
        name = f"gen_{case}"
        out = scratch / f"out_{case}"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "sysml_codegen",
                "generate",
                "--models",
                str(FIXTURES / name),
                "--output",
                str(out),
                "--package-name",
                name,
            ],
            capture_output=True,
            text=True,
            cwd=scratch,
        )
        if proc.returncode != 0:
            print(f"{name}: generate failed\n{proc.stdout[-2000:]}{proc.stderr[-2000:]}")
            return 1
        spec = yaml.safe_load((out / "pipelines/pipeline.yaml").read_text())
        [module_key] = [k for k in spec["modules"] if k.endswith("__plant__diff")]
        wiring = spec["modules"][module_key]["inputs"]
        run_root = scratch / f"run_{case}"
        loader = ProvisionalPackageLoader(
            package_dir=out, package_name=name, link_root=run_root / "link"
        )
        module, _fingerprint = loader.load()
        registry = getattr(module, f"create_{name}_registry")()
        execute_pipeline(
            out / "pipelines/pipeline.yaml",
            run_root / "run",
            registry=registry,
            custom_schema_types=module.CUSTOM_SCHEMA_TYPES,
        )
        [result_file] = list((run_root / "run").rglob("plant__result.json"))
        value = float(json.loads(result_file.read_text()))
        print(f"{name:13} wiring {json.dumps(wiring, sort_keys=True)}")
        print(
            f"{name:13} generated plant.result = {value}  matches intent {value == EXPECTED_INTENT}"
        )
        shutil.rmtree(run_root / "link", ignore_errors=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        sys.exit(child(Path(sys.argv[2])))
    sys.exit(parent())
