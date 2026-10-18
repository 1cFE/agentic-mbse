// expect: FLAG
// flagged: Sub2::b Sub2::a
package 'inherit_def_reordered' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub2 :> Sub { in b : Real; in a : Real; }
    part q { calc c : Sub2 { in b = 3; in a = 10; } }
}
