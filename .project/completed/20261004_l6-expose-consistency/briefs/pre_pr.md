# Brief: pre_pr — branch gate for harness-right-size

Owner has asked for the PR to be submitted now. Branch `harness-right-size` is pushed to origin at `67c4d23`; target is `main`. The owner is not present; where the command would ask the user, decide as below or stop with questions.

## Scope (already settled)

21+ commits over main in three groups: (1) `35fa2b6`, `d20069b`, `ce80472` — modeling-process right-sizing and workflow simplification (claude/commands, claude/skills, project_templates), already installed and trialled in fusion-tea; (2) the `l6-expose-consistency` item — `src/agentic_mbse/validation/adr002.py`, `level6_architecture.py`, new tests and fixtures, archived at `.project/completed/20261004_l6-expose-consistency/` (audit certified, consumer validation recorded in `consumer-validation.md`); (3) `.project/` tracking: 2026-10-04 status refresh and four draft specs. The working tree is clean. Treat all three as in scope; do not ask whether to split.

## Quality checks — parity rule, not green rule

`uv run pytest tests/` must pass (expected 1932 passed, 1 skipped, 33 deselected). `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, and `uv run mypy src/` fail on `main` today (119 ruff / 78 unformatted files / 91 mypy) and on this branch (118 / 78 / 91). **Do not reformat or lint-fix files this branch did not change.** Reformatting 78 files would bury a 20-line validator change. Fix only findings on lines this branch added or changed; the four touched Python files already pass `ruff check` individually. Record the before/after counts in your summary.

Scan the branch diff for debug artifacts, secrets, and large binaries as the command says. `.env` is gitignored and must not appear in the diff.

## PR

Create it with `gh pr create --base main`. Title: `Right-size modeling harness and fix L6 EXPOSE false positives`. Body: three short sections matching the scope groups, with the L6 section giving the before/after numbers from `consumer-validation.md` (fusion-tea `models/`: 7734 → 408 Level 6 issues, 0 added; stellarator study 1848 → 196; WI-099 scenario now passes all six levels) and the six follow-up backlog IDs. Note the parity rule for lint/format. End the body with the line `🤖 Generated with [Claude Code](https://claude.com/claude-code)`. Return the URL in your final message.

Do not commit; the orchestrator commits anything you change. Finish with `ARTIFACT: <PR URL>`.
