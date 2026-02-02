# Epic: Architecture Redesign — PM Script Engine (Phase 3D)

**Epic ID**: EPIC-ARCH-004
**Status**: Active
**Priority**: P0
**Created**: 2026-02-02
**Concept**: `.project/concepts/architecture-redesign/` (main.md §§ 2–3, workflows.md §§ 3–6, information-architecture.md §§ 3–5, delta-checklist.md § 3B)
**Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` §§ 3B.1–3B.4
**Depends On**: EPIC-ARCH-001 (Structure) — file structure and frontmatter schemas must be settled
**Parallel With**: EPIC-ARCH-003 (Commands) — commands add AP-7 script calls; this epic builds the scripts they call

---

## Executive Summary

Build the deterministic project management layer: structured file parsers, work item state derivation, a dashboard generator, 14 AP-7 operations, work item name resolution, CLI subcommands (`agentic-mbse status` and `agentic-mbse pm <operation>`), and Level 6 validation extensions. This is the largest single code addition — a new Python module (`src/agentic_mbse/pm/`) — and the mechanism that eliminates P5 (PM depends on agent memory) by making all state queries and state mutations deterministic and testable.

**Critical Success Factor**: `agentic-mbse status` produces an accurate, deterministic dashboard from a real project's state, and all 14 AP-7 operations pass unit tests with correct file mutations and error handling.

---

## Why This Epic Exists

**Problem P5**: Status tracking, archival, coverage reporting, and structured file mutations all rely on LLM execution today. This produces hallucinated state, missed updates, format inconsistencies, and no reliable dashboard.

**Architectural Principle AP-7**: When a workflow step involves structured file mutations (moving files, updating registry rows, changing status), the mutation is executed by a deterministic script, not by instructing an agent to edit markdown. Agents decide *what* to change and generate *content*; scripts execute the change correctly.

**Architectural Principle AP-4**: State queries are deterministic (Python scripts). State changes are agent-guided (commands). Intelligence layers on top.

The PM engine is pure Python with no dependency on skills or command prompts. It depends only on the file structure and frontmatter schemas from Epic 1. It can therefore proceed in parallel with Epic 3, which depends on Epic 2 (skills). The only convergence point is the `/status` command (Epic 3), which calls the Epic 4 dashboard.

---

## Why This Epic Comes Fourth (Parallel with Third)

The dependency chain is:

```
Epic 1: Structure → Epic 2: Knowledge → Epic 3: Commands
                                      ↘ Epic 4: PM Engine (THIS)
                                                    ↓
                                         /status command (convergence)
