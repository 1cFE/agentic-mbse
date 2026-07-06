package C6Lib {
    private import ScalarValues::*;

    // C6 negative fixture (Item 12): reproduces the two Item-8 L6 false positives in
    // a FLAT layout (no library/ dir), so the checks cannot rely on the path skip.
    // Neither should fire after C6:
    //  - C6a: `out attribute derated = availability * 0.9` is a calc-def-internal
    //         derived expression -> NOT V2_DYNAMIC_EXPRESSION (ADR-002 says derived
    //         expressions belong in a calc def). The fix keys off the owner type.
    //  - C6b: 'Trap Plant' is a quoted name -> NOT L6_INVALID_QUALIFIED_NAME
    //         (codegen's Item-5 sanitization turns it into a valid identifier).
    calc def AvailabilityCalc {
        in attribute availability : Real;
        out attribute derated : Real = availability * 0.9;
    }

    part def 'Trap Plant' {
        attribute availability : Real = 0.70;

        calc avail_calc : AvailabilityCalc {
            in availability = availability;
        }
    }
}
