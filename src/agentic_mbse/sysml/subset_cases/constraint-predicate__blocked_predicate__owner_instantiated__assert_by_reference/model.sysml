package Witness {
    private import ScalarValues::*;
    constraint def Positive {
        in attribute observed : Real;
        observed > 0.0
    }
    part def Holder {
        attribute x : Real = 5.0;
        constraint positive : Positive {
            in observed = x;
        }
        assert constraint checked ::> positive;
    }
    part holder : Holder;
}
