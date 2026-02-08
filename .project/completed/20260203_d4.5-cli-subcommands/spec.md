# Spec: D4.5 CLI Subcommands

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (Architecture Redesign — PM Script Engine)

---

## Business Goals

### Why This Matters

D4.5 is the interface boundary between agent-driven commands (Epic 3) and deterministic PM functions (D4.3 + D4.4). Without CLI subcommands, the 14 AP-7 operations and the dashboard are library-only — MBSE commands cannot call them. Every `/implement-model`, `/backlog`, `/status`, `/research`, and `/audit-models` invocation routes through `agentic-mbse pm <operation>` to ensure structured mutations are deterministic and testable.

This deliverable wires existing library code into the CLI. The operations and dashboard are already designed (D4.4) or built (D4.3). D4.5 adds argument parsing, project root detection, error reporting, and help text — the thin shell layer that makes library functions callable from agent commands.

### Success Criteria

- [ ] `agentic-mbse status` prints a markdown dashboard from any directory within a project
- [ ] `agentic-mbse status --json` prints machine-readable dashboard output
- [ ] `agentic-mbse pm <operation>` works for all 14 operations with correct argument parsing
- [ ] Exit codes are consistent: 0 = success, 1 = operation error, 2 = usage error
- [ ] `--help` text is clear for each subcommand and sub-subcommand
- [ ] Warnings go to stderr, results go to stdout

### Priority

P0 — blocks Epic 3 command integration. On the critical path for the architecture redesign.

---

## Problem Statement

### Current State

D4.1 (parsers), D4.2 (state derivation), and D4.3 (dashboard) are complete. D4.4 (operations) is in progress — spec and design are done, implementation is next. The `agentic-mbse` CLI currently has three subcommands: `validate`, `init`, and `install-commands`. There is no way to invoke PM operations or the dashboard from the command line.

### Desired Outcome

Two new CLI entry points:
- `agentic-mbse status [--json]` — dashboard output
- `agentic-mbse pm <operation> [args]` — all 14 AP-7 operations

Both share a project root detection mechanism that walks up from CWD.

---

## Scope

### In Scope

- `status` subcommand with `--json` flag
- `pm` subcommand group with 14 operation sub-subcommands
- Project root detection (walk up from CWD to find `work/BACKLOG.md`)
- Argument parsing for each operation (positional IDs, named flags, JSON string arguments)
- Exit code conventions (0/1/2)
- Stdout/stderr separation (results vs warnings)
- Help text for all subcommands

### Out of Scope

- The operations themselves (D4.4)
- Dashboard generation logic (D4.3)
- CLI integration tests (D4.6)
- Command prompts or skill changes (Epic 3)
- `--json` on individual `pm` operations (YAGNI — agents parse natural language trivially; add if a programmatic consumer emerges)
- Changes to existing `validate`, `init`, or `install-commands` subcommands

### Edge Cases & Considerations

