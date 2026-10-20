package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    constraint def Bounded { in q : Real; constraint inner { q < 10.0 } q > 0.0 }
    part def Site { attribute x : Real = 1.0; calc t : Twice { in v = x; } }
    part site : Site;
}
