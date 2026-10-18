package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute a : Real = 1.0;
        calc t : Twice { in v = v; }
    }
    part def Meter { attribute load : Real = 5.0; calc m : Twice { in v = load; } }
    part meter : Meter;
}
