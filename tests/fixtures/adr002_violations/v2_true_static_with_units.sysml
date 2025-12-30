// Test fixture: True static expressions WITH unit annotations
// This should NOT produce any V2 violations
// Unit annotations contain SI:: refs which are filtered by Phase 1

package V2TrueStaticUnitsTest {
    public import ScalarValues::*;
    public import SI::*;

    part def TestPart {
        // True static with unit: length (SI::metre)
        attribute length : Real = 3.0 [m];

        // True static with unit: mass (SI::kilogram)
        attribute mass : Real = 1000.0 [kg];

        // True static with unit: time (SI::second)
        attribute time_val : Real = 60.0 [s];

        // True static: literal arithmetic (no units)
        attribute double_value : Real = 2.0 * 3.0;
    }

    part designs::test_part : TestPart;
}
