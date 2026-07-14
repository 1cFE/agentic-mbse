# Brief: Item 2 plan — ExpressionIR

You are the plan stage for Item 2 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `plan.md` in `.project/active/expression-ir/`.

## Input
- Design rev 2 (committed, review-revised): `.project/active/expression-ir/design.md` — tagged union, allowlist, single encoder, the 8-site migration worklist, the every-.kind-reader rule, and the new-fixture spec are authoritative.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files, the design's schema sketches as the target shapes, per-phase `uv run pytest` gates (default suite selection only).
- Sequence: new module + serializer + round-trip tests first (offline); then extractor cutover with the allowlist inversion; then the 8-site migration in one lockstep phase with the golden regeneration (self-compare) and the version-constant bump; then final gates (default suite, ruff, byte-stable round-trip at (constraint-facts/v1, expression-ir/v1), no-silent-third-representation grep: ExpressionFact gone).
- The new .sysml fixture (^/** distinctness, unary minus, exercised unsupported) is authored in this repo's test fixtures; live tests run via `uv run pytest` here.
- Keep phases resumable from checkboxes.
