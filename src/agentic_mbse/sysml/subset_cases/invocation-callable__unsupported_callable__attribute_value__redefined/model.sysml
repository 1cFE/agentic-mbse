package fx {
    private import ScalarValues::*;
    part def Base { attribute a : Real = 1.0; attribute big : Real; }
    part def Site :> Base { attribute :>> big = ScalarFunctions::max(a, 2.0); }
    part site : Site;
}
