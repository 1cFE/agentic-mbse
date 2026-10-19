package fx {
    // A calc def with no output: L6_CALC_DEF_NO_OUTPUT, a native-correctness ERROR that
    // stays ERROR under every target.
    private import ScalarValues::*;
    calc def NoOut { in v : Real; }
    part def Site {
        attribute x : Real = 1.0;
        calc t : NoOut { in v = x; }
    }
    part site : Site;
}
