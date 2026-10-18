"""Codegen oracle for the Claim-1 differential (runs in the sysml-codegen venv).

For each fixture, runs the generator's real route (`sysml-codegen generate`) into a temp dir.
There is no subset screen inside codegen today, so this IS the generator "with the screen
bypassed": every outcome below comes from codegen's own elaboration/projection/generation.
For fixtures that generate, it also elaborates leniently and lists which declared attribute
names reached the instance graph, so a silent omission is visible.

Usage (cwd = sysml-codegen):  uv run python <this> <fixtures-dir> --json out.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

CODE = re.compile(r"\b((?:SI|SYSML|OVERRIDE|EXTRACTION)_[A-Z_]+)\b")


def run_fixture(path: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, "-m", "sysml_codegen", "generate", "--models", str(path), "--output", str(Path(tmp) / "out")],
            capture_output=True,
            text=True,
            timeout=600,
        )
        generated = "\n".join(p.read_text(errors="replace") for p in (Path(tmp) / "out").rglob("*") if p.is_file()) if proc.returncode == 0 else ""
    text = proc.stdout + proc.stderr
    errors = [line for line in text.splitlines() if line.startswith("ERROR")]
    codes = sorted({m for line in errors for m in CODE.findall(line)})
    result = {"exit": proc.returncode, "codes": codes, "error_lines": errors[:3]}
    if proc.returncode == 0:
        graph = elaborate_model_paths([path], strict=False)
        result["graph_attr_paths"] = sorted(a.display_path for a in graph.attrs.values())
        # an attribute that elaborated but whose name appears nowhere in the generated package
        result["omitted_from_output"] = sorted(
            p for p in result["graph_attr_paths"] if p.rsplit("__", 1)[-1] not in generated
        )
    return result


def main() -> int:
    fixtures = Path(sys.argv[1])
    out = sys.argv[sys.argv.index("--json") + 1]
    results = {}
    for f in sorted(fixtures.glob("*.sysml")):
        results[f.name] = run_fixture(f)
        r = results[f.name]
        print(f"{f.name:45} exit={r['exit']} codes={r['codes'] or '-'} omitted={r.get('omitted_from_output') or '-'}")
        for line in r["error_lines"][:1]:
            print(f"    {line[:220]}")
    Path(out).write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
