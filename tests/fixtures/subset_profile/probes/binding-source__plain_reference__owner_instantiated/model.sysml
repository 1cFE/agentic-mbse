package fx {
    private import ScalarValues::*;
    calc def Total2 { in x1 : Real; in x2 : Real; return r : Real = x1 + x2; }
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc t : Total2 { in x1 = a; in x2 = b; }
    }
    part site : Site;
}
