"""SC12 parity: fusion-tea's original study tools against the moved ones, on the station fixture.

What this shows (spec SC12, design Appendix G). Run on the same inputs, the original tools
(fusion-tea ``b06585709``, staged) and the moved tools (``sysml_codegen.study``, installed from
a wheel) give equal exit codes and equal output documents, except in the fields the closed list
B1-B13 names. Each case runs three times: ``orig``, ``orig2`` (orig again) and ``moved``.

Every rule the comparison applies is written below as a constant or one small function, and
the report counts each application:

1. Exit codes must be equal.
2. Noise is normalized by the token patterns in ``patterns.json``, never by whole field. orig
   and orig2 must then be equal; any residue is unexplained noise and fails the case.
3. Closed-list values that are determined are mapped from orig to moved by a fixed table
   (``TOOL_PATHS``, ``CENSUS_PRODUCERS``, ``teax_detail_mapping``), only in the fields named.
4. Closed-list values that are content-derived are masked by token on both sides
   (``mask_content``), and read-coverage receipts are compared by ``receipt_view``: tool
   declarations as path sets with moved-only package files as B8 additions, tool reads by
   module, and the reads of modules only the moved driver preloads excluded as measured.
5. Everything else must be equal, every ``detail`` string included.
6. Library parity: four functions agree with the project root pinned (``library``).

README.md lists every rule with the decision that ratified it and its evidence.

Run it with the parity venv's interpreter; README.md gives the commands.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVIDENCE = Path(__file__).resolve().parent
DECLARATION = EVIDENCE.parent / "fusion-tea" / "declaration.toml"
MODES = ("orig", "orig2", "moved")

#: The originals as fusion-tea runs them, and the moved tools as a target runs them.
ORIG_SCRIPT = {
    "indicators": "scripts/study/indicators.py",
    "preflight": "scripts/study/preflight.py",
    "verify": "scripts/study/verify.py",
    "integrate": "scripts/integrate.py",
}
MOVED_MODULE = {tool: f"sysml_codegen.study.{tool}" for tool in ORIG_SCRIPT}

#: The orig environment's four wheel variables. Only fusion-tea's gate-1a suite reads their
#: values; the parity stand-in does not, and integrate's gate 0 only checks they are set.
WHEEL_DUMMIES = {
    name: "parity-dummy"
    for name in ("STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL",
                 "STOP_PARSER_CODEGEN_WHEEL", "STOP_PARSER_COSTINGFE_WHEEL")
}

#: Rule 3, B2: each original tool path and the installed path that replaces it.
TOOL_PATHS = {
    **{f"scripts/study/{name}.py": f"sysml_codegen/study/{name}.py"
       for name in ("common", "identity", "indicators", "manifest", "preflight",
                    "read_coverage", "verify")},
    "scripts/integrate.py": "sysml_codegen/study/integrate.py",
}
ORIG_SCHEMAS, MOVED_SCHEMAS = "scripts/study/schemas/", "sysml_codegen/study/schemas/"
#: Rule 3, B11: the census producers.
CENSUS_PRODUCERS = {
    "sysml_codegen.snapshot.capture; the spine census helper":
        "sysml_codegen.snapshot.capture; sysml_codegen/study/census.py",
    "tests/models/test_model_family_spines.py::_by_entry_type":
        "sysml_codegen/study/census.py::by_entry_type",
}
#: Rule 4, B2: digested files only the moved tools have.
B2_ADDITIONS = frozenset({"sysml_codegen/study/roots.py", "sysml_codegen/study/census.py",
                          "sysml_codegen/study/declarations.py"})
#: Rule 4, B8: gate 7's pass detail carries the receipt's dependency digest.
GATE7_DIGEST = re.compile(r"^(baseline Python read coverage )[0-9a-f]{64}( and )")
RECEIPT_SCHEMA = "baseline-read-coverage/v1"
RETURN_SCHEMA = "integration-seam-return/v1"

#: Deterministic commits, so a case's mutation commit has the same id in every run.
GIT = ("git", "-c", "user.name=parity", "-c", "user.email=parity@example.invalid",
       "-c", "commit.gpgsign=false")
GIT_DATES = {"GIT_AUTHOR_DATE": "2026-10-12T00:00:00+00:00",
             "GIT_COMMITTER_DATE": "2026-10-12T00:00:00+00:00"}


@dataclass(frozen=True)
class Paths:
    scratch: Path
    staged: Path
    fixture: Path
    teax: Path

    @property
    def project(self) -> Path:
        return self.scratch / "project"

    @property
    def out(self) -> Path:
        return self.scratch / "out"

    @property
    def runs(self) -> Path:
        return self.scratch / "runs"

    @property
    def simkit(self) -> Path:
        return self.teax / "packages" / "teax-simkit"

    @property
    def tool_home(self) -> Path:
        return self.scratch / "venv" / "lib" / "python3.12" / "site-packages"


# --------------------------------------------------------------------------- the layout


PINS_STAND_IN = '''"""Parity stand-in for fusion-tea's gate-1a producer.

Its path is fusion-tea's: tests/test_dependency_provenance.py.

Written for the SC12 parity layout. fusion-tea's suite compares pinned revisions and wheel
hashes this layout does not have, so the stand-in checks only that the toolchain imports.
"""
import importlib


def test_the_toolchain_imports():
    for name in ("sysml_codegen", "agentic_mbse", "simkit"):
        importlib.import_module(name)
'''

SPINE_STAND_IN = '''"""Parity stand-in for fusion-tea's gate-5 producer.

Its path is fusion-tea's: tests/models/test_model_family_spines.py.

