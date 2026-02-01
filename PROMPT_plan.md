You are planning the next implementation iteration for the file-native comment
threading system. This is PLANNING ONLY — no implementation, no commits.

## Your Task

1. **Study all specs** in `specs/*` using parallel subagents (Task tool). Don't
   assume you know what's there — read every spec file.

2. **Study IMPLEMENTATION_PLAN.md** if it exists. Understand what's been
   planned vs. what remains.

3. **Study `src/comment_system/`** to understand what's already built. Don't
   assume anything is or isn't implemented — verify by reading the code.
   - Expected modules: `models.py`, `anchors.py`, `storage.py`, `cli.py`
   - Check what functions/classes exist, what's stubbed, what's complete.

4. **Gap analysis**: Compare specs against current code. What's specified but
   not implemented? What's partially done? What's tested?

5. **Create/update IMPLEMENTATION_PLAN.md** with prioritized tasks for the next
   iteration. Each task must:
   - Be sized for ONE iteration (~5 files max to read/modify)
   - Reference which spec(s) it addresses
   - Note backpressure (tests, typechecks, lints that verify it)
   - Have clear acceptance criteria

## Project Context

- **Language**: Python with UV package manager
- **Testing**: pytest (`uv run pytest tests/`)
- **Type checking**: mypy (`uv run mypy src/comment_system`)
- **Linting**: ruff (`uv run ruff check src/ tests/`)
- **Structure**: `src/comment_system/` for implementation, `tests/` for tests

## Rules

- Use "study" not "read" — emphasize thorough understanding.
- **Ultrathink** for complex analysis (reconciliation algorithm, anchor design).
- Don't assume anything is implemented without verification.
- Break down tasks < 5 files. Prefer small, verifiable increments.
- Use markdown bullet points for the plan, not JSON.
- List tasks in priority order (dependencies first, then features).
- Each task should have: description, spec references, backpressure, acceptance.
