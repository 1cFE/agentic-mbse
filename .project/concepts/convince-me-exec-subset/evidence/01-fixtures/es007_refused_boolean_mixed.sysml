package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        attribute enabled : Boolean = true;
        assert constraint c { x > 0.0 and enabled }
    }
    part site : Site;
}
