# Spec: ExpressionIR — Production Tree, Extraction, Serialization

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC, Item 2

---

## Problem

Item 1 landed the neutral constraint facts, but it shipped the predicate itself as a
deliberately **provisional** tree. Look at `src/agentic_mbse/sysml/expression_facts.py`:
`ExpressionFact` is tagged `PREDICATE_TREE_SCHEMA_VERSION = "predicate-tree/v0"`, and Item 1's
design (D4/C1) states plainly that this tree is a stand-in Item 2 replaces. Two gaps make it a
stand-in, not the production representation:

1. **The node algebra is incomplete.** The concept names one canonical `ExpressionIR` with a
   fixed node algebra: literal, feature reference, unary/binary/n-ary operator, invocation, unit
   annotation, and — the one this project keeps getting bitten by — an **explicit unsupported
   node carrying a structural diagnostic**. Today's extractor (`constraint_extraction.py`,
   `_expression_fact`) has a catch-all: anything that is not a chain, reference, or literal
   becomes a generic operator node built from whatever attributes it finds. There is no
   invocation node, no distinct unit-annotation node, and no unsupported node. An expression
   shape the algebra cannot represent is silently coerced into a generic operator node rather
   than named. That is exactly the silent-disappearance failure the concept's Principle 5
   ("Silence Is Never an Outcome") exists to stop, reproduced at the tree level.

2. **The representation is provisional by contract.** The `predicate-tree/v0` version is a
   placeholder. Downstream (sysml-codegen Items 5/7, snapshot v3 in Item 8) needs the canonical,
   frozen tree to compile predicates and to seal packages. Until Item 2 promotes it, every
   consumer is reading a wire shape marked "will change."

S2 already proved the hard part: the probe-grade `ExpressionIR` serialized byte-stably and
compiled to Python matching live SysIDE on every supported point (concept Appendix B, S2 result).
Item 2 is the production build-out of that proven shape — not new research.

## Success Criteria

- [ ] All five S2 predicate shapes (the WI-014 `cost <= budget` predicate, the IFE viability
      predicate, an inline owner-reference predicate, a negated assertion, and a compound Boolean)
      and the S2 stress calc expressions (arithmetic with unary minus and `^`, unit annotations)
      extract to `ExpressionIR` trees.
- [ ] Every one of those trees JSON-round-trips **byte-identically** — both within a single load
      (`serialize(parse(serialize(t))) == serialize(t)`) and across independent live loads of the
      same fixture.
