# Design: ExpressionIR — Production Tree, Extraction, Serialization

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Commit at design start:** `75fef8d`
**Epic:** CONSTRAINT-EXEC, Item 2

---

## Overview

Promote Item 1's provisional single-dataclass predicate tree (`ExpressionFact`, `predicate-tree/v0`)
to the production `ExpressionIR`: a tagged union of one dataclass per algebra kind, an allowlist
dispatch that routes every unrecognized shape to an explicit unsupported node, and a byte-stable
serialize/parse surface. The bump is `predicate-tree/v0 → expression-ir/v1`; the envelope stays
`constraint-facts/v1`.

## Related Artifacts

- **Spec (accepted, review-revised):** `.project/active/expression-ir/spec.md`
- **Spec review:** `.project/active/expression-ir/spec-review.md`
- **Epic:** `.project/reference/epic_constraint_execution.md` (Item 2)
- **Required Reading:**
  - Concept `ExpressionIR` paragraph + Appendix B S2: `.project/reference/constraint-execution-concept.md`
  - S2 probe IR + findings: `.project/reference/s2-spike/s2_ir.py`, `.project/reference/s2-spike/findings.md`
- **Item 1 (dependency, CERTIFIED):** `expression_facts.py`, `constraint_facts.py`,
  `constraint_extraction.py`, `.project/active/constraint-facts/design.md` (D4/D9/C1 + amended forward-record)
- **In-repo idiom:** `src/agentic_mbse/sysml/aggregation.py` (distinct-dataclass node algebra + union)

## Research Findings

- **The repo already ships this exact idiom.** `aggregation.py:88-165` is a node algebra of
  **distinct dataclasses** — `FeatureReferenceNode`, `LiteralNode`, `OperatorNode`, `InvocationNode`,
  `UnsupportedNode`, `NullNode` — joined by a `TypeAlias` union (`AggregationNode`, `:161`). Item 1's
  own design named this "a near-superset" of the concept's `ExpressionIR` algebra and cited it as the
  model. Item 2 finishes that lineage: the provisional `ExpressionFact` mega-dataclass becomes the
  distinct-node algebra aggregation.py already demonstrates.
- **Item 1 anticipated a separate `expression_ir.py`.** Its architecture diagram
  (`constraint-facts/design.md:199-211`) drew `(Item 2) expression_ir.py — adopts the leaf vocabulary`
  as a distinct module above `constraint_facts.py`. Following that is the lowest-surprise layout and
  honors the forward-record.
- **S2's `extract_ir` (`s2_ir.py:100-162`) is the proven dispatch**, in the exact order Item 1's
  extractor already uses (`constraint_extraction.py:358-383`): FeatureChainExpression → OperatorExpression
  → FeatureReferenceExpression → literals → invocation → fallback. Item 2 keeps the order and **inverts
  the fallback**: today's fallback builds a generic operator node; the new fallback is the unsupported node.
- **The landed fixtures already cover four of the five S2 predicate shapes** (verified in-repo):
  `source_forms.sysml` has the inline-owner-reference (`inline_owner_reference`), the negated assertion
  (`negated_inline`), the `<=` comparison (`inline_owner_reference`, `WithinLimit`), and the
  defaulted-formal mechanic (`typed_omitted_default`); `type_units.sysml:42-44` has the compound Boolean
  (`compound_boolean`) and unit annotations (`1 [m]`, `1 [kg]`, `100 [cm]`, `1 [m] + 1 [m]`). What is
  **absent everywhere**: `^`/`**` spelling distinctness, unary minus, and any structurally unsupported
  expression. Those three gaps drive one new fixture (see D6).
- **Migration surface is one site larger than the spec's list.** `grep` for the retiring symbols found
  `tests/test_sysml/test_constraint_extraction.py` imports the internal `_expression_fact` and asserts on
  node attributes — a site the spec's Migration-surface section did not name. Surfaced in D7 below.

## Core Concept

