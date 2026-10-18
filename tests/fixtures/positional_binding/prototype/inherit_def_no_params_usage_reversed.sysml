// Fixture: prototype/inherit_def_no_params_usage_reversed
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/inherit_def_no_params_usage_reversed.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): inherit_def_no_params_usage_reversed FLAG FLAG q::c::a q::c::b yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: inherit_def_no_params_usage_reversed::q::c | b | inherit_def_no_params_usage_reversed::Sub::a
// finding: inherit_def_no_params_usage_reversed::q::c | a | inherit_def_no_params_usage_reversed::Sub::b
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: q::c::b q::c::a
package 'inherit_def_no_params_usage_reversed' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub3 :> Sub;
    part q { calc c : Sub3 { in b = 3; in a = 10; } }
}
