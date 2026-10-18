package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        assert constraint c { x > 0.0 and x < 2.0 }
    }
    part site : Site;
}
