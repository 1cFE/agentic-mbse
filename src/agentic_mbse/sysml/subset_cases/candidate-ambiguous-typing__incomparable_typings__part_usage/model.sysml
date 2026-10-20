package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Base { attribute rate : Real default 1.0; calc t : Twice { in v = rate; } }
    part def A :> Base { :>> rate default 2.0; }
    part def B :> Base { :>> rate default 3.0; }
    part def Site { part unit : A, B; }
    part site : Site;
}
