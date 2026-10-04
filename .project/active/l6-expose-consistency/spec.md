# Spec: L6 EXPOSE Validation Consistency

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** MEDIUM
**Branch:** harness-right-size
**Backlog Item:** L6-EXPOSE-CONSISTENCY

## Problem

[INHERITED: ../../reports/2026-10-04-0901-status-report.md] Current validation contradicts the shipped EXPOSE pattern: a design attribute directly bound to a calculation output is accepted by static-expression classification but rejected by supported-operator and design-attribute-completeness checks. The October 4 live-parser reproduction returns `V4_UNSUPPORTED_OPERATOR` for `.` and `L6_DESIGN_ATTR_UNEXTRACTABLE` for `output_val` on `exposed_output`. Users following the documented binding pattern receive architecture errors for supported dataflow.

## Success Criteria

- [ ] [INHERITED: ../../reports/2026-10-04-0901-status-report.md] The retained `tests/fixtures/adr002_violations/v2_expose_pattern.sysml` reproduction produces neither false-positive diagnostic for its valid exposed output, through the individual checks and the combined L6 route in a checked design location.
- [ ] [INHERITED: ../../../docs/patterns/expose-pattern.md] Pure EXPOSE bindings on part definitions and part usages remain accepted; arithmetic over a calculation output remains rejected as a derived expression.
- [ ] [INFERRED] Controls prove that unsupported operators, absent design values/bindings, unextractable static defaults, and invalid reference targets still receive their applicable diagnostics. The fix does not admit an arbitrary dotted reference merely because it contains `.`.

## Known Requirements

- **[INHERITED]** The existing pure-EXPOSE classification defines the supported boundary; this repair reconciles the conflicting checks against it. Source: `src/agentic_mbse/validation/adr002.py:389` and `docs/patterns/expose-pattern.md`.
- **[INFERRED]** Validation must distinguish a valid dynamic output binding from a numeric static default; a supported EXPOSE attribute does not need a precomputed literal value to be complete.

## Non-Goals

- New expression support, codegen output behavior, or modeling-workflow changes.

## Open Questions / Deferred to design

- How the checks share semantic classification without duplicating its policy, including parser-resolved target validation and the existing supported calculation/part reference-chain shapes.
- Which positive and negative controls exercise the public combined L6 route without unrelated fixture diagnostics hiding the result; the existing reproduction is the regression referent, not a required implementation layout.

## Related Artifacts

- **Backlog:** [L6-EXPOSE-CONSISTENCY](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Product guidance:** [EXPOSE pattern](../../../docs/patterns/expose-pattern.md).
- **Checks:** `src/agentic_mbse/validation/adr002.py:94`, `src/agentic_mbse/validation/level6_architecture.py:475`, and combined L6 at `:977`.
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Review this draft, then use `$my-design` for the shared classification and validation approach.
