// Fixture: requirements/requirement_def_without_subject
// Source: design Appendix A (D20); tests/learning/test_syside_input_redefinition.py::test_m4_the_first_ordinary_input_lands_on_the_library_subject_and_is_an_error
// SysIDE 0.8.4 reports this model as an error by design (requirement-definition-subject-parameter-position,
// "Subject must be the first input parameter"); learning-findings M4. `lo` lands on the library subject slot.
// finding: requirement_def_without_subject::X | lo | Requirements::RequirementCheck::subj | SPECIAL_SLOT
// unverifiable: none
package requirement_def_without_subject {
    private import ScalarValues::*;
    requirement def X { in lo : Real; in hi : Real; }
}
