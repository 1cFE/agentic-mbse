# Brief: Item 1 design review — Neutral Constraint Facts

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/constraint-facts/`.

## Review target
`.project/active/constraint-facts/design.md` (spec, spec-review, briefs beside it; concept at `.project/reference/constraint-execution-concept.md`).

## Orchestrator evidence (verified cross-repo, which you cannot read)
The design's D1 (dataclass) rested on in-repo precedent only. The orchestrator verified downstream directly: sysml-codegen's `src/sysml_codegen/extraction/data_models.py` imports `agentic_mbse.sysml.data_models` dataclasses and `agentic_mbse.sysml.types` values today. Treat D1's precedent claim as confirmed; do not spend review effort there.

## What to probe hardest
1. **The provisional-predicate-tree seam (C1).** Item 1 carries a "provisional" predicate tree that Item 2's ExpressionIR later canonicalizes. Is this a version-churn trap? If Item 2 replaces the tree shape, does `constraint-facts/v1` need a v2 immediately — invalidating Item 8's snapshot section within the same epic? Check whether the design isolates the predicate field so Item 2's arrival is additive (e.g. opaque/versioned sub-document) or whether it bakes a tree shape three items will have to migrate. This is the highest-stakes structural call.
2. **Six source forms × schema totality.** Walk each of S1's six source-form fixtures against the proposed schemas: every field the golden asserts must have a home, including inheritance/retyping facts, omitted defaulted formals, and anonymous-assertion source-location identity.
3. **Byte-stability contract.** `sort_keys` + fixed separators + `ensure_ascii=True` + `allow_nan=False`: any float-repr or int/float boundary hazard for literal values? Where do quantity values live and can they be non-finite (the spec's Kleene story lives downstream, but the FACTS must carry non-finite literals losslessly or reject them loudly)?
4. **The banned-heuristic replacements.** The design must state the exact structural discriminators (result_expression ownership; structural dimension resolution) at extraction points, and the deleted learning module's fixtures must genuinely survive as semantic oracle (paths, test wiring).
5. **D6 `owning_definition`**: is the resolution rule total across the six forms (what is the owning definition of a direct-usage-owned assert at package scope)?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against fixtures and code — do not take the design's word.
