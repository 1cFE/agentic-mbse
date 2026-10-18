// Fixture: prototype/calc_omitted_first
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/calc_omitted_first.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): calc_omitted_first FLAG FLAG q::c::b yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: calc_omitted_first::q::c | b | calc_omitted_first::Sub::a
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: q::c::b
package 'calc_omitted_first' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { calc c : Sub { in b = 3; } }
}
