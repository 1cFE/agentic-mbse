package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute x : Real = 1.0;
        calc m : Twice { in v = x; if v < 1.0 ? v else 1.0 }
    }
    part site : Site;
}
