// expect: PASS
// flagged: -
package 'calc_reversed_redefines_keyword' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in redefines b = 3; in redefines a = 10; } }
}
