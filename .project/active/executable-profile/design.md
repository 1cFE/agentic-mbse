# Design: Executable Profile — Eligibility Gates and Named Diagnostics

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Branch:** `constraint-exec-epic` (commit e9cce18)
**Epic:** CONSTRAINT-EXEC, Item 3

## Overview

A pure decision procedure that reads Item 1/2's `ConstraintFacts` and returns, per constraint
usage, exactly one outcome — **admit**, **block** (with named diagnostics), or **unassessed** —
so every modeled assertion ends in one visible place and nothing reaches codegen silently.

## Related Artifacts

- **Spec:** `.project/active/executable-profile/spec.md` (read fully; its `[HARD]`/`[NEED]` points are fixed here)
- **Epic:** `.project/reference/epic_constraint_execution.md` (Item 3)
- **Concept:** `.project/reference/constraint-execution-concept.md` (executable-profile paragraph, Non-Goals, Appendix B / S2 operator matrix v1, S1 carry-forwards)
- **S1 golden:** `tests/fixtures/constraint_fact_shapes/golden.json` (`type_units.equality_cases` — the 14-row oracle)
- **Landed inputs:** `src/agentic_mbse/sysml/{constraint_facts,expression_ir,expression_facts,constraint_extraction}.py`
- **Seams to replace:** `validation/level4_constraints.py` (0% placeholder), `validation/level6_architecture.py:595` (blanket warning)

## Research Findings

- **Fact surface (all present, no new extraction).** Every field the gate needs is on the landed
  types. Leaf operand facts hang off `OperandTypeFact` (`expression_facts.py:52`): `category` is
  the full eight-value vocabulary (`boolean/string/integer/real/enum/quantity/unresolved/unknown`),
  plus `enumeration` and a `UnitFact(unit, dimension)`. `unit=None, dimension=<set>` is the
  first-class "dimension known, exact unit unknown" state (`expression_facts.py:37`).
- **Operator vocabulary is closed.** Live extraction routes any operator outside a fixed allowlist
  to `UnsupportedNode` (`constraint_extraction.py:69` `_OPERATOR_SYMBOLS`). So `OperatorNode.operator`
  is one of `{< <= > >= == != and or not xor implies + - * / ** ^}`; `[` becomes a
  `UnitAnnotationNode`; a feature chain becomes a `FeatureReferenceNode` with non-empty
  `chain_segments`. The gate's node-kind walk sees only these shapes.
- **`operand_type` marks value vs proposition.** `OperatorNode.operand_type` is `None` on
  comparison/connective nodes and set on arithmetic nodes (`constraint_extraction.py:429`); leaf and
  unit-annotation nodes always carry it. This is the seam that recovers "the type of this operand"
  at a comparison, whether the operand is a leaf, a `[m]` annotation, or an arithmetic subtree.
- **The golden already carries the answer key.** `type_units.equality_cases[].decision` holds the
  11 decision codes (4 `support_*`, 7 `block_*`) the profile must reproduce; Item 1 excluded the
  `decision` field from production facts, so Item 3 is where these become executable truth. Operand
  facts for the two new inequality cases already exist in the golden (metre/centimetre in
  `quantity_convertible_unit`; integer/real in `integer_real`).
- **Naming collision.** `agentic_mbse.extraction.profile` already exists (the PDF pipeline). The new
  module must not be called `profile`; it lives beside the facts in `sysml/`.
- **`sysml/types.py` is syside-free** (pydantic/enum only), so `ValidationCode` can gain entries
  without threatening the license-free guarantee — but the profile module itself stays decoupled
  from it (see B1/D2).

## Core Concept

The profile is a **whitelist decision procedure**: a modeled assertion is executable only if every
construct in its effective predicate is on an explicit admit list and every operand pair passes an
explicit type/unit gate. Anything not proven admissible **blocks** — totality comes from
default-deny, not from enumerating every bad case.

Each usage flows through three ordered layers, and the layer ordering short-circuits (first layer
that decides, stops):

1. **Form gate** — dispatch on `ConstraintSource.form`. `satisfy`, `requirement_constraint`
   (require/assume), `plain_usage` → **unassessed**; `named_usage_reference` → **block**; only
   `inline` and `definition_typed` asserts continue. An unknown form → block (default-deny).
