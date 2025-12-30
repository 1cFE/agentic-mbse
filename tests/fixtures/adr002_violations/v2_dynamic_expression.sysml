/**
 * ADR-002 V2 VIOLATION: Design attribute references calc output
 *
 * This file intentionally violates V2 to test detection.
 * Uses calc def from library/simple_calc.sysml.
 */
package V2ViolationTest {
    public import ScalarValues::*;
    public import V2TestLibrary::*;

    part test_part {
        // Calc usage - valid (uses calc def from library/)
        calc my_calc : SimpleCalc {
            in input_val = 10.0;
        }

        // VIOLATION: Design attribute references calc output
        // This should be a calc def, not a static expression
        attribute derived_value : Real = my_calc.output_val * 0.95;
    }
}
