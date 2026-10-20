package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Spare {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        attribute low : Real = if x < y ? x else y;
    }
    part def Site { attribute z : Real = 1.0; calc t : Twice { in v = z; } }
    part site : Site;
}
