# Spec: D4.4 AP-7 Operations

**Status:** Implementation Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Complexity:** HIGH
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (Architecture Redesign — PM Script Engine)

---

## Business Goals

### Why This Matters

The PM engine's mutation layer is the core AP-7 deliverable. Today, structured file mutations (adding knowledge entries, closing work items, updating validation status) would require agents to directly edit registry files — producing format inconsistencies, incorrect IDs, missed cross-file updates, and no atomicity guarantees. AP-7 eliminates this by making every structured mutation a deterministic, testable Python function.

This is the largest single code addition in Epic 4. It produces `src/agentic_mbse/pm/operations.py` — the module that every MBSE command calls for state transitions. Without it, commands (Epic 3) cannot perform their AP-7 script calls, and the CLI (D4.5) has nothing to wire.

### Success Criteria

- [ ] All 13 mutation operations + `impact-query` + `status` stub implemented in `operations.py`
- [ ] `supersede-insight` exists as a stub with `NotImplementedError` and TODO marker
- [ ] Every atomic operation is truly all-or-nothing: compute all changes in memory, then write
- [ ] Every operation works correctly on an empty project (AP-1)
- [ ] Sequential ID assignment is collision-free (read highest existing, increment)
- [ ] BACKLOG.md body re-rendering produces correct markdown from YAML frontmatter

### Priority

P0 — blocks D4.5 (CLI subcommands) and is the critical path for Epic 3 command integration.

---

## Problem Statement

### Current State

D4.1 (parsers) and D4.2 (state derivation) are complete. The PM engine can **read** all structured files and **derive** project state. But it cannot **mutate** anything — there are no functions to add items, close items, register entries, or update statuses.

### Desired Outcome

A complete set of deterministic operations that commands call to mutate project files. Each operation takes structured input, validates it, and produces correct file mutations with proper ID assignment, format compliance, and atomicity.

---

## Scope

### In Scope

- 13 mutation operations (see Functional Requirements below)
- 1 query operation (`impact-query`)
- 1 delegation stub (`status` → D4.3 dashboard)
- 1 deferred stub (`supersede-insight` → `NotImplementedError`)
- BACKLOG.md body re-rendering function (shared by `close-item`, `add-item`)
- Sequential ID assignment helpers (next DI-XXX, PR-XXX, AD-XXX, SV-XXX, G-XXX, AQ-XXX, WI-XXX)
- Return types for each operation (confirmation messages, assigned IDs, impact results)

### Out of Scope

- Dashboard generator (D4.3) — `status` operation delegates to it
- CLI argument parsing and subcommand wiring (D4.5)
- Tests (D4.6) — accompany implementation but not specified here
- Level 6 validation extensions (D4.7)
- Command prompt changes (Epic 3)
- `resolve-work-item` — already implemented in `state.py`

### Edge Cases & Considerations

- **Concurrent writes**: Not handled. Operations assume single-writer (agent calls one operation at a time). This is acceptable at the expected scale (~3-5 concurrent items).
- **Partially corrupted files**: Operations that read before writing (e.g., `close-item` reading spec.md) must handle parse warnings gracefully — fail the operation if required fields are missing, not silently proceed.
- **Empty project**: Every operation must produce sensible behavior when called on a project with no existing entries. `add-insight` on a KNOWLEDGE.md with no entries should produce `DI-001`. `close-item` on a project with no active items should produce a clear error.
- **ID gaps**: If a user manually deletes DI-003, the next ID is still DI-004 (based on highest existing), not DI-003. IDs are never reused.
- **BACKLOG.md without frontmatter**: If BACKLOG.md exists but has no YAML frontmatter, operations that modify it should fail with a clear error, not corrupt the file.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic (D4.4 section) and architecture concept docs (workflows.md, information-architecture.md, frontmatter-schemas.md) unless marked [INFERRED].

#### FR-1: Operation Module Structure

The operations MUST be implemented in `src/agentic_mbse/pm/operations.py`. Each operation is a public function that takes a `project_root: Path` argument plus operation-specific parameters. Operations MUST be importable and callable without CLI scaffolding.

#### FR-2: Atomicity Model

Operations classified as **atomic** MUST follow this pattern:
1. Validate all inputs (file existence, format, ID validity)
2. Compute all changes in memory (new content, updated content)
3. Write all files
4. If any validation fails, return an error with no files changed

