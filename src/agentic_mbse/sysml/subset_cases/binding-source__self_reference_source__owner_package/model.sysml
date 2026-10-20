package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc t : Twice { in v = v; }
}
