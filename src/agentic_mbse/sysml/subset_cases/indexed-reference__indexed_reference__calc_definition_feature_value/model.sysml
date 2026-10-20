package fx {
    private import ScalarValues::*;
    calc def First { in xs : Real[2]; return r : Real = xs#(1); }
    part def Site {
        attribute a : Real = 1.0;
    }
    part site : Site;
}
