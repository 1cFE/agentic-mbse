---
date: 2026-07-14T06:42:34-07:00
researcher: Codex
topic: "CONSTRAINT-EXEC PR code-quality audit"
tags: [research, code-quality, constraints, expression-ir, validation]
status: complete
last_updated: 2026-07-14
---

# Research: CONSTRAINT-EXEC PR Code-Quality Audit

**Date**: 2026-07-14T06:42:34-07:00
**Researcher**: Codex
**Research Type**: Codebase / Architecture / Pull-request audit

## Research Question

[OWNER-VERBATIM] “we have a MASSIVE pr open for this repo. I am concerned about code quality. I
did not expect so many lines to have changed for this. I need you to audit the quality. In
particular, look for:

- Fragile code: brittle / duct-taped logic
- Duplication
- Violation of patterns

For any issues found, name opportunities to simplify.”

## Scope and Baseline

The audited range is `main...constraint-exec-epic` at `9e24c93`, matching the branch-local PR body
at `.project/CONSTRAINT_EXEC_PR_BODY.md:1-25`. The range changes 88 files with 14,926 insertions and
272 deletions.

The headline size overstates the amount of production code, but the review burden is still real:

| Area | Added lines | Share of additions |
|---|---:|---:|
| `.project/` history, specs, designs, audits, and reference copies | 8,312 | 55.7% |
| Tests and fixtures | 4,200 | 28.1% |
| Production `src/` | 2,253 | 15.1% |
| Docs and templates | 161 | 1.1% |

The 2,473-line `tests/fixtures/constraint_fact_shapes/golden.json` and archived pipeline artifacts
make the PR look much larger than its runtime implementation. They also make review harder because
the production golden is stored as one canonical JSON line.

## Summary

- **Do not merge as-is.** Mixed-unit arithmetic bypasses the required safety gate and can be
  admitted with no diagnostic.
- **The versioned wire boundary fails open.** Parsers accept unsupported schema versions and
  silently rewrite nested ExpressionIR documents to the current version.
- **The profile's “total/default-deny” claim depends on unchecked shapes and assertions.** Parsed
  but internally inconsistent operand facts can crash instead of returning `BLOCK`; targeted mypy
  exposes the same brittle control-flow seam.
- **Validation reporting mixes two populations.** Level 4 can report a total smaller than the sum
  of its eligibility categories.
- **There is avoidable structural duplication.** The lazy public API has three inventories, codec
  logic crosses module boundaries through private helpers, fixtures have two owners, and the
  committed golden generator is already broken.

## Detailed Findings

### F1 — High: arithmetic bypasses the unit-safety gate

The approved contract says unit policy applies to arithmetic, not only comparisons. Operands in a
unit-sensitive operation must be dimensionless or carry identical exact units; conversions must
block (`.project/completed/20260713_executable-profile/spec.md:161-176`). The design restates that
the operand-fact gate runs “at every arithmetic node”
(`.project/completed/20260713_executable-profile/design.md:72-77`).

The implementation does not do that. The arithmetic branch only recursively walks each child and
returns (`src/agentic_mbse/sysml/executable_profile.py:369-377`). It never calls the existing
`unit_compatibility()` helper (`src/agentic_mbse/sysml/executable_profile.py:148-176`). A parent
comparison later trusts the arithmetic node's declared result fact
(`src/agentic_mbse/sysml/executable_profile.py:275-293`).

A mutation probe against HEAD constructed snapshot-valid IR for mixed-unit addition. Walking
`1 [m] + 1 [cm]` as a value produced `arithmetic_diagnostics []`. The same hole admits other
incompatible arithmetic operand categories if the result node claims a usable type.

Existing tests do not close the hole. The live `unit_bearing_arithmetic` case is same-unit
arithmetic under equality, so the outer equality blocks it for requiring real tolerance rather
than proving the arithmetic gate ran (`tests/test_sysml/test_executable_profile.py:100-121`). The
matrix tests call the unit helper only for top-level inequality operands
(`tests/test_sysml/test_executable_profile_matrix.py:48-52`).

**Simplification opportunity:** add one typed `_walk_value_operation` or `_walk_arithmetic` helper.
It should recurse, validate operator arity, recover operand facts, and apply one shared pairwise unit
policy. Comparisons and arithmetic should use the same operand-recovery/result path instead of
splitting “walk” from “gate.” Add mixed-unit, quantity/unitless, incompatible-category, unary, and
n-ary arithmetic tests.

### F2 — High: versioned parsers accept and mutate unsupported schemas

