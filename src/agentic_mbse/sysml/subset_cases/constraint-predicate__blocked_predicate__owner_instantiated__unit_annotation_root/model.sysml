package Witness {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;
    part def Holder {
        assert constraint c { 1 [m] }
    }
    part holder : Holder;
}
