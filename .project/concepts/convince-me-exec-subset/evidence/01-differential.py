"""Differential conformance prototype for Claim 1 (pytest-style: exits non-zero on any disagreement).

Compares, per boundary fixture:
  * the PROTOTYPE screen's decision (01-screen.py, agentic-mbse venv, no sysml_codegen import), and
  * the generator's own outcome (01-codegen-oracle.json, produced by running `sysml-codegen generate`,
    which has no subset screen today, so it is the generator with the screen bypassed).

Row verdicts:
  AGREE      both refuse (with a mapped code), both admit, or both report the same omission
  MISSED     codegen refuses (or silently omits) but the screen says nothing
  OVERBROAD  the screen refuses (or reports an omission) but codegen admits
  MISMATCH   both refuse, but the screen's rule does not map to codegen's code

Usage (cwd = agentic-mbse):  uv run python -I <this> [env controls are read by 01-screen.py]
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("screen", HERE / "01-screen.py")
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)

#: Codegen-owned diagnostic mapping (one-to-many), as the end-state adapter would hold it.
RULE_TO_CODES = {
    "ES-001": {"SI_CONSTRAINT_UNATTACHED"},
    "ES-003": {"SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_OCCURRENCE_AMBIGUOUS", "SI_MULTIPLICITY_UNSUPPORTED"},
    "ES-004": {"SI_MULTIPLICITY_UNRESOLVED", "SI_MULTIPLICITY_UNSUPPORTED"},
    "ES-005": {"SI_EXPRESSION_SOURCE_UNSUPPORTED"},
    "ES-006": {"SI_EVIDENCE_INCOMPLETE"},
    "ES-007": {"SI_CONSTRAINT_BLOCKED"},
    "ES-010": {"SI_RENDERING_COLLISION"},
}


def screen_decision(path: Path) -> tuple[set[str], set[str]]:
    results = screen.run([path])
    refused, omitted = set(), set()
    for rule, r in results.items():
        if r["status"] != "checked":
            refused.add(f"{rule}:UNVERIFIED")
        for f in r["findings"]:
            outcome = f.get("outcome", r["outcome"])
            if outcome.startswith("refused"):
                refused.add(rule)
            elif outcome == "omitted":
                omitted.add(rule)
    return refused, omitted


def verdict(cg: dict, refused: set[str], omitted: set[str]) -> str:
    cg_refused = cg["exit"] != 0
    cg_codes = set(cg["codes"])
    cg_omitted = bool(cg.get("omitted_from_output"))
    if cg_refused:
        if not refused:
            return "MISSED"
        mapped = set().union(*(RULE_TO_CODES.get(r, set()) for r in refused))
        return "AGREE" if mapped & cg_codes else "MISMATCH"
    if refused:
        return "OVERBROAD"
    if cg_omitted and not omitted:
        return "MISSED"
    if omitted and not cg_omitted:
        return "OVERBROAD"
    return "AGREE"


def main() -> int:
    oracle = json.loads((HERE / "01-codegen-oracle.json").read_text())
    print(f"controls: SCREEN_DISABLE={os.environ.get('SCREEN_DISABLE', '-')} SCREEN_OVERBROAD={os.environ.get('SCREEN_OVERBROAD', '-')} SCREEN_ES003_V1={os.environ.get('SCREEN_ES003_V1', '-')}")
    print(f"{'fixture':46} {'codegen (screen bypassed)':40} {'screen':28} verdict")
    tally: dict[str, int] = {}
    bad = []
    for name in sorted(oracle):
        cg = oracle[name]
        refused, omitted = screen_decision(HERE / "01-fixtures" / name)
        v = verdict(cg, refused, omitted)
        tally[v] = tally.get(v, 0) + 1
        cg_txt = ("refused " + ",".join(cg["codes"]) if cg["exit"] else "generated") + (" +omits " + ",".join(p.rsplit("__", 1)[-1] for p in cg.get("omitted_from_output", [])) if cg.get("omitted_from_output") else "")
        sc_txt = ("refused " + ",".join(sorted(refused)) if refused else "admitted") + (" +omits " + ",".join(sorted(omitted)) if omitted else "")
        print(f"{name.removesuffix('.sysml'):46} {cg_txt[:40]:40} {sc_txt[:28]:28} {v}")
        if v != "AGREE":
            bad.append((name, v))
    print()
    print("tally:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    if bad:
        print("FAILED:", "; ".join(f"{n} {v}" for n, v in bad))
        return 1
    print("PASSED: screen and generator agree on every fixture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
