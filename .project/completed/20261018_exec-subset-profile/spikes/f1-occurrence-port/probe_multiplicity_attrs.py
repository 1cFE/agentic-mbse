"""Learning probe (F2): what SysIDE 0.8.4 returns for multiplicity attributes on redefinitions.

Usage: python -I probe_multiplicity_attrs.py MODEL_PATH [...]
Prints, per user PartUsage: multiplicity vs declared_multiplicity (identity + bounds text),
is_ordered / is_nonunique, and the redefined features.
"""
import sys
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter


def show(m):
    if m is None:
        return "None"
    lo, up = getattr(m, "lower_bound", None), getattr(m, "upper_bound", None)
    txt = lambda e: None if e is None else (SysideAdapter.authored_text(e) or type(e).__name__)
    return f"{type(m).__name__}@{SysideAdapter.element_id(m).hex[:8]} [{txt(lo)}..{txt(up)}]"


model, _ = SysideAdapter.load_model([Path(p) for p in sys.argv[1:]])
for u in SysideAdapter.elements_of_type(model, "PartUsage"):
    redefs = [str(r.redefined_feature.qualified_name) for r in (u.owned_redefinitions or ())]
    print(f"{u.qualified_name}: mult={show(u.multiplicity)} declared={show(getattr(u, 'declared_multiplicity', None))} "
          f"ordered={u.is_ordered} nonunique={u.is_nonunique} redefines={redefs}")
