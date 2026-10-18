// Fixture: types/multiple_types_with_rename
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r3_an_explicit_input_with_several_types_gets_no_implied_redefinition
// `x` is explicit (no implied target); `b` takes position 2 of both types: Sub::b matches, Add::q does not.
// Nothing binds Add::p; that is an unbound formal, not a positional finding.
// finding: multiple_types_with_rename::q::c | b | multiple_types_with_rename::Add::q
// unverifiable: none
package multiple_types_with_rename {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    calc def Add { in p : Real; in q : Real; return r : Real = p + q; }
    part q { calc c : Sub, Add { in x redefines a = 10; in b = 3; } }
}
