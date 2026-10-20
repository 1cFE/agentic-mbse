package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    requirement def Limit { attribute cap : Real = 5.0; require constraint capped { cap > 0.0 } }
    part def Site { attribute x : Real = 1.0; calc t : Twice { in v = x; } }
    part site : Site;
}
