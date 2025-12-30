// Test fixture: True static expressions (pure literals)
// This should NOT produce any V2 violations

package V2TrueStaticTest {
    public import ScalarValues::*;
    public import SI::*;

    part def TestPart {
        // True static: simple literal
        attribute pi_value : Real = 3.14159;

        // True static: literal arithmetic
        attribute pi_squared : Real = 3.14159 * 3.14159;

        // True static: compound literal expression
        attribute circumference_factor : Real = 2.0 * 3.14159;

        // True static: division of literals
        attribute half_pi : Real = 3.14159 / 2.0;
    }

    part designs::test_part : TestPart;
}
