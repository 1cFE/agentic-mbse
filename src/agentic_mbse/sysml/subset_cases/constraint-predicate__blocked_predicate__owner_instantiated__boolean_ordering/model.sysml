package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute flag : Boolean = true;
        assert constraint c { flag < 1.0 }
    }
    part holder : Holder;
}
