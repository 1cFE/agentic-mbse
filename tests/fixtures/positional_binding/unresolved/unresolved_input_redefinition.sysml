// Fixture: unresolved/unresolved_input_redefinition
// Source: design Appendix A (D19); tests/learning/test_syside_input_redefinition.py::test_m1_unresolved_supertypes_and_redefinitions_also_target_placeholders
// The first input's `:>> zz` does not resolve: that input is unverifiable. `b` is still judged: it takes
// position 2 (Sub::b) and matches. SysIDE reports a reference-error diagnostic for this model by design.
// finding: none
// unverifiable: UNRESOLVED_INPUT_REDEFINITION @ unresolved_input_redefinition.sysml:12
package unresolved_input_redefinition {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q {
        calc c : Sub {
            in :>> zz = 1;
            in b = 3;
        }
    }
}
