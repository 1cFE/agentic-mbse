# Spec: ExpressionIR — Production Tree, Extraction, Serialization

**Status:** Draft — spec-review incorporated (Approved-with-must-fixes; all 4 must-fixes + 3 nice-to-haves discharged 2026-07-12)
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
The probe's actual code and findings are **readable in-repo** at `.project/reference/s2-spike/`
(`s2_ir.py` — the `IRNode` node shapes, `_OPERATOR_ENUM_MAP`, `extract_ir` dispatch, compat
render; `findings.md` — the operator matrix, oracle envelope, and "Facts the design can now rely
on"). Design should work from the probe IR directly, not from Appendix B's summary. Item 2 is the
production build-out of that proven shape — not new research.

## Success Criteria

- [ ] All five S2 predicate shapes (the WI-014 `cost <= budget` predicate, the IFE viability
      predicate, an inline owner-reference predicate, a negated assertion, and a compound Boolean)
      and the S2 stress calc expressions (arithmetic with unary minus and `^`, unit annotations)
      extract to `ExpressionIR` trees.
- [ ] Every one of those trees JSON-round-trips **byte-identically** — both within a single load
      (`serialize(parse(serialize(t))) == serialize(t)`) and across independent live loads of the
      same fixture.
- [ ] **Source operator spellings survive distinctly in the tree.** A round-trip preserves and
      distinguishes `^` from `**`, unary minus, and the `[` unit-annotation — a fixture exercising
      both `^` and `**` extracts to trees that keep them different operator strings, and the
      unit-annotation node keeps its source unit spelling (`m`) alongside the resolved `UnitFact`
      QN (`SI::metre`). A spelling collapse is caught here, not two items downstream (Item 13's
      calc compat renders byte-identically and depends on the distinction — see the extraction
      requirement below).
- [ ] The unsupported node is real and exercised: a fixture containing a structurally
      unrepresentable expression extracts to a tree whose unsupported node carries a structural
      diagnostic — the node's metaclass kind, a diagnostic message, and the source text where
      available. Silence is never an outcome at the tree level — no expression node is dropped or
      coerced into a wrong-kind node.
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
  node's **metaclass kind**, a **diagnostic message** stating what could not be structured, and the
  **source text where available** (via `reconstruct_expression`, mirroring Item 1's
  `ExtractionDiagnosticFact.operand_source`; the S2 probe carried only `node_type` + `diagnostic`,
  so source text is a deliberate addition). So a limit can never vanish silently — this is the
  tree-level instance of the concept's Principle 5. Source: concept Principle 5 + `ExpressionIR`
  paragraph; epic Item 2 §1 and success criterion 2; `s2-spike/s2_ir.py:159`.
- **[HARD]** **The dispatch is an allowlist, and its inversion routes to the unsupported node.**
  Today's extractor coerces *anything* that is not a chain/reference/literal into a generic
  operator node built from `str(operator)` + operands — so a non-operator metaclass (a conditional,
  a `select`/`collect`), or an `OperatorExpression` whose operator does not normalize, becomes an
  operator node with `operator="None"` (`constraint_extraction.py:365-383`). Item 2 **inverts** this:
  a recognized metaclass with a normalizable operator routes to a productive node; **every other
  metaclass, and any absent or unrecognized operator, routes to the unsupported node.** This
  inversion — allow-known, catch-all-else-to-unsupported — is the mechanism that kills the silent
  coercion, and it is a fixed requirement, not a design choice. (Which specific metaclasses and
  operators are on the allowlist is the design-stage enumeration — see Open Questions.) Source: the
  landed catch-all above; concept Principle 5.
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
- **[INHERITED]** Extraction is **S2's `extract_ir` hardened** (`s2-spike/s2_ir.py:100`): it runs
  against live SysIDE expression nodes and includes **operator normalization** — but normalization
  is **enum→symbol only** (SysIDE's operator-enum name → its SysML symbol text, the probe's
  `_OPERATOR_ENUM_MAP` at `s2_ir.py:70`). It **preserves distinct source operator spellings**: `^`
  stays `^` and `**` stays `**` (the probe kept `Caret → "^"`, `Power → "**"` and collapsed them
  only at compile time), unary minus keeps its spelling, and the `[` unit-annotation node keeps its
  source unit text. Normalization must not collapse two source spellings into one — Item 13's
  byte-identical calc-compat rendering (a non-goal here, but a downstream dependent) can only
  recover `^` if the tree still holds it. Source: epic Item 2 §2; `s2-spike/s2_ir.py`,
  `findings.md` (operator matrix, "byte-identical calc compat").
- **[INHERITED]** Field shapes are **dataclasses reusing Item 1's leaf facts** — the S2 probe's
  pydantic fields were stand-ins; Item 1's leaves are dataclasses and Item 2 adopts that idiom.
  Source: epic Item 2 success criterion 3; S2 carry-forward.

### Serialization (scope §3)

- **[INHERITED]** Canonical, **byte-stable JSON round-trip**, within a load and across independent
  loads, exercised through a typed parse layer (not bare `json.loads`) so the round-trip tests the
  full reconstruction. Item 1's `_canonical_json` discipline (sort_keys, fixed separators,
  `allow_nan=False`, explicit nulls) is the established pattern to follow. Source: epic Item 2 §3;
  Item 1 `constraint_facts.serialize`.
