"""Hold the occurrence port to sysml-codegen: capture oracle expectations, compare, run controls.

    uv run python scripts/subset_profile/occurrence_parity.py capture (CASE... | --all) [--agentic-rev REV]
    uv run python scripts/subset_profile/occurrence_parity.py compare --all [--agentic-rev REV]
    uv run python scripts/subset_profile/occurrence_parity.py controls

Promoted from spike F1 (`oracle.py`, `compare.py`, `run_all.sh`, `mutants.py`, `controls.sh`).

- `capture` builds an isolated tree (the `probe.py` pattern: `git archive` of codegen at the pin
  and of agentic-mbse at REV, `uv sync --frozen`), runs codegen's own oracle
  (`occurrence_oracle.py`) on each parity-seed case and writes its `expected.json`. An
  expectation is only ever written by this command.
- `compare --all` runs the oracle and the exported port (`occurrence_port_run.py`) side by side
  in one tree on the recorded F1 run: the 34 parity-seed cases (11 F1 edge fixtures, 22
  prototype fixtures, the P-6 fixture), all 37 codegen corpus fixtures and both dc3 trees. It
  also checks that each stored `expected.json` still equals today's oracle. Log:
  `evidence/occurrence-parity.log`.
- `controls` runs the F1 mutant ports against the stored seed expectations, in this checkout,
  with no codegen. Each catchable mutant must be flagged by at least one case. Log:
  `evidence/occurrence-parity-controls.log`.

The sibling checkouts are only read with `git archive`; a run fails if either one's HEAD or
status changes.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from probe import (  # noqa: E402  (this directory is on sys.path when the script runs)
    IsolationBreachError,
    build_tree,
    child_env,
    export_tree,
    read_identity,
    read_license_key,
    resolve_rev,
    sibling_state,
)

from tests.helpers.occurrence_oracle_schema import (  # noqa: E402
    schema_differences,
    strip_oracle_only_fields,
    to_oracle_schema,
)
from tests.helpers.subset_probe_judge import PINNED_CODEGEN_REV  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED_DIR = REPO_ROOT / "tests" / "fixtures" / "subset_profile" / "occurrence"
EVIDENCE = REPO_ROOT / ".project" / "completed" / "20261018_exec-subset-profile" / "evidence"
DC3_PINS = {"dc3_baseline": "808464df", "dc3_repaired": "60b44d53"}
CASE_TIMEOUT_S = 900


def seed_cases() -> list[Path]:
    return sorted(d for d in SEED_DIR.iterdir() if d.is_dir())


def case_models(case: Path) -> list[Path]:
    models = sorted(case.glob("*.sysml"))
    if not models:
        raise SystemExit(f"{case} has no .sysml model")
    return models


@contextmanager
def isolated_tree(
    tmp_root: Path, agentic_rev: str, codegen_repo: Path, dc3_repo: Path
) -> Iterator[tuple[Path, Path, dict[str, str], dict[str, Any]]]:
    """Yield (tree, python, env, identity) and check both sibling checkouts are untouched."""
    agentic = resolve_rev(REPO_ROOT, agentic_rev)
    codegen = resolve_rev(codegen_repo, PINNED_CODEGEN_REV)
    tmp_root.mkdir(parents=True, exist_ok=True)
    tree = Path(tempfile.mkdtemp(prefix="parity-", dir=tmp_root)).resolve()
    for checkout in (codegen_repo, dc3_repo, REPO_ROOT):
        if tree.is_relative_to(checkout):
            raise IsolationBreachError(f"temp tree {tree} is inside the checkout {checkout}")
    before = {repo: sibling_state(repo) for repo in (codegen_repo, dc3_repo)}
    env = child_env(read_license_key())
    python = build_tree(tree, codegen_repo, codegen, agentic, env)
    identity = vars(read_identity(tree, python, env, codegen, agentic))
    print(f"tree {tree}\nidentity {json.dumps(identity)}")
    yield tree, python, env, identity
    for repo, state in before.items():
        if sibling_state(repo) != state:
            raise IsolationBreachError(f"{repo} changed during the run")
    shutil.rmtree(tree)


def run_in_tree(
    tree: Path, python: Path, env: dict[str, str], script: str, out: Path, *args: str
) -> dict[str, Any]:
    argv = [str(python), "-I", str(HERE / script), *args]
    done = subprocess.run(
        argv, cwd=tree, env=env, capture_output=True, text=True, timeout=CASE_TIMEOUT_S
    )
    if done.returncode != 0 or not out.exists():
        raise SystemExit(f"{script} failed ({done.returncode}):\n{done.stdout}\n{done.stderr}")
    data: dict[str, Any] = json.loads(out.read_text())
    return data


def oracle(
    tree: Path, python: Path, env: dict[str, str], name: str, models: list[Path]
) -> dict[str, Any]:
    out = tree / "results" / f"{name}.oracle.json"
    out.parent.mkdir(exist_ok=True)
    data = run_in_tree(tree, python, env, "occurrence_oracle.py", out, str(out), *map(str, models))
    data["inputs"] = [str(Path(p).relative_to(tree)) for p in data["inputs"]]
    return data


def port(
    tree: Path, python: Path, env: dict[str, str], name: str, models: list[Path]
) -> dict[str, Any]:
    out = tree / "results" / f"{name}.port.json"
    out.parent.mkdir(exist_ok=True)
    return run_in_tree(
        tree,
        python,
        env,
        "occurrence_port_run.py",
        out,
        str(tree / "agentic-mbse"),
        str(out),
        *map(str, models),
    )


def copy_case(tree: Path, case: Path) -> list[Path]:
    dest = tree / "cases" / case.name
    dest.mkdir(parents=True)
    return [Path(shutil.copy(model, dest / model.name)) for model in case_models(case)]


def capture(args: argparse.Namespace) -> int:
    cases = seed_cases() if args.all else [SEED_DIR / name for name in args.cases]
    with isolated_tree(args.tmp_root, args.agentic_rev, args.codegen_repo, args.dc3_repo) as (
        tree,
        python,
        env,
        identity,
    ):
        for case in cases:
            data = oracle(tree, python, env, case.name, copy_case(tree, case))
            if "oracle_crash" in data:
                raise SystemExit(
                    f"oracle crashed on {case.name}; no expectation written:\n{data['oracle_crash']}"
                )
            strip_oracle_only_fields(data)  # refuses an incomplete capture before it is written
            data["identity"] = {k: v for k, v in identity.items() if k != "tree_root"}
            (case / "expected.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
            print(f"captured {case.name}")
    return 0


def recorded_run(tree: Path, dc3_repo: Path) -> list[tuple[str, list[Path], Path | None]]:
    """(name, model paths, stored expectation or None) for every case of the recorded F1 run."""
    cases: list[tuple[str, list[Path], Path | None]] = [
        (f"seed__{case.name}", copy_case(tree, case), case / "expected.json")
        for case in seed_cases()
    ]
    batch = json.loads(
        (tree / "sysml-codegen/tests/fixtures/v6_recapture_batch/batch.json").read_text()
    )
    captured = set(batch["captured"])
    for name in batch["fixtures"]:
        prefix = "corpus" if name in captured else "corpusx"
        cases.append((f"{prefix}__{name}", [tree / "sysml-codegen/tests/fixtures" / name], None))
    for name, rev in DC3_PINS.items():
        dest = tree / name
        export_tree(dc3_repo, resolve_rev(dc3_repo, rev), dest)
        cases.append((f"{name}_{rev}", [dest / "models"], None))
    return cases


def compare(args: argparse.Namespace) -> int:
    lines: list[str] = []
    matched = 0
    with isolated_tree(args.tmp_root, args.agentic_rev, args.codegen_repo, args.dc3_repo) as (
        tree,
        python,
        env,
        identity,
    ):
        lines.append(
            f"identity {json.dumps({k: v for k, v in identity.items() if k != 'tree_root'})}"
        )
        cases = recorded_run(tree, args.dc3_repo)
        for name, models, stored in cases:
            want_raw = oracle(tree, python, env, name, models)
            got_raw = port(tree, python, env, name, models)
            problems: list[str] = []
            if "oracle_crash" in want_raw:
                problems.append("oracle crashed: " + want_raw["oracle_crash"][-400:])
            if "port_crash" in got_raw:
                problems.append("port crashed: " + got_raw["port_crash"][-400:])
            if got_raw.get("codegen_imported"):
                problems.append("the port imported sysml_codegen")
            if not problems:
                want = strip_oracle_only_fields(want_raw)
                problems += schema_differences(want, got_raw["port"])
                if stored is not None:
                    stale = schema_differences(
                        strip_oracle_only_fields(json.loads(stored.read_text())), want
                    )
                    problems += [
                        f"stored expectation differs from today's oracle: {d}" for d in stale
                    ]
            full = want_raw.get("full") or {}
            full_note = (
                "full=n/a"
                if not full.get("ran")
                else f"full occ={full['occurrences_equal']} calcs={full['calcs_equal']}"
            )
            kind = (
                "fatal" if "fatal" in want_raw else f"strict={want_raw.get('strict', {}).get('ok')}"
            )
            lines.append(
                f"{'MATCH' if not problems else 'MISMATCH':8} {name:70} {kind} {full_note}"
            )
            lines += [f"    {p[:400]}" for p in problems]
            matched += not problems
        lines.append(f"TOTAL {matched}/{len(cases)} match")
    log = "\n".join(lines) + "\n"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "occurrence-parity.log").write_text(log)
    print(log)
    return 0 if matched == len(cases) else 1


# ---- negative controls ------------------------------------------------------------------


def _mutants() -> dict[str, Callable[[], Callable[[], None]]]:
    """Each entry installs one deliberately wrong port and returns the function that undoes it."""
    from agentic_mbse.sysml import occurrence_extraction as port_module

    builder, slots = port_module._Builder, port_module._SlotIndex

    def patch(owner: Any, name: str, replacement: Any) -> Callable[[], None]:
        original = owner.__dict__[name]
        setattr(owner, name, replacement)
        return lambda: setattr(owner, name, original)

    def declared_multiplicity() -> Callable[[], None]:
        original = builder.reading

        class DeclaredView:
            def __init__(self, usage: Any) -> None:
                self._usage = usage

            def __getattr__(self, name: str) -> Any:
                if name == "multiplicity":
                    return getattr(self._usage, "declared_multiplicity", None)
                return getattr(self._usage, name)

        return patch(
            builder,
            "reading",
            lambda self, usage, parent: original(self, DeclaredView(usage), parent),
        )

    return {
        "declared_multiplicity": declared_multiplicity,
        "no_effective_decl": lambda: patch(slots, "effective_declaration", lambda self, c: max(c)),
        "writer_is_base": lambda: patch(builder, "select_writer", lambda self, base, c, s: base),
        "typed_anywhere": lambda: (lambda: None),  # applied to the rendering, below
    }


def _typed_anywhere(model: Any, rendered: dict[str, Any]) -> dict[str, Any]:
    """The prototype's rule: a part def "has occurrences" if any usage is typed by it."""
    from agentic_mbse.sysml.occurrence_extraction import declaration_id
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    typed = {
        str(declaration_id(t))
        for usage in SysideAdapter.elements_of_type(model, "PartUsage")
        for t in (getattr(usage, "types", None) or ())
        if getattr(t, "qualified_name", None) is not None
    }
    if "def_occurrences" in rendered:
        rendered["def_occurrences"] = {d: int(d in typed) for d in rendered["def_occurrences"]}
    return rendered


