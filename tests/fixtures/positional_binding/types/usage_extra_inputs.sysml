// Fixture: types/usage_extra_inputs
// Source: design Appendix A (spec Det-6: extra inputs near the old heuristic).
// `a` and `b` match by position; `extra` has no formal to land on and is a new parameter.
// finding: none
// unverifiable: none
package usage_extra_inputs {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q { calc c : Sub { in a = 10; in b = 3; in extra = 1; } }
}
