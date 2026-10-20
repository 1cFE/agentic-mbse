package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute x : Real = 5.0;
        attribute flag : Boolean = true;
        assert constraint c { (x < 1.0) == flag }
    }
    part holder : Holder;
}
