package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute fuel : Real = 1.5; attribute rate : Real = 2.0; calc t : Twice { in v = rate; }
        attribute label : Real = fuel; }
    part gen : Gen;
}
