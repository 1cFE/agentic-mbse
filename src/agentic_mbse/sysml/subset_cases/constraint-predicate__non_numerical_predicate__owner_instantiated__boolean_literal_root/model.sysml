package Witness {
    private import ScalarValues::*;
    part def Holder {
        assert constraint c { true }
    }
    part holder : Holder;
}
