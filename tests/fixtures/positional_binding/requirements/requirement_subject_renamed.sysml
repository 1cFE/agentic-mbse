// Fixture: requirements/requirement_subject_renamed
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r2_a_renamed_usage_subject_implicitly_redefines_the_definition_subject
// `veh` lands on R::v and the library subj, but it is a subject: role-excluded. `lo`, `hi` match.
// finding: none
// unverifiable: none
package requirement_subject_renamed {
    private import ScalarValues::*;
    part def V; part def D; part def O;
    requirement def R { subject v : V; in lo : Real; in hi : Real; }
    part q { requirement r : R { subject veh : V; in lo = 1; in hi = 3; } }
}
