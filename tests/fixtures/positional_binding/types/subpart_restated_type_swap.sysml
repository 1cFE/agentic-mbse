// Fixture: types/subpart_restated_type_swap
// Source: design Appendix A (S4 row 3); tests/learning/test_syside_input_redefinition.py::test_s4_restating_the_type_too_gives_targets_owned_by_both_usage_and_definition
// The redefining usage restates its type, so each input has two implied targets: one owned by Q1::c, one by Sub (D6).
// finding: subpart_restated_type_swap::Q4::c | b | subpart_restated_type_swap::Q1::c::a
// finding: subpart_restated_type_swap::Q4::c | b | subpart_restated_type_swap::Sub::a
// finding: subpart_restated_type_swap::Q4::c | a | subpart_restated_type_swap::Q1::c::b
// finding: subpart_restated_type_swap::Q4::c | a | subpart_restated_type_swap::Sub::b
// unverifiable: none
package subpart_restated_type_swap {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part def Q1 { calc c : Sub { in a; in b; } }
    part def Q4 :> Q1 { calc :>> c : Sub { in b = 3; in a = 10; } }
}
