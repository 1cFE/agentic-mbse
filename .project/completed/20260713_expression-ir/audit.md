# Audit: ExpressionIR — Production Tree, Extraction, Serialization (CONSTRAINT-EXEC Item 2)

**Verdict:** Certify (with notes)
**Audited:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** 204cf57 (audits `b05d41e..e352fd8`)

---

## Summary

Item 2 delivers what the spec, design, and epic asked for. The provisional single-dataclass
`ExpressionFact` (`predicate-tree/v0`) is replaced by a six-node distinct-dataclass algebra
(`expression-ir/v1`) with an allowlist dispatch that routes every unrecognized shape to an
explicit `UnsupportedNode` — the silent-coercion the concept's Principle 5 forbids is gone, and
I verified its removal by live mutation probe, not by reading the code. The unit_text fix, the
operator-spelling fidelity, the version discipline, and the eight-site migration all hold up
against live execution and an independent re-derivation of the golden diff. The suite is green
(1333 passed) and Ruff is clean on every file this item touched. Two minor notes below; neither
blocks certification.

## Findings

### Plan completion

All three phases verified complete.

- **Phase 1** (new `expression_ir.py`, offline round-trip, live de-risk): the module exists with
  the six node dataclasses, the union, the version constant, and the bare serialize/parse surface
  (`expression_ir.py:41-223`). The de-risk results recorded in the plan match what I observed live:
  `^` and `**` carry distinct operator strings; the `if ... ? ... else ...` construct routes to
  unsupported via the unrecognized-operator arm.
- **Phase 2** (atomic cutover + 8-site migration + golden regen): all eight sites migrated;
  `ExpressionFact`/`predicate-tree`/`PREDICATE_TREE_SCHEMA_VERSION` grep clean across `src/` and
  `tests/` (no hits). Golden regen independently verified (see Spec conformance).
- **Phase 3** (live coverage + gates): `test_expression_ir_extraction.py` exercises spelling
  distinctness, unary minus, the unsupported node, unit source+resolved fidelity, leaf-type
  instances, and round-trip within a load and across two independent loads. All pass.

### Spec conformance

Verified against the seven success criteria and the tagged requirements.

- **Five S2 predicate shapes + stress calc extract and round-trip byte-identically, across
  independent loads** — met. The five shapes are covered by the landed fixtures: inline
  owner-reference (`inline_owner_reference`), negated assertion (`negated_inline`), compound
  Boolean (`compound_boolean`, walked `or > and/not` at `test_constraint_fact_shapes.py:99-103`),
  the `<=` comparison (WI-014 shape, `below_limit`/`WithinLimit`), and the defaulted-formal IFE
  mechanic (`typed_omitted_default`). Stress calc: unary minus, `^`, and unit annotations
  (`operator_fidelity.sysml` + `type_units.sysml`). **"Across independent loads" is genuinely
  tested with two separate model loads, not one load serialized twice** —
  `test_round_trip_stable_across_independent_loads` (`test_expression_ir_extraction.py:115-118`)
  calls `_extract` (a fresh `try_load_model`) twice and byte-compares; and the golden self-compare
  (`test_constraint_fact_shapes.py:54-58`) byte-matches a fresh load against a stored serialization
  from a prior independent load, which covers the source_forms shapes across loads.
- **Source operator spellings survive distinctly** — met. `^` and `**` extract to different
  `operator` strings (`test_caret_and_power_stay_distinct`, verified live). Unary minus is a
  one-operand `-` operator node (`test_unary_minus_preserved_as_one_operand_operator`). The
  unit-annotation node keeps `unit_text="m"` alongside `operand_type.unit.unit="SI::metre"`.
  Normalization is membership-check-only (`_normalize_operator`, `constraint_extraction.py:376-381`):
  `str(operator)` already yields SysML symbol text, so an unmapped operator returns `None` and
  routes to unsupported — it never passes a raw enum name through (D4 satisfied).
