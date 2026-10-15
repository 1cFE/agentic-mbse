// expect: PASS
// flagged: -
package 'calc_in_order' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in a = 10; in b = 3; } }
}
