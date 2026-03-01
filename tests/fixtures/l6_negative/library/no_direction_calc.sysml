/**
 * L6 negative test: calc def with a parameter missing direction marker.
 * Should trigger L6_CALC_DEF_NO_DIRECTION (WARNING).
 */
package NoDirectionTest {
    import ScalarValues::*;

    calc def NoDirectionCalc {
        x : Real;
        out result : Real;
    }
}
