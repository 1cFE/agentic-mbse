# PROMPT_build.md

You are building the **comment system** feature for agentic-mbse. Each iteration: implement ONE task, validate, commit.

## Build Loop Protocol

1. **Read specs/**: Understand requirements and design decisions
2. **Read IMPLEMENTATION_PLAN.md**: Pick the highest-priority incomplete task
3. **Search before assuming**: Use Grep/Glob to find existing code before adding new modules
4. **Implement ONE task completely**: No placeholders, no TODOs, no stubs
5. **Validate**: Run `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`
6. **Update IMPLEMENTATION_PLAN.md**: Mark task done, note discoveries/blockers
7. **Update AGENTS.md** ONLY for operational learnings (new commands, gotchas)
8. **Commit**: `git add -A && git commit -m "<task>: <what changed and why>"`

## Project Context

- **Language**: Python 3.12+ with uv for dependency management
- **Structure**: `src/comment_system/` with modules: `models.py`, `anchors.py`, `storage.py`, `cli.py`
- **Specs**: `specs/*.md` (read all spec files for requirements context)
- **Tests**: `tests/` directory, pytest framework
- **Validation**: All three must pass before commit (pytest, mypy, ruff)

## Guardrails (9s Convention)

- **999**: Capture the why in docs and tests. Comments explain decisions, tests verify behavior.
- **9999**: Single sources of truth. No migrations, no adapters, no dual representations.
- **99999**: Implement completely. If you write a function, it handles all cases. No stubs.
- **999999**: Keep IMPLEMENTATION_PLAN.md current. Mark tasks done immediately, note blockers as new tasks.
- **9999999**: AGENTS.md is operational only. Document commands, gotchas, setup steps. NOT progress notes.
- **99999999**: Bugs found? Resolve immediately OR create task in IMPLEMENTATION_PLAN.md with repro steps.
- **999999999**: Clean completed tasks from IMPLEMENTATION_PLAN.md when a logical phase finishes.
- **9999999999**: AGENTS.md clarity over completeness. Brief, actionable, no status updates.

## This Iteration

Read IMPLEMENTATION_PLAN.md. Pick ONE task. Implement it. Validate. Commit. Stop.

If no tasks remain, write "Build complete — all tasks done" and stop.
