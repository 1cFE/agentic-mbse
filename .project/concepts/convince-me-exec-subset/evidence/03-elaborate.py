"""C3 step 2: run the checkable fences through the real generator route and L6.

Each case is one model file: the fence (wrapped in a package with standard imports
when it needs them), plus an optional prelude (definitions the fence names but does
not define) and an optional harness (the instantiation that makes it executable).
Context files live in 03-contexts/<idx>.{prelude,harness}.sysml.

Oracle 1: `sysml-codegen generate --models <case> --output <tmp>` (the full route).
Oracle 2: `agentic-mbse validate --level=6 <case>`.

Run from the agentic-mbse repo root:
    uv run python .project/concepts/convince-me-exec-subset/evidence/03-elaborate.py
Writes 03-elaboration.log and 03-elaboration.json.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CODEGEN = Path("/home/reid/src/sysml-codegen")
SCRATCH = Path(
    os.environ.get(
        "C3_SCRATCH",
        "/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c3",
    )
)
FENCES = SCRATCH / "fences"
RUNS = SCRATCH / "runs"
CONTEXTS = HERE / "03-contexts"

WRAP_HEAD = (
    "package FenceWrap {\n"
    "    private import ScalarValues::*;\n"
    "    private import ISQ::*;\n"
    "    private import SI::*;\n"
    "    private import NumericalFunctions::*;\n"
)
CODE = re.compile(
    r"\b(SI_[A-Z_]+|SYSML_NAMESPACE_NOT_DISTINGUISHABLE|OVERRIDE_TARGET_MISSING|"
    r"EXTRACTION_DIAGNOSTIC_BLOCKING|L\d_[A-Z_]+|NON_NUMERICAL|MALFORMED_NUMERICAL)\b"
)


def env() -> dict[str, str]:
    out = dict(os.environ)
    for line in (REPO / ".env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            out.setdefault(k.strip(), v.strip().strip('"'))
    return out


def build_case(idx: int, wrapped: bool) -> tuple[str, Path]:
    body = (FENCES / f"f{idx:03d}.sysml").read_text()
    prelude = CONTEXTS / f"{idx:03d}.prelude.sysml"
    harness = CONTEXTS / f"{idx:03d}.harness.sysml"
    has_ctx = prelude.exists() or harness.exists()
    name = f"f{idx:03d}" + ("-ctx" if has_ctx else "")
    case_dir = RUNS / name / "models"
    case_dir.mkdir(parents=True, exist_ok=True)
    if wrapped or has_ctx:
        text = WRAP_HEAD
        text += prelude.read_text() if prelude.exists() else ""
        text += body
        text += harness.read_text() if harness.exists() else ""
        text += "}\n"
    else:
        text = body
    (case_dir / "example.sysml").write_text(text)
    return name, case_dir


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, env=env(), capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def assess(name: str, case_dir: Path) -> dict:
    out_dir = case_dir.parent / "generated"
    gen_rc, gen_out = run(
        [str(CODEGEN / ".venv/bin/sysml-codegen"), "generate", "--models", str(case_dir),
         "--output", str(out_dir), "--overwrite"],
        CODEGEN,
    )
    l6_rc, l6_out = run(
        [str(REPO / ".venv/bin/agentic-mbse"), "validate", "--level=6", str(case_dir)], REPO
    )
    generated_text = ""
    if out_dir.exists():
        generated_text = "\n".join(p.read_text(errors="replace") for p in out_dir.rglob("*.py"))
    codes = sorted(set(CODE.findall(gen_out)))
    if gen_rc == 0:
        outcome = "generated"
    elif "nothing to generate" in gen_out:
        outcome = "nothing-to-generate"
    elif codes:
        outcome = "refused"
    else:
        outcome = "error"
    return {
        "case": name,
        "generate_outcome": outcome,
        "generate_rc": gen_rc,
        "generate_codes": sorted(set(CODE.findall(gen_out))),
        "generate_tail": gen_out.strip().splitlines()[-6:],
        "generated_py_files": len(list(out_dir.rglob("*.py"))) if out_dir.exists() else 0,
        "generated_text": generated_text,
        "l6_rc": l6_rc,
        # L6 prints every counter; a code counts only when its counter is nonzero.
        "l6_codes": sorted({m.group(1) for m in re.finditer(r"^\s+([A-Z][A-Z0-9_]+): (\d+)$", l6_out, re.M) if int(m.group(2)) > 0}),
        "l6_tail": [l.strip() for l in l6_out.splitlines() if re.search(r"ERROR:|WARNING:|Passed:|Failed:", l)][:8],
    }


def main() -> int:
    rows = list(csv.DictReader((HERE / "03-inventory.csv").open()))
    complete = [
        (int(r["idx"]), r["status"] == "complete-wrapped", r["id"])
        for r in rows
        if r["status"].startswith("complete")
    ]
    ctx_ids = sorted({int(p.name[:3]) for p in CONTEXTS.glob("*.sysml")})
    by_idx = {int(r["idx"]): r for r in rows}
    cases = {idx: (wrapped, rid) for idx, wrapped, rid in complete}
    for idx in ctx_ids:
        cases.setdefault(idx, (True, by_idx[idx]["id"]))

    results = []
    for idx, (wrapped, rid) in sorted(cases.items()):
        # Definitions alone first (what a "complete definition" check sees) ...
        if idx in ctx_ids and by_idx[idx]["status"].startswith("complete"):
            name, case_dir = build_case_no_ctx(idx, wrapped)
            res = assess(name, case_dir)
            res.update(idx=idx, id=rid, context=False)
            results.append(res)
            print(f"{name:12} gen={res['generate_outcome']} {res['generate_codes']} l6={res['l6_codes']}", flush=True)
        # ... then with its prelude/harness, when one exists.
        name, case_dir = build_case(idx, wrapped)
        res = assess(name, case_dir)
        res.update(idx=idx, id=rid, context=idx in ctx_ids)
        results.append(res)
        print(f"{name:12} gen={res['generate_outcome']} {res['generate_codes']} l6={res['l6_codes']}", flush=True)

    for r in results:
        r["material_emitted"] = "material" in r.pop("generated_text")
    (HERE / "03-elaboration.json").write_text(json.dumps(results, indent=2))

    lines = []
    for r in results:
        lines.append(f"## {r['case']}  ({r['id']})  context={r['context']}")
        lines.append(f"generate {r['generate_outcome']} rc={r['generate_rc']} codes={r['generate_codes']} py_files={r['generated_py_files']}")
        lines.extend("  | " + t for t in r["generate_tail"])
        lines.append(f"L6 rc={r['l6_rc']} codes={r['l6_codes']}")
        lines.extend("  | " + t for t in r["l6_tail"])
        lines.append("")
    (HERE / "03-elaboration.log").write_text("\n".join(lines))
    return 0


def build_case_no_ctx(idx: int, wrapped: bool) -> tuple[str, Path]:
    body = (FENCES / f"f{idx:03d}.sysml").read_text()
    name = f"f{idx:03d}"
    case_dir = RUNS / name / "models"
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "example.sysml").write_text(WRAP_HEAD + body + "}\n" if wrapped else body)
    return name, case_dir


if __name__ == "__main__":
    sys.exit(main())