- [ ] The unsupported node is real and exercised: a fixture containing a structurally
      unrepresentable expression extracts to a tree whose unsupported node carries a structural
      diagnostic (the node's metaclass kind, source text where available, and a message). Silence
      is never an outcome at the tree level — no expression node is dropped or coerced into a
      wrong-kind node.
- [ ] The canonical node types are `@dataclass`es that reuse Item 1's leaf vocabulary
      (`FeatureReferenceFact`, `LiteralFact`, `OperandTypeFact`, `UnitFact` from
      `expression_facts.py`) — the leaf idiom is visibly adopted, not restated as new pydantic
      stand-ins.
- [ ] The predicate sub-document version is `expression-ir/v1`; the envelope stays
      `constraint-facts/v1`. `constraint_facts.py` predicate slots (usage/definition predicates,
      formal defaults, actual values, redefinition values) carry the canonical tree.
- [ ] agentic-mbse suite green (default selection); Ruff clean.

## Known Requirements

### Node algebra (scope §1)

- **[INHERITED]** The canonical `ExpressionIR` node algebra has exactly these productive node
  kinds plus one terminal: **literal**, **feature reference**, **unary/binary/n-ary operator**,
  **invocation**, **unit annotation**, and an **explicit unsupported node**. Source: concept
  "Neutral Constraint Facts" (`ExpressionIR` paragraph); epic Item 2 §1.
- **[INHERITED]** A feature reference keeps **source name, qualified target, and feature-chain
  segments, and does not pre-classify** the value as channel, parameter, or intermediate — that
  classification is codegen's job. This is already the shape of `FeatureReferenceFact`
  (`expression_facts.py:70`); Item 2 preserves it, not re-litigates it. Source: concept
  `ExpressionIR` paragraph; Item 1 `FeatureReferenceFact` docstring (`[HARD]` no-role-tag note).
- **[INHERITED]** The **unsupported node carries a structural diagnostic** — the unrepresentable
  node's metaclass kind and a message stating what could not be structured — so a limit can never
  vanish silently. This is the tree-level instance of the concept's Principle 5. Source: concept
  Principle 5 + `ExpressionIR` paragraph; epic Item 2 §1 and success criterion 2.
- **[INFERRED]** "Unsupported" here means **structurally un-extractable** — an expression node
  shape the algebra has no productive mapping for — **not** profile-ineligible. Invocation is a
  first-class node kind (the tree represents it faithfully) even though the executable profile
  (Item 3) later *blocks* invocation. The tree represents; the profile judges. Conflating the two
  would put profile logic in the wrong item. Source: inferred from the epic's Item 2/Item 3
  split (Item 2 out-of-scope explicitly excludes profile eligibility).

### Extraction (scope §2)

- **[HARD]** `FeatureChainExpression` must be dispatched **before** `OperatorExpression`, because
  FCE is a subtype of `OperatorExpression` in SysIDE — checking the operator branch first
  misclassifies a chain as an operator. This ordering already exists (`expression.py:428-430`,
  `constraint_extraction.py:358-361`) and is a correctness constraint Item 2 preserves.
- **[INHERITED]** Extraction is **S2's `extract_ir` hardened**: it runs against live SysIDE
  expression nodes and includes **operator normalization** (mapping SysIDE's operator
  representation to canonical operator strings). Source: epic Item 2 §2; concept Appendix B S2.
- **[INHERITED]** Field shapes are **dataclasses reusing Item 1's leaf facts** — the S2 probe's
  pydantic fields were stand-ins; Item 1's leaves are dataclasses and Item 2 adopts that idiom.
  Source: epic Item 2 success criterion 3; S2 carry-forward.

### Serialization (scope §3)

- **[INHERITED]** Canonical, **byte-stable JSON round-trip**, within a load and across independent
  loads, exercised through a typed parse layer (not bare `json.loads`) so the round-trip tests the
  full reconstruction. Item 1's `_canonical_json` discipline (sort_keys, fixed separators,
  `allow_nan=False`, explicit nulls) is the established pattern to follow. Source: epic Item 2 §3;
  Item 1 `constraint_facts.serialize`.
- **[INHERITED]** The predicate sub-document is versioned **`expression-ir/v1`**; the envelope
  version **stays `constraint-facts/v1`** (the two-level scheme Item 1's design D4/D9 carved out
  for exactly this arrival — bump only the sub-version). Byte-stability is guaranteed **per version
  pair**; cross-sub-version byte-compat (`predicate-tree/v0` vs `expression-ir/v1`) is an explicit
  non-goal — Item 2's tree bump is *allowed* to change bytes. Source: Item 1 design D4, D9, C1;
  brief.
- **[INHERITED]** Item 8 (snapshot v3) will pin **both** versions when it embeds these facts;
  Item 2 must keep the sub-version a single, discoverable module constant so Item 8 can pin it.
  Source: Item 1 design C1 "Action" + D9 downstream note.

### Honest bounds

- **[INHERITED]** **n-ary operator capacity is latent.** The algebra admits n-ary operator nodes,
  but live SysIDE emits nested **binary** nodes for infix operators, so there is **no parity
  evidence for true n-ary nodes**. The spec states this bound honestly: n-ary is a representable
  shape with no live producer while the constructs that could emit it stay blocked. Source: concept
  Appendix B, S2 carry-forward (4).
- **[INHERITED]** **Kleene / three-valued evaluation semantics do not live in the tree.** They
  belong to the compiler (Item 7). The IR is structural only; no evaluation semantics leak into it.
  Source: concept Principle 3 + Appendix B S2; brief.

## Non-Goals

- **Compiling IR to Python.** The Kleene predicate compiler is Item 7; the calc compat rendering
  is Item 13. Item 2 produces the tree, not executable code.
- **Profile eligibility.** Deciding which operators, equality categories, and unit relations may
  *run* is Item 3's executable profile. Item 2 represents `xor`, `implies`, invocation, real
  equality, and unit conversion faithfully as tree nodes; it does not gate them.
