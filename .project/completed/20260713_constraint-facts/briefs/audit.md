# Brief: Item 1 audit — Neutral Constraint Facts

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/constraint-facts/`.
- Attempt execution first (pytest works via `uv run pytest`); if blocked, write "Requested live probes" for the orchestrator.
- **NEVER run `pytest tests/ -m ""` or anything in `test_corpus_integration.py`** — that's the PDF-extraction subsystem, disjoint from this item, slow, and spends API money. [OWNER instruction.] The item's gate is the default suite.

## Audit target
The five Item 1 phase commits (`ce9a8ef..16005d3`) against `spec.md` (review-revised), `design.md` (rev 2 + MF4 addendum), `plan.md` (with the Phase 5 gate re-scope note).

## Context you must weigh
Phase 5 was completed by the orchestrator after the implement session hit its wall-clock timeout; the session's unconfirmable `-m ""` claim was withdrawn in plan.md. Audit the actual state, not the session's narrative.

## What to verify (by execution where possible)
1. **The six source forms** extract correctly: run the re-anchored golden tests; confirm the production golden asserts fact fields only (no Item-3 decision fields) and dimension = real `ISQBase::LengthUnit` (not the fabricated `ISQBase::Length`).
2. **Banned heuristics**: guard test green AND your own independent grep (namespace-prefix discrimination, `removesuffix` strips) over the three production modules.
3. **Dispatch order**: trace `constraint_extraction.py` against the design's gate ordering (membership first, isinstance assert gate, satisfy, named-usage-reference, then result_expression within asserts). The requirement_constraint-misclassified-as-inline bug (design MF2) must have a test proving it.
4. **Wire-format neutrality**: grep serialized output/tests for any `syside`/`Kind.` library string; direction must be neutral in/out/inout. Byte-stable round-trip at the pinned (constraint-facts/v1, predicate-tree/v0) pair — run the test.
5. **Tagged owner totality** (design MF3): all four owner kinds covered with tests, including package-scoped direct usage.
6. **Capture module retirement**: `tests/constraint_fact_learning.py` gone; S1 fixtures retained as semantic oracle; no orphan imports.
7. **Spec success-criteria walk** with evidence per item.

Verdict: Certify / Certify-with-notes / Fail.
