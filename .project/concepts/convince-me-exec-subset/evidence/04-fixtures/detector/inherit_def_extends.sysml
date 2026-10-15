// expect: PASS
// flagged: -
package 'inherit_def_extends' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub4 :> Sub { in :>> a; in :>> b; in c : Real; }
    part q { calc c : Sub4 { in a = 10; in b = 3; in c = 1; } }
}
