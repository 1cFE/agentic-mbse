package es {
    // One declared feature value per inventory role (sysml-codegen
    // expression_evidence.py:281-347), plus the two result-expression forms the inventory
    // does not enumerate.
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }       // calc_definition_dependency
    calc def Bare { in v : Real; v * 3.0 }                            // calc_result_expression
    constraint def Positive { in q : Real; q > 0.0 }                  // constraint_predicate
    part def P {
        attribute x : Real = 1.0;
        attribute mirror : Real = x;                                  // alias
        attribute scaled : Real = x * 2.0;                             // computed_attribute
        attribute product_value : Real = NumericalFunctions::product((x, x));
        calc t : Twice { in v = x; }                                  // binding
        calc anon { in q : Real = x; q + 1.0 }                        // other_expression_site
        constraint c : Positive { in q = x; }
    }
    part p : P;
}
