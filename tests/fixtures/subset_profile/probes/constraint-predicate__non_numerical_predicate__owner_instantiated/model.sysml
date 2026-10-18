package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute x : Real = 1.0;
        attribute enabled : Boolean = true;
        assert constraint c { enabled }
        calc t : Twice { in v = x; }
    }
    part site : Site;
}