Written for the SC12 parity layout. ``_contract`` and ``_by_entry_type`` are fusion-tea's
lines 174-182 at b06585709, verbatim: the original seam imports ``_by_entry_type`` from this
module for gate 4. The one test checks the tracked census against the committed package.
"""
from __future__ import annotations

import json
from pathlib import Path


{helpers}

PROJECT = Path(__file__).resolve().parents[2]


def test_the_tracked_census_is_the_committed_packages():
    tracked = json.loads((PROJECT / "census.json").read_text())
    by_type = _by_entry_type(PROJECT / "pkg" / "station_study")
    assert tracked["by_entry_type"] == {{key: sorted(value) for key, value in by_type.items()}}
'''

#: A route that reads a project file no route may read, then runs the station's (gate 7).
LEAKY_ROUTE = '''"""The station route, after reading a project file no route may read."""
from pathlib import Path

import study_route


def execute_baseline(out, *, package_dir, manifest_path):
    (Path(manifest_path).resolve().parents[1] / "census.json").read_text()
    return study_route.execute_baseline(out, package_dir=package_dir, manifest_path=manifest_path)
'''


def spine_helpers(staged: Path) -> str:
    """fusion-tea's ``_contract`` and ``_by_entry_type``: lines 174-182, checked by name."""
    lines = (staged / "tests/models/test_model_family_spines.py").read_text().splitlines()
    helpers = "\n".join(lines[173:182])
    if not (helpers.startswith("def _contract(") and "\ndef _by_entry_type(" in helpers):
        raise SystemExit("staged spine lines 174-182 are not _contract and _by_entry_type")
    return helpers


def git(project: Path, *argv: str) -> str:
    done = subprocess.run([*GIT, "-C", str(project), *argv], capture_output=True, text=True,
                          env={**os.environ, **GIT_DATES}, check=True)
    return done.stdout.strip()