Every ExpressionIR node serializes a `schema_version`, but the decoder dispatches only on `kind`
and never validates that version (`src/agentic_mbse/sysml/expression_ir.py:180-217`). Constructing
the current dataclass then replaces the input version with `expression-ir/v1`
(`src/agentic_mbse/sysml/expression_ir.py:41-114`). The root facts decoder likewise accepts any
envelope version (`src/agentic_mbse/sysml/constraint_facts.py:303-315`).

Verified mutation probes:

- An ExpressionIR document with `schema_version="expression-ir/v999"` parsed successfully and
  reserialized as `expression-ir/v1`.
- An empty facts document with `schema_version="constraint-facts/v999"` parsed successfully and
  retained the unsupported version.

This is a cross-repo wire contract. Treating a future schema as today's shape can silently lose or
misread data. The current tests pin versions produced by current constructors but never test
rejection (`tests/test_sysml/test_expression_ir_serialize.py:37-38` and
`tests/test_sysml/test_constraint_facts_serialize.py:172-175`).

The discriminants are also caller-settable constructor fields. A caller can construct a literal
node with a false `kind` or version and serialize an impossible document.

**Simplification opportunity:** validate the envelope version once at `constraint_facts.parse()`
and validate every ExpressionIR subdocument version in one public decoder. Make `kind` and
`schema_version` non-init constants (`field(init=False)` or explicit codec constants), so invalid
states cannot be constructed through the normal API. Add wrong-version, missing-version,
wrong-kind, and future-field tests.

### F3 — Medium: default-deny totality relies on assertions and diagnostic-list side effects

The profile accepts both live-extracted and snapshot-parsed facts
(`.project/completed/20260713_executable-profile/spec.md:62-78`). The parser performs no semantic
validation, so `OperandTypeFact(category="quantity", unit=None)` is representable
(`src/agentic_mbse/sysml/expression_facts.py:51-62`). `unit_compatibility()` asserts that quantity
facts always have a `UnitFact` (`src/agentic_mbse/sysml/executable_profile.py:164-170`). A probe
comparing two such operands raised `AssertionError` instead of producing one named `BLOCK` result.

The comparison walk has a second brittle dependency. It recursively appends diagnostics, compares
the list length, and assumes that any node without `operand_type` must have appended something
before it accesses `.operand_type` (`src/agentic_mbse/sysml/executable_profile.py:275-284`). Targeted
mypy reports two `union-attr` errors at lines 282-283 because `UnsupportedNode` has no such field.

**Simplification opportunity:** make value walking return a typed result such as
`OperandTypeFact | EligibilityDiagnostic` instead of mutating a shared list and inspecting its
length. Validate operand invariants at the parser/profile boundary and turn malformed facts into a
named default-deny reason. Assertions can remain only after the type has been narrowed and the
wire shape validated.

### F4 — Medium: Level 4 reports incompatible populations

The legacy “Total constraints” count excludes the `RequirementUsage` subtree, including satisfy
usages (`src/agentic_mbse/sysml/syside_adapter.py:34-43` and
`src/agentic_mbse/validation/level4_constraints.py:100-110`). The new eligibility metrics evaluate
every extracted `ConstraintUsage`, including satisfy as unassessed
(`src/agentic_mbse/sysml/constraint_extraction.py:113-120` and
`src/agentic_mbse/validation/level4_constraints.py:42-66`).

Verified on `tests/fixtures/constraint_fact_shapes/source_forms.sysml`:

```text
Total constraints: 12
Eligible: 8
Ineligible: 1
Unassessed: 4
```

The categories sum to 13, so a reader cannot reconcile them with the displayed total. The design
explicitly preserved the old counts and added eligibility beside them, but did not reconcile the
denominators (`.project/completed/20260713_executable-profile/design.md:235-240`).

**Simplification opportunity:** derive every displayed constraint population from one
`ProfileResult`. Name separate totals if both are useful, such as `Cataloged usages` and
`Executable assertions`, and add a test that each category set reconciles with its named total.

### F5 — Medium: the public single-node extractor drops structured diagnostics

Non-finite literal extraction records a structured diagnostic in `_ExtractionContext`
(`src/agentic_mbse/sysml/constraint_extraction.py:354-371`). The public
`extract_expression_ir()` creates that context and discards it
(`src/agentic_mbse/sysml/constraint_extraction.py:464-473`). Its test must import the private
context and private extractor to observe the diagnostic
(`tests/test_sysml/test_constraint_extraction.py:173-204`); the public API test covers only a clean
expression (`tests/test_sysml/test_constraint_extraction.py:207-226`).

That undercuts the design decision to reject a non-finite value with a structured diagnostic and
not rely only on a bare serialization error
(`.project/completed/20260713_constraint-facts/design.md:139-148`).

