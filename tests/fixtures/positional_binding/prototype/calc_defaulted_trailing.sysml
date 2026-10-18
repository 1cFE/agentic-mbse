// Fixture: prototype/calc_defaulted_trailing
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/calc_defaulted_trailing.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): calc_defaulted_trailing PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'calc_defaulted_trailing' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def SubD { in a : Real; in b : Real = 0.0; return r : Real = a - b; }
    part q { calc c : SubD { in a = 10; } }
}
