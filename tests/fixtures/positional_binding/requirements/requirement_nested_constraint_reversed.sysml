// Fixture: requirements/requirement_nested_constraint_reversed
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_a_constraint_nested_in_a_requirement_is_an_ordinary_constraint_owner
// finding: requirement_nested_constraint_reversed::R::k | lim | requirement_nested_constraint_reversed::Le::x
// finding: requirement_nested_constraint_reversed::R::k | x | requirement_nested_constraint_reversed::Le::lim
// unverifiable: none
package requirement_nested_constraint_reversed {
    private import ScalarValues::*;
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part def V; part def D; part def O;
    requirement def R { subject v : V; require constraint k : Le { in lim = 5; in x = 3; } }
}