2. **Resolve then node-kind walk** — first *resolve* the effective predicate (the usage's own
   `predicate` for inline; for definition-typed, look up `source.constraint_definition.qualified_name`
   in the `{qn: ConstraintDefinitionFact}` index and take that definition's `predicate`). Resolution
   is where the two absence cases route under default-deny **before** any walk: a definition-lookup
   miss → **block** `block_unresolved_definition`; a resolved-but-`None` predicate (bodyless
   `constraint def Foo;`, or a degenerate inline assert — both fields are `ExpressionIR | None`) →
   **block** `block_missing_predicate`. Only a non-`None` predicate is walked. Each node is then
   classified by role: a **proposition** (comparison/connective) or a **value**
   (leaf/arithmetic/unit-annotation). Feature chains, invocations, `xor`, `implies`,
   `UnsupportedNode`, unadmitted operators (including `!=`), and unadmitted node roles each emit a
   construct-named block diagnostic.
3. **Operand-fact gate** — at every comparison node, apply the equality gate (`==`) or the unit
   policy (`< <= > >=`) to the two operands' recovered `OperandTypeFact`; at every arithmetic node,
   apply the unit policy. Each produces one of the 11 golden decision codes.

The key insight from S2: the predicate compiler strip-renders unit annotations, so it is **not** a
unit safety net. The gate is the only thing standing between a unit-mismatched comparison and a
silent bare-float comparison — which is why it must run over the *same* `ExpressionIR` the compiler
lowers, not a re-derived one.

It composes with the landed pieces and adds no parallel mechanism: it reads `ConstraintFacts`
(never syside, never the evaluator), reuses `OperandTypeFact`/`UnitFact` for all type reasoning, and
hands its decisions to two existing seams (L4 coverage, L6 diagnostics) and one new one (codegen
preflight).

## Key Bets

- **B1. The eight-value `category` plus `UnitFact` is a sufficient basis for every gate decision.**
  The golden's 14 rows resolve purely from `(category, enumeration, unit)` with no evaluator call.
  *If false → some decision needs a fact the neutral schema doesn't carry, and either the schema
  grows (Item 1 rework) or that case becomes an explicit profile restriction.*
- **B2. One `ConstraintFacts` value can be made to feed both preflight and compilation.** The seam
  holds only if sysml-codegen builds facts once (live-extracted or parsed **once**) and consumes the
  profile's resolved effective predicate rather than re-resolving or re-parsing. The guarantee has
  two arms by construction path (D7): in-process it is object identity, resting on the single-parse
  precondition; across a serialization boundary (Item 8's license-free snapshot path) it is
  serialization-equality, which object identity cannot provide. *If false → a predicate passes a gate
  reading one IR and reaches a compiler reading another, reopening the S2 drift hole.*
- **B3. Live SysIDE never emits a true n-ary `and`/`or`/arithmetic node** (it nests binaries; S2
  carry-forward 4). The gate treats `OperatorNode` uniformly by operator and operand count, so this
  is latent, not special-cased. *If false → an n-ary node's operands are still each classified, so
  the walk still terminates; only untested, not broken.*

## Key Decisions

- **D1. Module placement: `src/agentic_mbse/sysml/executable_profile.py`.** *Rejected:*
  `sysml/profile.py` (collides conceptually with `extraction.profile`); placement under
  `validation/` (the profile is a facts→decisions library consumed by *both* validation and codegen,
  so it belongs beside the facts, not inside one consumer).
- **D2. The profile defines its own decision/diagnostic dataclasses; it does not import
  `ValidationCode` or syside.** L4/L6 translate `EligibilityDiagnostic.reason` → `ValidationIssue`.
  *Rejected:* profile emits `ValidationIssue` directly (couples the license-free library to the
  validation layer and pydantic; blocks reuse by codegen).
- **D3. Operand-fact gate is a code-branch decision procedure (ordered guards), not a literal
  lookup table.** The unit sub-structure (`unit`/`dimension`/`None`) has no finite key without
  exploding a cross-product table, and precedence (unit checks before type checks) reads clearly as
  sequenced guards. The golden.json *is* the table — it validates the code. *Rejected:* a table keyed
  on the category cross-product (sparse, can't encode the `unit=None` precedence cleanly); a
  per-case `if` ladder with no shared helper (duplicates the unit logic between `==` and `<=`).
- **D4. `==` and `<=`/`<`/`>`/`>=` share one `unit_compatibility(left, right)` helper; equality
  layers the real-tolerance and enum checks on top.** The only differences: same-exact-unit quantity
  and integer/real mix **admit** for ordering, **block** for equality. *Rejected:* two independent
  gates (drifts; the golden proves they share operand facts).
- **D5. `!=` blocks under default-deny (`block_unsupported_operator`).** It is not in the concept's
  admit list and has no golden row; blocking is loud and safe (the author gets a named diagnostic),
  and folding it into the equality gate is a cheap, lossless future relaxation. *Rejected:* admit
  `!=` via the equality gate now (unpinned behavior beyond the spec's enumerated admit set).
- **D6. A bare-Boolean-reference predicate (whole predicate is a `FeatureReferenceNode`/`LiteralNode`
  of category boolean, or a boolean variable as a connective operand) blocks under default-deny
  (`block_non_predicate_root`).** The spec explicitly parks this to design; first scope stays minimal.
  *Rejected:* admit bare booleans (widens scope with no golden evidence; a future item can add it to
  the admit set explicitly).
- **D7. The same-IR seam is carried by the decision object, with two arms matching the spec's "same
  instance *or* same serialized facts."** `UsageDecision.effective_predicate` holds the
  `ExpressionIR` the gate walked; the preflight contract requires the compiler to lower *that*,
  never a freshly resolved one.
  - *Live single-process arm — object identity.* Precondition: preflight and the compiler run in one
    process over one `ConstraintFacts` value parsed/extracted **once**. Under that precondition
    `admitted[].effective_predicate` is the identical object the compiler lowers. The assertion lives
    on the codegen side, as a `gated_ir is compiled_ir` check at the pre-compile seam.
  - *Snapshot license-free arm — serialization-equality.* Across a parse boundary (Item 8's
    `constraint_facts.parse()`), object identity is false by construction (two parses = two graphs),
    so the check is `serialize_expression(compiled_ir) == serialize_expression(gated_ir)` — the
    compiler asserts the serialized predicate it is about to lower equals the one the gate walked.
    `serialize_expression` already exists (`expression_ir.py:133`); this arm is the verifiable form
    for the snapshot path.

  *Rejected:* object identity as the sole guarantee (vacuous across a serialization boundary — the
  exact hole the spec's "or same serialized facts" clause closes); rely on call-ordering convention
  (the spec forbids "precedes" as mere convention); assert only in a sysml-codegen test (necessary
  but not sufficient — the API must make drift impossible, not just detectable).
- **D8. Introduce `PROFILE_SEMANTIC_VERSION = "executable-profile/v1"` alongside the existing
  package-version pin.** A behavior change (e.g. relaxing the dimension-only block) bumps it, so the
  consumer can assert it and see the change; the fact-schema version wouldn't move. *Rejected:*
  package version alone (a patch release could change decisions invisibly).
- **D9. The two new inequality-unit fixtures reuse the certified operand facts** (metre/centimetre
  from `quantity_convertible_unit`, integer/real from `integer_real`) under a new
  `type_units.inequality_cases` block, each `{name, operator, left, right, decision}`. The `left`/
  `right` operand objects are a **byte-copy** of the certified `equality_cases` operands — not a hand
  re-authoring — since the operator does not change the operand facts and only the `decision` (the
  hand-authored answer key Item 1 excluded from production facts) is new. *Rejected:* add `<=` probes
  to `type_units.sysml` and re-extract (heavier, and edits the S1-certified fixture); re-authoring the
  operand facts by hand (could drift from what live extraction produces).

## Architecture

**Data flow.** `ConstraintFacts` → `evaluate_profile(facts)` → `ProfileResult` (a list of
`UsageDecision`). Three consumers read `ProfileResult`:

- **L4** (`analyze_constraints`) reports eligibility **coverage** — counts of admit/block/unassessed
  over asserted constraints — replacing `check_constraint_coverage`.
- **L6** (`check_constraint_executability`) emits one **WARNING `ValidationIssue` per blocked
  construct** (construct + location + identity + reason), and nothing for admitted or unassessed
  usages — replacing the blanket per-usage warning.
- **sysml-codegen** calls `preflight(facts)` **before any compilation**; if any would-execute usage
  is blocked it halts generation and emits the diagnostics; otherwise it lowers each admitted
  decision's `effective_predicate`.

**Effective-predicate resolution lives in the profile.** For `definition_typed`, the profile looks
up `source.constraint_definition.qualified_name` in a `{qn: ConstraintDefinitionFact}` index and
walks that definition's predicate; for `inline` it walks the usage's own. Resolution is where the two
absence cases route under default-deny before the walk: an index miss → block
`block_unresolved_definition`; a resolved-`None` predicate → block `block_missing_predicate` (MF2).
The resolved predicate is stored on the decision (D7) so no consumer re-resolves.

**The walk** is a recursive classify over `ExpressionIR`, threading the constraint identity +
location for diagnostics. Propositions recurse into propositions/comparisons; comparisons and
arithmetic nodes invoke the operand-fact gate. Block diagnostics accumulate (a predicate with both a
chain and an `xor` yields two) — the *outcome* is singular (`BLOCK`), the *diagnostics* plural.

## Required Invariants

- **I1. Total.** Every `ConstraintUsageFact` receives exactly one `eligibility` ∈ {admit, block,
  unassessed}. No fall-through: any construct/operand-category/form/node-role not on an admit list
  blocks with a named reason — including the two *absence* inputs that are not "a node with an
  unadmitted role": a resolved-`None` effective predicate (`block_missing_predicate`) and a
  definition-lookup miss (`block_unresolved_definition`), both routed at resolution before the walk.
  The profile decides over `facts.usages` only and reads `facts.definitions` **solely** as the
  predicate lookup index, so an unused `ConstraintDefinition` never becomes a `UsageDecision` — the
  concept's inventory rule holds by construction.
- **I2. Silent-on-clean, loud-on-gap.** A usage whose effective predicate uses only admitted
  constructs and passes every gate emits **zero** diagnostics; each blocked construct emits exactly
  one diagnostic naming construct + location + identity + reason.
- **I3. Reason-distinguishable.** The equality gate reproduces all 11 golden codes; the seven
  `block_*` reasons are distinct values, never collapsed to a bare "blocked."
- **I4. License-free.** `import agentic_mbse.sysml.executable_profile` pulls in no syside (structural
  test, D2/B1). The profile reads facts only — never the live model, never the evaluator.
- **I5. Same-IR (two arms).** The `ExpressionIR` on `UsageDecision.effective_predicate` is the exact
  object reachable from `facts` (not a copy). Under the single-parse precondition (D7) gate and
  compiler share that instance, verified by `gated_ir is compiled_ir` at the codegen seam; across a
  parse boundary the seam is verified by `serialize_expression` equality, since identity cannot hold.
  A second parse or a re-serialize between preflight and compile violates I5 either way.

## Component Overview

- **`sysml/executable_profile.py`** — the profile. Public surface:
  - `Eligibility` enum (`ADMIT`/`BLOCK`/`UNASSESSED`).
  - `EligibilityDiagnostic` — `reason: str`, `construct: str`, `location: LocationFact | None`,
    `constraint_identity: IdentityFact`, `message: str`.
  - `UsageDecision` — `identity`, `location`, `eligibility`, `diagnostics: list`,
    `unassessed_kind: str | None`, `effective_predicate: ExpressionIR | None`.
  - `ProfileResult` — `decisions: list[UsageDecision]` plus derived counts (admit/block/unassessed).
  - `evaluate_profile(facts) -> ProfileResult` — top-level.
  - `preflight(facts) -> PreflightResult` — codegen gate (`ok`, `blocking`, `admitted`, `unassessed`).
  - Matrix helpers (the test seam): `classify_equality(left, right) -> str`,
    `unit_compatibility(left, right) -> str` — return golden decision codes.
  - `REASON_CODES` — the 11 golden codes, the construct blocks (`block_assert_by_reference`,
    `block_feature_chain`, `block_invocation`, `block_xor`, `block_implies`, `block_unsupported_node`),
    and the default-deny codes (`block_unsupported_operator`, `block_unsupported_operand_category`,
    `block_non_predicate_root`, `block_missing_predicate`, `block_unresolved_definition`) — plus
    `PROFILE_SEMANTIC_VERSION`.
- **`validation/level4_constraints.py`** — delete the whole `check_constraint_coverage` function and
  its caller surface: the `unconstrained, coverage_metrics = ...` call and the `unconstrained` →
  warnings loop (`level4_constraints.py:131–138`). The existing constraint *counts*
  (`Total constraints`, `ConstraintUsage`, `ConstraintDefinition`, `level4_constraints.py:141–146`)
  **survive** — L4 tests assert them; the profile adds eligibility coverage (admit/block/unassessed)
  alongside them, not in place of them.
- **`validation/level6_architecture.py`** — `check_constraint_executability` body replaced by
  profile-driven per-construct WARNINGs. Preserve the function's loud-on-failure discipline
  (`level6_architecture.py:608–620` deliberately removed an `except: constraints = []` swallow): the
  replacement calls `extract_constraint_facts(model)` and must let an extraction failure surface, not
  collapse it to "no diagnostics."
- **`sysml/types.py`** — new `ValidationCode` entries for the eligibility diagnostics (WARNING).
- **`tests/`** — profile unit tests (golden-driven equality + inequality matrix), import-hygiene
  test, updated L4/L6 tests, updated golden fixture (`inequality_cases`).

## Non-Goals

- The predicate compiler, Kleene/margin semantics (Item 7).
- Catalog persistence, the two-level `ConstraintCatalog` (Items 5, 7).
- Concrete lowering, actual resolution against the output registry, ID minting (Item 5). The profile
  confirms an operand's recovered category; it does **not** resolve where an actual's value comes
  from (that is Item 5's strict resolver — a feature-chain *actual* does not trip the chain block).
- Resolving an exact-unit contract for a dimension-only quantity feature (this item blocks it).
- Rewriting a blocked predicate (the profile blocks and names the fix; the author rewrites).

## Implementation Notes

- **Equality gate precedence** (must match golden ordering): (1) either operand `unresolved` →
  `block_unresolved_operand`; (2) either `unknown` → `block_unsupported_operand_category`; (3) run
  `unit_compatibility` — if not `ok`, return its reason; (4) if any operand is `quantity` (units now
  proven compatible) or any is `real`, or an integer/real mix → `block_real_equality_requires_tolerance`;
  (5) both `enum` → same enumeration `support_enum_same_enumeration` else
  `block_incompatible_enumerations`; (6) both `boolean`→`support_boolean`, both `string`→
  `support_string`, both `integer`→`support_integer`.
- **`unit_compatibility(left, right)`** ordered guards: exactly one operand dimensioned quantity,
  other unitless numeric → `block_unitless_dimensioned`; both quantity with any `unit.unit is None`
  → `block_unknown_exact_unit`; both quantity, dimensions differ → `block_incompatible_dimensions`;
  both quantity, units differ (same dimension) → `block_unit_conversion_required`; else `ok`
  (both dimensionless, or both same exact unit). Integer/real/dimensionless mixes → `ok`.
- **Ordering comparison** = `unit_compatibility` only; `ok` → admit. So `integer <= real` admits and
  `1 [m] <= 100 [cm]` → `block_unit_conversion_required`.
- **`is_negated` vs `not`.** Usage-level `is_negated=true` is admitted polarity (no diagnostic); a
  `not` `OperatorNode` in the body is an admitted connective. Both pass.
- **Recovering an operand's type** at a comparison: read the operand node's `operand_type`
  (present on leaf/unit/arithmetic nodes; a proposition operand in value position → `block_non_predicate_root`).
- **L4/L6 severity is WARNING** (spec Decisions). WARNING→ERROR later is a one-field change on the
  same payload.

Interface sketch (≤10 lines, illustrative):

```python
def evaluate_profile(facts: ConstraintFacts) -> ProfileResult: ...

def classify_equality(left: OperandTypeFact, right: OperandTypeFact) -> str:
    """One of the 11 golden decision codes."""

@dataclass(frozen=True)
class UsageDecision:
    identity: IdentityFact
    eligibility: Eligibility
    diagnostics: list[EligibilityDiagnostic]
    unassessed_kind: str | None
    effective_predicate: ExpressionIR | None   # the exact IR the gate walked (D7)
```

## Potential Risks

- **Duplicate diagnostics across L4 and L6.** Mitigation: L4 reports *counts* only; L6 owns the
  per-construct diagnostics. Division of labor stated in Architecture.
- **Existing L6 tests assert the blanket warning.** Removing it changes their expectations.
  Mitigation: the plan updates the L6 tests; suite stays green because WARNING never fails a level,
  and admitted asserts (e.g. `observed <= limit`) now emit nothing.
- **`unknown` category has no golden row.** It is reachable (`constraint_extraction.py:332`).
  Mitigation: default-deny covers it (`block_unsupported_operand_category`) with a unit test, not a
  golden pin.
- **Cross-repo seam unverifiable from here.** sysml-codegen is a separate repo. Mitigation: specify
  the `preflight` contract precisely; the wiring commit there is mechanical (locate the pre-compile
  seam, insert the call, branch on `.ok`, lower `admitted[].effective_predicate`).
- **Duplicate extraction.** L4 and L6 each call `extract_constraint_facts(model)`, so one validation
  run extracts twice. Not a correctness issue (extraction is deterministic). Plan note: accept the
  small cost, or add a per-run fact cache if profiling warrants.

## Integration Strategy

- **Replaces:** the L4 0% attribute-coverage placeholder and the L6 blanket "dropped at extraction"
  warning. **Adds:** the codegen preflight seam.
- **sysml-codegen wiring (this item owns, separate small commit there):** build `ConstraintFacts`
  once, call `preflight(facts)`; if `not ok`, halt and emit `blocking[]` diagnostics; else feed
  `admitted[].effective_predicate` to the existing compiler. The same-IR assertion lives here, at the
  pre-compile seam (D7): `gated_ir is compiled_ir` on the in-process path,
  `serialize_expression(compiled_ir) == serialize_expression(gated_ir)` on the snapshot path. Pin the
  agentic-mbse package version (coordinated-pair discipline) and assert `PROFILE_SEMANTIC_VERSION`.

## Validation Approach

- **Golden matrix test** drives `classify_equality` over all 14 `equality_cases` and asserts the
  returned code equals `decision` — the S1 answer key becomes production truth.
- **Inequality test** drives `unit_compatibility`/ordering over the two new `inequality_cases`
  (`1 [m] <= 100 [cm]` → block; `integer <= real` → admit).
- **Form-gate test** over the golden's source-form fixtures: satisfy/require/plain → unassessed,
  named_usage_reference → block, inline/definition_typed asserts → walked. Confirms the
  `typed_feature_chain_and_literal` usage (feature-chain *actual*) is **admitted**.
- **Silent-on-clean / loud-on-gap test**: a clean model yields zero diagnostics; a model with a
  chain / xor / real-equality yields exactly the matching named diagnostics.
- **Absence-case tests (MF2)**: a `definition_typed` usage typed by a bodyless definition (predicate
  `None`) → `block_missing_predicate`; a `definition_typed` usage whose `constraint_definition` QN is
  absent from `facts.definitions` → `block_unresolved_definition`. Synthetic `ConstraintFacts`, no
  golden pin (matching how `unknown` is covered).
- **Import-hygiene test**: subprocess imports `executable_profile` and asserts `syside` not loaded.
- **L4/L6 tests**: coverage counts; per-construct WARNINGs; no blanket warning.
- Gate = default suite (`uv run pytest tests/`). Never run `pytest -m ""` or the corpus test.

## Next-Stage Handoff

- **Fixed:** the three-layer order and short-circuit; the 11 decision codes and their golden mapping;
  `unit_compatibility` precedence; module placement and public surface (D1, Component Overview); the
  two-arm same-IR seam via `UsageDecision.effective_predicate` (D7 — object identity under the
  single-parse precondition, serialization-equality across a parse boundary); the absence-case routing
  (`block_missing_predicate`, `block_unresolved_definition`) at resolution; the `preflight` contract;
  WARNING severity; D5 (`!=` blocks) / D6 default-deny calls.
- **Open:** exact `ValidationCode` spellings and message wording (constrained only by "construct +
  location + identity + reason"); L4's exact metric labels and whether unassessed is a separate line;
  the physical JSON shape of `inequality_cases` (a new key vs a sibling file).
- **De-risk first:** the cross-repo `preflight` wiring — a `/_my_spike` in sysml-codegen aimed at the
  right question (B2/MF1): not just "does the pre-compile seam exist," but "does one parsed
  `ConstraintFacts` reach both the gate and the compiler, or is there a second parse / re-serialize
  between them?" The answer decides which same-IR arm applies (object identity vs serialization
  equality) and where the assertion sits.

---
Next Step: After approval → `/_my_plan` (multi-file, two repos) then `/_my_implement`.
