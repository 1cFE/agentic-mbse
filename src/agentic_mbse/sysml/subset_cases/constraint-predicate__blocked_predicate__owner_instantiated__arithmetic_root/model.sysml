package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute x : Real = 5.0;
        assert constraint c { x + 1.0 }
    }
    part holder : Holder;
}
