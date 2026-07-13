# Spike: Constraint Fact Shapes in Live SysIDE

## Summary of Findings

**Verdict: S1 passes with one explicit profile restriction.** Live SysIDE 0.8.4 exposes the
source form, membership kind, polarity, ownership and scope, predicate structure, actuals and
defaults, inheritance/retyping, and operand type/dimension evidence without invoking an
evaluator. The committed fixture, golden JSON, and five kept tests freeze those shapes.

Exact unit is not universally recoverable. A structural unit annotation identifies its exact
unit and dimension, but a feature typed only as `LengthValue` proves the dimension, not one
runtime unit. [AGENT] Unit-sensitive operations must therefore block unless both exact units are
known and identical through authoritative structural facts.

[AGENT] The evidence admits equality for Boolean, string, integer, and operands from the same
enumeration. It blocks incompatible enums, unresolved or incompatible operands, unit conversion,
unknown exact units, and all real-valued equality without an explicit modeled tolerance. Matching
quantity units establish compatibility but do not make real equality safe.

Two SysIDE access quirks are now pinned: extract through a base `ConstraintUsage` subtype sweep
so satisfy is not missed, and recover constraint-definition inputs by owner-filtered attribute
enumeration because `ConstraintDefinition.parameters` omits them in 0.8.4.

Validation: 5 focused tests passed; the full suite passed with 1,295 passed, 1 skipped, and 33
deselected; focused Ruff checks passed. The upstream concept now records the verdict and links
back to this document.

## Question / Goal

Assumption under test: live SysIDE exposes every neutral constraint fact needed by S1—source
form, owning membership kind, polarity, ownership and scope, inheritance and retyping, actual
expressions, compound Boolean structure, and equality operand type/unit evidence—without
invoking the evaluator.

The assumption is confirmed only if a committed SysML fixture matrix, kept tests, golden JSON
facts, and diagnostics recover the full S1 matrix. Any field that cannot be recovered becomes a
schema cut or an explicit executable-profile restriction.

Upstream artifact:
`/home/reid/1cfe/sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`,
Appendix B, S1.

Metadata at start:

- Date: 2026-07-11 12:52:30 PDT
- Branch: `push-down-item1-expression`
- Commit: `d340c8e`
- SysIDE version: pending live probe

## Log

### 1. Context and baseline

Read the upstream concept, `.project/CURRENT_WORK.md`, `CLAUDE.md`, the SysIDE adapter,
expression utilities, and existing live-SysIDE test patterns before probing.

Initial command:

```bash
uv run python -c "import syside; print(getattr(syside, '__version__', 'no __version__'))"
```

Observed: `uv` could not initialize `/home/reid/.cache/uv` because the environment mounts that
global cache read-only. This is an execution-environment setup issue, not evidence about
SysIDE. All reproduction commands below set `UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache`.

The workspace virtual environment contains SysIDE `0.8.4`. The existing live adapter tests pass
with the alternate cache.

### 2. Source-form probe

Created `probe_source_forms.sysml` and `probe_constraint_shapes.py` in this folder. The model
covers inline, definition-typed, named-usage-reference, and satisfy forms; require/assume
memberships; positive and negated assertions; part-definition, calculation-definition, and
direct-usage owners; anonymous assertions; owner references, feature chains, literals, and an
omitted default; inheritance and redefinition.

Command:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache uv run --offline python \
  .project/active/spike-constraint-fact-shapes/probe_constraint_shapes.py
