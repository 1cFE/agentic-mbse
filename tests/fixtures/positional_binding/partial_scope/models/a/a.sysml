// Part of fixture partial_scope/ (expectations in partial_scope/expect.txt). Self-contained, so
// models/a/ can be validated alone (plan Phase 5 scope test). Inputs bind valued attributes so
// L2's literal-binding warnings do not mask the positional result.
package ScopeA {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q {
        attribute big : Real = 10.0;
        attribute small : Real = 3.0;
        calc c : Sub { in b = small; in a = big; }
        attribute result : Real = c.r;
    }
}
