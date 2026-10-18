package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        assert constraint c { (if x < y ? x else y) > 0.0 }
    }
    part site : Site;
}
