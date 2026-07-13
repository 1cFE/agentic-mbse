# Brief: Item 2 design — ExpressionIR

You are the design stage for Item 2 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `design.md` in `.project/active/expression-ir/`.

## Input
- Spec (committed, review-revised): `.project/active/expression-ir/spec.md` — node algebra, unsupported-node inversion [HARD], operator-spelling fidelity, migration surface, expression-ir/v1 naming (recorded override) are fixed. Open Questions are yours to decide and record.
- S2 probe IR in-repo: `.project/reference/s2-spike/s2_ir.py` (the proven extraction shapes) + `findings.md`.
- Item 1 landed code (the base you're evolving): `expression_facts.py`, `constraint_facts.py`, `constraint_extraction.py` + Item 1's design (note its amended forward-record).

## Design guidance (orchestrator, agent-grade)
- Decide and record: the ExpressionFact→ExpressionIR transition (evolve the landed dataclasses in place vs new module with the old one deleted — prefer whichever leaves ONE tree, no silent third representation), node-kind representation (distinct kinds vs operator-node fields for invocation/unit-annotation), the unsupported-node allowlist contents, the standalone serialize surface, and the exact migration steps for each named surface item.
- The five S2 predicate-shape fixtures: decide how the three scratch-generated shapes become committed fixtures here (author minimal .sysml files in this repo's test fixtures — they're small).
- Downstream consumers to keep in view: Item 7 (Kleene compiler walks this tree in sysml-codegen), Item 13 (compat renderer must reproduce today's calc output byte-identically from it). Every field S2's compat rendering read must survive; name them.
- A skeptical design_review follows; make transition and dispatch decisions explicit with rejected alternatives.
