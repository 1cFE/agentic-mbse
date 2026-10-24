/**
 * L6 negative test: calc def with no output parameter.
 * L6 no longer checks this (ADR 0006); the generator refuses it.
 */
package NoOutputTest {
    import ScalarValues::*;

    calc def NoOutputCalc {
        in x : Real;
        in y : Real;
    }
}
