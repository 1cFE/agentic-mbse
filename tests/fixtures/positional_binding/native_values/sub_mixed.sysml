// Native-value fixture: mixed spelling (intended a - b = 10 - 3 = 7).
// Source: tests/learning/test_syside_input_redefinition.py::test_r1a_mixed_spelling_leaves_sub_b_unbound_and_native_evaluation_yields_nothing (SysIDE 0.8.4 native value: none).
// Evaluated by tests/test_validation/test_positional_binding_native_values.py.
package sub_mixed {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q {
        calc c : Sub { in b = 3; in :>> a = 10; }
        attribute v : Real = c.r;
    }
}
