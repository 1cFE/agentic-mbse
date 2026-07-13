# Brief: Item 1 plan — Neutral Constraint Facts

You are the plan stage for Item 1 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/constraint-facts/`.

## Input
- Design rev 2 (committed, review-revised + MF4 live-confirmed): `.project/active/constraint-facts/design.md` — module split, dispatch order, tagged owner fact, predicate sub-versioning, and the dimension traversal (select the most-specific unit-definition type from mRef's types, per the addendum) are authoritative.
- Spec, spec-review, design-review beside it.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files (`expression_facts.py`, `constraint_facts.py`, `constraint_extraction.py`), the dispatch-order pseudocode from the design, per-phase verification commands.
- Live extraction tests run in THIS repo's env (`uv run pytest ...` — the license loads for script/pytest runs, not bare `python -c`). The S1 fixtures are committed at `tests/fixtures/constraint_fact_shapes/`.
- Phase the golden re-anchor as: production extractor → production golden (self-comparing, real `ISQBase::LengthUnit` dimension) → semantic-oracle comparison against S1's `golden.json` fact fields (decision fields excluded).
- Include the deletion of `tests/constraint_fact_learning.py` (retire decision) and the re-pointing of its kept tests, as their own phase with a suite-green gate.
- Final gates: full suite green, ruff clean, byte-stable round-trip test present and green, no banned heuristic (grep for the namespace-prefix and Unit-suffix-strip patterns the design names).
- Keep phases resumable from checkboxes.
