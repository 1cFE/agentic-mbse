package Witness {
    private import ScalarValues::*;
    part def Holder {
        assert constraint c { 1.0 }
    }
    part holder : Holder;
}
