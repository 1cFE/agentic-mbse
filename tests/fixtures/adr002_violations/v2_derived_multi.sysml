// Test fixture: Multiple design attribute references (DERIVED EXPRESSION)
// This SHOULD produce a V2 violation per ADR-002 Amendment

package V2DerivedMultiTest {
    public import ScalarValues::*;
    public import SI::*;

    part def TestPart {
        // Static inputs - these are fine (true static)
        attribute major_radius : Real = 3.0;
        attribute minor_radius : Real = 1.0;
        attribute elongation : Real = 1.8;

        // VIOLATION: derived expression with multiple design attribute refs
        // This should be extracted to a calc def
        attribute volume : Real = 2.0 * 3.14159 * 3.14159 * major_radius * minor_radius * minor_radius * elongation;
    }

    part designs::test_part : TestPart;
}
