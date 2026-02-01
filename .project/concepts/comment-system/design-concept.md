# Design Document: File-Native Comment Threading System

**Status:** Draft  
**Author:** Reid + Claude  
**Date:** 2026-02-01  
**Version:** 0.1  

---

## 1. Motivation

Agentic development workflows need a structured feedback loop between humans and AI agents. Today, feedback happens through chat — unstructured, ephemeral, and disconnected from the artifacts under review. Google Antigravity demonstrated that anchoring feedback to specific text selections (Google Docs-style inline commenting) dramatically improves the quality of human-agent collaboration. But Antigravity's implementation is proprietary, embedded in their UI, and not accessible to external tools.

We need a **file-native, tool-agnostic commenting layer** that:

- Works on any text file (markdown, code, config) in any editor
- Stores comments in sidecar files that never modify the source document
- Exposes a deterministic API that any agent can consume without LLM involvement in the plumbing
- Is git-friendly by default (plain JSON, diffable, mergeable)
- Supports rendering in VSCode/Cursor while remaining fully functional from CLI

### 1.1 Design Philosophy

**The artifact layer is stochastic. The feedback layer must be deterministic.**

Agents write plans, code, and documentation — that's where LLM reasoning belongs. But the commenting system (creating threads, anchoring to text, tracking resolution status, reconciling after edits) is traditional software. Agents interact with it through structured tool calls that map to deterministic CRUD operations. The LLM never generates or parses the comment data structure — it reads structured input and calls structured tools.

This means the orchestration layer can be a bash script, a Python workflow, or a Makefile. The control flow is always predictable. LLM calls happen only at leaf nodes where actual reasoning is required.

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-1: Comment Creation
- **FR-1.1:** Users and agents can create comments anchored to a specific text selection in a source file.
- **FR-1.2:** Comments are stored in a sidecar file adjacent to (or in a known directory relative to) the source file. The source file is never modified.
- **FR-1.3:** Each comment creates a thread. Threads support replies from both humans and agents.
- **FR-1.4:** Threads have a status lifecycle: `open` → `resolved` | `wontfix`. Resolved threads can be reopened.

#### FR-2: Anchoring
- **FR-2.1:** Comments are anchored to a text selection defined by line range, content hash, and surrounding context.
- **FR-2.2:** When the source file changes, anchors are automatically reconciled (see §5).
- **FR-2.3:** Anchors have three health states: `anchored` (exact match), `drifted` (fuzzy match found, may need human verification), `orphaned` (anchor target deleted or unrecoverable).
- **FR-2.4:** Orphaned comments remain visible and accessible. They are never silently deleted.

#### FR-3: Surfaces
- **FR-3.1:** CLI for humans — create, list, reply, resolve comments from the command line.
- **FR-3.2:** CLI/MCP for agents — identical operations, structured JSON input/output, designed for tool-call integration.
- **FR-3.3:** VSCode/Cursor extension — renders comments as gutter annotations and a comment panel. Supports "highlight text → add comment" UX.
- **FR-3.4:** All three surfaces read and write the same sidecar files. No synchronization layer, no server, no database.

#### FR-4: Querying
- **FR-4.1:** List all unresolved comments for a file, a directory, or the entire project.
- **FR-4.2:** Filter by status, author, anchor health, and file path.
- **FR-4.3:** Get full thread history for a specific comment (all replies, timestamps, authors).

