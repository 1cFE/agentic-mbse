# Brief: audit stage, rollup-guidance

Run as a fresh subagent by the orchestrating session on 2026-10-25. You did not write any of this; check it skeptically.

## Task

Audit commit `d2f441a3` on branch `rollup-guidance` in `/home/reid/src/agentic-mbse` against `.project/active/rollup-guidance/spec.md`, following `~/.claude/commands/_my_audit.md`. Write the audit to `.project/active/rollup-guidance/audit.md`. Do not fix anything and do not commit.

## What matters most

The owner's goal is that shipped guidance teaches what the tools actually do. Docs in this area have been wrong several times, including the sysml-codegen doc the brief for this item trusted. So verify every factual claim in the changed text yourself, against the tools, not against other docs:

- Run the example test: `SYSML_CODEGEN=/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen uv run --env-file .env pytest tests/test_validation/test_tool_examples.py -q` (expected 125 passed).
- Every sysml-codegen test name cited exists at `/home/reid/src/sysml-codegen` main `e6c20bca` and asserts what the text says it does. Run them.
- "The generator would build the same rollup in `designs/`": probe it yourself with the wrong-way example under `designs/` (scratch dir under `/tmp/claude-1000/`, not the repo).
- "Named totals each become their own generated module": check it.
- The validate codes named for `designs/` are the ones validate reports.
- Grep the shipped trees (`docs`, `skills`, `agents`, `project_templates`) for anything the change now contradicts.

Also judge: does a modeller with named children of different kinds, several levels deep (dc3's case, `/home/reid/src/dc3/work/completed/20261024_WI-008_generator-idiom/design.md` P6/P8), now get a working shape from the guide and skill? Is the guide/skill paragraph in a sensible place (it currently sits under a heading about structures the generator refuses)? Is the text plain and short per `.claude/rules/working-voice.md`?

Rank findings must-fix / should-fix / note. End with `ARTIFACT: <path>`.
