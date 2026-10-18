// Fixture: prototype/inherit_def_extends
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/inherit_def_extends.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): inherit_def_extends PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'inherit_def_extends' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Sub4 :> Sub { in :>> a; in :>> b; in c : Real; }
    part q { calc c : Sub4 { in a = 10; in b = 3; in c = 1; } }
}
