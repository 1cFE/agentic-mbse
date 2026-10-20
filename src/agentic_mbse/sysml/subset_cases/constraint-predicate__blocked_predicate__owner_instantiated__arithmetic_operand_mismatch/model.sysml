package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute x : Real = 5.0;
        attribute flag : Boolean = true;
        assert constraint c { x + flag <= 1.0 }
    }
    part holder : Holder;
}
