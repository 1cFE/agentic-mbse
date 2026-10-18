// Fixture: spelling/reversed_deliberate_rename
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r1b_explicit_redefines_keyword_inputs_carry_no_implied_redefinition
// Both inputs are deliberate renames with explicit `redefines`, so neither has an implied target.
// finding: none
// unverifiable: none
package reversed_deliberate_rename {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q { calc c : Sub { in y redefines b = 3; in x redefines a = 10; } }
}
