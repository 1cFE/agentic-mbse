package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute x : Real = 1.0;
        attribute k : Real = 3.0;
        calc c : Twice { in v = x; }
        attribute y : Real = c.r * k;
    }
    part site : Site;
}
