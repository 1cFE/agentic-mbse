"""Count usages where `multiplicity` and `declared_multiplicity` differ (SysIDE 0.8.4).

Usage: python -I probe_multiplicity_identity.py MODEL_PATH [...]
"""
import sys
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter

model, _ = SysideAdapter.load_model([Path(p) for p in sys.argv[1:]])
total = differ = redef_no_own = 0
for kind in ("PartUsage", "AttributeUsage"):
    for u in SysideAdapter.elements_of_type(model, kind):
        total += 1
        m, d = u.multiplicity, getattr(u, "declared_multiplicity", None)
        same = (m is None and d is None) or (m is not None and d is not None and SysideAdapter.element_id(m) == SysideAdapter.element_id(d))
        differ += not same
        if (u.owned_redefinitions or ()) and m is None:
            redef_no_own += 1
print(f"usages={total} multiplicity!=declared={differ} redefinitions_with_no_multiplicity={redef_no_own}")
