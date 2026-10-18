// Fixture: prototype/inherited_usage_redefined_in_subpart
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/inherited_usage_redefined_in_subpart.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): inherited_usage_redefined_in_subpart FLAG FLAG Q2::c::a Q2::c::b yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: inherited_usage_redefined_in_subpart::Q2::c | b | inherited_usage_redefined_in_subpart::Sub::a
// finding: inherited_usage_redefined_in_subpart::Q2::c | a | inherited_usage_redefined_in_subpart::Sub::b
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: Q2::c::b Q2::c::a
package 'inherited_usage_redefined_in_subpart' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part def Q1 { calc c : Sub; }
    part def Q2 :> Q1 { calc :>> c { in b = 3; in a = 10; } }
}