```

Observed:

- Inline assertions own `result_expression`; `asserted_constraint` is the assertion itself.
- Definition-typed assertions have no usage-owned `result_expression`; their
  `constraint_definition` owns the predicate, while usage-owned parameters carry actuals.
- Assert-by-reference is an anonymous `AssertConstraintUsage`. Its
  `referenced_feature_target` and `asserted_constraint` identify the named usage; `in :>>`
  parameters preserve the rebinding actuals.
- Satisfy is a `SatisfyRequirementUsage` with the requirement definition and satisfying-subject
  binding available structurally.
- Require versus assume is available as `RequirementConstraintMembership.kind`. It is not a
  property of the owned `ConstraintUsage` subtype.
- Negation is directly available as `AssertConstraintUsage.is_negated`.
- Owner and owning type distinguish `PartDefinition`, `CalculationDefinition`, and `PartUsage`.
- Derived definitions and typed usages expose the inherited source constraint through
  `features`; their local redefining attributes expose `owned_redefinitions` back to the base
  feature.
- Anonymous assertion identity needs its source location because both `name` and
  `qualified_name` are absent.

Two SysIDE 0.8.4 access-path findings matter to production extraction:

- A `ConstraintUsage` subtype sweep finds all four forms. An
  `AssertConstraintUsage`-rooted subtype sweep does not return satisfy, despite satisfy's
  multiple-inheritance semantics. Extraction must sweep the common base and classify afterward.
- `ConstraintDefinition.parameters` and `owned_members` do not surface the user-declared input
  attributes in this model. The inputs remain recoverable by an `AttributeUsage` model sweep
  filtered by `owner is definition`; the default is an owned `FeatureValue` with
  `is_default = true`.

### 3. Static expression and type/unit probe

Created `probe_type_units.sysml`. It covers compatible and incompatible enums, integer/real
promotion, Boolean/string/integer equality, exact and convertible units, incompatible
dimensions, unit-bearing arithmetic, unitless versus dimensioned values, a quantity feature
whose exact unit is not statically fixed, an unresolved operand, inherited and aliased real
types, and nested `and`/`or`/`not`.

The probe used only loaded semantic elements, `cached_result_type`, `Type.conforms`, feature
typing, unit-reference targets, and CST source tokens. It never constructed `syside.Compiler`
or invoked an evaluator.

Observed:

- Expression structure is complete: operators and ordered operands survive, including `and`,
  `or`, `not`, comparisons, arithmetic, feature references, feature chains, and the `[` unit
  annotation operator.
- A reference retains a resolved semantic target. Its exact authored spelling, including aliases
  such as `m`, remains available from its CST span. This supplies source name plus qualified
  target without reconstructing expression text.
- `Integer` conforms to both `Integer` and `Real`; a real-typed feature conforms only to `Real`.
  This statically proves promotion.
- Enum operands expose their owning `EnumerationDefinition`, so same-enumeration and
  incompatible-enumeration cases are distinguishable.
- Unit annotations resolve `m`, `cm`, and `kg` to `SI::metre`, `SI::centimetre`, and
  `SI::kilogram`. Their types distinguish length from mass. Exact unit equality, same-dimension
  conversion, and incompatible dimensions are therefore distinguishable without evaluation.
- Addition of operands carrying the same exact unit can retain that unit by the operator rule.
- A feature declared only as `LengthValue` proves the length dimension but not one exact runtime
  unit. Its initializer does not make all future values use that unit.
- An unresolved name survives as a placeholder target and produces the expected
  `reference-error` diagnostic.
- SysIDE reports no diagnostic for incompatible enum equality or incompatible-dimension
  equality. Loader diagnostics cannot be the equality gate.

### 4. Kept fixture and golden facts

Promoted the probe matrix into:

- `tests/fixtures/constraint_fact_shapes/source_forms.sysml`
- `tests/fixtures/constraint_fact_shapes/type_units.sysml`
- `tests/fixtures/constraint_fact_shapes/golden.json`
- `tests/constraint_fact_learning.py`
- `tests/test_sysml/test_constraint_fact_shapes.py`

`golden.json` contains the captured definition, usage, owner, membership, polarity, actual,
default, inheritance, redefinition, expression, type, unit, decision, and diagnostic facts. The
test-only capture code is intentionally not a production IR or schema commitment.

Focused validation:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache uv run --offline pytest \
  tests/test_sysml/test_constraint_fact_shapes.py -q
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache uv run --offline ruff check \
  tests/constraint_fact_learning.py \
  tests/test_sysml/test_constraint_fact_shapes.py \
  .project/active/spike-constraint-fact-shapes/probe_constraint_shapes.py \
  .project/active/spike-constraint-fact-shapes/generate_golden.py
```

Observed: 5 tests passed; Ruff passed.

### 5. Equality and unit gate decided from evidence

[AGENT] The S1 equality gate is:

| Operand shape | Decision | Static reason |
|---|---|---|
| Boolean / Boolean | Support | Both categories recover exactly. |
| String / String | Support | Both categories recover exactly. |
| Integer / Integer | Support | Both operands prove integer conformance. |
| Same enum / same enum | Support | Both operands name the same enumeration. |
| Different enums | Block | Enumeration identities differ. |
| Integer / Real | Block | Promotion yields real-valued equality, which needs an explicit modeled tolerance. |
| Same exact quantity unit | Block equality | Unit compatibility is proven, but the value comparison is still real-valued equality. |
| Same dimension, different units | Block | A conversion is required; generated runtime values cannot convert silently. |
| Different dimensions | Block | Unit types prove incompatibility. |
| Unit-bearing arithmetic with one provable exact unit | Block equality | The result unit is recoverable, but equality remains real-valued. |
| Unitless / dimensioned | Block | Operand categories are incompatible. |
| Quantity feature with dimension but no exact unit | Block | Exact-unit compatibility cannot be proven statically. |
| Unresolved operand | Block | The operand category cannot be proven. |
| Inherited or aliased real type | Block equality | Real conformance is recoverable through inheritance/alias resolution; tolerance is still absent. |

[AGENT] S1 confirms the proposed neutral facts with one restriction: exact unit is a conditional
fact, not a universally recoverable field. A profile may admit a unit-sensitive numeric operation
only when both operands' exact units are structurally known and identical. A quantity feature
that proves only its dimension must block unless a later contract supplies an exact unit through
another authoritative structural fact.

### 6. Full validation and upstream loop closure

Command:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache uv run --offline pytest tests/ -q
```

Observed: 1,295 passed, 1 skipped, 33 deselected. Six existing multiprocessing deprecation
warnings were reported; no test failed.

`git diff --check` and the focused Ruff checks passed. The pre-existing untracked
`.project/backlog/epic_command-refresh.md` and
`.project/research/20260703-112157_command-refresh-from-agentic-project-init.md` were not changed.

Added an `[AGENT]` S1 verdict and this back-reference under **Next-Stage Handoff → First risk to
de-risk** in the upstream concept:
`/home/reid/1cfe/sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`.

## Reproduction

From the repository root:

```bash
export UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache

# Inspect the exploratory source-form probe.
uv run --offline python \
  .project/active/spike-constraint-fact-shapes/probe_constraint_shapes.py

# Regenerate a candidate golden on stdout for review.
uv run --offline python \
  .project/active/spike-constraint-fact-shapes/generate_golden.py

# Verify the committed golden and semantic decisions.
uv run --offline pytest tests/test_sysml/test_constraint_fact_shapes.py -q

# Run the repository suite used at close-out.
uv run --offline pytest tests/ -q
```

Expected focused result: 5 tests pass. `type_units.sysml` intentionally produces exactly one
golden `reference-error` for `missing_value`; the test asserts that diagnostic. The source-form
fixture has no diagnostics.

## Open Questions / Follow-ups

- S2 must decide the canonical expression representation and prove live/Python behavior parity;
  S1 records the source facts only.
- Production design must choose where an exact unit contract comes from for quantity feature
  references. S1 proves that `LengthValue` alone supplies a dimension, not an exact unit.
- Satisfy and assert-by-reference are fully catalogable, but remain outside executable profile v1
  as the upstream concept states.
