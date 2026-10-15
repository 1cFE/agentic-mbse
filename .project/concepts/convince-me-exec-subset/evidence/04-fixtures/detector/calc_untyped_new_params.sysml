// expect: PASS
// flagged: -
package 'calc_untyped_new_params' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c { in a : Real = 10; in b : Real = 3; return r : Real = a - b; } }
}