def build_layout(paths: Paths) -> str:
    """``$S/project``: the fixture at its root, the originals, the stand-ins, the declaration.

    Returns the base commit every run resets to.
    """
    project = paths.project
    if project.exists():
        shutil.rmtree(project)
    shutil.copytree(paths.fixture, project, ignore=shutil.ignore_patterns("__pycache__"))
    scripts = project / "scripts"
    shutil.copytree(paths.staged / "scripts/study", scripts / "study",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(paths.staged / "scripts/integrate.py", scripts / "integrate.py")
    (project / "tests/models").mkdir(parents=True)
    (project / "tests/test_dependency_provenance.py").write_text(PINS_STAND_IN)
    (project / "tests/models/test_model_family_spines.py").write_text(
        SPINE_STAND_IN.format(helpers=spine_helpers(paths.staged)))
    shutil.copy2(DECLARATION, project / "pyproject.toml")
    (project / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n")
    git(project, "init", "-q")
    git(project, "add", ".")
    git(project, "commit", "-q", "-m", "parity layout")
    return git(project, "rev-parse", "HEAD")


def reset_project(paths: Paths, base: str) -> None:
    git(paths.project, "reset", "-q", "--hard", base)
    git(paths.project, "clean", "-q", "-fdx")


# ----------------------------------------------------------------------------- the runs


def environment(paths: Paths, mode: str, unset: tuple[str, ...]) -> dict[str, str]:
    """The environment of one run. Both modes share fusion-tea's variables: the four wheel
    dummies and ``STOP_PARSER_TEAX_ROOT``. Each mode adds one variable, a harness side of a
    closed-list item:

    - A ``uv`` shim first on ``PATH`` runs ``uv run X ...`` as ``X ...`` (B3).
    - moved: ``TEAX_SIMKIT_PATH``, its one teax root (B7).
    - orig: ``SYSML_CODEGEN_PROJECT_ROOT``, which no original tool reads. The fixture route
      imports the moved ``identity`` in both modes (design Appendix G), and its
      ``build_sealed`` needs a project root. The moved seam hands that root to its producers
      (B1, DD2), and the moved ``run_route`` pins it before observing (B1 refinement). The
      original seam and driver do neither, so without the variable ``roots`` would run
      ``git`` under observation and read coverage would refuse the child at gate 7.
    """
    env = {
        "PATH": f"{paths.scratch}/shim:{paths.scratch}/venv/bin:/usr/bin:/bin",
        "HOME": str(paths.scratch / "home"),
        "LC_ALL": "C.UTF-8",
        "TMPDIR": str(paths.scratch / "tmp"),
        "GIT_CONFIG_NOSYSTEM": "1",
        "SYSIDE_LICENSE_KEY": os.environ["SYSIDE_LICENSE_KEY"],
        **WHEEL_DUMMIES,
        "STOP_PARSER_TEAX_ROOT": str(paths.teax),
    }
    if mode == "moved":
        env["TEAX_SIMKIT_PATH"] = str(paths.simkit)
    else:
        env["SYSML_CODEGEN_PROJECT_ROOT"] = str(paths.project)
    for name in unset:
        del env[name]
    return env


def fresh(directory: Path) -> Path:
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    return directory


@dataclass(frozen=True)
class Case:
    name: str
    tool: str
    argv: tuple[str, ...]
    #: Edits the project before the run; committed unless ``commit`` is false.
    prepare: Callable[[Path], None] | None = None
    commit: bool = True
    unset: tuple[str, ...] = ()


def run_case(paths: Paths, base: str, case: Case, mode: str) -> None:
    """One run from the base commit; its exit code, stdio and ``out/`` land in ``runs/``."""
    reset_project(paths, base)
    if case.prepare is not None:
        case.prepare(paths.project)
        if case.commit:
            git(paths.project, "add", "-A")
            git(paths.project, "commit", "-q", "-m", case.name)
    fresh(paths.out)
    fresh(paths.scratch / "tmp")
    program = ([ORIG_SCRIPT[case.tool]] if mode != "moved" else ["-m", MOVED_MODULE[case.tool]])
    done = subprocess.run(
        [str(paths.scratch / "venv/bin/python"), *program, *case.argv],
        cwd=paths.project, env=environment(paths, mode, case.unset),
        capture_output=True, text=True,
    )
    dest = fresh(paths.runs / case.name / mode)
    (dest / "exit_code").write_text(f"{done.returncode}\n")
    (dest / "stdout").write_text(done.stdout)
    (dest / "stderr").write_text(done.stderr)
    shutil.move(str(paths.out), dest / "out")


# --------------------------------------------------------------------------- the cases


def edit(path: Path, old: str, new: str) -> None:
    """Replace ``old`` once in ``path``, refusing when it is absent: a no-op mutation would
    pass for a real one."""
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"mutation target not found exactly once in {path}: {old!r}")
    path.write_text(text.replace(old, new))


def edit_json(path: Path, mutate: Callable[[dict[str, Any]], object]) -> None:
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n")


def repin_to_zero(project: Path) -> None:
    edit_json(project / "studies/manifest.json",
              lambda m: m["fingerprints"]["indicator_inputs"].update(digest="0" * 64))


def stale_recorded_provenance(project: Path) -> None:
    edit_json(project / "studies/manifest.json",
              lambda m: m["fingerprints"]["recorded_provenance"].update(
                  semantic_fingerprint="0" * 64))


def dirty_package(project: Path) -> None:
    with (project / "pkg/station_study/inputs/station_params.json").open("a") as handle:
        handle.write("\n")


def skew_oracle(project: Path) -> None:
    exact = '* values[STATION + "energy_price"] * 1000.0'
    edit(project / "studies/oracle_entry.py", exact, exact + " * 1.000001")


def fail_pins_gate(project: Path) -> None:
    path = project / "tests/test_dependency_provenance.py"
    failure = '    raise AssertionError("parity: a pinned revision moved")\n'
    path.write_text(path.read_text() + failure)


def fail_spine_gate(project: Path) -> None:
    path = project / "tests/models/test_model_family_spines.py"
    failure = '    raise AssertionError("parity: the family twins differ")\n'
    path.write_text(path.read_text() + failure)


def move_generated_bytes(project: Path) -> None:
    path = project / "pkg/station_study/pipelines/pipeline.yaml"
    path.write_text(path.read_text() + "# parity: a byte regeneration rewrites\n")


def lose_handwritten(project: Path) -> None:
    (project / "pkg/station_study/handwritten/pumpstation/requiredflow_impl.py").unlink()


def stale_census(project: Path) -> None:
    edit_json(project / "census.json", lambda c: c.update(entry_points=c["entry_points"] + 1))


def census_without_fingerprint(project: Path) -> None:
    edit_json(project / "census.json", lambda c: c.pop("derived_against_semantic_fingerprint"))


def add_leaky_route(project: Path) -> None:
    (project / "studies/leaky_route.py").write_text(LEAKY_ROUTE)


def build_cases(paths: Paths) -> dict[str, Case]:
    """Appendix G's case list. Every path is relative to the project, which is the cwd."""
    recorded = json.loads((paths.fixture / "studies/manifest.json").read_text())
    lineage = recorded["fingerprints"]["recorded_provenance"]
    teax_head = git(paths.teax, "rev-parse", "HEAD")
    station = ("--package", "pkg/station_study", "--manifest", "studies/manifest.json")
    baseline = ("--identity", "studies/baseline/package_identity.json",
                "--baseline-result", "studies/baseline/baseline_result.json")
    verify = (*station, "--identity", "studies/baseline/package_identity.json",
              "--store", "../inputs/_work/station-grid-v1.db",
              "--out", "../out/verification_summary.json")
    request = {
        "--audited-work": "models@HEAD", "--models-root": "models",
        "--package": "pkg/station_study", "--manifest": "studies/manifest.json",
        "--groups": "studies/axes.json", "--census-file": "census.json",
        "--route-sys-path": "studies", "--route-module": "study_route",
        "--route-callable": "execute_baseline", "--out-dir": "../out",
        "--expected-teax-revision": teax_head,
        "--expected-semantic-fingerprint": lineage["semantic_fingerprint"],
        "--expected-executable-fingerprint": lineage["executable_fingerprint"],
    }

    def integrate(name: str, *, drop: tuple[str, ...] = (), **kwargs: Any) -> Case:
        overrides = kwargs.pop("set", {})
        flags = {flag: overrides.get(flag, value) for flag, value in request.items()
                 if flag not in drop}
        return Case(f"integrate-{name}", "integrate",
                    tuple(token for pair in flags.items() for token in pair), **kwargs)

    cases = [
        Case("indicators-complete", "indicators",
             (*station, "--groups", "studies/axes.json", "--out", "../out/indicators.json")),
        Case("indicators-pin-mismatch", "indicators",
             (*station, "--groups", "studies/axes.json", "--out", "../out/indicators.json"),
             prepare=repin_to_zero),
        Case("indicators-print-fingerprint", "indicators",
             ("--package", "pkg/station_study", "--print-fingerprint")),
        Case("preflight-gates-complete", "preflight",
             ("gates", *station, "--groups", "studies/axes.json", *baseline,
              "--out", "../out/preflight_results.json")),
        Case("preflight-gates-stale-manifest", "preflight",
             ("gates", *station, "--groups", "studies/axes.json", *baseline,
              "--out", "../out/preflight_results.json"), prepare=stale_recorded_provenance),
        Case("preflight-clean-clean", "preflight",
             ("clean", "--package", "pkg/station_study", "--out", "../out/preflight_clean.json")),
        Case("preflight-clean-dirty", "preflight",
             ("clean", "--package", "pkg/station_study", "--out", "../out/preflight_clean.json"),
             prepare=dirty_package, commit=False),
        Case("verify-complete", "verify", verify),
        Case("verify-oracle-mutated", "verify", verify, prepare=skew_oracle),
        integrate("g0-input-missing", drop=("--route-module",)),
        integrate("g0-input-invalid", set={"--audited-work": "models"}),
        integrate("g0-env-missing", unset=("STOP_PARSER_WHEEL_TARGET",)),
        integrate("g0-package-not-integrated", prepare=dirty_package, commit=False),
        integrate("g1a-refused", prepare=fail_pins_gate),
        integrate("g1b-unasked", drop=("--expected-teax-revision",)),
        integrate("g1b-refused", set={"--expected-teax-revision": "0000000000"}),
        integrate("g2-refused", prepare=move_generated_bytes),
        integrate("g3-handwritten-lost", prepare=lose_handwritten),
        integrate("g4-census-unasked", drop=("--census-file",)),
        integrate("g4-census-stale", prepare=stale_census),
        integrate("g5-refused", prepare=fail_spine_gate),
        integrate("g6-manifest-stale", prepare=repin_to_zero),
        integrate("g7-read-coverage-refused", prepare=add_leaky_route,
                  set={"--route-module": "leaky_route"}),
        integrate("g8-verification-refused", prepare=skew_oracle),
        integrate("g9-unasked", drop=("--expected-semantic-fingerprint",)),
        integrate("g9-lineage-mismatch", set={"--expected-executable-fingerprint": "0" * 64}),
        integrate("seam-internal-error", prepare=census_without_fingerprint),
        integrate("candidate"),
    ]
    return {case.name: case for case in cases}


# ------------------------------------------------------------- setup: preloads, inputs


def python(paths: Paths, source: str, *, cwd: Path, env: dict[str, str]) -> str:
    """Run ``source`` in a child interpreter of the parity venv; return its stdout."""
    done = subprocess.run([str(paths.scratch / "venv/bin/python"), "-c", source],
                          cwd=cwd, env=env, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"python -c failed:\n{source}\n{done.stderr}")
    return done.stdout


def in_child(paths: Paths, call: str, *, cwd: Path, env: dict[str, str]) -> Any:
    """Evaluate ``parity.<call>`` in a child interpreter and return its JSON result."""
    source = (f"import json, sys\nsys.path.insert(0, {str(EVIDENCE)!r})\nimport parity\n"
              f"print(json.dumps(parity.{call}, default=str))")
    return json.loads(python(paths, source, cwd=cwd, env=env))


#: What a gate-7 driver has imported when ``run_route`` starts observing. Both drivers begin
#: ``import json, sys`` (``ROUTE_DRIVER_SOURCE``), so this does that and nothing more.
DRIVER_MODULES = ("import json, sys\n"
                  "from {module} import run_route\n"
                  "print(json.dumps(sorted(sys.modules)))")
#: The modules that running one statement adds to a fresh interpreter.
CLOSURE = ("import json, sys\n"
           "before = set(sys.modules)\n"
           "{statement}\n"
           "print(json.dumps(sorted(set(sys.modules) - before)))")
#: What the moved observer does before observing that the original does not: import ``roots``
#: (B1), and read the interpreter's build-time ``TZPATH`` at import (B13, since audit F1).
PRELOAD_SOURCES = ("import sysml_codegen.study.roots",
                   "import sysconfig\nsysconfig.get_config_var('TZPATH')")


def module_files(names: list[str]) -> dict[str, dict[str, Any]]:
    """Each module's cached ``.pyc`` and whether it is the standard library's (child only)."""
    import importlib
    import sysconfig

    stdlib = sysconfig.get_path("stdlib") + "/"
    found = {}
    for name in names:
        module = importlib.import_module(name)
        origin = getattr(module.__spec__, "origin", None)
        found[name] = {
            "cached": getattr(module, "__cached__", None),
            "stdlib": (origin in ("built-in", "frozen")
                       or bool(origin and origin.startswith(stdlib))),
        }
    return found


def renamed_tool_module(name: str) -> str:
    """An original tool module's name after rule 3's ``TOOL_PATHS``; any other name as is."""
    path = TOOL_PATHS.get(name.replace(".", "/") + ".py")
    return path.removesuffix(".py").replace("/", ".") if path else name


def measure_preloads(paths: Paths) -> dict[str, Any]:
    """The modules the moved driver imports before observation that the original's does not.

    Parity excludes two groups among them, only where orig records the read as
    ``runtime-observed`` and moved does not record it at all:

    - The standard-library ``.pyc`` reads (spec B13 consequence), after checking each module
      is loaded by one of ``PRELOAD_SOURCES``: importing ``sysml_codegen.study.roots``, or
      reading the build-time ``TZPATH`` through ``sysconfig``.
    - The installed ``sysml_codegen`` modules (Q1 rule 3, a B1 and B8 consequence): the moved
      observer lives in the package the route imports. The original driver's own tool modules,
      renamed by rule 3's table, are not preloads: the moved driver loading
      ``sysml_codegen.study.read_coverage`` is the original loading ``scripts.study.read_coverage``.
    """
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(paths.project), "LC_ALL": "C.UTF-8"}

    def imported(module: str) -> set[str]:
        source = DRIVER_MODULES.format(module=module)
        return set(json.loads(python(paths, source, cwd=paths.project, env=env)))

    orig_driver = imported("scripts.study.read_coverage")
    preloaded = sorted(imported("sysml_codegen.study.read_coverage") - orig_driver)
    closure: set[str] = set()
    for statement in PRELOAD_SOURCES:
        source = CLOSURE.format(statement=statement)
        closure |= set(json.loads(python(paths, source, cwd=paths.scratch, env=env)))
    files = in_child(paths, f"module_files({preloaded!r})", cwd=paths.scratch, env=env)
    stdlib = {name: info["cached"] for name, info in sorted(files.items()) if info["stdlib"]}
    outside = sorted(set(stdlib) - closure)
    if outside:
        raise SystemExit(f"preloaded standard-library modules outside the roots/sysconfig "
                         f"closure: {outside}")
    not_stdlib = sorted(set(preloaded) - set(stdlib))
    counterparts = {renamed_tool_module(name) for name in orig_driver}
    package_modules = sorted(set(not_stdlib) - counterparts)
    strays = [name for name in package_modules
              if name != "sysml_codegen" and not name.startswith("sysml_codegen.")]
    if strays:
        raise SystemExit(f"preloaded modules outside the installed sysml_codegen package: {strays}")
    return {
        "preloaded_by_the_moved_driver": preloaded,
        "standard_library": stdlib,
        "not_standard_library": not_stdlib,
        "installed_package_modules": package_modules,
        "closure_check": "every standard-library module is loaded by importing "
                         "sysml_codegen.study.roots or by reading sysconfig's build-time TZPATH",
        "installed_package_check": "not_standard_library less the original driver's own tool "
                                   "modules renamed by TOOL_PATHS; every one is in the "
                                   "installed sysml_codegen package",
    }


