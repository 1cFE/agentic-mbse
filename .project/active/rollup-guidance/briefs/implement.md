# Brief: implement stage, rollup-guidance

Run as a subagent by the orchestrating session on 2026-10-25. Design and plan stages are skipped: the item is guidance only, and the orchestrator settles the spec's open questions below.

## Task

Implement `.project/active/rollup-guidance/spec.md` in `/home/reid/src/agentic-mbse` on branch `rollup-guidance`. Do not commit (the orchestrator commits). Do not touch sysml-codegen or dc3.

Read first: the spec, `evidence/probes.md` and probe `evidence/p2/` (the file that already passes both tools), `tests/test_validation/test_tool_examples.py` docstring (marker syntax), and the current text at `docs/patterns/adr002-calculations.md:176-200`.

## Orchestrator decisions on the spec's open questions [AGENT, 2026-10-25]

1. **Main example shape.** Show the direct form for same-kind groups (`sum(panel.capital_cost) + sum(caster.capital_cost)`) and different-kind singletons read directly. One prose sentence says a named intermediate per role (`panel_capital = sum(panel.capital_cost)`) also works and is optional. Reason: the simplest form that builds is the one to teach; the intermediate form was only ever taught because of a refusal that no longer exists.
2. **`designs/` rule.** Add one small wrong-way example marked `dir="designs" fails="V2_DYNAMIC_EXPRESSION"` (or whichever single code the probe shows reliably), so the one real placement rule is tested, not just stated. Say in prose that this is validate's rule (ADR-002), and that the generator would build it.
3. **Usage line.** Keep the part usage at the end of the one fence, with a short comment that in a project it lives in `designs/`.
4. **Hardcoded-placeholder anti-pattern.** Remove the fence; keep the point as one sentence of prose (don't bind a hand-typed child total where the children are modelled).
5. **Zero-module check in the test.** Out of scope for this item. Add one backlog row to `.project/backlog/BACKLOG.md` (P3, `[AGENT]`) saying a marked example that builds 0 modules passes the check half, with probe p1 as evidence.
6. **`mbse-concepts.md`.** Include it, as the spec says: replace both old fragments with a pointer to the new section.

## Quality bar

- Every claim in the new text is either shown by the marked example or cites its evidence. No claim about computed numbers unless it cites sysml-codegen's arithmetic tests by name.
- The guide and skill paragraphs are 2-3 sentences each and link to the pattern-doc section; do not copy the example into them.
- Grep the shipped trees (`docs`, `skills`, `agents`, `project_templates`) for other text that says the two-term rollup is refused, that named intermediates are required, or that the generator needs rollups in `library/`. Fix any you find in the same way, and list them.
- Follow `.claude/rules/working-voice.md` and `markdown-formatting.md` (one line per paragraph). Match the surrounding doc's style.

## Verify

Run `SYSML_CODEGEN=/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen uv run --env-file .env pytest tests/test_validation/test_tool_examples.py -q` (baseline 121 passed) and report the new count, plus the module count `check` reports for the new example. Also run `uv run pytest tests/test_validation -q` and `uv run ruff check tests/`.

Report: files changed, each decision you had to make beyond this brief, test output, and anything you did not check. End with `ARTIFACT: <path of the main changed file>`.
