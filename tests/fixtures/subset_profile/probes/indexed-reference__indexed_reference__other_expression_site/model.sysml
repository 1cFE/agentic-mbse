package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Q { attribute v : Real = 1.0; }
    part def Site {
        attribute x : Real = 1.0;
        part qs : Q[2];
        calc m : Twice { in v = x; qs#(1).v + 4272.5 }
    }
    part site : Site;
}
