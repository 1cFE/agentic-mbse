package Witness {
    private import ScalarValues::*;
    part def Holder {
        part sensor { attribute ok : Boolean = true; }
        assert constraint c { sensor.ok }
    }
    part holder : Holder;
}
