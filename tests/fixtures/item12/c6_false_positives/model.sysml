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
    //  - C6c: `out attribute powered = availability ^ 2` uses power INSIDE a calc
    //         def -> NOT V4_UNSUPPORTED_OPERATOR. Power is unsupported at design
    //         scope but legitimate in a calc def; the flat layout defeats the path
    //         skip, so the fix keys off the owner type (sibling of C6a).
    //  - C6d: `out attribute rooted = sqrt(availability)` invokes a function INSIDE
    //         a calc def -> NOT V4_STATIC_FUNCTION_INVOCATION. Same reasoning.
    calc def AvailabilityCalc {
        in attribute availability : Real;
        out attribute derated : Real = availability * 0.9;
        out attribute powered : Real = availability ^ 2;
        out attribute rooted : Real = sqrt(availability);
    }

    part def 'Trap Plant' {
        attribute availability : Real = 0.70;

        calc avail_calc : AvailabilityCalc {
            in availability = availability;
        }
    }
}
