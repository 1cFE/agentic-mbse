import sys
from pathlib import Path
import syside
P = Path("/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/probe2")
ASK = {"u": [("M::Host::x", "M::h")], "usib": [("M::Host::x", "M::h")], "uoth": [("M::Host::x", "M::h")],
       "d": [("M::Host::x", "M::s")], "dsib": [("M::Host::x", "M::s")], "bnone": [("M::Host::x", "M::h")],
       "int": [("M::IHost::n", "M::h")], "cntu": [("M::Car::n", "M::c")], "cntd": [("M::Car::n", "M::c")],
       "cntw": [("M::Car::n", "M::c")], "twod": [("M::Host::x", "M::s"), ("M::Host::x", "M::s2")],
       "plain": [("M::P::x", "M::sys::p")]}
def kinds(model):
    out = []
    for el in model.elements(syside.Feature, include_subtypes=True):
        if el.owned_redefinitions and not str(getattr(el, "qualified_name", "")).startswith(("ScalarValues", "Base")):
            try: fv = el.feature_value_expression
            except Exception: fv = "?"
            reds = [str(getattr(r.redefined_feature, "qualified_name", None)) for r in el.owned_redefinitions]
            owner = el.owner
            out.append(f"{type(el).__name__} qn={el.qualified_name} owner={getattr(owner,'qualified_name',None)} redefines={reds} fv={'yes' if fv is not None else 'none'}")
    return out
for c in sys.argv[1:]:
    files = [str(p) for p in (P / "cases" / c).rglob("*.sysml")]
    try:
        model, _ = syside.load_model(files)
    except Exception as e:
        print(f"== {c}: load failed {str(e)[:150]}"); continue
    print(f"== {c}")
    for k in kinds(model):
        if "M::" in k: print("   ", k)
    els = {str(el.qualified_name): el for el in model.elements(syside.Element, include_subtypes=True) if getattr(el, "qualified_name", None) is not None}
    comp = syside.Compiler()
    for f, s in ASK.get(c.split("_")[0], []):
        v, rep = comp.evaluate_feature(els[f], scope=els[s], stdlib=model.lib)
        print(f"    native {f} in {s} -> {v!r} diags={[str(d.message) for d in rep.diagnostics]}")
