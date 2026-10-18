// Fixture: prototype/calc_anonymous_inputs
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/calc_anonymous_inputs.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): calc_anonymous_inputs PASS PASS - yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: none
// unverifiable: none
// The two lines below are the prototype's own header.
// expect: PASS
// flagged: -
package 'calc_anonymous_inputs' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in : Real = 10; in : Real = 3; } }
}
