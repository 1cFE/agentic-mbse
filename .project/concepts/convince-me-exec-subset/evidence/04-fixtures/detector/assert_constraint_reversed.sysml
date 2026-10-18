// expect: FLAG
// flagged: q::k::lim q::k::x
package 'assert_constraint_reversed' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { assert constraint k : Le { in lim = 5; in x = 3; } }
}
