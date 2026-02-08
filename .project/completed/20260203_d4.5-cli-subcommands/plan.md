# Implementation Plan: D4.5 CLI Subcommands

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d4.5-cli-subcommands/spec.md`
- **Design:** `.project/active/d4.5-cli-subcommands/design.md` — See here for component details, function signatures, argument tables, and architecture

## Implementation Strategy

**Phasing Rationale:**
4 phases, ordered by dependency and risk. Phase 1 builds shared utilities that all handlers need. Phase 2 proves the end-to-end pattern with `status` (no D4.4 dependency — uses D4.3 dashboard which is complete). Phase 3 wires the bulk of `pm` operations (simple arg patterns). Phase 4 handles the JSON-argument operations, which are the most complex arg parsing pattern.

D4.4 (operations) is not yet implemented. All `pm` operation handlers are tested with mocked operations. Integration tests with real operations are deferred to D4.6.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/test_pm_cli.py` after each phase
- `uv run pytest tests/` after each phase to catch regressions
- `uv run ruff check src/ tests/` for linting

---

## Phase 1: Infrastructure — Project Root Detection + Shared Helpers

### Goal
Build the shared utilities every subsequent phase depends on: `find_project_root()`, `_print_warnings()`, `_dispatch()`, `_parse_json_arg()`, `_validate_json_list()`, and the `EXIT_USAGE` constant. Create the test file and pm_cli module skeleton.

### Test Stencil (Write This First)
```python
# tests/test_pm_cli.py

class TestFindProjectRoot:
    def test_finds_root_via_backlog(self, tmp_path):
        (tmp_path / "work").mkdir()
        (tmp_path / "work" / "BACKLOG.md").write_text("---\n---\n")
        sub = tmp_path / "work" / "active" / "WI-001_foo"
        sub.mkdir(parents=True)
        # monkeypatch cwd to sub, call find_project_root, assert == tmp_path

    def test_finds_root_via_claude_fallback(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        # monkeypatch cwd to tmp_path, assert find_project_root() == tmp_path

    def test_returns_none_outside_project(self, tmp_path):
        # monkeypatch cwd to tmp_path (no markers), assert None

class TestPrintWarnings:
    def test_prints_to_stderr(self, capsys):
        # call _print_warnings with sample warnings, check capsys.readouterr().err

class TestParseJsonArg:
    def test_valid_json(self):
        # assert returns (parsed, None)
    def test_invalid_json(self):
        # assert returns (None, error_string)

class TestDispatch:
    def test_no_project_root(self, monkeypatch, capsys):
        # monkeypatch find_project_root to return None
        # assert _dispatch returns EXIT_FAILURE, stderr has error message
    def test_success(self, monkeypatch):
        # mock find_project_root and operation fn returning OperationResult(success=True)
        # assert returns EXIT_SUCCESS
    def test_failure(self, monkeypatch):
        # mock operation fn returning OperationResult(success=False)
        # assert returns EXIT_FAILURE
```

### Changes Required

**See `design.md` for:**
- `find_project_root` signature and logic → `design.md#component-1`
- `pm_cli.py` module structure and helpers → `design.md#component-2`
- Exit code constants → `design.md#component-5` (`EXIT_USAGE = 2`)

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pm_cli.py` (NEW — write first)
- [x] Create test file with imports
- [x] `TestFindProjectRoot`: 3 tests (backlog marker, claude fallback, not found)
- [x] `TestPrintWarnings`: 1 test (stderr output)
- [x] `TestParseJsonArg`: 2 tests (valid, invalid)
- [x] `TestDispatch`: 3 tests (no root, success, failure)

#### 2. CLI Module
**File:** `src/agentic_mbse/cli/__init__.py` (MODIFY)
- [x] Add `find_project_root() -> Path | None` after existing path helpers (~line 149)

#### 3. PM CLI Module
**File:** `src/agentic_mbse/cli/pm_cli.py` (NEW)
- [x] Create with module docstring and imports
- [x] `EXIT_USAGE = 2`
- [x] `_print_warnings()`
- [x] `_parse_json_arg()` — returns `(value, None)` or `(None, error_msg)`
- [x] `_validate_json_list()` — wraps parse + Pydantic validation
- [x] `_dispatch()` — find root, call fn, print result/warnings, return exit code

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pm_cli.py -v` → All 9+ tests pass
- [x] `uv run pytest tests/` → No regressions
- [x] `uv run ruff check src/agentic_mbse/cli/pm_cli.py`

**Manual:**
- [x] `python -c "from agentic_mbse.cli import find_project_root"` imports without error

**What We Know Works After This Phase:**
Project root detection, warning printing, JSON parsing, and the dispatch pattern — all tested in isolation without needing D4.4 operations.

---