- **Unsupported node is real, exercised, carries a structural diagnostic** — met, and verified by
  two live probes. (1) The `if` fixture yields `UnsupportedNode(node_kind="OperatorExpression",
  diagnostic="unrecognized operator 'if'", source_text=<present>)`. (2) **Mutation probe:** a
  fabricated object of an unrecognized metaclass routed through `_expression_ir` produced
  `UnsupportedNode(node_kind="FakeMeta", diagnostic="unknown node type: FakeMeta")` — never a
  generic operator node. The allowlist inversion is real: the dispatch's final arm is
  `return _unsupported_node(expression)` (`constraint_extraction.py:490`), with no silent
  catch-all remaining.
- **Canonical node types are dataclasses reusing Item 1's leaf vocabulary** — met.
  `test_leaf_facts_are_the_frozen_leaf_types` asserts the node fields are `LiteralFact`,
  `FeatureReferenceFact`, `OperandTypeFact`, `UnitFact` instances. No pydantic stand-ins.
- **Version pins: `expression-ir/v1` predicate, `constraint-facts/v1` envelope** — met.
  `EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"` (`expression_ir.py:38`), single discoverable
  module constant Item 8 can pin; `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"`
  unchanged (`constraint_facts.py:39`); `test_schema_versions_are_pinned` asserts both
  (`test_constraint_facts_serialize.py:174-175`). Item 1's byte-stability definition holds at the
  new pair — the within-load and across-load round-trip tests pass at
  `(constraint-facts/v1, expression-ir/v1)`.
