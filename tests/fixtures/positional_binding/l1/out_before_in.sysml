// Fixture: out_before_in (design Appendix A; learning-findings R4)
// Source: tests/learning/test_syside_input_redefinition.py::test_r4_positions_count_an_out_parameter_and_syside_rejects_the_model
// Observed SysIDE 0.8.4: positions count the `out` parameter, so `a` lands on O::o and
// `b` on O::a, and SysIDE reports `redefinition-direction-conformance` (a semantic
// diagnostic). Design expectation: `validate` rejects this model at L1.
// Phase 1 records whether it does (evidence/phase1-fixture-truth.md).
package out_before_in {
    private import ScalarValues::*;
    calc def O { out o : Real; in a : Real; in b : Real; }
    part q { calc u : O { in a = 1; in b = 2; } }
}
