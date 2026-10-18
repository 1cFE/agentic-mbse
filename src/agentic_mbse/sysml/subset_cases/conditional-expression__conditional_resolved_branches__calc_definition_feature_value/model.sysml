package fx {
    private import ScalarValues::*;
    calc def Pick { in a : Real; in b : Real; return r : Real = if a < b ? 1.0 else 2.0; }
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        calc m : Pick { in a = x; in b = y; }
    }
    part site : Site;
}