- **Suite green, Ruff clean** — met. `uv run pytest tests/`: 1333 passed, 1 skipped, 33 deselected.
  `uv run ruff check` on the sysml source dir and all Item 2 test files: all checks passed. (The
  one repo-wide ruff error is a pre-existing import-order issue in `validation/adr002` tests,
  unrelated to this item and consistent with the plan's noted pre-existing errors.)

**Migration completeness (spec's Migration surface):** the eight sites are all migrated. `grep`
for `ExpressionFact | predicate-tree | PREDICATE_TREE_SCHEMA_VERSION | _expression_fact` across
`src/` and `tests/` returns **no hits**. The two `.kind` metaclass-name readers the design surfaced
now read `.reference.chain_segments` and `.literal.kind` (`test_constraint_fact_shapes.py:121,123`),
matching design step 8.

**Golden diff independently re-derived (not trusted from the plan note):**
- Phase 2 cutover (`81b2002~1 → 81b2002`): the non-predicate skeleton is **byte-identical** after
  stripping predicate subtrees — nothing outside the predicate trees moved. Every one of the 125
  `predicate-tree/v0` version strings retired; `expression-ir/v1` appears 113 times. The count drop
  of exactly 12 is the 12 unit-annotation `operands[1]` unit-reference subtrees collapsing into
  `unit_text` + resolved `UnitFact` — **the only subtree deletion**, matching the design checklist.
- unit_text fix (`48a61ee`): the diff is exactly 12 `unit_text` leaves, all changing a canonical
  name to a source spelling (`metre → m`, `centimetre → cm`, `kilogram → kg`). Nothing else changed.

**Non-goals respected:** no IR-to-Python compilation, no profile eligibility gating, no
`ExpressionAST` retirement, no leaf-vocabulary or envelope change. Invocation is a first-class node
kind (`InvocationNode`) but unexercised, as the honest-bounds requirement states.

### Design conformance

Implementation follows the design.

- **D1** (new module, `ExpressionFact` deleted, leaves stay, one-way imports): confirmed —
  `expression_ir.py` imports `expression_facts` only; `constraint_facts` imports `expression_ir`.
- **D2/D3** (six distinct dataclasses; unit annotation and invocation as distinct kinds): confirmed
  at `expression_ir.py:41-124`. Wrong-kind representation is a type error — `LiteralNode` has no
  `operator` slot, `UnsupportedNode` has no `operands`.
- **D4** (allowlist × operator-symbol set, inversion to unsupported): confirmed — dispatch order is
  FCE → OperatorExpression → FRE → literal → invocation → unsupported
  (`constraint_extraction.py:465-491`), FCE before OE as required.
- **D5** (one serialize/parse path, `_canonical_json` defined once): confirmed — `_canonical_json`
  lives in `expression_ir.py:127` and `constraint_facts` imports it; both bare and embedded
  serialization recurse the identical node encoding.
- **D7** (per-node `schema_version`): confirmed on every node dataclass.
- **Name-collision resolution** (the orchestrator's `Ir*` rename, `e352fd8`): clean. The six
  `expression_ir` nodes collide on bare names with `aggregation.py`'s unrelated node algebra;
  package-level re-exports use an `Ir*` prefix (`IrLiteralNode`, …) while bare names route to the
  aggregation nodes. Verified live: `IrLiteralNode is expression_ir.LiteralNode` and bare
  `LiteralNode is aggregation.LiteralNode`, both distinct — no silent shadowing.

### Code integrity

No significant issues. The `unit_text` fix is structural, not a string hack: `_unit_text`
(`constraint_extraction.py`) reads the unit referent's `short_name` slot (the symbol a `[m]`
annotation resolves through), falling back to `name` then `reconstruct_expression` only when
`short_name` is absent. This is the correct structural distinction between the source spelling and
the canonical name, and it satisfies the B1 fidelity bet.

**Notes (non-blocking):**

1. **`UnsupportedNode.source_text` is garbled for the `if` construct.** The live probe showed
   `source_text` for the ternary reconstructing as `"base > 0.0 if <FRE> if <FRE>"` — malformed
   because `reconstruct_expression` (Item 1 code, `expression.py:420`) does not cleanly render an
   if-expression. The field is non-null and the criterion is "source text **where available**"
   (best-effort), so this meets the spec, but a downstream consumer reading `source_text` for
   diagnostics should not expect faithful source for off-allowlist operator expressions. Fixing
   `reconstruct_expression` is out of scope for Item 2.

2. **Commit `48a61ee` message undercounts the golden change** ("the only diff is unit_text values
   on the four unit-annotation nodes"). The actual regen changed 12 `unit_text` leaves across
   several usages, not four. The code change is correct and confined to `unit_text`; only the
   message's count is off. No action needed.

---

## Certification

**Checked and verified:**
- Full default suite run live (1333 passed, 1 skipped); Item 2 test files run in isolation (40 passed).
- Ruff clean on all Item 2 source and test files.
- Allowlist inversion verified by two live mutation probes (`if` construct + fabricated metaclass) —
  both route to `UnsupportedNode`, never a generic operator.
- "Across independent loads" confirmed as two genuinely separate model loads.
- Both golden regens (Phase 2 cutover and the unit_text fix) independently re-derived leaf-by-leaf,
  confirming the design checklist (unit `operands[1]` subtree the only structural deletion; skeleton
  otherwise byte-identical).
- Migration grep clean; version pins asserted; the `Ir*`/aggregation collision resolution verified live.
- `unit_text` fix confirmed structural (`short_name`), matching the golden and B1.

**Not checked:**
- The corpus/integration tests (`test_corpus_integration.py`, `pytest -m ""`) — excluded by OWNER
  instruction; the default suite is the gate.
- Downstream consumption of these facts (Items 5/7/8 in sysml-codegen) — out of scope; not in this repo.
- True n-ary operator extraction and live invocation extraction — representable but unexercised by
  design (honest bounds); no success criterion requires them, and I did not attempt to produce one.
- The full byte-content of every predicate subtree in the golden was spot-checked structurally
  (skeleton + version + unit-deletion counts), not read node-by-node for all 24 usages.
