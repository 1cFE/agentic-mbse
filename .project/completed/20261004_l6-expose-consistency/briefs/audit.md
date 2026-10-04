# Brief: audit — l6-expose-consistency

Audit the implemented item in `.project/active/l6-expose-consistency/` against its upstream artifacts: `spec.md` (contract), `design.md` (decisions D1–D6, invariants 1–7), `design-review.md` (must-fix items, Appendix C maps them to the design), and `plan.md` (checkboxes and implementation notes). You are a fresh session; you did not write any of it.

## Intent (orchestrator, provenance marked)

[INHERITED: spec] Make the supported-operator check and the design-attribute completeness check agree with the static-expression check on pure EXPOSE bindings by consulting the one existing EXPOSE predicate. No widening, no new expression support.

[AGENT] The implementation is committed at HEAD (`git show --stat HEAD`). Files: `src/agentic_mbse/validation/adr002.py`, `src/agentic_mbse/validation/level6_architecture.py`, `tests/test_sysml/test_adr002.py`, `tests/test_validation/test_l6_expose_consistency.py`, `tests/fixtures/l6_expose_consistency/**`.

## Orchestrator rulings you should audit against, not re-litigate

- D6 (keep the predicate's existing boundary, part-headed and multi-hop sibling chains included) is `[AGENT]` ratified by the orchestrator, not owner-originated. Audit that the code and tests implement it as recorded; the dotted-path doc rows are a recorded follow-up non-goal.
- Gate ruling: repo-wide ruff/format/mypy already fail on untouched code. The item's gate is no growth, new files fully clean, no new findings on changed lines. Baseline before: 1922 passed, 1 skipped, 33 deselected; ruff 119; 78 files unformatted; mypy 91 errors in 19 files.

## What to verify

1. Each spec success criterion has a committed test that proves it exactly as the design's Validation Approach states, not a weaker "contains" or `>=` form.
2. Each design invariant (1–7) holds in the code. In particular: no second EXPOSE decision site, no `"."` string test, `extract_operators` / `SUPPORTED_OPERATORS` / `STATIC_OPERATORS` / `evaluate_true_static_expression` untouched, FORMULA behaviour and `tests/test_l8_extractability.py` unchanged.
3. Each design-review must-fix item landed (design Appendix C); the predicate docstring claims only what the code checks.
4. The plan's checkboxes and notes reflect what actually happened; no placeholder, TODO, or dead code was introduced; `_build_calc_output_catalog` has no remaining reference anywhere.
5. Run the gate yourself and record the numbers: `uv run pytest tests/ -q`, `uv run ruff check src/ tests/` (count), `uv run ruff format --check src/ tests/` (count), `uv run mypy src/` (count). Also `uv run ruff check` on the five touched/new Python files alone.
6. Anything the implementation does that the design did not say (compare the diff of HEAD to the design's Implementation Notes).

Write findings with severity. Update the item's tracking only within `.project/active/l6-expose-consistency/`; leave `CURRENT_WORK.md`, `BACKLOG.md`, and `active/README.md` alone (the owner has uncommitted edits there). Produce `.project/active/l6-expose-consistency/audit.md`.
