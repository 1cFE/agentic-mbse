package fx {
    private import ScalarValues::*;
    attribute enabled : Boolean = true;
    assert constraint c { enabled }
    part def Site { attribute y : Real = 1.0; }
    part site : Site;
}
