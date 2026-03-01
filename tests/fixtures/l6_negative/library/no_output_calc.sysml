/**
 * L6 negative test: calc def with no output parameter.
 * Should trigger L6_CALC_DEF_NO_OUTPUT.
 */
package NoOutputTest {
    import ScalarValues::*;

    calc def NoOutputCalc {
        in x : Real;
        in y : Real;
    }
}
