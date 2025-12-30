// Test fixture: Single design attribute reference (DERIVED EXPRESSION)
// This SHOULD produce a V2 violation per ADR-002 Amendment

package V2DerivedSingleTest {
    public import ScalarValues::*;
    public import SI::*;

    part def TestPart {
        // Static input - this is fine (true static)
        attribute radius : Real = 5.0;

        // VIOLATION: derived expression referencing design attribute
        // This should be extracted to a calc def
        attribute diameter : Real = radius * 2.0;
    }

    part designs::test_part : TestPart;
}
