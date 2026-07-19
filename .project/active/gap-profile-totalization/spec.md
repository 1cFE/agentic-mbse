# Spec: Profile Default-Deny Totalization

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-07-18 15:56 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** GAP-CLOSE Item 4

---

## Problem

Executable-profile v3 is intended to default-deny malformed serialized facts, but three adjacent
paths do not carry that contract through. Malformed `xor` and `implies` nodes with zero, one, or
three operands round-trip through the codec and become non-numerical warnings instead of blocks.
A quantity ratio can be admitted when both facts name the same exact unit even if their dimensions
contradict one another. When numerical containment promotes a non-numerical diagnostic to blocking
force, the diagnostic still describes a statement that "is not executed" instead of the error and
repair that halt generation.

These are verified totality and diagnostic defects inside v3. They leave malformed wire-valid input
with an unsafe or misleading outcome, and codegen currently pins the misleading promoted message in
its conformance suite.

## Success Criteria

- [x] Each `xor` and `implies` shape with 0, 1, or 3 operands survives a codec round trip and then
      returns `BLOCK` with a named arity diagnostic; valid two-operand behavior is unchanged.
- [x] A serialized quantity-ratio fact whose operands carry the same exact unit but contradictory
      dimensions returns `BLOCK` with a named dimension/derived-unit diagnostic rather than
      `ADMIT`.
- [x] Every non-numerical diagnostic promoted to error force by numerical containment has an
      error-appropriate reason and message that explains the halt and gives repair guidance. The
      coordinated codegen conformance assertion pins the corrected contract.
- [x] The profile remains `executable-profile/v3`, and focused regression coverage proves that no
      decision changes for well-formed consumer input. Any contrary evidence stops this item for
      owner review before implementation proceeds.
- [x] Each defect has an isolated regression that is demonstrably RED on pre-fix HEAD and green
      after the fix. Companion focused and normal/full gates, then codegen focused and licensed
      full gates against the updated companion, all pass.
- [x] Existing committed fixtures and canonical serialized bytes remain unchanged. Any necessary
      fixture change is made through the established capture path and is limited to a reviewed,
      justified diff.

## Known Requirements

- **[INHERITED]** `xor` and `implies` require exactly two operands. The 0-, 1-, and 3-operand
  codec-roundtrip forms must default-deny rather than warn. Source:
  `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item 4, F7; verified reproduction in
  `../sysml-codegen/.project/research/20260718_gap-review-verification.md`, F7.
- **[HARD]** `OperatorNode` and the v1 expression codec accept arbitrary operand-list lengths, so
  direct-construction coverage alone cannot prove the wire-boundary contract. The regression must
  exercise public serialization and parsing before profile evaluation. Existing system:
  `src/agentic_mbse/sysml/expression_ir.py` and the codec tests in
  `tests/test_sysml/test_expression_ir_serialize.py`.
- **[INHERITED]** Quantity-ratio classification must compare dimensions before admitting equal
  exact-unit strings. A serialized contradictory fact must block. Source:
  `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item 4, F8; verified D-R3 responsibility in
  `../sysml-codegen/.project/research/20260718_gap-review-verification.md`, F8.
- **[HARD]** `UnitFact` has no cross-field invariant and the codec preserves its `unit` and
  `dimension` fields, so malformed semantic combinations remain valid codec input. The profile is
  the existing decision boundary for this check. Existing system:
  `src/agentic_mbse/sysml/expression_facts.py`, `src/agentic_mbse/sysml/expression_ir.py`, and
  `src/agentic_mbse/sysml/executable_profile.py`.
- **[INHERITED]** Containment promotion must change the diagnostic semantics as well as its force.
  A blocking diagnostic must describe the error that halts generation and tell the model author
  how to separate or rewrite the mixed assertion; it must not retain "is not executed" wording.
  Source: `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item 4, promoted diagnostics, and
  `../sysml-codegen/.project/research/20260718_gap-review-verification.md`, hygiene 9.
- **[INHERITED]** The corrected promoted-diagnostic contract includes the coordinated assertion in
  `../sysml-codegen/tests/conformance/test_constraint_non_numerical.py`; the companion and codegen
  changes are one Item 4 scope. Source: `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item
  4.
- **[INHERITED]** These corrections stay within v3's documented default-deny behavior. There is no
  v4 bump. If implementation or tests reveal a changed decision for any well-formed consumer
  input, stop and surface the premise conflict instead of absorbing it into this item. Source:
  `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item 4 version ruling.
- **[INHERITED]** Validation is test-first: preserve isolated pre-fix RED evidence, run focused
  gates before full gates in both repositories, and keep fixture bytes stable except for reviewed
  and justified capture output. Source: `../sysml-codegen/.project/backlog/epic_gap_close.md`, Epic
  Strategy, Item 4 success criteria, and wave gates.

## Non-Goals

- Changing any decision for well-formed profile input or changing the admitted numerical matrix.
- Bumping `PROFILE_SEMANTIC_VERSION`, either wire-schema version, or package versions as part of
  this item.
- Adding a new fact invariant, codec representation, public interface, or architecture layer.
- Executing non-numerical assertions or changing the v3 containment policy.
- Closing other GAP-CLOSE findings or unrelated documentation and diagnostic hygiene.

## Open Questions / Deferred to plan

- None. The verified reproductions and the epic settle the required outcomes. Exact test placement
  and the smallest error-appropriate promoted reason/message are plan-stage details.
- Deliberate pipeline disposition: skip explicit `my-spec-review`, `my-design`, and
  `my-design-review`. The mechanisms are adjacent guard-order and diagnostic-totalization fixes
  with no interface or architecture change. Proceed through `my-plan`; retain the independent epic
  audit after implementation.

---

## Related Artifacts

- **Epic:** `../sysml-codegen/.project/backlog/epic_gap_close.md`, Item 4
- **Required Reading:**
  - `../sysml-codegen/.project/research/20260718-123558_constraint-expression-final-gap-review.md`,
    F7, F8, and promoted-diagnostic hygiene
  - `../sysml-codegen/.project/research/20260718_gap-review-verification.md`, F7, F8, and hygiene 9
- **Inherited profile contract:**
  `../sysml-codegen/.project/active/numerical-constraint-profile/{spec,design}.md`
- **Companion remediation evidence:** `.project/active/constraint-exec-remediation/{plan,audit}.md`
- **Primary companion implementation surface:**
  `src/agentic_mbse/sysml/executable_profile.py`
- **Primary companion tests:**
  `tests/test_sysml/test_executable_profile_arithmetic.py`,
  `tests/test_sysml/test_executable_profile_v3.py`,
  `tests/test_sysml/test_expression_ir_serialize.py`, and
  `tests/test_sysml/test_constraint_facts_serialize.py`
- **Coordinated codegen test:**
  `../sysml-codegen/tests/conformance/test_constraint_non_numerical.py`
- **Plan:** `.project/active/gap-profile-totalization/plan.md` (to be created)

---

**Next Steps:** Retain the independent GAP-CLOSE epic audit. Do not close this item before that
certification stage.
