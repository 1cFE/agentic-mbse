// expect: PASS
// flagged: -
package 'calc_explicit_rename' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in local redefines a = 10; in b = 3; } }
}
