/**
 * ADR-002 V4 VIOLATION: Unsupported operator in static expression
 *
 * This file intentionally violates V4 to test detection.
 */
package V4ViolationTest {
    public import ScalarValues::*;

    part test_part {
        attribute base_value : Real = 2.0;

        // VIOLATION: ** (exponentiation) is not a supported operator
        // Should use a calc def for complex calculations
        attribute squared : Real = base_value ** 2;

        // Valid: uses only +, -, *, /
        attribute doubled : Real = base_value * 2.0;
    }
}
