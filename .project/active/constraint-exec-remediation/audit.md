# Audit: CONSTRAINT-EXEC PR Remediation

**Verdict:** Certify
**Audited:** 2026-07-17
**Branch:** `constraint-exec-epic`
**Commit:** `9e24c93` plus uncommitted remediation work

---

## Summary

The remediation now closes all original findings and the three wire-boundary gaps from the prior
certification pass. Malformed snapshot leaves reach the executable profile's named D-R3 block,
mutated wire tags cannot serialize, and the defining extraction module exposes both public
extractors. The local agentic-mbse remediation is certified; paired sysml-codegen compatibility
remains separate cross-repo work.

## Findings

### Plan completion

All seven phases are verified complete. The previously unchecked Phase 1 walk item is implemented
by the typed value-recovery path in `executable_profile.py`; Phase 7 records and tests the three
fresh audit cures in `plan.md`.

### Spec conformance

- **D-R1 / D-R2 arithmetic policy — verified.** Arithmetic derives facts from operands and the
  existing arithmetic matrix remains green.
- **D-R3 malformed-fact totality — verified on the public snapshot path.** Literal,
  feature-reference, and unit-annotation decoders preserve `null` or absent `operand_type` as a
  malformed semantic fact (`expression_ir.py:249-270`). Six full-facts codec/profile cases produce
  `block_malformed_operand_fact` (`test_executable_profile_arithmetic.py:259`).
- **Versioned codec guarantee — verified.** Missing/foreign input tags still fail during parse.
  Valid documents retain byte-stable round trips. Serializer-side checks reject mutated tags before
  encoding (`expression_ir.py:145-187`, `constraint_facts.py:191-202`).
- **D-R6 public diagnostics API — verified.** The defining module now lists both public extractors
  (`constraint_extraction.py:54`), and its star-import surface is pinned
  (`test_public_api_exports.py:64`).
- **Non-goals respected.** No compiler behavior, wire version, generic codec rename, or
  sysml-codegen-local finding was added to this remediation.

The archived executable-profile spec still has two open cross-repo success criteria: codegen
preflight wiring and both-repo green certification. They are not local remediation claims and were
not marked complete.

### Design conformance

The implementation preserves the one-way pure-module layering and the recorded parser/profile
boundary. Leaf fact optionality is explicit in the three value-leaf dataclasses
(`expression_ir.py:50-97`), while structural wire tags remain required. Serializer validation walks
nested dataclass aggregates, so the same invariant covers bare IR and IR embedded anywhere in
`ConstraintFacts` (`expression_ir.py:135-182`). Mutable lists remain mutable; no new frozen-object
contract was introduced.

### Code integrity

No god functions, implicit modes, policy-bearing fallbacks, broad exception swallows, compatibility
shims, placeholders, or silent invariant fallbacks were found in the Phase 7 diff. The tag validator
has one mechanical job and raises with the node family, found tag, and expected tag. The optional
leaf fact is required by D-R3 and is handled explicitly by the profile rather than defaulted to a
plausible value.

---

## Certification

- Reviewed the Phase 7 production and test diff against the remediation plan and the inherited
  constraint-facts, ExpressionIR, and executable-profile contracts.
- Reproduced the initial red state: 17 focused failures matching the three fresh findings.
- Focused final set: **92 passed**.
- Normal suite: **1484 passed, 1 skipped, 33 deselected**.
- Targeted mypy over the five core extraction/facts/IR/profile modules: clean.
- Ruff check and Ruff format check over the seven touched Python files: clean.
- Targeted `git diff --check`: clean; no TODO/FIXME/pass/NotImplemented placeholders found.
- Verified all remediation plan checkboxes are complete. No archived epic/spec checkbox was changed.

**Not checked:** paid/slow Claude-budget corpus cases; paired sysml-codegen compatibility and its
same-IR preflight seam; the four sysml-codegen-local audit findings; performance of duplicate L4/L6
extraction. The known cosmetic whitespace finding in the archived executable-profile plan is outside
the Phase 7 diff.
