package fx {
    private import ScalarValues::*;
    calc def Labelled { in v : Real; in u : String; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel_unit : String = "liter"; attribute rate : Real = 2.0; calc t : Labelled { in v = rate; in u = fuel_unit; } }
    part gen : Gen;
}
