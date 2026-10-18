package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc def Thrice { in v : Real; return r : Real = 3.0 * v; }
    part def Base { attribute x : Real = 1.0; calc c : Twice { in v = x * 2.0; } }
    part def Derived :> Base { calc :>> c : Thrice; }
    part d1 : Derived;
}
