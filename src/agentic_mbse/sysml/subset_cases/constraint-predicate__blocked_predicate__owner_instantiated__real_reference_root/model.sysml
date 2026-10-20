package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute x : Real = 5.0;
        assert constraint c { x }
    }
    part holder : Holder;
}
