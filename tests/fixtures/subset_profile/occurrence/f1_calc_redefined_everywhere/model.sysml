package f1f {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc def Thrice { in v : Real; return r : Real = 3.0 * v; }
    part def Base { attribute x : Real = 1.0; calc c : Twice { in v = x; } }
    part def Derived :> Base { calc :>> c : Thrice; }
    part d1 : Derived;
    part d2 : Derived;
    part def Other { attribute y : Real = 2.0; calc c2 : Twice { in v = y; } }
    part o : Other { calc :>> c2 : Thrice; }
    part o2 : Other;
    attribute z : Real = 4.0;
    calc pc : Twice { in v = z; }
}
