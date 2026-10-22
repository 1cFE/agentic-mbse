"""S2 follow-up: does SysIDE see the redefined part count that the generator builds wrongly?

    spike/codegen.sh spike/channel-trace/probe_count.py spike/channel-trace/models/default_count
"""

import sys
from pathlib import Path

import syside

model, _ = syside.load_model([str(p) for p in Path(sys.argv[1]).rglob("*.sysml")])
pack = next(p for p in model.elements(syside.PartUsage) if p.name == "pack")
for f in list(pack.owned_features.collect()) + list(pack.inherited_features.collect()):
    if f.name in ("cell_count", "cells"):
        v, r = syside.Compiler().evaluate_feature(f, scope=pack, stdlib=model.lib)
        print(f"evaluate_feature({f.qualified_name}, scope=pack) -> {v!r} {[str(d.message) for d in r.diagnostics]}")
        mult = getattr(f, "multiplicity", None)
        if mult is not None:
            for bound in ("lower_bound", "upper_bound"):
                b = getattr(mult, bound, None)
                if b is not None:
                    bv, br = syside.Compiler().evaluate(b, stdlib=model.lib, scope=pack)
                    print(f"  multiplicity {bound} in scope pack -> {bv!r}")
