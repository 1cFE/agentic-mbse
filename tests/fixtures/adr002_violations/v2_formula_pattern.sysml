/**
 * ADR-002 V2: FORMULA Pattern Test Cases
 *
 * Tests for the FORMULA pattern exemption per ADR-002 Amendment (2026-02-09).
 * FORMULA pattern: all feature refs are sibling attributes, no calc output refs.
 *
 * No library imports needed — all refs are local sibling attributes.
 */
package V2FormulaPatternTest {
    public import ScalarValues::*;

    part def FormulaTestPart {
        // Inputs (true static)
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute rate : Real = 12.0;

        // Simple FORMULA: sibling refs only → NO violation
        attribute area : Real = length * width;

        // Chain FORMULA: refs another computed attr → NO violation
        attribute cost : Real = area * rate;

        // FORMULA + literal: sibling ref mixed with literal → NO violation
        attribute p_net_kw : Real = length * 1000.0;
    }
}
