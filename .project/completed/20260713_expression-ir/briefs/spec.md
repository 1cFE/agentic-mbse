# Brief: Item 2 spec — ExpressionIR: Production Tree, Extraction, Serialization

You are the spec stage for Item 2 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** — PDF-extraction subsystem, unrelated, spends API money. [OWNER instruction.] The gate is the default suite.
- Artifact: `spec.md` in `.project/active/expression-ir/`.

## Provenance of what you're given
- Concept (owner-ratified), readable in-repo: `.project/reference/constraint-execution-concept.md` — the `ExpressionIR` paragraph in "Neutral Constraint Facts" + Appendix B S2 result and carry-forwards.
- Epic Item 2: `.project/reference/epic_constraint_execution.md`.
- S2 findings + probe IR: `~/../..` is unreachable — the S2 spike artifacts live in **sysml-codegen**, but their substance is in the concept's Appendix B S2 blocks; the probe-grade IR (`s2_ir.py`) shape is described there. If you cannot read the sysml-codegen copies, say so and work from Appendix B + Item 1's landed code.
- **Item 1 is CERTIFIED on this branch** — its leaf vocabulary is the binding adoption target: `src/agentic_mbse/sysml/expression_facts.py` (leaf facts), `constraint_facts.py` (the `predicate-tree/v0` provisional sub-document + `PREDICATE_SCHEMA_VERSION` constant), `constraint_extraction.py`. Read the real code. Item 2's job includes replacing `predicate-tree/v0` with the canonical `expression-ir/v1` sub-document, bumping ONLY the sub-version (the envelope stays `constraint-facts/v1` — that carve-out was designed for exactly this arrival; see Item 1's design.md D9).

## Objective (from the epic)
Promote S2's probe-grade ExpressionIR to a production agentic-mbse-owned tree: the concept's node algebra, live extraction, byte-stable JSON.

## Scope (epic Item 2 §1–3)
1. **Node algebra**: literal, feature reference (source name, qualified target, chain segments — never pre-classified), unary/binary/n-ary operator, invocation, unit annotation, explicit unsupported node with structural diagnostic.
2. **Extraction** from live SysIDE expression nodes (S2's `extract_ir` hardened; operator normalization; FeatureChainExpression-before-OperatorExpression dispatch).
3. **Serialization**: canonical byte-stable JSON round-trip, within and across loads; versioned (`expression-ir/v1` as the predicate sub-document version).

## Out of scope
- Compiling IR to Python (Item 7 owns the Kleene predicate compiler; Item 13 the calc compat rendering); profile eligibility (Item 3); `ExpressionAST` retirement (Item 13).

## Success criteria (from the epic)
- All five S2 predicate shapes and the S2 stress calc expressions extract to trees that JSON-round-trip byte-identically across independent loads.
- The unsupported node carries a structural diagnostic (silence is never an outcome at tree level).
- Field shapes visibly adopt Item 1's fact vocabulary (S2 carry-forward: probe pydantic fields were stand-ins; Item 1's leaf facts are dataclasses — adopt that idiom).
- agentic-mbse suite green (default selection).

## Carry-forwards binding this item (concept Appendix B, S2)
- (4) n-ary capacity is latent (live SysIDE emits nested binary for infix) — no parity evidence for true n-ary; fine while the constructs that could produce them stay blocked, but the spec must state this bound honestly.
- The Kleene semantics live in the COMPILER (Item 7), not the tree — don't let evaluation semantics leak into the IR spec.
