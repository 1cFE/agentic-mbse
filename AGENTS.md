# AGENTS.md — Comment System

## Build & Validate

```bash
uv sync --extra dev              # Install all deps
uv run pytest tests/             # Tests
uv run mypy src/comment_system   # Type check
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
```

## Project Structure

```
src/comment_system/
├── models.py    # Pydantic models (Thread, Comment, Anchor, Sidecar)
├── anchors.py   # Anchor reconciliation logic
├── storage.py   # File I/O for .comments/ sidecars
├── cli.py       # CLI entry point
specs/           # Spec documents (requirements)
tests/           # pytest tests mirror src/ structure
.comments/       # Sidecar storage (created at runtime)
```

## Conventions

**Imports:**
```python
from comment_system.models import Thread, Comment, Anchor, Sidecar
from comment_system.storage import load_sidecar, save_sidecar
```

**Critical rules:**
- **NEVER modify source files.** All writes go to `.comments/` only.
- **ULID for IDs.** Thread/comment IDs are ULIDs (sortable, unique).
- **Atomic writes.** Temp file + rename for all sidecar updates.
- **pathlib.Path** throughout. No string path manipulation.
- **Type hints** on all functions. `mypy` must pass.

**Error handling:** Custom exceptions (`CommentSystemError`, `AnchorNotFoundError`, `InvalidAnchorError`). Library raises; CLI catches and prints user-friendly messages.

**Status lifecycle:** `open` → `resolved` | `wontfix`. Resolved can reopen → `open`.

**Health states:** `anchored` (exact match) → `drifted` (fuzzy match) → `orphaned` (lost).

**Reconciliation priority:** content hash → context hash + fuzzy → line offset → orphaned.

## Gotchas

- **Test isolation:** Use `tmp_path` fixture. No shared directories.
- **Sidecar paths mirror source tree:** `src/foo.py` → `.comments/src/foo.py.json`
- **Reconciliation is lazy:** CLI must explicitly call `reconcile()` when needed.
- **CLI testing:** Use `click.testing.CliRunner` with `catch_exceptions=False`.
- **ULID in tests:** Don't compare ULIDs for equality across runs.
