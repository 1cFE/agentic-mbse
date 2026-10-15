// expect: FLAG
// flagged: q::c::b q::c::a
package 'inherit_def_no_params_usage_reversed' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub3 :> Sub;
    part q { calc c : Sub3 { in b = 3; in a = 10; } }
}