There is **one predicate tree**, and its shape is the algebra, not a bag of nullable fields. Item 1
shipped the tree as a single `ExpressionFact` dataclass with a `kind` string and every other field
nullable (`operator`, `operands`, `reference`, `literal`, `operand_type`) — so nothing structural
stopped a literal node from carrying an operator, and the extractor's catch-all coerced any unknown
shape into an operator node with `operator="None"`. That is the exact silent-coercion the concept's
Principle 5 forbids, reproduced at the tree level. Item 2 replaces the mega-dataclass with **one
dataclass per algebra kind** — literal, feature reference, operator, unit annotation, invocation, and
an explicit unsupported node — joined by a `kind`-tagged union. Wrong-kind representation stops being a
convention and becomes a type error: a `LiteralNode` has no `operator` field to set. Dispatch becomes an
**allowlist**: a recognized metaclass with a normalizable operator produces a productive node; every
other metaclass, and any absent or unrecognized operator, produces the unsupported node carrying a
structural diagnostic. The nodes reuse Item 1's frozen leaf facts (`FeatureReferenceFact`, `LiteralFact`,
`OperandTypeFact`, `UnitFact`) unchanged, so this is a re-typing of the tree, not a change to what a
leaf is. Serialization stays Item 1's canonical-JSON discipline; because each node now serializes only
its own fields, the wire shape changes — which is exactly the `predicate-tree/v0 → expression-ir/v1`
bump the two-level version scheme (Item 1 D4/D9) was carved out to allow.

This composes with existing pieces: the leaf facts and `IdentityFact` stay in `expression_facts.py`
(frozen at the `constraint-facts/v1` envelope); the syside-touching extractor stays the only place that
imports syside; the canonical-JSON discipline (`sort_keys`, fixed separators, `allow_nan=False`, explicit
nulls) is reused, defined once, for both the bare tree and the embedded predicate.

## Key Bets

- **B1.** Every field S2's proven compat rendering read survives the re-typing, so Item 13 can still
  reproduce today's calc output byte-identically from the tree. Those fields are: the operator **spelling**
  (`^` distinct from `**`, unary minus as a one-operand `-`), `operands`, the literal `value`/`result_type`,
  the feature reference `source_name`/`chain_segments`, the unit annotation's `unit_text`, and the
  invocation `function_qn`/`arguments`. *If false → Item 13's byte-identity gate cannot be met and the
  calc cutover has no faithful source, defeating the one-tree decision S2 made.*
- **B2.** Keeping the read-side attribute names stable across the transition (`operator`, `operands`,
  `operand_type`, `kind`, `reference`, `literal`) means most existing tree-walking assertions survive
  unchanged; only construction sites and the version string must migrate. *If false → the migration
  surface is far larger than the four-plus-one sites enumerated, and every consumer that walks the tree
  breaks.*
- **B3.** A distinct `kind` discriminant on each node is sufficient for a total parse: `parse` switches on
  `kind` and reconstructs exactly one node type, recursing on child slots. *If false → parse cannot
  round-trip a serialized tree without out-of-band type information, and the byte-stable round-trip
  criterion fails.*

## Key Decisions

