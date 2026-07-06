package BodyAssignLib {
    private import ScalarValues::*;

    // C2b negative fixture (Item 12): the body-assignment output form. `y` is
    // declared as a named output with no inline value, then assigned in the calc
    // body. Extraction keeps the channel but loses auto-impl -> WARN (L6 stays
    // passing).
    calc def BodyCalc {
        in attribute d : Real;
        return attribute y : Real;
        y = d * 5;
    }

    // C2b negative-of-the-negative: the inline output form carries its value on the
    // output member itself, so auto-impl is preserved -> must NOT fire.
    calc def InlineCalc {
        in attribute e : Real;
        out attribute z : Real = e * 6;
    }
}
