"""Claim 2 guard: fail on any refusal site that is not reviewed and classified.

Usage:
    python 02-inventory-test.py <codegen_src_root> <agentic_mbse_src_root> [--write-baseline]

Rules (each failure names file:line):
  R1 every code at a site (or free-text/builtin class) is in 02-classification.csv
  R2 every site_id is in the reviewed baseline 02-sites.baseline
  R3 a site whose code is not a literal (coded-DYNAMIC) needs an explicit exemption
     in 02-dynamic-exemptions.csv, with a reason
  R4 a baseline site that no longer exists is stale (the baseline must track removals)
Exit 0 when clean, 1 otherwise.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_inventory():
    spec = importlib.util.spec_from_file_location("inv", HERE / "02-inventory.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.inventory


def main() -> int:
    codegen_root, ambse_root = Path(sys.argv[1]), Path(sys.argv[2])
    rows = load_inventory()(codegen_root, ambse_root)
    baseline_path = HERE / "02-sites.baseline"
    if "--write-baseline" in sys.argv:
        baseline_path.write_text("\n".join(sorted(r["site_id"] for r in rows)) + "\n")
        print(f"wrote {len(rows)} reviewed sites to {baseline_path.name}")
        return 0

    classified = {r["key"] for r in csv.DictReader((HERE / "02-classification.csv").open())}
    exempt = {
        r["site_id"]: r["reason"]
        for r in csv.DictReader((HERE / "02-dynamic-exemptions.csv").open())
        if r["reason"].strip()
    }
    baseline = set(baseline_path.read_text().split())
    failures: list[str] = []
    seen: set[str] = set()
    for r in rows:
        where = f"{r['file']}:{r['line']} in {r['function']}"
        seen.add(r["site_id"])
        if r["channel"] == "coded-DYNAMIC":
            if r["site_id"] not in exempt:
                failures.append(f"R3 non-literal code `{r['code']}` at {where}: add a literal code or a reviewed exemption")
        elif r["channel"] not in {"coded-relay", "plumbing"}:
            for code in r["code"].split("|"):
                if code not in classified:
                    failures.append(f"R1 unclassified code {code} ({r['channel']}) at {where}")
        if r["site_id"] not in baseline:
            failures.append(f"R2 new unreviewed refusal site {r['site_id']} at {where}")
    for stale in sorted(baseline - seen):
        failures.append(f"R4 stale baseline site {stale} (removed or moved to another function)")

    print(f"sites enumerated: {len(rows)}; baseline: {len(baseline)}; classified keys: {len(classified)}; dynamic exemptions: {len(exempt)}")
    if failures:
        print(f"FAIL: {len(failures)} problem(s)")
        for f in failures:
            print("  " + f)
        return 1
    print("PASS: every refusal site is reviewed, every code classified, every non-literal code exempted with a reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
