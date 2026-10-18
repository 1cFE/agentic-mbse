// Fixture: unresolved/unresolved_subsetting
// Source: audit Advisory 1; tests/learning/test_syside_input_redefinition.py::test_a1_an_unresolved_subsetting_target_is_a_placeholder_and_inputs_look_new
// Both owners subset a feature that does not exist, so SysIDE subsets a placeholder; their reversed inputs must not read as new parameters.
// SysIDE reports reference-error diagnostics for this model by design.
// finding: none
// unverifiable: UNRESOLVED_OWNER_TYPE @ unresolved_subsetting.sysml:14
// unverifiable: UNRESOLVED_OWNER_TYPE @ unresolved_subsetting.sysml:15
package unresolved_subsetting {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q {
        calc s : Sub;
        calc c :> missing { in b = 3; in a = 10; }
        constraint k subsets missing2 { in lim = 5; in x = 3; }
    }
}
