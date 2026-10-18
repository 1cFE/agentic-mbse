// Fixture: types/subpart_deliberate_rename
// Source: design Appendix A (S4); tests/learning/test_syside_input_redefinition.py::test_s4_a_parent_usage_without_inputs_leaves_the_definition_owning_the_formals
// `local` explicitly redefines Sub::a; `b` lands on Sub::b by position and matches.
// finding: none
// unverifiable: none
package subpart_deliberate_rename {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part def Q1 { calc c : Sub; }
    part def Q3 :> Q1 { calc :>> c { in local redefines a = 10; in b = 3; } }
}
