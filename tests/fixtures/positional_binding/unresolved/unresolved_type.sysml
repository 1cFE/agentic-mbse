// Fixture: unresolved/unresolved_type
// Source: design Appendix A (D19); tests/learning/test_syside_input_redefinition.py::test_m1_the_owner_keeps_an_explicit_typing_to_a_shared_placeholder_classifier
// Both owners' types are typos, so SysIDE types them by a placeholder; their inputs must not read as new parameters.
// SysIDE reports reference-error diagnostics for this model by design.
// finding: none
// unverifiable: UNRESOLVED_OWNER_TYPE @ unresolved_type.sysml:13
// unverifiable: UNRESOLVED_OWNER_TYPE @ unresolved_type.sysml:14
package unresolved_type {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q {
        calc c : Sbu { in b = 3; in a = 10; }
        constraint k : Lee { in lim = 5; in x = 3; }
    }
}
