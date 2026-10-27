# Brief: spec stage, rollup-guidance

Run as a subagent by the orchestrating session on 2026-10-25 (the `orchestrate-stage.sh` helper is absent on this box).

## Task

Write `.project/active/rollup-guidance/spec.md` following `~/.claude/commands/_my_spec.md`. Do not implement anything. Work in `/home/reid/src/agentic-mbse` on branch `rollup-guidance`; do not commit (the orchestrator commits).

## Intent

[OWNER] 2026-10-25: fix the agentic-mbse side of the costing gap with a complete, tested rollup example in `docs/patterns/adr002-calculations.md`, plus a short paragraph in `project_templates/MODELING_GUIDE.md.template` and `skills/sysml-conventions/SKILL.md`, all marked so both tools run them. dc3 and sysml-codegen are out of scope.

[OWNER] standing goal (2026-10-23, `.project/CURRENT_WORK.md`, P-0007): the shipped guidance teaches what the tools actually do; every complete shipped example is marked and run through `agentic-mbse validate` and `sysml-codegen check` by `tests/test_validation/test_tool_examples.py` (read its docstring for the marker syntax).

Why [AGENT, from the owner conversation]: consumer project dc3 (WI-008, `/home/reid/src/dc3/work/completed/20261024_WI-008_generator-idiom/design.md` P6, P8) abandoned the toolkit's costing pattern because our docs show only `sum(child.capital_cost)` over identical children (`docs/patterns/adr002-calculations.md:176-200`, marked "parser-validated" only, incomplete, not run by the test). The generator supports more than the docs say.

## Source of truth

- sysml-codegen at `/home/reid/src/sysml-codegen` (main `e6c20bca`): `tests/fixtures/costed_cart_d5/library.sysml` (Deck Assembly: `sum()` over identical arrayed children with one named intermediate per role; Frame Assembly: two singleton children of different kinds referenced directly; Cart Plant: nested assemblies), `docs/architecture/modeling-assumptions.md` § 4 and § 6, `tests/integration/test_costed_component_exact_route.py` (18 pass today, including `test_a_two_term_same_name_rollup_is_refused`).
- Generator: `/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen`. Run the example test with `SYSML_CODEGEN=<that path> uv run --env-file .env pytest tests/test_validation/test_tool_examples.py` (baseline 121 passed).

## What the spec must settle

- The behaviours the guidance will state, each with how it is verified (a marked example in the test, or a probe recorded as evidence). At least: per-role named intermediates; different-kind singleton children referenced directly; `sum()` over an exact-multiplicity group; nesting two or more levels; the refused two-term same-name form (`SI_RENDERING_COLLISION`).
- [AGENT, unverified] § 4 says the rollup expression must sit on a part def in `library/`, not in `designs/`. Requirement: probe this on current main before any guidance states it; if it does not hold, the guidance leaves it out. Same for any other § 4 condition the guidance repeats.
- Where each piece goes, and that the guide and skill paragraphs stay short and point to the pattern doc rather than restating it.
- The current incomplete snippet and its "parser-validated" status are replaced, not kept beside the new example.

Use the provenance grades in `.claude/rules/capture-fidelity.md`. Keep it short; this is a small item. Follow `.claude/rules/working-voice.md` and `markdown-formatting.md` (one line per paragraph).

End your final message with `ARTIFACT: <path>`.
