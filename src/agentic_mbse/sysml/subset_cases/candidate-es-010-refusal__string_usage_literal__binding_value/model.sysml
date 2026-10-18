package fx {
    private import ScalarValues::*;
    calc def Labelled { in u : String; in v : Real; return r : Real = 2.0 * v; }
    part def Gen { attribute rate : Real; calc t : Labelled { in u = "liter"; in v = rate; } }
    part gen : Gen { :>> rate = 2.0; }
}
