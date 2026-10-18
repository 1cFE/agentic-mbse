package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Total2 { in xs : Real[0..*] ordered nonunique; return r : Real = 2.0 * NumericalFunctions::sum(xs); }
    part def Base { attribute a : Real = 1.0; attribute b : Real = 2.0; calc t : Total { in xs = (a, b); } }
    part def Derived :> Base { calc :>> t : Total2; }
    part d1 : Derived;
}
