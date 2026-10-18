// Fixture: prototype/multiple_types
// Source: .project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/multiple_types.sysml (copied unchanged below this header)
// Prototype result (04-detector-fixtures.log): multiple_types FLAG FLAG q::c::a q::c::b yes
// Expected positional findings, one per (owner, input, target), reason SWAP unless stated:
// finding: multiple_types::q::c | b | multiple_types::Sub::a
// finding: multiple_types::q::c | b | multiple_types::Add::p
// finding: multiple_types::q::c | a | multiple_types::Sub::b
// finding: multiple_types::q::c | a | multiple_types::Add::q
// unverifiable: none
// naive-control: wrong (04-detector-naive-control.log)
// The two lines below are the prototype's own header.
// expect: FLAG
// flagged: q::c::b q::c::a
package 'multiple_types' {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    calc def Add { in p : Real; in q : Real; return r : Real = p + q; }
    part q { calc c : Sub, Add { in b = 3; in a = 10; } }
}
