package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Spare {
        attribute xs : Real[2] = (1.0, 2.0);
        attribute head : Real = xs#(1);
    }
    part def Site { attribute z : Real = 1.0; calc t : Twice { in v = z; } }
    part site : Site;
}
