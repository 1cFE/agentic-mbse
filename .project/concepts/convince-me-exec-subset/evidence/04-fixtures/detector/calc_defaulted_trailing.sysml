// expect: PASS
// flagged: -
package 'calc_defaulted_trailing' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def SubD { in a : Real; in b : Real = 0.0; return r : Real = a - b; }
    part q { calc c : SubD { in a = 10; } }
}
