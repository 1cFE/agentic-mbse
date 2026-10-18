// Fixture: prototype/assert_constraint_reversed
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/assert_constraint_reversed.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): assert_constraint_reversed FLAG FLAG q::k::lim q::k::x yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: assert_constraint_reversed::q::k | lim | assert_constraint_reversed::Le::x
// finding: assert_constraint_reversed::q::k | x | assert_constraint_reversed::Le::lim
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: q::k::lim q::k::x
package 'assert_constraint_reversed' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { assert constraint k : Le { in lim = 5; in x = 3; } }
}
