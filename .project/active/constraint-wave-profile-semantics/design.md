# Design: Constraint-Wave Profile Semantics

**Status:** Implementation Complete — audit defects remediated; provenance gates open
**Owner:** Reid W
**Created:** 2026-07-19
**Updated:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Coordinated baselines:** agentic-mbse `4ed2a07`; sysml-codegen `512786c`
**Epic:** CONSTRAINT-WAVE-REMEDIATION, Item 1 (R-1, R-2)

## Overview

Executable-profile v4 makes ordering admission total over the eight operand categories and makes
assertion polarity part of the profile decision. The positive predicate bytes remain unchanged;
codegen verifies the source fact against the decision, then uses the decision-carried polarity and
expected truth as the only semantic authority through lowering, catalog generation, and compilation.

## Related Artifacts

- **Approved contract:** `spec.md`; `spec-review.md`
- **Required design review:** `design-review.md`
- **Epic:** `../../../../sysml-codegen/.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 1
- **Reconciliation:** `../../../../sysml-codegen/.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md`
- **Primary review:** `../../../../sysml-codegen/.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`, R-1 and R-2
- **Original concept:** `../../../../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies.md`
- **Definitive concept:** `../../../../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`
- **Prior designs:** `../../completed/20260713_executable-profile/design.md`;
  `../../../../sysml-codegen/.project/completed/20260713_constraint-lowering/design.md`;
  `../../../../sysml-codegen/.project/completed/20260713_constraint-generation/design.md`
- **Numerical-profile contract:** `../../../../sysml-codegen/.project/active/numerical-constraint-profile/spec.md`;
  `../../../../sysml-codegen/.project/active/numerical-constraint-profile/design.md`

The approved semantic contract is unchanged. The spec was narrowly amended after design review to
name hashed, versioned candidate-pair evidence and defer release-readiness certification to Epic
Item 8. Its owner-ratified `[INFERRED]` ordering and polarity selections remain agent-originated and
are not promoted to owner-originated settled requirements here.

### Design-review resolution map

| Finding | Design resolution |
|---|---|
| C1 | D7-D8 and the source-key table separate true predicate-source ownership from per-usage polarity; one neutral body serves opposite-polarity usages. |
| C2 | D11 and the pre-output order move source grouping, continuity, naming, input, parse, and compile checks into a read-only plan. |
| M1 | The seven-row decision table, five named constructors, and non-`assert` validation make every allowed state explicit. |
| M2 | The diagnostic precedence table and separate L4/L6/codegen cardinality rules fix selection, ordering, warning, and halt behavior. |
| M3 | D9 and the compatibility seam distinguish candidate wheels from releases and prove both skew directions from a complete hashed no-index closure. |
| M4 | `predicate_source_key` crosses lowering, concrete records, catalog entries, the plan, and compiler ownership. |
| M5 | Dirty baselines, reviewed clean overlays, historical worktrees, phase allowlists, and Item 2/4/6 overlap gates isolate both repositories. |
| M6 | I15 and the native-exception tests preserve the existing arithmetic boundary and leave F1 external. |
| m1 | The consumer-map test checks exact fields; focused behavioral tests prove source-key and membership-identity use. |
| m2 | `block_unitless_dimensioned` is excluded from ordering v4 and remains only on equality/arithmetic paths. |
| m3 | B4 and the lowering/plan sections name graph extension, filesystem mutation, and permitted earlier in-memory work separately. |

The fresh review's remaining findings are evidence-scope corrections, not semantic changes:

| Fresh finding | Design resolution |
|---|---|
| M1 | D9 uses the amended spec's candidate terminology and leaves release-readiness with Epic Item 8. |
| M2 | The compatibility seam uses one complete hashed wheelhouse, proves the `agentic-mbse>=0.1.2` versus `==0.1.1` cause, and runs an `==0.1.2` positive control from that same wheelhouse. |
| m1 | Every untracked file admitted to a clean candidate overlay is sealed and reverified by relative path, content hash, file type, and executable mode. |

## Research Findings

- The category vocabulary is already the required closed eight-value set on
  `OperandTypeFact.category`; no fact-schema change is needed
  (`src/agentic_mbse/sysml/expression_facts.py:51-62`).
- Ordering currently calls only `unit_compatibility`. That helper returns `"ok"` for any two
  dimensionless categories, which admits Boolean, String, and enumeration ordering
  (`src/agentic_mbse/sysml/executable_profile.py:164-195,521-525`).
- `UsageDecision` carries the selected predicate but no polarity. `_evaluate_usage` reaches the
  body walk without consulting `ConstraintUsageFact.is_negated`
  (`src/agentic_mbse/sysml/executable_profile.py:115-125,717-783`).
- The codec assigns raw JSON polarity directly. Values such as `None`, `0`, and `"false"` can
  therefore reach the profile unless it performs an exact-type check
  (`src/agentic_mbse/sysml/constraint_facts.py:272-285`).
- L6 already translates one profile diagnostic into one `ERROR` and preserves decision/diagnostic
  order. Its no-location rendering is currently empty rather than the required stable placeholder
  (`src/agentic_mbse/validation/level6_architecture.py:594-649`).
- Codegen currently re-reads `usage.is_negated`, derives `expected_value`, and then carries both
  through `ConcreteConstraint` and `ConstraintCatalogEntry`
  (`../../../../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:970-987,1083-1104`;
  `../../../../sysml-codegen/src/sysml_codegen/resolution/models.py:368-438,454-482`). This is correct
  runtime behavior but a second semantic path around the profile decision.
- Catalog assembly preserves predicate bytes and polarity, and the same-IR guard checks stable
  parse/serialize bytes before compilation
  (`../../../../sysml-codegen/src/sysml_codegen/generation/constraint_catalog.py:61-180`).
- The current compile-once key is not a definition key. `predicate_definition_key()` returns
  `usage_qualified_name`, so two usages of one definition compile two bodies; the first entry's
  polarity is also baked into the emitted function
  (`../../../../sysml-codegen/src/sysml_codegen/generation/constraint_catalog.py:46-54`;
  `../../../../sysml-codegen/src/sysml_codegen/generation/modules.py:131-173`).
- True predicate-source identity already exists in neutral facts.
  `ConstraintSource.effective_predicate_source` is the definition identity for
  `definition_typed` and the usage identity for `inline`
  (`src/agentic_mbse/sysml/constraint_facts.py:83-100`;
  `src/agentic_mbse/sysml/constraint_extraction.py:620-638`). No new extraction lookup is needed.
- The compiler currently combines two responsibilities: evaluate the positive body and interpret
  one usage's polarity. It returns raw truth, status, and polarity-adjusted margin from one emitted
  function (`../../../../sysml-codegen/src/sysml_codegen/generation/predicate_compiler.py:232-302`).
  The existing negated execution test proves the current final result, not correct sharing across
  two opposite-polarity usages of one definition
  (`../../../../sysml-codegen/tests/execution/test_constraint_execution.py:509-544`).
- Generation-time IR and compile checks currently run after output clearing, directory creation,
  primitives, and schemas. Existing pre-output checks stop at names, output paths, params coverage,
  and symlink safety (`../../../../sysml-codegen/src/sysml_codegen/cli/__init__.py:971-1009`).
- Current compatibility identifiers are profile v3, companion package `0.1.1`, and codegen floor
  `agentic-mbse>=0.1.1` (`src/agentic_mbse/sysml/executable_profile.py:49-55`;
  `pyproject.toml:5-8`; `../../../../sysml-codegen/pyproject.toml:23-28`).
- Both locks record companion `0.1.1`, and codegen forces the dirty sibling through an editable uv
  source. Those active locks cannot by themselves prove resolver rejection
  (`uv.lock:24-25`; `../../../../sysml-codegen/pyproject.toml:64-65`;
  `../../../../sysml-codegen/uv.lock:5-8,782-785`).

## Core Concept

The profile is the semantic firewall. It first classifies whether an executable-form assertion has
a real Boolean polarity, then selects one positive source predicate and walks it under a total
numerical whitelist. Its decision carries the selected predicate, `is_negated`, and the derived
`expected_value`; it never edits the predicate to encode assertion meaning.

Downstream code treats the source fact as provenance and the decision as authority. Lowering proves
that fact and decision agree, then carries two separate identities: a predicate-source key that owns
the reusable positive body, and a constraint ID that owns one usage's polarity and wiring. A
read-only pre-output plan groups only by predicate source and compiles one polarity-neutral body.
Each generated assertion wrapper calls that body and passes its own decision-carried polarity pair
to one shared finalizer. The finalizer compares raw truth with expected truth and flips a finite
simple margin once. This supports positive and negated usages of one definition without duplicating
or rewriting the body, and keeps raw `actual_value` equal to the modeled predicate result.

## Key Bets

- **B1.** The eight-category operand facts are sufficient to decide every ordering row without
  Python values or SysIDE calls. *If false → the profile cannot be total from neutral facts and this
  correction would require a fact-schema or runtime-type expansion.*
- **B2.** Every executable assertion has one positive source predicate plus one usage-owned
  polarity. *If false → separate polarity cannot represent modeled assertion meaning and the
  original constraint architecture is wrong.*
- **B3.** A codegen run uses one `ConstraintFacts` object for profile evaluation and lowering, or
  preserves canonical serialization across its codec boundary, including original source identity,
  the duplicated usage predicate, and the selected decision predicate. *If false → decision-only
  byte checks cannot prove that the compiler received the modeled source.*
- **B4.** The companion profile-version guard runs during lowering before graph extension and any
  filesystem output, and the compiled-predicate plan can be built before output clearing. *If false
  → skew or invalid source groups can reach graph/filesystem mutation before rejection.*

## Key Decisions

- **D1. Ordering gets a dedicated total classifier.** `classify_ordering(left, right)` uses the
  closed eight-category product. Only integer/real cross-products and quantity/quantity may reach
  `unit_compatibility`; every other pair blocks. *Rejected: keep using `unit_compatibility` alone
  (it treats all dimensionless categories alike and recreates R-1).*
- **D2. The new R-1 reason is `block_ordering_category_pair`.** It names the pair and says ordering
  requires two integer/real operands or two quantities. Existing unresolved, unknown, malformed,
  dimension, exact-unit, and conversion reasons retain their codes and receive ordering-specific
  repair text. *Rejected: `block_non_numerical_ordering` (quantity/integer is not non-numerical,
  so the name would lie about part of the rejected product).*
- **D3. The malformed-polarity reason is `block_invalid_assertion_polarity`.** Exact acceptance is
  `type(usage.is_negated) is bool`; the diagnostic reports the stable received type name and asks the
  producer to supply a JSON Boolean. *Rejected: truthiness coercion (makes `0`, `1`, and non-empty
  strings host-language semantics).*
- **D4. `UsageDecision` carries both `is_negated` and `expected_value`.** Both public fields are
  `bool | None`. For an executable-form usage with valid polarity they are actual `bool` values and
  `expected_value == (not is_negated)`, regardless of ADMIT, predicate BLOCK, or NON_NUMERICAL.
  Invalid polarity blocks with both fields `None`; unassessed/non-executable forms also use `None`
  because no executable assertion meaning was classified. *Rejected: polarity-only with consumer
  derivation (allows each consumer to recreate the semantic path); expected-only (loses source
  polarity provenance).*
- **D5. Polarity is classified before predicate resolution or walking.** An invalid value emits
  exactly one diagnostic, sets one usage-level BLOCK, and leaves `effective_predicate=None`.
  *Rejected: walk then block (adds irrelevant predicate diagnostics and violates the required
  single-error contract).*
- **D6. Positive source IR is never folded.** `effective_predicate` remains the exact inline or
  definition-selected positive object. Canonical serialized bytes are the cross-boundary proof.
  *Rejected: wrap the IR in `not` (changes bytes and raw evidence); BLOCK negation (removes an
  owner-intended first-scope feature).*
- **D7. Codegen uses decision authority with provenance verification.** Lowering compares the raw
  fact polarity to the decision pair and compares source-selected IR bytes to decision IR bytes.
  It then uses only the decision pair for ID minting, concrete records, and catalog projection, and
  carries `predicate_source_key` from the canonical
  `usage.source.effective_predicate_source` identity, with the specified portable-location fallback
  only for an anonymous inline source.
  *Rejected: delete fact/catalog polarity (loses provenance); continue deriving from the fact
  (keeps the second authority); derive a key from `usage_qualified_name` or IR bytes (splits reusable
  definitions or merges unrelated sources).*
- **D8. Compile a polarity-neutral body once per true source.** Group catalog entries only by
  `predicate_source_key`; require canonical positive `predicate_ir` agreement inside the group;
  validate each entry's polarity pair independently. `compile_predicate_body(ir, fn_name)` returns
  raw Kleene truth plus a source-oriented simple margin. A small shared
  `finalize_assertion(raw, source_margin, *, is_negated, expected_value)` produces status and final
  margin per usage. *Rejected: polarity in the group key (duplicates the body); group-wide polarity
  equality (rejects valid mixed polarity); polarity-bearing shared function (first usage wins).*
- **D9. Compatibility identifiers are exact candidate identifiers.** Set
  `PROFILE_SEMANTIC_VERSION` to `"executable-profile/v4"`, version the companion candidate as
  `0.1.2`, raise codegen's declared floor to `agentic-mbse>=0.1.2`, and resolve both candidate locks
  to `0.1.2`. This item builds hashed candidate wheels; it does not publish or call them released.
  *Rejected: retain v3 or package `0.1.1` (conceals a public decision change); describe an
  unpublished candidate as a release.*
- **D10. Facts and snapshots migrate by re-profiling, not rewriting.** Keep
  `constraint-facts/v1` and snapshot format v3. Existing payload bytes load under the corrected
  package and produce v4 decisions. *Rejected: snapshot-format bump or fixture recapture (the
  stored payload contains facts, not historical `UsageDecision`s).*
- **D11. Build a read-only `ConstraintGenerationPlan` before output clearing.** The plan validates
  catalog models, source keys, source/usage/decision/catalog IR continuity, per-entry polarity,
  group body agreement, emitted predicate names, parse/compile success, and wrapper input
  reconciliation. Emission receives only the validated plan. *Rejected: keep checks inside
  `_generate_modules` (clears and partially writes the target before discovering contradictions).*

## Architecture

### Companion decision boundary

`evaluate_profile` retains the current source-form gate. For `inline` and `definition_typed`, it
runs this order:

1. Require `type(is_negated) is bool`. Otherwise return one `BLOCK` with
   `block_invalid_assertion_polarity`; do not resolve or walk the predicate.
2. Set decision `is_negated` to that Boolean and `expected_value = not is_negated`.
3. Resolve the positive predicate exactly as today. Missing definition/body remains a reason-grade
   BLOCK, but the valid decision polarity pair remains attached.
4. Walk the positive predicate. At each ordering node, recover both operand facts and call the total
   ordering classifier. Append diagnostics depth-first and left-to-right.
5. Return one usage decision. Never rewrite or copy the selected predicate.

The ordering classifier has explicit precedence:

1. Either category `unresolved` → `block_unresolved_operand`.
2. Else either category `unknown` → `block_unsupported_operand_category`.
3. Else pair not in the five-pair whitelist → `block_ordering_category_pair`.
4. Else integer/real pair → `ok`.
5. Else quantity/quantity → existing `unit_compatibility`, preserving malformed-unit,
   unknown-exact-unit, incompatible-dimension, conversion-required, and exact-unit outcomes.

The whitelist is `{integer, real} × {integer, real}` plus `(quantity, quantity)`. This procedure is
independent of the ordering operator, so the same 64-row table runs for each of `<`, `<=`, `>`, and
`>=`. It never calls Python comparison or SysIDE.

### Public decision contract

The additive public shape is:

```python
@dataclass(frozen=True)
class UsageDecision:
    identity: IdentityFact
    location: LocationFact | None
    eligibility: Eligibility
    diagnostics: list[EligibilityDiagnostic]
    unassessed_kind: str | None
    effective_predicate: ExpressionIR | None
    is_negated: bool | None
    expected_value: bool | None