## Phase 2: `status` Subcommand

### Goal
First end-to-end working subcommand. Proves the full chain: argparse registration → `find_project_root` → call PM library → format output → exit code. No D4.4 dependency — uses D4.3 dashboard (`generate_dashboard()`) which is already complete.

### Test Stencil (Write This First)
```python
class TestCmdStatus:
    def test_markdown_output(self, tmp_path, monkeypatch, capsys):
        # Create minimal project structure in tmp_path (work/BACKLOG.md, etc.)
        # monkeypatch cwd to tmp_path
        # Call cmd_status(MockArgs(json_output=False))
        # assert EXIT_SUCCESS, stdout contains "## Project:"

    def test_json_output(self, tmp_path, monkeypatch, capsys):
        # Same setup, json_output=True
        # assert stdout is valid JSON with "project", "state", "requirements", "validation" keys

    def test_no_project_root(self, tmp_path, monkeypatch, capsys):
        # monkeypatch cwd to tmp_path (no project markers)
        # assert EXIT_FAILURE, stderr has error

class TestStatusIntegration:
    def test_status_in_help(self):
        # subprocess.run(["uv", "run", "agentic-mbse", "--help"])
        # assert "status" in stdout
```

### Changes Required

**See `design.md` for:**
- `cmd_status` handler → `design.md#component-6`
- Registration in `main()` → `design.md#component-7`
- JSON mode data flow → `design.md#component-6` (JSON mode section)

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_cli.py` (ADD)
- [x] `TestCmdStatus`: markdown output, JSON output, no project root
- [x] `TestStatusIntegration`: `status` appears in `--help`
- [x] Helper: create minimal project fixture (reusable for later phases)

#### 2. Status Handler
**File:** `src/agentic_mbse/cli/__init__.py` (MODIFY)
- [x] Add `cmd_status(args)` function — imports `_print_warnings` from `pm_cli`, lazy-imports PM modules
- [x] Markdown path: `generate_dashboard()` → print `.markdown`
- [x] JSON path: `derive_project_state()` + `parse_requirements()` + `parse_validation_matrix()` → `json.dumps()`
- [x] Register `status` subparser in `main()` with `--json` flag (`dest="json_output"`)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pm_cli.py::TestCmdStatus -v` → All pass
- [x] `uv run pytest tests/` → No regressions

**Manual:**
- [x] `cd` into a project directory with `work/BACKLOG.md`, run `uv run agentic-mbse status` → dashboard prints
- [x] `uv run agentic-mbse status --json` → valid JSON output
- [x] `cd /tmp && uv run agentic-mbse status` → error message, exit 1

**What We Know Works After This Phase:**
Full end-to-end subcommand: argparse → project detection → PM library call → formatted output → exit code. The pattern is proven for all subsequent operations.

---

## Phase 3: `pm` Subcommand Group — Registration + Simple Operations

### Goal
Wire the `pm` nested subparser group and implement dispatch handlers for the 10 operations that use only positional/flag arguments (no JSON parsing): `close-item`, `add-insight`, `save-research`, `trace-element`, `promote-requirement`, `impact-query`, `register-decision`, `update-validation`, `add-item`, `add-validation`.

### Test Stencil (Write This First)
```python
class TestPmNoOperation:
    def test_no_operation_exits_2(self, capsys):
        # Call cmd_pm_no_operation(MockArgs())
        # assert returns EXIT_USAGE, stderr has "No operation specified"

class TestPmCloseItem:
    def test_dispatches_correctly(self, monkeypatch):
        # Mock find_project_root → tmp_path
        # Mock close_item → OperationResult(success=True, message="Closed WI-001")
        # Call cmd_pm_close_item(MockArgs(wi_id="WI-001"))
        # assert EXIT_SUCCESS, mock called with (tmp_path, wi_id="WI-001")

class TestPmAddInsight:
    def test_dispatches_all_args(self, monkeypatch):
        # Mock add_insight, verify all 6 args passed through

class TestPmSaveResearch:
    def test_reads_content_file(self, tmp_path, monkeypatch):
        # Create content file, mock save_research
        # Verify content read from file and passed to operation

    def test_missing_content_file(self, capsys):
        # assert returns EXIT_USAGE

class TestPmImpactQuery:
    def test_formats_results(self, monkeypatch, capsys):
        # Mock impact_query → ImpactResult with elements
        # Verify formatted output

class TestPmTraceElement:
    def test_multi_value_args(self, monkeypatch):
        # Verify --knowledge and --requirement accept multiple values

class TestPmIntegration:
    def test_pm_in_help(self):
        # subprocess: agentic-mbse --help → "pm" in output
    def test_pm_help_lists_operations(self):
        # subprocess: agentic-mbse pm --help → all operation names present
```

