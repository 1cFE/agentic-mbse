# Brief: Item 3 design review — Executable Profile

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `design-review.md` in `.project/active/executable-profile/`.

## Review target
`.project/active/executable-profile/design.md` (spec, spec-review, briefs beside it).

## Ground truth
Landed types (`expression_facts.py`, `expression_ir.py`, `constraint_facts.py`); golden matrix (`tests/fixtures/constraint_fact_shapes/golden.json` — all 14 equality rows' decision codes); L4/L6 sites (`agentic_mbse/validation/level4_constraints.py`, `level6_architecture.py`); the concept's executable-profile paragraph + Non-Goals.

## What to probe hardest
1. **The 14-row reproduction claim.** The author self-reviewed the precedence against all 14 golden rows — re-derive it independently: walk each row's operand facts through the designed guard ordering and confirm the decision code, especially the tricky rows (enum-vs-enum incompatible; dimension-known-unit-unknown; promotion poisoning equality but not ordering).
2. **Default-deny completeness at the IR level.** For each of the six IR node kinds (incl. UnsupportedNode, UnitAnnotationNode, InvocationNode) in each position (predicate root, operand, nested), does the designed walk give exactly one outcome? What happens on an empty/missing predicate (satisfy, plain usages)?
3. **The same-IR seam (D7).** `UsageDecision.effective_predicate` carrying the walked instance: is this actually enforceable across the repo boundary (sysml-codegen consumes serialized facts — is instance identity even meaningful there, or must the contract be serialization-equality)? The preflight contract must not rest on Python object identity across a serialization boundary.
4. **L4/L6 replacement fidelity.** Read the current code: does the design's replacement preserve everything else those validators do (other checks in the same functions), and is the deletion surface named precisely?
5. **D9 fixture reuse**: synthesizing `inequality_cases` from certified operand facts rather than re-extracting — is that sound (are the operand facts sufficient to represent an inequality case without a real .sysml source), or does it break the golden's provenance discipline (S1's golden came from live extraction)?
6. **The unassessed/inventory boundary**: unused definitions never appear as unassessed (concept rule) — where does the design enforce it?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code and fixtures — do not take the design's word.