- **[INHERITED: brief/epic]** The predicate sub-document is versioned **`expression-ir/v1`**. The
  brief and epic name the canonical tree `ExpressionIR`; the sub-document takes that name. The
  envelope version **stays `constraint-facts/v1`** — the two-level scheme Item 1's design D4/D9
  carved out for exactly this arrival: bump only the sub-version. Byte-stability is guaranteed **per
  version pair** (D9); cross-sub-version byte-compat (`predicate-tree/v0` vs `expression-ir/v1`) is
  an explicit non-goal — Item 2's tree bump is *allowed* to change bytes.
- **[AGENT — recorded override of a CERTIFIED artifact]** The sub-document **namespace** changes
  `predicate-tree → expression-ir` at this bump. Item 1's landed, certified design named the future
  bump `predicate-tree/v1` throughout (`constraint-facts/design.md` D4 `:159`, D9 `:167`/`:389`, C1
  `:411`/`:416`, `:507`). This is an orchestrator decision (agent-grade): the production tree *is*
  the `ExpressionIR`, so the concept's vocabulary names it, and the provisional `predicate-tree`
  namespace retires with the provisional tree. The **mechanism is unchanged** — bump only the
  sub-version, envelope stays `v1`, per-version-pair byte-stability (D9). Per capture-fidelity Law 4,
  this override is surfaced, not buried: Item 1's design forward-record has been amended in place
  with a one-line correction note so Item 8's recorded expectation is updated, not silently
  contradicted.
- **[INHERITED]** Item 8 (snapshot v3) will pin **both** versions when it embeds these facts —
  `constraint-facts/v1` + the then-current `expression-ir/vN`. Item 2 must keep the sub-version a
  single, discoverable module constant so Item 8 can pin it. Source: Item 1 design C1 "Action" + D9
  downstream note (amended for the namespace rename).

### Migration surface (the sub-version bump)

"agentic-mbse suite green" makes the following a defined worklist, not a scavenger hunt — the bump
from `predicate-tree/v0` to `expression-ir/v1` and the tree-shape change break each of these landed
sites, and the suite goes red until they migrate:

- **[HARD]** The production golden `tests/fixtures/constraint_fact_shapes/production_facts.json`
  bakes the v0 version strings and the full v0 tree shape. `test_production_golden_self_compares`
  (in `tests/test_sysml/test_constraint_fact_shapes.py`) regenerates production output and
  byte-compares it to this golden, so the golden **must be regenerated** and the diff reviewed under
  the byte-identity discipline (only the version string + tree-shape changes are expected).
- **[HARD]** `test_schema_versions_are_pinned` (`tests/test_sysml/test_constraint_facts_serialize.py:185`)
  asserts the predicate version `== "predicate-tree/v0"` — a direct hardcode of the retired name;
  it re-pins to `expression-ir/v1`.
