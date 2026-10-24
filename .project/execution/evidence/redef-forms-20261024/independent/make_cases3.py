import sys, pathlib
root = pathlib.Path(sys.argv[1]) / "cases"
HDR = "    private import ScalarValues::*;\n    calc def Dbl { in a : Real; return r : Real = a * 2; }\n"
HOST = "    part def Host {\n        attribute x : Real default 1.0;\n        calc d : Dbl { in a = x; }\n    }\n"
def case(name, body):
    d = root / name; d.mkdir(parents=True, exist_ok=True)
    (d / "m.sysml").write_text("package M {\n" + HDR + HOST + body + "}\n")
case("xnest_neg", "    part def Outer { part inner : Host; }\n    part o : Outer { :>> inner.x = -5.0; }\n")
case("xnest_const", "    part def Outer { part inner : Host; }\n    part o : Outer { :>> inner.x = 2.0 * 4.0; }\n")
case("xnest_other", "    part src { attribute k : Real = 7.0; }\n    part def Outer { part inner : Host; }\n    part o : Outer { :>> inner.x = src.k; }\n")
case("xnest_deep2", "    part def Mid { part inner : Host; }\n    part def Outer { part mid : Mid; }\n    part o : Outer { :>> mid.inner.x = 5.0; }\n")
case("xnest_indef", "    part def Outer { part inner : Host; }\n    part def Outer2 :> Outer { :>> inner.x = 5.0; }\n    part o : Outer2;\n")
case("xnest_long", "    part def Outer { part inner : Host; }\n    part o : Outer { part :>> inner { :>> x = 2.0 * 4.0; } }\n")