ROUTE_GRID = ("import sys\n"
              "from pathlib import Path\n"
              "import study_route\n"
              "study_route.run_grid(Path(sys.argv[1]), package_dir=Path('pkg/station_study'))")


def shared_inputs(paths: Paths, base: str) -> None:
    """The grid store both ``verify`` runs read, from the fixture's own route, made once."""
    reset_project(paths, base)
    inputs = fresh(paths.scratch / "inputs")
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8", "HOME": str(paths.scratch / "home"),
           "PYTHONPATH": str(paths.project / "studies"),
           "SYSML_CODEGEN_PROJECT_ROOT": str(paths.project)}
    subprocess.run([str(paths.scratch / "venv/bin/python"), "-c", ROUTE_GRID, str(inputs)],
                   cwd=paths.project, env=env, check=True, capture_output=True)


def library(project: str) -> dict[str, Any]:
    """Rule 6 (child only): four functions, original against moved, the moved root pinned."""
    root = Path(project)
    sys.path.insert(0, project)
    import scripts.integrate as orig_integrate
    import scripts.study.identity as orig_identity
    import scripts.study.manifest as orig_manifest

    from sysml_codegen.study import identity, integrate, manifest, roots

    roots.use_project_root(root)
    package = root / "pkg/station_study"
    probes = [root, package, package / "contracts/model_contract.json",
              root.parent / "out/indicators.json"]
    pairs = {
        "indicator_input_fingerprint": (orig_manifest.indicator_input_fingerprint(package),
                                        manifest.indicator_input_fingerprint(package)),
        "build_sealed": (
            orig_identity.build_sealed(package_name="station_study", package_root=package),
            identity.build_sealed(package_name="station_study", package_root=package)),
        "repo_relative_posix": ([orig_manifest.repo_relative_posix(p) for p in probes],
                                [manifest.repo_relative_posix(p) for p in probes]),
        "rederived_census": (orig_integrate.rederived_census(package),
                             integrate.rederived_census(package)),
    }
    return {name: {"equal": orig == moved, "orig": orig, "moved": moved}
            for name, (orig, moved) in pairs.items()}