**Simplification opportunity:** return an `ExpressionExtractionResult(ir, diagnostics)` from the
public entry point, or raise one documented structured exception. Do not keep a second public
extraction path whose only diagnostic channel is deliberately thrown away.

### F6 — Medium: the committed golden regeneration path is broken and fixtures have two owners

The committed generator imports `tests.constraint_fact_learning`
(`.project/active/spike-constraint-fact-shapes/generate_golden.py:14-15`), but that module was
retired and no longer exists. The production extractor itself documents that retirement
(`src/agentic_mbse/sysml/constraint_extraction.py:3-7`). The checked-in regeneration instructions
therefore cannot regenerate the 2,473-line oracle.

The spike and test fixture directories also contain byte-identical copies of both SysML inputs:

- `.project/active/spike-constraint-fact-shapes/probe_source_forms.sysml` and
  `tests/fixtures/constraint_fact_shapes/source_forms.sysml`
- `.project/active/spike-constraint-fact-shapes/probe_type_units.sysml` and
  `tests/fixtures/constraint_fact_shapes/type_units.sysml`

**Simplification opportunity:** keep the executable fixture in one canonical location and use a
path reference from the research artifact. Delete the dead generator or replace it with a working,
tested command based on the production extractor. Prefer a formatted generated artifact or an
attached formatter command so future reviewers can inspect semantic diffs.

### F7 — Medium: the lazy public API maintains three parallel inventories

Lazy loading is justified: importing a pure fact/profile submodule must not load licensed SysIDE.
The implementation, however, repeats the public surface in `TYPE_CHECKING` imports
(`src/agentic_mbse/sysml/__init__.py:18-133`), `__all__`
(`src/agentic_mbse/sysml/__init__.py:135-239`), and `_LAZY`
(`src/agentic_mbse/sysml/__init__.py:241-356`). The file grew from 161 to 372 lines.

A new or renamed symbol can type-check but fail at runtime, appear in `dir()` without resolving, or
resolve while being omitted from star import. The generic barrel names `parse` and `serialize` are
also ambiguous beside `parse_expression` and `serialize_expression`
(`src/agentic_mbse/sysml/__init__.py:173-178`).

**Simplification opportunity:** keep one declarative runtime registry and derive `__all__` from it.
Move the unavoidable static declarations to a `.pyi` stub, or keep the new wire APIs on their
descriptive submodules rather than re-exporting them. If they remain public at the barrel, prefer
`parse_constraint_facts` and `serialize_constraint_facts`. Add one consistency test that resolves
every exported name.

### F8 — Low/medium: codec layering depends on private internals and repeats leaf decoding

`constraint_facts` imports private `_canonical_json` and private `_expression_ir_from_dict` from
`expression_ir` (`src/agentic_mbse/sysml/constraint_facts.py:16-18`). Both modules separately
reconstruct `IdentityFact` (`src/agentic_mbse/sysml/expression_ir.py:138-147` and
`src/agentic_mbse/sysml/constraint_facts.py:189-199`).

The module dependency points in the intended direction, but the public typed wire contract is
implemented through underscore helpers. A harmless private refactor can break the parent codec,
and schema evolution requires synchronized parser ladders.

**Simplification opportunity:** expose one explicit dict-level ExpressionIR codec, or place
canonical JSON and shared leaf decoders in a small lower-level codec module. Keep
`constraint_facts` dependent on a public codec surface only.

### F9 — Low: canonical output ordering can collide across files

Constraint ordering uses only `(line, qualified_name)`
(`src/agentic_mbse/sysml/constraint_extraction.py:236-239`). Anonymous assertions are supported and
identified by location (`tests/test_sysml/test_constraint_extraction.py:142-150`). Two anonymous
assertions on the same line number in different files therefore have the same sort key, leaving
serialized order dependent on model enumeration/input order.

**Simplification opportunity:** sort by `(file, line, column, qualified_name)`, using the location
data already extracted. Add a two-file anonymous-assertion stability test.

## Additional Simplification Opportunities

These are not merge-blocking defects, but they explain some avoidable cost:

- **Extract and index once.** L4 and L6 each run the full fact extraction independently
  (`src/agentic_mbse/validation/level4_constraints.py:56-57` and
  `src/agentic_mbse/validation/level6_architecture.py:618-619`). Within one extraction, formal and
  redefinition recovery repeatedly scan all `AttributeUsage` elements per definition/context
  (`src/agentic_mbse/sysml/constraint_extraction.py:516-535,687-700`). Build
  `attributes_by_owner` once and pass one facts/profile result through a validation run. The
  archived design explicitly accepted duplicate L4/L6 extraction pending profiling, so measure
  before making this a release blocker.
