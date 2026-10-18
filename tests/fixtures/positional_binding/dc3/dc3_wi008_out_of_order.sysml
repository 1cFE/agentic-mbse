// Fixture: dc3/dc3_wi008_out_of_order
// Source: dc3 60b44d5 work/learnings/RAW_LEARNINGS.md:29 (`calc c : D { in b_in = y; in a_in = x; }` gives
// D(a_in = y, b_in = x); SysIDE -7 instead of 7) and work/active/WI-008_generator-idiom/design.md:63. Minimal model (D22).
// finding: dc3_wi008_out_of_order::p::c | b_in | dc3_wi008_out_of_order::D::a_in
// finding: dc3_wi008_out_of_order::p::c | a_in | dc3_wi008_out_of_order::D::b_in
// unverifiable: none
package dc3_wi008_out_of_order {
    private import ScalarValues::*;
    calc def D { in a_in : Real; in b_in : Real; return r : Real = a_in - b_in; }
    part p {
        attribute x : Real = 10.0;
        attribute y : Real = 3.0;
        calc c : D { in b_in = y; in a_in = x; }
    }
}
