# Brief: Item 1 implement — Neutral Constraint Facts

You are the implement stage for Item 1 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase (subject leads with the phase), check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/constraint-facts/`. Do NOT commit `uv.lock` (known pre-existing local modification hazard).

## Input — execute the plan
`.project/active/constraint-facts/plan.md` (5 phases) is authoritative; it references `design.md` sections for the dispatch pseudocode, schemas, and traversals — follow those exactly.

## Environment
- Live extraction tests run in this repo: `uv run pytest tests/...` (license loads for pytest/script runs, NOT bare `python -c` probes).
- S1 fixtures: `tests/fixtures/constraint_fact_shapes/`.

## Quality bar
- Match existing `agentic_mbse.sysml` idiom (see `aggregation.py`, `data_models.py` for dataclass/docstring style). No TODOs, no commented-out code.
- The banned heuristics must not appear even transiently: inline-vs-definition-typed decided ONLY by result_expression ownership within the assert gate; dimension ONLY by the structural mRef traversal (most-specific unit-definition type).
- Awareness: sysml-codegen consumes this repo via editable install. Item 1 is additive (new modules) — do not modify existing shared modules' behavior; if a plan step seems to require it, STOP and report.
- Final gates: full suite green, ruff clean, byte-stable round-trip green, banned-heuristic grep guard green.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