```

The allowed states are exhaustive:

| Decision route | Eligibility | Effective predicate | Polarity pair | Diagnostics |
|---|---|---|---|---|
| Executable form, invalid polarity | `BLOCK` | `None` | both `None` | exactly `block_invalid_assertion_polarity` |
| Executable form, missing/unresolved body | `BLOCK` | `None` | Boolean, complementary | exactly the resolution reason |
| Executable form, body diagnostics | `BLOCK` | selected positive body | Boolean, complementary | one or more error-force reasons |
| Executable form, non-numerical body | `NON_NUMERICAL` | selected positive body | Boolean, complementary | one or more non-numerical reasons |
| Executable form, admitted body | `ADMIT` | selected positive body | Boolean, complementary | empty |
| Unassessed form | `UNASSESSED` | `None` | both `None` | empty; `unassessed_kind` set |
| Non-executable blocked form | `BLOCK` | `None` | both `None` | exactly its form-gate reason |

Five private named constructors cover the seven rows: `_invalid_polarity_block`,
`_missing_body_block`, `_body_decision`, `_unassessed`, and `_non_executable_block`. They populate
every field explicitly. `_body_decision` accepts only ADMIT, predicate BLOCK, or NON_NUMERICAL and
requires the positive body plus Boolean pair. `__post_init__` rechecks the table from eligibility,
predicate presence, diagnostic reason/force, and `unassessed_kind`; it raises `ValueError`, never
`assert`, so the same states reject under `python -O`. In particular, a missing-body BLOCK or
NON_NUMERICAL decision with a missing polarity pair is unrepresentable.

`CONSTRAINT_USAGE_FACT_FIELD_CONSUMERS: Mapping[str, str]` is public beside the decision types. Its
keys are exactly the eleven `ConstraintUsageFact` fields. Values name the profile consumer or the
tested downstream rationale:

- `identity`, `location` → decision identity and diagnostics.
- `source` → form gate, effective-predicate selection, and predicate-source identity.
- `is_negated` → polarity classifier and expected-truth derivation.
- `predicate` → inline selection and same-IR proof.
- `owner`, `scope`, `actuals`, `omitted_default_formals`, `inherited_into` → lowering-owned
  expansion/resolution; decision-irrelevant at the profile boundary.
- `membership_kind` → lowering identity minting and catalog provenance; decision-irrelevant after
  `source.form` has classified the usage.

The map is a completeness inventory, not a dispatcher. A kept test compares its keys with
`{field.name for field in dataclasses.fields(ConstraintUsageFact)}`. Separate behavior tests prove
that `source` produces the carried source key and `membership_kind` changes the minted identity;
the guard does not pretend that pinning rationale prose proves consumption.

### Coordinated codegen flow

The existing `zip(facts.usages, profile.decisions, strict=True)` is the join. Before actual
resolution or concrete expansion, lowering performs a decision-consistency guard:

- every executable decision route is checked against the state table; ADMIT additionally requires
  an effective predicate and no diagnostics;
- `usage.is_negated` must be the same Boolean as `decision.is_negated`;
- `usage.source.effective_predicate_source` must carry the expected source identity;
- for `definition_typed`, the referenced definition predicate, the usage's duplicated predicate,
  and `decision.effective_predicate` must have equal canonical bytes;
- for `inline`, the effective-source identity must equal the usage identity and the original usage
  predicate must equal decision bytes;
- any missing or contradictory value raises `CodeGenerationError` during lowering, before
  constraint graph extension and before filesystem output. Earlier extraction and in-memory
  context-building work has already occurred; the design makes no stronger claim.

After the guard, `decision.is_negated` supplies the `constraint_id` tuple and
`ConcreteConstraint.is_negated`; `decision.expected_value` supplies
`ConcreteConstraint.expected_value`. `predicate_source_key` is derived from the already-extracted
effective source, never from usage name or IR contents:

| Source form | `predicate_source_key` | Group-equal fields | Per-entry fields |
|---|---|---|---|
| `definition_typed` | `definition:<effective-source QN>` | canonical positive `predicate_ir` | polarity pair, constraint ID, owner, inputs, evaluation channel |
| named `inline` | `inline:<effective-source QN>` | canonical positive `predicate_ir` | polarity pair, constraint ID, owner, inputs, evaluation channel |
| anonymous `inline` | `inline:<kind>:<portable file>:<line>:<column>` | canonical positive `predicate_ir` | polarity pair, constraint ID, owner, inputs, evaluation channel |

The anonymous key uses the same route-normalized, root-relative location identity already required
for anonymous source identity; absence of both QN and location is a lowering error. The key excludes
polarity, concrete owner, and IR hash. `ConcreteConstraint` and `ConstraintCatalogEntry` each gain
the required `predicate_source_key: str` field and retain the current complementary-pair validator
(`resolution/models.py:387-438,474-482`). The raw usage/source facts remain unchanged as provenance.

Catalog assembly projects the decision-derived pair, true source key, and exact `predicate_ir`.
Groups require only source-key and canonical-positive-body agreement. Each entry independently
validates `type(is_negated) is bool`, `type(expected_value) is bool`, and complementarity; opposite
polarities inside one source group are valid and expected.

The compiler boundary splits in two:

- `compile_predicate_body(ir, fn_name)` emits one polarity-neutral function per
  `predicate_source_key`. It returns raw Kleene truth and a source-oriented simple margin. It does
  not know `constraint_id`, `is_negated`, `expected_value`, status, or final margin sign.
- `finalize_assertion(raw_value, source_margin, *, is_negated, expected_value)` is emitted once in
  the shared predicates/runtime module. It verifies the Boolean pair, returns `indeterminate` for
  `raw_value is None`, otherwise compares raw truth with `expected_value`, negates a finite simple
  margin once when `is_negated`, and normalizes either signed zero to `0.0`. A `None` compound margin
  stays `None`.

Each assertion wrapper imports its source-keyed body, calls it once, then calls the shared finalizer
with that catalog entry's constants. Two distinct positive/negated usages of one definition
therefore emit one body function, two wrappers, identical raw results, opposite expected truth, and
one sign adjustment per wrapper.

The source margin keeps the current structural convention without polarity: `b - a` for `<`/`<=`,
`a - b` for `>`/`>=`, and `None` for a compound predicate. The body returns
`_PredicateBodyResult(actual_value, source_margin)`. Zero normalization belongs only to the
finalizer, so neither body compilation nor a wrapper can apply the sign or normalize twice.

### Pre-output validation order

The profile-version and decision/source-continuity guards remain inside context building/lowering,
before constraint graph extension. After a complete `PipelineContext` exists, `run_codegen` performs
this read-only order before `_clear_output_directory()` or `_setup_output_directories()`:

1. Existing constraint-name, duplicate-output-path, params-coverage, and link-safety checks.
2. Revalidate concrete and catalog models without `assert`-based narrowing.
3. Reject missing keys and duplicate constraint IDs; group repeated source keys and reject body-byte
   divergence inside a group.
4. Validate every entry's polarity pair, predicate round-trip, wrapper inputs, and source-keyed
   function name; reject normalized name collisions.
5. Parse and compile every polarity-neutral body into a `ConstraintGenerationPlan` held in memory.

Only a successfully validated plan permits clearing or creating output directories. The plan maps
source keys to compiled body source/arguments and constraint IDs to source keys plus per-usage
finalization constants. `_generate_modules` and predicate-module emission consume the plan; they do
not regroup, select a first entry, or compile. General filesystem failures can still occur during
emission, but all Item 1 semantic/catalog/compiler contradictions fail before any output-tree
mutation.

### Diagnostic flow

Each ordering node emits zero or one diagnostic. Its local precedence is fixed; once one row fires,
the comparison emits it and does not append a second left/right/category/unit reason:

| Priority | Condition | Result |
|---|---|---|
| 1 | arity is not two | `block_unsupported_node`; message `comparison has <N> operands; expected 2` |
| 2 | left value recovery fails | first left recovery reason |
| 3 | right value recovery fails | first right recovery reason |
| 4 | either category is `unresolved` | `block_unresolved_operand` |
| 5 | either category is `unknown` | `block_unsupported_operand_category` |
| 6 | pair is outside the five-pair whitelist | `block_ordering_category_pair` |
| 7 | quantity fact/unit is malformed or exact unit unknown | existing specific reason |
| 8 | quantity dimensions or exact units differ | existing specific reason |
| 9 | admitted integer/real or exact-unit quantity pair | no diagnostic |

Operand recovery walks each operand in the existing deterministic expression traversal order and
returns only its first failure. The comparison checks the left recovery result before the right, so
two malformed operands produce the single left-side reason for that comparison. This local collapse
does not collapse sibling comparisons in a compound predicate.

Compound predicates visit proposition children depth-first, left-to-right, so N malformed ordering
nodes produce exactly N diagnostics in that order. A numerical compound promotes contained
non-numerical diagnostics to the existing blocking-containment reason; a wholly non-numerical usage
stays one `NON_NUMERICAL` decision.

Cardinalities stay distinct:

- L4 counts one outcome per usage.
- L6 emits one `ERROR` per BLOCK diagnostic and one aggregated `WARNING` per NON_NUMERICAL usage.
- Codegen renders every NON_NUMERICAL usage warning exactly once, in usage order, before checking
  for BLOCK; it then emits one deterministic halt containing every BLOCK diagnostic. Warnings never
  replace or mask that halt.

All renderers use `file:line` when location exists and the literal `<no location>` otherwise. The
two new exact messages are:

- `block_ordering_category_pair`: `ordering '<op>' requires Integer/Real operands or two Quantity operands; got <left>/<right>. Rewrite both operands as one admitted numerical pair.`
- `block_invalid_assertion_polarity`: `assertion polarity must be a JSON Boolean; got type '<type>'. Re-extract or repair the fact payload so is_negated is true or false.`

Existing ordering reason codes use these exact repair templates:

| Reason | Message |
|---|---|
| `block_unresolved_operand` | `ordering '<op>' has an unresolved operand type. Resolve both operands to typed model features before generation.` |
| `block_unsupported_operand_category` | `ordering '<op>' has an unknown operand category. Use Integer, Real, or exact-unit Quantity operands.` |
| `block_malformed_operand_fact` | `ordering '<op>' is missing a quantity unit fact. Re-capture the model facts with a compatible companion package.` |
| `block_unknown_exact_unit` | `ordering '<op>' needs exact units for both Quantity operands. Declare the exact modeled units.` |
| `block_incompatible_dimensions` | `ordering '<op>' cannot compare different dimensions. Use operands with the same modeled dimension.` |
| `block_unit_conversion_required` | `ordering '<op>' does not convert units. Express both operands in the same exact modeled unit.` |

`block_unitless_dimensioned` remains reachable from equality/arithmetic but not from ordering v4:
quantity/unitless ordering is a non-whitelist pair and deterministically uses
`block_ordering_category_pair`. Messages do not include unordered collections, arbitrary object
representations, or host exception text.

## Required Invariants

- **I1 — Total ordering.** For every ordering operator and every one of 64 ordered category pairs,
  exactly one classifier result exists. Only five pairs reach numerical/unit admission checks.
- **I2 — No host semantics.** Profile decisions depend only on neutral facts and the explicit
  whitelist. No Python value comparison, truthiness, or SysIDE evaluation occurs.
- **I3 — Boolean polarity.** An executable-form usage reaches its body only with
  `type(is_negated) is bool`; malformed polarity produces one BLOCK and no body diagnostic.
- **I4 — Complementary decision pair.** A classified decision has actual Booleans and
  `expected_value == (not is_negated)` at every subsequent seam; every decision matches one state
  table row under normal and optimized Python.
- **I5 — Positive source continuity.** Effective-source identity and canonical bytes agree from the
  original inline/definition source through the duplicated usage predicate, decision, concrete,
  catalog, generation plan, and polarity-neutral compiler input.
- **I6 — One authority.** Source facts provide provenance; the decision provides codegen semantics.
  A lowering mismatch fails before graph extension; a plan mismatch fails before output clearing.
- **I7 — Source-keyed compile once.** Exactly one polarity-neutral body is emitted per true
  predicate-source key. Opposite-polarity usages of one definition share it without sharing usage
  interpretation.
- **I8 — Exact-once interpretation.** Polarity changes status and a simple margin per usage, never
  the body or raw `actual_value`; zero becomes `0.0`; compound margin stays absent.
- **I9 — Route parity.** Live extraction and facts-codec input yield byte-equivalent source keys,
  decisions, diagnostics, lowering records, catalogs, plans, and body-compiler inputs.
- **I10 — Deterministic compound diagnostics.** N malformed ordering comparisons yield N ordered
  diagnostics, N ordered L6 errors, one BLOCK decision, and one codegen halt.
- **I11 — Consumer completeness.** The field-consumer map key set equals the dataclass field set;
  behavioral tests prove the source-key and membership-identity consumers.
- **I12 — Compatibility is fail-closed.** Both skew directions reject in hermetic wheel tests; only
  the exact profile-v4 candidate pair passes. The new-codegen/old-companion resolver rejection is
  caused by the declared `agentic-mbse>=0.1.2` floor, with every other dependency available from the
  same hashed local closure and an `agentic-mbse==0.1.2` positive control passing there.
- **I13 — Pre-output semantics.** Catalog, group, source-continuity, name, input, and body-compile
  validation completes before `_clear_output_directory()` and directory creation.
- **I14 — Stored facts are historical facts, not decisions.** Snapshot v3 and constraint-facts/v1
  bytes do not change for this semantic migration.
- **I15 — Native arithmetic failures remain native.** Division by zero, zero-to-negative power,
  exponent overflow, and other body exceptions propagate unchanged; Item 1 does not convert them to
  indeterminate or claim the external F1 normalization contract.

## Component Overview

- **`src/agentic_mbse/sysml/executable_profile.py`** — v4 constant, two reason codes, total ordering
  classifier, polarity-first decision construction, public decision fields, and consumer map.
- **`src/agentic_mbse/validation/level6_architecture.py`** — stable `<no location>` rendering while
  retaining one-error-per-diagnostic translation.
- **`docs/patterns/constraints.md`** — v4 ordering whitelist, separate polarity, raw-value behavior,
  and repair guidance.
- **Companion tests** — exhaustive ordering matrix; direct/codec polarity rejection; live/codec
  four-row polarity/source-form matrix; L4/L6 diagnostic parity; field-consumer drift guard.
- **`src/sysml_codegen/analysis/constraint_lowering.py`** — v4 guard, fact/decision consistency,
  decision-authority lowering, exact positive-IR guard.
- **`src/sysml_codegen/resolution/models.py` and `generation/constraint_catalog.py`** — add the true
  source key; retain per-entry polarity and positive IR; group only for body-byte agreement.
- **`src/sysml_codegen/generation/predicate_compiler.py`** — polarity-neutral body compiler and the
  small shared per-usage finalizer.
- **`src/sysml_codegen/generation/modules.py` and `cli/__init__.py`** — build a read-only validated
  generation plan before output clearing; emission consumes the plan without regrouping/recompiling.
- **Codegen metadata/tests** — raised dependency floor and lock, route ladder, skew matrix, exact-once
  execution oracle, unchanged-snapshot re-profiling.

## Non-Goals

- New equality, tolerance, typed-runtime, or non-numerical ordering semantics.
- Rewriting predicate IR to represent assertion polarity.
- Changing constraint-facts/v1, snapshot v3, occurrence identity, actual resolution, or study policy.
- Reworking Item 2 name safety, Item 4 snapshot portability, Item 6 symlink symmetry, or their
  fixtures except where a focused compatibility assertion reads them unchanged.
- Normalizing native arithmetic exceptions or closing `[GAP-CLOSE-F1-TEAX-NORMALIZATION]`.
- Changing PR state, merge order, commits, pushes, or release publication in this item.

## Implementation Notes

- Keep `unit_compatibility` shared by equality and arithmetic. Ordering calls the new classifier;
  changing the shared helper would risk unrelated v3/v4 rows.
- The category matrix must assert the exact reason for every row, not only ADMIT/BLOCK. Generate
  cases from the fixed eight-item tuple and four operators; do not generate expectations from the
  production classifier.
- Direct malformed-polarity tests must bypass dataclass type hints with `None`, strings, integers,
  and one container. Codec tests mutate canonical JSON and parse it through the public codec.
- The live matrix includes positive/negated × inline/definition-typed plus two distinct usages of
  one definition under opposite polarities. Compare effective-source identity and
  `serialize_expression` bytes at every seam; do not compare object identity across codec/snapshot.
- Before implementation, record each repository's `HEAD`, porcelain status, binary tracked diff,
  untracked-path inventory, and SHA-256 per overlapping file into the item evidence/temp workspace.
  Every untracked file selected for a candidate overlay must also have one sealed manifest entry:
  normalized repository-relative path, SHA-256 of regular-file content or symlink-target bytes,
  file type (`regular` or `symlink`), full permission mode, and executable-bit mask. Reject duplicate,
  absolute, parent-traversing, device, socket, FIFO, and otherwise unsupported entries. Verify each
  source entry against the manifest before import, copy without following symlinks while preserving
  mode, then verify the overlay entry against the same manifest. Directories are created from the
  sealed paths and are not imported as content. Hash the completed manifest and retain it with the
  candidate patch evidence. After each phase, compare the active trees to that dirty baseline plus
  the phase allowlist. A path outside the allowlist or an unexplained baseline change stops the phase.
- Historical and skew evidence uses clean temporary worktrees at companion `4ed2a07` and
  `54a95d2`, and codegen `512786c`. Candidate evidence uses clean temporary overlay worktrees made
  from an explicit reviewed candidate patch and untracked-file manifest. Never reset, checkout, or
  build resolver evidence from the active dirty trees.
- Do not regenerate all snapshots, normalize unrelated files, or rewrite lock data beyond the two
  version entries and codegen dependency floor. Run focused overlap gates for Item 2 name safety,
  Item 4 snapshot portability, and Item 6 seal symmetry after each codegen phase that touches a
  shared file.
- Companion evidence runs first. Codegen evidence records the exact companion revision/wheel hash
  before any consumer test so an editable install cannot silently select another checkout.
- Licensed runs use `uv run --env-file .env`; never print the license value.

## Potential Risks

- **Semantic pair drifts after decision.** Assignment-validating Pydantic models and the compiler
  consistency check catch mutation at concrete, catalog, and compiler boundaries.
- **Source-key construction drifts across routes.** Definition keys use the extracted definition QN;
  inline keys use the extracted effective-source identity plus portable anonymous fallback. The
  live/codec ladder compares keys before grouping.
- **Per-wrapper finalization duplicates semantics.** Emit one shared finalizer and call it with
  per-usage constants; wrappers contain wiring only.
- **Matrix expectations mirror implementation.** Keep the 64-row oracle as static test data or a
  test-only rule spelled independently from production, with exact five-pair whitelist assertions.
- **Candidate dependency floor is bypassed by editable installs or obscured by a sparse wheelhouse.**
  Record runtime `__version__`, profile version, source revision, and wheel hash. Build one no-index
  wheelhouse containing both companion versions needed by the matrix and the complete compatible
  direct/transitive wheel closure for codegen. Pin every selected distribution and SHA-256 in the
  resolver inputs. Use the same wheelhouse for the causal conflict and positive control, plus a
  separate `--no-deps` runtime-guard bypass.
- **Broad fixture recapture overwrites Item 4 portability work.** Re-profile existing bytes in
  place and hash the `constraint_facts` subtree before/after; no capture command belongs in this
  migration.
- **Diagnostic wording diverges between L6 and codegen.** Both render the same
  `EligibilityDiagnostic`; tests compare ordered reason/message/location tuples before checking
  their consumer-specific wrapper text.
- **Non-finite coverage is mistaken for exception normalization.** Limit the oracle to already
  materialized non-finite operands. Keep explicit division/negative-power/overflow tests asserting
  the same native exceptions cross the new body/finalizer split unchanged.

## Integration Strategy

Implementation is companion-first:

1. Capture both dirty baselines. In a clean companion overlay, add profile v4 semantics, decision
   states, diagnostics, docs, and tests. Bump `pyproject.toml`, `src/agentic_mbse/__init__.py`, and
   the companion lock to candidate `0.1.2`; build and hash the candidate wheel.
2. Apply the reviewed companion patch to the active tree. Run companion evidence first and compare
   against the dirty baseline.
3. In a clean codegen overlay, raise the declared floor and lock, update the v4 guard, carry source
   identity, split body compilation/finalization, and add the read-only pre-output plan.
4. Apply the reviewed codegen patch to the active tree. Run route, runtime, snapshot, optimized, and
   Item 2/4/6 overlap gates; compare against the dirty baseline after each phase.
5. Seal the complete local wheelhouse and run hermetic skew and exact-pair candidate evidence from
   its hashed wheels and clean worktrees. Publication and full wave release-readiness remain Epic
   Item 8.

The migration has no dual-read period. Old codegen sees v4 and halts during lowering before graph
extension/filesystem output. Corrected codegen's metadata rejects package `0.1.1`; its runtime guard
also rejects profile v3 when a hermetic test deliberately bypasses resolution. Existing snapshot-v3
files load unchanged and are immediately evaluated by the installed v4 procedure.

## Validation Approach

### Companion seam

- **Ordering product:** 4 operators × 8 left categories × 8 right categories = 256 cases. Assert
  exact result code, exact diagnostic cardinality, and no Python comparison. Add focused compatible
  and incompatible quantity subcases after the category gate.
- **Polarity boundary:** positive/negated × inline/definition-typed, direct plus codec. Assert exact
  Boolean fields and complementary truth. Mutate to `None`, `"false"`, `0`, `1`, list, and object;
  each yields one `block_invalid_assertion_polarity`, no predicate-walk diagnostic.
- **Compound diagnostics:** one body with several malformed ordering nodes nested under `and`/`or`;
  include two-sided structural failures and mixed category/unit failures; assert one result per
  comparison under the precedence table, exact ordered tuples, and one BLOCK. Feed the same facts to
  L6 and assert one ordered error per diagnostic plus `<no location>` behavior. Separately assert one
  aggregated L6 warning per wholly NON_NUMERICAL usage.
- **Consumer drift:** `test_constraint_usage_fact_field_consumers_are_exhaustive` compares exact key
  sets. Targeted tests prove `source` selects source key/body and `membership_kind` changes identity.
- **Live/codec:** licensed extraction of the four-row fixture, canonical codec round-trip, then
  byte-equal source keys, normalized decisions, and diagnostics.

### Codegen seam

- **Route ladder:** for definition-typed rows, compare definition identity/body → effective-source
  identity → duplicated usage predicate → decision → concrete → catalog → plan → body-compiler
  argument. For inline rows, compare usage/effective-source identity and original usage predicate
  through the same later rungs. Run live and snapshot/codec routes and compare every identity/byte.
- **Contradiction guards:** mutate each of decision polarity, expected truth, concrete pair,
  catalog pair, source key, group body, and each continuity rung independently. Lowering mutations
  fail before graph extension; catalog/group/name/input/compile mutations fail while building the
  plan before a sentinel output directory is cleared or changed. Run normal and `python -O`.
- **Two usages, one definition:** model distinct positive and negated usages of one reusable
  definition. Assert one source key, one emitted body function, two wrappers, independently valid
  polarity pairs, and no first-entry dependency under reversed catalog order.
- **Exact-once runtime oracle:** those paired usages share one positive body. Cover true/nonzero,
  false/nonzero, strict zero, inclusive zero, and already-materialized non-finite operands. Assert
  the spec table exactly, including equal raw `actual_value`, opposite expected truth, one margin
  sign adjustment per usage, `0.0`, and `None` indeterminacy.
- **Native exception boundary:** division by zero, zero-to-negative power, and exponent overflow
  propagate the same exception class/message before and after the body/finalizer split. Do not feed
  these cases into the non-finite oracle or claim indeterminate.
- **Warning/halt order:** multiple NON_NUMERICAL usages followed/interleaved with BLOCK usages emit
  each warning once in fact order, then one deterministic BLOCK halt; compiler/plan/output mutation
  counters remain zero.
- **Snapshot migration:** hash existing snapshot files and their `constraint_facts` subtrees, load
  them without rewrite, assert profile v4 decisions, and confirm hashes remain unchanged.

### Compatibility seam

- Build old companion `0.1.1` from clean `54a95d2`, new companion candidate `0.1.2` from the reviewed
  clean overlay, old codegen from clean `512786c`, and the new codegen candidate from its clean
  overlay. Record commit/patch identity and SHA-256 for every wheel. Populate one immutable local
  wheelhouse with those artifacts and a complete compatible wheel closure for every other direct
  and transitive requirement. Its lock manifest records normalized distribution name, version,
  wheel filename/tags, and SHA-256 for every selectable file; resolver commands use `--no-index`,
  that wheelhouse alone, fully pinned hashed inputs, and no editable sources or network indexes.
- **Old codegen + new companion:** install the old-codegen and new-companion wheels with their sealed
  dependency closure from the same wheelhouse in an isolated environment; the v3 runtime guard must
  reject profile v4 during lowering before graph extension/filesystem output.
- **New codegen + old companion:** from the complete wheelhouse, resolve the new codegen candidate
  together with the explicit request `agentic-mbse==0.1.1`. Normalize the resolver's cause records
  and assert the exact conflicting pair: the candidate codegen metadata requires
  `agentic-mbse>=0.1.2`, while the test requests `agentic-mbse==0.1.1`. Also assert that no other
  distribution is missing or unsatisfied. In a separate isolated environment, install the new
  codegen wheel with `--no-deps` plus the old companion wheel and prove the v4 runtime guard rejects
  v3. The editable repository lock is not evidence for either claim.
- **Same-wheelhouse positive control:** without changing the wheelhouse or any non-companion pin,
  replace only the explicit companion request with `agentic-mbse==0.1.2`; resolution and installation
  must succeed. This proves the negative result is caused by `>=0.1.2` versus `==0.1.1`, rather than
  an incomplete dependency closure or incompatible unrelated pin.
- **Exact candidate pair:** resolve and install the two candidate artifacts with their sealed
  dependency closure from the same wheelhouse, then pass profile, lowering, pre-output plan,
  catalog/compiler, snapshot, and execution selections. Assert both repository locks name `0.1.2`,
  runtime reports package `0.1.2` and profile v4, and evidence records hashes.
- Run the companion suite before codegen selections. Run applicable focused suites under normal and
  optimized Python. Finish with repository-defined lint/format/diff checks, without PR operations.

## Next-Stage Handoff

Treat D1-D11, the decision state table, source-key table, diagnostic precedence, two reason
codes/messages, candidate versions, pre-output plan, and exact-once oracle as fixed. The plan must
be companion-first, capture both dirty baselines before edits, and isolate each historical RED in
clean worktrees. De-risk the true-source grouping first with two opposite-polarity usages of one
definition, then build the pre-output plan and prove a sentinel target is untouched on every
semantic failure. Preserve native arithmetic exceptions and all unrelated Item 2/4/6 work.

No technical question remains open. After design review, use `my-plan` for the coordinated
two-repository implementation; do not jump directly to implementation.

---

Next Step: `my-design-review`, then `my-plan` after approval.
