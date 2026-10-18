package fx {
    private import ScalarValues::*;
    attribute def Pair { attribute a : Real; }
    part def Site {
        attribute p : Pair { :>> a = 1.0; }
        attribute y : Real = 2.0 * p.a;
    }
    part site : Site;
}
