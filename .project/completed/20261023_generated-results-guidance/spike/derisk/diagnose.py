"""Diagnostics for the Phase 1 failures. Not pass conditions; they characterise each failure.

    ./codegen.sh derisk/diagnose.py      (from spike/)
"""

from __future__ import annotations

from pathlib import Path

import syside

HERE = Path(__file__).resolve().parent / "models"


def load(case):
    model, _ = syside.load_model([str(p) for p in sorted((HERE / case).rglob("*.sysml"))])
    els = {}
    for el in model.elements(syside.Element, include_subtypes=True):
        qn = getattr(el, "qualified_name", None)
        if qn is not None:
            els[str(qn)] = el
    return model, els


def ev(model, feature, scope, **kw):
    v, rep = syside.Compiler().evaluate_feature(feature, scope=scope, stdlib=model.lib, **kw)
    v = v if isinstance(v, (int, float, bool)) or v is None else repr(v)
    return v, [str(d.message) for d in rep.diagnostics]


def show(model, els, feature, scope, **kw):
    print(f"  evaluate_feature({feature}, scope={scope}{', ' + str(kw) if kw else ''}) -> {ev(model, els[feature], els[scope], **kw)}")


print("== outer_retyping: tripled under different scopes (meaning 21.0)")
m, e = load("outer_retyping")
for scope in ["OuterRetyping::HotMiddle::inner", "OuterRetyping::HotInner", "OuterRetyping::outer::middle", "OuterRetyping::outer"]:
    show(m, e, "OuterRetyping::Inner::tripled", scope)
show(m, e, "OuterRetyping::Inner::k", "OuterRetyping::HotMiddle::inner")

print("== named_subsets: rack_2's calc usage d (meaning d.y = 8.0)")
m, e = load("named_subsets")
show(m, e, "NamedSubsets::Double::y", "NamedSubsets::Rack::d")
show(m, e, "NamedSubsets::Rack::d", "NamedSubsets::Room::rack_2")
show(m, e, "NamedSubsets::Double::y", "NamedSubsets::Room::rack_2")
show(m, e, "NamedSubsets::Rack::capacity", "NamedSubsets::Room::rack_2")

print("== split_files: motor's calc usage t (meaning t.y = 12.0)")
m, e = load("split_files")
show(m, e, "SplitLib::Triple::y", "SplitLib::Motor::t")
show(m, e, "SplitLib::Motor::t", "SplitDesign::Cart::motor")
show(m, e, "SplitLib::Motor::boosted", "SplitDesign::Cart::motor")

print("== units_int_bool: unit annotations")
m, e = load("units_int_bool")
for f in ["UnitsIntBool::Box::double_mass", "UnitsIntBool::Box::double_grams", "UnitsIntBool::Box::mass", "UnitsIntBool::Box::grams"]:
    show(m, e, f, "UnitsIntBool::box")
    show(m, e, f, "UnitsIntBool::box", experimental_quantities=True)
