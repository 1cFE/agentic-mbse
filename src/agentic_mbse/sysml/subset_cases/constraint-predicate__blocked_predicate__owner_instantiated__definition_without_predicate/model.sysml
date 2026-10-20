package Witness {
    private import ScalarValues::*;
    constraint def Empty {
        in attribute observed : Real;
    }
    part def Holder {
        attribute x : Real = 5.0;
        assert constraint c : Empty {
            in observed = x;
        }
    }
    part holder : Holder;
}
