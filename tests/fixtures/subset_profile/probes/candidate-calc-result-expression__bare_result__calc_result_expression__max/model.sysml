package fx {
    private import ScalarValues::*;
    calc def Big { in a : Real; in b : Real; return r : Real; ScalarFunctions::max(a, b) }
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        calc m : Big { in a = x; in b = y; }
    }
    part site : Site;
}
