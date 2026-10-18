package fx {
    private import ScalarValues::*;
    calc def Min2 { in a : Real; in b : Real; return r : Real = if a < b ? a else b; }
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        calc m : Min2 { in a = x; in b = y; }
    }
    part site : Site;
}
