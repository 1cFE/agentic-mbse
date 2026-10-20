package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc def Bare { in v : Real; 2.0 * v }
    part def Site { attribute x : Real = 1.0; calc t : Twice { in v = x; } }
    part site : Site;
}