#### FR-5: Decision Log
- **FR-5.1:** When a thread is resolved, the resolution can optionally include a `decision` summary — a one-line distillation of what was decided and why.
- **FR-5.2:** An auto-generated `DECISIONS.md` file aggregates all resolved decisions for human and agent reference. This serves as a lightweight "knowledge item" (à la Antigravity's KI system).

### 2.2 Non-Functional Requirements

- **NFR-1: Zero source modification.** The commenting system must never write to, append to, or modify the source file in any way.
- **NFR-2: Git-native.** Sidecar files are plain JSON, committable, diffable, and mergeable. Comment history is part of the repo history.
- **NFR-3: No runtime dependencies.** No server, no database, no background process. The CLI is a single binary or script. The sidecar files are the entire state.
- **NFR-4: Deterministic operations.** Every CLI command and MCP tool call produces the same output given the same input. No LLM in the loop for any CRUD operation.
- **NFR-5: Resilient to failure.** If reconciliation fails, comments degrade gracefully (orphaned, not deleted). If the sidecar file is corrupted, the source file is unaffected.
- **NFR-6: Performance.** Reconciliation on a 10,000-line file with 100 comments completes in < 1 second.

---

## 3. Architecture Overview

```
Source files (never modified)          Sidecar files (comment state)
┌─────────────────────┐               ┌──────────────────────────────┐
│ PLAN.md             │               │ .comments/PLAN.md.json       │
│ ARCHITECTURE.md     │──────────────▶│ .comments/ARCHITECTURE.md.json│
│ src/model.py        │  references   │ .comments/src/model.py.json  │
└─────────────────────┘               └──────────┬───────────────────┘
                                                  │
                                                  │  read/write
                              ┌───────────────────┼───────────────────┐
                              │                   │                   │
                      ┌───────▼──────┐   ┌────────▼───────┐  ┌───────▼──────┐
                      │   CLI        │   │  MCP / Agent   │  │   VSCode     │
                      │  (human)     │   │   Tool API     │  │  Extension   │
                      └──────────────┘   └────────────────┘  └──────────────┘
```

### 3.1 File Layout

```
project-root/
├── .comments/                          # Comment storage root
│   ├── config.json                     # Project-level settings
│   ├── DECISIONS.md                    # Auto-generated decision log
│   ├── PLAN.md.json                    # Sidecar for PLAN.md
│   ├── ARCHITECTURE.md.json            # Sidecar for ARCHITECTURE.md
│   └── src/
│       └── model.py.json               # Mirrors source tree structure
├── PLAN.md                             # Source (never modified by system)
├── ARCHITECTURE.md
└── src/
    └── model.py
```

The `.comments/` directory mirrors the source tree structure. Each source file `<path>` has a corresponding sidecar at `.comments/<path>.json`. This makes it trivial to find the sidecar for any file, and keeps the directory structure navigable.

---

## 4. Data Model

### 4.1 Sidecar File Schema

Each `.comments/<file>.json` contains:

```jsonc
{
  "version": "1.0",
  "source_file": "PLAN.md",
  "source_hash": "sha256:a1b2c3...",         // Hash of source at last reconciliation
  "last_reconciled": "2026-02-01T10:30:00Z",
  "threads": [
    {
      "id": "t_01JKXYZ...",                   // ULID (sortable, unique)
      "status": "open",                       // open | resolved | wontfix
      "anchor": { ... },                      // See §4.2
      "comments": [
        {
          "id": "c_01JKXYZ...",               // ULID
          "author": "reid",                   // or "claude-code", "agent:reviewer", etc.
          "author_type": "human",             // human | agent
          "body": "Reconsider this approach — the cost model assumes linear scaling but our data shows step functions.",
          "created_at": "2026-02-01T10:00:00Z"
        },
        {
          "id": "c_01JKABC...",
          "author": "claude-code",
          "author_type": "agent",
          "body": "Agreed. I've updated the cost model to use piecewise linear segments with breakpoints at 10MW, 50MW, and 200MW.",
          "created_at": "2026-02-01T10:15:00Z"
        }
      ],
      "decision": null,                       // Populated on resolution. See §4.3
      "created_at": "2026-02-01T10:00:00Z",
      "resolved_at": null
    }
  ]
}
```

### 4.2 Anchor Schema

The anchor is the critical data structure. It stores redundant signals so that the comment can survive source file edits. Signals are listed in descending priority order for reconciliation.

```jsonc
{
  "anchor": {
    // --- Primary signal: content identity ---
    "content_hash": "sha256:f4e5d6...",       // Hash of the exact selected text
    "content_snippet": "assumes linear scaling but our data", // First 80 chars, for human readability

    // --- Secondary signal: context fingerprint ---
    "context_before_hash": "sha256:...",      // Hash of 3 lines before selection
    "context_after_hash": "sha256:...",       // Hash of 3 lines after selection
    "context_before_snippet": "## Cost Model\n\nThe LCOE calculation",  // First 80 chars
    "context_after_snippet": "at scale. We should validate\nthis against",

    // --- Tertiary signal: structural position ---
    "line_start": 42,                         // 1-indexed, inclusive
    "line_end": 45,                           // 1-indexed, inclusive
    "char_start": 0,                          // 0-indexed offset within line_start
    "char_end": null,                         // null = end of line_end

    // --- Reconciliation metadata ---
    "health": "anchored",                     // anchored | drifted | orphaned
    "drift_distance": 0,                      // Lines moved from original position
    "last_verified": "2026-02-01T10:30:00Z"
  }
}
```

**Why this structure:**

| Signal | Survives... | Fails when... |
|--------|-------------|---------------|
| `content_hash` | Moves, surrounding edits | Selected text itself is edited |
| `context_*_hash` | Selected text edits | Surrounding context changes too |
| `content_snippet` (fuzzy) | Minor edits to selection | Major rewrites |
| `line_start/end` | No edits above the anchor | Any insertion/deletion above |

By storing all four, we can attempt reconciliation in priority order and degrade gracefully.

### 4.3 Decision Schema

When a thread is resolved, the resolver (human or agent) can attach a decision:

```jsonc
{
  "decision": {
    "summary": "Cost model updated to piecewise linear with breakpoints at 10/50/200 MW",
    "decided_by": "reid",
    "decided_at": "2026-02-01T11:00:00Z"
  }
}
```

---

## 5. Anchor Reconciliation

This is the hardest problem in the system. When the source file changes, comment anchors may no longer point to the right text. The reconciliation algorithm must re-anchor comments reliably or mark them as degraded.

### 5.1 Design Principles (Borrowed from Google Docs)

Google Docs handles anchor invalidation with these behaviors. We adopt the same philosophy:

| Scenario | Google Docs Behavior | Our Behavior |
|----------|---------------------|--------------|
| Text within anchor is edited | Comment stays, shows updated text | Re-anchor using context signals → `drifted` |
| Text within anchor is deleted entirely | Comment becomes "orphaned", shown in sidebar with notice | `orphaned` status, original snippet preserved |
| Text is moved to new location | Comment follows the text | Attempt content-hash match at new location → `drifted` |
| Text above anchor is inserted/deleted | Comment line numbers shift | Re-anchor using content hash → `anchored` (line numbers updated) |
| Surrounding context changes | Comment stays on its text | Primary signal (content hash) still works → `anchored` |
| File is renamed | Comment stays attached | Handled by rename tracking (see §5.4) |
| File is deleted | Comments become inaccessible | Sidecar remains; `orphaned` on all threads |

**Critical rule: Comments are never silently deleted.** The worst case is `orphaned` status with the original snippet preserved for human review.

### 5.2 Reconciliation Algorithm

Reconciliation runs when:
- A CLI or MCP command reads a sidecar file and detects that `source_hash` doesn't match the current file
- A git hook fires after commit/checkout (optional)
- The VSCode extension detects a file save

**Algorithm (per thread):**

```
function reconcile(thread, old_source, new_source):
    anchor = thread.anchor

    // Step 1: Try exact content match (handles moves and surrounding edits)
    locations = find_all_occurrences(new_source, anchor.content_hash)
    if locations.length == 1:
        update_anchor(anchor, locations[0])
        anchor.health = "anchored"
        anchor.drift_distance = abs(locations[0].line_start - anchor.line_start)
        return

    if locations.length > 1:
        // Ambiguous — use context to disambiguate
        best = pick_by_context(locations, anchor, new_source)
        if best:
            update_anchor(anchor, best)
            anchor.health = "drifted"  // Ambiguous match = drifted
            return

    // Step 2: Content hash failed. Try context-based relocation.
    // Look for the surrounding context (before/after hashes) in the new source.
    candidate = find_by_context(anchor, new_source)
    if candidate:
        // Found the neighborhood. Try fuzzy content match within it.
        fuzzy = fuzzy_match(candidate.region, anchor.content_snippet)
        if fuzzy and fuzzy.similarity > 0.6:
            update_anchor(anchor, fuzzy.location)
            anchor.health = "drifted"
            return

    // Step 3: Context also failed. Try line-based heuristic as last resort.
    // Apply the same line offset that the file diff introduces.
    shifted = apply_diff_offset(anchor.line_start, anchor.line_end, old_source, new_source)
    if shifted and content_at(new_source, shifted).similarity(anchor.content_snippet) > 0.4:
        update_anchor(anchor, shifted)
        anchor.health = "drifted"
        return

    // Step 4: All signals exhausted. Mark orphaned.
    anchor.health = "orphaned"
    // Preserve original snippet and line range for human review
```

### 5.3 Fuzzy Matching Strategy

For fuzzy content matching, we use a lightweight approach:

1. **Normalized Levenshtein distance** on the content snippet (first 200 chars). Threshold: 0.6 similarity for `drifted` status.
2. **Line-level diff alignment.** Use the unified diff between old and new source to compute where each old line maps in the new file. This handles insertions/deletions above the anchor cheaply.
3. **Sliding window search.** If content hash fails, slide a window of `anchor_length ± 20%` lines through the new file, scoring each window by Jaccard similarity of word-level n-grams against the original selection.

All of this is conventional string matching — no LLM involvement.

### 5.4 File Rename Tracking

When a source file is renamed:

1. The sidecar file does **not** automatically rename. It still references the old path.
2. On next access, the CLI detects that the source file is missing.
3. It checks `git log --follow --diff-filter=R` for rename history.
4. If a rename is found, it updates the sidecar's `source_file` field and moves the sidecar file to match the new path.
5. If no rename is detected, all threads are marked `orphaned`.

This can also be handled by a git post-checkout hook that runs a `comment reconcile --all` command.

### 5.5 Concurrent Edit Safety

Since the sidecar is a JSON file and multiple surfaces might write to it:

- **CLI operations** use atomic write (write to temp file, then rename) with file-level locking (`flock` on Unix).
- **VSCode extension** holds an in-memory copy and writes on save, with conflict detection (compare `source_hash` before write).
- **Agent operations** are sequential by nature (one tool call at a time within a conversation).

For the initial implementation, file-level locking is sufficient. If concurrent multi-agent workflows become common, we can upgrade to a WAL-style approach or per-thread JSON Lines format.

---

## 6. CLI Interface

### 6.1 Human CLI

Designed for interactive use from the terminal:

```bash
# Create a comment anchored to lines 42-45 of PLAN.md
comment add PLAN.md -L 42:45 "Reconsider the linear scaling assumption"

# Create a comment anchored to a text match
comment add PLAN.md --match "linear scaling" "This doesn't hold above 50MW"

# List all unresolved comments in a file
comment list PLAN.md

# List all unresolved comments in the project
comment list --all

# List with filters
comment list --all --status=open --health=orphaned
comment list --all --author=claude-code

# View a specific thread with full history
comment show t_01JKXYZ

# Reply to a thread
comment reply t_01JKXYZ "Good point — I'll update the breakpoints"

# Resolve a thread with a decision
comment resolve t_01JKXYZ --decision "Switched to piecewise linear model"

# Resolve without decision
comment resolve t_01JKXYZ

# Reopen a resolved thread
comment reopen t_01JKXYZ

# Force reconciliation on a file
comment reconcile PLAN.md

# Reconcile everything
comment reconcile --all

# Generate/update DECISIONS.md
comment decisions
```

### 6.2 Agent CLI / MCP Interface

Identical operations, but optimized for structured I/O. Every command accepts `--json` for machine-readable output, or is exposed as an MCP tool with typed parameters and structured return values.

```bash
# Agent lists unresolved comments (JSON output for parsing)
comment list PLAN.md --json --status=open

# Returns:
# {
#   "file": "PLAN.md",
#   "threads": [
#     {
#       "id": "t_01JKXYZ",
#       "status": "open",
#       "anchor": { "line_start": 42, "line_end": 45, "health": "anchored", "content_snippet": "..." },
#       "comment_count": 2,
#       "latest_comment": { "author": "reid", "body": "..." },
#       "created_at": "..."
#     }
#   ]
# }
```

**MCP Tool Definitions:**

| Tool | Parameters | Returns |
|------|-----------|---------|
| `comment_list` | `file?`, `status?`, `health?`, `author?` | Thread summaries (id, status, anchor snippet, latest comment) |
| `comment_show` | `thread_id` | Full thread with all comments and anchor details |
| `comment_reply` | `thread_id`, `body` | Updated thread |
| `comment_resolve` | `thread_id`, `decision?` | Updated thread |
| `comment_add` | `file`, `line_start`, `line_end`, `body` | New thread |
| `comment_reconcile` | `file?` | Reconciliation report (anchored/drifted/orphaned counts) |

The MCP tools are thin wrappers around the same library that powers the CLI. No separate codepath.

---

## 7. VSCode Extension Surface

### 7.1 Rendering

The extension reads `.comments/<file>.json` and renders:

- **Gutter icons:** Small comment indicator on lines with active threads. Color-coded by status:
  - 🟡 Yellow: open thread
  - 🟢 Green: resolved
  - 🔴 Red: orphaned (anchor lost)
  - 🟠 Orange: drifted (anchor uncertain)
- **Inline decorations:** Subtle background highlight on anchored text ranges (similar to GitHub PR review highlighting).
- **Comment panel:** Sidebar panel showing all threads for the active file, sorted by line number. Each thread is expandable to show full history.
- **Peek view:** Clicking a gutter icon opens a peek widget (like "Peek Definition") showing the thread inline.

### 7.2 Interaction

- **Highlight text → right-click → "Add Comment"** (or keyboard shortcut): Creates a new thread anchored to the selection.
- **Click gutter icon → reply inline:** Opens a text input within the peek view.
- **Resolve button** on each thread in the comment panel.
- **"Comment: Reconcile"** command in the command palette to force reconciliation.

### 7.3 File Watching

The extension watches both source files and their corresponding sidecar files:

- **Source file changed:** Triggers lazy reconciliation (debounced, runs after 2 seconds of inactivity). Updates gutter icons and highlights.
- **Sidecar file changed:** Reloads comment data. This handles the case where an agent (running in a separate terminal) adds or resolves comments — the VSCode UI updates automatically.

### 7.4 Native Comment API Integration

VSCode has a built-in [Comment API](https://code.visualstudio.com/api/references/vscode-api) (`CommentController`, `CommentThread`, `Comment`) that provides:

- Threaded comment UI in the editor gutter (same as GitHub PR reviews)
- Comments Panel in the sidebar
- Resolved/unresolved toggle
- Markdown rendering in comment bodies
- Keyboard navigation between threads

The extension should use this native API as its primary rendering mechanism, mapping our sidecar data structure onto VSCode's `CommentThread` objects. This gives us a polished, familiar UI for free and ensures compatibility with existing VSCode themes and accessibility features.

---

## 8. Orchestration Patterns

### 8.1 Human Review → Agent Iteration

The most common workflow:

```bash
# 1. Agent generates a plan
claude-code "Write an implementation plan for the cost model refactor" > PLAN.md

# 2. Human reviews and adds comments (CLI or VSCode)
comment add PLAN.md -L 15:20 "This assumes linear scaling — use piecewise"
comment add PLAN.md -L 34:38 "Missing error handling for API timeouts"

# 3. Orchestration script dispatches agent
UNRESOLVED=$(comment list PLAN.md --json --status=open)
claude-code "Address the following review comments on PLAN.md: $UNRESOLVED"

# 4. Agent addresses comments and resolves them via tool calls
#    (agent calls comment_reply and comment_resolve via MCP)

# 5. Human verifies, may reopen or add new comments
comment list PLAN.md  # Check what's left
```

### 8.2 Multi-Agent Review Pipeline

```bash
# Agent 1 writes the plan
claude-code "Write PLAN.md for the energy model" 

# Agent 2 reviews the plan (read-only + comment)
claude-code "Review PLAN.md for technical correctness. 
             Use the comment_add tool for each issue found.
             Do NOT modify the source file."

# Human reviews Agent 2's comments, resolves trivials, escalates others
comment list PLAN.md

# Agent 1 addresses remaining open comments
claude-code "Address all open comments on PLAN.md using comment_show 
             and comment_resolve."
```

### 8.3 Continuous Review Loop (Git Hook Integration)

```bash
# .git/hooks/post-commit
#!/bin/bash
comment reconcile --all --quiet
ORPHANED=$(comment list --all --json --health=orphaned | jq '.threads | length')
if [ "$ORPHANED" -gt 0 ]; then
    echo "⚠️  $ORPHANED comment(s) orphaned by this commit. Run 'comment list --health=orphaned' to review."
fi
```

---

## 9. Edge Cases and Failure Modes

### 9.1 Multiple Anchors to Same Text

Two threads anchor to overlapping or identical text ranges. This is allowed — each thread is independent. The CLI and VSCode extension show both threads on the affected lines.

### 9.2 Large Files with Many Comments

For files with > 100 threads, the sidecar file could become large. Mitigation:
- Resolved threads older than a configurable age (default: 30 days) can be archived to `.comments/.archive/<file>.json`.
- The `comment list` command only shows resolved threads if `--include-resolved` is passed.
- The `DECISIONS.md` file captures the important outcomes, so archived threads are rarely needed.

### 9.3 Binary Files and Non-Text Content

The system only supports text files. Attempting to comment on a binary file returns an error. If needed in the future, binary file comments can anchor to byte offsets instead of line ranges.

### 9.4 Merge Conflicts in Sidecar Files

Since sidecars are JSON, git merges will often conflict. Mitigation strategies:

1. **Thread-level merging:** A custom git merge driver that understands the thread array structure and merges at the thread level (threads are identified by ULID, so conflicts only arise if the same thread was modified on both branches).
2. **Pragmatic approach for v1:** Accept that sidecar merge conflicts will occasionally require manual resolution. The schema is simple enough that this is tractable. Include a `comment repair` command that validates and fixes common issues (duplicate IDs, malformed anchors).

### 9.5 Stale Decisions

The `DECISIONS.md` file can become stale if threads are reopened after decisions are recorded. The `comment decisions` command regenerates the file from current thread state, so it's always recoverable. Include a note at the top: "Auto-generated — do not edit manually."

### 9.6 Agent Creates Malformed Comments

Since agents call the MCP tools (not raw file writes), the tool implementation validates all inputs:
- `body` must be non-empty, max 10,000 chars.
- `line_start` and `line_end` must be valid for the current file.
- `thread_id` must exist for reply/resolve operations.
- Invalid calls return structured errors, not silent failures.

---

## 10. Implementation Plan

### Phase 1: Core Library + CLI (MVP)

**Deliverables:**
- Core library (Python or TypeScript) implementing the data model, CRUD operations, and reconciliation algorithm.
- CLI tool wrapping the library.
- Basic reconciliation: content hash + line-offset heuristic.
- `comment add`, `list`, `show`, `reply`, `resolve`, `reconcile` commands.

**Not included:** VSCode extension, MCP server, fuzzy matching, git merge driver.

### Phase 2: Agent Integration

**Deliverables:**
- MCP server exposing comment tools.
- Claude Code slash commands or hook integration.
- `--json` output on all CLI commands.
- `DECISIONS.md` generation.

### Phase 3: VSCode Extension

**Deliverables:**
- Extension using native Comment API.
- Gutter icons, inline highlights, comment panel.
- "Highlight → Comment" UX.
- File watching for live updates.

### Phase 4: Advanced Reconciliation

**Deliverables:**
- Fuzzy matching (Levenshtein, n-gram Jaccard).
- Context-based re-anchoring.
- File rename tracking via git history.
- Git merge driver for sidecar files.
- Thread archiving for large projects.

---

## 11. Open Questions

1. **Language choice for core library.** Python is natural for the Claude Code ecosystem and quick to prototype. TypeScript would share code with the VSCode extension. A Rust CLI would be fastest and most portable. Recommendation: Python for Phase 1-2, consider a TypeScript port for Phase 3 if needed.

2. **Sidecar path convention.** `.comments/` in project root (proposed above) vs. `.comments.json` adjacent to each file vs. `.vscode/comments/`. The project-root approach is cleanest for git and avoids cluttering source directories.

3. **ULID vs UUID for IDs.** ULIDs are sortable by creation time, which is useful for display ordering. Recommended over UUIDv4.

4. **Comment body format.** Plain text for v1. Markdown support in v2 (rendered in VSCode, passed as-is to agents). Rich media (screenshots, diagrams) deferred to v3+.

5. **Multi-repo / monorepo support.** The `.comments/` directory is per-repo by design. For monorepos, each package could have its own `.comments/` or share a root-level one. Defer decision until real usage patterns emerge.

6. **Should `comment reconcile` run automatically or only on demand?** Proposal: Automatic on read (lazy reconciliation) for CLI/MCP. Debounced for VSCode. Explicit `reconcile --all` for git hooks and CI.

---

## Appendix A: Comparison with Existing Tools

| Feature | This System | Antigravity | claude-review | CriticMarkup | vscode-code-review |
|---------|-------------|-------------|---------------|--------------|-------------------|
| Source file modified | Never | N/A (artifacts) | Never | Yes (inline) | Never |
| Storage format | JSON sidecar | Proprietary/opaque | SQLite | Inline syntax | CSV |
| Threaded comments | Yes | Yes | Yes | No | No |
| Resolve/reopen | Yes | Agent resolves | Yes | Accept/reject | No |
| Agent-accessible API | MCP + CLI | Injected into context | Slash commands | None | None |
| Anchor reconciliation | Content hash + fuzzy | N/A | Text-based | N/A | Line numbers only |
| Git-native | Yes (JSON) | No | No (SQLite) | Yes (inline) | Yes (CSV) |
| VSCode integration | Native Comment API | Built-in (proprietary) | Browser only | None | Custom decorations |
| Works on any text file | Yes | Artifacts only | Markdown only | Markdown only | Any file |
| Deterministic operations | All CRUD | UI-mediated | Slash commands | Manual | Manual |

## Appendix B: Example Sidecar File

Complete example for a hypothetical `PLAN.md`:

```json
{
  "version": "1.0",
  "source_file": "PLAN.md",
  "source_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "last_reconciled": "2026-02-01T14:30:00Z",
  "threads": [
    {
      "id": "t_01JKXYZ1A2B3C4D5E6F7",
      "status": "resolved",
      "anchor": {
        "content_hash": "sha256:abc123...",
        "content_snippet": "The LCOE calculation assumes linear scaling",
        "context_before_hash": "sha256:def456...",
        "context_after_hash": "sha256:ghi789...",
        "context_before_snippet": "## Cost Model\n\nThis section describes",
        "context_after_snippet": "across all capacity ranges.\n\n### Assumptions",
        "line_start": 42,
        "line_end": 44,
        "char_start": 0,
        "char_end": null,
        "health": "anchored",
        "drift_distance": 0,
        "last_verified": "2026-02-01T14:30:00Z"
      },
      "comments": [
        {
          "id": "c_01JKXYZ1A2B3C4D5E6F7",
          "author": "reid",
          "author_type": "human",
          "body": "This assumes linear scaling but our data shows step functions at capacity thresholds. Need piecewise model.",
          "created_at": "2026-02-01T10:00:00Z"
        },
        {
          "id": "c_01JKABC1A2B3C4D5E6F7",
          "author": "claude-code",
          "author_type": "agent",
          "body": "Updated to piecewise linear with breakpoints at 10MW, 50MW, and 200MW based on the DOE reference data in references/doe-cost-curves-2025.pdf.",
          "created_at": "2026-02-01T10:45:00Z"
        }
      ],
      "decision": {
        "summary": "Cost model uses piecewise linear segments with breakpoints at 10/50/200 MW per DOE 2025 data",
        "decided_by": "reid",
        "decided_at": "2026-02-01T11:00:00Z"
      },
      "created_at": "2026-02-01T10:00:00Z",
      "resolved_at": "2026-02-01T11:00:00Z"
    },
    {
      "id": "t_01JKDEF1A2B3C4D5E6F7",
      "status": "open",
      "anchor": {
        "content_hash": "sha256:jkl012...",
        "content_snippet": "API calls to the weather service are made synchronously",
        "context_before_hash": "sha256:mno345...",
        "context_after_hash": "sha256:pqr678...",
        "context_before_snippet": "### Data Pipeline\n\nFor each site evaluation",
        "context_after_snippet": "and cached for 24 hours.\n\n### Error Handling",
        "line_start": 78,
        "line_end": 80,
        "char_start": 0,
        "char_end": null,
        "health": "drifted",
        "drift_distance": 3,
        "last_verified": "2026-02-01T14:30:00Z"
      },
      "comments": [
        {
          "id": "c_01JKDEF1A2B3C4D5E6F7",
          "author": "reid",
          "author_type": "human",
          "body": "This needs timeout handling. What happens if the weather API is down during a batch run of 500 sites?",
          "created_at": "2026-02-01T13:00:00Z"
        }
      ],
      "decision": null,
      "created_at": "2026-02-01T13:00:00Z",
      "resolved_at": null
    }
  ]
}
```