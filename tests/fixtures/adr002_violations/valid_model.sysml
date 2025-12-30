/**
 * ADR-002 COMPLIANT: No violations
 *
 * This file demonstrates proper ADR-002 compliance.
 * Per ADR-002 Amendment (2025-12-22): Only TRUE STATIC expressions allowed.
 */
package ValidModelTest {
    public import ScalarValues::*;
    public import SI::*;

    part test_part {
        // True static: literals only
        attribute radius : Real = 3.0;
        attribute height : Real = 10.0;

        // True static: literal arithmetic (no refs)
        attribute pi_value : Real = 3.14159;
        attribute two_pi : Real = 2.0 * 3.14159;

        // True static: unit annotation (SI:: refs filtered)
        attribute length : Real = 5.0 [m];
    }
}
