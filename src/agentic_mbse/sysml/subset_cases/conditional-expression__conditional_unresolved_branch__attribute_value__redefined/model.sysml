package fx {
    private import ScalarValues::*;
    part def Base {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        attribute low : Real;
    }
    part def Site :> Base { attribute :>> low = if x < y ? x else y; }
    part site : Site;
}
