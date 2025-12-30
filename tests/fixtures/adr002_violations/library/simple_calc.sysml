/**
 * Library calc def for V2 violation testing.
 *
 * This calc def is in library/ so its outputs can be cataloged.
 */
package V2TestLibrary {
    public import ScalarValues::*;

    calc def SimpleCalc {
        in attribute input_val : Real;
        out attribute output_val : Real = input_val * 2.0;
    }
}
