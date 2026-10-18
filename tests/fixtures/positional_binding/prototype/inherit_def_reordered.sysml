// Fixture: prototype/inherit_def_reordered
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/inherit_def_reordered.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): inherit_def_reordered FLAG FLAG Sub2::a Sub2::b yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: inherit_def_reordered::Sub2 | b | inherit_def_reordered::Sub::a
// finding: inherit_def_reordered::Sub2 | a | inherit_def_reordered::Sub::b
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: Sub2::b Sub2::a
package 'inherit_def_reordered' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub2 :> Sub { in b : Real; in a : Real; }
    part q { calc c : Sub2 { in b = 3; in a = 10; } }
}
