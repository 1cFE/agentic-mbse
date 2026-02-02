# Design: D4.5 CLI Subcommands

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Updated:** 2026-02-02
**Branch:** revamp-architecture

## Overview

Wire the D4.3 dashboard and D4.4 operations into the `agentic-mbse` CLI as two new subcommand groups: `agentic-mbse status` and `agentic-mbse pm <operation>`. The implementation adds a new `pm_cli.py` module alongside the existing `cli/__init__.py` and a shared `find_project_root()` utility.

## Related Artifacts

- **Spec:** `.project/active/d4.5-cli-subcommands/spec.md`
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.5 section)
- **D4.4 Design:** `.project/active/d4.4-operations/design.md`
- **Existing CLI:** `src/agentic_mbse/cli/__init__.py` (1102 lines)
- **PM module:** `src/agentic_mbse/pm/__init__.py` (104 lines)
- **Dashboard:** `src/agentic_mbse/pm/dashboard.py` (177 lines)
- **Types:** `src/agentic_mbse/pm/types.py` (245 lines)

---

## Research Findings

### Existing CLI Patterns

**Framework**: argparse (stdlib). No external dependencies for CLI.

**Dispatch pattern** (`cli/__init__.py:1008-1101`):
- `main()` creates top-level `ArgumentParser` with `subparsers`
- Each subcommand registers via `subparsers.add_parser()` + `parser.set_defaults(func=cmd_*)`
- `args.func(args)` dispatches — all `cmd_*` functions take `argparse.Namespace`, return `int`
- Exit codes: `EXIT_SUCCESS = 0`, `EXIT_FAILURE = 1` from `validation/__init__.py`

**Error handling** (`cli/__init__.py:475-487`):
- `cmd_validate` prints errors directly and returns exit codes
- No try/except wrapping — exceptions propagate to `main()` caller
- Errors go to stdout via `print()` (not stderr) — the existing convention is informal

**File size**: `cli/__init__.py` is already 1102 lines (dominated by `cmd_init` at ~470 lines). Adding 14 operation sub-subcommands with argument definitions inline would push it past 1500 lines.

### PM Module Types (D4.4 Design)

The D4.4 design specifies these return types that the CLI must handle:

- **`OperationResult`**: `success: bool`, `message: str`, `ids_assigned: dict`, `files_modified: list`, `warnings: list[ParseWarning]` — used by all mutation operations
- **`ImpactResult`**: `query_id: str`, `affected_elements: list[TraceabilityEntry]`, `affected_work_items: list[str]`, `warnings: list[ParseWarning]` — used by `impact_query`
- **`DashboardResult`**: `markdown: str`, `warnings: list[ParseWarning]` — used by `get_status` / `generate_dashboard()` (already defined at `types.py:242`)

### Input Types for JSON Arguments (D4.4 Design)

Three Pydantic input types for JSON CLI arguments:
- **`InsightInput`**: title, source, context, model_implications, analysis_implications, rationale (optional)
- **`GoalInput`**: goal, priority, source, status (default "active"), traced_requirements (default "")
- **`QuestionInput`**: question, source, implies (default ""), status (default "open")

These validate at the Pydantic layer, giving clear error messages on malformed JSON input.

### Dashboard JSON Serialization

`DashboardResult` is a Pydantic `BaseModel` (`types.py:242`). For `--json` output, `result.model_dump_json(indent=2)` produces clean JSON. The `ProjectState` inside the dashboard result is also a Pydantic model, so the full object graph serializes. However, `DashboardResult` only has `markdown: str` + `warnings` — for `--json`, we need to expose the structured `ProjectState` plus requirements/validation metrics, not just the rendered markdown.

Two options for `--json`:
1. Serialize `DashboardResult` as-is (just `{"markdown": "...", "warnings": [...]}`) — simple but not useful for programmatic consumers since they'd have to parse the markdown string
2. Build a richer JSON representation with the `ProjectState`, requirement counts, and validation counts as structured data

