// Fixture: requirements/case_def_without_subject
// Source: design Appendix A (D20); tests/learning/test_syside_input_redefinition.py::test_p1_the_library_subject_a_subject_less_case_def_lands_on_reads_subject_membership
// SysIDE 0.8.4 reports this model as an error by design (case-definition-subject-parameter-position); learning-findings M4.
// finding: case_def_without_subject::X | lo | Cases::Case::subj | SPECIAL_SLOT
// unverifiable: none
package case_def_without_subject {
    private import ScalarValues::*;
    case def X { in lo : Real; in hi : Real; }
}
