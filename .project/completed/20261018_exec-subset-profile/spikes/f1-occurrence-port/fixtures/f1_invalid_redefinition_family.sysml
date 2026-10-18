package f1h {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc def Thrice { in v : Real; return r : Real = 3.0 * v; }
    part def Other { attribute y : Real = 2.0; calc c2 : Twice { in v = y; } }
    part o : Other { calc :>> c2 : Thrice { in v = y; } }
}
