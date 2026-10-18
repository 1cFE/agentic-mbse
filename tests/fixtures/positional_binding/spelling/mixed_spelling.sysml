// Fixture: spelling/mixed_spelling
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r1a_mixed_spelling_gives_b_an_implied_redefinition_of_sub_a
// `b` lands on Sub::a by position although `:>> a` also redefines Sub::a; the `:>>` input is not flagged.
// finding: mixed_spelling::q::c | b | mixed_spelling::Sub::a
// unverifiable: none
package mixed_spelling {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q { calc c : Sub { in b = 3; in :>> a = 10; } }
}
