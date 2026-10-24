import sys, pathlib
root = pathlib.Path(sys.argv[1]) / "cases"
HDR = "    private import ScalarValues::*;\n    calc def Dbl { in a : Real; return r : Real = a * 2; }\n"
FORMS = {"bare": ":>> {f} = {v};","attr": "attribute :>> {f} = {v};","redef": "redefines {f} = {v};","attrredef": "attribute redefines {f} = {v};","dflt": ":>> {f} default {v};"}
def case(name, body):
    d = root / name; d.mkdir(parents=True, exist_ok=True)
    (d / "m.sysml").write_text("package M {\n" + HDR + body + "}\n")
HOST = "    part def Host {\n        attribute x : Real default 1.0;\n        attribute y : Real default 3.0;\n        calc d : Dbl { in a = x; }\n    }\n"
for k, f in FORMS.items():
    case(f"twod_{k}", HOST + f"    part def Sub :> Host {{ :>> x default 2.0; }}\n    part s : Sub {{ {f.format(f='x', v='5.0')} }}\n    part s2 : Sub;\n")
    # count via usage, but usage also redefines wheels (so the multiplicity owner is the usage)
    case(f"cntw_{k}", "    part def Wheel { attribute w : Real default 1.0; calc d : Dbl { in a = w; } }\n    part def Car {\n        attribute n : Integer default 2;\n        part wheels : Wheel[n];\n    }\n" + f"    part c : Car {{ {f.format(f='n', v='3')} part :>> wheels : Wheel[n]; }}\n")
case("beq_none", HOST.replace("x : Real default 1.0", "x : Real = 1.0") + "    part h : Host;\n")
case("binit_none", HOST.replace("x : Real default 1.0", "x : Real := 1.0") + "    part h : Host;\n")
case("bdflt_none", HOST + "    part h : Host;\n")
