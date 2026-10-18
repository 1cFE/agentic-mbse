// expect: FLAG
// flagged: q::c::b q::c::a
package 'multiple_types' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Add { in p : Real; in q : Real; return r : Real = p + q; }
    part q { calc c : Sub, Add { in b = 3; in a = 10; } }
}
