package fx {
    private import ScalarValues::*;
    calc def Labelled { in u : String; in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel_unit : String; attribute rate : Real; calc t : Labelled { in u = fuel_unit; in v = rate; } }
    part gen : Gen { :>> fuel_unit = "liter"; :>> rate = 2.0; }
}
