package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    item def Fuel { attribute d : Real = 1.0; }
    part def Site {
        attribute x : Real = 1.0;
        calc t : Twice { in v = x; }
        item fuel : Fuel { assert constraint dpos { d > 0.0 } }
    }
    part site : Site;
}