- **Cache expensive test setup.** The fact-shape tests reload and re-extract the same two SysML
  files for each test (`tests/test_sysml/test_constraint_fact_shapes.py:41-43,54-225`). The profile
  tests reevaluate all 28 usages for each name lookup
  (`tests/test_sysml/test_executable_profile.py:33-39`). Module-scoped fixtures and a decision map
  would remove repetition without reducing coverage.
- **Clarify immutability.** `UsageDecision` and result dataclasses are `frozen=True` but contain
  mutable lists (`src/agentic_mbse/sysml/executable_profile.py:93-142`). Use tuples if immutability
  is a real contract, or remove the frozen claim.

## Architecture Insights

Several unusual choices are sound and should not be “simplified” away:

- The six-form constraint classification is explicit and membership-first
  (`src/agentic_mbse/sysml/constraint_extraction.py:580-600`). It matches the documented semantic
  split and is not accidental branching.
- Unknown expression metaclasses and operators become `UnsupportedNode` instead of being coerced
  (`src/agentic_mbse/sysml/constraint_extraction.py:434-495`). That is the correct fail-visible
  pattern.
- L6 deliberately lets extraction failures propagate and emits warnings only for blocked usages
  (`src/agentic_mbse/validation/level6_architecture.py:615-641`). This preserves the repo's
  loud-on-failure rule.
- Lazy package loading is required for the license-free import guarantee. The duplication in the
  registry is the issue, not laziness itself. The subprocess test verifies the guarantee
  (`tests/test_sysml/test_executable_profile_hygiene.py:13-24`).
- Plain dataclasses follow the approved design. The defect is missing validation at a cross-repo
  parser boundary, not the absence of Pydantic.

## Validation Performed

- Targeted changed-area suite: **136 passed** in 2.72 seconds.
- Ruff over changed production and principal test files: **passed**.
- Targeted mypy over the four pure modules: **failed with two `union-attr` errors** at
  `src/agentic_mbse/sysml/executable_profile.py:282-283`.
- Mutation probes reproduced:
  - mixed-unit arithmetic with zero diagnostics;
  - ExpressionIR `v999` silently rewritten to `v1`;
  - root facts `v999` accepted;
  - zero-operand `and` admitted by the private walk;
  - Level 4 category counts exceeding its displayed total.
- `git diff --check main...HEAD` found one trailing blank line in an archived plan at
  `.project/completed/20260713_executable-profile/plan.md:520`; this is cosmetic.

The full 1,401-test suite was not rerun during this audit. The PR body records its earlier full-suite
result at `.project/CONSTRAINT_EXEC_PR_BODY.md:21-25`; the focused run confirms that the defects above
are missing assertions, not current red tests.

## Feasibility Assessment

The architecture is salvageable without a rewrite. The fact/IR/profile split is coherent, and most
production growth is direct schema and extraction logic rather than framework code. The two high
findings are localized:

1. centralize value-operation gating in the profile;
2. validate and seal discriminants at the codec boundary.

The medium findings can be fixed in the same cleanup with small, testable changes. The public API
registry and fixture ownership cleanup can be separate commits if minimizing semantic churn is more
important than shrinking this PR before merge.

## Recommendations

1. **[AGENT] Block merge on F1 and F2.** Add failing regression tests first, then fix arithmetic
   gating and version rejection.
2. **[AGENT] Fix F3 in the same profile change.** A default-deny gate should return a decision for
   malformed snapshot facts, not assert. Require targeted mypy to pass for the new pure modules.
3. **[AGENT] Reconcile Level 4 reporting before merge.** The current output is user-visible and
   internally contradictory.
4. **[AGENT] Repair or remove the dead generator before merge.** A checked-in 2,473-line oracle
   needs a working reproduction path and one canonical source fixture.
5. **[AGENT] Follow with the API/codec cleanup.** Collapse the lazy registry, give wire functions
   descriptive names, and stop importing private codec helpers across modules.
6. **[AGENT] Keep the PR-size explanation in review context.** About 84% of additions are project
   artifacts or tests. That explains the line count but does not reduce the need to fix the runtime
   defects.

## Open Questions

- Should unsupported or malformed snapshot facts raise a typed parse error immediately, or should
  the executable profile convert them into a named `BLOCK` diagnostic? The current contract mixes
  parser trust with profile totality; one layer needs explicit ownership.
- Is the one-line production golden a downstream byte fixture that must remain verbatim, or can a
  formatted review copy be generated beside it?
- Are generic `agentic_mbse.sysml.parse` and `serialize` imports already used by the paired
  sysml-codegen PR? If so, rename them in both coordinated branches; otherwise keep them
  submodule-only now.
