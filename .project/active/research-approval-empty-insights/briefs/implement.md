# Brief: implement — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_implement`. **Inputs:** `plan.md`, `design.md`, `spec.md` in `.project/active/research-approval-empty-insights/`. Run both phases in this session.

## What this work is for

[AGENT, re-derived] Research approved with no new insight goes through the supported operation, so nobody moves the file by hand. The shipped `/research` instruction is part of the repair: it is how an agent learns to pass `--insights '[]'`.

## Rulings

- [OWNER] (2026-10-05) No reserved gates. Decide execution details and record them in the plan's implementation notes; do not ask.
- [AGENT] (orchestrator, 2026-10-05) Design D1-D7 and the plan are accepted as written, including the plan's test 11 and its move of the CLI tests into Phase 1.

## Engineering bar

- `approve_research` stays one function with one path and one move statement. No early-return copy for the empty case. The result is derived from the entries written (design I6).
- Refuse before any write (I1). Check order is the design's: normalize, containment, exists, regular file, type check, then the gated registry read.
- The non-empty success message, `files_modified` order, IDs, and warnings are unchanged byte for byte (I5).
- Tests use real temp projects for anything the spec states about files on disk. Follow the existing style and helpers in `tests/test_pm_operations.py` and `tests/test_pm_cli.py`; parametrize rather than copy.
- Record the red-before-green evidence in the plan as you go: for each test the plan expects to fail against unchanged `src/`, the actual failure message. If a test meant to fail passes, or fails for another reason, fix the test before touching `src/`.
- Use the design's exact text for the messages, help strings, `research.md` line, and `SKILL.md` row. If a string cannot be used as written, say why in the plan notes.
- Leave no TODOs, no placeholder code, no commented-out code, and no unrelated edits.

## Boundaries

- Do not commit. The orchestrator commits after reading the diff.
- Do not touch `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md`. It is an untracked file from another session.
- Do not run `close` or `pre_pr`.

## Gates to run and report

`uv run pytest tests/` (default selection), `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/`. Report the actual counts and any failure verbatim. If a gate was already failing on `2a229f4` before your change, show that with evidence and leave it alone.

Check off the plan's boxes as each step completes. Finish with `ARTIFACT: <path>`.
