package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    attribute def A { attribute d : Real = 1.0; constraint dpos { d > 0.0 } }
    part def Site { attribute x : Real = 1.0; calc t : Twice { in v = x; } }
    part site : Site;
}