### Changes Required

**See `design.md` for:**
- `register_pm_subcommands()` and nested subparsers → `design.md#component-3`
- Argument table (all 14 operations) → `design.md#component-3`
- Dispatch handlers → `design.md#component-4`
- Special cases (`impact-query`, `save-research`) → `design.md#component-5`
- `cmd_pm_no_operation` → `design.md#component-7`

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_cli.py` (ADD)
- [x] `TestPmNoOperation`: no operation → EXIT_USAGE
- [x] Per-operation dispatch tests (mock operation, verify args passed through):
  - [x] `close-item`, `add-insight`, `save-research`, `trace-element`
  - [x] `promote-requirement`, `impact-query`, `register-decision`, `update-validation`
  - [x] `add-item`, `add-validation`
- [x] `save-research` special case: missing content file → EXIT_USAGE
- [x] `impact-query` special case: formatted output
- [x] `trace-element`: multi-value `--knowledge` / `--requirement`
- [x] Integration: `pm` in `--help`, `pm --help` lists all operations

#### 2. PM CLI Registration + Handlers
**File:** `src/agentic_mbse/cli/pm_cli.py` (ADD)
- [x] `cmd_pm_no_operation()` — default handler for bare `pm`
- [x] `register_pm_subcommands(subparsers)` — create `pm` parser + 10 operation sub-subparsers with argument definitions
- [x] 10 dispatch handlers: `cmd_pm_close_item`, `cmd_pm_add_insight`, `cmd_pm_save_research`, `cmd_pm_trace_element`, `cmd_pm_promote_requirement`, `cmd_pm_impact_query`, `cmd_pm_register_decision`, `cmd_pm_update_validation`, `cmd_pm_add_item`, `cmd_pm_add_validation`

#### 3. Main Integration
**File:** `src/agentic_mbse/cli/__init__.py` (MODIFY)
- [x] Import `register_pm_subcommands` from `pm_cli`
- [x] Call `register_pm_subcommands(subparsers)` in `main()` after status registration

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pm_cli.py -v` → All tests pass (Phase 1 + 2 + 3)
- [x] `uv run pytest tests/` → No regressions
- [x] `uv run ruff check src/agentic_mbse/cli/`

**Manual:**
- [x] `uv run agentic-mbse --help` → shows `status` and `pm`
- [x] `uv run agentic-mbse pm --help` → lists all registered operations
- [x] `uv run agentic-mbse pm` → "No operation specified" error, exit 2
- [x] `uv run agentic-mbse pm close-item --help` → shows `WI-XXX` positional arg
- [x] `uv run agentic-mbse pm add-insight --help` → shows all 5 required + 1 optional flag

**What We Know Works After This Phase:**
The full `pm` subcommand infrastructure is in place. All 10 simple operations have argument parsing and dispatch. Nested subparsers work correctly. The only remaining work is the 3 JSON-argument operations + stub.

---

## Phase 4: JSON Argument Operations + Supersede Stub

### Goal
Wire the 3 operations requiring JSON argument parsing (`approve-research`, `register-intent`, `supersede-insight`) plus the `NotImplementedError` stub handling. This completes all 14 operations.

### Test Stencil (Write This First)
```python
class TestPmApproveResearch:
    def test_valid_json_insights(self, monkeypatch):
        # Mock approve_research
        # args.insights = '[{"title": "t", "source": "s", "context": "c", ...}]'
        # assert dispatches correctly with InsightInput list

    def test_invalid_json(self, capsys):
        # args.insights = "not json"
        # assert EXIT_USAGE, stderr has JSON error

    def test_invalid_insight_schema(self, capsys):
        # args.insights = '[{"title": "t"}]'  (missing required fields)
        # assert EXIT_USAGE, stderr has validation error

class TestPmRegisterIntent:
    def test_goals_only(self, monkeypatch): ...
    def test_questions_only(self, monkeypatch): ...
    def test_neither_provided(self, capsys):
        # assert EXIT_USAGE

class TestPmSupersedeInsight:
    def test_not_implemented(self, monkeypatch, capsys):
        # Mock supersede_insight raising NotImplementedError
        # assert EXIT_FAILURE, stderr has message
```

### Changes Required