- **`ExpressionAST` retirement.** Migrating the calc-side expression compiler onto the shared tree
  and deleting `ExpressionAST` is Item 13 (staged, byte-identity-gated).
- **Any sysml-codegen consumption.** Downstream repos pin and read these facts; that wiring is
  their items (5, 7, 8).
- **Changing the leaf vocabulary or the envelope facts.** Item 1's `FeatureReferenceFact`,
  `LiteralFact`, `OperandTypeFact`, `UnitFact`, and the usage/owner/context envelope are frozen at
  `constraint-facts/v1`. A leaf *field* change would bump the envelope — out of scope here.

## Open Questions / Deferred to design

- **Module layout and the `ExpressionFact` → `ExpressionIR` transition.** Whether the canonical
  node type is a new `expression_ir.py` module, whether the leaf types relocate there (Item 1
  design C1 notes this is a mechanical, still-acyclic move), and whether `ExpressionFact` is
  renamed or replaced. Item 1's `constraint_facts.py` references `ExpressionFact` in several
  predicate slots; design must decide the concrete type those slots carry and keep the import
  direction acyclic (`constraint_facts` → IR → leaves, never back). Deferred to design.
- **Whether unit annotation and invocation become distinct node *kinds* or are distinguished by a
  field on the operator node.** Today unit annotation is an operator node with `operator="["` plus
  a `UnitFact` on `operand_type` (`constraint_extraction.py:237-256`). The concept lists unit
  annotation and invocation as first-class algebra members; design decides the concrete node
  representation. Deferred to design.
- **The exact trigger boundary for the unsupported node.** Which SysIDE node metaclasses and
  which operator/callee shapes route to the unsupported node versus a productive node — and
  whether the current silent generic-operator fallback for unrecognized operators is fully
  replaced. The *outcome* is fixed (no silent drop or coercion; §Node algebra above); the boundary
  is a design decision. Deferred to design.
- **Standalone tree serialize/parse surface.** Whether Item 2 exposes an `expression_ir`-level
  `serialize`/`parse` for a bare tree (the round-trip test needs one) in addition to Item 1's
  embedded `_expression_from_dict`. Deferred to design.
- **Sourcing the S2 fixtures.** The concrete S2 predicate/stress-expression fixture text lives in
  the sysml-codegen S2 spike artifacts, which are **not readable from this repo** (the brief
  confirms this). The five S2 predicate shapes overlap heavily with Item 1's landed fixture corpus
  (WI-014 `cost <= budget`, IFE viability, inline owner-ref, negated, compound). Design/plan
  should confirm whether the existing agentic-mbse fixtures cover the success criteria or whether
  equivalent fixtures must be reconstructed from Appendix B's descriptions. Deferred to design/plan.

---

## Related Artifacts

- **Epic:** `.project/reference/epic_constraint_execution.md` (CONSTRAINT-EXEC, Item 2)
- **Required Reading:**
  - Concept `ExpressionIR` paragraph + Appendix B S2 result and carry-forwards:
    `.project/reference/constraint-execution-concept.md`
  - S2 findings ("Facts the design can now rely on"): `spike-expression-tree-parity/findings.md`
    — **not readable from this repo** (lives in sysml-codegen); substance is in concept Appendix B.
- **Item 1 (dependency, CERTIFIED on this branch):**
  - `src/agentic_mbse/sysml/expression_facts.py` (leaf vocabulary + provisional tree)
  - `src/agentic_mbse/sysml/constraint_facts.py` (`constraint-facts/v1` envelope, predicate slots)
  - `src/agentic_mbse/sysml/constraint_extraction.py` (live extraction, `_expression_fact`)
  - `.project/active/constraint-facts/design.md` (D4, D9, C1 — the sub-version carve-out)
- **Design:** `.project/active/expression-ir/design.md` (to be created)

---

**Process note (orchestrated run):** the default pytest suite is the gate. Do **not** run
`pytest tests/ -m ""` or `test_corpus_integration.py` — the PDF-extraction corpus tests are
unrelated and spend API money [OWNER]. The orchestrator commits; this stage does not.

**Next Steps:** After approval, proceed to `/_my_design`.
