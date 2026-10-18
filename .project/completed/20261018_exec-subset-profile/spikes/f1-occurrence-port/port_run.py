"""Run the port on one model and emit the oracle's JSON schema (minus `full`).

Usage: python -I port_run.py OUT.json MODEL_PATH [MODEL_PATH ...]
Asserts at exit that sysml_codegen was never imported.
"""

from __future__ import annotations

import json
import sys
import traceback
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402
from occurrence_port import FactFailure, OccurrenceStructure, SlotIndex, _pkey, decl, semantic_owner  # noqa: E402


def scope_key(scope) -> str:
    if isinstance(scope, tuple) and len(scope) == 2 and scope[0] == "pkg":
        return f"pkg:{scope[1]}"
    return "occ:" + _pkey(scope)


def run(model) -> dict:
    out: dict = {"names": {}}
    for kind in ("PartUsage", "PartDefinition", "CalculationUsage", "Package"):
        for element in SysideAdapter.elements_of_type(model, kind):
            if getattr(element, "qualified_name", None) is not None:
                out["names"][str(decl(element))] = str(element.qualified_name)
    try:
        SlotIndex(model)
    except FactFailure as error:
        out["fatal"] = {"stage": "slots", "cause": error.cause, "detail": error.detail}
        return out
    structure = OccurrenceStructure.__new__(OccurrenceStructure)
    structure.visits = []
    try:
        structure.__init__(model)
    except FactFailure as error:
        first = next((v for v in structure.visits if v[2].resolution not in ("absent", "exact")), None)
        out["strict"] = {"ok": False, "resolution": first[2].resolution} if first else {"ok": False, "cause": error.cause}
        out["fatal"] = {"stage": "occurrences", "cause": error.cause, "detail": error.detail}
        return out
    first = next((v for v in structure.visits if v[2].resolution not in ("absent", "exact")), None)
    out["strict"] = {"ok": True} if first is None else {"ok": False, "resolution": first[2].resolution}

    def ppath(node):
        return _pkey(node.path) if node is not None else None

    out["roots"] = sorted({str(u) for u, parent, _r in structure.visits if parent is None})
    out["visits"] = sorted([[str(u), ppath(p)] for u, p, _r in structure.visits], key=lambda c: (c[0], c[1] or ""))
    out["unexpandable"] = sorted(
        [[str(u), ppath(p), r.resolution] for u, p, r in structure.visits if r.resolution not in ("absent", "exact")],
        key=lambda c: (c[0], c[1] or ""),
    )
    nodes = structure.nodes.values()
    out["occurrences"] = sorted(
        [
            {
                "path": _pkey(n.path),
                "usage": str(n.usage),
                "type": str(n.type_id) if n.type_id else None,
                "closure": sorted(str(t) for t in n.closure),
                "children": sorted(str(c) for c in n.children),
            }
            for n in nodes
        ],
        key=lambda r: r["path"],
    )
    counts: dict[str, int] = defaultdict(int)
    for n in nodes:
        counts[str(n.usage)] += 1
    out["counts"] = dict(sorted(counts.items()))
    out["def_occurrences"] = {
        str(d): sum(1 for n in nodes if d in n.closure) for d in structure.definitions
    }
    try:
        writers = structure.calc_writers()
        out["writers_status"] = "ok" if writers else "no_calc_usages_selected"
        out["writers"] = sorted(
            [scope_key(s), str(b), str(c), sorted(str(a) for a in app)] for s, b, c, app in writers
        )
    except FactFailure as error:
        out["writers_status"] = "error"
        out["writers_error"] = {"cause": error.cause, "detail": error.detail}
        out["writers"] = []
    attach = {}
    for usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        scopes, cause = structure.attachment(semantic_owner(usage))
        attach[str(decl(usage))] = [sorted(scope_key(s) for s in scopes), cause]
    out["calc_attachment"] = dict(sorted(attach.items()))
    return out


def main() -> int:
    out_path = Path(sys.argv[1])
    paths = [Path(p) for p in sys.argv[2:]]
    model, diagnostics = SysideAdapter.load_model(paths)
    result: dict = {"inputs": [str(p) for p in paths], "load_errors": bool(diagnostics is not None and diagnostics.contains_errors())}
    try:
        result.update(run(model))
    except Exception:
        result["port_crash"] = traceback.format_exc()
    result["codegen_imported"] = any(m.startswith("sysml_codegen") for m in sys.modules)
    out_path.write_text(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
