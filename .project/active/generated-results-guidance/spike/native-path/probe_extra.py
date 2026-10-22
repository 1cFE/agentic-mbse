"""Extra S1 probes: literal multiplicity sum, and ways to get a Boolean from an assert constraint.

Usage (repo root):
    uv run python .project/active/generated-results-guidance/spike/native-path/probe_extra.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import native_path  # noqa: E402

syside = native_path.syside
files = [str(p) for p in (HERE / "model_extra").rglob("*.sysml")]
model, diags = syside.load_model(files)
print("load diagnostics:", [str(d.message) for d in getattr(diags, "diagnostics", [])][:5])

for p in [
    "probe_extra::host.packlit.total",
    "probe_extra::host.packlit.n",
    "probe_extra::host.packredef.total",
    "probe_extra::host.pos_flag",
    "probe_extra::host.load_positive",
    "probe_extra::host.inline_neg",
]:
    try:
        print(p, "->", native_path.evaluate(model, p))
    except Exception as e:  # noqa: BLE001
        print(p, "-> ERROR", type(e).__name__, e)

# Constraint verdict attempts: evaluate the constraint's result expression in the
# constraint usage's scope (the usage inherits the def's body expression).
host = next(p for p in model.elements(syside.PartUsage) if p.name == "host")
for cname in ["load_positive", "load_negative", "inline_neg"]:
    cu = native_path.child(host, cname)
    print(f"--- {cname}: type {type(cu).__name__}")
    # 1. result expression on the usage itself
    rexpr = getattr(cu, "result_expression", None)
    print("  usage.result_expression:", rexpr)
    # 2. the definition's result expression, evaluated with the usage as scope
    for d in getattr(cu, "constraint_definition", None) and [cu.constraint_definition] or []:
        print("  def:", d.name, "def.result_expression:", getattr(d, "result_expression", None))
        if getattr(d, "result_expression", None) is not None:
            v, r = syside.Compiler().evaluate(d.result_expression, stdlib=model.lib, scope=cu)
            print("  evaluate(def.result_expression, scope=usage) ->", v, [str(x.message) for x in r.diagnostics])
    if rexpr is not None:
        for scope in (cu, host):
            v, r = syside.Compiler().evaluate(rexpr, stdlib=model.lib, scope=scope)
            print(f"  evaluate(usage.result_expression, scope={scope.name}) ->", v, [str(x.message) for x in r.diagnostics])
    # 3. the usage's 'result' feature, if any
    for f in list(cu.owned_features.collect()) + list(cu.inherited_features.collect()):
        if f.name in ("result",) or type(f).__name__.endswith("Expression"):
            try:
                v, r = syside.Compiler().evaluate_feature(f, scope=cu, stdlib=model.lib)
                print(f"  evaluate_feature({type(f).__name__} {f.name}, scope=usage) ->", v, [str(x.message) for x in r.diagnostics])
            except Exception as e:  # noqa: BLE001
                print("  feature", f.name, "ERROR", e)
