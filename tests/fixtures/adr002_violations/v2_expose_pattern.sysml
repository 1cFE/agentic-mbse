/**
 * ADR-002 V2: EXPOSE Pattern Test Cases
 *
 * Tests for the EXPOSE pattern exemption.
 * EXPOSE pattern: attribute x = calc.x (pure value propagation)
 *
 * Uses existing V2TestLibrary::SimpleCalc from library/simple_calc.sysml
 */
package ExposePatternTest {
    public import ScalarValues::*;
    public import V2TestLibrary::*;

    part expose_test_part {
        // Calc usage - valid
        calc my_calc : SimpleCalc {
            in input_val = 10.0;
        }

        // EXPOSE pattern - SHOULD be exempt from V2
        // Pure value propagation, no computation
        // Expression type: FeatureChainExpression (verified)
        attribute exposed_output : Real = my_calc.output_val;
    }

    part multi_ref_test {
        // Two calc usages
        calc calc1 : SimpleCalc { in input_val = 5.0; }
        calc calc2 : SimpleCalc { in input_val = 7.0; }

        // NOT EXPOSE pattern - multiple references
        // Expression type: OperatorExpression (addition)
        // This SHOULD still be flagged as V2 violation
        attribute combined : Real = calc1.output_val + calc2.output_val;
    }

    part mixed_ref_test {
        calc my_calc : SimpleCalc { in input_val = 5.0; }

        // Sibling attribute (true static)
        attribute sibling_a : Real = 10.0;

        // MIXED: sibling ref + calc output ref → SHOULD be V2 violation
        // _is_formula_pattern rejects because my_calc.output_val is a calc output ref
        attribute mixed : Real = sibling_a + my_calc.output_val;
    }
}
