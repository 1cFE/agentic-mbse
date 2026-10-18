package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part site { attribute a : Real = 1.0; calc t : Twice { in v = v; } }
}
