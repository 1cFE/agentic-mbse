// Fixture: requirements/anonymous_assert_reversed
// Source: design Appendix A (D9); tests/learning/test_syside_input_redefinition.py::test_p1_an_anonymous_assert_owner_has_no_qualified_name_through_element_ref
// The owner has no qualified name, so each finding has no identity (`<none>` owner) and can never be pinned.
// finding: <none> | lim | anonymous_assert_reversed::Le::x
// finding: <none> | x | anonymous_assert_reversed::Le::lim
// unverifiable: none
package anonymous_assert_reversed {
    private import ScalarValues::*;
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    part q { assert constraint : Le { in lim = 5; in x = 3; } }
}
