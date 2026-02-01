# Specification: VSCode Extension

**Purpose:** Render comments as native VSCode UI elements with real-time updates and intuitive interaction patterns.

## Requirements

**REQ-1: Native Comment API**
- MUST use VSCode CommentController API for rendering
- MUST register CommentThread objects for each thread
- MUST map thread status to VSCode's resolved/unresolved states
- MUST render comment bodies as markdown

**REQ-2: Gutter Indicators**
- MUST show gutter icons on lines with active threads
- Icon colors: 🟡 open, 🟢 resolved, 🔴 orphaned, 🟠 drifted
- MUST show count badge for threads with multiple comments
- Click on gutter icon MUST open comment panel

**REQ-3: Inline Highlights**
- MUST highlight anchored text ranges with subtle background color
- Health-based styling: solid (anchored), dashed (drifted), strikethrough (orphaned)
- MUST clear highlights when thread is resolved

**REQ-4: Comment Creation**
- "Highlight text → right-click → Add Comment" UX
- Keyboard shortcut (configurable, default: `Cmd+K Cmd+M`)
- MUST anchor to exact selection (line_start, line_end, char offsets)
- MUST validate selection before creating thread

**REQ-5: File Watching**
- MUST watch source files for changes (debounced 2 seconds)
- MUST watch sidecar files for external modifications
- Source change triggers lazy reconciliation + UI update
- Sidecar change triggers comment reload (handles external CLI/agent edits)

**REQ-6: Comment Panel**
- MUST show all threads for active file in sidebar
- Sort by line number (orphaned threads at bottom)
- Expandable threads showing full comment history
- Inline reply input within thread

**REQ-7: Commands**
- "Comment: Reconcile File" in command palette
- "Comment: Show Decisions" (opens DECISIONS.md)
- "Comment: Reconcile All" (project-wide)

## Acceptance Criteria

**AC-1:** Given file with 3 threads, when file opens, then 3 gutter icons appear at correct line numbers

**AC-2:** Given text selection on lines 10-15, when "Add Comment" clicked, then comment panel opens with input focused

**AC-3:** Given sidecar file updated by CLI, when 2 seconds elapse, then VSCode UI reflects new comment

**AC-4:** Given source file edited with insertion above thread, when saved, then gutter icon moves to new line position automatically

**AC-5:** Given thread resolved in VSCode, when checking sidecar file, then status is "resolved" and resolved_at is set

**AC-6:** Given orphaned thread, when hovering gutter icon, then tooltip shows "Anchor lost: [original snippet]"

**AC-7:** Given DECISIONS.md exists, when "Comment: Show Decisions" runs, then file opens in editor

## Interfaces

**Inputs:**
- Source files (read-only, for anchor positions)
- Sidecar files (read/write via file-operations layer)
- User interactions (clicks, text input)

**Outputs:**
- VSCode CommentThread objects
- Gutter decorations (DecorationTypes)
- Updated sidecar files (on create/reply/resolve)

**References:**
- `data-model.md`: Thread/comment structures
- `file-operations.md`: Sidecar read/write
- `anchor-reconciliation.md`: Triggered on file change

## Constraints

**CON-1:** MUST work with VSCode 1.85+ and Cursor
**CON-2:** UI updates MUST debounce (avoid flicker on rapid edits)
**CON-3:** Extension MUST NOT block editor (all operations async)
**CON-4:** MUST respect VSCode theme colors for highlights

## Out of Scope

- Rich text editor for comments (markdown only)
- Image/attachment support in comments
- Comment search within extension (use native search)
- Diffing comments across git branches
- Real-time collaboration (extension operates on local files only)
