// Fixture: requirements/requirement_actor
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_special_parameters_are_inputs_told_apart_by_owning_membership_type
// The usage restates subject and actor (renamed) before the ordinary input; special roles are excluded.
// finding: none
// unverifiable: none
package requirement_actor {
    private import ScalarValues::*;
    part def V; part def D; part def O;
    requirement def R { subject v : V; actor d : D; in lo : Real; }
    part q { requirement r : R { subject v : V; actor drv : D; in lo = 1; } }
}
