import sys, pathlib
root = pathlib.Path(sys.argv[1]) / "cases"
HDR = "    private import ScalarValues::*;\n    calc def Dbl { in a : Real; return r : Real = a * 2; }\n"
FORMS = {
    "bare": ":>> {f} = {v};",
    "attr": "attribute :>> {f} = {v};",
    "redef": "redefines {f} = {v};",
    "attrredef": "attribute redefines {f} = {v};",
    "dflt": ":>> {f} default {v};",
}
def case(name, body):
    d = root / name; d.mkdir(parents=True)
    (d / "m.sysml").write_text("package M {\n" + HDR + body + "}\n")
HOST = lambda base: f"    part def Host {{\n        attribute x : Real{base};\n        attribute y : Real default 3.0;\n        calc d : Dbl {{ in a = x; }}\n    }}\n"
for k, f in FORMS.items():
    # usage, literal, base default
    case(f"u_{k}", HOST(" default 1.0") + f"    part h : Host {{ {f.format(f='x', v='5.0')} }}\n")
    # specializing def, literal
    case(f"d_{k}", HOST(" default 1.0") + f"    part def Sub :> Host {{ {f.format(f='x', v='5.0')} }}\n    part s : Sub;\n")
    # usage, expression reading sibling
    case(f"usib_{k}", HOST(" default 1.0") + f"    part h : Host {{ {f.format(f='x', v='y * 2')} }}\n")
    # specializing def, sibling expression
    case(f"dsib_{k}", HOST(" default 1.0") + f"    part def Sub :> Host {{ {f.format(f='x', v='y * 2')} }}\n    part s : Sub;\n")
    # usage, expression reading another part
    case(f"uoth_{k}", HOST(" default 1.0") + f"    part src {{ attribute k : Real = 7.0; }}\n    part h : Host {{ {f.format(f='x', v='src.k')} }}\n")
    # nested literal
    case(f"nest_{k}", HOST(" default 1.0") + f"    part def Outer {{ part inner : Host; }}\n    part o : Outer {{ {f.format(f='inner.x', v='5.0')} }}\n")
    # nested expression
    case(f"nestx_{k}", HOST(" default 1.0") + f"    part def Outer {{ attribute q : Real default 4.0; part inner : Host; }}\n    part o : Outer {{ {f.format(f='inner.x', v='q * 2')} }}\n")
    # base variants with usage override
    case(f"bnone_{k}", HOST("") + f"    part h : Host {{ {f.format(f='x', v='5.0')} }}\n")
    case(f"binit_{k}", HOST(" := 1.0") + f"    part h : Host {{ {f.format(f='x', v='5.0')} }}\n")
    case(f"beq_{k}", HOST(" = 1.0") + f"    part h : Host {{ {f.format(f='x', v='5.0')} }}\n")
    # two levels: def specializes def with form, then usage overrides with same form
    case(f"two_{k}", HOST(" default 1.0") + f"    part def Sub :> Host {{ {f.format(f='x', v='2.0')} }}\n    part s : Sub {{ {f.format(f='x', v='5.0')} }}\n    part s2 : Sub;\n")
    # integer
    case(f"int_{k}", "    part def IHost {\n        attribute n : Integer default 1;\n        calc d : Dbl { in a = n; }\n    }\n" + f"    part h : IHost {{ {f.format(f='n', v='4')} }}\n")
    # count, usage
    case(f"cntu_{k}", "    part def Wheel { attribute w : Real default 1.0; calc d : Dbl { in a = w; } }\n    part def Car {\n        attribute n : Integer default 2;\n        part wheels : Wheel[n];\n    }\n" + f"    part c : Car {{ {f.format(f='n', v='3')} }}\n")
    # count, specializing def
    case(f"cntd_{k}", "    part def Wheel { attribute w : Real default 1.0; calc d : Dbl { in a = w; } }\n    part def Car {\n        attribute n : Integer default 2;\n        part wheels : Wheel[n];\n    }\n" + f"    part def BigCar :> Car {{ {f.format(f='n', v='3')} }}\n    part c : BigCar;\n")
    # plain (no calc in the def), calc reads p.x from outside
    case(f"plain_{k}", "    part def P { attribute x : Real default 1.0; }\n    part sys {\n" + f"        part p : P {{ {f.format(f='x', v='5.0')} }}\n        calc d : Dbl {{ in a = p.x; }}\n    }}\n")
