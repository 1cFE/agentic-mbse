# Brief: Item 1 spec review — Neutral Constraint Facts

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec-review.md` in `.project/active/constraint-facts/`.

## Review target
`.project/active/constraint-facts/spec.md` — the spec for production `ConstraintDefinitionFact`/`ConstraintUsageFact`/`ConstraintSource` schemas + live extraction.

## Context
- The stage brief the author received: `.project/active/constraint-facts/briefs/spec.md`.
- The owner-ratified concept is now readable in-repo: `.project/reference/constraint-execution-concept.md` (the author could NOT read it — they worked from the S1 findings and brief only; a prime review angle is whether anything in the concept's "Neutral Constraint Facts" section, Required Invariants, or S1 carry-forwards failed to reach the spec).
- Epic item text: `.project/reference/epic_constraint_execution.md`, Item 1.
- Ground truth: S1 findings (`.project/active/spike-constraint-fact-shapes/findings.md`), golden fixtures (`tests/fixtures/constraint_fact_shapes/`), kept tests (`tests/test_sysml/test_constraint_fact_shapes.py`), adapter (`agentic_mbse/sysml/syside_adapter.py`).

## What this item must get right (weigh your findings against these)
1. This schema is the vocabulary three repos consume; a shape error here multiplies downstream. Versioning and byte-stable serialization are load-bearing (snapshot v3 consumes the JSON section).
2. All six source-form classes pinned so nothing falls between "assertion" and "authoring inventory" (the concept's `[AGENT]` note demands both non-asserted shapes are pinned).
3. The two banned heuristics (namespace prefix, unit-suffix strip) must be requirements with principled replacements, not advisory notes.
4. Downstream needs: Item 2 adopts the feature-ref/literal leaf vocabulary; Item 5 needs owner/scope + `owning_part_def_qn`-grade identity facts; Item 8 needs the versioned JSON section; Item 3 needs operand type/unit facts sufficient for the equality/unit gates.

Verdict format: must-fix list (each with why it's load-bearing), then nice-to-haves, then an overall verdict (Approved / Approved-with-must-fixes / Rework). Verify claims against the golden fixtures and code — do not take the spec's word.