def check_environment(paths: Paths) -> dict[str, Any]:
    import agentic_mbse
    import simkit

    import sysml_codegen

    venv = paths.scratch / "venv"
    facts = {
        "python": sys.version.split()[0],
        "sys.prefix": sys.prefix,
        "sys.base_prefix": sys.base_prefix,
        "sysml_codegen": sysml_codegen.__file__,
        "agentic_mbse": agentic_mbse.__file__,
        "simkit": simkit.__file__,
        "SYSIDE_LICENSE_KEY": "set" if os.environ.get("SYSIDE_LICENSE_KEY") else "missing",
    }
    problems = [
        message for ok, message in (
            (Path(sys.prefix) == venv, f"run me with {venv}/bin/python"),
            (sys.base_prefix == "/usr", "the venv must be on /usr/bin/python3.12"),
            (Path(sysml_codegen.__file__).is_relative_to(venv), "sysml_codegen is not the wheel"),
            (Path(agentic_mbse.__file__).is_relative_to(venv), "agentic_mbse is not the wheel"),
            (Path(simkit.__file__).is_relative_to(paths.simkit), "simkit is not teax's"),
            (facts["SYSIDE_LICENSE_KEY"] == "set", "SYSIDE_LICENSE_KEY is not set"),
        ) if not ok
    ]
    if problems:
        raise SystemExit("; ".join(problems))
    return facts


def setup(paths: Paths) -> None:
    environment_facts = check_environment(paths)
    shim = fresh(paths.scratch / "shim") / "uv"
    shim.write_text('#!/bin/sh\n# B3, harness side: `uv run X ...` runs as `X ...`.\n'
                    '[ "$1" = run ] || { echo "uv shim: only uv run" >&2; exit 2; }\n'
                    'shift\nexec "$@"\n')
    shim.chmod(0o755)
    fresh(paths.scratch / "home")
    base = build_layout(paths)
    shared_inputs(paths, base)
    reset_project(paths, base)
    preloads = measure_preloads(paths)
    library_result = in_child(paths, f"library({str(paths.project)!r})", cwd=paths.scratch,
                              env={"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"})
    state = {"base": base, "environment": environment_facts, "preloads": preloads,
             "library": library_result,
             "sources": json.loads((paths.scratch / "wheels/sources.json").read_text())}
    (paths.scratch / "setup.json").write_text(json.dumps(state, indent=2) + "\n")
    (EVIDENCE / "preloads.json").write_text(json.dumps(preloads, indent=2) + "\n")


# ----------------------------------------------------------------------- normalization


@dataclass
class Patterns:
    """Rule 2: the declared noise patterns, with a count of every application."""

    rules: list[tuple[str, re.Pattern[str], str, str]]
    counts: Counter[str] = field(default_factory=Counter)

    @classmethod
    def load(cls, paths: Paths, token: str | None) -> Patterns:
        declared = json.loads((EVIDENCE / "patterns.json").read_text())["patterns"]
        # Two patterns name a run's own values: the scratch root, and the read-coverage token
        # the run minted. A run with no token gets a pattern that matches nothing.
        values = {"@SCRATCH@": re.escape(str(paths.scratch)),
                  "@TOKEN@": re.escape(token) if token else r"(?!x)x"}
        rules = []
        for p in declared:
            regex = p["regex"]
            for placeholder, value in values.items():
                regex = regex.replace(placeholder, value)
            rules.append((p["id"], re.compile(regex), p["replacement"], p["scope"]))
        return cls(rules)

    def apply(self, text: str, scope: str) -> str:
        for name, regex, replacement, applies in self.rules:
            if applies in ("all", scope):
                text, count = regex.subn(replacement, text)
                self.counts[name] += count
        return text


def run_token(run: Path) -> str | None:
    """The read-coverage token a run minted, read from its scratch directory's name."""
    prefix = "read-coverage-tmp-"
    found = [p.name.removeprefix(prefix) for p in (run / "out").glob(prefix + "*")]
    if len(found) > 1:
        raise SystemExit(f"{run}: more than one read-coverage scratch directory")
    return found[0] if found else None


