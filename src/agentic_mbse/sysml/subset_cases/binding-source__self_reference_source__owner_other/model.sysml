package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    item def Box {
        attribute a : Real = 1.0;
        calc t : Twice { in v = v; }
    }
    part def Site { attribute x : Real = 1.0; }
    part site : Site;
}