- **[HARD]** The hand-built old-node trees in `tests/test_sysml/test_constraint_facts_serialize.py`
  (`_literal_expression`, `_reference_expression`, `_hand_built_facts`) construct the old
  `ExpressionFact` node type directly; they migrate to the new node types.
- **[HARD]** The constant `PREDICATE_TREE_SCHEMA_VERSION` (`expression_facts.py:25`) and its
  importers — `constraint_extraction.py` (emit sites), the `sysml/__init__.py` re-export, and the
  serialize test — carry the value. Design decides whether the constant is **renamed** (e.g.
  `EXPRESSION_IR_SCHEMA_VERSION`) alongside the value change; either way all importers update.

Source: brief probe #1 (name the migration surface); landed sites verified in this repo.

### Honest bounds

- **[INHERITED]** **n-ary operator capacity is latent.** The algebra admits n-ary operator nodes,
  but live SysIDE emits nested **binary** nodes for infix operators, so there is **no parity
  evidence for true n-ary nodes**. The spec states this bound honestly: n-ary is a representable
  shape with no live producer while the constructs that could emit it stay blocked. Source: concept
  Appendix B, S2 carry-forward (4).
- **[INHERITED]** **Invocation is representable but unexercised** — the same evidentiary status as
  n-ary. The algebra has an invocation node and the probe defined one, but S2 gathered **no live
  parity evidence** for it (`findings.md:78` — "Invocation, feature chains | blocked, cataloged |
  IR nodes exist; no live parity attempted"). Item 2 provides the node kind so the tree can
  represent an invocation faithfully; it does not claim a verified extraction of one, and no
  success criterion requires exercising it. Source: concept Appendix B S2; `s2-spike/findings.md`.
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
- **The allowlist contents (not the inversion).** The inversion itself is now a fixed requirement
  (allow-known, catch-all-else-to-unsupported; §Node algebra). What remains for design is the
  *enumeration*: exactly which SysIDE node metaclasses and which normalizable operators sit on the
  allowlist and route to a productive node. Deferred to design.
- **Standalone tree serialize/parse surface.** Whether Item 2 exposes an `expression_ir`-level
  `serialize`/`parse` for a bare tree (the round-trip test needs one) in addition to Item 1's
  embedded `_expression_from_dict`. Deferred to design.
- **Sourcing the S2 fixtures.** The probe IR and findings are readable in-repo
  (`.project/reference/s2-spike/`), but the concrete `.sysml` **fixture text** for the five shapes
  is not fully on hand: `findings.md:147-148` records that only the WI-014 (`cost <= budget`) and
  IFE viability (`eta * gain >= threshold`, defaulted formal) predicates are committed fixtures —
  in sysml-codegen — and the inline owner-reference, negated, and compound-Boolean predicates were
  **scratch-generated** by the spike and never committed. So the real question stands: do
  agentic-mbse's landed fixtures cover all five shapes, or must equivalents be authored here for
  the extraction/round-trip tests? Design/plan resolves it against the actual fixture corpus.
  Deferred to design/plan.

---

## Related Artifacts

- **Epic:** `.project/reference/epic_constraint_execution.md` (CONSTRAINT-EXEC, Item 2)
- **Required Reading:**
  - Concept `ExpressionIR` paragraph + Appendix B S2 result and carry-forwards:
    `.project/reference/constraint-execution-concept.md`
  - **S2 probe IR and findings, readable in-repo:** `.project/reference/s2-spike/s2_ir.py`
    (the `IRNode` node shapes, `_OPERATOR_ENUM_MAP`, `extract_ir` dispatch, compat render) and
    `.project/reference/s2-spike/findings.md` (operator matrix, oracle envelope, "Facts the design
    can now rely on"). Design works from these directly, not from Appendix B's summary. The only
    thing *not* here is the `.sysml` fixture text for the scratch-generated shapes (see Open
    Questions — Sourcing the S2 fixtures).
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
