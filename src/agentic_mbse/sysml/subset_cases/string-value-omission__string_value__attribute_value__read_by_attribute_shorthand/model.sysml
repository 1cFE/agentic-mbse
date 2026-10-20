package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel_unit : String; attribute label : String = fuel_unit; attribute rate : Real; calc t : Twice { in v = rate; } }
    part gen : Gen { :>> fuel_unit = "liter"; :>> rate = 2.0; }
}
