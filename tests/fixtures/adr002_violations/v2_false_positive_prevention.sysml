/**
 * Test fixture for V2 false positive prevention.
 *
 * Verifies that a static design attribute with the same name
 * as a calc output does NOT trigger V2 violation.
 *
 * The key case: "output_val" is a calc output name in V2TestLibrary::SimpleCalc,
 * but this file defines a STATIC attribute also named "output_val".
 * The V2 check should NOT flag this as a violation because it's a design
 * attribute, not a reference to the calc output.
 */
package V2FalsePositiveTest {
    public import ScalarValues::*;

    part test_part {
        // Static attribute with same name as a known calc output
        // "output_val" is defined in V2TestLibrary::SimpleCalc
        // This should NOT trigger V2 because it's a static literal value
        attribute output_val : Real = 100.0;

        // Reference the static attribute - should NOT trigger V2
        // because output_val here refers to the local static attribute,
        // not the calc output from SimpleCalc
        attribute doubled_output : Real = output_val * 2.0;
    }
}
