// Fixture: prototype/calc_explicit_rename
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/calc_explicit_rename.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): calc_explicit_rename PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'calc_explicit_rename' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in local redefines a = 10; in b = 3; } }
}