- **D1. New `expression_ir.py` module; delete `ExpressionFact` from `expression_facts.py`; leaves stay.**
  The tree nodes, the `ExpressionIR` union, the `EXPRESSION_IR_SCHEMA_VERSION` constant, and the bare-tree
  `serialize_expression`/`parse_expression` live in a new module that imports the leaves from
  `expression_facts.py`. `ExpressionFact` is deleted, leaving **one tree**. Import direction stays one-way:
  `constraint_facts → expression_ir → expression_facts`. *Rejected: evolve `ExpressionFact` in place
  (muddies the module documented as "the frozen leaf vocabulary" with the version-bumping tree, and
  contradicts Item 1's own anticipated `expression_ir.py` layout). Rejected: relocate the leaf types into
  `expression_ir.py` (a larger, unnecessary diff — Item 1 C1 marked it optional/mechanical; not needed for
  acyclicity).*
- **D2. Distinct dataclass per algebra kind, joined by a `kind`-tagged union** — the aggregation.py idiom.
  Six nodes: `LiteralNode`, `FeatureReferenceNode`, `OperatorNode`, `UnitAnnotationNode`, `InvocationNode`,
  `UnsupportedNode`. *Rejected: keep the single `ExpressionFact` mega-dataclass with nullable fields
  (S2's/Item 1's provisional shape — it makes wrong-kind coercion a convention, not a type error, and is
  the shape the spec's inversion exists to retire).*
- **D3. Unit annotation and invocation are distinct node kinds, not fields on the operator node.**
  `UnitAnnotationNode` carries the annotated `value` subtree, the source `unit_text` (`"m"`), and the
  resolved `UnitFact` (via `operand_type`, `SI::metre`) — the spelling-fidelity criterion needs both the
  source text and the resolved QN as first-class slots. `InvocationNode` carries `function_qn` +
  `arguments` — no operator symbol, a resolved function QN instead. Both match the concept algebra 1:1 and
  aggregation.py's existing `InvocationNode`. *Rejected: operator node with `operator="["` plus a `UnitFact`
  hung on `operand_type` (Item 1's provisional coding, `constraint_extraction.py:237-256`) — overloads
  `operands[1]` as the unit ref and gives the resolved unit no clean home distinct from the source text.*
- **D4. Allowlist = a fixed metaclass set × a fixed operator-symbol set; inversion → unsupported.** See
  [Allowlist](#allowlist-d4) for the exact contents. Normalization is enum-name→symbol only and **signals
  "unrecognized"** rather than passing an unmapped enum name through (S2's `_operator_text` passed it
  through; Item 2 must not). *Rejected: S2's permissive fallthrough (`s2_ir.py:96`, returns the raw enum
  name) — it re-creates the silent generic-operator node the inversion is required to kill.*
- **D5. One serialization path, exposed bare and embedded.** `serialize_expression(ir)` is
  `_canonical_json(dataclasses.asdict(ir))`; `constraint_facts.serialize(facts)` is the same call over the
  aggregate and recurses through the identical nodes — byte-identical node encoding in both. `parse` is one
  `_expression_ir_from_dict(dict)` dispatcher on `kind`, used by both the bare `parse_expression` and
  `constraint_facts.parse`'s predicate slots. `_canonical_json` is defined once (in `expression_ir.py`, the
  lower module) and imported by `constraint_facts`. *Rejected: a second serialize/parse for the bare tree
  (two encoders drift; the "silent third representation" risk in miniature).*
- **D6. One new fixture for the three uncovered cases; reuse the landed fixtures for the rest.** The
  landed `source_forms.sysml`/`type_units.sysml` already exercise four predicate shapes + unit annotations
  + defaulted formals; the migrated tests re-extract them through the new tree. A new small fixture
  `tests/fixtures/expression_ir/operator_fidelity.sysml` adds exactly the gaps: `^` **and** `**` in one
  model, unary minus, and one structurally unsupported expression. *Rejected: author all five S2 shapes
  fresh (duplicates fixtures that already extract and round-trip; larger surface for no coverage gain).
  Rejected: skip the unsupported fixture (a HARD success criterion requires an exercised unsupported node).*
- **D7. Per-node version string retained, renamed to `EXPRESSION_IR_SCHEMA_VERSION`.** Each node carries a
  `schema_version` slot defaulting to the module constant `"expression-ir/v1"`. The spec's expected golden
  diff ("only the version string + tree-shape changes") assumes the version string still appears in the
  bytes; keeping it per-node is the lowest-surprise migration and Item 8 still pins the single module
  constant. *Rejected: version only at the envelope/root (union types give no clean root-vs-child boundary
  for a recursive `asdict`, and it enlarges the golden diff beyond the spec's stated expectation). Tunable
  at plan stage — see Handoff.*

## Architecture

Modules in `src/agentic_mbse/sysml/`, layered so imports point one way:

```
expression_facts.py   leaf vocabulary ONLY (ExpressionFact deleted) — no syside, no deps
        ▲
expression_ir.py      node dataclasses + ExpressionIR union + EXPRESSION_IR_SCHEMA_VERSION
        ▲             + serialize_expression/parse_expression + _canonical_json (shared)
        │
constraint_facts.py   predicate slots carry ExpressionIR; serialize/parse reuse expression_ir
        ▲
constraint_extraction.py   the only syside-touching module; builds ExpressionIR nodes
```

**Data flow (extraction).** `constraint_extraction._expression_ir(node, ctx)` (renamed from
`_expression_fact`) dispatches a live syside expression node in the fixed order (D4), builds one node
dataclass, and recurses on child expressions. `operand_type` is attached to value-producing nodes exactly
as Item 1 does today (`_operand_type_fact`) — arithmetic/leaf nodes carry it; comparison/connective operator
nodes carry `operand_type=None` (a proposition, not a value).

**Data flow (serialize).** `constraint_facts.serialize` → `_canonical_json(dataclasses.asdict(facts))`
recurses into the predicate slots' `ExpressionIR` nodes; `serialize_expression(ir)` does the same over a
bare node. **Parse** routes both through `_expression_ir_from_dict`, which reads `kind` and constructs the
matching node.

## Node algebra (schema sketch, representative)

```python
@dataclass
class LiteralNode:          kind="literal";     literal: LiteralFact;  operand_type: OperandTypeFact
@dataclass
class FeatureReferenceNode: kind="feature_ref"; reference: FeatureReferenceFact; operand_type: OperandTypeFact
@dataclass
class OperatorNode:         kind="operator";    operator: str;  operands: list[ExpressionIR]
                            operand_type: OperandTypeFact | None       # None for comparison/connective
@dataclass
class UnitAnnotationNode:   kind="unit";        value: ExpressionIR;  unit_text: str | None
                            operand_type: OperandTypeFact              # resolved UnitFact lives here
@dataclass
class InvocationNode:       kind="invocation";  function_qn: list[str] | None; arguments: list[ExpressionIR]
                            operand_type: OperandTypeFact | None
@dataclass
class UnsupportedNode:      kind="unsupported"; node_kind: str;  diagnostic: str;  source_text: str | None

ExpressionIR = LiteralNode | FeatureReferenceNode | OperatorNode | UnitAnnotationNode | InvocationNode | UnsupportedNode
```

Every node carries `schema_version: str = EXPRESSION_IR_SCHEMA_VERSION` (D7; omitted above for brevity).
The metaclass detail Item 1 preserved stays in the leaves: `LiteralFact.kind` (`"LiteralRational"` vs
`"LiteralInteger"`), `FeatureReferenceFact.chain_segments` (chain vs plain). `UnsupportedNode.node_kind`
is the **unrepresentable** node's metaclass; `source_text` comes from `reconstruct_expression`
(`expression.py:420`) and is a deliberate addition over the S2 probe, which carried only `node_type` +
`diagnostic`.

### Allowlist (D4)

**Recognized metaclasses** (dispatch order fixed; FeatureChainExpression **before** OperatorExpression —
`[HARD]`, FCE subtypes OE):

1. `FeatureChainExpression` → `FeatureReferenceNode` (chain segments set).
2. `OperatorExpression` → `OperatorNode`, **or** `UnitAnnotationNode` when the operator normalizes to `[`.
   Requires the operator to be in the operator-symbol set below; **absent or unrecognized operator →
   `UnsupportedNode`.**
3. `FeatureReferenceExpression` → `FeatureReferenceNode` (plain).
4. `LiteralRational` / `LiteralInteger` / `LiteralBoolean` / `LiteralString` → `LiteralNode`
   (via Item 1's `is_literal_node`).
5. Invocation-shaped node (`function` with a `name`, per S2 `s2_ir.py:150`) → `InvocationNode`.
6. **Everything else → `UnsupportedNode`.**

**Operator-symbol set** (the normalization target; from `_OPERATOR_ENUM_MAP`, `s2_ir.py:70`, spellings
preserved distinctly): `< <= > >= == != and or not xor implies + - * / ** ^ [`. `[` routes to
`UnitAnnotationNode`, not `OperatorNode`. `**` and `^` stay separate symbols; normalization never collapses
two source spellings into one (Item 13 recovers `^` only if the tree still holds it).

## Required Invariants

- **Serialize → parse → serialize is byte-identical** for any bare tree and any embedded predicate, at the
  pinned pair `(constraint-facts/v1, expression-ir/v1)`; and across independent live loads of the same
  fixture. Cross-sub-version byte-compat (`predicate-tree/v0` vs `expression-ir/v1`) is an explicit non-goal.
- **No expression node is dropped or coerced.** Every syside expression node maps to exactly one algebra
  node; the unrepresentable ones map to `UnsupportedNode` with metaclass + message + source text (where
  available), never to a wrong-kind node. Silence is never an outcome (Principle 5).
- **Source operator spellings survive distinctly** — `^` ≠ `**`, unary minus preserved, `[` unit annotation
  keeps its `unit_text` alongside the resolved `UnitFact` QN.
- **Wrong-kind representation is a type error** — a `LiteralNode` has no `operator` slot; an
  `UnsupportedNode` has no operands.
- **Leaf vocabulary unchanged.** Nodes reuse `FeatureReferenceFact`/`LiteralFact`/`OperandTypeFact`/`UnitFact`
  as-is; a leaf field change would bump the `constraint-facts/v1` envelope and is out of scope.
- **Import direction stays one-way:** `constraint_facts → expression_ir → expression_facts`; no back-edge.
- **`EXPRESSION_IR_SCHEMA_VERSION` is a single, discoverable module constant** Item 8 can pin.

## Component Overview

- **`expression_ir.py` (new)** — the six node dataclasses, the `ExpressionIR` union,
  `EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"`, `serialize_expression`/`parse_expression`, the
  `_expression_ir_from_dict` dispatcher, the moved leaf/identity parse helpers, and the shared
  `_canonical_json`. Imports `expression_facts` only.
- **`expression_facts.py` (edit)** — delete `ExpressionFact` and `PREDICATE_TREE_SCHEMA_VERSION`; keep the
  leaves + `IdentityFact`. Update `__all__`.
- **`constraint_facts.py` (edit)** — predicate slots (`FormalFact.default`, `ActualFact.value`,
  `ConstraintDefinitionFact.predicate`, `ConstraintUsageFact.predicate`, `RedefinitionFact.value`) type as
  `ExpressionIR`; `serialize`/`parse` delegate tree handling to `expression_ir`.
- **`constraint_extraction.py` (edit)** — `_expression_fact` → `_expression_ir`, building node dataclasses
  with the inverted allowlist dispatch; the reference/literal builders return `FeatureReferenceNode`/
  `LiteralNode`; the operator branch splits into operator / unit-annotation / unsupported.
- **`sysml/__init__.py` (edit)** — re-export the node types + union + `EXPRESSION_IR_SCHEMA_VERSION` +
  `serialize_expression`/`parse_expression`; drop `ExpressionFact` + `PREDICATE_TREE_SCHEMA_VERSION`.
- **New fixture** `tests/fixtures/expression_ir/operator_fidelity.sysml` (D6).

## Non-Goals

- Compiling IR to Python (Item 7 Kleene compiler; Item 13 calc compat). Item 2 produces the tree only.
- Profile eligibility (Item 3). Invocation is a first-class node even though the profile later blocks it.
- `ExpressionAST` retirement (Item 13, byte-identity-gated).
- Any sysml-codegen consumption (Items 5/7/8).
- Changing the leaf vocabulary or the `constraint-facts/v1` envelope facts.
- Exercising true n-ary operator nodes or a verified invocation extraction — both are representable but
  have **no live producer** (findings §honest bounds); no success criterion requires them.

## Implementation Notes

- **Preserve read-side attribute names** (`operator`, `operands`, `operand_type`, `kind`, `reference`,
  `literal`) so existing tree-walking assertions survive (B2). This is why `test_constraint_extraction.py`'s
  compound/operand-type assertions (`:58-62`, `:136-139`) need no change — only its direct
  `_expression_fact` import + `MockLiteralRational` test (`:192-203`) migrates to the renamed function and
  new return type.
- **`kind` discriminant mechanism** — a `kind: str` field with a fixed per-class default is the simplest;
  the plan may instead have the serializer inject `kind` by `isinstance`. Either is fine as long as the
  serialized bytes carry `kind` and parse dispatches on it.
- **Unsupported fixture candidate** — a `ConditionalExpression` (`if c ? a : b`) is a clean off-allowlist
  metaclass; fall back to a `select`/`collect` expression if SysIDE 0.8.4 parses it differently. Plan/impl
  confirms the parse and the emitted metaclass name.
- **Normalization must signal "unrecognized"** (D4) — refactor `_operator_text` so an unmapped enum returns
  a sentinel that routes to `UnsupportedNode`, not the raw enum name.
- **`_canonical_json` relocation** — moving it to `expression_ir.py` keeps ONE definition; verify
  `constraint_facts.serialize` still imports and uses it (byte output must not change except for the tree
  shape + version string).

## Potential Risks

- **The golden diff hides an unintended change.** The regenerated `production_facts.json` will differ in
  every predicate node (new shape) + version string. *Mitigation:* review the diff node-by-node against the
  expected shape; the self-compare test (`test_production_golden_self_compares`) then pins it. Confirm no
  non-predicate field moved.
- **`operand_type` placement regressions Item 3's reads.** Item 1 attached `operand_type` to value nodes
  for Item 3's gate; a distinct-node rewrite could drop it on some node type. *Mitigation:* the migrated
  `test_constraint_extraction.py` operand-type assertions (`:58-69`) and `test_operand_facts_match_s1_type_unit_oracle`
  cover it; keep `operand_type` on literal/reference/unit/arithmetic-operator nodes.
- **An unmapped-but-common operator lands in unsupported.** If the operator set omits a spelling SysIDE
  actually emits for a supported construct, a real predicate silently becomes unsupported. *Mitigation:* the
  operator set is the S2-proven `_OPERATOR_ENUM_MAP`; the fixtures exercise the full comparison/arithmetic/
  connective range, and any miss shows as an unexpected `UnsupportedNode` in the golden.

## Integration Strategy

- Add `expression_ir.py`; edit the four landed src modules + `__init__.py` in one change (the type of the
  predicate slots changes, so a partial migration leaves the suite red).
- The migration is the spec's enumerated surface **plus `test_constraint_extraction.py`** (surfaced D7):
  1. `expression_facts.py:25` — delete constant + `ExpressionFact`.
  2. `constraint_extraction.py` — rename/rebuild `_expression_ir`; import nodes + version from `expression_ir`.
  3. `constraint_facts.py` — retype predicate slots; delegate tree parse to `expression_ir`.
  4. `sysml/__init__.py` — swap the re-exports.
  5. `test_constraint_facts_serialize.py` — migrate `_literal_expression`/`_reference_expression`/
     `_hand_built_facts` to new nodes; re-pin `test_schema_versions_are_pinned` to `"expression-ir/v1"`.
  6. `test_constraint_extraction.py` — migrate the `_expression_fact` import + `MockLiteralRational` test.
  7. `production_facts.json` — regenerate; review the diff.

## Validation Approach

- **Five predicate shapes + operator fidelity extract and round-trip byte-identically**, within a load and
  across independent loads — over the reused landed fixtures + the new `operator_fidelity.sysml`.
- **Spelling distinctness:** a fixture with both `^` and `**` extracts to nodes with different `operator`
  strings; the unit-annotation node keeps `unit_text="m"` alongside `operand_type.unit.unit="SI::metre"`.
- **Unsupported node exercised:** the unsupported fixture extracts to an `UnsupportedNode` carrying
  metaclass + message + source text; no sibling node is dropped or mis-kinded.
- **Leaf reuse visible:** node fields are `FeatureReferenceFact`/`LiteralFact`/`OperandTypeFact`/`UnitFact`
  instances, not new stand-ins.
- **Version pinned:** `EXPRESSION_IR_SCHEMA_VERSION == "expression-ir/v1"`; envelope stays
  `constraint-facts/v1`; the pinned-versions test asserts both.
- **Gate:** default pytest suite green + Ruff clean. Do **not** run `pytest tests/ -m ""` or
  `test_corpus_integration.py` [OWNER].

## Next-Stage Handoff

- **Fixed:** new `expression_ir.py` with the six-node distinct-dataclass union (D1/D2); unit annotation +
  invocation as distinct kinds (D3); the allowlist contents and the inversion-to-unsupported (D4); one
  shared serialize/parse path exposed bare + embedded (D5); one new fixture for the three uncovered cases
  (D6); the full seven-site migration including the surfaced `test_constraint_extraction.py`.
- **Open (plan decides):** the `kind` discriminant mechanism (default field vs serializer injection); the
  exact unsupported construct (`ConditionalExpression` vs `select`/`collect`), pending a parse check; the
  per-node-vs-root version placement (D7 — retained per-node, but tunable if the golden review argues
  otherwise).
- **De-risk first:** author `operator_fidelity.sysml` and confirm live SysIDE emits (a) distinct enum values
  for `^` vs `**`, and (b) a non-allowlist metaclass for the chosen unsupported construct. Both are cheap
  live checks; the whole design's fidelity + unsupported criteria rest on them. If `^`/`**` collapse or the
  unsupported construct parses as an allowlisted operator, revisit the fixture before building the nodes.

---

**Next Step:** After approval → `/_my_plan`.
