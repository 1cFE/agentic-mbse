package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel_unit : String = "liter"; attribute rate : Real = 2.0; calc t : Twice { in v = rate; } }
    part gen : Gen;
}
