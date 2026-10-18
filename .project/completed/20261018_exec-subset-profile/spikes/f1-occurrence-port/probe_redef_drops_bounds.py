"""List part redefinitions with no own multiplicity whose redefined feature declares one.

Usage: python -I probe_redef_drops_bounds.py MODEL_PATH [...]
"""
import sys
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter

model, _ = SysideAdapter.load_model([Path(p) for p in sys.argv[1:]])
for u in SysideAdapter.elements_of_type(model, "PartUsage"):
    if u.multiplicity is not None:
        continue
    for r in u.owned_redefinitions or ():
        base = r.redefined_feature
        if getattr(base, "multiplicity", None) is not None:
            m = base.multiplicity
            txt = lambda e: None if e is None else SysideAdapter.authored_text(e)
            print(f"{u.qualified_name} :>> {base.qualified_name} base=[{txt(m.lower_bound)}..{txt(m.upper_bound)}] "
                  f"base_ordered={base.is_ordered} redef_ordered={u.is_ordered}")