```

- **Epic 4 depends on Epic 1** (file structure, frontmatter schemas, entity formats) but NOT on Epic 2 (skills) or most of Epic 3 (commands).
- **Epic 3 commands add AP-7 script calls** (e.g., `agentic-mbse pm add-insight ...` in `/implement-model`). Those calls are correct even before Epic 4 implements the scripts — they document the integration contract.
- **The sole convergence point** is `/status`, which is a command (Epic 3) that calls the dashboard script (Epic 4). It is deliberately the last item in Epic 3.
- **All other AP-7 operations** are called by commands but independently testable.

---

## Open Design Questions (Must Resolve During This Epic)

| # | Question | Impact if unresolved | Proposed resolution approach |
|---|----------|---------------------|------------------------------|
| Q13 | What's the minimum viable PM dashboard? | Scope of D4.3. Risk of over-engineering first version. | Start with work item states only (epic progress, item status, stage). Add REQUIREMENTS.md metrics and VALIDATION_MATRIX.md metrics incrementally. Dashboard must be useful on an empty project (AP-1). |
| Q14 | Should `/analyze-models` be a script or agent command? | Whether model analysis metrics live in the PM module or remain purely agent-driven. | Hybrid: if deterministic metrics emerge (structural counts, validation level distribution), add them to the dashboard. `/analyze-models` remains an agent command for interpretation. |

---

## Success Criteria

- [ ] New Python module `src/agentic_mbse/pm/` exists with `__init__.py`, `parser.py`, `state.py`, `dashboard.py`, `operations.py`
- [ ] 8 parsers implemented: YAML frontmatter, BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md, ARCHITECTURE.md, OVERVIEW.md, traceability_matrix.csv
- [ ] All parsers handle malformed input gracefully (warnings + partial results, not crashes)
- [ ] Work item state derivation implemented (two-step: file system → frontmatter override)
- [ ] Epic state derivation implemented (draft/active/completed from sub-item states)
- [ ] `agentic-mbse status` produces accurate markdown dashboard from project state
- [ ] All 14 AP-7 operations implemented and unit tested
- [ ] Work item name resolution (WI-XXX → directory path) implemented
- [ ] Per-operation error model documented (atomic vs tolerant)
- [ ] `agentic-mbse pm <operation>` CLI subcommands work end-to-end
- [ ] Level 6 validation extended with 4 traceability sub-checks
- [ ] All operations produce correct output on empty projects (AP-1: design for 0, 1, N)
- [ ] All existing agentic-mbse tests pass (`uv run pytest tests/`)

---

## Deliverables

Seven deliverables with a dependency structure (see [Sequencing](#sequencing) below).

### D4.1: Parsers (`src/agentic_mbse/pm/parser.py`)

**Type**: Implementation
**Status**: Complete
**Dependencies**: Epic 1 complete (file structure, templates, frontmatter schemas settled)
**Delta checklist**: § 3B.1 parser items

**Objective**: Build structured file parsers for every file the PM engine reads. Each parser validates input per the AP-7 guarantee: malformed input produces clear error messages; partial results with warnings are preferred over hard failures.

**Parsers to implement**:

| Parser | Input file | Key output | Schema reference |
|--------|-----------|------------|------------------|
| YAML frontmatter (generic) | Any .md with `---` delimiters | Dict of parsed fields | frontmatter-schemas.md § 1 |
| BACKLOG.md | `work/BACKLOG.md` | Epic list with items, standalone list | frontmatter-schemas.md § 3.5 |
| REQUIREMENTS.md | `modeling_project/REQUIREMENTS.md` | List of PR-XXX rows (ID, Requirement, Source, Enforcement, Validation Method) | information-architecture.md § 3 Role 4 |
| VALIDATION_MATRIX.md | `modeling_project/VALIDATION_MATRIX.md` | List of SV-XXX rows (ID, Description, Type, Mechanism, Expected, Tolerance, Source, Test, Status) | information-architecture.md § 3 Role 6 |
| KNOWLEDGE.md | `knowledge/KNOWLEDGE.md` | List of DI-XXX entries (Title, Source, Context, Model/Analysis implications, Status, Superseded-by/Supersedes) | information-architecture.md § 3 Role 2 |
| ARCHITECTURE.md | `modeling_project/ARCHITECTURE.md` | List of AD-XXX entries (Title, Decision, Rationale, Date, Status) | information-architecture.md § 3 Role 5 |
| OVERVIEW.md | `modeling_project/OVERVIEW.md` | Goals Registry rows (ID, Goal, Priority, Status, Source, Traced Requirements), Analysis Questions rows (ID, Question, Implies, Source, Status) | information-architecture.md § 3 Role 3 |
| traceability_matrix.csv | `data/traceability_matrix.csv` | List of rows (Element, File, Type, Knowledge, Requirement, Source_Type, Source_Document, Source_Location, Confidence, Assumptions, Last_Verified) | information-architecture.md § 5.3 |

**Design constraints**:
- Generic YAML frontmatter parser is used by all markdown parsers (spec.md, design.md, plan.md, epic files, BACKLOG.md)
- Markdown table parsers must handle missing columns, extra whitespace, and partial rows
- CSV parser must handle quoting, commas in fields, and missing columns
- Unknown fields in YAML are silently ignored (frontmatter-schemas.md § 5 note 2)
- Empty string and omitted optional fields are normalized to "not set" (frontmatter-schemas.md § 5 note 3)
- Dates are validated as YYYY-MM-DD; invalid dates produce warnings, not hard failures (frontmatter-schemas.md § 5 note 5)

**Scope note**: Parsers are read-only. They do not write or modify files — that's the job of operations (D4.4). Parsers may be called by operations, the dashboard, or the state derivation module.

**Exit criteria**:
- [ ] 8 parsers implemented with type-annotated return types
- [ ] Each parser handles: valid input, missing file, empty file, malformed content
- [ ] Warnings include file path, field name, and expected format
- [ ] Parser unit tests cover all error paths (D4.6)

---

### D4.2: State Derivation (`src/agentic_mbse/pm/state.py`)

**Type**: Implementation
**Status**: Pending
**Dependencies**: D4.1 (parsers must exist to read frontmatter)
**Delta checklist**: § 3B.1 state items

**Objective**: Implement the work item state machine: the two-step read from workflows.md § 3.2 (file system structure → frontmatter override), epic state derivation, and stage detection.

**State derivation logic** (from workflows.md § 3.2):

1. **File system check**: Does `work/active/{WI-XXX}_{name}/` exist? → active. Does `work/completed/YYYYMMDD_{WI-XXX}_{name}/` exist? → completed. Neither but in BACKLOG.md? → backlog.
2. **Frontmatter override** (active items only): Read `spec.md` Status field. If `paused`, `abandoned`, or `failed`, that overrides the default active state.
3. **Stage detection** (active items only): Which artifact files exist in the directory? spec.md only → speccing; +design.md → designing; +plan.md → planning; implementation evidence → implementing.
4. **Epic state derivation**: `draft` (no sub-items active), `active` (at least one sub-item active), `completed` (all sub-items completed). Derived from sub-item states in BACKLOG.md cross-referenced with file system.

**Work item name resolution (B-014)**:
- Given a WI-XXX ID (possibly partial), resolve to the full directory path
- Search `work/active/{WI-XXX}_*/` then `work/completed/*_{WI-XXX}_*/`
- Handle ambiguity: multiple matches → error with candidate list
- Handle not-found: clear error message
- This is an internal utility used by close-item, impact-query, and other operations

**Exit criteria**:
- [ ] Two-step state derivation implemented and tested
- [ ] Stage detection correctly identifies all 4 stages (speccing, designing, planning, implementing)
- [ ] Epic state derived from sub-item states
- [ ] Work item name resolution handles: exact match, not found, ambiguous
- [ ] State derivation produces partial results on parse errors (e.g., bad frontmatter in one item doesn't block others)

---

### D4.3: Dashboard Generator (`src/agentic_mbse/pm/dashboard.py`)

**Type**: Implementation
**Status**: Pending
**Dependencies**: D4.1 (parsers), D4.2 (state derivation)
**Delta checklist**: § 3B.1 dashboard items

**Objective**: Generate the `agentic-mbse status` output. Plain markdown that renders in both terminal and IDE. Sections cover work items, project rules, and validation status.

**Dashboard sections** (from workflows.md § 4.3):

```
## Project: [name]

