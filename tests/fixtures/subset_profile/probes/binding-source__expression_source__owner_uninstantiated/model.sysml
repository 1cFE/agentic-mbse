package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc t : Total { in xs = (a, b); }
    }
    part def Meter { attribute load : Real = 5.0; calc m : Total { in xs = load; } }
    part meter : Meter;
}
