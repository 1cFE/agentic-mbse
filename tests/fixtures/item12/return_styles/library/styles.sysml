package ReturnStylesLib {
    private import ScalarValues::*;

    // C2a negative-of-the-negative (Item 12): the four legal output forms codegen
    // now accepts (Item 3). None is anonymous, so C2a must NOT fire. StyleD's
    // body-assignment is the C2b WARN case, not a C2a FAIL.
    calc def ControlA {
        in attribute a : Real;
        out attribute y : Real = a * 2;
    }

    calc def NamedReturnB {
        in attribute b : Real;
        return y : Real = b * 3;
    }

    calc def BareInC {
        in x : Real;
        out attribute y : Real = x * 4;
    }

    calc def StyleD {
        in attribute d : Real;
        return attribute y : Real;
        y = d * 5;
    }
}
