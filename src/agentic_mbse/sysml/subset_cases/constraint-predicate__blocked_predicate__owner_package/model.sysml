package fx {
    private import ScalarValues::*;
    attribute x : Real = 1.0;
    attribute enabled : Boolean = true;
    assert constraint c { x > 0.0 and enabled }
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    calc t : Twice { in v = x; }
}