Option 1 is consistent with the spec's "machine-readable output" goal. A programmatic consumer that gets `ProjectState` as JSON can query work item states, epic progress, etc. without parsing markdown. Option 2 is more useful.

**Decision**: For `--json`, call `generate_dashboard()` but instead of printing `result.markdown`, serialize the underlying `ProjectState` plus parsed requirements and validation data. This requires a minor addition to `DashboardResult` or a separate code path in the status handler that calls `derive_project_state()`, `parse_requirements()`, and `parse_validation_matrix()` directly and serializes their results. The simplest approach: add a `state` field to `DashboardResult` or create a `StatusJsonResult` model.

Actually, the simplest approach that avoids modifying `DashboardResult` (which is D4.3's domain): the `cmd_status` handler calls `generate_dashboard()` for markdown mode. For `--json` mode, it calls the same parsers directly (`derive_project_state`, `parse_requirements`, `parse_validation_matrix`) and serializes a dict. This keeps the JSON structure flexible without coupling it to the dashboard model.

---

## Proposed Design

### Component 1: Project Root Detection (`cli/__init__.py`)

```python
def find_project_root() -> Path | None:
    """Walk up from CWD to find a project root.

    Looks for work/BACKLOG.md (primary) or .claude/ (fallback).
    Returns None if neither found.
    """
```

Implementation: Start at `Path.cwd()`, walk up via `.parent` until hitting the filesystem root. Check `candidate / "work" / "BACKLOG.md"` first, then `candidate / ".claude"`. Return the first match, or `None`.

This lives in `cli/__init__.py` as a module-level function (alongside `_get_data_root()`, `get_commands_dir()`, etc. at `cli/__init__.py:106-149`). It's a CLI concern — the PM library functions take `project_root: Path` explicitly.

### Component 2: PM CLI Module (`cli/pm_cli.py`)

**New file**: `src/agentic_mbse/cli/pm_cli.py`

This module contains all `pm` subcommand registration and dispatch functions. Separating it from `cli/__init__.py` follows NF-4 (keep manageable file sizes) and keeps the 14 operation handlers organized.

**Structure**:

```python
"""CLI handlers for 'agentic-mbse pm' subcommands."""

import argparse
import json
import sys
from pathlib import Path

from agentic_mbse.pm.types import ParseWarning

# Imported when called (D4.4 dependency):
# from agentic_mbse.pm import operations


from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS


def _print_warnings(warnings: list[ParseWarning]) -> None:
    """Print parser warnings to stderr."""
    for w in warnings:
        print(f"Warning: {w.file}: {w.message}", file=sys.stderr)


def _parse_json_arg(value: str, label: str) -> tuple[dict | list | None, str | None]:
    """Parse a JSON string argument.

    Returns (parsed_value, None) on success, or (None, error_message) on failure.
    Callers return exit code 2 on failure — no sys.exit() here.
    """
    try:
        return json.loads(value), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON for {label}: {e}"


def register_pm_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'pm' subcommand group with all operation sub-subcommands."""
```

**The key function is `register_pm_subcommands()`** — called from `main()` in `cli/__init__.py`. It creates the `pm` parser, adds a second level of subparsers, and registers each operation.

### Component 3: Subcommand Registration Detail

`register_pm_subcommands()` creates nested subparsers:

```python
def register_pm_subcommands(subparsers):
    pm_parser = subparsers.add_parser(
        "pm",
        help="Project management operations (AP-7)",
        description="Deterministic project management operations. "
                    "Each operation reads structured files, validates inputs, "
                    "and writes atomically.",
    )
    pm_subs = pm_parser.add_subparsers(dest="operation")

    # close-item
    p = pm_subs.add_parser("close-item", help="Archive a completed work item")
    p.add_argument("wi_id", metavar="WI-XXX", help="Work item ID to close (e.g. WI-001)")
    p.set_defaults(func=cmd_pm_close_item)

    # add-insight
    p = pm_subs.add_parser("add-insight", help="Register a domain insight (DI-XXX)")
    p.add_argument("--title", required=True, help="Insight title")
    p.add_argument("--source", required=True, help="Source document or reference")
    p.add_argument("--context", required=True, help="Context explaining the insight")
    p.add_argument("--model-implications", required=True, help="How this affects the model")
    p.add_argument("--analysis-implications", required=True, help="How this affects analysis")
    p.add_argument("--rationale", help="Optional rationale")
    p.set_defaults(func=cmd_pm_add_insight)

    # ... (all 14 operations follow this pattern)
```

Each operation's arguments match the D4.4 function signatures exactly. The full argument list for all 14 operations:

| Operation | Positional | Required flags | Optional flags |
|-----------|-----------|----------------|----------------|
| `close-item` | `wi_id` | — | — |
| `add-insight` | — | `--title`, `--source`, `--context`, `--model-implications`, `--analysis-implications` | `--rationale` |
| `save-research` | — | `--topic`, `--content-file` | — |
| `approve-research` | `file` | `--insights` (JSON) | — |
| `trace-element` | — | `--element`, `--file`, `--type` | `--knowledge` (multi), `--requirement` (multi), `--source-type`, `--source-doc`, `--source-location`, `--confidence`, `--assumptions` |
| `promote-requirement` | — | `--requirement`, `--source`, `--enforcement`, `--validation-method` | — |
| `impact-query` | `query_id` | — | — |
| `register-decision` | — | `--title`, `--decision`, `--rationale` | — |
| `update-validation` | `sv_id` | `--status` | — |
| `register-intent` | — | — | `--goals` (JSON), `--questions` (JSON) |
| `add-item` | — | `--name`, `--scale`, `--priority` | `--epic`, `--goal` |
| `add-validation` | — | `--description`, `--type`, `--mechanism`, `--expected`, `--tolerance` | `--source`, `--test` |
| `supersede-insight` | `old_id` | `--new-insight` (JSON), `--reason` | — |

**Multi-value arguments** (`--knowledge`, `--requirement` in `trace-element`): Use `nargs="*"` or `action="append"`. Since agents may pass multiple IDs, `action="append"` is more natural: `--knowledge DI-001 --knowledge DI-002`. But `nargs="+"` with space-separated values is also viable: `--knowledge DI-001 DI-002`. The `action="append"` pattern is safer since it avoids ambiguity with positional args.

**JSON arguments**: `--insights`, `--goals`, `--questions`, `--new-insight` accept a JSON string. argparse receives them as `str`; the dispatch function parses with `json.loads()` and validates with Pydantic.

**`register-intent` validation**: At least one of `--goals` or `--questions` must be provided. argparse can't express this directly. The dispatch function validates and exits 2 if both are missing.

### Component 4: Dispatch Functions (`pm_cli.py`)

Each operation gets a thin dispatch function. They all follow the same pattern:

```python
def cmd_pm_close_item(args: argparse.Namespace) -> int:
    from agentic_mbse.cli import find_project_root
    from agentic_mbse.pm.operations import close_item

    project_root = find_project_root()
    if project_root is None:
        print("Error: Not inside a project (no work/BACKLOG.md found)", file=sys.stderr)
        return EXIT_FAILURE

    result = close_item(project_root, args.wi_id)
    _print_warnings(result.warnings)
    print(result.message)
    return EXIT_SUCCESS if result.success else EXIT_FAILURE
```

To reduce boilerplate, a shared helper handles the common pattern:

```python
def _dispatch(args: argparse.Namespace, fn, **kwargs) -> int:
    """Common dispatch: find root, call operation, handle result."""
    from agentic_mbse.cli import find_project_root

    project_root = find_project_root()
    if project_root is None:
        print("Error: Not inside a project (no work/BACKLOG.md found)", file=sys.stderr)
        return EXIT_FAILURE

    result = fn(project_root, **kwargs)
    _print_warnings(result.warnings)
    print(result.message)
    return EXIT_SUCCESS if result.success else EXIT_FAILURE
```

Then each handler extracts args and delegates:

```python
def cmd_pm_close_item(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.operations import close_item
    return _dispatch(args, close_item, wi_id=args.wi_id)

def cmd_pm_add_insight(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.operations import add_insight
    return _dispatch(args, add_insight,
        title=args.title,
        source=args.source,
        context=args.context,
        model_implications=args.model_implications,
        analysis_implications=args.analysis_implications,
        rationale=args.rationale,
    )
```

**Lazy imports**: Operations are imported inside each dispatch function, not at module level. This avoids importing the entire PM module when running `agentic-mbse validate` or `agentic-mbse init`. The PM module pulls in pydantic, yaml, csv, and the parser/state/dashboard modules — none of which are needed for non-PM commands.

**Argparse dash-to-underscore**: argparse converts `--model-implications` to `args.model_implications` automatically (dashes become underscores in the namespace). This aligns with Python function parameter names.

**Keyword-passing convention**: All operation args are passed as keyword arguments via `_dispatch(args, fn, **kwargs)`, including `close_item`'s `wi_id` which is positional in the function signature (`close_item(project_root, wi_id)`). This works in Python (positional args can be passed by name) and keeps the dispatch pattern uniform across all 14 operations.

### Component 5: Special Dispatch Cases

Three operations need special handling beyond the `_dispatch` pattern:

#### `impact-query` — returns `ImpactResult`, not `OperationResult`

```python
def cmd_pm_impact_query(args: argparse.Namespace) -> int:
    from agentic_mbse.cli import find_project_root
    from agentic_mbse.pm.operations import impact_query

    project_root = find_project_root()
    if project_root is None:
        print("Error: Not inside a project (no work/BACKLOG.md found)", file=sys.stderr)
        return EXIT_FAILURE

    result = impact_query(project_root, query_id=args.query_id)
    _print_warnings(result.warnings)

    # Format ImpactResult as readable output
    if not result.affected_elements:
        print(f"No traced elements found for {result.query_id}")
    else:
        print(f"Impact analysis for {result.query_id}:")
        print(f"  Affected elements: {len(result.affected_elements)}")
        for elem in result.affected_elements:
            print(f"    - {elem.element} ({elem.file})")
    return EXIT_SUCCESS
```

#### `save-research` — reads content from file

```python
EXIT_USAGE = 2  # defined once at module level in pm_cli.py

def cmd_pm_save_research(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.operations import save_research

    content_path = Path(args.content_file)
    if not content_path.exists():
        print(f"Error: Content file not found: {content_path}", file=sys.stderr)
        return EXIT_USAGE
    content = content_path.read_text(encoding="utf-8")

    return _dispatch(args, save_research, topic=args.topic, content=content)
```

#### JSON argument operations — parse + validate before dispatch

A shared helper validates JSON args and Pydantic models, returning an exit code on failure instead of calling `sys.exit()`:

```python
def _validate_json_list(raw_json: str, label: str, model_cls: type[BaseModel]) -> tuple[list | None, int | None]:
    """Parse JSON string, validate as list of Pydantic models.

    Returns (validated_list, None) on success, or (None, exit_code) on failure.
    """
    parsed, err = _parse_json_arg(raw_json, label)
    if err is not None:
        print(f"Error: {err}", file=sys.stderr)
        return None, EXIT_USAGE
    if not isinstance(parsed, list):
        print(f"Error: {label} must be a JSON array", file=sys.stderr)
        return None, EXIT_USAGE
    try:
        validated = [model_cls.model_validate(item) for item in parsed]
    except Exception as e:
        print(f"Error: Invalid {label} data: {e}", file=sys.stderr)
        return None, EXIT_USAGE
    return validated, None


def cmd_pm_approve_research(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.operations import approve_research
    from agentic_mbse.pm.types import InsightInput

    insights, err = _validate_json_list(args.insights, "--insights", InsightInput)
    if err is not None:
        return err

    return _dispatch(args, approve_research,
        pending_file=args.file,
        insights=insights,
    )
```

The same `_validate_json_list` pattern applies to `register-intent` (goals/questions) and `supersede-insight` (new_insight). All error paths return exit codes — no `sys.exit()` anywhere in dispatch functions.

#### `supersede-insight` — stub operation

The D4.4 design specifies `supersede_insight` raises `NotImplementedError`. The CLI handler catches this and prints a user-friendly message:

```python
def cmd_pm_supersede_insight(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.operations import supersede_insight

    # ... parse JSON args via _validate_json_list ...
    try:
        return _dispatch(args, supersede_insight,
            old_id=args.old_id,
            new_insight=new_insight_data,
            reason=args.reason,
        )
    except NotImplementedError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_FAILURE
```

### Component 6: Status Subcommand (`cli/__init__.py`)

The `status` subcommand is registered directly in `main()` (not in `pm_cli.py`) since it's a top-level command, not under `pm`:

```python
# In main():
status_parser = subparsers.add_parser(
    "status",
    help="Show project status dashboard",
)
status_parser.add_argument(
    "--json",
    action="store_true",
    dest="json_output",
    help="Output as JSON instead of markdown",
)
status_parser.set_defaults(func=cmd_status)
```

The handler imports `_print_warnings` from `pm_cli` to share the warning-printing logic:

```python
def cmd_status(args: argparse.Namespace) -> int:
    """Show project status dashboard."""
    from agentic_mbse.cli.pm_cli import _print_warnings

    project_root = find_project_root()
    if project_root is None:
        print("Error: Not inside a project (no work/BACKLOG.md found)", file=sys.stderr)
        return EXIT_FAILURE

    if args.json_output:
        from agentic_mbse.pm.state import derive_project_state
        from agentic_mbse.pm.parser import parse_requirements, parse_validation_matrix
        import json

        warnings = []
        state_result = derive_project_state(project_root)
        warnings.extend(state_result.warnings)
        req_result = parse_requirements(project_root / "modeling_project" / "REQUIREMENTS.md")
        warnings.extend(req_result.warnings)
        val_result = parse_validation_matrix(project_root / "modeling_project" / "VALIDATION_MATRIX.md")
        warnings.extend(val_result.warnings)

        _print_warnings(warnings)

        output = {
            "project": project_root.name,
            "state": state_result.data.model_dump(mode="json"),
            "requirements": [r.model_dump(mode="json") for r in req_result.data],
            "validation": [v.model_dump(mode="json") for v in val_result.data],
        }
        print(json.dumps(output, indent=2))
    else:
        from agentic_mbse.pm.dashboard import generate_dashboard

        result = generate_dashboard(project_root)
        _print_warnings(result.warnings)
        print(result.markdown)

    return EXIT_SUCCESS
```

**JSON mode** calls parsers directly to get structured data rather than serializing the markdown string. This is more useful for programmatic consumers — they get `ProjectState` with epic/item details, requirement entries, and validation entries as structured JSON. JSON mode skips `generate_dashboard()` entirely to avoid duplicate parser calls.

### Component 7: Integration in `main()` (`cli/__init__.py`)

Minimal changes to `main()`:

```python
from agentic_mbse.cli.pm_cli import register_pm_subcommands

def main() -> int:
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ... existing validate, init, install-commands ...

    # status command (top-level)
    status_parser = subparsers.add_parser("status", help="Show project status dashboard")
    status_parser.add_argument("--json", action="store_true", dest="json_output",
                               help="Output as JSON instead of markdown")
    status_parser.set_defaults(func=cmd_status)

    # pm command group (delegated to pm_cli module)
    register_pm_subcommands(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS

    return args.func(args)
```

The `register_pm_subcommands` import is at module level (not lazy) since it only imports the registration function, not the PM library. The actual PM imports happen lazily inside dispatch functions.

**Handling missing `operation` in `pm`**: When `agentic-mbse pm` is called with no operation, `args.operation` will be `None` and `args.func` won't be set. The existing `if not args.command` check won't catch this since `args.command` is `"pm"`. We need to handle the `pm` no-operation case:

```python
# In register_pm_subcommands:
def cmd_pm_no_operation(args: argparse.Namespace) -> int:
    # This is set as the default func for the pm parser itself
    # It triggers when 'agentic-mbse pm' is called with no operation
    print("Error: No operation specified. Run 'agentic-mbse pm --help' for available operations.",
          file=sys.stderr)
    return EXIT_USAGE

pm_parser.set_defaults(func=cmd_pm_no_operation)
```

This ensures `agentic-mbse pm` (no operation) exits 2 with a helpful message, matching the spec's FR-3.

### Component 8: File Layout Summary

```
src/agentic_mbse/
├── cli/
│   ├── __init__.py        # Modified: add find_project_root(), cmd_status(), register_pm call
│   └── pm_cli.py          # NEW: register_pm_subcommands(), 14 cmd_pm_* handlers, _dispatch()
└── pm/
    ├── __init__.py         # Modified: export new types from D4.4 (OperationResult, etc.)
    ├── types.py            # Modified by D4.4: OperationResult, ImpactResult, InsightInput, etc.
    ├── operations.py       # Created by D4.4: 14 operation functions
    ├── parser.py           # Unchanged
    ├── state.py            # Unchanged
    └── dashboard.py        # Unchanged
```

D4.5 creates one new file (`pm_cli.py`) and modifies one existing file (`cli/__init__.py`). The `pm/` module changes are D4.4's responsibility.

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| D4.4 not complete when D4.5 is implemented | Medium | CLI handlers use lazy imports. The argument parsing and dispatch structure can be built and tested independently. Tests mock the operations. |
| argparse nested subparsers (sub-sub-commands) have quirks | Low | Well-documented pattern. The `dest="operation"` + `set_defaults(func=...)` approach works reliably. Test with `--help` at each level. |
| JSON argument quoting issues in shell | Medium | Agents wrap JSON in single quotes. Document in `--help` text: `--insights '[{"title": "..."}]'`. Test with various shell quoting scenarios. |
| `find_project_root()` false positives | Low | `work/BACKLOG.md` is a specific enough marker. Fallback to `.claude/` handles edge cases (fresh init before BACKLOG.md exists). |
| Exit code 2 vs 1 boundary | Low | Clear convention: argparse errors → 2 (automatic), JSON/usage errors → `EXIT_USAGE` (returned, never `sys.exit()`), operation failures → `EXIT_FAILURE` (from `result.success`). All handlers return int, consistent with existing pattern. |

---

## Integration Strategy

**D4.4 dependency**: D4.5 imports from `agentic_mbse.pm.operations` which D4.4 creates. Both deliverables target the same branch (`revamp-architecture`). Implementation order: D4.4 first (or in parallel with D4.5 using mocked operations for testing).

**Epic 3 integration**: Commands call operations via `agentic-mbse pm <name> ...` shell invocations. The CLI is the interface boundary. Commands never import `operations.py` directly — they always go through the CLI.

**Existing CLI**: The `validate`, `init`, and `install-commands` subcommands are unchanged. The `status` and `pm` subcommands are additive.

---

## Validation Approach

### Testing Strategy

Test file: `tests/test_pm_cli.py`

**Unit tests** (mock operations, test argument parsing and dispatch):
- Each operation's argument parsing (required args present, optional args default correctly)
- JSON argument parsing (valid JSON, invalid JSON → exit 2, wrong structure → exit 2)
- Project root detection (found, not found → exit 1)
- Exit code mapping (`result.success=True` → 0, `result.success=False` → 1)
- Warnings printed to stderr

**Integration tests** (with temp directory project structure):
- `agentic-mbse status` end-to-end (empty project, populated project)
- `agentic-mbse status --json` produces valid JSON
- `agentic-mbse pm close-item WI-001` end-to-end (requires D4.4 operations)
- `agentic-mbse pm --help` lists all operations
- `agentic-mbse pm` with no operation → exit 2

**Test approach**: Follow existing pattern in `test_cli.py` — `MockArgs` class for unit tests, `subprocess.run` for integration tests. CLI integration tests can use `tmp_path` fixtures with minimal project structures.

### Success Criteria

All spec acceptance criteria met. All existing tests pass (`uv run pytest tests/`).

---

**Next Step:** After approval → `/_my_plan` (implementation is structured enough that a plan helps track the per-operation wiring)
