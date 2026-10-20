package fx {
    // Item 2a case indexed-reference__indexed_reference__calc_result_expression: one unconfirmed pair.
    private import ScalarValues::*;
    calc def First { in xs : Real[2]; return r : Real; xs#(1) }
    part def Site { attribute a : Real = 1.0; }
    part site : Site;
}
