// Fixture: requirements/requirement_in_param_swapped
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_subject_counts_toward_positions_of_the_other_inputs
// With the subject restated, the swapped ordinary inputs land on each other's formals.
// finding: requirement_in_param_swapped::q::r | hi | requirement_in_param_swapped::R::lo
// finding: requirement_in_param_swapped::q::r | lo | requirement_in_param_swapped::R::hi
// unverifiable: none
package requirement_in_param_swapped {
    private import ScalarValues::*;
    part def V; part def D; part def O;
    requirement def R { subject v : V; in lo : Real; in hi : Real; }
    part q { requirement r : R { subject v : V; in hi = 3; in lo = 1; } }
}
