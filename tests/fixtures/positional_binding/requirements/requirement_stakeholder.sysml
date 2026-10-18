// Fixture: requirements/requirement_stakeholder
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_special_parameters_are_inputs_told_apart_by_owning_membership_type
// The usage restates subject and stakeholder (renamed) before the ordinary input; special roles are excluded.
// finding: none
// unverifiable: none
package requirement_stakeholder {
    private import ScalarValues::*;
    part def V; part def D; part def O;
    requirement def R { subject v : V; stakeholder o : O; in lo : Real; }
    part q { requirement r : R { subject v : V; stakeholder own : O; in lo = 1; } }
}
