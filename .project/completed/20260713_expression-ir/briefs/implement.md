# Brief: Item 2 implement — ExpressionIR

You are the implement stage for Item 2 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/expression-ir/`. Do NOT commit `uv.lock`.
- **NEVER run `pytest tests/ -m ""` or anything in `test_corpus_integration.py`** — unrelated PDF subsystem, spends API money. [OWNER instruction.] All gates use the default suite selection.

## Input — execute the plan
`.project/active/expression-ir/plan.md` (3 phases) is authoritative; `design.md` rev 2 holds the schema sketches, allowlist, 8-site migration worklist, and golden-diff checklist. Phase 2 is deliberately atomic (suite red mid-phase, green at gate) — commit Phase 2 only at its green gate.

## Environment
- Live tests: `uv run pytest tests/...` in this repo (license loads for pytest runs).
- Phase 1's live de-risk gate (distinct `^`/`**` enums; off-allowlist metaclass behavior) comes FIRST — if either check contradicts the design, STOP and report before building nodes.

## Quality bar
- Match `agentic_mbse.sysml` idiom. No TODOs, no commented-out code.
- Golden regeneration diff must match the design's golden-diff checklist (unit-node operands[1] drop is the only subtree deletion) — record the diff review in plan notes.
- Final gates: default suite green, ruff clean, byte-stable round-trip at (constraint-facts/v1, expression-ir/v1), grep gates (no ExpressionFact, no silent third representation).
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
