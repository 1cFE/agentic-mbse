// expect: PASS
// flagged: -
package 'calc_anonymous_inputs' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in : Real = 10; in : Real = 3; } }
}
