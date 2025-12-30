/**
 * ADR-002 V1 VIOLATION: Calc def in designs/ instead of library/
 *
 * This file intentionally violates V1 to test detection.
 */
package V1ViolationTest {
    public import ScalarValues::*;

    // VIOLATION: Calc def should be in library/, not here in designs/
    calc def InvalidCalcLocation {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    part test_part {
        calc invalid_calc : InvalidCalcLocation {
            in x = 5.0;
        }
    }
}
