package anon {
    private import ScalarValues::*;
    constraint def Positive { in observed : Real; observed > 0.0 }
    part def Site {
        attribute x : Real = 1.0;
        constraint positive : Positive { in observed = x; }
        assert positive;
        assert constraint named_check : Positive { in observed = x; }
    }
    part site : Site;
}
