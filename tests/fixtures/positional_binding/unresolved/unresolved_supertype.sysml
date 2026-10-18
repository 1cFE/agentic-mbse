// Fixture: unresolved/unresolved_supertype
// Source: design Appendix A (D19); tests/learning/test_syside_input_redefinition.py::test_m1_unresolved_supertypes_and_redefinitions_also_target_placeholders
// SysIDE reports a reference-error diagnostic for this model by design.
// finding: none
// unverifiable: UNRESOLVED_OWNER_TYPE @ unresolved_supertype.sysml:8
package unresolved_supertype {
    private import ScalarValues::*;
    calc def D :> Missing { in c : Real; }
}