Operations classified as **tolerant** (impact-query, status) SHOULD produce partial results with warnings when inputs are malformed.

#### FR-3: Sequential ID Assignment

Each entity type (DI-XXX, PR-XXX, AD-XXX, SV-XXX, G-XXX, AQ-XXX, WI-XXX) MUST have an ID assignment function that:
- Reads the relevant registry file using the existing parser
- Finds the highest existing numeric ID
- Returns the next sequential ID (zero-padded to 3 digits)
- Handles empty registries (first ID is XXX-001)

#### FR-4: BACKLOG.md Body Re-Rendering

A shared function MUST re-render the BACKLOG.md markdown body from its YAML frontmatter. The rendered body MUST match the format defined in the BACKLOG.md template:
- Epic sections with goal, priority, status, epic file link, and item table
- Standalone items section with scale, priority, status columns
- Completed items show completion date in Notes column
- Empty state shows the "no items" message from the template

This function is called by `close-item`, `add-item`, and any operation that modifies BACKLOG.md frontmatter.

#### FR-5: Return Types

Each operation MUST return a structured result that includes:
- Success/failure status
- For mutations: the IDs assigned, files modified, confirmation message
- For queries: the query results
- For failures: the error message and which validation failed

[INFERRED] A consistent return type (e.g., `OperationResult`) simplifies CLI integration in D4.5.

#### FR-6: `close-item` Operation

**Atomicity**: Atomic
**Called by**: `/backlog close`, `/status close`, `/audit-models`

Given a WI-XXX ID:
1. Resolve to directory path via `resolve_work_item()` (from state.py)
2. Read spec.md — set `Status: completed`, `Updated: YYYY-MM-DD` (today)
3. If design.md exists — set `Status: complete`, `Updated: YYYY-MM-DD`
4. If plan.md exists — set `Status: complete`, `Updated: YYYY-MM-DD`
5. Move `work/active/{WI-XXX}_{name}/` → `work/completed/YYYYMMDD_{WI-XXX}_{name}/`
6. Update BACKLOG.md YAML frontmatter: set item status to `completed`, add `completed` date
7. Re-render BACKLOG.md markdown body
8. Return confirmation with archive path

**Validation**: Item MUST be in `work/active/`. Item MUST exist in BACKLOG.md. spec.md MUST exist and be parseable.

#### FR-7: `add-insight` Operation

**Atomicity**: Atomic
**Called by**: `/implement-model`, `/backlog close`, `/status close`, `/quick-model`

Given structured fields (title, source, context, model_implications, analysis_implications, rationale [optional]):
1. Parse KNOWLEDGE.md to find highest DI-XXX ID
2. Assign next DI-XXX ID
3. Format entry per the entity format in information-architecture.md Role 2
4. Append to KNOWLEDGE.md
5. Return assigned ID and confirmation

**Validation**: All required fields (title, source, context, model_implications, analysis_implications) MUST be non-empty. Status is always `captured` for new entries.

#### FR-8: `save-research` Operation

**Atomicity**: Atomic
**Called by**: `/research`

Given a topic string and content string:
1. Generate filename: `YYYYMMDD-HHMMSS_topic.md` (topic kebab-cased)
2. Ensure `knowledge/research/pending/` directory exists
3. Write content to the generated path
4. Return the file path

**Validation**: Topic MUST be non-empty. Content MUST be non-empty. Agent does NOT choose the file path — the operation enforces the naming convention.

#### FR-9: `approve-research` Operation

**Atomicity**: Atomic
**Called by**: `/research`

Given a pending research file path and a list of insight entries (as structured data):
1. Verify the file exists in `knowledge/research/pending/`
2. For each insight: assign next DI-XXX ID, format entry, append to KNOWLEDGE.md
3. Move file from `knowledge/research/pending/` → `knowledge/research/approved/`
4. Return confirmation with new file path and assigned DI-XXX IDs

**Validation**: File MUST exist in pending/. Each insight MUST have all required fields. File move and KNOWLEDGE.md appends are all-or-nothing.

#### FR-10: `trace-element` Operation

**Atomicity**: Atomic
**Called by**: `/implement-model`

