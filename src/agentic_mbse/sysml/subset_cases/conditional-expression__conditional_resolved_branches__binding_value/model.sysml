package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        calc t : Twice { in v = if x < y ? 1.0 else 2.0; }
    }
    part site : Site;
}
