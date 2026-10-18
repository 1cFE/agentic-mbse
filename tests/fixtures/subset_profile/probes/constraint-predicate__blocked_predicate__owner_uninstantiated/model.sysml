package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute x : Real = 1.0;
        attribute enabled : Boolean = true;
        assert constraint c { x > 0.0 and enabled }
    }
    part def Meter { attribute load : Real = 5.0; calc m : Twice { in v = load; } }
    part meter : Meter;
}