- **Project root not found**: Walk up from CWD fails to find `work/BACKLOG.md` or `.claude/`. Print clear error and exit 1.
- **Operations called outside a project**: Same as above — detect and report before dispatching.
- **JSON argument parsing failures**: `--insights`, `--goals`, `--questions` accept JSON strings. Invalid JSON should produce a clear error (exit 2, not 1 — it's a usage error).
- **Long string arguments**: `save-research --content-file <path>` uses file paths, not inline content, to avoid shell argument length limits.
- **Missing operations.py**: Until D4.4 is implemented, the CLI wiring exists but operations aren't callable. This is acceptable — D4.5 and D4.4 will be integrated in the same branch.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic (D4.5 section) and D4.4 design doc unless marked [INFERRED].

#### FR-1: Project Root Detection

A shared utility MUST find the project root by walking up from CWD, looking for `work/BACKLOG.md` as the primary marker. If not found, fall back to looking for `.claude/`. If neither is found, print an error to stderr and exit 1.

Both `status` and `pm` subcommands use this before dispatching to library functions.

[INFERRED] This utility belongs in the CLI module (not the PM module) since it's a CLI concern — the PM library functions take `project_root: Path` explicitly.

#### FR-2: `status` Subcommand

```
agentic-mbse status [--json]
```

- Default: print markdown dashboard to stdout (from `generate_dashboard()` or `get_status()`)
- `--json`: print JSON representation to stdout (from `DashboardResult` serialization)
- Warnings from partial parse go to stderr
- Exit 0 on success, exit 1 if project root not found or dashboard generation fails

#### FR-3: `pm` Subcommand Group

```
agentic-mbse pm <operation> [args]
```

The `pm` subcommand uses nested sub-subcommands (argparse sub-parsers). Each operation is a separate sub-subcommand with its own argument definition. Running `agentic-mbse pm` with no operation prints usage/help (exit 2).

#### FR-4: Operation Argument Definitions

Each operation sub-subcommand MUST define arguments matching the D4.4 design function signatures. The CLI parses arguments and calls the corresponding `operations.py` function with typed Python values.

| Operation | CLI Syntax | Notes |
|-----------|-----------|-------|
| `close-item` | `agentic-mbse pm close-item <WI-XXX>` | Positional WI ID |
| `add-insight` | `agentic-mbse pm add-insight --title <text> --source <text> --context <text> --model-implications <text> --analysis-implications <text> [--rationale <text>]` | 5 required, 1 optional |
| `save-research` | `agentic-mbse pm save-research --topic <kebab-case> --content-file <path>` | File path only, no stdin |
| `approve-research` | `agentic-mbse pm approve-research <file> --insights '<json>'` | Positional file path, JSON string |
| `trace-element` | `agentic-mbse pm trace-element --element <name> --file <path> --type <kind> [--knowledge <DI-XXX>...] [--requirement <PR-XXX>...] [--source-type <type>] [--source-doc <name>] [--source-location <loc>] [--confidence <value>] [--assumptions <text>]` | 3 required, rest optional; `--knowledge` and `--requirement` accept multiple values |
| `promote-requirement` | `agentic-mbse pm promote-requirement --requirement <text> --source <ID> --enforcement <method> --validation-method <method>` | All 4 required |
| `impact-query` | `agentic-mbse pm impact-query <ID>` | Positional DI-XXX or PR-XXX |
| `register-decision` | `agentic-mbse pm register-decision --title <text> --decision <text> --rationale <text>` | All 3 required |
| `update-validation` | `agentic-mbse pm update-validation <SV-XXX> --status <status>` | Positional SV ID + required status |
| `register-intent` | `agentic-mbse pm register-intent [--goals '<json>'] [--questions '<json>']` | At least one required; JSON strings |
| `add-item` | `agentic-mbse pm add-item --name <name> --scale <trivial\|standard> --priority <P0\|P1\|P2\|P3> [--epic <epic-name>] [--goal <G-XXX>]` | 3 required, 2 optional |
| `add-validation` | `agentic-mbse pm add-validation --description <text> --type <type> --mechanism <mechanism> --expected <value> --tolerance <tolerance> [--source <text>] [--test <text>]` | 5 required, 2 optional |
| `supersede-insight` | `agentic-mbse pm supersede-insight <DI-XXX> --new-insight '<json>' --reason <text>` | Positional old ID, JSON + text |

#### FR-5: Exit Code Conventions

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Operation completed, dashboard rendered |
| 1 | Operation error | Validation failure, file not found, ID not found, atomicity failure |
| 2 | Usage error | Bad arguments, missing required args, invalid JSON, no operation specified |

Exit 2 is the argparse default for usage errors. Exit 1 is returned when `OperationResult.success` is False.

#### FR-6: Output Conventions

- **Stdout**: Operation result — `OperationResult.message` for mutations, markdown dashboard for `status`, `ImpactResult` formatted as markdown for `impact-query`
- **Stderr**: Warnings from parser read phase (`OperationResult.warnings`, `DashboardResult.warnings`) and CLI-level errors (project root not found, invalid JSON)

#### FR-7: JSON Argument Parsing

Operations that accept JSON arguments (`--insights`, `--goals`, `--questions`, `--new-insight`) MUST:
1. Accept the argument as a string
2. Parse with `json.loads()`
3. Validate against the expected Pydantic model (`InsightInput`, `GoalInput`, `QuestionInput`)
4. On parse failure: print error to stderr, exit 2 (usage error, not operation error)

#### FR-8: Dispatch Pattern

[INFERRED] Each operation sub-subcommand sets a `func` default that points to a thin dispatch function. The dispatch function:
1. Detects project root (FR-1)
2. Extracts and converts arguments from `argparse.Namespace`
3. Calls the corresponding `operations.py` function
4. Prints `result.message` to stdout
5. Prints warnings to stderr (if any)
6. Returns exit code based on `result.success`

This follows the established pattern in the existing CLI (`cmd_validate`, `cmd_init`, `cmd_install_commands` each set via `parser.set_defaults(func=...)`).

#### FR-9: Operation Name Convention

CLI operation names use kebab-case (`close-item`, `add-insight`). Python function names use snake_case (`close_item`, `add_insight`). The CLI translates between the two.

The operation name `add-item` is the sole canonical name. No alias for `add-to-backlog`. The `/backlog` command (Epic 3) SHOULD reference `agentic-mbse pm add-item` when finalized.

### Non-Functional Requirements

- **NF-1**: The CLI layer MUST NOT contain business logic. It parses arguments, calls library functions, and formats output.
- **NF-2**: The CLI layer MUST follow the existing argparse pattern in `cli/__init__.py` (subparsers, `set_defaults(func=...)`, exit code return).
- **NF-3**: All `--help` text MUST be sufficient for an agent to construct a correct invocation without external documentation.
- **NF-4**: The `pm` subcommand group SHOULD be implemented in a separate function or file to keep `cli/__init__.py` manageable, given that 14 sub-subcommands with arguments will add significant line count.

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse status` prints markdown dashboard to stdout
- [ ] `agentic-mbse status --json` prints JSON dashboard to stdout
- [ ] `agentic-mbse pm close-item WI-001` calls `close_item()` and prints result
- [ ] `agentic-mbse pm add-insight --title "..." --source "..." --context "..." --model-implications "..." --analysis-implications "..."` calls `add_insight()` and prints assigned DI-XXX
- [ ] `agentic-mbse pm save-research --topic "topic-name" --content-file /path/to/file` calls `save_research()` with file content
- [ ] `agentic-mbse pm impact-query DI-001` calls `impact_query()` and prints affected elements
- [ ] All 14 operations have working CLI sub-subcommands with correct argument parsing
- [ ] `agentic-mbse pm` with no operation prints usage and exits 2
- [ ] `agentic-mbse pm close-item` with no WI-XXX prints usage and exits 2

### Error Handling

- [ ] Running from outside a project (no `work/BACKLOG.md` found) prints clear error to stderr and exits 1
- [ ] Invalid JSON in `--insights` prints parse error to stderr and exits 2
- [ ] Operation failure (e.g., WI-XXX not found) prints error message to stdout and exits 1
- [ ] Parser warnings from operations are printed to stderr

### Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] New subcommands appear in `agentic-mbse --help` output
- [ ] `agentic-mbse pm --help` lists all 14 operations

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.5 section)
- **D4.4 Design (dependency):** `.project/active/d4.4-operations/design.md`
- **D4.4 Spec (dependency):** `.project/active/d4.4-operations/spec.md`
- **D4.3 Dashboard (dependency):** `src/agentic_mbse/pm/dashboard.py`
- **Existing CLI:** `src/agentic_mbse/cli/__init__.py`
- **Design:** `.project/active/d4.5-cli-subcommands/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