### Work Items
Epic: [epic name]                         [N/M done]
  [x] item-name .................. completed YYYY-MM-DD
  [ ] item-name .................. active:implementing (phase X/Y)
  [ ] item-name .................. backlog

Standalone:
  [x] item-name .................. completed YYYY-MM-DD
  [ ] item-name .................. backlog

### Project Rules (REQUIREMENTS.md)
Total: N | With validation method: N | Machine-enforceable: N

### Validation Status (VALIDATION_MATRIX.md)
Total: N | Passing: N | Failing: N | Pending: N
Failing: SV-XXX (description)
```

**Design constraints**:
- Plain markdown, no external dependencies (ASCII trees, tables, inline metrics)
- Must work on an empty project (AP-1): "No work items. No requirements. No validation criteria."
- Section headers are always present; sections show "none" or metrics as appropriate
- Failing validation criteria are listed individually (so the user sees what needs attention)
- Dashboard must be deterministic: same input → same output

**Minimum viable dashboard** (Q13 resolution approach):
1. **V1**: Work items section only (epic progress, item states with stage detection)
2. **V2**: Add REQUIREMENTS.md metrics (total, with validation method, machine-enforceable)
3. **V3**: Add VALIDATION_MATRIX.md metrics (total, passing, failing, pending, failing details)

Implement V1 first. V2 and V3 are incremental additions once parsers for those files exist.

**Exit criteria**:
- [ ] Dashboard produces correct output for: empty project, one item, multiple epics + standalone
- [ ] REQUIREMENTS.md metrics section works (or graceful degradation if file missing)
- [ ] VALIDATION_MATRIX.md metrics section works (or graceful degradation if file missing)
- [ ] Output is valid markdown that renders correctly in terminal and IDE

---

### D4.4: AP-7 Operations (`src/agentic_mbse/pm/operations.py`)

**Type**: Implementation
**Status**: Pending
**Dependencies**: D4.1 (parsers for reading files), D4.2 (state derivation for close-item, impact-query)
**Delta checklist**: § 3B.1 operations items

**Objective**: Implement 14 AP-7 operations plus the `save-research` file save. Each operation is a function that takes structured input and mutates project files deterministically. Mutation operations are atomic (all-or-nothing); query operations are tolerant (partial results with warnings).

**The key constraint (AP-7)**: The script is the source of truth for *where* files go, *what format* registry entries use, and *which files* get updated. The agent never directly edits registry files for state transitions.

#### Exhaustive Operation Inventory

Operations are listed in recommended build order (most immediately useful first). Each entry includes: tier, description, calling commands, atomicity model, and CLI interface.

**Tier 1 Operations (fully deterministic)**:

| # | Operation | Tier | Atomicity | What it does | Called by |
|---|-----------|------|-----------|--------------|----------|
| 1 | `close-item` | T1 | Atomic | Move `work/active/{WI-XXX}_{name}/` → `work/completed/YYYYMMDD_{WI-XXX}_{name}/`; update BACKLOG.md YAML frontmatter status to completed with date; re-render BACKLOG.md markdown body | `/backlog close`, `/status close` |
| 2 | `add-insight` | T1 (T3 invocation) | Atomic | Assign next DI-XXX ID; format entry from agent-supplied fields (title, source, context, model-implications, analysis-implications, rationale); append to `knowledge/KNOWLEDGE.md`; validate all required fields present | `/implement-model`, `/backlog close`, `/status close`, `/quick-model` (suggestion only) |
| 3 | `save-research` | T1 | Atomic | Write research document content to `knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md`; agent does NOT choose file path — script enforces naming convention | `/research` |
| 4 | `approve-research` | T2 | Atomic | Move file from `knowledge/research/pending/` → `approved/`; for each insight in `--insights` JSON: assign DI-XXX ID, format entry, append to `knowledge/KNOWLEDGE.md`; print confirmation with file paths + IDs | `/research` |
| 5 | `trace-element` | T1 | Atomic | Append row to `data/traceability_matrix.csv`; validate schema; prevent duplicate entries; validate PR-XXX exists in REQUIREMENTS.md; validate DI-XXX exists in KNOWLEDGE.md | `/implement-model` |
| 6 | `promote-requirement` | T1 | Atomic | Assign next PR-XXX ID; append row to `modeling_project/REQUIREMENTS.md` table; validate format; record Source (DI-XXX or G-XXX) | `/implement-model`, `/backlog close`, `/status close` |
| 7 | `impact-query` | T1 | Tolerant | Given DI-XXX or PR-XXX, traverse `data/traceability_matrix.csv` to find affected model elements; cross-reference with `work/active/` for affected work items; return structured result for agent interpretation | `/research` (knowledge supersession), `/status` (impact analysis) |
| 8 | `register-decision` | T1 | Atomic | Assign next AD-XXX ID; append entry to `modeling_project/ARCHITECTURE.md` Key Decisions section; validate format (title, decision, rationale, date, status) | `/audit-models`, `/backlog close`, `/status close` |
| 9 | `update-validation` | T1 | Atomic | Update Status column in `modeling_project/VALIDATION_MATRIX.md` for specified SV-XXX entry; validate SV-XXX exists | `/audit-models` |
| 10 | `register-intent` | T1 | Atomic | Assign G-XXX and/or AQ-XXX IDs; format entries from agent-supplied fields; append to Goals Registry and Analysis Questions tables in `modeling_project/OVERVIEW.md`; validate format; prevent duplicate IDs | `/formalize-intent` |
| 11 | `add-item` | T1 | Atomic | Assign next WI-XXX ID; append work item entry to `work/BACKLOG.md` YAML frontmatter (under specified epic or standalone list); re-render BACKLOG.md markdown body | `/status decompose`, `/backlog add` |
| 12 | `add-validation` | T1 | Atomic | Assign next SV-XXX ID; append row to `modeling_project/VALIDATION_MATRIX.md` table; validate format (description, type, mechanism, expected, tolerance) | `/status close`, `/spec-model` (initial SV-XXX entries), `/backlog close` |
| 13 | `status` (dashboard) | T1 | Tolerant | Parse all structured files; produce dashboard markdown (delegates to D4.3 dashboard module) | `/status` (default mode), `agentic-mbse status` CLI |

**Tier 2 Operations (script + headless LLM or structured content)**:

| # | Operation | Tier | Atomicity | What it does | Called by |
|---|-----------|------|-----------|--------------|----------|
| 14 | `supersede-insight` | T2 | Atomic | Mark old DI-XXX as superseded in KNOWLEDGE.md (Status → superseded, add Superseded-by field); assign new DI-XXX ID; create new entry with Supersedes field; query traceability_matrix.csv for affected elements; produce impact report to `knowledge/research/impacts/DI-XXX_superseded.md` | `/research` (knowledge contradiction detected) |

**Internal Utilities**:

| Utility | What it does | Used by |
|---------|--------------|---------|
| `resolve-work-item` | Given WI-XXX, search `work/active/{WI-XXX}_*/` then `work/completed/*_{WI-XXX}_*/`; return path or not-found | `close-item`, `impact-query`, `add-insight` (source validation) |

#### Cross-Reference: Commands → Operations

This table verifies that every AP-7 script invocation in Epic 3 commands is covered by an operation in this epic.

| Command | Operations called | Lines in command |
|---------|------------------|-----------------|
| `/implement-model` | `add-insight`, `trace-element`, `promote-requirement` | 64-68 |
| `/audit-models` | `update-validation`, `register-decision` | 66, 88 |
| `/research` | `save-research`, `supersede-insight`, `approve-research` | 62, 73, 89 |
| `/backlog` | `add-to-backlog` (= `add-item`), `close-item`, `promote-requirement`, `register-decision`, `add-validation`, `add-insight` | 41, 74, 91, 96-99 |
| `/formalize-intent` | `register-intent` | 74 |
| `/status` | `status` (dashboard), `add-item`, `close-item`, `promote-requirement`, `register-decision`, `add-validation`, `add-insight` | 35-36, 71, 83, 97-115 |
| `/quick-model` | `add-insight` (suggestion only, not formal call) | 90 |
| `/spec-model` | `add-validation` (creates SV-XXX entries — referenced at line 69 but script call not yet explicit in command) | 69 |

**Gap identified**: `/spec-model` references creating SV-XXX entries in VALIDATION_MATRIX.md (line 69) but does not include an explicit `agentic-mbse pm add-validation` script call. When implementing this operation, verify that `/spec-model` should also call the script (or if it writes directly, which would violate AP-7). This is a D3 cleanup item to coordinate with Epic 3.

**Naming note**: The `/backlog` command uses `add-to-backlog` as the operation name. This corresponds to `add-item` in the architecture. The CLI should accept both names or standardize on one. Recommend standardizing on `add-item` since that's the architecture's name.

#### Error Model (B-015)

| Category | Operations | Behavior |
|----------|-----------|----------|
| **Atomic** (all-or-nothing) | `close-item`, `add-insight`, `save-research`, `approve-research`, `trace-element`, `promote-requirement`, `register-decision`, `update-validation`, `register-intent`, `add-item`, `add-validation`, `supersede-insight` | Succeed completely or fail with no side effects. On failure: clear error message, no files changed. |
| **Tolerant** (partial results) | `status` (dashboard), `impact-query`, `resolve-work-item` | Produce partial results with warnings when inputs are malformed. E.g., "3 of 5 work items parsed; spec.md in WI-003 has invalid Status." |

**Exit criteria**:
- [ ] All 14 operations + save-research + resolve-work-item implemented
- [ ] Each atomic operation is truly atomic (test: interrupt mid-operation, verify no partial writes)
- [ ] Each tolerant operation produces partial results with warnings
- [ ] ID assignment is sequential and collision-free (reads highest existing ID, increments)
- [ ] BACKLOG.md body re-rendering works correctly after state changes
- [ ] Unit tests for every operation (D4.6)

---

### D4.5: CLI Subcommands

**Type**: Implementation
**Status**: Pending
**Dependencies**: D4.3 (dashboard), D4.4 (operations)
**Delta checklist**: § 3B.2

**Objective**: Wire the operations and dashboard into the `agentic-mbse` CLI as two subcommand groups: `agentic-mbse status` (dashboard) and `agentic-mbse pm <operation>` (state mutations and queries).

**CLI interface**:

```
agentic-mbse status [--json]
    Dashboard output. --json for programmatic consumption.