Given element details (element, file, type, knowledge, requirement, source_type, source_document, source_location, confidence, assumptions, last_verified [optional, defaults to today]):
1. Validate PR-XXX IDs exist in REQUIREMENTS.md (if provided)
2. Validate DI-XXX IDs exist in KNOWLEDGE.md (if provided)
3. Check for duplicate entries in traceability_matrix.csv (same element + file)
4. Append row to CSV (Last_Verified defaults to today's date if not provided)
5. Return confirmation

**Validation**: Element and file MUST be non-empty. Referenced PR-XXX and DI-XXX MUST exist in their respective registries. Duplicate element+file combination MUST be rejected.

#### FR-11: `promote-requirement` Operation

**Atomicity**: Atomic
**Called by**: `/implement-model`, `/backlog close`, `/status close`

Given requirement text, source ID (DI-XXX or G-XXX), enforcement method, and validation method:
1. Parse REQUIREMENTS.md to find highest PR-XXX ID
2. Assign next PR-XXX ID
3. Append row to REQUIREMENTS.md table with all 5 columns (ID, Requirement, Source, Enforcement, Validation Method)
4. Return assigned ID and confirmation

**Validation**: Requirement text MUST be non-empty. Source MUST match DI-XXX or G-XXX pattern. Enforcement and validation_method MUST be non-empty — the architecture states that "each requirement specifies both criteria and method" to make requirements enforceable rather than aspirational. Callers (commands) are responsible for obtaining these from the agent/user before calling the operation.

#### FR-12: `impact-query` Operation

**Atomicity**: Tolerant
**Called by**: `/research`, `/status`

Given a DI-XXX or PR-XXX ID:
1. Parse traceability_matrix.csv
2. Find rows where Knowledge column contains the DI-XXX or Requirement column contains the PR-XXX
3. Cross-reference with `work/active/` to find affected work items
4. Return structured result: affected elements (with file paths), affected requirements, affected work items

**Validation**: ID MUST match DI-XXX or PR-XXX pattern. Missing traceability CSV returns empty results with a warning. Partial parse of CSV produces partial results.

#### FR-13: `register-decision` Operation

**Atomicity**: Atomic
**Called by**: `/audit-models`, `/backlog close`, `/status close`

Given title, decision, rationale:
1. Parse ARCHITECTURE.md to find highest AD-XXX ID
2. Assign next AD-XXX ID
3. Format entry per the Key Decisions section format
4. Append to ARCHITECTURE.md under `## Key Decisions`
5. Return assigned ID and confirmation

**Validation**: Title, decision, and rationale MUST be non-empty. Date is today's date. Status is always `active` for new entries.

#### FR-14: `update-validation` Operation

**Atomicity**: Atomic
**Called by**: `/audit-models`

Given an SV-XXX ID and a new status:
1. Parse VALIDATION_MATRIX.md
2. Find the row with matching SV-XXX
3. Update the Status column to the new value
4. Re-write VALIDATION_MATRIX.md with the updated table
5. Return confirmation

**Validation**: SV-XXX MUST exist in the matrix. New status MUST be a valid VerificationStatus enum value.

#### FR-15: `register-intent` Operation

**Atomicity**: Atomic
**Called by**: `/formalize-intent`

Given lists of goal entries and/or question entries (as structured data):
1. Parse OVERVIEW.md to find highest G-XXX and AQ-XXX IDs
2. Assign next IDs for each new entry
3. Append rows to Goals Registry and/or Analysis Questions tables
4. Return assigned IDs and confirmation

**Validation**: Each goal MUST have goal text, priority, source. Each question MUST have question text, source. Prevent duplicate IDs.

#### FR-16: `add-item` Operation

**Atomicity**: Atomic
**Called by**: `/status decompose`, `/backlog add`

Given name, scale, priority, and optional epic name and goal:
1. Parse BACKLOG.md to find highest WI-XXX ID
2. Assign next WI-XXX ID
3. Add entry to BACKLOG.md YAML frontmatter (under specified epic or standalone list)
4. Re-render BACKLOG.md markdown body
5. Return assigned ID and confirmation

**Validation**: Name MUST be non-empty. Scale MUST be valid enum. Priority MUST be valid enum. If epic specified, it MUST exist in BACKLOG.md epics list. Status is always `backlog` for new items.

#### FR-17: `add-validation` Operation

**Atomicity**: Atomic
**Called by**: `/status close`, `/spec-model`, `/backlog close`

Given description, type, mechanism, expected, tolerance:
1. Parse VALIDATION_MATRIX.md to find highest SV-XXX ID
2. Assign next SV-XXX ID
3. Append row to VALIDATION_MATRIX.md table
4. Return assigned ID and confirmation

**Validation**: Description MUST be non-empty. Type MUST be valid VerificationType. Mechanism MUST be valid VerificationMechanism. Status is always `pending` for new entries.

#### FR-18: `supersede-insight` Stub

**Atomicity**: N/A (stub)
**Called by**: `/research`

Implement as a function stub that raises `NotImplementedError` with a descriptive message. Include a `# TODO: D4.4 stretch — implement full supersession flow per workflows.md § 6.1` comment.

The full implementation (when built) would: mark old DI-XXX as superseded, create new DI-XXX, query traceability for affected elements, produce impact report to `knowledge/research/impacts/`.

#### FR-19: `status` Delegation Stub

**Atomicity**: Tolerant
**Called by**: `/status`, `agentic-mbse status`

Implement as a function that delegates to the D4.3 dashboard module. For now, call `derive_project_state()` from state.py and return the raw `ProjectState` object. The D4.3 deliverable will add the markdown rendering.

[INFERRED] This provides a working integration point for D4.5 CLI even before D4.3 is fully built.

### Non-Functional Requirements

- **NF-1**: Operations MUST NOT import from `cli/` or any command/agent code. The PM module is a pure library.
- **NF-2**: Operations MUST use existing parsers from `parser.py` for all file reads. No ad-hoc parsing in operations.
- **NF-3**: All file writes MUST use UTF-8 encoding.
- **NF-4**: Operations SHOULD follow the existing code style in parser.py and state.py (type annotations, docstrings, ParseWarning accumulation pattern where appropriate).

---

## Acceptance Criteria

### Core Functionality

- [ ] `close-item` correctly archives a work item (frontmatter updates, directory move, BACKLOG.md update + re-render)
- [ ] `add-insight` assigns sequential DI-XXX IDs and produces correctly formatted KNOWLEDGE.md entries
- [ ] `save-research` enforces `YYYYMMDD-HHMMSS_topic.md` naming convention
- [ ] `approve-research` atomically moves file and appends insights
- [ ] `trace-element` validates referenced IDs exist and prevents duplicates
- [ ] `promote-requirement` assigns PR-XXX and appends correct table row
- [ ] `impact-query` returns affected elements, requirements, and work items
- [ ] `register-decision` assigns AD-XXX and appends correct entry format
- [ ] `update-validation` modifies the correct row in-place
- [ ] `register-intent` assigns G-XXX / AQ-XXX IDs and appends to correct tables
- [ ] `add-item` assigns WI-XXX, updates BACKLOG.md frontmatter, and re-renders body
- [ ] `add-validation` assigns SV-XXX and appends correct table row
- [ ] `supersede-insight` raises `NotImplementedError` with TODO comment
- [ ] `status` delegates to state derivation and returns `ProjectState`

### Atomicity & Error Handling

- [ ] Atomic operations leave no partial writes on validation failure
- [ ] Each operation returns a structured result with success/failure, IDs assigned, files modified
- [ ] Operations produce clear error messages (file path, what went wrong, what was expected)
- [ ] Operations on empty projects produce correct first IDs (XXX-001) and sensible output

### Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] Operations are importable from `agentic_mbse.pm` (added to `__init__.py` exports)
- [ ] BACKLOG.md re-rendering round-trips correctly (render → parse → render produces same output)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.4 section)
- **Architecture:** `.project/concepts/architecture-redesign/workflows.md` (§§ 3–6)
- **Architecture:** `.project/concepts/architecture-redesign/information-architecture.md` (§§ 3–5)
- **Architecture:** `.project/concepts/architecture-redesign/frontmatter-schemas.md` (§§ 1–5)
- **Depends on:** `.project/active/d4.1-parsers/` (complete)
- **Depends on:** `.project/active/d4.2-state-derivation/` (complete)
- **Design:** `.project/active/d4.4-operations/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
