package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    item def Box {
        attribute x : Real = 1.0;
        assert constraint c { x > 0.0 }
    }
    part def Site { attribute z : Real = 1.0; calc t : Twice { in v = z; } }
    part site : Site;
}
