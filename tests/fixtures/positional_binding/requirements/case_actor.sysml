// Fixture: requirements/case_actor
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_special_parameters_are_inputs_told_apart_by_owning_membership_type (use case def)
// The use case usage restates subject and actor (renamed); special roles are excluded.
// finding: none
// unverifiable: none
package case_actor {
    private import ScalarValues::*;
    part def V; part def D; part def O;
    use case def UC { subject s : V; actor d : D; }
    part q { use case uc : UC { subject s2 : V; actor d2 : D; } }
}
