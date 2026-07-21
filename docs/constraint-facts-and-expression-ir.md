# ConstraintFacts & ExpressionIR

Two production schemas agentic-mbse owns and downstream repos (sysml-codegen) read as
ground truth. Both were built in the constraint-execution epic to make modeled assertions
*executable*: `ConstraintFacts` is the neutral record of what constraints a model declares;
`ExpressionIR` is the predicate tree those constraints (and calc expressions) compile from.

This page is the durable mental model — it stands on its own so it survives the archival of
the `.project/` design artifacts it points to at the end. It is a summary, not the full
mechanism.

## ConstraintFacts — the neutral constraint record (Item 1)

`agentic_mbse.sysml.constraint_facts` (schema tag `constraint-facts/v1`).

**What it is.** A frozen, tool-neutral snapshot of every constraint a loaded SysIDE model
declares — definitions, usages, their formals and resolved actuals, owners, and extraction
diagnostics — with a canonical JSON serialization. It carries *facts*, not decisions: it does
not classify a constraint as executable or drop it, it records what is there.

**Why it exists.** Constraint execution spans two repos. agentic-mbse extracts and classifies;
sysml-codegen lowers and generates. A neutral, serialized fact schema is the seam between them:
the extractor emits `ConstraintFacts` once, and every downstream consumer (the executable
profile, the lowering pass, the snapshot format's `constraint_facts` section) reads the same
ground truth instead of re-walking the SysIDE AST. It promotes the S1 spike's test-only fact
shapes into the production schema.

**Key types** (`sysml/constraint_facts.py`):

- `ConstraintFacts` — the aggregate: definitions, usages, context, diagnostics.
- `ConstraintDefinitionFact` / `ConstraintUsageFact` — a reusable `constraint def` and one
  concrete usage of it.
- `FormalFact` / `ActualFact` — a definition's declared formal and a usage's resolved actual.
- `ConstraintSource`, `ContextFact`, `RedefinitionFact`, `ExtractionDiagnosticFact`,
  `LocationFact`, `OwnerFact`, `IdentityFact` — provenance, redefinition, and diagnostic leaves.

**Extraction.** `extract_constraint_facts(model)` (`sysml/constraint_extraction.py`) sweeps,
classifies, and recovers the facts from a loaded model, accumulating extraction diagnostics.

## ExpressionIR — the production predicate tree (Item 2)

`agentic_mbse.sysml.expression_ir` (schema tag `expression-ir/v1`).

**What it is.** A `kind`-tagged union of one dataclass per algebra kind — `LiteralNode`,
`FeatureReferenceNode`, `OperatorNode`, `UnitAnnotationNode`, `InvocationNode`, and an explicit
`UnsupportedNode` — with serialize / parse / canonical-JSON support. It reuses Item 1's frozen
leaf facts (`FeatureReferenceFact`, `LiteralFact`, `OperandTypeFact`, `UnitFact`) unchanged.

**Why it exists.** It is the single expression representation both a constraint predicate and a
calc-def output compile from. References are carried **unclassified** (a `FeatureReferenceNode`
holds a `source_name`, not an input/intermediate tag) — classifying a reference is caller
policy applied at render time, so the same tree serves sysml-codegen's calc renderer
(`extraction/calc_compat_renderer.py`) and its Kleene predicate compiler
(`generation/predicate_compiler.py`). This replaced sysml-codegen's retired private
`ExpressionAST` syntax tree.

**Extraction.** `extract_expression_ir(ast_node)` (`sysml/constraint_extraction.py`) converts a
raw SysIDE AST node into an `ExpressionIR` tree; `serialize_expression` / `parse_expression`
round-trip it through canonical JSON.

## Deeper design artifacts

For full mechanism depth (spike findings, schema-shape decisions, the extraction diagnostics
taxonomy), see the archived `.project/` artifacts — `20260713_constraint-facts` (Item 1) and
the CONSTRAINT-EXEC epic record. Those are design-history; the schemas above are the ground
truth if the two ever disagree.

## Related

- `docs/patterns/constraints.md` — the modeler-facing constraint syntax and the
  ADMIT / BLOCK / unassessed profile outcomes.
- `docs/subtype-enumeration-decision-table.md` — where the constraint sweep is subtype-aware.