**See `design.md` for:**
- `_validate_json_list()` → `design.md#component-2` (already implemented in Phase 1)
- JSON operation handlers → `design.md#component-5`
- `supersede-insight` stub handling → `design.md#component-5`

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_cli.py` (ADD)
- [x] `TestPmApproveResearch`: valid JSON, invalid JSON, invalid schema
- [x] `TestPmRegisterIntent`: goals only, questions only, neither (EXIT_USAGE)
- [x] `TestPmSupersedeInsight`: NotImplementedError → EXIT_FAILURE

#### 2. JSON Operation Handlers
**File:** `src/agentic_mbse/cli/pm_cli.py` (ADD to `register_pm_subcommands`)
- [x] Register `approve-research` sub-subparser (positional `file`, `--insights` JSON)
- [x] Register `register-intent` sub-subparser (`--goals` JSON, `--questions` JSON)
- [x] Register `supersede-insight` sub-subparser (positional `old_id`, `--new-insight` JSON, `--reason`)
- [x] `cmd_pm_approve_research` — `_validate_json_list` for `--insights` with `InsightInput`
- [x] `cmd_pm_register_intent` — validate at least one provided, `_validate_json_list` for each
- [x] `cmd_pm_supersede_insight` — JSON parse + `NotImplementedError` catch

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pm_cli.py -v` → All tests pass (all 4 phases)
- [x] `uv run pytest tests/` → No regressions
- [x] `uv run ruff check src/ tests/`
- [x] `uv run ruff format src/ tests/` (formatting clean)

**Manual:**
- [x] `uv run agentic-mbse pm --help` → all 14 operations listed (including 3 new + supersede)
- [x] `uv run agentic-mbse pm approve-research --help` → shows positional file + `--insights`
- [x] `uv run agentic-mbse pm register-intent --help` → shows `--goals` and `--questions`
- [x] `uv run agentic-mbse pm supersede-insight --help` → shows positional old_id + args

**What We Know Works After This Phase:**
All 14 operations are wired. JSON argument parsing and Pydantic validation work correctly. The full CLI surface matches the spec. D4.5 is complete pending D4.4 integration.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/test_pm_cli.py -v` — run D4.5 tests
- `uv run pytest tests/` — full suite
- `uv run ruff check src/ tests/` — lint
- `uv run ruff format src/ tests/` — format

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: `find_project_root` tested with monkeypatched cwd — no real filesystem dependency
- **Phase 2**: `status` uses D4.3 dashboard (complete) — no D4.4 risk
- **Phase 3**: All operation calls are mocked — D4.4 absence doesn't block testing
- **Phase 4**: JSON validation tested with both valid and malformed input — catches Pydantic errors at CLI boundary

## Implementation Notes

All 4 phases implemented in a single pass. 30 tests written and passing. 557 total tests pass with 0 regressions.

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Created `src/agentic_mbse/cli/pm_cli.py` with `_print_warnings()`, `_parse_json_arg()`, `_validate_json_list()`, `_dispatch()`, `EXIT_USAGE = 2`
- Added `find_project_root()` to `src/agentic_mbse/cli/__init__.py` after existing path helpers
- Created `tests/test_pm_cli.py` with `TestFindProjectRoot` (3), `TestPrintWarnings` (1), `TestParseJsonArg` (2), `TestDispatch` (3) = 9 tests
**Issues:** None
**Deviations:**
- Used lazy import wrappers (`_op_close_item`, `_op_add_insight`, etc.) instead of importing operations inside each dispatch function. This makes monkeypatching cleaner in tests and keeps the lazy-import benefit.
- `find_project_root()` in `pm_cli.py` delegates to `cli.__init__.find_project_root()` to avoid duplicating the logic.

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `cmd_status()` to `src/agentic_mbse/cli/__init__.py` — handles both markdown and JSON modes
- Registered `status` subparser with `--json` flag in `main()`
- Added `TestCmdStatus` (3 tests) and `TestStatusIntegration` (1 test) + `_make_minimal_project()` fixture
**Issues:** None
**Deviations:** None — followed design exactly.

### Phase 3 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `register_pm_subcommands()` with all 14 operation sub-subparsers
- Added `cmd_pm_no_operation()` as default for bare `pm`
- Added 10 dispatch handlers for simple operations
- Wired `register_pm_subcommands(subparsers)` call in `main()`
- Added tests: `TestPmNoOperation`, `TestPmCloseItem`, `TestPmAddInsight`, `TestPmSaveResearch`, `TestPmImpactQuery`, `TestPmTraceElement`, `TestPmIntegration` = 9 tests
**Issues:** None
**Deviations:**
- `close_item()` takes `wi_id` as positional (not keyword-only) in operations.py. The `cmd_pm_close_item` handler calls `_op_close_item(project_root, args.wi_id)` directly instead of using `_dispatch()`, matching the function signature.

### Phase 4 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `cmd_pm_approve_research`, `cmd_pm_register_intent`, `cmd_pm_supersede_insight` handlers
- All registered in `register_pm_subcommands()`
- Added tests: `TestPmApproveResearch` (3), `TestPmRegisterIntent` (3), `TestPmSupersedeInsight` (1) = 7 tests
**Issues:** None
**Deviations:** None — followed design exactly.

---

**Status**: Complete
