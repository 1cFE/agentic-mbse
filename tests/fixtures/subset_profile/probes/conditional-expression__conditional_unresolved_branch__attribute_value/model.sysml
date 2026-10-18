package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        attribute low : Real = if x < y ? x else y;
    }
    part site : Site;
}
