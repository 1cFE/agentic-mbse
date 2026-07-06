package FormulaComputedDesign {
    private import ScalarValues::Real;
    private import FormulaComputedLibrary::*;

    // F6 negative-of-the-negative (Item 12): FORMULA computed attributes whose
    // refs are all same-part owned siblings are a codegen-supported wire (Item 5,
    // REQ-CA-06). None of these may fire V2_DYNAMIC_EXPRESSION.
    part MarginPart {
        attribute revenue : Real = 100.0;
        attribute cost : Real = 60.0;

        // FORMULA reading literal siblings -> supported, must NOT fire.
        attribute net_margin : Real = revenue - cost;

        // FORMULA reading a FORMULA sibling on the same part -> supported
        // (REQ-CA-06, FORMULA-to-FORMULA), must NOT fire.
        attribute total_payout : Real = net_margin * 2.0;
    }

    // F6 negative fixture: the genuinely-unsupported case must STILL fire. A
    // reference to a calc OUTPUT inside arithmetic (foreign namespace, dotted
    // path) is the dynamic-expression case codegen does not support.
    part DynamicPart {
        attribute base : Real = 10.0;

        calc scale : ScaleCalc {
            in value = base;
        }

        // References calc output `scale.result` in arithmetic -> V2 violation.
        attribute derated : Real = scale.result * 0.95;
    }
}
