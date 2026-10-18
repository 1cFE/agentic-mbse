// Fixture: types/def_adds_first_input
// Source: design Appendix A; tests/learning/test_syside_input_redefinition.py::test_r3_definition_to_definition_inheritance_is_positional_too
// A subdefinition's first new input lands on the supertype's first formal.
// finding: def_adds_first_input::D | c | def_adds_first_input::Sub::a
// unverifiable: none
package def_adds_first_input {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    calc def D :> Sub { in c : Real; }
}
