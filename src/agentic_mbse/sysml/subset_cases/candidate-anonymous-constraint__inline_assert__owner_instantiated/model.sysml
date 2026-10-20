package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        assert constraint { x > 0.0 }
    }
    part site : Site;
}
