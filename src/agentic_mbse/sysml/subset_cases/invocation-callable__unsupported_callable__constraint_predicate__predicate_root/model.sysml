package Witness {
    private import ScalarValues::*;
    calc def Check { in v : Real; return ok : Boolean = v < 1.0; }
    part def Holder {
        attribute x : Real = 5.0;
        assert constraint c { Check(x) }
    }
    part holder : Holder;
}
