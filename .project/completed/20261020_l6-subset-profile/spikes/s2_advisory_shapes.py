"""Spike S2: which SysML expressions fire each advisory walker (design D12)?

    uv run python .project/active/l6-subset-profile/spikes/s2_advisory_shapes.py

Throwaway. Each candidate is a tiny package written to a temp dir, loaded with SysIDE, and run
through the same two walkers `s1_trees.py` uses over the contract's expression sites:
- opaque: `reconstruct_expression` reached its `return str(expr_node)` line (traced);
- wrapper: `decompose_aggregation_expression(...).wrappers` is non-empty on a site invoking `sum`.
Prints one line per candidate: load errors, each site's opaque node types, wrappers, or the
walker exception.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s1_trees import advisories  # noqa: E402

from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402

HEADER = """package P {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    private import SequenceFunctions::*;
    private import ControlFunctions::*;
    part def Cell { attribute mass : Real = 2.0; attribute ok : Boolean = true; }
    part def Pack {
        part cells : Cell[3];
"""
FOOTER = """
    }
}
"""

CANDIDATES: dict[str, str] = {
    # ---- control: plain shapes the walker names structurally ----
    "ctl_sum_chain": "attribute total : Real = sum(cells.mass);",
    "ctl_arith": "attribute x : Real = 1.0 + 2.0 * 3.0;",
    # ---- wrapper candidates (sum over an invocation) ----
    "wrap_sum_collect": "attribute total : Real = sum(cells.mass->collect { in m : Real; m * 2.0 });",
    "wrap_sum_select": "attribute total : Real = sum(cells->select { in c : Cell; c.ok }.mass);",
    "wrap_sum_select_arrow": "attribute total : Real = sum((cells->select { in c : Cell; c.ok }).mass);",
    "wrap_sum_collect_call": "attribute total : Real = sum(collect(cells.mass, { in m : Real; m }));",
    "wrap_sum_evaluation": "attribute total : Real = sum(Evaluation(cells.mass));",
    "wrap_sum_seq": "attribute total : Real = sum((cells.mass, 1.0));",
    "wrap_sum_abs": "attribute total : Real = sum(abs(cells.mass));",
    "wrap_sum_filter": "attribute total : Real = sum(cells.mass->select { in m : Real; m > 1.0 });",
    "wrap_sum_dotcollect": "attribute total : Real = sum(cells.{ in c : Cell; c.mass });",
    "wrap_sum_dotselect": "attribute total : Real = sum(cells.?{ in c : Cell; c.ok }.mass);",
    # ---- opaque candidates (no structural branch in reconstruct_expression) ----
    "opq_metadata": "attribute m = Cell.metadata;",
    "opq_meta_op": "attribute m = cells meta KerML::Element;",
    "opq_unresolved_call": "attribute y : Real = notAFunction(1.0);",
    "opq_calc_usage_call": "calc twice { in v : Real; return r : Real = v * 2.0; } attribute y : Real = twice(3.0);",
    "opq_body_expr": "attribute f = { in v : Real; v * 2.0 };",
    "opq_new": "attribute c = new Cell();",
    "opq_if": "attribute y : Real = if true ? 1.0 else 2.0;",
    "opq_cast": "attribute y = cells.mass as Real;",
    "opq_index": "attribute y : Real = cells.mass#(1);",
    "opq_string_concat": 'attribute s : String = "a" + "b";',
    "opq_null_coalesce": "attribute y : Real = cells.mass ?? 0.0;",
    "opq_istype": "attribute b : Boolean = cells istype Cell;",
    "opq_at": "attribute b : Boolean = cells @ Cell;",
    "opq_all": "attribute s = all Cell;",
    "opq_literal_inf": "attribute n = *;",
}


def probe(name: str, body: str, work: Path) -> str:
    path = work / f"{name}.sysml"
    path.write_text(HEADER + "        " + body + FOOTER, encoding="utf-8")
    model, diagnostics = SysideAdapter.load_model([path])
    errors = [str(e) for e in diagnostics.errors]
    report = advisories(model)
    own = [
        f for key in ("opaque_firings", "wrapper_firings") for f in report[key] if "Pack" in f["site"]
    ]
    parts = [f"load_errors={len(errors)}"]
    if errors:
        parts.append(f"first_error={errors[0][:120]!r}")
    for key in ("opaque_firings", "wrapper_firings"):
        hits = [f for f in report[key] if f["site"].startswith("P::")]
        if hits:
            parts.append(f"{key}={[(h['site'], h.get('nodes') or h.get('wrappers')) for h in hits]}")
    if report["walker_failures"]:
        parts.append(f"walker_failures={report['walker_failures']} {report['walker_failure_examples']}")
    del own
    return f"{name}: " + "; ".join(parts)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="l6-spike-s2-") as tmp:
        for name, body in CANDIDATES.items():
            try:
                print(probe(name, body, Path(tmp)), flush=True)
            except Exception as error:
                print(f"{name}: PROBE RAISED {type(error).__name__}: {error}", flush=True)


if __name__ == "__main__":
    main()