def controls(args: argparse.Namespace) -> int:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
    from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    catchable = {"no_effective_decl", "writer_is_base", "typed_anywhere"}
    lines = [
        f"agentic-mbse {subprocess.run(['git', '-C', str(REPO_ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()}"
    ]
    ok = True
    for mutant, install in _mutants().items():
        flagged: list[str] = []
        undo = install()
        try:
            for case in seed_cases():
                model, _ = SysideAdapter.load_model(case_models(case))
                rendered = to_oracle_schema(extract_occurrence_structure(model))
                if mutant == "typed_anywhere":
                    rendered = _typed_anywhere(model, rendered)
                want = strip_oracle_only_fields(json.loads((case / "expected.json").read_text()))
                if rendered != want:
                    flagged.append(case.name)
        finally:
            undo()
        expectation = "must be caught" if mutant in catchable else "not catchable (F1 Surprise 1)"
        verdict = bool(flagged) if mutant in catchable else not flagged
        ok &= verdict
        lines.append(
            f"{mutant:22} flagged {len(flagged)}/{len(seed_cases())} ({expectation}): "
            f"{'OK' if verdict else 'UNEXPECTED'} {flagged}"
        )
    log = "\n".join(lines) + "\n"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "occurrence-parity-controls.log").write_text(log)
    print(log)
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "compare"):
        command = sub.add_parser(name)
        command.add_argument("--agentic-rev", default="HEAD")
        command.add_argument(
            "--codegen-repo", type=Path, default=Path.home() / "src" / "sysml-codegen"
        )
        command.add_argument("--dc3-repo", type=Path, default=Path.home() / "src" / "dc3")
        command.add_argument("--tmp-root", type=Path, default=Path("/tmp/subset-profile"))
    sub.choices["capture"].add_argument("cases", nargs="*", help="parity-seed case names")
    sub.choices["capture"].add_argument("--all", action="store_true", help="every parity-seed case")
    sub.choices["compare"].add_argument("--all", action="store_true", required=True)
    sub.add_parser("controls")
    args = parser.parse_args()
    if args.command in ("capture", "compare"):
        args.codegen_repo, args.dc3_repo = args.codegen_repo.resolve(), args.dc3_repo.resolve()
    if args.command == "capture" and bool(args.cases) == bool(args.all):
        parser.error("capture takes case names or --all, not both or neither")
    return {"capture": capture, "compare": compare, "controls": controls}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
