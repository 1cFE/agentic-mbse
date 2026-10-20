package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Outer {
        in a : Real;
        in b : Real;
        calc t : Total { in xs = (a, b); }
        return r : Real = a + b;
    }
    part def Site { attribute x : Real = 1.0; calc o : Outer { in a = x; in b = x; } }
    part site : Site;
}
