// expect: PASS
// flagged: -
package 'assert_constraint_byname' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { assert constraint k : Le { in :>> lim = 5; in :>> x = 3; } }
}
