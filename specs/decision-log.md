# Specification: Decision Log Generation

**Purpose:** Auto-generate a human-readable decision log from resolved comment threads to serve as project knowledge base.

## Requirements

**REQ-1: Generation Trigger**
- MUST be explicitly triggered via `comment decisions` command
- MAY be triggered automatically by git post-commit hook
- MUST be idempotent (safe to run repeatedly)

**REQ-2: Content Aggregation**
- MUST include all resolved threads with non-null decision field
- MUST group by source file, sorted alphabetically
- MUST sort threads within each file by resolution timestamp (newest first)
- MUST exclude resolved threads without decisions

**REQ-3: Output Format**
- File: `DECISIONS.md` in project root
- Header: Auto-generated notice + last updated timestamp
- Per decision: Original anchor snippet, decision summary, decider, date, link to source file

**REQ-4: Staleness Handling**
- MUST regenerate from current sidecar state (not append)
- MUST warn if reopened threads had decisions (include in separate section)
- MUST handle deleted source files gracefully (mark as "[deleted]")

**REQ-5: Git Integration**
- Generated file MUST be committable
- MUST use markdown format for diffs
- MUST NOT run automatically unless opt-in configured

## Acceptance Criteria

**AC-1:** Given 3 resolved threads with decisions across 2 files, when `comment decisions` runs, then `DECISIONS.md` contains 3 entries grouped by file

**AC-2:** Given `DECISIONS.md` exists, when `comment decisions` runs, then file is completely regenerated (not appended)

**AC-3:** Given thread resolved on 2026-02-01 and thread resolved on 2026-02-05, when generating log, then 2026-02-05 decision appears first

**AC-4:** Given thread with decision later reopened, when generating log, then decision appears in "Reopened Decisions" section

**AC-5:** Given source file deleted, when generating log, then decision entry shows "[deleted: old/path.md]"

**AC-6:** Given `DECISIONS.md` header, when read, then header includes "Auto-generated — do not edit manually"

## Interfaces

**Inputs:**
- All sidecar files in `.comments/`
- Optional: Filter by date range or file pattern

**Outputs:**
- `DECISIONS.md` file in project root
- Generation summary (N decisions included)

**References:**
- `data-model.md`: Decision object structure
- `file-operations.md`: Reading sidecars, writing DECISIONS.md

## Constraints

**CON-1:** Generation MUST complete in < 5 seconds for 1000 decisions
**CON-2:** Output MUST be deterministic (same sidecars → same DECISIONS.md)
**CON-3:** MUST handle unicode in decision summaries correctly
**CON-4:** File size MUST stay under 1 MB (warn if exceeded)

## Out of Scope

- Decision search/query interface (use `grep` on DECISIONS.md)
- Decision versioning (use git history)
- Decision tagging or categorization
- Export to other formats (JSON, CSV, etc.)
- Decision templates or structured decision fields
