// Fixture: prototype/calc_reversed_byname
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/calc_reversed_byname.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): calc_reversed_byname PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'calc_reversed_byname' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in :>> b = 3; in :>> a = 10; } }
}
