// Fixture: out_before_in (design Appendix A; learning-findings R4)
// Source: tests/learning/test_syside_input_redefinition.py::test_r4_positions_count_an_out_parameter_and_syside_rejects_the_model
// Observed SysIDE 0.8.4: positions count the `out` parameter, so `a` lands on O::o and `b` on O::a.
// SysIDE reports `redefinition-direction-conformance` in `diagnostics.validation`, which no `validate` level reads (backlog VALIDATE-SEMA-DIAGNOSTICS).
// Current behavior, pinned by tests/test_validation/test_positional_binding.py::test_out_before_in_passes_l1_and_fails_l2_on_two_positional_errors:
// L1 passes; L2 fails with two positional errors, `a` → O::o and `b` → O::a. The design expected an L1 rejection (Det-6 row open for the owner).
package out_before_in {
    private import ScalarValues::*;
    calc def O { out o : Real; in a : Real; in b : Real; }
    part q { calc u : O { in a = 1; in b = 2; } }
}
