package def_bare_expr {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Base {
        attribute y : Real = 5.0;
        attribute x : Real default 1.0;
        calc t : Twice { in v = x; }
    }
    part def Sub :> Base { :>> x = y * 3.0; }
    part p : Sub;
}
