// expect: FLAG
// flagged: Q2::c::b Q2::c::a
package 'inherited_usage_redefined_in_subpart' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part def Q1 { calc c : Sub; }
    part def Q2 :> Q1 { calc :>> c { in b = 3; in a = 10; } }
}
