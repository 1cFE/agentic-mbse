"""Compare oracle (codegen) and port JSON outputs, criterion by criterion.

Usage: python3 compare.py RESULTS_DIR  (expects <case>.oracle.json and <case>.port.json)
Writes RESULTS_DIR/summary.json and prints one line per case plus every mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# The only place a generator code appears: mapping the port's neutral classes for comparison.
RESOLUTION_TO_CODE = {
    "ordered": "SI_MULTIPLICITY_UNSUPPORTED",
    "nonunique": "SI_MULTIPLICITY_UNSUPPORTED",
    "range": "SI_MULTIPLICITY_UNSUPPORTED",
    "unresolved_upper": "SI_MULTIPLICITY_UNRESOLVED",
    "unresolved_lower": "SI_MULTIPLICITY_UNRESOLVED",
    "negative": "SI_MULTIPLICITY_INVALID",
}
CAUSE_TO_CODE = {
    "redefinition_invalid": "SI_REDEFINITION_INVALID",
    "containment_recursive": "SI_CONTAINMENT_RECURSIVE",
    "id_unstable": "SI_ID_UNSTABLE",
}


def strict_code(port: dict) -> dict:
    s = port.get("strict", {})
    if s.get("ok"):
        return {"ok": True}
    if "resolution" in s:
        return {"ok": False, "code": RESOLUTION_TO_CODE[s["resolution"]]}
    return {"ok": False, "code": CAUSE_TO_CODE.get(s.get("cause"), s.get("cause"))}


def fatal_code(side: dict, is_port: bool):
    f = side.get("fatal")
    if not f:
        return None
    return [f["stage"], CAUSE_TO_CODE.get(f["cause"], f["cause"]) if is_port else f["code"]]


def compare(oracle: dict, port: dict) -> dict:
    names = {**oracle.get("names", {}), **port.get("names", {})}

    def nm(x):
        return names.get(x, x) if isinstance(x, str) else x

    checks: dict[str, list] = {}

    def diff(label, a, b, render=lambda v: v):
        if a == b:
            checks[label] = []
            return
        if isinstance(a, list) and isinstance(b, list):
            sa = {json.dumps(x, sort_keys=True) for x in a}
            sb = {json.dumps(x, sort_keys=True) for x in b}
            checks[label] = [("codegen_only", render(json.loads(x))) for x in sorted(sa - sb)] + [
                ("port_only", render(json.loads(x))) for x in sorted(sb - sa)
            ]
        elif isinstance(a, dict) and isinstance(b, dict):
            keys = sorted(set(a) | set(b))
            checks[label] = [(nm(k), {"codegen": a.get(k), "port": b.get(k)}) for k in keys if a.get(k) != b.get(k)]
        else:
            checks[label] = [{"codegen": a, "port": b}]

    for side, label in ((oracle, "oracle_crash"), (port, "port_crash")):
        if side.get(label):
            checks[label] = [side[label][-800:]]
    diff("fatal", fatal_code(oracle, False), fatal_code(port, True))
    diff("strict_first_error", oracle.get("strict", {}).get("ok") and {"ok": True} or {"ok": False, "code": oracle.get("strict", {}).get("code")}, strict_code(port))
    diff("a_roots", oracle.get("roots"), port.get("roots"), nm)
    diff("b_occurrences", oracle.get("occurrences"), port.get("occurrences"), lambda r: {**r, "usage": nm(r["usage"])})
    diff("b_counts", oracle.get("counts"), port.get("counts"))
    diff("b_visits", oracle.get("visits"), port.get("visits"), lambda r: [nm(r[0]), r[1]])
    has_o = {k: v > 0 for k, v in (oracle.get("def_occurrences") or {}).items()}
    has_p = {k: v > 0 for k, v in (port.get("def_occurrences") or {}).items()}
    diff("c_def_has_occurrences", has_o, has_p)
    diff("c_def_occurrence_counts", oracle.get("def_occurrences"), port.get("def_occurrences"))
    diff("d_writers", oracle.get("writers"), port.get("writers"), lambda r: [r[0], nm(r[1]), nm(r[2])])
    diff("d_writers_status", oracle.get("writers_status"), port.get("writers_status"))
    diff("d_calc_attachment", oracle.get("calc_attachment"), port.get("calc_attachment"))
    port_unexp = [[u, p, RESOLUTION_TO_CODE[r]] for u, p, r in port.get("unexpandable", [])]
    diff("e_unexpandable", oracle.get("unexpandable") or [], port_unexp, lambda r: [nm(r[0]), r[1], r[2]])
    if port.get("codegen_imported"):
        checks["port_imported_codegen"] = [True]
    mismatched = {k: v for k, v in checks.items() if v}
    stats = {
        "roots": len(oracle.get("roots") or []),
        "occurrences": len(oracle.get("occurrences") or []),
        "writers": len(oracle.get("writers") or []),
        "unexpandable": len(oracle.get("unexpandable") or []),
        "defs_with_occ": sum(1 for v in (oracle.get("def_occurrences") or {}).values() if v),
    }
    return {"match": not mismatched, "mismatches": mismatched, "stats": stats, "full": oracle.get("full"), "strict": oracle.get("strict"), "fatal": oracle.get("fatal")}


def main() -> int:
    root = Path(sys.argv[1])
    summary = {}
    for oracle_path in sorted(root.glob("*.oracle.json")):
        case = oracle_path.name[: -len(".oracle.json")]
        port_path = root / f"{case}.port.json"
        if not port_path.exists():
            summary[case] = {"match": False, "mismatches": {"port_missing": [True]}}
            continue
        summary[case] = compare(json.loads(oracle_path.read_text()), json.loads(port_path.read_text()))
    (root / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str))
    for case, r in summary.items():
        full = r.get("full") or {}
        full_s = "full=n/a" if not full.get("ran") else f"full occ={full['occurrences_equal']} calcs={full['calcs_equal']}"
        strict = r.get("strict") or {}
        print(f"{'MATCH' if r['match'] else 'MISMATCH':8} {case:60} {r.get('stats')} strict={'ok' if strict.get('ok') else strict.get('code')} {full_s}")
        for label, items in r.get("mismatches", {}).items():
            for item in items:
                print(f"    {label}: {json.dumps(item, default=str)[:400]}")
    print(f"TOTAL {sum(r['match'] for r in summary.values())}/{len(summary)} match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
