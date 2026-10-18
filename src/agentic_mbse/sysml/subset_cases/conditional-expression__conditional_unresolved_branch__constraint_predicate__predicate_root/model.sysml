package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute x : Real = 5.0;
        attribute flag : Boolean = true;
        assert constraint c { if flag ? x < 1.0 else x > 2.0 }
    }
    part holder : Holder;
}