agentic-mbse pm close-item <WI-XXX>
agentic-mbse pm add-insight --title <text> --source <source> --context <text> --model-implications <text> --analysis-implications <text> [--rationale <text>]
agentic-mbse pm save-research --topic <topic-kebab-case> --content-file <path>
agentic-mbse pm approve-research <file> --insights '<json>'
agentic-mbse pm trace-element --element <name> --file <path> --type <kind> [--knowledge DI-XXX] [--requirement PR-XXX] [--source-type <type>] [--source-doc <name>] [--source-location <loc>]
agentic-mbse pm promote-requirement --requirement <text> --source <ID>
agentic-mbse pm impact-query <ID>
agentic-mbse pm register-decision --title <text> --decision <text> --rationale <text>
agentic-mbse pm update-validation <SV-XXX> --status <status>
agentic-mbse pm register-intent --goals '<json>' --questions '<json>'
agentic-mbse pm add-item --name <name> --scale <trivial|standard> --priority <P0|P1|P2|P3> [--epic <epic-name>] [--goal <G-XXX>]
agentic-mbse pm add-validation --description <text> --type <type> --mechanism <mechanism> --expected <value> --tolerance <tolerance>
agentic-mbse pm supersede-insight <DI-XXX> --new-insight '<json>' --reason <text>
```

**Design constraints**:
- All PM subcommands operate on the current working directory (find project root by walking up to find `work/BACKLOG.md` or `.claude/`)
- JSON arguments use single-quoted strings on the CLI; the Python CLI parses them
- Exit codes: 0 = success, 1 = operation error (validation failure, file not found), 2 = usage error
- Stdout: operation result (confirmation text, dashboard markdown, impact report)
- Stderr: warnings (malformed files, skipped entries)

**Exit criteria**:
- [ ] `agentic-mbse status` works end-to-end
- [ ] `agentic-mbse pm <operation>` works for all 14 operations
- [ ] `--json` flag on status produces machine-readable output
- [ ] Exit codes are consistent
- [ ] `--help` text is clear for each subcommand

---

### D4.6: Tests

**Type**: Implementation (accompanies each deliverable)
**Status**: Pending
**Dependencies**: Developed alongside D4.1–D4.5
**Delta checklist**: § 3B.3

**Objective**: Comprehensive test coverage for the PM module: unit tests for parsers, state derivation, dashboard, and every operation; integration tests for CLI subcommands; test fixtures with sample project structures.

**Test files**:

| Test file | Covers | Key scenarios |
|-----------|--------|---------------|
| `tests/test_pm_parser.py` | D4.1 parsers | Valid input, empty file, missing file, malformed content, partial parse, unknown fields ignored |
| `tests/test_pm_state.py` | D4.2 state derivation | File system → state mapping, frontmatter override, epic state derivation, stage detection, name resolution (exact/ambiguous/not-found) |
| `tests/test_pm_dashboard.py` | D4.3 dashboard | Empty project, single item, multiple epics + standalone, partial data (missing REQUIREMENTS.md), failing validation items |
| `tests/test_pm_operations.py` | D4.4 operations | Per-operation: happy path, validation errors, duplicate prevention, ID assignment, atomicity, BACKLOG.md re-rendering |
| `tests/test_pm_cli.py` | D4.5 CLI | End-to-end with temp directories, argument parsing, exit codes, JSON output |
| `tests/fixtures/pm/` | All | Sample BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md, ARCHITECTURE.md, OVERVIEW.md (with Goals Registry and Analysis Questions tables), traceability_matrix.csv, spec.md/design.md/plan.md with frontmatter, work item directories |

**Testing approach**:
- Fixtures provide realistic but minimal project structures
- Each test creates a temp directory, copies fixtures, runs operations, and asserts file state
- Parser tests verify both the parsed output structure and the warnings produced
- Operation tests verify both the file mutations AND that the return value is correct
- Integration tests invoke the CLI binary and check stdout/stderr/exit code

**Exit criteria**:
- [ ] Test fixtures exist for all PM file types
- [ ] Each parser has ≥4 test cases (valid, empty, missing, malformed)
- [ ] Each operation has ≥3 test cases (happy path, validation error, edge case)
- [ ] Dashboard tests cover empty project, partial data, full data
- [ ] CLI integration tests cover ≥5 operations end-to-end
- [ ] All tests pass: `uv run pytest tests/test_pm_*.py`

---

### D4.7: Level 6 Validation Extension

**Type**: Implementation
**Status**: Pending
**Dependencies**: D4.1 (parsers for REQUIREMENTS.md, traceability_matrix.csv, SOURCE_INDEX.md)
**Delta checklist**: § 3B.4

**Objective**: Extend `src/agentic_mbse/validation/level6_traceability.py` with four traceability sub-checks per information-architecture.md § 5.5.

**Sub-checks**:

| # | Sub-check | What it verifies | Input files |
|---|-----------|-----------------|-------------|
| 1 | **Format check** | Doc comments on definitions contain `Source` and `Reference` fields | SysML model files (via syside adapter) |
| 2 | **Resolvability check** | Referenced source documents exist in SOURCE_INDEX.md | SysML model doc comments + `knowledge/SOURCE_INDEX.md` |
| 3 | **Completeness check** | `data/traceability_matrix.csv` has an entry for each definition | SysML definitions (via syside) + traceability CSV |
| 4 | **Requirement coverage check** | Every PR-XXX in REQUIREMENTS.md has at least one satisfying element in traceability_matrix.csv | `modeling_project/REQUIREMENTS.md` + traceability CSV |

**Design decisions to make during implementation**:
- Sub-checks 1–3 naturally extend Level 6 (traceability & documentation)
- Sub-check 4 is a cross-file requirement coverage check. It may belong in Level 7 (architectural integrity) or as a `--traceability` flag. Decide based on where it fits in the existing validation flow.
- If SOURCE_INDEX.md or traceability_matrix.csv don't exist, the sub-checks should produce warnings (not hard failures) — a project without traceability is valid at Level 6 minus these sub-checks.

**Exit criteria**:
- [ ] All 4 sub-checks implemented
- [ ] Each sub-check produces specific, actionable messages (element name, file path, what's missing)
- [ ] Graceful degradation when supporting files (SOURCE_INDEX.md, traceability CSV) don't exist
- [ ] Test coverage for each sub-check

---

## Sequencing

```
D4.1 (parsers) ──────► D4.2 (state derivation) ──► D4.3 (dashboard) ──┐
       │                                                                 │
       └───────────────► D4.4 (operations, in priority order) ──────────┤
                                                                         ▼
                                                              D4.5 (CLI subcommands)
                                                                         │
                                                              D4.6 (tests: accompany each)
       │
       └───────────────► D4.7 (Level 6 extension — anytime after parsers)
