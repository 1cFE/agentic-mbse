# Brief: plan — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_plan`. **Inputs:** `spec.md` and `design.md` in `.project/active/research-approval-empty-insights/`.

## What this work is for

[AGENT, re-derived] Research approved with no new insight goes through the supported operation, so nobody moves the file by hand.

## Rulings

- [OWNER] (2026-10-05) No reserved gates. Decide and record; do not ask.
- [AGENT] (orchestrator, 2026-10-05) The design is accepted as written, including D5 (normalize the path before the containment check). Spec criterion 4 was amended to match. No design review was run: D5 was the one non-obvious decision and it is ruled.

## Scale and shape

This is a LOW item for one implementation session. Write a short plan, not a long one. The design already fixes the decisions, the exact messages, the exact shipped wording, and a ten-test list mapped to spec criteria. Point at those sections by path; do not restate them.

[AGENT] Suggested shape, two phases. Change it if you see a better cut.

1. **Operation, test-first.** Write tests 1-7 from the design's operation table in `tests/test_pm_operations.py`. Confirm the new ones fail for the right reason against current code. Then change `approve_research` (`src/agentic_mbse/pm/operations.py:910`) per D1-D5 and the design's check order. Green on `uv run pytest tests/test_pm_operations.py`.
2. **CLI tests and shipped text.** Tests 8-10 through `main()` in `tests/test_pm_cli.py`; the two argparse help strings (`src/agentic_mbse/cli/pm_cli.py:560`, `:562`); the added line in `claude/commands/research.md` after `:79`; the reworded row at `claude/skills/toolkit-awareness/SKILL.md:90`. Use the exact text in the design's Implementation Notes.

Each phase ends with the project gates: `uv run pytest tests/` (default selection), `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/`.

## What the plan must make checkable

- The red-before-green evidence for the new tests: which tests failed before the code change, and with what message.
- The design's invariants I1-I6 each map to at least one named test.
- A final step that updates the item's tracking line in `.project/CURRENT_WORK.md` and the backlog status line. Leave `close` to the owner.

Finish with `ARTIFACT: <path>`.
