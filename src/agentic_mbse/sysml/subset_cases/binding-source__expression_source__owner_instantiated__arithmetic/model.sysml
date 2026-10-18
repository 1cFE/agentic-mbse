package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel_code : Real; attribute rate : Real; calc t : Twice { in v = rate * fuel_code; } }
    part gen : Gen { :>> fuel_code = 1.0; :>> rate = 2.0; }
}