```

- **D4.1** (parsers) is the foundation — everything else reads files through them
- **D4.2** (state derivation) builds on parsers; required by dashboard and some operations
- **D4.3** (dashboard) builds on state derivation; required by status CLI
- **D4.4** (operations) builds on parsers independently; some operations also use state derivation
- **D4.5** (CLI) wires everything together; depends on dashboard + operations
- **D4.6** (tests) accompany each deliverable — not a separate phase
- **D4.7** (Level 6) can proceed anytime after D4.1 parsers exist

**Recommended D4.4 build order** (most immediately useful first):
1. `close-item` — needed for close flow
2. `add-insight` — needed for inline knowledge capture (B-008)
3. `save-research` — needed for deterministic file save in research flow
4. `approve-research` — needed for research approval flow
5. `trace-element` — needed for traceability recording during implementation
6. `promote-requirement` — needed for MR-XXX → PR-XXX promotion
7. `impact-query` — needed for knowledge evolution analysis
8. `register-decision` — needed for design-to-architecture promotion
9. `update-validation` — needed for SV-XXX status tracking
10. `register-intent` — needed for `/formalize-intent` G-XXX/AQ-XXX registration
11. `add-item` — needed for `/status decompose` and `/backlog add`
12. `add-validation` — needed for `/status close` and `/spec-model`
13. `supersede-insight` — T2, most complex, defers gracefully
14. Work item name resolution — utility, build when first operation needs it (close-item)

---

## Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| PM engine scope creep (14 operations + parsers + dashboard is substantial) | Medium | Medium | Build in priority order. The first 6 operations cover the critical flows. Defer lower-priority operations if needed without blocking Epic 3 commands. |
| YAML frontmatter format needs to change after parsers are built | High | Low | Schemas are consolidated in frontmatter-schemas.md (Epic 1, D1.5). The generic YAML parser handles schema changes gracefully. |
| Markdown table parsing is fragile | Medium | Medium | Use a robust parsing strategy: split by `|`, strip whitespace, handle missing/extra columns with warnings. Test against hand-edited tables with formatting variations. |
| BACKLOG.md re-rendering loses user formatting | Medium | Low | BACKLOG.md body is entirely tool-owned — rendered deterministically from YAML frontmatter. No user formatting to preserve. Document this clearly. |
| Operation atomicity is hard to guarantee (multi-file writes) | Medium | Medium | For operations that touch multiple files (e.g., supersede-insight touches KNOWLEDGE.md + traceability CSV + impact report), implement as: validate all inputs → compute all changes → write all files. If any write fails, document which files were changed for manual recovery. |
| Level 6 validation extension conflicts with existing validation architecture | Low | Low | Sub-checks extend an existing level (not a new level). Existing Level 6 test infrastructure is reusable. |

---

## What This Epic Does NOT Include

Explicitly out of scope:

- **Command prompts or skill content** — Epic 2 and 3. This epic builds the scripts that commands call; it does not define command workflows.
- **Information architecture changes** — Epic 1. File structure and schemas are settled.
- **Agent behavior** — Agents invoke PM scripts via CLI; this epic builds the CLI, not the agent logic.
- **Git integration** — Deferred (Q16). Operations use file system, not git.
- **Hook integration** — Deferred (Q17). No auto-validation on file writes.
- **Cross-project sharing** — Deferred (Q18).
- **The `/status` command itself** — That's Epic 3, D3.2. This epic provides the `agentic-mbse status` CLI script that the command wraps.

---

## Relationship to Epic 1

Epic 1 (Structure) provides the inputs this epic parses:
- File structure (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- Template files define the empty-state format parsers must handle
- YAML frontmatter schemas (frontmatter-schemas.md) are the parser input contracts
- Entity formats (DI-XXX, PR-XXX, AD-XXX, SV-XXX, G-XXX, AQ-XXX, WI-XXX) define the ID schemes operations must assign

---

## Relationship to Epic 3

Epic 3 (Commands) is the primary consumer of this epic's outputs:
- Commands call AP-7 operations via `agentic-mbse pm <operation>` CLI
- `/status` command wraps `agentic-mbse status` dashboard
- The cross-reference table in D4.4 maps every command → operation dependency
- Commands can be written with placeholder script calls before this epic delivers; the calls become operational when the scripts are built
- The `add-to-backlog` vs `add-item` naming discrepancy should be resolved (standardize on `add-item`)

---

**Last Updated**: 2026-02-02
**Next Action**: Begin D4.2 (state derivation) — builds on D4.1 parsers.
