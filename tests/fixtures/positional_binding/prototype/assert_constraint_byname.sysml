// Fixture: prototype/assert_constraint_byname
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/assert_constraint_byname.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): assert_constraint_byname PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'assert_constraint_byname' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { assert constraint k : Le { in :>> lim = 5; in :>> x = 3; } }
}
