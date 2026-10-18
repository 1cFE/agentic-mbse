package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute a : Real = 0.9;
        attribute b : Real = 0.8;
        calc t : Twice { in v = ScalarFunctions::max(a, b); }
    }
    part site : Site;
}
