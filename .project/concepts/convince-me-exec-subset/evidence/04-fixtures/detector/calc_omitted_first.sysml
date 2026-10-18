// expect: FLAG
// flagged: q::c::b
package 'calc_omitted_first' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in b = 3; } }
}
