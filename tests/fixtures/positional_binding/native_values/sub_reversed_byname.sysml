// Native-value fixture: reversed explicit :>> (intended a - b = 10 - 3 = 7).
// Source: .project/concepts/convince-me-exec-subset/evidence/04-eval.py SPELLINGS and 04-eval.log (SysIDE 0.8.4 native value: 7).
// Evaluated by tests/test_validation/test_positional_binding_native_values.py.
package sub_reversed_byname {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q {
        calc c : Sub { in :>> b = 3; in :>> a = 10; }
        attribute v : Real = c.r;
    }
}
