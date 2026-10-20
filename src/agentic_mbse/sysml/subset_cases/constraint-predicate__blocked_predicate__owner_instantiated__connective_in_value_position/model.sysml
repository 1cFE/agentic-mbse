package Witness {
    private import ScalarValues::*;
    part def Holder {
        attribute flag : Boolean = true;
        attribute other : Boolean = false;
        assert constraint c { (flag xor other) == flag }
    }
    part holder : Holder;
}
