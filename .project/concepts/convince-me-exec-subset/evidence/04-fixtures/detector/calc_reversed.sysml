// expect: FLAG
// flagged: q::c::b q::c::a
package 'calc_reversed' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in b = 3; in a = 10; } }
}