def read_run(run: Path, patterns: Patterns) -> dict[str, Any]:
    """Every output of one run, normalized: exit code, stdio, and each file under ``out/``.

    teax's work area ``out/_work/`` holds its SQLite stores and package links; it is compared
    by file listing, and its bytes are not tool documents.
    """
    outputs: dict[str, Any] = {"exit_code": int((run / "exit_code").read_text())}
    for name in ("stdout", "stderr"):
        outputs[name] = parse(patterns.apply((run / name).read_text(), name))
    for path in sorted(p for p in (run / "out").rglob("*") if p.is_file()):
        relative = patterns.apply(path.relative_to(run / "out").as_posix(), "path")
        if relative.startswith("_work/"):
            outputs.setdefault("_work listing", []).append(relative)
            continue
        scope = "seam_traceback.txt" if path.name == "seam_traceback.txt" else path.suffix
        outputs[relative] = parse(patterns.apply(path.read_text(), scope))
    return outputs


def parse(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


# ------------------------------------------------------------------ closed-list rules


def map_tool_file(path: str) -> str:
    if path.startswith(ORIG_SCHEMAS):
        return MOVED_SCHEMAS + path.removeprefix(ORIG_SCHEMAS)
    return TOOL_PATHS.get(path, path)


def teax_detail_mapping(paths: Paths) -> tuple[str, str]:
    """Rule 3, B7: gate 1b names the simkit root ``TEAX_SIMKIT_PATH`` where the original named
    the checkout root ``STOP_PARSER_TEAX_ROOT``."""
    return (f"the teax checkout at {paths.teax} is not",
            f"the teax checkout at {paths.simkit} is not")


def seam_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """An integrate return's gate rows and its blocker; nothing for any other document."""
    if doc.get("schema_version") != RETURN_SCHEMA:
        return []
    return [*doc["gates"], *([doc["blocker"]] if doc["blocker"] else [])]


def map_determined(doc: dict[str, Any], paths: Paths, applied: Counter[str]) -> None:
    """Rule 3 on an orig document, in place: tool paths, producers, gate 1b's teax root."""
    def mapped(value: str, table: dict[str, str], rule: str) -> str:
        if value in table:
            applied[rule] += 1
            return table[value]
        return value

    producers = {**TOOL_PATHS, **CENSUS_PRODUCERS}
    if isinstance(doc.get("tool"), dict):
        doc["tool"]["path"] = mapped(doc["tool"]["path"], TOOL_PATHS, "B2 tool.path")
    if isinstance(doc.get("command"), list) and doc["command"]:
        doc["command"][0] = mapped(doc["command"][0], TOOL_PATHS, "B2 command[0]")
    old, new = teax_detail_mapping(paths)
    for row in seam_rows(doc):
        row["producer"] = mapped(row["producer"], producers, "B2/B11 producer")
        if row["gate"] == "teax-revision" and old in row["detail"]:
            row["detail"] = row["detail"].replace(old, new)
            applied["B7 gate 1b teax root"] += 1


def mask_content(doc: dict[str, Any], side: str, applied: Counter[str]) -> None:
    """Rule 4 on either side, in place: source digests, the receipt digest in gate 7's detail."""
    tool = doc.get("tool")
    if isinstance(tool, dict) and "source_digest" in tool:
        digest = tool["source_digest"]
        digest["digest"] = "<B2 source digest>"
        files = []
        for entry in digest["files"]:
            path = map_tool_file(entry["path"]) if side == "orig" else entry["path"]
            if side == "moved" and path in B2_ADDITIONS:
                applied[f"B2 addition {path}"] += 1
                continue
            if not path.endswith(".schema.json"):
                entry = {**entry, "sha256": "<B2 source bytes>"}
            files.append({**entry, "path": path})
        digest["files"] = files
        applied["B2 source digest"] += 1
    for row in seam_rows(doc):
        if row["gate"] == "preflight" and GATE7_DIGEST.match(row["detail"]):
            row["detail"] = GATE7_DIGEST.sub(r"\1<B8 dependency digest>\2", row["detail"])
            applied["B8 gate 7 detail digest"] += 1


def module_key(path: Path, site: Path) -> str:
    """The module a source or bytecode file under ``site`` loads; any other file's path.

    ``sysml_codegen/study/common.py`` and its ``__pycache__/common.cpython-312.pyc`` are both
    ``sysml_codegen.study.common``, and ``__init__`` names its package.
    """
    parts = list(path.relative_to(site).parts)
    if path.suffix == ".pyc" and len(parts) >= 2 and parts[-2] == "__pycache__":
        parts[-2:] = [parts[-1].split(".", 1)[0]]
    elif path.suffix == ".py":
        parts[-1] = path.stem
    else:
        return str(path)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def receipt_view(orig: dict[str, Any], moved: dict[str, Any], paths: Paths,
                 excluded: frozenset[str], package_modules: frozenset[str],
                 applied: Counter[str]) -> tuple[dict, dict]:
    """Rule 4 on a pair of read-coverage receipts: comparable views of each.

    Tool code is orig's ``$S/project/scripts/``, mapped by rule 3's table, and the installed
    package ``TOOL_HOME/sysml_codegen/``, which the route imports in both modes.

    - ``dependency_digest`` is masked (B8).
    - Declarations of tool code are compared as path sets; category and sha256 are free (B8,
      B2). Every orig one must be in moved. Moved-only ones under the installed package are B8
      additions (Q1 rule 1): the original already permitted reads of the installed package, as
      ``runtime-observed`` under the venv prefix, and the moved observer declares the same files
      with digests. The permission is the same; the receipt records more.
    - Reads of tool code are compared by module, category and sha256 free (Q1 rule 2, B8). orig
      reads the installed package's bytecode as runtime; moved reads its source and bytecode as
      declared. A file that is no module keeps its sha256.
    - orig's reads of modules only the moved driver preloads are dropped where moved does not
      record them: the measured standard-library ``.pyc`` files (spec B13 consequence), and the
      measured installed-package modules (Q1 rule 3), each only when orig read it as runtime.
    - Every other entry is compared whole: path, category and sha256.
    """
    # The receipts are already normalized, so the roots are named as rule 2 renders them.
    scratch = Path("<S>")
    orig_scripts = scratch / paths.project.relative_to(paths.scratch) / "scripts"
    site = scratch / paths.tool_home.relative_to(paths.scratch)
    package = site / "sysml_codegen"

    def tool_code(path: str, side: str) -> Path | None:
        candidate = Path(path)
        if side == "orig" and candidate.is_relative_to(orig_scripts):
            # scripts/study/<x> and scripts/<integrate> both land in sysml_codegen/study/.
            relative = candidate.relative_to(orig_scripts).as_posix().removeprefix("study/")
            return package / "study" / relative
        return candidate if candidate.is_relative_to(package) else None

    moved_reads = {row["path"] for row in moved["reads"]}
    moved_modules = {module_key(code, site) for row in moved["reads"]
                     if (code := tool_code(row["path"], "moved")) is not None}
    sides = {}
    for side, receipt in (("orig", orig), ("moved", moved)):
        view = {k: v for k, v in receipt.items() if k not in ("reads", "declarations")}
        view["dependency_digest"] = "<B8 dependency digest>"
        declared, declared_elsewhere = set(), {}
        for row in receipt["declarations"]:
            code = tool_code(row["path"], side)
            if code is not None:
                declared.add(str(code))
            else:
                declared_elsewhere[row["path"]] = [row["category"], row["sha256"]]
        modules: dict[str, str] = {}
        categories: dict[str, set[str]] = {}
        read_elsewhere = {}
        for row in receipt["reads"]:
            code = tool_code(row["path"], side)
            if code is not None:
                key = module_key(code, site)
                modules[key] = row["sha256"] if key == str(code) else "<B8 category, B2 bytes>"
                categories.setdefault(key, set()).add(row["category"])
                applied["B8 installed-package read, by module"] += 1
            elif (side == "orig" and row["path"] in excluded
                  and row["category"] == "runtime-observed" and row["path"] not in moved_reads):
                applied["B13 preloaded standard-library read"] += 1
            else:
                read_elsewhere[row["path"]] = [row["category"], row["sha256"]]
        if side == "orig":
            for key in sorted((package_modules & set(modules)) - moved_modules):
                if categories[key] == {"runtime-observed"}:
                    del modules[key]
                    applied["B1/B8 preloaded installed-package module"] += 1
        view["reads elsewhere"] = read_elsewhere
        view["declarations elsewhere"] = declared_elsewhere
        sides[side] = (view, declared, modules)
    orig_view, orig_declared, orig_modules = sides["orig"]
    moved_view, moved_declared, moved_modules_view = sides["moved"]
    additions = moved_declared - orig_declared
    applied["B8 installed-package declaration addition"] += len(additions)
    orig_view["declarations of tool code"] = sorted(orig_declared)
    moved_view["declarations of tool code"] = sorted(moved_declared - additions)
    orig_view["reads of tool code, by module"] = dict(sorted(orig_modules.items()))
    moved_view["reads of tool code, by module"] = dict(sorted(moved_modules_view.items()))
    applied["B8 receipt"] += 1
    return orig_view, moved_view


def differences(orig: Any, moved: Any, where: str = "") -> list[str]:
    """Every place two normalized values differ, as JSON-ish paths."""
    if isinstance(orig, dict) and isinstance(moved, dict):
        found = []
        for key in sorted(set(orig) | set(moved), key=str):
            if key not in orig:
                found.append(f"{where}/{key}: only in moved")
            elif key not in moved:
                found.append(f"{where}/{key}: only in orig")
            else:
                found += differences(orig[key], moved[key], f"{where}/{key}")
        return found
    if isinstance(orig, list) and isinstance(moved, list) and len(orig) == len(moved):
        return [found for i, (a, b) in enumerate(zip(orig, moved, strict=True))
                for found in differences(a, b, f"{where}[{i}]")]
    if orig != moved:
        return [f"{where}: orig {short(orig)} != moved {short(moved)}"]
    return []


def short(value: Any) -> str:
    text = json.dumps(value) if not isinstance(value, str) else repr(value)
    return text if len(text) <= 400 else text[:400] + "..."


def human_summary_holds(outputs: dict[str, Any]) -> bool:
    """integrate's stderr is the human summary of its own return, and nothing else."""
    from sysml_codegen.study.integrate import human_summary

    document = outputs.get("integration_return.json", outputs["stdout"])
    return isinstance(document, dict) and outputs["stderr"] == human_summary(document) + "\n"


# --------------------------------------------------------------------------- comparing


def compare_case(paths: Paths, case: str, excluded: frozenset[str],
                 package_modules: frozenset[str]) -> dict[str, Any]:
    runs = {mode: paths.runs / case / mode for mode in MODES}
    patterns = {mode: Patterns.load(paths, run_token(run)) for mode, run in runs.items()}
    outputs = {mode: read_run(run, patterns[mode]) for mode, run in runs.items()}
    result: dict[str, Any] = {"case": case,
                              "exit_codes": {m: outputs[m]["exit_code"] for m in MODES}}
    noise = differences(outputs["orig"], outputs["orig2"])
    applied: Counter[str] = Counter()
    # integrate's stderr renders its return. When every run's does exactly that, comparing the
    # returns compares the stderr too; otherwise stderr is compared like any other output.
    if case.startswith("integrate-") and all(human_summary_holds(outputs[m]) for m in MODES):
        for mode in MODES:
            outputs[mode]["stderr"] = "<the human summary of the return, checked>"
    orig, moved = copy.deepcopy(outputs["orig"]), copy.deepcopy(outputs["moved"])
    for name in sorted(set(orig) & set(moved)):
        if isinstance(orig[name], dict) and isinstance(moved[name], dict):
            if orig[name].get("schema_version") == RECEIPT_SCHEMA:
                orig[name], moved[name] = receipt_view(orig[name], moved[name], paths,
                                                       excluded, package_modules, applied)
                continue
            map_determined(orig[name], paths, applied)
            mask_content(orig[name], "orig", applied)
            mask_content(moved[name], "moved", applied)
    found = differences(orig, moved)
    for document in (moved.get("integration_return.json"), moved.get("stdout")):
        if isinstance(document, dict) and document.get("schema_version") == RETURN_SCHEMA:
            found += declared_rows_hold(document)
    result.update(
        noise=noise, differences=found, closed_list=dict(sorted(applied.items())),
        patterns={mode: dict(sorted((+patterns[mode].counts).items())) for mode in MODES},
        status=("NOISE" if noise else "DIFFERENT" if found
                else f"EQUAL after closed-list fields {closed_list_ids(applied)}" if applied
                else "EQUAL"),
    )
    return result


def declared_rows_hold(document: dict[str, Any]) -> list[str]:
    """Rule 3, B5 and B12: rows 1a and 5 state the declaration's target and checked text."""
    import tomllib

    table = tomllib.loads(DECLARATION.read_text())["tool"]["sysml-codegen"]["integrate"]["gates"]
    problems = []
    for row in document["gates"]:
        declared = table.get(row["gate"])
        stated = (row["producer"], row["checked"])
        if declared and stated != (declared["target"], declared["checked"]):
            problems.append(f"row {row['gate']} does not state the declared target and checked")
    return problems


def evidence_copy(outputs: dict[str, Any]) -> dict[str, Any]:
    """One run's normalized outputs as committed: a receipt and the recaptured snapshot are
    summarized, because their full bytes (about 800 kB and 17 kB) stay in the scratch runs."""
    copied = dict(outputs)
    for name, value in outputs.items():
        if isinstance(value, dict) and value.get("schema_version") == RECEIPT_SCHEMA:
            copied[name] = {k: v for k, v in value.items() if k not in ("reads", "declarations")}
            for key in ("reads", "declarations"):
                counts = Counter(row["category"] for row in value[key])
                copied[name][f"{key} by category"] = dict(sorted(counts.items()))
        elif name.endswith(".snapshot.json"):
            text = json.dumps(value, sort_keys=True)
            copied[name] = f"<{len(text)} characters of JSON; compared in full by comparison.json>"
    return copied


def closed_list_ids(applied: Counter[str]) -> str:
    ids = sorted({bid for rule in applied for bid in re.findall(r"B\d+", rule)},
                 key=lambda b: int(b[1:]))
    return "[" + ", ".join(ids) + "]"


# ----------------------------------------------------------------------------- report


def report(paths: Paths, cases: dict[str, Case]) -> int:
    state = json.loads((paths.scratch / "setup.json").read_text())
    excluded = frozenset(str(Path(path).resolve())
                         for path in state["preloads"]["standard_library"].values() if path)
    package_modules = frozenset(state["preloads"]["installed_package_modules"])
    results = []
    for name in cases:
        if not (paths.runs / name).is_dir():
            results.append({"case": name, "status": "NOT RUN"})
            continue
        result = compare_case(paths, name, excluded, package_modules)
        results.append(result)
        dest = fresh(EVIDENCE / "cases" / name)
        (dest / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
        for mode in ("orig", "moved"):
            run = paths.runs / name / mode
            outputs = evidence_copy(read_run(run, Patterns.load(paths, run_token(run))))
            (dest / f"{mode}.json").write_text(json.dumps(outputs, indent=2) + "\n")
    library_ok = all(entry["equal"] for entry in state["library"].values())
    (EVIDENCE / "results.json").write_text(json.dumps(
        {"setup": state, "library_parity_holds": library_ok, "cases": results}, indent=2) + "\n")
    lines = ["# SC12 parity report", "",
             f"Generated by `parity.py` from `{paths.scratch}`. See README.md for the method and "
             f"`cases/<case>/comparison.json` for every difference and count.", "",
             "## Sources", ""]
    for name, source in state["sources"].items():
        lines.append(f"- {name}: " + ", ".join(f"{k} `{v}`" for k, v in source.items()))
    lines += ["", "## Environment", ""]
    lines += [f"- {k}: `{v}`" for k, v in state["environment"].items()]
    lines += ["", "## Library parity (rule 6)", ""]
    lines += [f"- `{name}`: {'equal' if entry['equal'] else 'DIFFERENT'}"
              for name, entry in state["library"].items()]
    lines += ["", "## Cases", "",
              "| Case | Exit (orig/orig2/moved) | Status | Closed-list applications |",
              "|---|---|---|---|"]
    for result in results:
        codes = "/".join(str(result.get("exit_codes", {}).get(m, "-")) for m in MODES)
        applied = ", ".join(f"{k} ×{v}" for k, v in result.get("closed_list", {}).items())
        lines.append(f"| {result['case']} | {codes} | {result['status']} | {applied} |")
    lines += ["", "## Pattern applications (rule 2), summed over the three runs of every case", ""]
    totals: Counter[str] = Counter()
    for result in results:
        for counts in result.get("patterns", {}).values():
            totals.update(counts)
    lines += [f"- `{k}`: {v}" for k, v in sorted(totals.items())]
    lines += ["", "## Differences", ""]
    for result in results:
        for kind in ("noise", "differences"):
            for entry in result.get(kind, []):
                lines.append(f"- {result['case']} ({kind}): {entry}")
    (EVIDENCE / "report.md").write_text("\n".join(lines) + "\n")
    failing = [r["case"] for r in results if not r["status"].startswith("EQUAL")]
    print("\n".join(lines[lines.index("## Cases"):]))
    return 1 if failing or not library_ok else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    for flag in ("--scratch", "--staged", "--fixture", "--teax"):
        parser.add_argument(flag, type=Path, required=True)
    parser.add_argument("step", choices=("all", "setup", "run", "report"))
    parser.add_argument("cases", nargs="*", help="with run: the cases to run (default: all)")
    args = parser.parse_args()
    paths = Paths(args.scratch.resolve(), args.staged.resolve(), args.fixture.resolve(),
                  args.teax.resolve())
    cases = build_cases(paths)
    if args.step in ("all", "setup"):
        setup(paths)
    if args.step in ("all", "run"):
        base = json.loads((paths.scratch / "setup.json").read_text())["base"]
        unknown = sorted(set(args.cases) - set(cases))
        if unknown:
            raise SystemExit(f"unknown cases: {unknown}")
        for name in args.cases or list(cases):
            for mode in MODES:
                run_case(paths, base, cases[name], mode)
            print(f"ran {name}", flush=True)
    if args.step in ("all", "report"):
        return report(paths, cases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
